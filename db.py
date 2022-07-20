import logging
import sqlite3


def sqlite_connection():
    try:
        return sqlite3.connect('database/example.db')
    except sqlite3.Error as error:
        logging.error(
            f"Ошибка при создании db sqlite {error}", exc_info=True)


def lower_string(_str):
    return _str.lower()


def cities_create_update(cities) -> None:
    try:
        connection = sqlite_connection()
        create_table = (
            'CREATE TABLE IF NOT EXISTS cities'
            '(name TEXT PRIMARY KEY,'
            ' href TEXT,'
            ' population INTEGER)'
        )
        cursor = connection.cursor()
        cursor.execute(create_table)
        logging.info("База городов создана и успешно подключена к sqlite")
        insert = """INSERT INTO cities
                (name, href, population)
                VALUES (?, ?, ?)
                ON CONFLICT (name) 
                DO UPDATE SET
                (name, href, population) = (EXCLUDED.name, EXCLUDED.href, 
                EXCLUDED.population);"""
        cursor.executemany(
            insert, (*cities, ))
        logging.info("Обновлённые данные внесены в sqlite")
        cursor.close()
        connection.commit()
    except sqlite3.Error as error:
        logging.error(
            f"Ошибка при подключении к sqlite {error}", exc_info=True)
    finally:
        if connection:
            connection.close()


def cities_find(city_fragment) -> list:
    try:
        connection = sqlite_connection()
        cursor = connection.cursor()
        connection.create_function("lower_function", 1, lower_string)
        query = """SELECT name, href, population
                FROM cities
                WHERE lower_function(name)
                LIKE ?;"""
        cursor.execute(
            query,
            ('%' + city_fragment.lower() + '%',)
        )
        logging.info("Запрос городов из БД выполнен")
        records = cursor.fetchall()
        cursor.close()
        connection.commit()
        return records
    except sqlite3.Error as error:
        logging.error(
            f"Ошибка при подключении к sqlite {error}", exc_info=True)
    finally:
        if connection:
            connection.close()
