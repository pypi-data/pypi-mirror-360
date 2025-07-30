#!/usr/bin/env python3
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from os.path import expandvars
from pathlib import Path
from typing import Any, Type

import yaml

from toolforge_weld.errors import ToolforgeError

LOGGER = logging.getLogger(__name__)
# This helps testing
CONFIGS_BASE_DIR = Path("/etc/toolforge")


class LoadConfigError(ToolforgeError):
    """Raised when unable to load a config file."""


@dataclass
class Section:
    # Override with your section name as seen in the config file
    _NAME_: str = field(default="noname", init=False)

    @classmethod
    def from_dict(cls, my_dict: dict[str, Any]):
        raise NotImplementedError


@dataclass
class Config:
    sections: dict[str, Section]
    # toolforge cli subcommand binaries search prefix
    toolforge_prefix: str = "toolforge-"

    def __getattr__(self, name) -> Any:
        return self.sections[name]

    @classmethod
    def from_dict(cls, my_dict: dict[str, Any]):
        # doing it like this instead of **my_dict allows to more
        # gracefully deprecate keys, as we have to sync puppet changes
        # with code changes
        params = {}
        if "toolforge_prefix" in my_dict:
            params["toolforge_prefix"] = my_dict["toolforge_prefix"]

        if "sections" in my_dict:
            params["sections"] = my_dict["sections"]

        return cls(**params)


@dataclass
class ApiGatewaySection(Section):
    _NAME_: str = field(default="api_gateway", init=False)
    url: str = "https://api.svc.tools.eqiad1.wikimedia.cloud:30003"

    @classmethod
    def from_dict(cls, my_dict: dict[str, Any]):
        # doing it like this instead of **my_dict allows to more
        # gracefully deprecate keys, as we have to sync puppet changes
        # with code changes
        # the TOOL_ prefix is the prefix of all non-user set envvars
        url = os.environ.get("TOOL_TOOLFORGE_API_URL", None)
        if url is None:
            url = my_dict.get("url", cls.url)

        params = {"url": url}
        return cls(**params)


def load_config(
    client_name: str, extra_sections: list[Type[Section]] | None = None
) -> Config:
    """
    Loads the config for the given client.
    """
    extra_sections = extra_sections or []
    # TODO: Implement some kind of merge strategy
    configs_less_to_more_priority: list[Path] = [
        CONFIGS_BASE_DIR / f"{client_name}.yaml",
        CONFIGS_BASE_DIR / "common.yaml",
        Path("~/.toolforge.yaml"),
        Path("~/.config/toolforge.yaml"),
        Path("$XDG_CONFIG_HOME/toolforge.yaml"),
    ]

    config: dict[str, Any] = {}
    for conf_file in configs_less_to_more_priority:
        full_file = Path(expandvars(conf_file.expanduser()))
        if full_file.exists() and full_file.is_file():
            try:
                config.update(yaml.safe_load(full_file.open()))
            except Exception as error:
                # by default the error does not show which file failed to load
                # so we show it here ourselves
                raise LoadConfigError(
                    f"Unable to parse config file {full_file}"
                ) from error

            LOGGER.debug("Updating config from %s", full_file)
        else:
            LOGGER.debug("Unable to find config file %s, skipping", full_file)

    sections = {
        section._NAME_: section.from_dict(config.get(section._NAME_, {}))
        for section in [ApiGatewaySection] + extra_sections
    }
    config["sections"] = sections
    return Config.from_dict(config)
