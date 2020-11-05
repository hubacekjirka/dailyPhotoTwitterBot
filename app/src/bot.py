import os
import sys
import logging

from config import tweetingEnabled, telegramingEnabled, chatIdFolder
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
    LOGGER.info("Bot started")

    # Picks a photo from the backlog's photo folder and stores it
    # as a Photo object.
    #     Optionally: gets photo from S3
    try:
        CURRENTDIR = os.path.dirname(os.path.realpath(__file__))
        # initialize a PhotoPicker object, sets paths
        photoPicker = PhotoPicker(CURRENTDIR)

        # Retrieves a photo file and creates a photo object
        pickedPhoto = photoPicker.getPhoto()

    except Exception as e:
        LOGGER.error(f"Couldn't retrieve the photo file. Error: {e}")
        sys.exit()

    LOGGER.debug(f"Filename: {pickedPhoto.fileName}")

    # Tweeting
    try:
        tweetPostResult = 0
        tweet = TweetPost(pickedPhoto)
        LOGGER.debug(tweet.tweetPostText)

        if tweetingEnabled:
            tweetPostResult, tweetPostStatus = tweet.postTweetPost()
            LOGGER.debug(tweetPostResult)
            LOGGER.debug(str(tweetPostStatus).encode("utf-8"))

    except Exception as e:
        LOGGER.info(f"Error occured during tweeting. Error: {e}")
        sys.exit()

    # Telegraming
    try:
        telegramPostResult = 0
        chatIdFilePath = os.path.join(chatIdFolder, "chatIds.json")
        telegramMessage = TelegramPost(pickedPhoto, chatIdFilePath)
        if tweet is not None:
            if tweet.place is not None:
                if tweet.place.place_type == "admin":
                    # if no city granularity is available, the api returns admin as the best match
                    telegramMessage.setLocation(f"{tweet.place.full_name}")
                else:
                    telegramMessage.setLocation(f"{tweet.place.full_name}, {tweet.place.country}")
        # post it on telegram
        if telegramingEnabled:
            telegramPostResult = telegramMessage.postTelegramPost()
    except Exception as e:
        LOGGER.info(f"Error occured during telegramming. Error: {e}")
        sys.exit()

    # move file, if posting is succesful and enabled on all platforms
    # TODO: refactor this in the "future" to instance variables
    try:
        if (
            tweetPostResult == 0
            and telegramPostResult == 0
            and tweetingEnabled
            and telegramingEnabled
        ):

            LOGGER.debug(f"Moving {pickedPhoto.fileName} to the used photo folder.")

            # if everything goes well, move the photo file to the the
            # archive folders
            photoPicker.copyPhotoToArchive()

            photoPicker.copyPhotoToArchiveS3()
            photoPicker.removePhotoFromBacklogS3()
    except Exception as e:
        LOGGER.error(e)
        sys.exit()

    LOGGER.info("So, O-Ren...any more subordinates for me to kill?")
