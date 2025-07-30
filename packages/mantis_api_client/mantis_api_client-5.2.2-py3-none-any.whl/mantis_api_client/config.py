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
from dataclasses import field
from pathlib import Path
from typing import Optional

from mantis_authz.config import AuthzConfig
from omegaconf import OmegaConf
from omegaconf import SI


@dataclass
class MantisOIDCConfig(AuthzConfig):
    realm: str = "mantis"
    client_id: str = "mantis-cli"
    domain: Optional[str] = None
    redirect_url: dict = field(
        default_factory=lambda: {
            "scheme": "http",
            "host": "localhost",
            "port": 9876,
            "path": "/callback",
        }
    )
    redirect_url_timeout: int = SI(
        "${oc.decode:${oc.env:OIDC_REDIRECT_URL_TIMEOUT,60}}"
    )
    redirect_uri: str = (
        "${oc.env:OIDC_REDIRECT_URI,${.redirect_url.scheme}://${.redirect_url.host}:${.redirect_url.port}${.redirect_url.path}}"
    )


@dataclass
class MantisApiClientConfig:
    dataset_api_url: str
    dataset_web_url: str
    scenario_api_url: str
    user_api_url: str
    cacert: Optional[Path] = SI("${oc.env:CR_CA_CERT,null}")
    cert: Optional[Path] = SI("${oc.env:CR_CLIENT_CERT,null}")
    key: Optional[Path] = SI("${oc.env:CR_CLIENT_KEY,null}")

    config_file: Path = SI(
        "${oc.env:MANTIS_CONFIG,${oc.env:XDG_CONFIG_HOME,${oc.env:HOME}/.config}/mantis/config.yml}"
    )

    # OIDC
    oidc: MantisOIDCConfig = field(default_factory=MantisOIDCConfig)


mantis_api_client_config = OmegaConf.structured(MantisApiClientConfig)
