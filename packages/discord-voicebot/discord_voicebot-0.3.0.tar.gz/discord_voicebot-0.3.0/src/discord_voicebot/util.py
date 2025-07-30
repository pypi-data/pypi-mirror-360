import os
import pathlib
from typing import Callable, TypeVar

import discord
from dotenv import dotenv_values

T = TypeVar("T")


def intents() -> discord.Intents:
    """Return intents with members and voice states enabled."""
    intents = discord.Intents.default()
    intents.members = True
    intents.voice_states = True
    return intents


def _env_file() -> pathlib.Path:
    return (
        pathlib.Path(os.getenv("XDG_CONFIG_HOME", "~/.config")).expanduser()
        / "voicebot"
        / ".env"
    )


def _find_env_var(
    cli_var: str,
    plain_var: str,
    *,
    cast: Callable[[str], T] = str,
    default: T | None = None,
) -> T | None:
    if val := os.getenv(cli_var):
        try:
            return cast(val)
        except Exception:
            return default
    if val := os.getenv(plain_var):
        try:
            return cast(val)
        except Exception:
            return default
    env_file = _env_file()
    if env_file.exists():
        data = dotenv_values(env_file)
        if val := data.get(plain_var):
            try:
                return cast(val)
            except Exception:
                return default
    return default


def find_token() -> str:
    """Locate the Discord token using several fallbacks."""
    token = _find_env_var("_VOICEBOT_TOKEN_CLI", "DISCORD_TOKEN")
    if token:
        return token
    raise RuntimeError("Discord token not found. See README.")


def find_ping_url(default: str | None = None) -> str | None:
    """Return the health check URL from env or config."""
    return _find_env_var(
        "_VOICEBOT_PING_URL_CLI",
        "VOICEBOT_PING_URL",
        default=default,
    )


def find_ping_interval(default: int = 300) -> int:
    """Return the ping interval in seconds from env or config."""
    result = _find_env_var(
        "_VOICEBOT_PING_INTERVAL_CLI",
        "VOICEBOT_PING_INTERVAL",
        cast=int,
        default=default,
    )
    return result if isinstance(result, int) else default
