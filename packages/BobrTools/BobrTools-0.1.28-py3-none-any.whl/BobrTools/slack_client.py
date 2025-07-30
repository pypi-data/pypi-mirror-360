from slack_sdk import WebClient
from .helpers import get_env_variable


class SlackClient:
    def __init__(self, token=None):
        self.token = token or get_env_variable("SLACK_BOT_TOKEN")
        self.slack = WebClient(token=self.token)

    def send_message(self, channel, text, thread_ts=None, parse=None):
        return self.slack.chat_postMessage(
            channel=channel,
            text=text,
            thread_ts=thread_ts,
            parse=parse
        )
