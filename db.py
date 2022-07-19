import logging
import sqlite3


def my_connection():
    return sqlite3.connect('database/example.db')


def lower_string(_str):
    return _str.lower()


def cities_create_update(cities) -> None:
    try:
        sqlite_connection = my_connection()
        create_table = (
            'CREATE TABLE IF NOT EXISTS cities'
            '(name TEXT PRIMARY KEY,'
            ' href TEXT,'
            ' population INTEGER)'
        )
        cursor = sqlite_connection.cursor()
        logging.info("База городов создана и успешно подключена к PostrgeSQL")
        cursor.execute(create_table)
        logging.info('Таблица PostrgeSQL создана')
        insert = """INSERT INTO cities
                (name, href, population)
                VALUES (?, ?, ?)
                ON CONFLICT (name) 
                DO UPDATE SET
                (name, href, population) = (EXCLUDED.name, EXCLUDED.href, 
                EXCLUDED.population);"""
        cursor.executemany(
            insert, (*cities, ))
        cursor.close()
        sqlite_connection.commit()
    except sqlite3.Error as error:
        logging.error(
            f"Ошибка при подключении к sqlite {error}", exc_info=True)
    finally:
        if sqlite_connection:
            sqlite_connection.close()


def cities_find(city_fragment) -> list:
    try:
        sqlite_connection = my_connection()
        cursor = sqlite_connection.cursor()
        sqlite_connection.create_function("lower_function", 1, lower_string)
        query = """SELECT name, href, population
                FROM cities
                WHERE lower_function(name)
                LIKE ?;"""
        cursor.execute(
            query,
            ('%' + city_fragment.lower() + '%',)
        )
        records = cursor.fetchall()
        cursor.close()
        sqlite_connection.commit()
        return records
    except sqlite3.Error as error:
        logging.error(
            f"Ошибка при подключении к sqlite {error}", exc_info=True)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
