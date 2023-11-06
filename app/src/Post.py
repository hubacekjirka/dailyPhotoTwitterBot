from PhotoWithBenefits import PhotoWithBenefits
from constants import friendly_camera_mapping


class Post:
    """
    Base class for Tweetpost and Telegrampost
    """

    def __init__(self, photo: PhotoWithBenefits):
        self._photo = photo
        self._intro_text = "#photoOfTheDay"
        if photo._throwback_everyday:
            self._intro_text = f"{self._intro_text} #ThrowbackEveryday"
        elif photo._throwback_thursday:
            self._intro_text = f"{self._intro_text} #ThrowbackThursday"

        self._exif_section = self._get_exif_section()

    def _get_exif_section(self):
        if len(self._photo._exif) == 0:
            return ""

        exif_section_elements = []
        if self._photo._exif.get("Model"):
            friendly_camera_name = self._get_friendly_camera_model_name(
                self._photo._exif.get("Model")
            )
            exif_section_elements.append(f"shot on {friendly_camera_name}")

        if self._photo._exif.get("DateTimeOriginal"):
            exif_section_elements.append(
                f"in {self._photo._exif.get('DateTimeOriginal')[:4]}"
            )

        exifSection = f"{', '.join(exif_section_elements)}."
        return exifSection

    def _get_friendly_camera_model_name(self, model):
        """
        Retrieve a nicer camera model name instead of a cryptic one
        """
        return friendly_camera_mapping.get(model, model)
