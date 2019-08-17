from config import (
    telegram_token,
    chat_id
)
import requests

def sendImage(filePath,telegramMessage):
    result = 0
    try:
        url = f"https://api.telegram.org/bot{telegram_token}/sendPhoto"
        files = {'photo': open(filePath, 'rb')}
        data = {
            "chat_id" : chat_id,
            "caption" : telegramMessage}
        response = requests.post(url, files=files, data=data)
        if response.status_code != 200:
            raise Exception(f"{response.status_code} {response.reason}")
    except Exception as e:
        print(e)
        result = -1

    return result