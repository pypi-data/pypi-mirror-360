import time
import telegram
from .helpers import get_env_variable
from telegram.error import RetryAfter


class TelegramClient:
    def __init__(self, token=None):
        self.token = token or get_env_variable("TELEGRAM_BOT_TOKEN")
        self.telegram = telegram.Bot(token=self.token)

    async def send_message(
            self, chat_id, text, parse_mode=None, disable_notification=False,
            max_retries=5, timeout_delay=20
    ):
        retries = 0

        while retries < max_retries:
            try:
                return await self.telegram.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode=parse_mode,
                    disable_notification=disable_notification,
                    read_timeout=timeout_delay
                )
            except RetryAfter as e:
                wait_time = int(e.retry_after) + 1
                time.sleep(wait_time)

            retries += 1
