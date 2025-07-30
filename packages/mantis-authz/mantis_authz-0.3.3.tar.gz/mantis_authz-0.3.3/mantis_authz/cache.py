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
from dataclasses import field


@dataclass
class CacheStore:
    jwks: list = field(default_factory=list)


authz_cache = CacheStore()
