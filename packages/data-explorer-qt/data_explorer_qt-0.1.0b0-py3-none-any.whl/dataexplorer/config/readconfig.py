# pyright: reportAny=false, reportExplicitAny=false
from typing import Any
import toml
from pathlib import Path

starting_path = Path(__file__)
config_path = starting_path.parent / "config.toml"


def get_config() -> dict[str, Any]:
    config = toml.load(config_path)
    config = construct_stylesheets(config)
    return config


def construct_stylesheets(config: dict[str, Any]) -> dict[str, Any]:
    for key in config["Themes"]:
        assert isinstance(key, str)
        config["Themes"][key] = _theme_constructor(config["Themes"][key])
    return config


def _theme_constructor(theme_input: dict[str, str] | str) -> str:
    if isinstance(theme_input, dict):
        return "\n".join([_theme_constructor(theme_input[key]) for key in theme_input])
    else:
        return theme_input


def get_list_of_themes(config: dict[str, Any]):
    return list(config["Themes"].keys())


CONFIG = get_config()
CONFIG_STYLESHEET = CONFIG["Themes"]["Dark"]
