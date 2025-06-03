import random
from typing import Tuple

import boto3

from app.config import S3Provider


class S3_handler:

    def __init__(self, s3_config: S3Provider) -> None:
        """
        Initializes the S3 handler with the provided configuration.
        :param s3_config: S3Provider configuration object containing AWS credentials and bucket info.
        :raises
            KeyError: If any required AWS configuration key is missing.
            RuntimeError: If there is an issue initializing the S3 client.
        """
        try:
            self.bucket = s3_config.bucket
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=s3_config.access_key_id,
                aws_secret_access_key=s3_config.secret_access_key,
                region_name=s3_config.region,
            )
        except KeyError as e:
            raise KeyError(f"Missing AWS configuration key: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to initialize S3 client: {e}") from e

    def get_random_file_as_binary(self, prefix: str) -> Tuple[bytes, str]:
        """
        Fetches a random file under a given S3 prefix and returns its binary content.

        :param bucket_name: Name of the S3 bucket.
        :param prefix: S3 key prefix (like a folder path).
        :return: Tuple containing the binary content of the file and its S3 key.
        :raises FileNotFoundError: If no files are found under the given prefix.
        :raises RuntimeError: If there is an issue with the S3 client.
        """
        response = self.s3_client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)

        if "Contents" not in response or not response["Contents"]:
            raise FileNotFoundError(f"No files found in s3://{self.bucket}/{prefix}")

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
            raise FileNotFoundError(f"No files found under prefix {prefix} in bucket {self.bucket}")

        chosen_key = random.choice(files)

        obj = self.s3_client.get_object(Bucket=self.bucket, Key=chosen_key)
        return bytes(obj["Body"].read()), chosen_key
