from datetime import date, datetime, timedelta
from typing import List, Dict, Optional

from loader import bot
from states.search_info import SearchInfoState
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup
from telegram_bot_calendar import DetailedTelegramCalendar

from keyboards.calendar_ru import LSTEP
from keyboards.inline.cities import city_markup
from keyboards.inline.photos import photos_markup
from keyboards.inline.hotels import hotels_markup
from utils.city_founding import city_founding
from utils.hotel_founding import lowprice_founding, highprice_founding, bestdeal_founding
from utils.hotel_detail import hotel_detail
from utils.result_output import result_output


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def start_search(message: Message) -> None:
    """
    Message handler. Начало поиска отелей:
    - запрашивается город для поиска
    - сохраняется информация о пользователе и введенной команде

    :param message: сообщение
    """

    user_id: int = message.from_user.id
    chat_id: int = message.chat.id

    bot.set_state(user_id, SearchInfoState.city, chat_id)
    bot.send_message(user_id, 'В каком городе будем искать?')

    with bot.retrieve_data(user_id, chat_id) as data:
        data['command'] = message.text
        data['date_time'] = datetime.utcnow().strftime('%d.%m.%Y %H:%M:%S')
        data['user_id'] = user_id
        data['chat_id'] = chat_id


@bot.message_handler(state=SearchInfoState.city)
def enter_city(message: Message) -> None:
    """
    Message handler.
    - уточняется город для поиска

    :param message: сообщение
    """

    user_id: int = message.from_user.id
    chat_id: int = message.chat.id

    cities_dict: Dict[str, str] = city_founding(message.text)
    if cities_dict:
        with bot.retrieve_data(user_id, chat_id) as data:
            data['cities'] = cities_dict
        cities_keyboard: InlineKeyboardMarkup = city_markup(cities_dict)
        text: str = 'Уточните пожалуйста место поиска:'
        bot.send_message(user_id, text, reply_markup=cities_keyboard)
        bot.set_state(user_id, SearchInfoState.get_city, chat_id)
    else:
        text: str = 'Похоже ничего не нашлось или произошла ошибка! ' \
               'Попробуйте еще раз.' \
               '\nВ каком городе будем искать?'
        bot.send_message(user_id, text)


@bot.callback_query_handler(func=lambda call: True,
                            state=SearchInfoState.get_city)
def get_city(call: CallbackQuery) -> None:
    """
    CallbackQuery handler.
    - сохраняется город для поиска
    - запрашивается дата заезда в отель

    :param call: обратный вызов
    """

    user_id: int = call.from_user.id
    chat_id: int = call.message.chat.id
    message_id: int = call.message.message_id

    with bot.retrieve_data(user_id, chat_id) as data:
        city_id: str = call.data
        data['city_id'] = city_id
        data['city'] = data['cities'][city_id]
        del data['cities']
        city: str = data['city']
    bot.edit_message_text(f'Место для поиска: {city}', chat_id, message_id)

    calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru',
                                              min_date=date.today()
                                              ).build()

    bot.send_message(user_id, f'Укажите дату заезда: выберите {LSTEP[step]}',
                     reply_markup=calendar)
    bot.set_state(user_id, SearchInfoState.date_in, chat_id)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1),
                            state=SearchInfoState.date_in)
def get_date_in(call: CallbackQuery) -> None:
    """
    CallbackQuery handler.
    - сохраняется дата заезда в отель
    - запрашивается дата отъезда из отеля

    :param call: обратный вызов
    """

    user_id: int = call.from_user.id
    chat_id: int = call.message.chat.id
    message_id: int = call.message.message_id

    result, key, step = DetailedTelegramCalendar(calendar_id=1,
                                                 locale='ru',
                                                 min_date=date.today()
                                                 ).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Укажите дату заезда: выберите {LSTEP[step]}",
                              chat_id, message_id, reply_markup=key)
    elif result:
        bot.edit_message_text(f"Дата заезда: {result.strftime('%d.%m.%Y')}",
                              chat_id, message_id)

        with bot.retrieve_data(user_id, chat_id) as data:
            data['date_in'] = result.strftime('%d.%m.%Y')
            min_date: date = result + timedelta(days=1)

        calendar, step = DetailedTelegramCalendar(calendar_id=2, locale='ru',
                                                  min_date=min_date
                                                  ).build()
        bot.set_state(user_id, SearchInfoState.date_out, chat_id)
        bot.send_message(user_id, 'Укажите дату отъезда: '
                                  f'выберите {LSTEP[step]}',
                         reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2),
                            state=SearchInfoState.date_out)
def get_date_out(call: CallbackQuery) -> None:
    """
    CallbackQuery handler.
    - сохраняется дата отъезда из отеля
    - запрашивается количество отелей

    :param call: обратный вызов
    """

    user_id: int = call.from_user.id
    chat_id: int = call.message.chat.id
    message_id: int = call.message.message_id

    with bot.retrieve_data(user_id, chat_id) as data:
        min_date: date = (datetime.strptime(data['date_in'], '%d.%m.%Y') +
                          timedelta(days=1)).date()
    result, key, step = DetailedTelegramCalendar(calendar_id=2,
                                                 locale='ru',
                                                 min_date=min_date
                                                 ).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Укажите дату отъезда: выберите {LSTEP[step]}",
                              chat_id, message_id, reply_markup=key)
    elif result:
        bot.edit_message_text(f"Дата отъезда: {result.strftime('%d.%m.%Y')}",
                              chat_id, message_id)

        with bot.retrieve_data(user_id, chat_id) as data:
            data['date_out'] = result.strftime('%d.%m.%Y')
        bot.set_state(user_id, SearchInfoState.hotels_amount, chat_id)
        bot.send_message(user_id, 'Какое количество отелей вам вывести?',
                         reply_markup=hotels_markup())


@bot.callback_query_handler(func=lambda call: True,
                            state=SearchInfoState.hotels_amount)
def get_hotels_amount(call: CallbackQuery) -> None:
    """
    CallbackQuery handler.
    - сохраняется количество отелей
    - запрашивается количество фотографий для каждого отеля

    :param call: обратный вызов
    """

    user_id: int = call.from_user.id
    chat_id: int = call.message.chat.id
    message_id: int = call.message.message_id

    bot.edit_message_text(f'Количество отелей для вывода: {call.data}',
                          chat_id, message_id)
    bot.set_state(user_id, SearchInfoState.photos, chat_id)
    text: str = 'Сколько фотографий выводить для каждого отеля?'
    bot.send_message(user_id, text, reply_markup=photos_markup())
    with bot.retrieve_data(user_id, chat_id) as data:
        data['hotels_amount'] = int(call.data)


@bot.callback_query_handler(func=lambda call: True,
                            state=SearchInfoState.photos)
def photos(call: CallbackQuery) -> None:
    """
    CallbackQuery handler.
    - сохраняется количество фотографий для каждого отеля
    - для команд /lowprice и /highprice:
    запрашиваются данные с API и выводятся результаты поиска
    - для команды /bestdeal:
    запрашивается минимальная цена за сутки

    :param call: обратный вызов
    """

    user_id: int = call.from_user.id
    chat_id: int = call.message.chat.id
    message_id: int = call.message.message_id

    if call.data == '0':
        text: str = 'Для отелей не будут выведены фотографии.'
    else:
        text: str = f'Для каждого отеля будет выведено фотографий: {call.data}'

    bot.edit_message_text(text, chat_id, message_id)
    with bot.retrieve_data(user_id, chat_id) as data:
        data['photos_amount'] = int(call.data)
        command: str = data['command']
        cur_data: dict = data

    hotels = None
    waiting_text: str = 'Пожалуйста подождите...'
    if command == '/lowprice':
        bot.send_message(user_id, waiting_text)
        hotels: Optional[List[dict]] = lowprice_founding(cur_data)
        hotels: Optional[List[dict]] = hotel_detail(hotels,
                                                    cur_data['photos_amount'])
    elif command == '/highprice':
        bot.send_message(user_id, waiting_text)
        hotels: Optional[List[dict]] = highprice_founding(cur_data)
        hotels: Optional[List[dict]] = hotel_detail(hotels, cur_data['photos_amount'])

    if command == '/bestdeal':
        bot.set_state(user_id, SearchInfoState.min_price, chat_id)
        bot.send_message(user_id, 'Укажите минимальную цену за сутки (в руб.)')
    elif hotels:
        bot.set_state(user_id, SearchInfoState.result, chat_id)
        date_in = datetime.strptime(cur_data['date_in'], '%d.%m.%Y')
        date_out = datetime.strptime(cur_data['date_out'], '%d.%m.%Y')
        days = (date_out - date_in).days
        result_output(hotels, cur_data['user_id'], days)
    else:
        text = 'Похоже ничего не нашлось или произошла ошибка! ' \
               'Попробуйте позже или установите другие параметры для поиска'
        bot.send_message(user_id, text)


@bot.message_handler(state=SearchInfoState.min_price)
def get_min_price(message: Message) -> None:
    """
    Message handler.
    - сохраняется минимальная цена за сутки
    - запрашивается максимальная цена за сутки

    :param message: сообщение
    """

    user_id: int = message.from_user.id
    chat_id: int = message.chat.id

    if not message.text.isdigit():
        text: str = 'Нужно указать целое число. Попробуйте еще раз.' \
                    '\nУкажите минимальную цену за сутки (в руб.)'
        bot.send_message(user_id, text)
    else:
        bot.set_state(user_id, SearchInfoState.max_price, chat_id)
        bot.send_message(user_id,
                         'Укажите максимальную цену за сутки (в руб.)')
        with bot.retrieve_data(user_id, chat_id) as data:
            data['min_price'] = int(message.text)


@bot.message_handler(state=SearchInfoState.max_price)
def get_max_price(message: Message) -> None:
    """
    Message handler.
    - сохраняется максимальная цена за сутки
    - запрашиваются данные с API и выводятся результаты поиска

    :param message: сообщение
    """

    user_id: int = message.from_user.id
    chat_id: int = message.chat.id
    with bot.retrieve_data(user_id, chat_id) as data:
        min_price = data['min_price']

    if not message.text.isdigit():
        text: str = 'Нужно указать целое число. Попробуйте еще раз.' \
                    '\nУкажите максимальную цену за сутки (в руб.)'
        bot.send_message(user_id, text)
    elif min_price >= int(message.text):
        text: str = 'Максимальная цена за сутки должна быть больше ' \
                    'минимальной цены за сутки. Попробуйте еще раз.' \
                    '\nУкажите максимальную цену за сутки (в руб.)'
        bot.send_message(user_id, text)
    else:
        with bot.retrieve_data(user_id, chat_id) as data:
            data['max_price'] = int(message.text)
            cur_data: dict = data
        bot.send_message(user_id, 'Пожалуйста подождите...')
        hotels: Optional[List[dict]] = bestdeal_founding(cur_data)
        hotels: Optional[List[dict]] = hotel_detail(hotels,
                                                    cur_data['photos_amount'])
        if hotels:
            bot.set_state(user_id, SearchInfoState.result, chat_id)
            date_in = datetime.strptime(cur_data['date_in'], '%d.%m.%Y')
            date_out = datetime.strptime(cur_data['date_out'], '%d.%m.%Y')
            days = (date_out - date_in).days
            result_output(hotels, cur_data['user_id'], days)
        else:
            text = 'Похоже ничего не нашлось или произошла ошибка! ' \
                   'Попробуйте позже или установите другие параметры для поиска'
            bot.send_message(user_id, text)
