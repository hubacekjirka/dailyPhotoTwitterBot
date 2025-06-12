import random
from typing import Tuple

import boto3
from config import AwsProvider
from logger import logger


class S3Handler:

    def __init__(self, aws_config: AwsProvider) -> None:
        """
        Initializes the S3 handler with the provided configuration.
        :param s3_config: S3Provider configuration object containing AWS credentials and bucket info.
        :raises
            KeyError: If any required AWS configuration key is missing.
            RuntimeError: If there is an issue initializing the S3 client.
        """
        try:
            self.config = aws_config
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=aws_config.access_key_id,
                aws_secret_access_key=aws_config.secret_access_key,
                region_name=aws_config.region,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize S3 client: {e}") from e

    def get_random_file(self) -> Tuple[bytes, str]:
        """
        Fetches a random file under a given S3 prefix and returns its binary content.

        :return: Tuple containing the binary content of the file and its S3 key.
        :raises FileNotFoundError: If no files are found under the given prefix.
        :raises RuntimeError: If there is an issue with the S3 client.
        """
        response = self.s3_client.list_objects_v2(Bucket=self.config.bucket, Prefix=self.config.backlog_folder)

        if "Contents" not in response or not response["Contents"]:
            raise FileNotFoundError(f"No files found in s3://{self.config.bucket}/{self.config.backlog_folder}")

        # Filter out directories (zero-byte keys that end in '/')
        files = [
            obj["Key"]
            for obj in response["Contents"]
            if not obj["Key"].endswith("/")
            and obj["Key"]
            .lower()
            .endswith(
                (
                    ".jpg",
                    ".jpeg",
                    ".png",
                )
            )
        ]

        if not files:
            raise FileNotFoundError(
                f"No files found under prefix {self.config.backlog_folder} in bucket {self.config.bucket}"
            )

        chosen_key = random.choice(files)

        obj = self.s3_client.get_object(Bucket=self.config.bucket, Key=chosen_key)
        logger.info(f"Retrieved file {chosen_key} from s3://{self.config.bucket}/{self.config.backlog_folder}")
        return bytes(obj["Body"].read()), chosen_key
