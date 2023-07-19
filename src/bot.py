import telebot
from telebot import types
import boto3
import datetime
import re
from config import DefaultConfig


bot = telebot.TeleBot(token=DefaultConfig.BOT_TOKEN)
dynamoDB = boto3.client('dynamodb', endpoint_url=DefaultConfig.EXTERNAL_ENDPOINT)

class BotStatus:
    callback_status = False
    
    def __init__(self, callback_status) -> None:
        self.callback_status = callback_status

bot_status = BotStatus(False)

def scan_dynamo(table_name):
    response = dynamoDB.scan(TableName=table_name)
    return response['Items']

def query_dynamo(table_name, room_name):
    query_response = dynamoDB.query(
            TableName=table_name,
            KeyConditionExpression='#r = :room_name',
            ExpressionAttributeNames={
                '#r': 'room_name'
            },
            ExpressionAttributeValues={
                ':room_name': {'S': room_name}
            }
        )
    
    if query_response['Count'] == 1:
            return query_response['Items'][0]


    else: return None

def format_items(items):
    responses = []
    for item in items:
        item_response = format_item(item)
        responses.append(item_response)
    return responses

def format_item(item):
    room_name = item['room_name']['S']
    current_temperature = item['current_temperature']['N']
    current_vibration = item['current_vibration']['N']
    current_humidity = item['current_humidity']['N']
    last_update = str(datetime.datetime.utcfromtimestamp(float(item['timestamp']['N'])).strftime('%Y-%m-%d %H:%M:%S'))
    item_response = f"The {room_name} room has a temperature of {current_temperature}°C and a relative humidity of {current_humidity}%.\n{current_vibration} vibrations registered right now.\nLast update on {last_update} UTC"
    return item_response
     

@bot.message_handler(commands=['status'])
def get_status(message):
    items=scan_dynamo(DefaultConfig.NOSQL_TABLE_DEFAULT_NAME)
    messages=format_items(items)
    for response_message in messages:
        bot.send_message(chat_id=message.chat.id, text=response_message)

@bot.message_handler(commands=['room_info'])
def get_room_info(message):
    # Extract the room name from the message text using regular expression
    match = re.match(r'/room_info\s+(.+)', message.text)
    if match:
        room_name = match.group(1)  # Get the room name from the first capturing group
        item = query_dynamo(DefaultConfig.NOSQL_TABLE_DEFAULT_NAME, room_name)
        if item:
            item_response = format_item(item)
            bot.send_message(chat_id=message.chat.id, text=item_response)
        else:
            bot.send_message(chat_id=message.chat.id, text="No room found with this name.")
    else:
        bot.send_message(chat_id=message.chat.id, text="Invalid format. Please use /room_info room_name.")


@bot.message_handler(commands=["help"])
def send_help(message):
    cid = message.chat.id
    # Create the inline buttons
    button_status = types.InlineKeyboardButton(
        "System status", callback_data="get_status"
    )
    button_info = types.InlineKeyboardButton(
        "Room info", callback_data="get_room_info"
    )
    # Create the inline keyboard markup
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        button_status,
        button_info,
    )
    # Send the message with inline buttons
    bot.send_message(cid, "Choose a command:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    if call.data == "get_status":
        get_status(call.message)
    if call.data == "get_room_info":
        bot_status.callback_status = True
        bot.send_message(chat_id=call.message.chat.id, text="Please enter the room name:")

@bot.message_handler(func=lambda message: True)
def handle_user_response(message):
        if bot_status.callback_status:
            # The user's response is the room name, call the /room_info command
            message.text = "/room_info " + message.text
            # Call the get_room_info function with the room_name as if the user had entered /room_info directly
            get_room_info(message)
            bot_status.callback_status = False
        else: send_help(message)


# TODO: Function that handles the notification for sensor error

# TODO: Function that handles the notification for storage error

# TODO: Function that handles the notification for door error

# TODO: Function that recovers data from the S3 buckets and averages it 
    #TODO: temperature
    #TODO: humidity
    #TODO: vibration

# TODO: Function that creates a chart of the trend of vibration and temperature

# TODO: Function to retrieve Door Status


print('Bot started!')
bot.polling(True)