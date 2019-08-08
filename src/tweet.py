from PIL import JpegImagePlugin, Image
from PIL.ExifTags import TAGS
from os import listdir
from random import randint
import sys
import hashlib
import tweepy
import os
import PIL.Image


from config import (
    access_token,
    access_token_secret,
    consumer_key,
    consumer_secret
)

CURRENTDIR = os.path.dirname(os.path.realpath(__file__))
INTROTEXT = "Photo of the day."
CLOSURETEXT = "By photo of the day Twitter bot (GitHub: http://bit.ly/2YGoHrG)."

debug = True
tweetingEnabled = True
photoFolder = os.path.join(CURRENTDIR,"photos","backlog")
usedPhotoFolder = os.path.join(CURRENTDIR,"photos","usedPhoto")

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

def getExifSection(exifData):
    exifSection = []

    if exifData.get("Model"):
        exifSection.append(f"shot on {exifData.get('Model')}")

    if exifData.get("DateTimeOriginal"):
        exifSection.append(f"sometimes in {exifData.get('DateTimeOriginal')[:4]}")

    if len(exifSection) > 0:
        exifSection[0] = exifSection[0][:1].upper() + exifSection[0][1:]

    output = f"{', '.join(exifSection)}."
    return output

def getHashtags(exifData):
    hashtags = []

    hashtags.append("#photoOfTheDay")

    if exifData.get("Model"):
        hashtags.append(f"#{exifData.get('Model').replace(' ','')}")

    #TODO: country based on geo

    #TODO: AI recognized attributes

    output = f"{' '.join(hashtags)}"
    return output

def isSimilarAlreadyPosted():
    # TODO: https://realpython.com/fingerprinting-images-for-near-duplicate-detection/
    pass

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

def resize():
    pass

### Authenticate using application keys
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


### pick a photo at random
photos = [f for f in listdir(photoFolder)]
pickedPhoto = photos[randint(0,len(photos)-1)]

### get its exif information
exifData = getExif(os.path.join(photoFolder,pickedPhoto))
exifSection = getExifSection(exifData)
hashtags = getHashtags(exifData)

tweetMessage = f"{INTROTEXT} {exifSection} {CLOSURETEXT} {hashtags}"

### post it
if tweetingEnabled:
    postStatus = postMediaUpdate(
        api,
        os.path.join(photoFolder,pickedPhoto),
        tweetMessage)
else:
    postStatus = -1

### move file, if posting is succesful
if postStatus == 0:
    os.rename(
        os.path.join(photoFolder,pickedPhoto),
        os.path.join(usedPhotoFolder,pickedPhoto)
    )