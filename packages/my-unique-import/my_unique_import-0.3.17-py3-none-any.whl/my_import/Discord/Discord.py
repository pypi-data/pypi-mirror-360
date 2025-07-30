import logging
from typing import Optional
import discord
from discord.utils import MISSING


class DiscordClient(discord.Client):

    def __init__(self, *, intents=None, token=None, **options):
        if intents is None:
            intents = discord.Intents.all()
        self.token = token
        self.message_logger = []
        super().__init__(intents=intents, **options)

    async def on_ready(self):
        print('Connected to bot: {}'.format(self.user.name))
        print('Bot ID: {}'.format(self.user.id))

    async def on_message(self, message):
        self.message_logger.append(message)

        if message.author == self.user:
            return

        await self.message(message)

    async def message(self, message):
        pass

    def run(
            self,
            token: str = None,
            *,
            reconnect: bool = True,
            log_handler: Optional[logging.Handler] = MISSING,
            log_formatter: logging.Formatter = MISSING,
            log_level: int = MISSING,
            root_logger: bool = False,
    ) -> None:
        if token is None:
            token = self.token
        try:
            super().run(token, reconnect=reconnect, log_handler=log_handler,
                        log_formatter=log_formatter, log_level=log_level, root_logger=root_logger)
        except SystemExit:
            print("Process terminated gracefully")
