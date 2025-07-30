#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2021 AMOSSYS. All rights reserved.
#
# This file is part of Cyber Range AMOSSYS.
#
# Cyber Range AMOSSYS can not be copied and/or distributed without the express
# permission of AMOSSYS.
#
#
from dataclasses import dataclass
from typing import Optional
from typing import Union

import omegaconf.errors as om_err
from omegaconf import OmegaConf
from omegaconf import SI


@dataclass
class AuthzConfig:
    server_url: Optional[str] = SI("${oc.env:OIDC_SERVER_URL,null}")
    realm: Optional[str] = SI("${oc.env:OIDC_REALM,null}")
    discovery_url: Optional[str] = SI("${oc.env:OIDC_DISCOVERY_URL,null}")
    client_id: Optional[str] = SI("${oc.env:OIDC_CLIENT_ID,null}")
    client_secret: Optional[str] = SI("${oc.env:OIDC_CLIENT_SECRET,null}")

    use_permissions: bool = SI("${oc.decode:${oc.env:USE_PERMISSIONS,false}}")

    verify_ssl: Union[bool, str] = SI("${oc.decode:${oc.env:VERIFY_SSL,true}}")

    opa_addr: str = "${oc.env:OPA_ADDR}"
    default_policy_name: Optional[str] = SI("${oc.env:DEFAULT_POLICY_NAME,null}")
    skip_opa_backoffice_populate_input: bool = SI(
        "${oc.env:OPA_SKIP_BACKOFFICE_POPULATE,false}"
    )


authz_config = OmegaConf.structured(AuthzConfig)

if authz_config.use_permissions:
    # ensure OIDC values are also set
    mandatory_keys = (
        "server_url",
        "realm",
        "discovery_url",
        "client_id",
        "client_secret",
        "default_policy_name",
    )
    if not all(map(lambda k: authz_config[k], mandatory_keys)):
        raise om_err.MissingMandatoryValue(
            f"Missing mandatory values when 'use_permissions' is set: {mandatory_keys}"
        )
