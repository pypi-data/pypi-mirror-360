# -*- coding: utf-8 -*-
import asyncio
from typing import Awaitable
from typing import List
from typing import Optional
from urllib.parse import urlparse

from async_lru import alru_cache
from fastapi import Request
from fastapi_opa import OPAConfig
from fastapi_opa import OPAMiddleware
from fastapi_opa.auth import OIDCAuthentication
from fastapi_opa.auth import OIDCConfig
from fastapi_opa.opa.opa_config import Injectable
from mantis_authz.backoffice import MyOrganizations
from mantis_authz.backoffice import MyRoles
from mantis_authz.config import authz_config
from mantis_authz.models import Token
from mantis_authz.util import MantisOpenID
from opa_client import create_opa_client


class JwtInjectable(Injectable):
    def _exchange_token(self, access_token: str) -> str:
        oidc_client = MantisOpenID()
        new_token_data = oidc_client.exchange_token(
            access_token,
            subject_token_type="urn:ietf:params:oauth:token-type:access_token",
            audience=authz_config.client_id,
        )
        new_access_token = new_token_data["access_token"]
        return new_access_token

    async def extract(self, request: Request) -> Optional[str]:
        bearer = request.headers.get("Authorization")
        if bearer:
            access_token = bearer.replace("Bearer ", "")
            return self._exchange_token(access_token)
        return None


class MantisOPAMiddleware(OPAMiddleware):
    """A preconfigured OPAMiddleware."""

    def __init__(
        self,
        *args,
        injectables: Optional[List[Injectable]] = None,
        package_name: Optional[str] = None,
        **kwargs,
    ):
        if injectables is None:
            injectables = []
        if package_name is None:
            package_name = authz_config.default_policy_name
        oidc_config = OIDCConfig(
            well_known_endpoint=authz_config.discovery_url,
            app_uri="",
            client_id=authz_config.client_id,
            client_secret=authz_config.client_secret,
        )
        oidc_auth = OIDCAuthentication(oidc_config)
        opa_config = OPAConfig(
            authentication=oidc_auth,
            injectables=[JwtInjectable("token")] + injectables,
            opa_host=authz_config.opa_addr,
            package_name=package_name,
        )
        kwargs.setdefault("config", opa_config)
        super().__init__(*args, **kwargs)


@alru_cache(ttl=60)
async def backoffice_subject_data(access_token: str):
    results = await asyncio.gather(
        MyOrganizations(access_token).request(),
        MyRoles(access_token).request(),
    )
    return {
        "subject_organizations": results[0],
        "subject_roles": results[1],
    }


class MantisOPAClient:
    def __init__(self, access_token: Token):
        opa_addr_parts = urlparse(authz_config.opa_addr)
        self.opa_client = create_opa_client(
            async_mode=True,
            host=opa_addr_parts.hostname,
            port=opa_addr_parts.port,
        )
        self.raw_access_token = access_token.raw
        self.default_input_data: dict = {"token": self.raw_access_token}

    async def update_default_opa_input(self):
        if not authz_config.skip_opa_backoffice_populate_input:
            # TODO: make a single request with whole data returned
            bo_data = await backoffice_subject_data(self.default_input_data["token"])
            self.default_input_data.update({"backoffice": bo_data})

    async def check_permission(
        self,
        input_data: Optional[dict] = None,
        rule_name: str = "allow",
        policy_name: str = authz_config.default_policy_name,
    ) -> Awaitable[dict]:
        await self.update_default_opa_input()
        if input_data is None:
            input_data = self.default_input_data.copy()
        else:
            for kvp in self.default_input_data.items():
                input_data.setdefault(*kvp)
        async with self.opa_client as opa_client:
            perm = await opa_client.query_rule(input_data, policy_name, rule_name)
        return perm
