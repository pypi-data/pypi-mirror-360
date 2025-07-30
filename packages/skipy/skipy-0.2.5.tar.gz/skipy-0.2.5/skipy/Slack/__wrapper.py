import json

import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackWebClient:
    def __init__(self, token):
        self.client = WebClient(token=token)

    def upload_file(self, channel_id, file_path, title=None, initial_comment=None):
        try:
            response = self.client.files_upload_v2(
                channel=channel_id,
                file=file_path,
                title=title,
                initial_comment=initial_comment,
            )
            print(f"File uploaded successfully. File ID: {response['file']['id']}")
        except SlackApiError as e:
            print(f"Error uploading file: {e.response['error']}")

    def post_snippet(
        self,
        channel_id,
        text_snippet="This is test snippet",
        title=None,
        initial_comment=None,
    ):
        try:
            response = self.client.files_upload_v2(
                channel=channel_id,
                content=text_snippet,
                title=title,
                initial_comment=initial_comment,
            )
            print(f"File uploaded successfully. File ID: {response['file']['id']}")
        except SlackApiError as e:
            print(f"Error uploading file: {e.response['error']}")


class Slack:
    def __init__(self, web_hook_url):
        self.web_hook_url = web_hook_url

    def post(self, msg, username="Notification-Bot"):
        requests.post(
            self.web_hook_url,
            data=json.dumps(
                {
                    "text": msg,
                    "username": username,
                    "icon_emoji": ":smile_cat:",
                    "link_names": 1,
                }
            ),
        )
