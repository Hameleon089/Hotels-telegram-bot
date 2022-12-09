from telebot.types import BotCommand
from telebot import TeleBot
from config_data.config import DEFAULT_COMMANDS


def set_default_commands(bot: TeleBot) -> None:
    """
    Устанавливает команды для бота

    :param bot: бот
    """
    bot.set_my_commands(
        [BotCommand(*i) for i in DEFAULT_COMMANDS]
    )
