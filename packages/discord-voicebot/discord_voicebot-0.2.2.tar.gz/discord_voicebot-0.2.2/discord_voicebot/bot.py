import logging
import random

import discord
from discord.ext import commands

from . import util

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

REGULAR_MESSAGES = [
    "is now hanging out in",
    "has joined",
    "is chilling in",
    "jumped into",
    "entered",
    "is vibing in",
    "is now in",
]


def is_member_joined(before: discord.VoiceState, after: discord.VoiceState) -> bool:
    return before.channel is None and after.channel is not None


def get_channel_for_message(bot_client, guild_id):
    guild = bot_client.get_guild(guild_id)
    for ch in guild.text_channels:
        if ch.permissions_for(guild.me).send_messages:
            return ch
    return None


class VoiceBot:
    def __init__(self) -> None:
        self.token = util.find_token()
        self.bot = commands.Bot(command_prefix="!", intents=util.intents())

        self.bot.event(self.on_ready)
        self.bot.event(self.on_voice_state_update)

    async def on_ready(self):
        if self.bot.user is not None:
            logger.info("Logged in as %s (id=%s)", self.bot.user, self.bot.user.id)
        else:
            logger.error("Bot user is not initialized.")

    async def on_voice_state_update(self, member, before, after):
        if is_member_joined(before, after):
            to_channel = get_channel_for_message(self.bot, member.guild.id)
            if to_channel is None:
                logger.warning(
                    "No available channel to send join message for guild %s",
                    member.guild.id,
                )
                return
            message_text = random.choice(REGULAR_MESSAGES)
            logger.info("%s joined %s", member.display_name, after.channel.name)
            await to_channel.send(
                f"{member.display_name} {message_text} **{after.channel.name}**!",
                delete_after=300,
            )
            # TODO: store to DB if desired

    def run(self) -> None:
        logging.info("Starting bot")
        self.bot.run(self.token)


def main() -> None:
    VoiceBot().run()
