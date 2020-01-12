from Photo import Photo
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

        exifSectionElements = []
        if self.photo.exifData.get("Model"):
            exifSectionElements.append(f"shot on {self.photo.exifData.get('Model')}")

        if self.photo.exifData.get("DateTimeOriginal"):
            exifSectionElements.append(f"in {self.photo.exifData.get('DateTimeOriginal')[:4]}")

        exifSection = f"{', '.join(exifSectionElements)}."
        return exifSection