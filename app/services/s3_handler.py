import random

import boto3


class S3_handler:

    def __init__(self, config: dict[str, str]):
        try:
            self.bucket = config["bucket"]
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=config["aws_access_key_id"],
                aws_secret_access_key=config["aws_secret_access_key"],
                region_name=config["region"],
            )
        except KeyError as e:
            raise KeyError(f"Missing AWS configuration key: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to initialize S3 client: {e}") from e

    def get_random_file_as_binary(self, prefix: str) -> bytes:
        """
        Fetches a random file under a given S3 prefix and returns its binary content.

        :param bucket_name: Name of the S3 bucket.
        :param prefix: S3 key prefix (like a folder path).
        :return: Binary content of the selected file.
        """
        response = self.s3_client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)

        if "Contents" not in response or not response["Contents"]:
            raise FileNotFoundError(f"No files found in s3://{self.bucket}/{prefix}")

        # Filter out directories (zero-byte keys that end in '/')
        files = [obj["Key"] for obj in response["Contents"] if not obj["Key"].endswith("/")]

        # TODO: filter out any non-image files

        if not files:
            raise FileNotFoundError(f"No files found under prefix {prefix} in bucket {self.bucket}")

        chosen_key = random.choice(files)

        obj = self.s3_client.get_object(Bucket=self.bucket, Key=chosen_key)
        # TODO: return s3 key as well
        return bytes(obj["Body"].read())
