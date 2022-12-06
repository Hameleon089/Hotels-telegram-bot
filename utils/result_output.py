from typing import List

from loader import bot


def result_output(result: List[dict], user_id: int, days: int) -> None:
    """
    Выводит результаты поиска отелей в сообщения пользователю

    :param result: результаты поиска отелей
    :param user_id: id пользователя
    :param days: количество дней проживания в отеле
    """
    for num, hotel in enumerate(result):
        address: str = hotel["address"]
        if not address:
            address: str = 'нет данных'
        text: str = f'Отель №{num + 1}: ' \
                    f'\n\nНазвание: {hotel["hotel"]}' \
                    f'\nАдрес: {address}' \
                    f'\nРасстояние от центра: {hotel["distance"]:.2f} км' \
                    f'\nЦена за один день: {hotel["price"]:.1f} руб.' \
                    f'\nЦена за все дни (дней - {days}): ' \
                    f'{hotel["price"] * days:.1f} руб.' \
                    f'\n\nСсылка: ' \
                    f'https://www.hotels.com/h{hotel["hotel_id"]}.' \
                    f'Hotel-Information'
        bot.send_message(user_id, text)
        for photo in hotel['photos_list']:
            bot.send_photo(user_id, photo)
