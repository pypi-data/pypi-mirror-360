import os
import pathlib

import discord
from dotenv import dotenv_values


def intents() -> discord.Intents:
    """Return intents with members and voice states enabled."""
    intents = discord.Intents.default()
    intents.members = True
    intents.voice_states = True
    return intents


def find_token() -> str:
    """Locate the Discord token using several fallbacks."""
    # priority 1: command line (exported for systemd template)
    if token := os.getenv("_VOICEBOT_TOKEN_CLI"):
        return token

    # priority 2: plain env var
    if token := os.getenv("DISCORD_TOKEN"):
        return token

    # priority 3: .env in XDG config or cwd
    paths = [
        pathlib.Path(os.getenv("XDG_CONFIG_HOME", "~/.config")).expanduser()
        / "voicebot"
        / ".env",
        pathlib.Path(".env"),
    ]
    for p in paths:
        if p.exists():
            return dotenv_values(p).get("DISCORD_TOKEN", "") or ""

    raise RuntimeError("Discord token not found. See README.")
