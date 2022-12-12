from telebot.types import Message

from loader import bot
from logs.loggers import func_logger


@bot.message_handler(commands=['start'])
@func_logger
def bot_start(message: Message):
    bot.reply_to(message, f"Привет, {message.from_user.full_name}!")
