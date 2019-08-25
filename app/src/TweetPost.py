from Post import Post
from Photo import Photo
from config import (
    access_token,
    access_token_secret,
    consumer_key,
    consumer_secret
)
import tweepy

class TweetPost(Post):

    def __init__(self, photo: Photo):
        super().__init__(photo)
        self.api = self.getApi()
        self.apiCredentialsValid = self.verifyApiCredentials(self.api)
        self.closureText = "TwitterBot (GitHub: http://bit.ly/2YGoHrG)"
        self.tweetPostText = f"{self.introText} " \
            f"{self.exifSection} {self.closureText} " \
            f"{photo.exifHashtags} {photo.tensorFlowHashtags}"

    def getApi(self):
        ### Authenticate using application keys
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        return api

    def verifyApiCredentials(self, api):
        try:
            api.verify_credentials()
            print("Twitter authentication OK")
            return True
        except:
            print("Error during authentication")
            return False

    def getLocationDetails(self):
        pass
        # print(getExif(photo)['GPSInfo'][2])
        # print(getExif(photo)['GPSInfo'][4])

        # latD = float(getExif(photo)['GPSInfo'][2][0][0]) / float(getExif(photo)['GPSInfo'][2][0][1])
        # latM = float(getExif(photo)['GPSInfo'][2][1][0]) / float(getExif(photo)['GPSInfo'][2][1][1])
        # latS = float(getExif(photo)['GPSInfo'][2][2][0]) / float(getExif(photo)['GPSInfo'][2][2][1])
        # lonD = float(getExif(photo)['GPSInfo'][4][0][0]) / float(getExif(photo)['GPSInfo'][4][0][1])
        # lonM = float(getExif(photo)['GPSInfo'][4][1][0]) / float(getExif(photo)['GPSInfo'][4][1][1])
        # lonS = float(getExif(photo)['GPSInfo'][4][2][0]) / float(getExif(photo)['GPSInfo'][4][2][1])


        # print(latD)
        # print(latM)
        # print(latS)
        # print(lonD)
        # print(lonM)
        # print(lonS)

        # print(latD + latM / 60 + latS / 3600)
        # print(lonD + lonM / 60 + lonS / 3600)

        # aa = api.reverse_geocode(
        #     lat = "48.166944",
        #     lon = "11.551667",
        #     granularity = "admin"
        #     )

        # print(aa)

        # print(aa[0])
        # print(aa[0].id)
        # print(aa[0].full_name)

    def postTweetPost(self):
        if len(self.tweetPostText) > 275:
            self.tweetPostText = f"{self.tweetPostText[:275]}..."

        kwargs = {}
        # not today
        kwargs["possibly_sensitive"] = False
        if self.tweetPostText is not None: 
            kwargs["status"] = self.tweetPostText

        postResult = -1
        postStatus = None
        try:
            postStatus = self.api.update_with_media(
                self.photo.photoPath,
                **kwargs
            )
            postResult = 0
        except Exception as e:
            print(e)

        return postResult, postStatus