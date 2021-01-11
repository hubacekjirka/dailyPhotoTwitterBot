from Post import Post
from PhotoWithBenefits import PhotoWithBenefits
from config import telegram_token
import requests
import urllib
import json
import time
import os
import logging

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel("DEBUG")


class TelegramPost(Post):
    def __init__(self, photo: PhotoWithBenefits, chat_id_file_path):
        super().__init__(photo)
        self._chat_id_file_path = chat_id_file_path
        self._chat_ids = self._update_and_get_recipient_list(self._chat_id_file_path)
        self._signature = "TelegramBot (GitHub: http://bit.ly/PotDGithub)"
        self._location_name = None
        self._telegram_post_text = self._compose_telegram_post_text()

    def _compose_telegram_post_text(self):
        if self._location_name is not None:
            location_section = f"Shot in {self._location_name} "
        else:
            location_section = ""

        return (
            f"{self._intro_text} "
            f"{self._exif_section} {self._signature} "
            f"{self._photo._content_prediction_hashtags} "
            f"{location_section}"
            f"| Sent with ❤️"
        )

    def _update_and_get_recipient_list(self, chat_id_file_path):
        # Download updated from the Telegram's bot API
        # See: https://core.telegram.org/bots/api

        updates_url = f"https://api.telegram.org/bot{telegram_token}/getUpdates"
        response = urllib.request.urlopen(updates_url)
        data = json.loads(response.read().decode())

        # get chatIds from the getUpdates endpoint, extract chatIds of private
        # conversations only ~ a private message sent from users asking bot
        # to be subscribed to the daily delivery
        chat_ids = set(
            [
                message["message"]["chat"]["id"]
                for message in data["result"]
                if message["message"]["chat"]["type"] == "private"
            ]
        )

        # Retrieve preserved chatIds from the existing json file
        if os.path.isfile(chat_id_file_path):
            with open(chat_id_file_path) as json_data:
                json_content = json.load(json_data)
                # Put chatIds into the existing chatIds set
                list(map(lambda x: chat_ids.add(x), json_content["chatIds"]))

        # Save all chatIds to the JSON file
        with open(chat_id_file_path, "w") as json_data:
            json_data.write(json.dumps({"chatIds": list(chat_ids)}))

        return chat_ids

    def _set_location(self, location_name):
        self._location_name = location_name

    def post_telegram_post(self):
        # refresh telegram's message
        self._telegram_post_text = self._compose_telegram_post_text()
        result = 0
        try:
            """
            https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bot-39s-subscribers-at-once
            How can I message all of my bot's subscribers at once?
            Unfortunately, at this moment we don't have methods for
            sending bulk messages, e.g. notifications. We may add
            something along these lines in the future.
            #
            In order to avoid hitting our limits when sending out mass
            notifications, consider spreading them over longer intervals,
            e.g. 8-12 hours. The API will not allow more than ~30 messages
            to different users per second, if you go over that, you'll
            start getting 429 errors.
            """

            # push the message to every chatId
            for chatId in self._chat_ids:
                url = f"https://api.telegram.org/bot{telegram_token}/sendPhoto"
                files = {"photo": open(self._photo._file_path, "rb")}
                data = {"chat_id": chatId, "caption": self._telegram_post_text}
                response = requests.post(url, files=files, data=data)
                if response.status_code != 200:
                    raise Exception(f"{response.status_code} {response.reason}")
                # being nice to the Telegram's api
                time.sleep(0.05)
        except Exception as e:
            LOGGER.error(e)
            result = -1

        return result
