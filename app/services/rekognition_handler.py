import boto3
from config import AwsProvider
from logger import logger


class RekognitionHandler:

    def __init__(self, aws_config: AwsProvider) -> None:
        """
        Initializes the Rekognition handler with the provided configuration.
        :param aws_config: AwsProvider configuration object containing AWS credentials and region info.
        :raises
            KeyError: If any required AWS configuration key is missing.
            RuntimeError: If there is an issue initializing the Rekognition client.
        """
        try:
            self.client = boto3.client(
                "rekognition",
                aws_access_key_id=aws_config.access_key_id,
                aws_secret_access_key=aws_config.secret_access_key,
                region_name=aws_config.region,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Rekognition client: {e}") from e

    def get_picture_content(self, picture: bytes) -> list[dict[str, float]] | None:
        """
        Analyzes the picture using AWS Rekognition and returns an ordered list of label dictionaries.

        :param picture: The binary content of the picture to analyze.
        :return: List of dictionaries containing label names and their confidence scores.
        :raises RuntimeError: If there is an issue with the Rekognition client or the analysis fails.
        """
        try:
            response = self.client.detect_labels(Image={"Bytes": picture}, MaxLabels=10, MinConfidence=50)
            labels = [{"Name": label["Name"], "Confidence": label["Confidence"]} for label in response["Labels"]]

            logger.info(f"Rekognition labels: {labels}")
            return labels
        except Exception as e:
            logger.error(f"Failed to analyze picture with Rekognition: {e}")
            return None
