# -*- coding: utf-8 -*-
from typing import Any
from typing import Dict
from typing import Mapping
from typing import Optional
from typing import Union

import httpx
from mantis_authz.models import Token

Body = Optional[Mapping[str, Any]]
Params = Mapping[str, Any]


class API:
    def __init__(
        self,
        url: str,
        authorized_token: Optional[Union[Token, str]] = None,
    ):
        self._url: str = url
        self.__token: Optional[str] = None
        if isinstance(authorized_token, Token):
            self.__token = authorized_token.raw
        elif isinstance(authorized_token, str):
            self.__token = authorized_token

    async def _request(
        self,
        method: str,
        path: str,
        params: Params = {},
        headers: Dict[str, str] = {},
        body: Optional[Body] = None,
    ):
        additional_headers: dict[str, str] = {}
        method = method.upper()

        if body is None:
            body = {}

        headers = {
            **additional_headers,
            **headers,
        }
        if self.__token is not None:
            headers["authorization"] = f"Bearer {self.__token}"

        url = f"{self._url}{path}"

        async with httpx.AsyncClient() as client:
            request = client.build_request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                data=body,
            )
            response = await client.send(request)
        return response
