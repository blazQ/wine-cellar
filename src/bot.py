import datetime
import os
import re
import requests
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

from io import BytesIO

import json
import telebot
from dotenv import load_dotenv
from telebot import types

from config import DefaultConfig

load_dotenv()
bot = telebot.TeleBot(token=os.environ.get("BOT_TOKEN"))
api_id = os.environ.get("API_ID")
room_endpoint = f"{DefaultConfig.EXTERNAL_ENDPOINT}/restapis/{api_id}/test/_user_request_/room"
door_endpoint = f"{DefaultConfig.EXTERNAL_ENDPOINT}/restapis/{api_id}/test/_user_request_/doors"
sensor_endpoint = f"{DefaultConfig.EXTERNAL_ENDPOINT}/restapis/{api_id}/test/_user_request_/sensor"

commands = ['/status', '/room_info', '/doors', '/charts']


@bot.message_handler(commands=['status'])
def get_status(message):
    # Request to API Endpoint
    query_params = {'room': '*'}
    items = requests.get(url=room_endpoint, params=query_params).json()
    messages=format_items(items)
    for response_message in messages:
        bot.send_message(chat_id=message.chat.id, text=response_message)

@bot.message_handler(commands=['room_info'])
def get_room_info(message):
    # Extract the room name from the message text using regular expression
    match = re.match(r'/room_info\s+(.+)', message.text)
    if match:
        room_name = match.group(1)  # Get the room name from the first capturing group
        # Request to API Endpoint
        query_params = {'room_name': room_name}
        item = requests.get(url=room_endpoint, params=query_params).json()
        if item:
            item_response = format_item(item)
            bot.send_message(chat_id=message.chat.id, text=item_response)
        else:
            bot.send_message(chat_id=message.chat.id, text="No room found with this name.")
    else:
        bot.send_message(chat_id=message.chat.id, text="Invalid format. Please use /room_info room_name.")

@bot.message_handler(commands=['doors'])
def get_doors(message):
    query_params = {'door': '*'}
    records = json.loads(requests.get(url=door_endpoint, params=query_params).json())
    for room in DefaultConfig.ROOM_CONFIGURATION:
            found = None
            for item in records:
                if item['room'] == room:
                    found = item
            if found:
                # Send the status
                bot.send_message(chat_id=message.chat.id, text=format_door(found))
            else:
                # No status available yet.
                bot.send_message(chat_id=message.chat.id, text=f"No status yet available for room {room}")

@bot.message_handler(commands=['chart_sensor'])
def get_sensor_chart(message):
    match = re.match(r'/chart_sensor\s+(.+)', message.text)
    if match:
        sensor_type = match.group(1)
        query_params = {'sensor_type': sensor_type}
        item = requests.get(url=sensor_endpoint, params=query_params).json()
        if item:
            charted_data = chart_data(item, sensor_type)
            # send charts
            for chart in charted_data:
                bot.send_photo(chat_id=message.chat.id, photo=chart)
        else:
            bot.send_message(chat_id=message.chat.id, text="No sensor data for the selected sensor type.")
    else:
        bot.send_message(chat_id=message.chat.id, text="Invalid format. Please use /chart sensor_type.")


@bot.message_handler(commands=['chart_room'])
def get_sensor_chart(message):
    match = re.match(r'/chart_room\s+(.+)', message.text)
    if match:
        room_name = match.group(1)
        if room_name in DefaultConfig.ROOM_CONFIGURATION:
            for sensor in DefaultConfig.SENSOR_CONFIGURATION:
                query_params = {'sensor_type': sensor, 'room_name': room_name}
                item = requests.get(url=sensor_endpoint, params=query_params).json()
                if item:
                    charted_data = chart_data(item, sensor)
                    # send charts
                    for chart in charted_data:
                        bot.send_photo(chat_id=message.chat.id, photo=chart)
                else:
                    bot.send_message(chat_id=message.chat.id, text=f"No sensor data for {sensor}")
        else: bot.send_message(chat_id=message.chat.id, text="No room with that name.")
    else:
        bot.send_message(chat_id=message.chat.id, text="Invalid format. Please use /chart_room room_name")


@bot.message_handler(commands=['chart'])
def get_sensor_chart(message):
    match = re.match(r'/chart\s+(\S+)\s+(\S+)', message.text)
    if match:
        sensor_type = match.group(1)
        room_name = match.group(2)
        if room_name in DefaultConfig.ROOM_CONFIGURATION:
            if sensor_type in DefaultConfig.SENSOR_CONFIGURATION:
                    query_params = {'sensor_type': sensor_type, 'room_name': room_name}
                    item = requests.get(url=sensor_endpoint, params=query_params).json()
                    if item:
                        charted_data = chart_data(item, sensor_type)
                        # send charts
                        for chart in charted_data:
                            bot.send_photo(chat_id=message.chat.id, photo=chart)
                    else:
                        bot.send_message(chat_id=message.chat.id, text=f"No sensor data for {sensor_type}")
            else: bot.send_message(chat_id=message.chat.id, text="No sensors with that type.")
        else: bot.send_message(chat_id=message.chat.id, text="No room with that name.")
    else:
        bot.send_message(chat_id=message.chat.id, text="Invalid format. Please use /chart room_name")

@bot.message_handler(commands=['door'])
def get_door_status(message):
    match = re.match(r'/door\s+(.+)', message.text)
    if match:
        room_name = match.group(1)
        if room_name in DefaultConfig.ROOM_CONFIGURATION:
            query_params = {'room_name': room_name}
            item = json.loads(requests.get(url=door_endpoint, params=query_params).json())
            if item:
                    bot.send_message(chat_id=message.chat.id, text=format_door(item))
            else:
                bot.send_message(chat_id=message.chat.id, text=f"No sensor data for {room_name}")
        else: bot.send_message(chat_id=message.chat.id, text="No room with that name.")
    else:
        bot.send_message(chat_id=message.chat.id, text="Invalid format. Please use /door room_name")


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
    item_response = f"The {room_name} room has a temperature of {current_temperature}°C and a relative humidity of {current_humidity}%.\n{current_vibration} g vibrations registered right now.\nLast update on {last_update} UTC"
    return item_response

def format_door(last_record):
    return f"The door for the {last_record['room']} room is currently {last_record['reading'].lower()}. Last measurement at {datetime.datetime.utcfromtimestamp(float(last_record['timestamp'])).strftime('%Y-%m-%d %H:%M:%S')}"

def chart_data(relevant_data, title):
    charts = []
    for room_data in relevant_data:
        if room_data:
            current_room_name = room_data[0]['room']
            # sort the data by timestamp
            sorted_room_data = sorted(room_data, key=lambda x: x['timestamp'])
            timestamps = [measurement['timestamp'] for measurement in sorted_room_data]
            timestamps = [datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") for ts in timestamps]
            readings = [measurement['reading'] for measurement in sorted_room_data]
            if readings[0] != 'Open' and readings[0] != 'Closed':
                readings = [float(reading) for reading in readings]

            plt.figure(figsize=(10, 6))
            plt.plot(timestamps, readings, marker='o', linestyle='-', color='b')
            plt.xlabel("Timestamp")
            plt.ylabel("Reading")
            plt.title(f"{title} for {current_room_name}")
            plt.grid(True)
            buffer = BytesIO()
            plt.savefig(buffer, format="png")
            buffer.seek(0)
            # add plot to charts
            charts.append(buffer)
    return charts

@bot.message_handler(commands=["help"])
def send_help(message):
    cid = message.chat.id
    # Create the inline buttons
    button_status = types.InlineKeyboardButton(
        "System Status", callback_data="get_status"
    )
    button_info = types.InlineKeyboardButton(
        "Room Info", callback_data="get_room_info"
    )
    button_doors = types.InlineKeyboardButton(
        "Doors Status", callback_data="get_doors"
    )
    button_door = types.InlineKeyboardButton(
        "Door Info", callback_data="get_door"
    )
    button_sensor_chart = types.InlineKeyboardButton(
        "Sensor Charts", callback_data="chart_sensor"
    )
    button_room_chart = types.InlineKeyboardButton(
        "Room Charts", callback_data="chart_room"
    )
    button_chart = types.InlineKeyboardButton(
        "Specific Charts", callback_data="chart"
    )

    # Create the inline keyboard markup
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        button_status,
        button_info,
        button_doors,
        button_door,
        button_sensor_chart,
        button_room_chart,
        button_chart
    )
    # Send the message with inline buttons
    bot.send_message(cid, "Choose a command:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    if call.data == "get_status":
        get_status(call.message)
    if call.data == "get_room_info":
        bot.send_message(chat_id=call.message.chat.id, text="Use /room_info room_name to view the status of room_name")
    if call.data == "get_doors":
        get_doors(call.message)
    if call.data == "get_door":
        bot.send_message(chat_id=call.message.chat.id, text="Use /door room_name to view the measurement history of room_name's door.")
    if call.data == "chart_sensor":
        bot.send_message(chat_id=call.message.chat.id, text="Use /chart_sensor sensor_type to view the measurement history of sensor_type for each room")
    if call.data == "chart_room":
        bot.send_message(chat_id=call.message.chat.id, text="Use /chart_room room_name to view the measurement history for room_name ")
    if call.data == "chart":
        bot.send_message(chat_id=call.message.chat.id, text="Use /chart sensor_type room_name to view the measurement history of sensor_type for room_name")

print('Bot started!')
bot.polling(True)
