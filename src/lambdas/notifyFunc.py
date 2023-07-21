import datetime
import json
import logging

import urllib3
from botocore.exceptions import ClientError

from config import DefaultConfig

http = urllib3.PoolManager()
TOKEN = DefaultConfig.BOT_TOKEN
USER_ID = DefaultConfig.BOT_ID
TELEGRAM_URL = "https://api.telegram.org/bot{}/sendMessage".format(TOKEN)

''' Function that sends a Notification to the Telegram BOT API whenever something is posted on the topic. '''

def lambda_handler(event, context):
    for record in event['Records']:
        subject = record["Sns"]['Subject']
        message = record["Sns"]['Message']

        headers = {
            'Content-Type': 'application/json'
        }
        text = ""
        if subject == 'Sensor Error':
            text = format_text_sensor_error(message)
        elif subject == 'Routine Check Errors':
            text = format_text_storage_error(message)
        elif subject == 'Door left open!':
            text = format_text_door_error(message)

        payload = {
            "text": text,
            "chat_id": USER_ID
        }

        response = http.request('POST', url=TELEGRAM_URL, body=json.dumps(payload), headers=headers)
        return response.data.decode('utf-8')
    
def format_text_sensor_error(message_string):
    #{"device_id": "%s", "device_name": "%s", "room": "%s", "timestamp": "%s"}
    message = json.loads(json.loads(message_string))
    return f"There's a been a problem with a {message['device_type']} in room {message['room']} at {message['timestamp']} UTC.\nDevice ID: {message['device_id']}"

def format_text_storage_error(message_string):
    #payload = {'room_name': room_name, 'humidity_check': h_check, 'temperature_check': t_check, 
    # 'vibration_check': v_check, 'timestamp': datetime.datetime.now().timestamp()}
    message= json.loads(message_string)
    return_message= f"There's currently a problem with storage conditions in room {message['room_name']}.\n"
    if message['humidity_check'] == False:
        return_message += "The relative humidity inside the room is not within accepted ranges.\n"
    if message['temperature_check'] == False:
        return_message += "The air temperature inside the room is not within accepted ranges.\n"
    if message['vibration_check'] == False:
       return_message += "The currently registered vibration inside the room is above accepted ranges.\n"
    return_message += f" Lastly checked at {datetime.datetime.utcfromtimestamp(float(message['timestamp'])).strftime('%Y-%m-%d %H:%M:%S')} UTC"
    return return_message

def format_text_door_error(message_string):
    message = json.loads(message_string)
    return_message = f"The door in the {message['room']} room has remained open for more than 10 minutes."
    return return_message
