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
import json
import sys
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import TypeVar
from typing import Union

from mantis_authz import MantisOpenID
from mantis_authz.config import authz_config
from pydantic import BaseModel
from pydantic import Field
from pydantic import ValidationError
from rich.prompt import Confirm
from ruamel.yaml import YAML

from mantis_api_client.config import mantis_api_client_config

RT = TypeVar("RT")

oidc_client = None


class ConfigurationError(ValueError):
    pass


class Profile(BaseModel):
    domain: str
    refresh_token: str
    default_group: Optional[str] = None


class Session(BaseModel):
    active_profile: Optional[str] = None
    profiles: Dict[str, Profile] = Field(default_factory=dict)

    def get_active_profile(self, raise_exc: bool = True) -> Optional[Profile]:
        if self.active_profile is None:
            if raise_exc:
                raise ConfigurationError(
                    "Not authenticated, you need to execute 'mantis account login"
                )
            return None
        return self.profiles[self.active_profile]

    def set_active_profile(self, name: str) -> None:
        if name not in self.profiles:
            raise ValueError(f"Unknown profile '{name}'")
        self.active_profile = name


class ConfigFileManager:
    def __init__(self, path: Union[str, Path]) -> None:
        if isinstance(path, str):
            path = Path(path)
        if path.suffix in (".yaml", ".yml"):
            klass = YAML()
            loader = klass.load
            dumper = klass.dump
        # elif path.suffix == ".json":
        #     loader = json.load
        #     dumper = json.dump
        else:
            raise ValueError(f"Unknown file suffix '{path.suffix}'")
        self.loader = loader
        self.dumper = dumper
        self.path = path

    def load(self) -> Dict:
        return self.loader(self.path) or {}

    def dump(self, obj) -> None:
        self.dumper(obj, self.path)


class OIDCClient:
    """
    Provide a wrapper arround OIDC client providing token refreshing for API
    calls.
    """

    def __init__(self) -> None:
        try:
            self._session = self._parse_session_from_config()
        except FileNotFoundError:
            self._session = Session()
        self.set_context()
        self._oidc: Optional[MantisOpenID] = self._get_oidc()
        self._access_token: Optional[str] = None

    def get_active_profile_domain(self, **kwargs) -> Optional[str]:
        active_profile = self._session.get_active_profile(**kwargs)
        if active_profile is None:
            return None
        return active_profile.domain

    def get_default_group(self, **kwargs) -> Optional[str]:
        active_profile = self._session.get_active_profile(**kwargs)
        if active_profile is None:
            return None
        return active_profile.default_group

    @staticmethod
    def _parse_session_from_config() -> Session:
        obj = ConfigFileManager(mantis_api_client_config.config_file).load()
        try:
            session = Session(
                active_profile=obj.get("active_profile"),
                profiles=obj.get("profiles", {}),
            )
        except ValidationError:
            exit("Configuration format is incorrect.\nRun `mantis init` again")
        if (
            session.active_profile is not None
            and session.active_profile not in session.profiles
        ):
            raise ConfigurationError(
                "Unknown default profile '{}'".format(obj["active_profile"])
            )
        return session

    def _store_session_to_config(self) -> None:
        cfgmgr = ConfigFileManager(mantis_api_client_config.config_file)
        cfgmgr.dump(self._session.dict())

    def _get_oidc(self, domain: Optional[str] = None) -> Optional[MantisOpenID]:
        mantis_api_client_config.config_file.touch(exist_ok=True)

        if domain is None:
            # return early when no session is available
            if self._session.active_profile is None:
                return None
            active_profile = self._session.get_active_profile()
            assert active_profile is not None
            domain = active_profile.domain
        else:
            self.set_context(profile=domain)
        return MantisOpenID(
            server_url=mantis_api_client_config.oidc.server_url,
            realm_name=mantis_api_client_config.oidc.realm,
            client_id=mantis_api_client_config.oidc.client_id,
        )

    def set_context(self, profile: Optional[str] = None) -> None:
        if profile is None:
            profile = self._session.active_profile
            if profile is None:  # Production configuration
                profile = "mantis-platform.io"
        if profile:
            # prod mode
            mantis_domain = profile
            app_base_url = f"https://app.{mantis_domain}"
            id_base_url = f"https://id.{mantis_domain}"
            mantis_api_client_config.update(
                {
                    "dataset_api_url": f"{app_base_url}/api/dataset",
                    "dataset_web_url": f"{app_base_url}/datasets/resources",
                    "scenario_api_url": f"{app_base_url}/api/scenario",
                    "user_api_url": f"{app_base_url}/api/backoffice",
                }
            )
            mantis_api_client_config.oidc.server_url = id_base_url
            del app_base_url, id_base_url
            authz_config.use_permissions = True

    def configure_profile(
        self,
        domain: Optional[str] = None,
        token: Optional[str] = None,
        group: Optional[str] = None,
    ) -> None:
        profile_name = domain
        if profile_name is None:
            # remove profile
            if self._session.active_profile is not None:
                self._session.profiles.pop(self._session.active_profile, None)
        else:
            assert domain is not None and token is not None
            if profile_name not in self._session.profiles:
                profile = Profile(
                    domain=domain,
                    refresh_token=token,
                    default_group=group,
                )
                self._session.profiles[profile_name] = profile
        self._session.active_profile = profile_name
        self.set_context()
        self._store_session_to_config()

    def get_active_tokens(self) -> Dict:
        active_profile = self._session.get_active_profile()
        assert active_profile is not None and self._oidc is not None
        return self._oidc.refresh_token(active_profile.refresh_token)

    def token(self, domain: str, *args, **kwargs):
        oidc = self._get_oidc(domain)
        assert oidc is not None
        return oidc.token(*args, **kwargs)

    def auth_url(self, domain: str, *args, **kwargs):
        oidc = self._get_oidc(domain)
        assert oidc is not None
        return oidc.auth_url(*args, **kwargs)


def authorize(func: Callable[..., RT]) -> Callable[..., RT]:
    def authorize_wrapper(route: str, **kwargs: Any) -> Any:
        tokens = get_oidc_client().get_active_tokens()
        access_token = tokens["access_token"]
        kwargs.setdefault("headers", {}).update(
            {"Authorization": f"Bearer {access_token}"}
        )
        return func(route, **kwargs)

    if authz_config.use_permissions:
        return authorize_wrapper
    return func


def _migrate_legacy_session_file() -> None:
    config_file = mantis_api_client_config.config_file
    legacy_config_file = config_file.parent / "session.json"
    if legacy_config_file.exists() and not config_file.exists():
        print(f"Legacy configuration file found at `{legacy_config_file}`")
        confirm = Confirm.ask("Do you want to convert it automatically ?", default=True)
        if confirm:
            try:
                with legacy_config_file.open() as f:
                    legacy_config = json.load(f)
                with config_file.open("w") as f:
                    YAML().dump(_convert_legacy_config_file(legacy_config), f)
                legacy_config_file.unlink()
            except Exception:
                if Confirm.ask(
                    "Migration failed. You should remove the configuration file. Proceed ?",
                    default=True,
                ):
                    legacy_config_file.unlink()
            else:
                print(f"Migration completed. New configuration file is `{config_file}`")


def _convert_legacy_config_file(legacy_config: Dict) -> Dict:
    return {
        "active_profile": legacy_config.pop("active_profile")[11:],
        "profiles": {
            domain[11:]: {"domain": domain[11:], **conf}
            for domain, conf in legacy_config.items()
        },
    }


def initialize_oidc_client() -> None:
    global oidc_client
    mantis_api_client_config.config_file.parent.mkdir(parents=True, exist_ok=True)
    _migrate_legacy_session_file()
    oidc_client = OIDCClient()


def get_oidc_client() -> OIDCClient:
    if oidc_client is None:
        try:
            initialize_oidc_client()
        except Exception as e:
            from mantis_api_client.utils import colored

            print(colored(str(e), "white", "on_red"))
            sys.exit(1)

    assert oidc_client is not None
    return oidc_client


# Call OIDCClient initialization once here, to prevent some internal initialization issues
# like authz_config.use_permissions not being set properly
get_oidc_client()
