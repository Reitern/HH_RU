import json
import functions
import sqlite3
import os

db = sqlite3.connect('hh_ru.db')
cursor = db.cursor()
# создание таблицы
cursor.execute("""CREATE TABLE IF NOT EXISTS vacancy(
    id TEXT PRIMARY KEY,
    v_name TEXT,
    salary_from INT,
    salary_to INT);""")
db.commit()

# очистить таблицу от прошлых данных
cursor.execute("DELETE FROM vacancy")
db.commit()

# узнать id города по его названию
functions.area_id = functions.fnd_city_id('Россия', 'Ярославль')

# удалить файлы из папки pages
for file in os.scandir(path='./pages'):
    if file.name.endswith(".json"):
        os.unlink(file.path)

# удалить файлы из папки vacancies
for file in os.scandir(path='./vacancies'):
    if file.name.endswith(".json"):
        os.unlink(file.path)

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
    db.commit()

# выводим заполненную таблицу
for value in cursor.execute("SELECT * FROM vacancy"):
    print(value)

# находим и выводим максимальную зарплату с вакансией
cursor.execute("SELECT MAX(salary_from) FROM vacancy")
result1 = cursor.fetchone()

cursor.execute("SELECT MAX(salary_to) FROM vacancy")
result2 = cursor.fetchone()

print()

if result1 > result2:
    print('Максимальная ЗП: ' + str(result1[0]))
    cursor.execute("SELECT * FROM vacancy WHERE salary_from = (SELECT MAX(salary_from) FROM vacancy)")
    print(cursor.fetchall())
else:
    print('Максимальная ЗП: ' + str(result2[0]))
    cursor.execute("SELECT * FROM vacancy WHERE salary_to = (SELECT MAX(salary_to) FROM vacancy)")
    print(cursor.fetchall())

# находим и выводим минимсальную зарплату с вакансией
cursor.execute("SELECT MIN(salary_from) FROM vacancy")
result1 = cursor.fetchone()

cursor.execute("SELECT MIN(salary_to) FROM vacancy")
result2 = cursor.fetchone()

print()

if result1 < result2:
    print('Минимальная ЗП: ' + str(result1[0]))
    cursor.execute("SELECT * FROM vacancy WHERE salary_from = (SELECT MIN(salary_from) FROM vacancy)")
    print(cursor.fetchall())
else:
    print('Минимальная ЗП: ' + str(result2[0]))
    cursor.execute("SELECT * FROM vacancy WHERE salary_to = (SELECT MIN(salary_to) FROM vacancy)")
    print(cursor.fetchall())

# находим и выводим среднюю зарплату
print()
cursor.execute("SELECT AVG((salary_to+salary_from) / 2) FROM vacancy")
print('Средняя ЗП: ' + str(round(cursor.fetchone()[0])))
