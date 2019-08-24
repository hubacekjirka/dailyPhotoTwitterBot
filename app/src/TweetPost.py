from Post import Post
from Photo import Photo

class TweetPost(Post):

    def __init__(self, photo: Photo):
        super().__init__(photo)
        self.closureText = "TwitterBot (GitHub: http://bit.ly/2YGoHrG)"
        self.tweetPostText = f"{self.introText} " \
            f"{self.exifSection} {self.closureText} " \
            f"{photo.exifHashtags} {photo.tensorFlowHashtags}"
        print(self.tweetPostText)

    def postTweetPost(self):
        pass