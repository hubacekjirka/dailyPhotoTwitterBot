import os
import random
from config import (
    debug,
    tweetingEnabled,
    telegramingEnabled,
    chatIdFolder
)

from Photo import Photo
from TweetPost import TweetPost
from TelegramPost import TelegramPost
from PhotoPicker import PhotoPicker

if __name__ == "__main__":
    CURRENTDIR = os.path.dirname(os.path.realpath(__file__))
    photoPicker = PhotoPicker(CURRENTDIR)

    pickedPhoto = photoPicker.getPhotoPath()
    
    #TODO: exit when there're no photos in the folder
    pickedPhoto = Photo(os.path.join(
        photoPicker.photoFolder,
        pickedPhoto)
    )

    if debug:
        print(f"Filename: {pickedPhoto.photoPath}")   

    ### Tweeting
    tweetPostResult = 0
    tweet = TweetPost(pickedPhoto)
    if debug:
        print(tweet.tweetPostText)
    if tweetingEnabled:
        tweetPostResult, tweetPostStatus = tweet.postTweetPost()        
        if debug:
            print(tweetPostResult)
            print(str(tweetPostStatus).encode("utf-8"))

    ### Telegraming
    telegramPostResult = 0
    chatIdFilePath = os.path.join(chatIdFolder, "chatIds.json")
    telegramMessage = TelegramPost(pickedPhoto, chatIdFilePath)
    if tweet is not None:
        if tweet.place is not None:
            telegramMessage.setLocation(tweet.place.full_name)
    ### post it on telegram
    if telegramingEnabled:
         telegramPostResult = telegramMessage.postTelegramPost()

    ### move file, if posting is succesful and enabled on all platforms
    if (tweetPostResult == 0 and 
        telegramPostResult == 0 and
        tweetingEnabled and 
        telegramingEnabled):
        if debug:
            print(f"Moving {pickedPhoto.fileName} to the used photo folder.")
        os.rename(
            os.path.join(pickedPhoto.photoPath),
            os.path.join(photoPicker.usedPhotoFolder,pickedPhoto.fileName)
        )
    
    print(f"So, O-Ren...any more subordinates for me to kill?")