import os
import random

from Photo import Photo
from TweetPost import TweetPost

if __name__ == "__main__":
    CURRENTDIR = os.path.dirname(os.path.realpath(__file__))
    debug = True
    tweetingEnabled = True
    telegramingEnabled = False
    photoFolder = os.path.join(CURRENTDIR,"photos","backlog")
    usedPhotoFolder = os.path.join(CURRENTDIR,"photos","usedPhoto")
    
    ### pick a photo at random and create a photo object
    photos = [f for f in os.listdir(photoFolder) if f.endswith("jpg")]
    pickedPhoto = Photo(os.path.join(
        photoFolder,
        photos[random.randint(0,len(photos)-1)])
    )
    
    if debug:
        print(f"Filename: {pickedPhoto}")   

    ### Tweeting
    tweet = TweetPost(pickedPhoto)
    if debug:
        print(tweet.tweetPostText)
    tweetPostStatus = -1
    if tweetingEnabled:
        tweetPostResult, tweetPostStatus = tweet.postTweetPost()
    if debug:
        print(tweetPostResult)
        print(tweetPostStatus)

    ### Telegraming

    ### post it on telegram - only bother if everythong goes as expected
    # if telegramingEnabled and postStatus == 0:
    #     telegramMessage = f"{postMessage} | Sent with ❤️"
    #     postStatus = telegram.sendImage(
    #         os.path.join(photoFolder,pickedPhoto),
    #         telegramMessage)

    ### move file, if posting is succesful and enabled on all platforms
    if postStatus == 0 and tweetingEnabled and telegramingEnabled:
        os.rename(
            os.path.join(photoFolder,pickedPhoto),
            os.path.join(usedPhotoFolder,pickedPhoto)
        )