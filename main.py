import logging
import os
import sys
from http import HTTPStatus
from json import JSONDecodeError
from typing import Optional

import requests
import asyncio
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from requests import RequestException
from telebot.async_telebot import AsyncTeleBot
from telebot import types, ExceptionHandler
from telebot.types import Message

from db import cities_create_update, cities_find
from exceptions import BotException

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

PREFIX = 'https://ru.wikipedia.org'
RESPONSE_URL = (
        PREFIX
        + '/w/api.php?action=parse&page=%D0%93%D0%BE%D1%80%D0%BE%D0%B4%D1%81'
          '%D0%BA%D0%B8%D0%B5_%D0%BD%D0%B0%D1%81%D0%B5%D0%BB%D1%91%D0%BD%D0'
          '%BD%D1%8B%D0%B5_%D0%BF%D1%83%D0%BD%D0%BA%D1%82%D1%8B_%D0%9C%D0%BE'
          '%D1%81%D0%BA%D0%BE%D0%B2%D1%81%D0%BA%D0%BE%D0%B9_%D0%BE%D0%B1%D0'
          '%BB%D0%B0%D1%81%D1%82%D0%B8&format=json'
)

HELP = """Этот телеграм бот предназначен для получения численности населения 
города московской области по его названию. Если ввести часть названия города, 
то в ответ придут подходящие варианты (если подходит только один город, 
то его численность и ссылка на Wiki). """


class BotExceptionHandler(ExceptionHandler):
    def handle(self, exception):
        logging.error(exception)


def check_tokens():
    """Проверка наличия констант в переменных окружения."""
    if TELEGRAM_TOKEN:
        return True


def get_api_answer():
    """Возвращает API ответ c Wikipedia."""
    try:
        wiki_page = requests.get(RESPONSE_URL)
        if wiki_page.status_code != HTTPStatus.OK:
            raise Exception(
                f"Пришел некорректный ответ от сервера:"
                f" status_code - {wiki_page.status_code}")
        else:
            return wiki_page.json()
    except RequestException as error:
        logging.error(error, exc_info=True)
    except JSONDecodeError as error:
        logging.error(error, exc_info=True)


def api_parsing() -> Optional[list]:
    """Парсим полученную страницу."""
    response = get_api_answer()
    if not response:
        logging.error('Не получен ответ от сервера.')
        return
    xml_page = response.get('parse').get('text').get('*')
    if xml_page:
        table = BeautifulSoup(xml_page, 'xml').find_all(
            'table', class_='standard sortable')[0].find('tbody')
        if table:
            rows = table.find_all('tr')
            cities = []
            for row in rows[1:]:
                name = row.find_all('td')[1].find('a').get('title')
                href = PREFIX + str(
                    row.find_all('td')[1].find('a').get('href')
                )
                population = row.find_all('td')[4].get('data-sort-value')
                cities.append((name, href, int(population)))
            return cities


def main():
    """Основная логика работы бота."""
    logging.basicConfig(
        level=logging.INFO,
        handlers=[logging.StreamHandler(sys.stdout), ],
        format=f'%(asctime)s, %(levelname)s, %(message)s, %(name)s')
    bot = AsyncTeleBot(TELEGRAM_TOKEN, exception_handler=ExceptionHandler())
    logging.info('Запуск бота')

    if not check_tokens():
        logging.critical('Отсутствуют переменные окружения.')
        raise BotException('Программа принудительно остановлена.'
                           ' Отсутствуют переменные окружения.')

    @bot.message_handler(commands=['update'])
    async def update(message: Message):
        parsing = api_parsing()
        cities_create_update(parsing)
        await bot.send_message(
            message.chat.id,
            'Cities updated.'
        )

    @bot.message_handler(commands=['start'])
    async def start(message):
        if message.chat.id == ADMIN_ID:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add('/update', )
            await bot.send_message(
                message.chat.id,
                "Добро пожаловать, Администратор",
                reply_markup=keyboard
            )
        else:
            await bot.send_message(message.chat.id, HELP)

    @bot.message_handler(content_types=['text'])
    async def input_text(message):
        find_cities = cities_find(message.text)
        if not find_cities:
            await bot.send_message(
                message.chat.id,
                'Не найдено похожих городов в Московской области'
            )
        elif len(find_cities) == 1:
            text = (
                'Наименование города: {0}.'
                + '\nЧисленность населения: {2}.'
                + '\nОписание на Wikipedia: {1}').format(*find_cities[0])
            await bot.send_message(
                message.chat.id,
                text
            )
        else:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            names = [city_name[0] for city_name in find_cities]
            keyboard.add(*names)
            await bot.send_message(
                message.chat.id,
                'Подходит несколько городов, выберите необходимый!',
                reply_markup=keyboard
            )

    asyncio.run(bot.polling(none_stop=True, timeout=60, request_timeout=600))


if __name__ == '__main__':
    main()
