from config import (
    aws_access_key,
    aws_key_id,
    aws_bucket,
    photo_source,
    throwback_thursday,
)
from PhotoWithBenefits import PhotoWithBenefits
from datetime import datetime
from botocore.exceptions import ClientError
import os
import boto3
import random
import logging
import time

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
        self.throwback_thursday = throwback_thursday and datetime.now().weekday() == 3
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
        self._photo = PhotoWithBenefits(
            photo_path=os.path.join(self._file_folder, photo),
            throwback_thursday=self.throwback_thursday,
        )
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

        s3_objects = (
            s3.list_objects_v2(Bucket=aws_bucket, Prefix="usedPhoto")
            if self.throwback_thursday
            else s3.list_objects_v2(Bucket=aws_bucket, Prefix="backlog")
        )
        # Size: 0 ~ folder object
        s3_files = list(filter(lambda x: x["Size"] != 0, s3_objects["Contents"]))

        random_file = random.choice(s3_files)
        random_file_name = random_file["Key"].split("/")[-1]
        random_file_key = random_file["Key"]

        file_path = os.path.join(self._file_folder, random_file_name)
        s3.download_file(aws_bucket, random_file_key, file_path)
        LOGGER.info(f"Picked a random file from S3: {file_path}")

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
            copy_target = f"usedPhoto/{self._photo._file_name}"

            LOGGER.debug(f"Copying photo from {copy_source} to {copy_target}")

            for _ in range(3):
                try:
                    s3.copy(
                        copy_source,
                        aws_bucket,
                        copy_target,
                    )
                    break
                except ClientError as e:
                    LOGGER.warning(
                        f"S3 copy operation from {copy_source} to {copy_target} failed. Retrying ...",
                        exc_info=e,
                    )
                    time.sleep(3)
            else:
                raise Exception("Failed to perform S3 copy operation. Giving up ...")

    def remove_file_from_backlog_in_s3(self):
        if photo_source == "S3":
            s3 = self._get_s3_client_handle()
            LOGGER.debug(f"Deleting file from backlog/{self._photo._file_name}")

            for _ in range(3):
                try:
                    s3.delete_object(
                        Bucket=aws_bucket,
                        Key="backlog" + "/" + self._photo._file_name,
                    )
                    break
                except ClientError:
                    LOGGER.warning(f"S3 delete operation failed. Retrying ...")
            else:
                raise Exception("Failed to perform S3 delete opration. Giving up ...")
