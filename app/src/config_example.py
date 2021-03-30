import os
# Twitter access config file
# To use this file, insert your own keys and rename it to config.py

consumer_key = 'CONSUMERKEY'
consumer_secret = 'CONSUMERSECRET'

access_token = 'ACCESS-TOKEN'
access_token_secret = 'ACCESSTOKENSECRET'

# Folder for storing Telegram's ChatIds
chat_id_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "photos")
telegram_token = 'TELEGRAM TOKEN'

# values 'S3', anything else defaults to using the local folder only
photo_source = 'S3'
aws_access_key = 'AWSACCESSKEY'
aws_key_id = 'AWSKEYID'
aws_bucket = 'AWSBUCKETNAME'

# debugging variables
tweeting_enabled = True
telegraming_enabled = True
debug = True

# Sentry
sentry_api_key = ""
