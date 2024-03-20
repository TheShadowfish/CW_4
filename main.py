from src.api_interaction import HhApi
from src.vacancy import Vacancy

from src.connectors import VacancyJsonConnector
from src.connectors import VacancyCsvConnector
from src.connectors import VacancyTxtConnector
from src.connectors import VacancyFileConnector


def user_interaction():
    what_to_do = input("Выберите формат файла для сохранения данных: \n"
                       "TXT (vacancy.txt) (1) \n"
                       "CSV (vacancy.csv) (2) \n"
                       "JSON (vacancy.json) (3) (default) \n")

    if what_to_do == '1':
        file_connector = VacancyTxtConnector()
    elif what_to_do == '2':
        file_connector = VacancyCsvConnector()
    else:
        file_connector = VacancyJsonConnector()

    what_to_do = input(" Сделать запрос с HH.ru (1) \n"
                       " Загрузить вакансии из файла (2) \n"
                       " Загрузить из файла и отфильтровать (3) \n")

    # vacancy_list = []
    # json_connector = VacancyJsonConnector()
    # csv_connector = VacancyCsvConnector()
    # txt_connector = VacancyTxtConnector()

    if what_to_do == '1':
        vacancy_list = get_request_info(user_input(True), 'HeadHunter')
    elif what_to_do == '2':
        vacancy_list = open_file(file_connector)
    elif what_to_do == '3':
        vacancy_list = open_file(file_connector)
        vacancy_list = Vacancy.apply_filters(vacancy_list, user_input(False))
    else:
        exit(0)

    [print(f"{i}) {v}") for i, v in enumerate(vacancy_list, start=1)]

    while True:

        what_to_do = input(" Отфильтровать (1) \n Удалить дубликаты (2) \n"
                           " Пере-сохранить в файл (3) \n Добавить в файл (4)\n"
                           " Загрузить вакансии из файла (5) \n"
                           " Удалить конкретную вакансию (вакансии) из списка (6) \n"
                           " Выход БЕЗ СОХРАНЕНИЯ (7) \n"
                           " СОХРАНИТЬ результаты и выйти (8) \n")

        if what_to_do == '1':
            vacancy_list = Vacancy.apply_filters(vacancy_list, user_input(False))
        elif what_to_do == '2':
            vacancy_list = Vacancy.remove_duplicates(vacancy_list)
        elif what_to_do == '3':
            save_to_file(vacancy_list, file_connector, True)
        elif what_to_do == '4':
            save_to_file(vacancy_list, file_connector, False)
        elif what_to_do == '5':
            vacancy_list = open_file(file_connector)
        elif what_to_do == '6':
            v_list = verify_list(input("Номера вакансий, которые вы хотите удалить (введите номера через пробел)"),
                                 len(vacancy_list))
            print(v_list)
            if v_list:
                v_deleted = [vacancy for number, vacancy in enumerate(vacancy_list, start=1) if number in v_list]
                print("Будут удалены следующие вакансии: ")
                [print(f"{v_del[0]}) {v_del[1]}") for v_del in zip(v_list, v_deleted)]
                if input("Удалить? Y/N") not in ['т', 'T', 'N', 'n']:
                    vacancy_list = [v for num, v in enumerate(vacancy_list, start=1) if num not in v_list]

        elif what_to_do == '7':
            exit(0)
        elif what_to_do == '8':
            save_to_file(vacancy_list, file_connector, True)
            exit(0)
        else:
            pass

        [print(f"{i}) {v}") for i, v in enumerate(vacancy_list, start=1)]


def user_input(default: bool = False) -> dict[str, str | int | list[str]]:
    """
    Получение и обработка пользовательского ввода или значений по умолчанию
    """
    parameters = {'platforms': ['HeadHunter'],
                  'professional_role': 'Информационные технологии',
                  'filter_region': 'Санкт-Петербург',
                  'top_n': 10,
                  'filter_words': ['Python', 'backend', 'программист'],
                  'salary_range': '0 - 300000',
                  'per_page': 100
                  }

    if not default:
        print("Введите необходимые параметры запроса/выбора вакансий "
              "(отсутствие значения - параметр не используется)")
        parameters['platforms'] = ["HeadHunter"]
        parameters['professional_role'] = input("Введите специальность (область деятельности)")
        parameters['filter_region'] = input("Введите регион или город для поиска вакансий")

        top = input(f"Введите количество вакансий для вывода в топ N (default = {parameters['top_n']}): ")
        if top.isdigit():
            parameters['top_n'] = int(top)

        parameters['filter_words'] = input("Введите ключевые слова для фильтрации вакансий (через пробел): ").split()

        salary_range = input("Введите диапазон зарплат (Пример: 100000 - 150000): ")  # Пример: 100000 - 150000

        if salary_range == '':
            parameters['salary_range'] = salary_range
        else:
            salary = [int(s.strip()) for s in salary_range.split('-') if s.strip().isdigit()]
            # input(f'{salary}/// see')
            if len(salary) != 2 or salary[0] > salary[1]:
                print(f"Неверный диапазон. Используем значение по умолчанию ({parameters['salary_range']})")
            else:
                parameters['salary_range'] = salary_range

    return parameters


def get_request_info(parameters_input, api_type: str = 'HeadHunter') -> list[Vacancy]:
    """
    Проверка параметров ввода от пользователя, создание экземпляра HhApi, передача параметров в HhApi,
    возврат результатов в списке
    """
    # print(salary)
    if api_type not in parameters_input['platforms']:
        raise NotImplementedError(f"С платформой {api_type} взаимодействие пока не реализовано")

    if api_type == 'HeadHunter':

        parameters = HhApi.check_parameters_to_request(parameters_input)

        print(f"Parameters {parameters}")

        hh_api = HhApi(**parameters)

        print(f"Get vacation info from hh.ru... ({parameters})")
        res = hh_api.get_vacancies()
        print("Done!")

        # смотрим, сколько вакансий
        print(hh_api)

        user_question = ''
        if hh_api.pages > 2:
            user_question = input(f"Обработать все результаты поиска? {hh_api.found} - найдено на сайте, "
                                  f"выдача {hh_api.pages} страниц по {hh_api.per_page} вакансий? y/n")

        if user_question in {'y', 'Y', 'Н', 'н', ''}:
            vacancy_list = []
            for page_request in hh_api:
                print(f"loaded... Page {hh_api.page + 1} ({hh_api.per_page} per_page) "
                      f"from {hh_api.pages}: {round((hh_api.page + 1) * 100 / hh_api.pages)} %")

                v_next_page = HhApi.return_vacancy_list_from_json(page_request)
                vacancy_list.extend(v_next_page)

            else:
                return vacancy_list
        else:
            # res = hh_api.get_vacancies() - вакансии ТОЛЬКО с первой страницы результатов (page = 0)
            vacancy_list = HhApi.return_vacancy_list_from_json(res)
            return vacancy_list
            # [print(v) for v in vacancy_list]


def verify_list(vac_numbers: str, list_length: int) -> list[int] | None:
    """
    Обрабатывает и верифицирует список номеров вакансий, которые надо удалить
    :param list_length:
    :param vac_numbers: list[int] | None:
    :return: str
    """
    try:
        vac_list = [int(v) for v in vac_numbers.split(' ')]

        # bool_sum - число вакансий, номер которых превышает длину списка
        bool_sum = sum([(v > list_length) for v in vac_list])
        if bool_sum > 0:
            print(bool_sum)
            raise IndexError
        return vac_list
    except ValueError:
        print("Ошибка ValueError. Номер/номера удаляемых вакансий должны быть числами, разделенными пробелом")
        return None
    except IndexError:
        print("Ошибка IndexError. Номер удаляемой вакансии должен быть в пределах списка вакансий")
        return None


def open_file(connector: VacancyFileConnector) -> list[Vacancy]:
    v_list_read = connector.read_from_file()
    return v_list_read


def save_to_file(vacancy_list, connector: VacancyFileConnector, rewrite: bool = True):
    if rewrite:
        connector.write_to_file(vacancy_list)
    else:
        connector.append_to_file(vacancy_list)


# начало программы
if __name__ == '__main__':
    user_interaction()
