import os
import random

from Photo import Photo
from TweetPost import TweetPost
from TelegramPost import TelegramPost

if __name__ == "__main__":
    CURRENTDIR = os.path.dirname(os.path.realpath(__file__))
    debug = True
    tweetingEnabled = True
    telegramingEnabled = True

    # file paths
    photoFolder = os.path.join(CURRENTDIR,"photos","backlog")
    usedPhotoFolder = os.path.join(CURRENTDIR,"photos","usedPhoto")
    chatIdFolder = os.path.join(CURRENTDIR,"photos")
    
    ### pick a photo at random and create a photo object
    photos = [f for f in os.listdir(photoFolder) if f.endswith("jpg")]
    pickedPhoto = Photo(os.path.join(
        photoFolder,
        photos[random.randint(0,len(photos)-1)])
    )
    
    if debug:
        print(f"Filename: {pickedPhoto.photoPath}")   

    ### Tweeting
    tweetPostStatus = 0
    tweet = TweetPost(pickedPhoto)
    if debug:
        print(tweet.tweetPostText)
    if tweetingEnabled:
        tweetPostResult, tweetPostStatus = tweet.postTweetPost()
        if debug:
            print(tweetPostResult)
            print(tweetPostStatus)

    ### Telegraming
    telegramPostStatus = 0
    chatIdFilePath = os.path.join(chatIdFolder, "chatIds.json")
    telegramMessage = TelegramPost(pickedPhoto, chatIdFilePath)
    ### post it on telegram
    if telegramingEnabled:
         telegramPostStatus = telegramMessage.postTelegramPost()

    ### move file, if posting is succesful and enabled on all platforms
    if (tweetPostStatus == 0 and 
        telegramPostStatus == 0 and
        tweetingEnabled and 
        telegramingEnabled):
        if debug:
            print(f"Moving {pickedPhoto.fileName} to the used photo folder.")
        os.rename(
            os.path.join(pickedPhoto.photoPath),
            os.path.join(usedPhotoFolder,pickedPhoto.fileName)
        )