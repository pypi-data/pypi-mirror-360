# -*- coding: utf-8 -*-
from typing import Optional
from typing import Union

from mantis_authz.api import API
from mantis_authz.models import Token


class BackofficeAPI(API):
    """
    This API allows you to query the backoffice API.
    """

    def __init__(
        self,
        authorized_token: Optional[Union[Token, str]] = None,
    ):
        url = "http://backoffice-api:8000"
        super().__init__(url, authorized_token)
