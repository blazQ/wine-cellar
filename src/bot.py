import telebot
from config import DefaultConfig


bot = telebot.TeleBot(token=DefaultConfig.BOT_TOKEN)

@bot.message_handler(content_types=['text'])
def message_received(message):
    bot.send_message(chat_id=message.from_user.id, text=message.text)

# TODO: Function that handles the get status command.

# TODO: Function that handles the notification for sensor error

# TODO: Function that handles the notification for storage error

# TODO: Function that handles the notification for door error

# TODO: Function to get specific information regarding a room


bot.polling(True)