from config import (
    telegram_token
)
import requests, urllib, json, time, os

CURRENTDIR = os.path.dirname(os.path.realpath(__file__))
chatIdsFile = os.path.join(CURRENTDIR,"photos","chatIds.json")

def updateAndGetRecipientList():
    # Download updated from the Telegram's bot API
    # See: https://core.telegram.org/bots/api

    updatesUrl = f"https://api.telegram.org/bot{telegram_token}/getUpdates"
    response = urllib.request.urlopen(updatesUrl)
    data = json.loads(response.read().decode())

    # get chatIds from the getUpdates endpoint, extract chatIds of private
    # conversations only ~ a private message sent from users asking bot
    # to be subscribed to the daily delivery
    chatIds = set(
        [message["message"]["chat"]["id"] for message in data["result"]
            if message["message"]["chat"]["type"] == "private"]
    )

    # Retrieve preserved chatIds from the existing json file
    if os.path.isfile(chatIdsFile):
        with open(chatIdsFile) as jsonData:
            jsonContent = json.load(jsonData)
            # Put chatIds into the existing chatIds set
            list(map(lambda x: chatIds.add(x) , jsonContent["chatIds"]))

    # Save all chatIds to the JSON file
    with open(chatIdsFile, 'w') as jsonData:
        jsonData.write(json.dumps({"chatIds":list(chatIds)}))

    return chatIds

def sendImage(filePath,telegramMessage):
    result = 0
    try:
        # Checke whether there are any new subscribers for this amazing bot 
        chatIds = updateAndGetRecipientList()
        # 
        # https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bot-39s-subscribers-at-once
        # How can I message all of my bot's subscribers at once?
        # Unfortunately, at this moment we don't have methods for sending bulk 
        # messages, e.g. notifications. We may add something along these lines in the future.

        # In order to avoid hitting our limits when sending out mass notifications, consider 
        # spreading them over longer intervals, e.g. 8-12 hours. The API will not allow more than ~30 messages 
        # to different users per second, if you go over that, you'll start getting 429 errors.
        
        # push the message to every chatId
        for chatId in chatIds:
            url = f"https://api.telegram.org/bot{telegram_token}/sendPhoto"
            files = {'photo': open(filePath, 'rb')}
            data = {
                "chat_id" : chatId,
                "caption" : telegramMessage}
            response = requests.post(url, files=files, data=data)
            if response.status_code != 200:
                raise Exception(f"{response.status_code} {response.reason}")
            # being nice to the Telegram's api
            time.sleep(.05)
    except Exception as e:
        print(e)
        result = -1

    return result