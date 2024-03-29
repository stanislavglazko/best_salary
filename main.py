import os
from collections import defaultdict

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
        pages_number = response['pages']
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


def predict_rub_salary_hh(vacancy):
    if vacancy['salary'] and vacancy['salary']['currency'] == 'RUR':
        return predict_salary(
            vacancy['salary']['from'],
            vacancy['salary']['to'],
        )


def get_salary_of_vacancies(vacancies, predict_rub_salary, language='Python'):
    salaries = []
    for vacancy in vacancies[language]:
        salary = predict_rub_salary(vacancy)
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


def get_vacancies_from_sj(secret_key_sj, token, login_sj,
                          password_sj, id_sj, town=4,
                          page=0, language='Python'):
    url = 'https://api.superjob.ru/2.33/vacancies/'
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


def get_all_vacancies_from_sj(secret_key_sj, token, login_sj,
                              password_sj, id_sj,
                              town=4, page=0, language='Python'):
    language_vacancies = []
    page = 0
    more_vacancies = True
    while more_vacancies:
        response = get_vacancies_from_sj(
            secret_key_sj,
            token,
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
    table_rows = []
    headers = [
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата',
    ]
    table_rows.append(headers)
    for language, statistic in languages.items():
        new_row = [
            language,
            statistic['vacancies_found'],
            statistic['vacancies_processed'],
            statistic['average_salary'],
        ]
        table_rows.append(new_row)
    table = AsciiTable(table_rows, title=title)
    return table


def collect_vacancies_from_hh(top_languages):
    vacancies = {}
    for name in top_languages:
        vacancies[name] = get_all_vacancies_from_hh(language=name)
    return vacancies


def count_average_salary_hh(top_languages):
    vacancies = collect_vacancies_from_hh(top_languages)
    languages = defaultdict(dict)
    for language_name in vacancies.keys():
        languages[language_name]['vacancies_found'] = \
            get_vacancies_from_hh(
                language=language_name,
            )['found']
        languages[language_name]['average_salary'], languages[language_name]['vacancies_processed'] \
            = get_salary_of_vacancies(
            vacancies,
            predict_rub_salary_hh,
            language_name,
        )
    return languages


def collect_vacancies_from_sj(top_languages, token,
                                  secret_key_sj, login_sj, password_sj, id_sj):
    vacancies = {}
    for name in top_languages:
        vacancies[name] = get_all_vacancies_from_sj(
            secret_key_sj,
            token,
            login_sj,
            password_sj,
            id_sj,
            language=name,
        )
    return vacancies


def count_average_salary_sj(
        top_languages,
        token,
        secret_key_sj,
        login_sj,
        password_sj,
        id_sj):
    vacancies = collect_vacancies_from_sj(
        top_languages,
        token,
        secret_key_sj,
        login_sj,
        password_sj,
        id_sj,
    )
    languages = defaultdict(dict)
    for language_name in vacancies.keys():
        languages[language_name]['vacancies_found'] = \
            get_vacancies_from_sj(
                secret_key_sj,
                token,
                login_sj,
                password_sj,
                id_sj,
                language=language_name,
            )['total']
        languages[language_name]['average_salary'], languages[language_name]['vacancies_processed'] \
            = get_salary_of_vacancies(
            vacancies,
            predict_rub_salary_sj,
            language_name,
        )
    return languages


def main():
    top_languages = [
        'JavaScript',
        'Java',
        'Python',
        'Ruby',
        'PHP',
        'C++',
        'C#',
        'Go',
    ]
    load_dotenv()
    secret_key_sj = os.getenv("SECRET_KEY_SUPERJOB")
    login_sj = os.getenv("LOGIN_SUPERJOB")
    password_sj = os.getenv("PASSWORD_SUPERJOB")
    id_sj = os.getenv("CLIENT_ID_SUPERJOB")
    token = sj_authorization(
        secret_key_sj,
        login_sj,
        password_sj,
        id_sj,
    )
    table_hh = get_table(
        count_average_salary_hh(top_languages),
        title='HeadHunter Moscow',
    )
    table_sj = get_table(count_average_salary_sj(
        top_languages,
        token,
        secret_key_sj,
        login_sj,
        password_sj,
        id_sj,
    ))
    print(table_hh.table)
    print(table_sj.table)


if __name__ == '__main__':
    main()
