import argparse
import asyncio
import logging
import os
import random

import discord
import httpx
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
    def __init__(
        self,
        ping_url: str | None = None,
        ping_interval: int | None = None,
    ) -> None:
        self.token = util.find_token()
        self.ping_url = ping_url if ping_url is not None else util.find_ping_url()
        self.ping_interval = (
            ping_interval if ping_interval is not None else util.find_ping_interval()
        )
        self.bot = commands.Bot(command_prefix="!", intents=util.intents())

        self.bot.event(self.on_ready)
        self.bot.event(self.on_voice_state_update)

    async def healthcheck_pinger(self) -> None:
        if not self.ping_url:
            return
        while True:
            try:
                async with httpx.AsyncClient() as client:
                    await client.get(self.ping_url, timeout=5)
            except Exception as exc:
                logger.warning("Healthcheck ping failed: %s", exc)
            await asyncio.sleep(self.ping_interval)

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

        async def _runner() -> None:
            asyncio.create_task(self.healthcheck_pinger())
            await self.bot.start(self.token)

        asyncio.run(_runner())


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the Discord VoiceBot")
    parser.add_argument("--token", help="Discord bot token")
    parser.add_argument("--ping-url", help="URL to ping for health checks")
    parser.add_argument(
        "--ping-interval",
        type=int,
        default=None,
        help="Seconds between health check pings",
    )
    args = parser.parse_args(argv)

    if args.token:
        os.environ["_VOICEBOT_TOKEN_CLI"] = args.token
    if args.ping_url:
        os.environ["_VOICEBOT_PING_URL_CLI"] = args.ping_url
    if args.ping_interval is not None:
        os.environ["_VOICEBOT_PING_INTERVAL_CLI"] = str(args.ping_interval)

    VoiceBot(ping_url=args.ping_url, ping_interval=args.ping_interval).run()
