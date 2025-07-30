#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2021 AMOSSYS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from omegaconf import OmegaConf
from omegaconf import SI


@dataclass
class CrApiClientConfig:
    _api_host: str = "${oc.env:API_HOST,localhost}"
    core_api_url: str = "${oc.env:CORE_API_URL,http://${._api_host}:5000}"
    user_activity_api_url: str = (
        "${oc.env:USER_ACTIVITY_API_URL,http://${._api_host}:5002}"
    )
    provisioning_api_url: str = (
        "${oc.env:PROVISIONING_API_URL,http://${._api_host}:5003}"
    )
    redteam_api_url: str = "${oc.env:REDTEAM_API_URL,http://${._api_host}:5004}"
    cacert: Optional[Path] = SI("${oc.env:CR_CA_CERT,null}")
    cert: Optional[Path] = SI("${oc.env:CR_CLIENT_CERT,null}")
    key: Optional[Path] = SI("${oc.env:CR_CLIENT_KEY,null}")


cr_api_client_config = OmegaConf.structured(CrApiClientConfig)
