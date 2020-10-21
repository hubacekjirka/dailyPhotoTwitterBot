from PIL import Image
import os
import PIL.Image
from classify_image import classifyImage
import logging

LOGGER = logging.getLogger(__name__)


class Photo:
    """
    Photo class
    """

    def __init__(self, photoPath):
        self.photoPath = photoPath
        self.fileName = os.path.basename(photoPath)
        self.resize()
        self.exifData = self.getExif()
        self.exifHashtags = self.getExifHashtags()
        self.tensorFlowHashtags = self.getContentPrediction()

    def getExif(self):
        img = PIL.Image.open(self.photoPath)
        if img._getexif() is None:
            return {}

        LOGGGER.debug(f"Available exif tags: {img._getexif().items()}")

        exif = {
            PIL.ExifTags.TAGS[k]: v
            for k, v in img._getexif().items()
            if k in PIL.ExifTags.TAGS
        }
        return exif

    def getExifHashtags(self):
        hashtags = []
        hashtags.append("")

        if self.exifData.get("Model"):
            hashtags.append(f"#{self.exifData.get('Model').replace(' ','')}")

        exifHashtags = f"{' '.join(hashtags)}"
        return exifHashtags

    def resize(self):
        # keep resizing until the file is smaller than 3MB and 8192px
        #     => Twitter's API limit
        while (
            os.path.getsize(self.photoPath) >= 3 * 1024 * 1024
            or Image.open(self.photoPath).size[0] > 8192
            or Image.open(self.photoPath).size[1] > 8192
        ):

            img = Image.open(self.photoPath)
            resizedImg = img.resize(
                (round(img.size[0] * 0.75), round(img.size[1] * 0.75)),
                resample=PIL.Image.LANCZOS,
            )
            resizedImg.save(self.photoPath)

    def getContentPrediction(self):
        def composeTensorflowHashtags(imageClassification):
            output = []
            output.append("#tensorflow")
            output.append("Content prediction:")
            for node in imageClassification:
                output.append(f"{format(node[0] * 100, '.0f')}%")
                for predictedItems in node[1]:
                    for predictedItem in predictedItems.split(","):
                        # get rid of spaces
                        hashtag = f"#{predictedItem.replace(' ','')}"
                        output.append(hashtag)

            output = f"{' '.join(output)}"
            return output

        # call Tensorflow to identify objects in the picture
        tensorFlowHashtags = ""
        try:
            imageClassification = classifyImage(
                self.photoPath,
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "imagenet"),
                5,
            )
            tensorFlowHashtags = composeTensorflowHashtags(imageClassification)
        except Exception as e:
            print("An error occured during tensorflow processing")
            print(e)

        return tensorFlowHashtags
