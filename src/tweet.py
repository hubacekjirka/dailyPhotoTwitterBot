import tweepy
import os 
from os import listdir
from random import randint
import sys
import hashlib
from PIL import JpegImagePlugin, Image
from PIL.ExifTags import TAGS

import PIL.Image


from config import (
    access_token,
    access_token_secret,
    consumer_key,
    consumer_secret
)

CURRENTDIR = os.path.dirname(os.path.realpath(__file__))
INTROTEXT = "Photo of the day."
CLOSURETEXT = "By photo of the day Twitter bot (github: )." #TODO

photoFolder = os.path.join(CURRENTDIR,"photo")

def getMd5Hash(filePath):
    bufferSize = 65536
    md5 = hashlib.md5()

    with open(filePath, 'rb') as f:
        while True:
            data = f.read(bufferSize)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()

def getPhotosMd5Hash():
    photos = [f for f in listdir(photoFolder)]
    output = []
    for photo in photos:
        output.append({
            "file": photo,
            "md5": getMd5Hash(os.path.join(photoFolder,photo)),
        })
    return output

def getExif(photoPath):
    img = PIL.Image.open(photoPath)
    exif = {
        PIL.ExifTags.TAGS[k]: v
        for k, v in img._getexif().items()
        if k in PIL.ExifTags.TAGS
    }
    return exif

def getTweetMessage(introText,exifData,closureText):
    tweetMessage = f"{introText} "

    exifSection = ""
    if exifData.get("Model"):
        exifSection += f"shot on {exifData.get('Model')}"

    if exifData.get("DateTimeOriginal"):
        if exifSection != "":
            exifSection += ", "
        exifSection += f"sometimes in {exifData.get('DateTimeOriginal')[:4]}"

    if exifSection != "":
        exifSection = exifSection.capitalize()
        exifSection += "."
    
    tweetMessage = f"{introText} {exifSection} {closureText}"
    return tweetMessage

def isSimilarAlreadyPosted():
    # TODO: https://realpython.com/fingerprinting-images-for-near-duplicate-detection/
    pass

def postMediaUpdate(api,filePath,tweetMessage):
    result=0
    try:
        api.update_with_media(
            os.path.join(CURRENTDIR,"photo",pickedPhoto),
            status = tweetMessage)
    except Exception as e:
        print(e)
        result=-1
    return result

### Authenticate using application keys
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


### pick a photo at random
photos = [f for f in listdir(photoFolder)]
pickedPhoto = photos[randint(0,len(photos)-1)]

### get its exif information
exifData = getExif(os.path.join(CURRENTDIR,"photo",pickedPhoto))
tweetMessage = getTweetMessage(INTROTEXT,exifData,CLOSURETEXT)

### post it
postStatus = 0
# postStatus = postMediaUpdate(
#     api,
#     os.path.join(CURRENTDIR,"photo",pickedPhoto),
#     tweetMessage)

### move file, if posting is succesful
if postStatus == 0:
    #move file
    os.rename(os.path.join(CURRENTDIR,"photo",pickedPhoto),
    os.path.join(CURRENTDIR,"usedPhoto",pickedPhoto))