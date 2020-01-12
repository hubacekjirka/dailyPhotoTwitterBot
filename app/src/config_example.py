# Twitter access config file
# To use this file, insert your own keys and rename it to config.py

consumer_key = 'CONSUMERKEY'
consumer_secret = 'CONSUMERSECRET'

access_token = 'ACCESS-TOKEN'
access_token_secret = 'ACCESSTOKENSECRET'

# Folder for storing Telegram's ChatIds
chatIdFolder = os.path.join(os.path.dirname(os.path.realpath(__file__)),"photos")
telegram_token = 'TELEGRAM TOKEN'

# values 'S3', anything else defaults to using the local folder only
photoSource = 'S3'
awsAccessKey = 'AWSACCESSKEY'
awsKeyId = 'AWSKEYID'
awsBucket = 'AWSBUCKETNAME'

# debugging variables
tweetingEnabled = True
telegramingEnabled = True
debug = True