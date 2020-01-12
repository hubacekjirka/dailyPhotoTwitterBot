import os
import random
import sys
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

#TODO
# IMG_8953.jpeg produces:
# #photoOfTheDay !!!None!!! TwitterBot (GitHub: http://bit.ly/2YGoHrG)  #tensorflow Content prediction: 98% #koala #koalabear #kangaroobear #nativebear #Phascolarctoscinereus 0% #indri #indris #Indriindri #Indribrevicaudatus 0% #wombat 0% #Madagascarcat #ring-tailedlemur #Lemurcatta 0% #three-toedsloth #ai #Bradypustridactylus

if __name__ == "__main__":
    ### Picks a photo from the backlog's photo folder and stores in as a Photo object.
    ### Optionally: gets photo from S3
    try:
        CURRENTDIR = os.path.dirname(os.path.realpath(__file__))
        # initialize a PhotoPicker object, sets paths
        photoPicker = PhotoPicker(CURRENTDIR)

        # Retrieves a photo file and creates a photo object
        pickedPhoto = photoPicker.getPhoto()

    except Exception as e:
        print(e)
        print("Couldn't retrieve the photo file.")
        sys.exit()
    
    if debug:
        print(f"Filename: {pickedPhoto.fileName}")   

    ### Tweeting
    try:
        tweetPostResult = 0
        tweet = TweetPost(pickedPhoto)
        if debug:
            print(tweet.tweetPostText)
        if tweetingEnabled:
            tweetPostResult, tweetPostStatus = tweet.postTweetPost()        
            if debug:
                print(tweetPostResult)
                print(str(tweetPostStatus).encode("utf-8"))
    except Exception as e:
        print(e)
        sys.exit()

    ### Telegraming
    try:
        telegramPostResult = 0
        chatIdFilePath = os.path.join(chatIdFolder, "chatIds.json")
        telegramMessage = TelegramPost(pickedPhoto, chatIdFilePath)
        if tweet is not None:
            if tweet.place is not None:
                telegramMessage.setLocation(tweet.place.full_name)
        ### post it on telegram
        if telegramingEnabled:
            telegramPostResult = telegramMessage.postTelegramPost()
    except Exception as e:
        print(e)
        sys.exit()

    ### move file, if posting is succesful and enabled on all platforms
    #TODO: refactor this in the "future" to instance variables
    try:
        if (tweetPostResult == 0 and 
            telegramPostResult == 0 and
            tweetingEnabled and 
            telegramingEnabled):
            if debug:
                print(f"Moving {pickedPhoto.fileName} to the used photo folder.")
            
            # if everything goes well, move the photo file to the the 
            # archive folders
            photoPicker.copyPhotoToArchive()

            photoPicker.copyPhotoToArchiveS3()
            photoPicker.removePhotoFromBacklogS3()
    except Exception as e:
        print(e)
        sys.exit()
    
    print(f"So, O-Ren...any more subordinates for me to kill?")