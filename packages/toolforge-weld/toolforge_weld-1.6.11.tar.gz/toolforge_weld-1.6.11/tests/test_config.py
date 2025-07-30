from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest
import yaml

from toolforge_weld import config
from toolforge_weld.config import ApiGatewaySection, Config, Section


@pytest.fixture(autouse=True)
def config_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CONFIGS_BASE_DIR", tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg_config_home"))
    return tmp_path


def test_config_loads_default_config():
    expected_config = Config(
        sections={
            "api_gateway": ApiGatewaySection(
                url="https://api.svc.tools.eqiad1.wikimedia.cloud:30003"
            )
        },
        toolforge_prefix="toolforge-",
    )

    gotten_config = config.load_config(client_name="dummy-client")

    assert gotten_config == expected_config


def test_config_loads_api_url_from_env(monkeypatch):
    expected_config = Config(
        sections={"api_gateway": ApiGatewaySection(url="https://a.different.url")},
        toolforge_prefix="toolforge-",
    )
    monkeypatch.setenv("TOOL_TOOLFORGE_API_URL", "https://a.different.url")

    gotten_config = config.load_config(client_name="dummy-client")

    assert gotten_config == expected_config


@pytest.mark.parametrize(
    "custom_path",
    [
        "dummy-client.yaml",
        "common.yaml",
        "home/.toolforge.yaml",
        "xdg_config_home/toolforge.yaml",
        "home/.config/toolforge.yaml",
    ],
)
def test_custom_has_precedence(config_dir: Path, custom_path: str):
    overriding_config = {"api_gateway": {"url": "dummy_url"}}
    overriding_config_file = config_dir / custom_path
    if not overriding_config_file.parent.exists():
        os.makedirs(str(overriding_config_file.parent))

    overriding_config_file.write_text(yaml.dump(overriding_config))

    expected_config = Config(
        sections={"api_gateway": ApiGatewaySection(url="dummy_url")},
        toolforge_prefix="toolforge-",
    )

    gotten_config = config.load_config(client_name="dummy-client")

    assert gotten_config == expected_config


def test_adding_extra_section_works(config_dir: Path):
    overriding_config = {"extra_section": {"dummy_config": "dummy_value"}}
    overriding_config_file = config_dir / "dummy-client.yaml"
    if not overriding_config_file.parent.exists():
        os.makedirs(str(overriding_config_file.parent))

    overriding_config_file.write_text(yaml.dump(overriding_config))

    @dataclass
    class ExtraSection(Section):
        _NAME_: str = field(default="extra_section", init=False)
        dummy_config: str

        @classmethod
        def from_dict(cls, my_dict: dict[str, Any]):
            return cls(dummy_config=my_dict["dummy_config"])

    gotten_config = config.load_config(
        client_name="dummy-client",
        extra_sections=[ExtraSection],
    )

    assert gotten_config.extra_section == ExtraSection(dummy_config="dummy_value")
