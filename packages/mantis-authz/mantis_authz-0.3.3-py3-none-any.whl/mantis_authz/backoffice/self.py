# -*- coding: utf-8 -*-
from mantis_authz.backoffice.api import BackofficeAPI


class MyOrganizations(BackofficeAPI):
    async def request(self):
        res = await self._request("GET", "/my/organizations")
        return res.json()


class MyRoles(BackofficeAPI):
    async def request(self):
        res = await self._request("GET", "/my/roles")
        return res.json()
