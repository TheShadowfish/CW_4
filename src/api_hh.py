import requests
from abc import ABC, abstractmethod


class AbstractApiNoAuth(ABC):
    """
    Абстрактный класс для работы с API сервиса с вакансиями
    """

    # @abstractmethod
    # def __init__(self, url: str, api_key: str, *parameters: tuple[str]):
    #     pass

    @abstractmethod
    def get_request(self, **parameters: dict[str: str]) -> str:
        pass


class HhApi(AbstractApiNoAuth):
    """
    Класс для работы с API сервиса hh.ru
    """

    def __init__(self, url: str):
        self.__url = url
        # self.__parameters = parameters

    def get_request(self, sub_url: str = '', **parameters: dict[str: str]) -> requests:
        # URL = 'https://api.hh.ru/vacancies'

        res = requests.get(self.__url + sub_url, params=parameters)

        # print(res.status_code)
        #
        # print(res.json())
        # >> > {'alternate_url': 'https://hh.ru/search/vacancy?enable_snippets=true&text=Python',
        #       'arguments': None,
        #       'clusters': None,
        #       'fixes': None,
        #       'found': 13182,
        #       'items': [...]
        #       }
        # print(f"response2: status_code: {response2.status_code} \n result: \n {response2.text}")

        return res