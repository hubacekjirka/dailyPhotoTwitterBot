from typing import List, Sequence

import boto3
from config import AwsProvider
from core.custom_types import Label
from logger import logger


class RekognitionHandler:

    def __init__(self, aws_config: AwsProvider) -> None:
        """
        Initializes the Rekognition handler with the provided configuration.
        :param aws_config: AwsProvider configuration object containing AWS credentials and region info.
        :raises KeyError: If any required AWS configuration key is missing.
        :raises RuntimeError: If there is an issue initializing the Rekognition client.
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

    def get_picture_content(
        self, picture: bytes, max_labels: int = 10, min_confidence: float = 50.0
    ) -> Sequence["Label"]:
        """
        Analyzes the picture using AWS Rekognition and returns an ordered list of label dictionaries.

        :param picture: The binary content of the picture to analyze.
        :param max_labels: Maximum number of labels to return (default: 10).
        :param min_confidence: Minimum confidence level for labels (default: 50.0).
        :returns: Sequence of Label NamedTuples containing label names and confidence scores.
        :rtype: Sequence[Label]
        """
        logger.info("Getting picture content using Rekognition")

        response = self.client.detect_labels(
            Image={"Bytes": picture}, MaxLabels=max_labels, MinConfidence=min_confidence
        )
        labels: List[Label] = [
            Label(name=str(label["Name"]), confidence=int(label["Confidence"])) for label in response["Labels"]
        ]

        logger.info(f"Rekognition labels: {labels}")
        return labels
