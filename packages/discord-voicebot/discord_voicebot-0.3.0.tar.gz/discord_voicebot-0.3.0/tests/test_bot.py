from unittest.mock import Mock

import discord

from discord_voicebot import bot as bot_mod


def test_main_cli_token_sets_env(monkeypatch):
    monkeypatch.delenv("_VOICEBOT_TOKEN_CLI", raising=False)
    captured = {}

    def fake_run(self):
        captured["token"] = self.token

    monkeypatch.setattr(bot_mod.VoiceBot, "run", fake_run)
    bot_mod.main(["--token", "cli-token"])
    assert captured["token"] == "cli-token"


def test_main_health_args(monkeypatch):
    captured = {}

    def fake_run(self):
        captured["url"] = self.ping_url
        captured["interval"] = self.ping_interval

    monkeypatch.setattr(bot_mod.VoiceBot, "run", fake_run)
    bot_mod.main([
        "--ping-url",
        "http://example.com",
        "--ping-interval",
        "10",
    ])
    assert captured["url"] == "http://example.com"
    assert captured["interval"] == 10


def test_main_health_env(monkeypatch):
    for var in [
        "_VOICEBOT_PING_URL_CLI",
        "_VOICEBOT_PING_INTERVAL_CLI",
    ]:
        monkeypatch.delenv(var, raising=False)
    captured = {}

    def fake_run(self):
        captured["url"] = self.ping_url
        captured["interval"] = self.ping_interval

    monkeypatch.setattr(bot_mod.VoiceBot, "run", fake_run)
    monkeypatch.setenv("VOICEBOT_PING_URL", "http://env")
    monkeypatch.setenv("VOICEBOT_PING_INTERVAL", "55")
    bot_mod.main([])
    assert captured["url"] == "http://env"
    assert captured["interval"] == 55


def test_is_member_joined_positive():
    before = Mock(spec=discord.VoiceState)
    before.channel = None
    after = Mock(spec=discord.VoiceState)
    after.channel = Mock()
    assert bot_mod.is_member_joined(before, after)


def test_is_member_joined_negative():
    before = Mock(spec=discord.VoiceState)
    before.channel = Mock()
    after = Mock(spec=discord.VoiceState)
    after.channel = Mock()
    assert not bot_mod.is_member_joined(before, after)


class DummyPermission:
    def __init__(self, send):
        self.send_messages = send


class DummyChannel:
    def __init__(self, send):
        self._send = send

    def permissions_for(self, _):
        return DummyPermission(self._send)


class DummyGuild:
    def __init__(self, channels):
        self.id = 123
        self.text_channels = channels
        self.me = object()


class DummyBot:
    def __init__(self, guild):
        self.guild = guild

    def get_guild(self, guild_id):
        assert guild_id == self.guild.id
        return self.guild


def test_get_channel_for_message_returns_channel():
    channels = [DummyChannel(False), DummyChannel(True)]
    guild = DummyGuild(channels)
    client = DummyBot(guild)
    assert bot_mod.get_channel_for_message(client, guild.id) is channels[1]


def test_get_channel_for_message_returns_none():
    channels = [DummyChannel(False)]
    guild = DummyGuild(channels)
    client = DummyBot(guild)
    assert bot_mod.get_channel_for_message(client, guild.id) is None
