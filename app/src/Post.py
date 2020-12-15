from Photo import Photo
from constants import friendly_camera_mapping


class Post:
    """
    Base class for Tweetpost and Telegrampost
    """

    def __init__(self, photo: Photo):
        self.photo = photo
        self.introText = "#photoOfTheDay"
        self.exifSection = self.getExifSection()

    def getExifSection(self):
        if len(self.photo.exifData) == 0:
            return ""

        exif_section_elements = []
        if self.photo.exifData.get("Model"):
            friendly_camera_name = self.get_friendly_camera_model_name(
                self.photo.exifData.get("Model")
            )
            exif_section_elements.append(f"shot on {friendly_camera_name}")

        if self.photo.exifData.get("DateTimeOriginal"):
            exif_section_elements.append(
                f"in {self.photo.exifData.get('DateTimeOriginal')[:4]}"
            )

        exifSection = f"{', '.join(exif_section_elements)}."
        return exifSection

    def get_friendly_camera_model_name(self, model):
        """
        Retrieve a nicer camera model name instead of a cryptic one
        """
        return friendly_camera_mapping.get(model, model)
