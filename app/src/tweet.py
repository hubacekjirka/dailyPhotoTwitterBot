from PIL import JpegImagePlugin, Image
from PIL.ExifTags import TAGS
from os import listdir
from random import randint
import sys
import hashlib
import tweepy
import os
import PIL.Image
from classify_image import classifyImage

from config import (
    access_token,
    access_token_secret,
    consumer_key,
    consumer_secret
)

CURRENTDIR = os.path.dirname(os.path.realpath(__file__))
INTROTEXT = "#photoOfTheDay"
CLOSURETEXT = "TwitterBot (GitHub: http://bit.ly/2YGoHrG)"

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
    if img._getexif() is None:
        return {}

    exif = {
        PIL.ExifTags.TAGS[k]: v
        for k, v in img._getexif().items()
        if k in PIL.ExifTags.TAGS
    }
    return exif

def getExifSection(exifData):
    # in case no exif data is available, return empty string
    if len(exifData) == 0:
        return ""

    exifSection = []

    if exifData.get("Model"):
        exifSection.append(f"shot on {exifData.get('Model')}")

    if exifData.get("DateTimeOriginal"):
        exifSection.append(f"in {exifData.get('DateTimeOriginal')[:4]}")

    output = f"{', '.join(exifSection)}."
    return output

def getHashtags(exifData):
    hashtags = []

    hashtags.append("")

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

def resize(filePath):
    img  = Image.open(filePath)
    resizedImg = img.resize(
        (round(img.size[0]*.75), round(img.size[1]*.75)),
        resample = PIL.Image.LANCZOS
    )
    resizedImg.save(filePath)

def composeTensorflowHashtags(imageClassification):
    output = []
    output.append("#tensorflow")
    output.append("Content prediction:")
    for node in imageClassification:
        output.append(f"{format(node[0] * 100, '.0f')}%")
        for predictedItems in node[1]:
            for predictedItem in predictedItems.split(','):
            # get rid of spaces
                hashtag = f"#{predictedItem.replace(' ','')}"
                output.append(hashtag)

    output = f"{' '.join(output)}"
    return output


if __name__ == "__main__":
    ### Authenticate using application keys
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)


    ### pick a photo at random
    
    photos = [f for f in listdir(photoFolder) if f.endswith("jpg")]
    pickedPhoto = photos[randint(0,len(photos)-1)]

    ### get its exif information
    exifData = getExif(os.path.join(photoFolder,pickedPhoto))
    exifSection = getExifSection(exifData)
    hashtags = getHashtags(exifData)

    ### call Tensorflow to identify objects in the picture
    tensorFlowHashtags = ""
    try:
        imageClassification = classifyImage(
            os.path.join(photoFolder,pickedPhoto),
            os.path.join(CURRENTDIR,"imagenet"),
            5)
        tensorFlowHashtags = composeTensorflowHashtags(imageClassification)
        
    except Exception as e:
        print("An error occured during tensorflow processing")
        print(e)

    ### keep resizing until the file is smaller than 3.5MB and 8192px
    ###     => Twitter's API limit
    while (os.path.getsize(os.path.join(photoFolder,pickedPhoto)) > 3.5 * 1024 * 1024
        or Image.open(os.path.join(photoFolder,pickedPhoto)).size[0] > 8192
        or Image.open(os.path.join(photoFolder,pickedPhoto)).size[1] > 8192):
        resize(os.path.join(photoFolder,pickedPhoto))

    tweetMessage = f"{INTROTEXT} {exifSection} {CLOSURETEXT} {hashtags} {tensorFlowHashtags}"
    if len(tweetMessage) > 275:
        tweetMessage = f"{tweetMessage[:275]}..."

    if debug:
        print(f"Filename: {pickedPhoto}")
        print(tweetMessage)

    ### post it
    if tweetingEnabled:
        postStatus = postMediaUpdate(
            api,
            os.path.join(photoFolder,pickedPhoto),
            tweetMessage
        )
    else:
        postStatus = -1

    ### move file, if posting is succesful
    if postStatus == 0:
        os.rename(
            os.path.join(photoFolder,pickedPhoto),
            os.path.join(usedPhotoFolder,pickedPhoto)
        )