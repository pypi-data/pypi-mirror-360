from unittest.mock import Mock

import discord

from discord_voicebot import bot as bot_mod


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
