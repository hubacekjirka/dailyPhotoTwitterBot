import os
import sys
import logging
import sentry_sdk

from config import (
    tweeting_enabled,
    telegraming_enabled,
    chat_id_folder,
    photo_source,
    sentry_api_key,
)
from sentry_sdk import set_level
from sentry_sdk.integrations.logging import LoggingIntegration  # noqa: F401

from TweetPost import TweetPost

from TelegramPost import TelegramPost
from PhotoPicker import PhotoPicker

LOGGER = logging.getLogger(__file__)
LOGGER.setLevel("DEBUG")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(funcName)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if sentry_api_key is not None or not sentry_api_key == "":
        sentry_sdk.init(
            sentry_api_key,
            traces_sample_rate=1.0)
        set_level("info")
    else:
        LOGGER.warning("Sentry logging not started")

    LOGGER.info("Bot started")

    """
    The following try-except blogs uses PhotoPicker to retrieve a photo
    (Optinally from S3) and using the photo instantiates a Photo Object
    """
    try:
        CURRENTDIR = os.path.dirname(os.path.realpath(__file__))
        photo_picker = PhotoPicker(CURRENTDIR)

        # Retrieves a photo file and creates a photo object
        photo = photo_picker.get_photo()

    except Exception as e:
        LOGGER.exception(f"Couldn't retrieve the photo file. Error: {e}")
        sys.exit()

    # Tweeting
    try:
        tweet_posting_result = 0
        tweet = TweetPost(photo)
        LOGGER.debug(f"Tweet post text: {tweet._tweet_post_text}")

        if tweeting_enabled:
            tweet_posting_result, tweet_post_status = tweet.post_tweet()
            LOGGER.debug(tweet_posting_result)
            LOGGER.debug(str(tweet_post_status).encode("utf-8"))

    except Exception as e:
        LOGGER.exception(f"Error occured during tweeting. Error: {e}")
        sys.exit()

    # Telegraming
    try:
        telegram_post_result = 0
        chat_id_file_path = os.path.join(chat_id_folder, "chatIds.json")
        telegram_message = TelegramPost(photo, chat_id_file_path)
        if tweet is not None:
            # TODO: Remove this dependenci on the fact tweeting needs to be
            # configured AND enabled
            if tweet._geo is not None:
                if tweet._geo.place_type == "admin":
                    # if no city granularity is available, the api returns
                    # admin granularity as the best match
                    telegram_message._set_location(f"{tweet._geo.full_name}")
                else:
                    telegram_message._set_location(f"{tweet._geo.full_name}")
        # post it on telegram
        if telegraming_enabled:
            telegram_post_result = telegram_message.post_telegram_post()
    except Exception as e:
        LOGGER.exception(f"Error occured during telegramming. Error: {e}")
        sys.exit()

    # Move file, if posting is succesful and enabled on all platforms
    # TODO: refactor this in the "future" to instance variables
    try:
        if (
            tweet_posting_result == 0
            and telegram_post_result == 0
            and tweeting_enabled
            and telegraming_enabled
        ):

            LOGGER.debug(f"Moving {photo._file_name} to the used photo folder.")

            # if everything goes well, move the photo file to the the
            # archive folders
            photo_picker.copy_file_to_archive()

            # ... and if we're using S3, move it there too
            if photo_source == "S3" and not photo._throwback_thursday:
                photo_picker.copy_file_to_archive_in_s3()
                photo_picker.remove_file_from_backlog_in_s3()
    except Exception as e:
        LOGGER.exception(e)
        sys.exit()

    LOGGER.info("So, O-Ren...any more subordinates for me to kill?")
