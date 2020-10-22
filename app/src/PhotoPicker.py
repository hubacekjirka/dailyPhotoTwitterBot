from config import awsAccessKey, awsKeyId, awsBucket, photoSource
from Photo import Photo
import os
import boto3
import random
import logging

LOGGER = logging.getLogger(__name__)


class PhotoPicker:
    def __init__(self, currentDir):
        """
        Constructs a PhotoPicker object.
        Sets filesystem paths to the instance variables.

        Parameters
        ----------
        currentDir : str
            Path to the root folder of the application containing
            necessary photo folders.
        """
        self.photoFolder = os.path.join(currentDir, "photos", "backlog")
        self.usedPhotoFolder = os.path.join(currentDir, "photos", "usedPhoto")
        self.pickedPhoto = None
        self.s3ClientHandle = None

    def getPhoto(self):
        if photoSource == "S3":
            self.getPhotoFromS3()

        # pick a photo at random and create a photo object
        photos = [
            f
            for f in os.listdir(self.photoFolder)
            if f.endswith("jpg") or f.endswith("jpeg")
        ]
        photo = photos[random.randint(0, len(photos) - 1)]

        # TODO: raise exception when there're no photos in the folder

        self.pickedPhoto = Photo(os.path.join(self.photoFolder, photo))

        return self.pickedPhoto

    def createS3ClientHandle(self):
        return boto3.client(
            "s3", aws_access_key_id=awsAccessKey, aws_secret_access_key=awsKeyId
        )

    # TODO: Fix this, always creates new handle
    def getS3ClientHandle(self):
        if self.s3ClientHandle is None:
            return self.createS3ClientHandle()
        else:
            return self.s3ClientHandle

    def getPhotoFromS3(self):
        s3 = self.getS3ClientHandle()

        allObjects = s3.list_objects_v2(Bucket=awsBucket, Prefix="backlog")
        # Size: 0 ~ folder object
        filesOnly = list(filter(lambda x: x["Size"] != 0, allObjects["Contents"]))

        pickedFile = random.choice(filesOnly)
        pickedFileName = pickedFile["Key"].split("/")[-1]
        pickedFileKey = pickedFile["Key"]

        filePath = os.path.join(self.photoFolder, pickedFileName)
        LOGGER.debug(f"Picked {filePath}")
        s3.download_file(awsBucket, pickedFileKey, filePath)

    def copyPhotoToArchive(self):
        """
        Move photo file to the archive folder
        """
        os.rename(
            os.path.join(self.pickedPhoto.photoPath),
            os.path.join(self.usedPhotoFolder, self.pickedPhoto.fileName),
        )
        LOGGER.debug(f"Copying photo from {self.pickedPhoto.photoPath} "
            f"to {self.usedPhotoFolder}")

    def copyPhotoToArchiveS3(self):
        if photoSource == "S3":
            s3 = self.getS3ClientHandle()
            copy_source = {
                "Bucket": awsBucket,
                "Key": "backlog" + "/" + self.pickedPhoto.fileName,
            }
            s3.copy(
                copy_source, awsBucket, "usedPhoto" + "/" + self.pickedPhoto.fileName
            )

            LOGGER.debug(f"Copying photo from {copy_source} "
                f"usedPhoto/{self.pickedPhoto.fileName")

    def removePhotoFromBacklogS3(self):
        if photoSource == "S3":
            s3 = self.getS3ClientHandle()
            s3.delete_object(
                Bucket=awsBucket,
                Key="backlog" + "/" + self.pickedPhoto.fileName,
            )
        LOGGER.debug(f"File removed from backlog/{self.pickedPhoto.fileName}")
