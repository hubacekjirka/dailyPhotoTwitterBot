from config import aws_access_key, aws_key_id, aws_bucket, photo_source
from PhotoWithBenefits import PhotoWithBenefits
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
        self._file_folder = os.path.join(currentDir, "photos", "backlog")
        self._used_file_folder = os.path.join(currentDir, "photos", "usedPhoto")
        self._photo = None
        self._s3_client_handle = None

    def get_photo(self):
        """
        Retrieve a photo from S3 if it's enabled in the config to the local folder
        Pick a random photo from the local forlder (if S3 is enabled there's
        exacly one photo)
        """
        if photo_source == "S3":
            self._retrieve_random_file_from_s3()

        # Pick a random photo from the local folder
        files = [
            f
            for f in os.listdir(self._file_folder)
            if f.endswith("jpg") or f.endswith("jpeg")
        ]
        photo = files[random.randint(0, len(files) - 1)]

        # TODO: raise exception when there're no photos in the folder
        self._photo = PhotoWithBenefits(os.path.join(self._file_folder, photo))
        return self._photo

    def _create_s3_client_handle(self):
        return boto3.client(
            "s3", aws_access_key_id=aws_access_key, aws_secret_access_key=aws_key_id
        )

    # TODO: Fix this, always creates new handle
    def _get_s3_client_handle(self):
        if self._s3_client_handle is None:
            return self._create_s3_client_handle()
        else:
            return self._s3_client_handle

    def _retrieve_random_file_from_s3(self):
        s3 = self._get_s3_client_handle()

        s3_objects = s3.list_objects_v2(Bucket=aws_bucket, Prefix="backlog")
        # Size: 0 ~ folder object
        s3_files = list(filter(lambda x: x["Size"] != 0, s3_objects["Contents"]))

        random_file = random.choice(s3_files)
        random_file_name = random_file["Key"].split("/")[-1]
        random_file_key = random_file["Key"]

        file_path = os.path.join(self._file_folder, random_file_name)
        s3.download_file(aws_bucket, random_file_key, file_path)
        LOGGER.debug(f"Picked a random file from S3: {file_path}")

    def copy_file_to_archive(self):
        """
        Move photo file to the archive folder
        """
        os.rename(
            os.path.join(self._photo._file_path),
            os.path.join(self._used_file_folder, self._photo._file_name),
        )
        LOGGER.debug(
            f"Copying photo from {self._photo._file_path} "
            f"to {self._used_file_folder}"
        )

    def copy_file_to_archive_in_s3(self):
        if photo_source == "S3":
            s3 = self._get_s3_client_handle()
            copy_source = {
                "Bucket": aws_bucket,
                "Key": "backlog" + "/" + self._photo._file_name,
            }
            s3.copy(
                copy_source, aws_bucket, "usedPhoto" + "/" + self._photo._file_name
            )

            LOGGER.debug(
                f"Copying photo from {copy_source} "
                f"usedPhoto/{self.pickedPhoto.fileName}"
            )

    def remove_file_from_backlog_in_s3(self):
        if photo_source == "S3":
            s3 = self._get_s3_client_handle()
            s3.delete_object(
                Bucket=aws_bucket,
                Key="backlog" + "/" + self._photo._file_name,
            )
            LOGGER.debug(f"File removed from backlog/{self.pickedPhoto.fileName}")
