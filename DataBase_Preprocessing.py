import pandas as pd

import csv, math
import shutil, os
import sqlite3
import datetime


class Vacancy_Small:
    """Информация о мини-вакансии.
    Attributes:
        dic (dict): Словарь информации о зарплате.
    """
    def __init__(self, dic: dict):
        """Инициализация объекта Vacancy_Small. Приведение к более удобному виду.
        Args:
            dic (dict): Словарь информации про зарплату.
        """
        self.dic = dic
        self.salary = round(float(dic["salary"]), 1)

    def get_list(self) -> list:
        """Получить список значений вакансии для дальнейшего сохранения в csv
        Returns:
            list: вакансия в виде списка.
        """
        return [self.dic["name"], self.dic["salary"], self.dic["area_name"], self.dic["published_at"]]


class Vacancy_Big:
    """Информация о вакансии.
    Attributes:
        dic (dict): Словарь информации о зарплате.
        currency_value (float): курс валюты.
    """
    def __init__(self, dic: dict, currency_value: float):
        """Инициализация объекта Vacancy_Big. Приведение к более удобному виду.
        Args:
            dic (dict): Словарь информации про зарплату.
            currency_value (float): курс валюты.
        """
        self.dic = dic
        self.salary = self.get_salary(currency_value)

    def get_salary(self, currency_value: float) -> float:
        """Получить зарплату по новой формуле (левый-правый край, зарплата того года)
        Args:
            currency_value (float): курс валюты.
        Returns:
            float: зарплата в рублях по курсу того года.
        """
        try:
            salary_from = math.floor(float(self.dic["salary_from"]))
        except:
            salary_from = math.floor(float(self.dic["salary_to"]))
        try:
            salary_to = math.floor(float(self.dic["salary_to"]))
        except:
            salary_to = salary_from
        middle_salary = (salary_to + salary_from) / 2
        return middle_salary * currency_value

    def get_small(self) -> Vacancy_Small:
        """Получить уменьшенную версию вакансии.
        Returns:
            Vacancy_Small: уменьшенная версия вакансии.
        """
        new_dict = {
            "name": self.dic["name"],
            "salary": self.salary,
            "area_name": self.dic["area_name"],
            "published_at": self.dic["published_at"][:10],
        }
        return Vacancy_Small(new_dict)


class DB_Preprocessing:
    """Класс для получения ьазы данных из csv-файла.
    Attributes:
        currency_path: путь до файла с валютами.
        vacancy_csv_path: путь до начального csv-файла.
        vacancy_db_path: директория будущей базы данных.
        vacancy_db_name: название будущей базы данных.
    """
    needed_fields = ["name", "salary_from", "salary_to", "salary_currency", "area_name", "published_at"]
    new_needed_fields = ["name", "salary", "area_name", "published_at"]
    minimum_count_currencies = 50

    def __init__(self, currency_path: str, vacancy_csv_path: str, vacancy_db_path: str, vacancy_db_name: str):
        """Формирование стартовых данных и csv -> база данных.
        Args:
            currency_path: путь до файла с валютами.
            vacancy_csv_path: путь до начального csv-файла.
            vacancy_db_path: директория будущей базы данных.
            vacancy_db_name: название будущей базы данных.
        """
        self.currency_path = currency_path
        self.vacancy_csv_path = vacancy_csv_path
        self.vac_db_path = vacancy_db_path
        self.vac_db_name = vacancy_db_name
        self.start_line, self.index_of, self.all_currencies = self.get_start_values()
        self.currency_dict = self.get_currency_dict()
        self.read_csv_and_create_db()

    @staticmethod
    def get_indexes(start_line: list) -> dict:
        """Получить индексы для нужных столбцов.
        Args:
            start_line(list): список заголовков csv-файла.
        Returns:
            dict: словарь индексов заголовков csv-файла.
        """
        index_of = {}
        for field in DB_Preprocessing.needed_fields:
            try:
                field_index = start_line.index(field)
                index_of[field] = field_index
            except:
                print("Can't find "+field)
        return index_of

    @staticmethod
    def try_to_add(dic: dict, key, val) -> dict:
        """Попытка добавить в словарь значение по ключу или создать новый ключ, если его не было.
        Args:
            dic (dict): Словарь, в который добавляется ключ или значение по ключу.
            key: Ключ.
            val: Значение.
        Returns:
            dict: Изменный словарь.
        """
        try:
            dic[key] += val
        except:
            dic[key] = val
        return dic

    def get_start_values(self) -> (list, dict, dict):
        """Получение старовых данных для обработки.
        Returns:
            (list, dict, dict): список заголовков, словарь индексов заголовков, словарь кол-ва валют в файле.
        """
        all_currencies = {}
        with open(self.vacancy_csv_path, "r", encoding='utf-8-sig', newline='') as csv_file:
            file = csv.reader(csv_file)
            start_line = next(file)
            index_of = DB_Preprocessing.get_indexes(start_line)
            for line in file:
                if len(line) == len(start_line):
                    all_currencies = \
                        DB_Preprocessing.try_to_add(all_currencies, line[index_of["salary_currency"]], 1)
        csv_file.close()
        return start_line, index_of, all_currencies

    def get_currency_dict(self) -> dict:
        """Получает курс валют из базы данных.
        Returns:
            dict: словарь данных про валюты.
        """
        currency_dict = {}
        connect = sqlite3.connect(self.currency_path)
        cursor = connect.cursor()
        headers = [head[1] for head in cursor.execute("PRAGMA table_info('currencies')").fetchall()]
        df = pd.read_sql(f"SELECT * FROM currencies", connect)
        for val in df.values:
            currency_dict[val[0]] = {}
            for index in range(1, len(val)):
                currency_dict[val[0]][headers[index]] = val[index]
        return currency_dict

    @staticmethod
    def make_dir_if_needed(dir: str) -> None:
        """Создание нужной дериктории.
        Args:
            dir(str): нужная директория.
        """
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.mkdir(dir)

    def is_numeric_value(self, line: list, index_str: str) -> bool:
        """Проерка, можно ли кастовать значение по индексу index к типу float.
        Args:
            line (list): вакансия-строка.
            index_str (str): значение позиции.
        Returns:
            bool: молжно ли кастовать к числу.
        """
        try:
            float(line[self.index_of[index_str]])
        except:
            return False
        return True

    def try_to_get_vacancy(self, line: list) -> Vacancy_Small or None:
        """Проверка списка на соответствие требованиям вакансии.
        Args:
            line (list): список значений для проверки.
        Returns:
            Vacancy_Small or None: вакансия или None.
        """
        is_normal_len = len(line) == len(self.start_line)
        line_cur = line[self.index_of["salary_currency"]]
        if line_cur == "" or not is_normal_len:
            return None
        is_valid_cur = self.all_currencies[line_cur] > DB_Preprocessing.minimum_count_currencies
        sal_from = self.is_numeric_value(line, "salary_from")
        sal_to = self.is_numeric_value(line, "salary_to")
        data = line[self.index_of["published_at"]][:7]
        if is_valid_cur and (sal_from or sal_to):
            try:
                currency_value = self.currency_dict[data][line_cur]
                if math.isnan(currency_value):
                    return None
                new_vac_dict = dict(zip(self.start_line, line))
                big_vac = Vacancy_Big(new_vac_dict, currency_value)
                return big_vac.get_small()
            except:
                return None
        return None

    def create_db_from_data(self, temp_file_name: str) -> None:
        """Создание базы данных из полученных данных.
        Args:
            temp_file_name(str): имя временного csv-файла с профессиями.
        """
        full_db_name = self.vac_db_path + "/" + self.vac_db_name
        conn = sqlite3.connect(full_db_name)
        conn.execute("DROP TABLE IF EXISTS vacancies")
        pd.read_csv(temp_file_name).to_sql("vacancies", conn, index=False)

    def read_csv_and_create_db(self) -> None:
        """Чтение csv, фильтрация вакансий и формирование базы данных."""
        DB_Preprocessing.make_dir_if_needed(self.vac_db_path)
        count = 0
        temp_file_name = self.vac_db_path + "/" + "temp.csv"
        with open(file=temp_file_name, mode="a", encoding="utf-8-sig", newline='') as csv_basic_file:
            csv_base = csv.writer(csv_basic_file)
            csv_base.writerow(DB_Preprocessing.new_needed_fields)
            with open(self.vacancy_csv_path, "r", encoding='utf-8-sig', newline='') as csv_file:
                file = csv.reader(csv_file)
                next(file)
                for line in file:
                    vac = self.try_to_get_vacancy(line)
                    if vac is not None:
                        count+=1
                        csv_base.writerow(vac.get_list())
                        print(count, vac.get_list())
            csv_file.close()
        csv_basic_file.close()
        self.create_db_from_data(temp_file_name)


if __name__ == '__main__':
    preprocess = DB_Preprocessing("db_currencies/currencies.db", "api_hh/vacancies_from_hh.csv",
                                  "vacancies_database", "vacancies.db")
