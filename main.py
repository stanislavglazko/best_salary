import json
import os
import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable

languages_hh = {
    'JavaScript': {'vacancies_found': 0, 'vacancies_processed': 0, 'average_salary': 0},
    'Java': {'vacancies_found': 0, 'vacancies_processed': 0, 'average_salary': 0},
    'Python': {'vacancies_found': 0, 'vacancies_processed': 0, 'average_salary': 0},
    'Ruby': {'vacancies_found': 0, 'vacancies_processed': 0, 'average_salary': 0},
    'PHP': {'vacancies_found': 0, 'vacancies_processed': 0, 'average_salary': 0},
    'C++': {'vacancies_found': 0, 'vacancies_processed': 0, 'average_salary': 0},
    'C#': {'vacancies_found': 0, 'vacancies_processed': 0, 'average_salary': 0},
    'Go': {'vacancies_found': 0, 'vacancies_processed': 0, 'average_salary': 0}
}

languages_sj = {
    'JavaScript': {'vacancies_found': 0, 'vacancies_processed': 0, 'average_salary': 0},
    'Java': {'vacancies_found': 0, 'vacancies_processed': 0, 'average_salary': 0},
    'Python': {'vacancies_found': 0, 'vacancies_processed': 0, 'average_salary': 0},
    'Ruby': {'vacancies_found': 0, 'vacancies_processed': 0, 'average_salary': 0},
    'PHP': {'vacancies_found': 0, 'vacancies_processed': 0, 'average_salary': 0},
    'C++': {'vacancies_found': 0, 'vacancies_processed': 0, 'average_salary': 0},
    'C#': {'vacancies_found': 0, 'vacancies_processed': 0, 'average_salary': 0},
    'Go': {'vacancies_found': 0, 'vacancies_processed': 0, 'average_salary': 0}
}

vacancies_hh = {
    'JavaScript': [],
    'Java': [],
    'Python': [],
    'Ruby': [],
    'PHP': [],
    'C++': [],
    'C#': [],
    'Go': [],
}

vacancies_sj = {
    'JavaScript': [],
    'Java': [],
    'Python': [],
    'Ruby': [],
    'PHP': [],
    'C++': [],
    'C#': [],
    'Go': [],
}


def get_vacancies_from_hh(language='Python', text='Программист', area=1, period=30, page=0):
    url = 'https://api.hh.ru/vacancies'
    headers = {'User-Agent': 'best_salary/1.0 (stanislavglazko@gmail.com)'}
    payload = {'text': f'{text} {language}',
               'area': area, 'period': period, 'page': page}
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    return response.json()


def get_number_of_vacancies_hh(language='Python',
                               text='Программист', area=1, period=30, page=0):
    return get_vacancies_from_hh(language=language, text=text,
                                 area=area, period=period, page=page)['found']


def get_all_vacancies_from_hh(language='Python', text='Программист', area=1, period=30):
    global vacancies_hh
    page = 0
    pages_number = 1
    while page < pages_number:
        response = get_vacancies_from_hh(language=language,
                                         text=text, area=area, period=period, page=page)
        pages_number = min(int(response['found'] / 20), 100)
        page += 1
        for vacancy in response['items']:
            vacancies_hh[language].append(vacancy)


def predict_salary(currency, payment_from, payment_to):
    if currency != 'RUR' and currency != 'rub':
        return None
    if payment_from is not None and payment_from != 0:
        if payment_to is not None and payment_to != 0:
            return int((payment_from + payment_to) / 2)
        else:
            return int(payment_from * 1.2)
    else:
        if payment_to is not None and payment_to != 0:
            return int(payment_to * 0.8)
        return None


def predict_rub_salary_hh(salary):
    return predict_salary(salary['currency'],
                          salary['from'], salary['to'])


def get_salary_of_vacancies_hh(language='Python'):
    salaries = []
    global vacancies_hh
    for vacancy in vacancies_hh[language]:
        if vacancy['salary'] is not None:
            predict_salary_hh = predict_rub_salary_hh(vacancy['salary'])
            if predict_salary_hh is not None:
                salaries.append(predict_salary_hh)
    if len(salaries) > 0:
        return int(sum(salaries) / len(salaries)), len(salaries)


def sj_authorization(secret_key, login, password, id):
    url = 'https://api.superjob.ru/2.33/oauth2/password/'
    headers = {'X-Api-App-Id': secret_key}
    payload = {'login': login, 'password': password,
               'client_id': id, 'client_secret': secret_key}
    response = requests.post(url, headers=headers, params=payload)
    response.raise_for_status()
    return response.json()['access_token']


def get_vacancies_from_sj(secret_key, login, password, id, town=4, page=0, language='Python'):
    url = 'https://api.superjob.ru/2.33/vacancies/'
    token = sj_authorization(secret_key, login, password, id)
    headers = {'X-Api-App-Id': secret_key,
               'Authorization': f'Bearer {token}'}
    payload = {'keyword': f'Программист {language}',
               'town': town, 'count': 100, 'page': page}
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    return response.json()


def predict_rub_salary_sj(vacancy):
    return predict_salary(vacancy['currency'],
                          vacancy['payment_from'], vacancy['payment_to'])


def get_all_vacancies_from_sj(secret_key, login,
                              password, id, town=4, page=0, language='Python'):
    global vacancies_sj
    page = 0
    more_vacancies = True
    while more_vacancies:
        response = get_vacancies_from_sj(secret_key, login,
                                         password, id, town=town, page=page, language=language)
        more_vacancies = response['more']
        for vacancy in response['objects']:
            vacancies_sj[language].append(vacancy)
        page += 1


def get_salary_of_vacancies_sj(language='Python'):
    salaries = []
    global vacancies_sj
    for vacancy in vacancies_sj[language]:
        predict_salary_sj = predict_rub_salary_sj(vacancy)
        if predict_salary_sj is not None:
            salaries.append(predict_salary_sj)
    if len(salaries) > 0:
        return int(sum(salaries) / len(salaries)), len(salaries)


def print_table(source, title):
    table_data = []
    headers = ['Язык программирования', 'Вакансий найдено',
               'Вакансий обработано', 'Средняя зарплата']
    table_data.append(headers)
    for key in source.keys():
        new_row = []
        new_row.append(key)
        new_row.append(source[key]['vacancies_found'])
        new_row.append(source[key]['vacancies_processed'])
        new_row.append(source[key]['average_salary'])
        table_data.append(new_row)
    table = AsciiTable(table_data)
    table.title = title
    print(table.table)


def print_table_hh(title='HeadHunter Moscow'):
    print_table(languages_hh, title)


def print_table_sj(title='SuperJob Moscow'):
    print_table(languages_sj, title)


def count_vacancies_and_average_salary(secret_key, login, password, id):
    global vacancies_sj
    global vacancies_hh
    for key in vacancies_sj.keys():
        get_all_vacancies_from_sj(secret_key,
                                  login, password, id, language=key)
        get_all_vacancies_from_hh(language=key)
    for key in languages_sj.keys():
        languages_sj[key]['vacancies_found'] = \
            get_vacancies_from_sj(secret_key,
                                  login, password, id, language=key)['total']
        languages_sj[key]['average_salary'], languages_sj[key]['vacancies_processed'] \
            = get_salary_of_vacancies_sj(key)
        languages_hh[key]['vacancies_found'] = get_number_of_vacancies_hh(language=key)
        languages_hh[key]['average_salary'], languages_hh[key]['vacancies_processed'] \
            = get_salary_of_vacancies_hh(key)


def main():
    load_dotenv()
    secret_key = os.getenv("SECRET_KEY_SUPERJOB")
    login = os.getenv("LOGIN_SUPERJOB")
    password = os.getenv("PASSWORD_SUPERJOB")
    id = os.getenv("CLIENT_ID_SUPERJOB")
    count_vacancies_and_average_salary(secret_key, login, password, id)
    print_table_sj()
    print_table_hh()


if __name__ == '__main__':
    main()
