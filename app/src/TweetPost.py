from Post import Post
from Photo import Photo
from config import (
    access_token,
    access_token_secret,
    consumer_key,
    consumer_secret,
)
import tweepy
from tweepy import TweepError
import logging

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel("DEBUG")


class TweetPost(Post):
    def __init__(self, photo: Photo):
        super().__init__(photo)
        self.api = self.getApi()
        self.apiCredentialsValid = self.verifyApiCredentials(self.api)
        self.place = self.getLocationDetails()
        self.closureText = "TwitterBot (GitHub: http://bit.ly/PotDGithub)"
        self.tweetPostText = (
            f"{self.introText} "
            f"{self.exifSection} {self.closureText} "
            f"{photo.exifHashtags} {photo.tensorFlowHashtags}"
        )

    def getApi(self):
        # Authenticate using application keys
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        return api

    def verifyApiCredentials(self, api):
        try:
            api.verify_credentials()
            LOGGER.debug("Twitter authentication OK")
            return True

        except Exception as e:
            LOGGER.error(f"Error during authentication, error: {e}")
            return False

    def getLocationDetails(self):
        # Using Twitter's API to reverse decode photo's coordinates
        # to location: https://developer.twitter.com/en/docs/geo/places-near-location/api-reference/get-geo-reverse_geocode.html # noqa: E501
        try:
            gpsInfo = self.photo.exifData.get("GPSInfo")
            if gpsInfo is None:
                return None

            latD = float(gpsInfo[2][0][0]) / float(gpsInfo[2][0][1])
            latM = float(gpsInfo[2][1][0]) / float(gpsInfo[2][1][1])
            latS = float(gpsInfo[2][2][0]) / float(gpsInfo[2][2][1])
            lonD = float(gpsInfo[4][0][0]) / float(gpsInfo[4][0][1])
            lonM = float(gpsInfo[4][1][0]) / float(gpsInfo[4][1][1])
            lonS = float(gpsInfo[4][2][0]) / float(gpsInfo[4][2][1])

            lat = latD + latM / 60 + latS / 3600
            lon = lonD + lonM / 60 + lonS / 3600

            # flat earth fix
            if gpsInfo[1] == "S":
                lat = lat * (-1)
            if gpsInfo[3] == "W":
                lon = lon * (-1)

            LOGGER.debug(f"LAT: {lat}")
            LOGGER.debug(f"LON: {lon}")

            # picking only the first item as it seems to be the most
            # relevant one
            return self.api.reverse_geocode(lat=lat, lon=lon, granularity="admin")[0]
        except KeyError as e:
            LOGGER.error("Geo data not present " + e)
        except TweepError as e:
            LOGGER.error("Couldn't resolve location " + str(e.response.content))
        except Exception as e:
            LOGGER.error(
                f"Couldn't resolve location based on exif's coordinates, error: {e}"
            )

        return None

    def postTweetPost(self):
        if len(self.tweetPostText) > 275:
            self.tweetPostText = f"{self.tweetPostText[:275]}..."

        kwargs = {}
        # not today
        kwargs["possibly_sensitive"] = False

        if self.place is not None:
            kwargs["place_id"] = self.place.id

        if self.tweetPostText is not None:
            kwargs["status"] = self.tweetPostText

        postResult = -1
        postStatus = None
        try:
            postStatus = self.api.update_with_media(self.photo.photoPath, **kwargs)
            postResult = 0
        except Exception as e:
            LOGGER.error(e)

        return postResult, postStatus
