import os

import requests

from dotenv import load_dotenv
from terminaltables import AsciiTable


def get_vacancies_from_hh(language='Python',
                          text='Программист', area=1, period=30, page=0):
    url = 'https://api.hh.ru/vacancies'
    headers = {'User-Agent': 'best_salary/1.0 (stanislavglazko@gmail.com)'}
    payload = {
        'text': f'{text} {language}',
        'area': area,
        'period': period,
        'page': page,
    }
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    return response.json()


def get_all_vacancies_from_hh(language='Python',
                              text='Программист', area=1, period=30):
    language_vacancies = []
    page = 0
    pages_number = 1
    while page < pages_number:
        response = get_vacancies_from_hh(language=language,
                                         text=text, area=area,
                                         period=period, page=page)
        pages_number = min(int(response['found'] / 20), 100)
        page += 1
        for vacancy in response['items']:
            language_vacancies.append(vacancy)
    return language_vacancies


def predict_salary(payment_from, payment_to):
    if payment_from and payment_to:
        return int((payment_from + payment_to) / 2)
    elif payment_from:
        return int(payment_from * 1.2)
    elif payment_to:
        return int(payment_to * 0.8)
    return None


def predict_rub_salary_hh(salary):
    if salary and salary['currency'] == 'RUR':
        return predict_salary(salary['from'], salary['to'])


def get_salary_of_vacancies_hh(vacancies, language='Python'):
    salaries = []
    for vacancy in vacancies[language]:
        salary = predict_rub_salary_hh(vacancy['salary'])
        if salary:
            salaries.append(salary)
    if len(salaries) > 0:
        return int(sum(salaries) / len(salaries)), len(salaries)


def get_salary_of_vacancies_sj(vacancies, language='Python'):
    salaries = []
    for vacancy in vacancies[language]:
        salary = predict_rub_salary_sj(vacancy)
        if salary:
            salaries.append(salary)
    if len(salaries) > 0:
        return int(sum(salaries) / len(salaries)), len(salaries)


def sj_authorization(secret_key_sj, login_sj, password_sj, id_sj):
    url = 'https://api.superjob.ru/2.33/oauth2/password/'
    headers = {'X-Api-App-Id': secret_key_sj}
    payload = {
        'login': login_sj,
        'password': password_sj,
        'client_id': id_sj,
        'client_secret': secret_key_sj,
    }
    response = requests.post(url, headers=headers, params=payload)
    response.raise_for_status()
    return response.json()['access_token']


def get_vacancies_from_sj(secret_key_sj, login_sj,
                          password_sj, id_sj, town=4,
                          page=0, language='Python'):
    url = 'https://api.superjob.ru/2.33/vacancies/'
    token = sj_authorization(secret_key_sj, login_sj, password_sj, id_sj)
    headers = {
        'X-Api-App-Id': secret_key_sj,
        'Authorization': f'Bearer {token}',
    }
    payload = {
        'keyword': f'Программист {language}',
        'town': town,
        'count': 100,
        'page': page,
    }
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    return response.json()


def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] == 'rub':
        return predict_salary(vacancy['payment_from'], vacancy['payment_to'])


def get_all_vacancies_from_sj(secret_key_sj, login_sj,
                              password_sj, id_sj,
                              town=4, page=0, language='Python'):
    language_vacancies = []
    page = 0
    more_vacancies = True
    while more_vacancies:
        response = get_vacancies_from_sj(
            secret_key_sj,
            login_sj,
            password_sj,
            id_sj,
            town=town,
            page=page,
            language=language,
        )
        more_vacancies = response['more']
        for vacancy in response['objects']:
            language_vacancies.append(vacancy)
        page += 1
    return language_vacancies


def get_table(languages, title='SuperJob Moscow'):
    table_data = []
    headers = [
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата',
    ]
    table_data.append(headers)
    for language, statistic in languages.items():
        new_row = [
            language,
            statistic['vacancies_found'],
            statistic['vacancies_processed'],
            statistic['average_salary'],
        ]
        table_data.append(new_row)
    table = AsciiTable(table_data, title=title)
    return table


def collect_vacancies_for_top8_hh():
    top_8_languages = [
        'JavaScript',
        'Java',
        'Python',
        'Ruby',
        'PHP',
        'C++',
        'C#',
        'Go',
    ]
    vacancies = {}
    for name in top_8_languages:
        vacancies[name] = get_all_vacancies_from_hh(language=name)
    return vacancies


def count_average_salary_hh():
    vacancies = collect_vacancies_for_top8_hh()
    languages = {}
    for name_language in vacancies.keys():
        languages[name_language] = {
            'vacancies_found': 0,
            'vacancies_processed': 0,
            'average_salary': 0,
        }
        languages[name_language]['vacancies_found'] = \
            get_vacancies_from_hh(language=name_language)['found']
        languages[name_language]['average_salary'], languages[name_language]['vacancies_processed'] \
            = get_salary_of_vacancies_hh(vacancies, name_language)
    return languages


def collect_vacancies_for_top8_sj(secret_key_sj, login_sj, password_sj, id_sj):
    top_8_languages = [
        'JavaScript',
        'Java',
        'Python',
        'Ruby',
        'PHP',
        'C++',
        'C#',
        'Go',
    ]
    vacancies = {}
    for name in top_8_languages:
        vacancies[name] = get_all_vacancies_from_sj(
            secret_key_sj,
            login_sj,
            password_sj,
            id_sj,
            language=name,
        )
    return vacancies


def count_average_salary_sj(secret_key_sj, login_sj, password_sj, id_sj):
    vacancies = collect_vacancies_for_top8_sj(
        secret_key_sj,
        login_sj,
        password_sj,
        id_sj,
    )
    languages = {}
    for name_language in vacancies.keys():
        languages[name_language] = {
            'vacancies_found': 0,
            'vacancies_processed': 0,
            'average_salary': 0,
        }
        languages[name_language]['vacancies_found'] = \
            get_vacancies_from_sj(
                secret_key_sj,
                login_sj,
                password_sj,
                id_sj,
                language=name_language,
            )['total']
        languages[name_language]['average_salary'], languages[name_language]['vacancies_processed'] \
            = get_salary_of_vacancies_sj(vacancies, name_language)
    return languages


def main():
    load_dotenv()
    secret_key_sj = os.getenv("SECRET_KEY_SUPERJOB")
    login_sj = os.getenv("LOGIN_SUPERJOB")
    password_sj = os.getenv("PASSWORD_SUPERJOB")
    id_sj = os.getenv("CLIENT_ID_SUPERJOB")
    table_hh = get_table(count_average_salary_hh(), title='HeadHunter Moscow')
    table_sj = get_table(count_average_salary_sj(
        secret_key_sj,
        login_sj,
        password_sj,
        id_sj,
    ))
    print(table_hh.table)
    print(table_sj.table)


if __name__ == '__main__':
    main()
