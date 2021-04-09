import requests
import json
import time
import os

area_dict = {}
area_id = 0  # id города


# получить словарь стран
def country_dict():
    cntry_d = requests.get('https://api.hh.ru/areas').text
    return cntry_d


# получить номер города
def fnd_city_id(country_name, city_name):
    city_id = area_f = 0
    for country in json.loads(country_dict()):
         if country['name'] == country_name:
            area_dict = country['areas']
            break

    for area in area_dict:
        if area['name'] == city_name:
            city_id = area['id']
        else:
            for town in range(0, len(area['areas']) - 1):
                if area['areas'][town]['name'] == city_name:
                    city_id = area['areas'][town]['id']
                    area_f = 1
                    break
            if area_f == 1:
                break

    if city_id == 0:
        print('Not found')
    return city_id


# метод получения страниц с необходимым нам фильтром
def get_page(page):
    filters = dict(text='программист', area=area_id, only_with_salary='true', page=page, per_page=10)
    req = requests.get('https://api.hh.ru/vacancies', filters)
    data = req.content.decode(encoding='UTF8')
    req.close()
    return data


# в цикле получаем страницы и записываем их в файлы, в папку для страниц
def writing_pages():
    for page in range(0, 20):
        js_obj = json.loads(get_page(page))
        next_file_name = './pages/{}.json'.format(len(os.listdir('./pages')))
        f = open(next_file_name, mode='w', encoding='utf8')
        f.write(json.dumps(js_obj, ensure_ascii=False))
        f.close()

        if (js_obj['pages'] - page) <= 1:
            break

        time.sleep(0.25)
    return 0


# в цикле получаем вакансии и записываем их в файлы, в папку для вакансий
def writing_vacancies():
    for fl in os.listdir('./pages'):
        f = open('./pages/{}'.format(fl), encoding='utf8')  # получение файла из дериктории
        json_text = f.read()  # считывание страницы в переменную
        f.close()

        json_obj = json.loads(json_text)  # занесение переменной в объект

        # цикл проходит по каждой вакансии в странице
        for v in json_obj['items']:
            req = requests.get(v['url'])
            data = req.content.decode(encoding='utf8')
            req.close()

            # заполнение файла вакансиями
            file_name = './vacancies/{}.json'.format(v['id'])
            f = open(file_name, mode='w', encoding='utf8')
            f.write(data)
            f.close()

            time.sleep(0.25)
    return 0
