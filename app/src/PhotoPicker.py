from config import (
    awsAccessKey,
    awsKeyId,
    awsBucket,
    photoSource
)
from Photo import Photo
import requests
import os
import boto3
import random

class PhotoPicker:
    def __init__(self, currentDir):
        # file paths
        self.photoFolder = os.path.join(currentDir,"photos","backlog")
        self.usedPhotoFolder = os.path.join(currentDir,"photos","usedPhoto")
        self.pickedPhotoPath = None
        self.pickedPhoto = None

    def getPhoto(self):
        if photoSource == "S3":
            self.getPhotoFromS3()

        ### pick a photo at random and create a photo object
        photos = [f for f in os.listdir(self.photoFolder) if f.endswith("jpg") or f.endswith("jpeg")]
        photo = photos[random.randint(0,len(photos)-1)]
        
        #TODO: raise exception when there're no photos in the folder

        self.pickedPhoto = Photo(os.path.join(
            self.photoFolder,
            photo)
        )
        
        return self.pickedPhoto

    def getPhotoFromS3(self):
        s3 = boto3.client('s3', 
            aws_access_key_id=awsAccessKey, 
            aws_secret_access_key=awsKeyId
        )

        allObjects = s3.list_objects_v2(Bucket = awsBucket, Prefix = 'backlog')        
        # Size: 0 ~ folder object 
        filesOnly = list(filter(
            lambda x: x["Size"] != 0, 
            allObjects["Contents"])
        )

        pickedFile = random.choice(filesOnly)
        pickedFileName = pickedFile["Key"].split("/")[-1]
        pickedFileKey = pickedFile["Key"]

        filePath = os.path.join(self.photoFolder,pickedFileName)
        s3.download_file(awsBucket,pickedFileKey , filePath)
        print('done')

        #TODO: Copy the photo
        #TODO: Delete the photo