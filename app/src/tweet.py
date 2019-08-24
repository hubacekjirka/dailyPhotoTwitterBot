from PIL import JpegImagePlugin, Image
from PIL.ExifTags import TAGS
from os import listdir
from random import randint
import sys
import hashlib
import tweepy
import os
import PIL.Image
import telegram
from classify_image import classifyImage

from Photo import Photo
from TweetPost import TweetPost

from config import (
    access_token,
    access_token_secret,
    consumer_key,
    consumer_secret
)

CURRENTDIR = os.path.dirname(os.path.realpath(__file__))


debug = True
tweetingEnabled = False
telegramingEnabled = False
photoFolder = os.path.join(CURRENTDIR,"photos","backlog")
usedPhotoFolder = os.path.join(CURRENTDIR,"photos","usedPhoto")


def postMediaUpdate(api,filePath,tweetMessage):
    result=0
    try:
        api.update_with_media(
            filePath,
            status = tweetMessage)
    except Exception as e:
        print(e)
        result=-1
    return result


if __name__ == "__main__":
    ### Authenticate using application keys
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)


    ### pick a photo at random
    
    photos = [f for f in listdir(photoFolder) if f.endswith("jpg")]
    pickedPhoto = Photo(os.path.join(
        photoFolder,
        photos[randint(0,len(photos)-1)])
    )

    tweet = TweetPost(pickedPhoto)
    
    if debug:
        print(f"Filename: {pickedPhoto}")

    ### post it on twitter
    postStatus = 0
    if tweetingEnabled:
        if len(postMessage) > 275:
            tweetMessage = f"{postMessage[:275]}..."
        else:
            tweetMessage = postMessage

        postStatus = postMediaUpdate(
            api,
            os.path.join(photoFolder,pickedPhoto),
            tweetMessage
        )

    ### post it on telegram - only bother if everythong goes as expected
    if telegramingEnabled and postStatus == 0:
        telegramMessage = f"{postMessage} | Sent with ❤️"
        postStatus = telegram.sendImage(
            os.path.join(photoFolder,pickedPhoto),
            telegramMessage)

    ### move file, if posting is succesful and enabled on all platforms
    if postStatus == 0 and tweetingEnabled and telegramingEnabled:
        os.rename(
            os.path.join(photoFolder,pickedPhoto),
            os.path.join(usedPhotoFolder,pickedPhoto)
        )