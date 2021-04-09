import json
import os
import functions
from config import (db, cursor)


def create_tables():
    cursor.execute("""CREATE TABLE IF NOT EXISTS vacancy(
        id TEXT PRIMARY KEY,
        v_name TEXT,
        salary_from INT,
        salary_to INT);""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS main_cities(
            city_name TEXT PRIMARY KEY,
            salary_from INT,
            salary_to INT,
            avg_salary INT);""")


def load_data(country_name, city_name):
    # очистить таблицу от прошлых данных
    cursor.execute("DELETE FROM vacancy")
    db.commit()

    # удалить файлы из папки pages
    for file in os.scandir(path='./pages'):
        if file.name.endswith(".json"):
            os.unlink(file.path)

    # удалить файлы из папки vacancies
    for file in os.scandir(path='./vacancies'):
        if file.name.endswith(".json"):
            os.unlink(file.path)

    functions.area_id = functions.fnd_city_id(country_name, city_name)

    # загрузить страницы в папку
    functions.writing_pages()

    # загрузить вакансии в папку
    functions.writing_vacancies()
    print()

    for fl in os.listdir('./vacancies'):
        f = open('./vacancies/{}'.format(fl), encoding='utf8')  # получение файла из папки
        json_text = f.read()  # считывание вакансии в переменную
        f.close()
        v = json.loads(json_text)

        # заполняем таблицу значениями из полученных вакансий
        cursor.execute(f"INSERT INTO vacancy VALUES (?, ?, ?, ?)",
                       (v['id'], v['name'], v['salary']['from'], v['salary']['to']))

    # выводим заполненную таблицу
    # for value in cursor.execute("SELECT * FROM vacancy"):
    #     print(value)

    cursor.execute(f"INSERT INTO main_cities VALUES (?, ?, ?, ?)",
                   (city_name, min_sal(), max_sal(), avg_sal()))
    db.commit()


def max_sal():
    # находим и выводим максимальную зарплату с вакансией
    cursor.execute("SELECT MAX(salary_from) FROM vacancy")
    result1 = cursor.fetchone()

    cursor.execute("SELECT MAX(salary_to) FROM vacancy")
    result2 = cursor.fetchone()

    if result1 > result2:
        return result1[0]
    else:
        return result2[0]


def min_sal():
    # находим и выводим минимсальную зарплату с вакансией
    cursor.execute("SELECT MIN(salary_from) FROM vacancy")
    result1 = cursor.fetchone()

    cursor.execute("SELECT MIN(salary_to) FROM vacancy")
    result2 = cursor.fetchone()

    if result1 < result2:
        return result1[0]
    else:
        return result2[0]


def avg_sal():
    cursor.execute("SELECT AVG((salary_to+salary_from) / 2) FROM vacancy")
    result = cursor.fetchone()
    return result[0]


def get_from_main(city_name):
    city = [(str(city_name))]
    cursor.execute("SELECT * FROM main_cities WHERE city_name = ?", city)
    if cursor.fetchone() is None:
        return False
    else:
        return True
