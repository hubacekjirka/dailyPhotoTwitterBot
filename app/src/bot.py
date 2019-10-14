import os
import random
from config import debug

from Photo import Photo
from TweetPost import TweetPost
from TelegramPost import TelegramPost

if __name__ == "__main__":
    CURRENTDIR = os.path.dirname(os.path.realpath(__file__))
    tweetingEnabled = True
    telegramingEnabled = True

    # file paths
    photoFolder = os.path.join(CURRENTDIR,"photos","backlog")
    usedPhotoFolder = os.path.join(CURRENTDIR,"photos","usedPhoto")
    chatIdFolder = os.path.join(CURRENTDIR,"photos")
    
    ### pick a photo at random and create a photo object
    photos = [f for f in os.listdir(photoFolder) if f.endswith("jpg") or f.endswith("jpeg")]
    #TODO: exit when there're no photos in the folder
    pickedPhoto = Photo(os.path.join(
        photoFolder,
        photos[random.randint(0,len(photos)-1)])
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
            os.path.join(usedPhotoFolder,pickedPhoto.fileName)
        )
    
    print(f"So, O-Ren...any more subordinates for me to kill?")