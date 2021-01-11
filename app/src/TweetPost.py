from Post import Post
from PhotoWithBenefits import PhotoWithBenefits
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
    def __init__(self, photo: PhotoWithBenefits):
        super().__init__(photo)
        self._api = self._get_api()
        self._api_credentials_valid = self._verify_api_credentials(self._api)
        self._geo = self._get_geo()
        self._bot_signature = "TwitterBot (GitHub: http://bit.ly/PotDGithub)"
        self._tweet_post_text = (
            f"{self._intro_text} "
            f"{self._exif_section} {self._bot_signature} "
            f"{photo._content_prediction_hashtags}"
        )

    def _get_api(self):
        # Authenticate using application keys
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        return api

    def _verify_api_credentials(self, api):
        try:
            api.verify_credentials()
            LOGGER.debug("Twitter authentication OK")
            return True

        except Exception as e:
            LOGGER.error(f"Error during authentication, error: {e}")
            return False

    def _get_geo(self):
        # Using Twitter's API to reverse decode photo's coordinates
        # to location: https://developer.twitter.com/en/docs/geo/places-near-location/api-reference/get-geo-reverse_geocode.html # noqa: E501
        try:
            gpsInfo = self._photo._exif.get("GPSInfo")
            if gpsInfo is None:
                return None

            lat_d = float(gpsInfo[2][0])
            lat_m = float(gpsInfo[2][1])
            lat_s = float(gpsInfo[2][2])
            lon_d = float(gpsInfo[4][0])
            lon_m = float(gpsInfo[4][1])
            lon_s = float(gpsInfo[4][2])

            lat = lat_d + lat_m / 60 + lat_s / 3600
            lon = lon_d + lon_m / 60 + lon_s / 3600

            # flat earth fix
            if gpsInfo[1] == "S":
                lat = lat * (-1)
            if gpsInfo[3] == "W":
                lon = lon * (-1)

            LOGGER.debug(f"LAT: {lat}")
            LOGGER.debug(f"LON: {lon}")

            locations = None
            # Keep asking twitter
            try:
                locations = self._api.reverse_geocode(
                    lat=lat, lon=lon, granularity="country"
                )
                locations = self._api.reverse_geocode(
                    lat=lat, lon=lon, granularity="admin"
                )
                locations = self._api.reverse_geocode(
                    lat=lat, lon=lon, granularity="city"
                )

            except KeyError:
                pass

            if locations is not None:
                return locations[0]
        except KeyError as e:
            LOGGER.error("Geo data not present or not available " + e)
        except TweepError as e:
            LOGGER.error("Couldn't resolve location " + str(e.response.content))
        except Exception as e:
            LOGGER.error(
                f"Couldn't resolve location based on exif's coordinates, error: {e}"
            )

        return None

    def post_tweet(self):
        if len(self._tweet_post_text) > 275:
            self._tweet_post_text = f"{self._tweet_post_text[:275]}..."

        kwargs = {}
        # not today
        kwargs["possibly_sensitive"] = False

        if self._geo is not None:
            kwargs["place_id"] = self._geo.id

        if self._tweet_post_text is not None:
            kwargs["status"] = self._tweet_post_text

        post_result = -1
        post_status = None
        try:
            post_status = self._api.update_with_media(self._photo._file_path, **kwargs)
            post_result = 0
        except Exception as e:
            LOGGER.error(e)

        return post_result, post_status
