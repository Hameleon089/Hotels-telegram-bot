from telebot.types import Message

from loader import bot
from logs.loggers import func_logger


@bot.message_handler(state=None)
@func_logger
def bot_echo(message: Message):
    bot.reply_to(message, 'Я тебя не пониманию.'
                          '\nЧтобы узнать что я умею введи команду /help')
