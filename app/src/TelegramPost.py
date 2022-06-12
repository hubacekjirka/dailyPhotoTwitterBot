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

# Keep trying for two mintues
POST_RETRY_COUNT = 24  # retry posting 10 times
POST_RETRY_TIMEOUT = 5  # wait 10 seconds


class TelegramPost(Post):
    def __init__(self, photo: PhotoWithBenefits, chat_id_file_path):
        super().__init__(photo)
        self._chat_id_file_path = chat_id_file_path
        self._chat_ids = None

        try:
            # Dynamic adding of chats disabled, no use of it now
            # self._chat_ids = self._update_and_get_recipient_list(
            #     self._chat_id_file_path
            # )

            self._chat_ids = self._get_local_recipient_list(self._chat_id_file_path)

        except Exception as e:
            LOGGER.warning(f"Couldn't update recipient list. Error: {e}")

        self._signature = "TelegramBot (Github: http://bit.ly/PotDGithub)"
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

    # Retrieve locally specified chat_ids
    def _get_local_recipient_list(self, chat_id_file_path):
        try:
            chat_ids = set()
            with open(chat_id_file_path) as json_data:
                json_content = json.load(json_data)
                # Put chatIds into the existing chatIds set
                list(map(lambda x: chat_ids.add(x), json_content["chatIds"]))
                return chat_ids
        except Exception as e:
            LOGGER.error(f"Error gathering chat_ids, {e}")

    def _set_location(self, location_name):
        self._location_name = location_name

    def post_telegram_post(self):
        if self._chat_ids is None:
            raise Exception("No chat_ids as the message recipients set.")

        # refresh telegram's message ~ adds location text
        self._telegram_post_text = self._compose_telegram_post_text()
        result = 0

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

        # push the message to every chat_id
        for chat_id in self._chat_ids:
            LOGGER.info(f"Sending Telegram to {chat_id}")
            # reset counter for new chat_id
            retry_attempt = 1
            while retry_attempt <= POST_RETRY_COUNT:
                try:
                    url = f"https://api.telegram.org/bot{telegram_token}/sendPhoto"
                    files = {"photo": open(self._photo._file_path, "rb")}
                    data = {"chat_id": chat_id, "caption": self._telegram_post_text}
                    response = requests.post(url, files=files, data=data)

                    if response.status_code == 200:
                        LOGGER.info(f"Sent telegram to {chat_id}")
                    elif response.status_code == 403:
                        LOGGER.warning(
                            f"Couldn't send message to chat_id {chat_id}"
                            + f"because of: {response.status_code}; {response.reason}"
                            + f"{response.text}"
                        )
                    else:
                        raise Exception(
                            f"Something's wrong with chat_id {chat_id}: "
                            f" {response.status_code}; {response.reason}; "
                            + f"{response.text}"
                        )
                    # being nice to the Telegram's api and wait 0.05 sec
                    time.sleep(0.05)
                    break
                except Exception as e:
                    LOGGER.error(e)
                    if retry_attempt == POST_RETRY_COUNT:
                        raise Exception(
                            f"Failed {retry_attempt} times to send"
                            + f"Telegram message to {chat_id}. Giving up ..."
                        )
                    time.sleep(POST_RETRY_TIMEOUT)
                    retry_attempt += 1

        return result
