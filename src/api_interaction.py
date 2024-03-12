import requests
from abc import ABC, abstractmethod


class AbstractApiNoAuth(ABC):
    """
    Абстрактный класс для работы с API сервиса с вакансиями
    """

    @abstractmethod
    def get_vacancies(self, **parameters: dict[str: str]) -> list[dict]:
        pass

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def __next__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass


class HhApi(AbstractApiNoAuth):
    """
    Класс для работы с API сервиса hh.ru
    """

    def __init__(self, url: str = 'https://api.hh.ru/vacancies', **parameters: dict[str: str]):
        self.__url = url
        self.__parameters = parameters
        self.found = None
        self.pages = 0
        self.page = 0
        self.per_page = 0

        # print(self.__parameters)
        # input("wait...")

    def get_vacancies(self) -> list[dict]:
        # URL = 'https://api.hh.ru/vacancies'
        # sub_url = 'vacancies'

        res = requests.get(self.__url, params=self.__parameters)
        if res.status_code != 200:
            raise Exception(f"Request code= {res.status_code}, request='{self.__url}', params={self.__parameters}")

        self.found = res.json()['found']
        self.pages = res.json()['pages']
        self.page = res.json()['page']
        self.per_page = res.json()['per_page']

        return res.json()['items']

    def __iter__(self):
        self.current = 0
        return self
    #
    # def __next__(self):
        # if self.current < self.pages:
        #     number = self.current
        #     self.current += 1
        #
        #     def get_request(self, sub_url: str = 'vacancies', **parameters: dict[str: str]) -> list[dict]:
        #
        #     return self.data[number]
        # else:
        #     raise StopIteration

    def __next__(self) -> list[dict]:
        # URL = 'https://api.hh.ru/vacancies'

        if self.current < self.pages:
            self.page = self.current
            self.__parameters['page'] = self.page
            self.current += 1
                # return self.data[number]
            res = requests.get(self.__url, params=self.__parameters)
            if res.status_code != 200:
                raise Exception(f"Request code= {res.status_code}, request='{self.__url}', params={self.__parameters}")

            # self.page += 1
            # self.__parameters['page'] = self.page

            # self.found = res.json()['found']
            # self.pages = res.json()['pages']
            # self.page = res.json()['page']
            # self.per_page = res.json()['per_page']

            return res.json()['items']
        else:
            raise StopIteration


    def __repr__(self):
        repr_list = [str(i[0]) + ': ' + str(i[1]) for i in self.__dict__.items()]
        return f"<{self.__class__.__name__}({', '.join(repr_list)})>"
    def __str__(self):
        repr_list = [str(i[0]) + ': ' + str(i[1]) for i in self.__dict__.items()]
        delimeter = f'\n\t'
        return f"{self.__class__.__name__}{delimeter}{delimeter.join(repr_list)}"


    @classmethod
    def get_area_id(cls, area_name: str = 'Москва') -> str | None:
        """
        Возврат ID по имени населенного пункта или области
        """
        URL_area = 'https://api.hh.ru/areas'
        res = requests.get(URL_area)

        if res.status_code != 200:
            raise Exception(f"Request code= {res.status_code}, request='{URL_area}'")

        area = res.json()
        result = cls.recursive_find_area_id(area, area_name)

        return result

    @classmethod
    def recursive_find_area_id(cls, areas, area_name) -> int | None:
        """
        Найти в древовидной структуре словаря areas (HH.ru) искомый город
        """
        for area in areas:
            if area['name'] == area_name:
                return area['id']
            elif isinstance(area['areas'], list) and len(area['areas']) > 0:
                result = cls.recursive_find_area_id(area['areas'], area_name)
                if result is not None:
                    return result
            else:
                continue
        else:
            return None