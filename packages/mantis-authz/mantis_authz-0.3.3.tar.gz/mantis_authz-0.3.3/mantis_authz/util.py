# -*- coding: utf-8 -*-
import ssl
from typing import Any
from typing import Dict
from typing import Generic
from typing import List
from typing import Mapping
from typing import Optional
from typing import Tuple
from typing import TypeVar
from typing import Union

import aiohttp
import jose.exceptions
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OpenIdConnect as FastAPIOpenIdConnect
from fastapi.security import SecurityScopes
from fastapi.security.base import SecurityBase
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.security.http import HTTPBase
from jose import jwt
from keycloak import KeycloakOpenID
from keycloak import KeycloakOpenIDConnection
from keycloak import KeycloakUMA
from mantis_authz.cache import authz_cache
from mantis_authz.config import authz_config
from mantis_authz.models import Token
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED
from typing_extensions import Annotated

T = TypeVar("T")


class SingletonMeta(type, Generic[T]):
    _instances: Dict["SingletonMeta[T]", T] = {}

    def __call__(cls, *args, **kwargs) -> T:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class OpenIdConnect(FastAPIOpenIdConnect):
    """
    Class inheriting from `fastapi.security.OpenIdConnect`, that fixes the
    status code when the authorization header is absent (403 => 401).
    """

    async def __call__(self, request: Request) -> Optional[str]:
        try:
            return await super().__call__(request)
        except HTTPException as e:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail=e.detail
            )  # noqa: F811


class MantisOpenID(KeycloakOpenID, metaclass=SingletonMeta):
    """
    Pre-configured Keycloak OIDC.
    """

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("server_url", authz_config.server_url)
        kwargs.setdefault("realm_name", authz_config.realm)
        kwargs.setdefault("client_id", authz_config.client_id)
        kwargs.setdefault("client_secret_key", authz_config.client_secret)
        kwargs.setdefault("verify", authz_config.verify_ssl)
        super().__init__(**kwargs)


class MantisUMA(KeycloakUMA, metaclass=SingletonMeta):
    """
    Pre-configured Keycloak UMA client.
    """

    def __init__(self, token: Optional[str] = None) -> None:
        super().__init__(
            connection=KeycloakOpenIDConnection(
                server_url=authz_config.server_url,
                realm_name=authz_config.realm,
                client_id=authz_config.client_id,
                client_secret_key=authz_config.client_secret,
                verify=authz_config.verify_ssl,
                token=token,
            )
        )


def get_oidc_scheme() -> SecurityBase:
    oidc_scheme: SecurityBase
    if authz_config.use_permissions:
        oidc_scheme = OpenIdConnect(openIdConnectUrl=authz_config.discovery_url)
    else:
        # dummy authenticator use to respect endpoint definitions
        oidc_scheme = HTTPBase(scheme="null", auto_error=False)
    return oidc_scheme


async def get_cached_certs() -> Tuple[bool, List[Dict[str, str]]]:
    jwks = authz_cache.jwks
    cached = False
    if not jwks:
        async with aiohttp.ClientSession() as session:
            ssl_ctx = ssl.create_default_context()
            if isinstance(authz_config.verify_ssl, str):
                ssl_ctx.load_verify_locations(cafile=authz_config.verify_ssl)
            kwargs: Mapping[str, Any] = dict(ssl=ssl_ctx)
            async with session.get(authz_config.discovery_url, **kwargs) as response:
                data = await response.json()
            async with session.get(data["jwks_uri"], **kwargs) as response:
                certs = await response.json()
        authz_cache.jwks.extend(jwks := certs["keys"])
        cached = True
    return cached, jwks


async def get_jwk(kid: str) -> Optional[Dict]:
    cached, jwks = await get_cached_certs()
    for jwk in jwks:
        if kid == jwk["kid"]:
            return jwk
    # kid was not found, we should retry with fresh keys
    if not cached:
        # except when the jwks has just been refreshed
        # None is handled as en error by the caller
        return None
    del authz_cache.jwks[:]
    return await get_jwk(kid)


async def get_jwt_token_fastapi(
    security_scopes: SecurityScopes,
    token_header: Annotated[
        Union[HTTPAuthorizationCredentials, str, None], Depends(get_oidc_scheme())
    ],
) -> Optional[Token]:
    return await get_jwt_token(security_scopes.scopes, token_header)


async def get_jwt_token(
    scopes: List[str],
    token_header: Annotated[
        Union[HTTPAuthorizationCredentials, str, None], Depends(get_oidc_scheme())
    ],
) -> Optional[Token]:
    # Handle missing token header
    if token_header is None:
        if authz_config.use_permissions:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Bearer token required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return None

    expected_token_types = ("Bearer",)

    # Handle str formatted token header
    if isinstance(token_header, str):
        try:
            token_header_type, token_raw_data = token_header.split(maxsplit=1)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": expected_token_types[0]},
            )
        token_header = HTTPAuthorizationCredentials(
            scheme=token_header_type, credentials=token_raw_data
        )

    assert isinstance(token_header, HTTPAuthorizationCredentials)
    if token_header.scheme not in expected_token_types:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": expected_token_types[0]},
        )

    token_raw = token_header.credentials
    token_data = await parse_raw_token(token_raw, scopes=scopes)
    return Token(
        raw=token_raw,
        decoded=token_data,
        header_auth_type=token_header.scheme,
    )


async def parse_raw_token(
    token_raw: str,
    scopes: Optional[List[str]] = None,
) -> Dict:
    if scopes is None:
        scopes = []
    token_headers = jwt.get_unverified_header(token_raw)
    token_type = token_headers["typ"]
    if token_type != "JWT":
        raise ValueError("Invalid token type %r" % token_type)

    token_data: dict
    if authz_config.use_permissions:
        token_jwk = await get_jwk(token_headers["kid"])
        if token_jwk is None or token_headers["alg"] != token_jwk["alg"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is invalid",
            )
        try:
            token_data = jwt.decode(
                token_raw,
                token_jwk,
                audience=authz_config.client_id,
            )
        except jose.exceptions.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            )
        for scope in scopes:
            if scope not in token_data["scope"].split():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not enough permission",
                )
    else:
        token_data = jwt.get_unverified_claims(token_raw)
    return token_data
