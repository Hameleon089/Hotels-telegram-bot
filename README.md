# Hotels Telegram Bot

Телеграм бот для поиска информации об отелях по всему миру

## Используемые технологии
* Python (3.10)
* API: [Hotels API (RapidAPI)](https://rapidapi.com/apidojo/api/hotels4)
* Database: SQLite
* ORM: [Peewee (3.15.4)](https://docs.peewee-orm.com/en/latest/)
* Loging: [Loguru (0.6.0)](https://github.com/Delgan/loguru)
* [PyTelegramBotApi (4.8.0)](https://github.com/eternnoir/pyTelegramBotAPI)
* Python-dotenv (0.21.0)
* [Python-telegram-bot-calendar (1.0.5)](https://github.com/artembakhanov/python-telegram-bot-calendar)
* [Keyboa (3.1.0)](https://github.com/torrua/keyboa)
* Requests (2.28.1)

## Описание

### Команды бота:

* `/help` — помощь по командам бота
* `/lowprice` — вывод самых дешёвых отелей в городе
* `/highprice` — вывод самых дорогих отелей в городе
* `/bestdeal` — вывод отелей, наиболее подходящих по цене и расположению от центра
* `/history` — вывод истории поиска отелей

### Работа бота:

#### Команды `/lowprice`, `/highprice`, `/bestdeal`

Бот последовательно запрашивает у пользователя следующую информацию:

* Город для поиска отелей
* Дата заезда в отель
* Дата отъезда из отеля
* Количество отелей для вывода в результатах
* Количество фотографий, которое необходимо выводить для каждого отеля в результатах
* Минимальная стоимость отеля за сутки (только для команды `/bestdeal`)
* Максимальная стоимость отеля за сутки (только для комады `/bestdeal`)

После, выводятся результаты поиска отелей.

## Установка
1. Скопировать все содержимое репозитория
2. Создать новое виртуальное окружение python
3. Установить все библиотеки из `requirements.txt`
4. Переименовать файл `.env.template` в `.env` и заполнить в нем данные (токен бота Telegram и ключ от RapidAPI)

## Запуск
Для запуска бота необходимо запустить файл `main.py`.
