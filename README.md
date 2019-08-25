<h1 align="center">Welcome to Photo of the day twitter bot 👋</h1>
<p>
  <a href="https://twitter.com/hubacekjirka">
    <img alt="Twitter: hubacekjirka" src="https://img.shields.io/twitter/follow/hubacekjirka.svg?style=social" target="_blank" />
  </a>
</p>

> A Twitter bot, posting a random photo from the predefined folder. Additional to the picture, it attempts to gather other image metadata from its EXIF data and image content recognition using TensorFlow. The metadata is introduced as hashtags for reaching a broader audience, because who doesn't like likes and hearts <3

### 🏠 [Homepage](http://blog.hubacek.uk)

## Install

```sh
git clone https://github.com/hubacekjirka/dailyPhotoTwitterBot.git
docker build ./dailyPhotoTwitterBot/app --tag hubacekjirka/photooftheday
```

## Usage
Map Docker host photo folder to the guest

```sh
docker run --volume /PathToThePhotoFolder/photos:/app/src/photos \
-it hubacekjirka/photooftheday
```
The bot expects the following folders in the '/PathToThePhotoFolder/photos' foder:
- 'backlog' - photos to be posted
- 'usedPhotos' - succesfully posted photo

## Author

👤 **jiri hubacek**

* Twitter: [@hubacekjirka](https://twitter.com/hubacekjirka)
* Github: [@hubacekjirka](https://github.com/hubacekjirka)

## Credits
* kefranabg: [Readme generator](https://github.com/kefranabg/readme-md-generator)
* Sagar Sharma: [Tensor Flow](https://towardsdatascience.com/tensorflow-image-recognition-python-api-e35f7d412a70)
* Miguel Garcia: [How to Make a Twitter Bot in Python With Tweepy](https://realpython.com/twitter-bot-python-tweepy/)

## Show your support

Give a ⭐️ if this project helped you!

## 📝 License

Copyright © 2019 [jiri hubacek](https://github.com/hubacekjirka).<br />
This project is [MIT](https://github.com/hubacekjirka/dailyPhotoTwitterBot/blob/master/LICENSE) licensed.

***
_This README was generated with ❤️ by [readme-md-generator](https://github.com/kefranabg/readme-md-generator)_
