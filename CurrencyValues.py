import requests
import pandas as pd
import os, shutil
import csv
from ReportPDF_New_MProcess_2 import Error, Timer
from datetime import datetime

class Currency_Values_Creator:
    """Класс для работы с API Центробанка
    Attributes:
        data_dir (str): имя папки для файлов.
        csv_name (str): название csv_файла, который нужно будет создать.
    """
    temp_needed_fields = ["CharCode", "Nominal", "Value"]
    start_basic_row = ["Year", "Month", "CharCode", "InRuR"]

    def __init__(self, data_dir: str, csv_name: str):
        """Инициализация класса Currency_Values. Создание CSV-файла.
        Args:
            data_dir (str): имя папки для файлов.
            csv_name (str): имя будущего файла с данными по валютам.
        """
        self.data_dir = data_dir
        self.temp_xml_name = "temp_xml.xml"
        self.temp_csv_name = "temp_csv.csv"
        self.start_year = 2003
        self.start_month = 1
        self.end_year = datetime.now().year
        self.end_month = datetime.now().month
        self.index_of = {}
        self.create_csv(csv_name)

    def make_dir_if_needed(self) -> None:
        """Создание нужной дериктории"""
        if os.path.exists(self.data_dir):
            shutil.rmtree(self.data_dir)
        os.mkdir(self.data_dir)

    def get_start_and_end_months(self, cur_year: int) -> (int, int):
        """Получение начального и конечного месяца для запросов
        Args:
            cur_year (int): текущий год, который рассматриваем.
        Returns:
            (int, int): начальный месяц и конечный месяц для цикла запросов.
        """
        start_month_value = 1
        if cur_year == self.start_year:
            start_month_value = self.start_month
        end_month_value = 12
        if cur_year == self.end_year:
            end_month_value = self.end_month
        return start_month_value, end_month_value

    def get_needed_url(self, year: int, month: int) -> str:
        """Получение url-адреса по текущему году и месяцу.
        Args:
            year (int): текущий год.
            month (str): текущий месяц.
        Returns:
            str: корректный url-адрес.
        """
        str_month = str(month)
        if month < 10:
            str_month = "0" + str(month)
        return f"http://www.cbr.ru/scripts/XML_daily.asp?date_req=01/{str_month}/{str(year)}"

    def url_to_csv(self, cur_url: str) -> str:
        """Конвертация полученных их хапроса данных в CSV.
        Args:
            cur_url (str): адрес данных.
        Returns:
            str: имя полученного CSV-файла."""
        data = requests.get(cur_url)
        full_xml_path = self.data_dir + "/" + self.temp_xml_name
        file = open(file=full_xml_path, mode="w", encoding="utf-8-sig")
        file.write(data.text)
        file.close()
        full_csv_path = self.data_dir + "/" + self.temp_csv_name
        pd.read_xml(full_xml_path).to_csv(full_csv_path, index=False)
        return full_csv_path

    def save_data_from_xml(self, cur_year: int, cur_month: int, csv_name: str) -> None:
        """Преобразует данные из xml и добавляет их к итоговуму csv-файлу.
        Args:
            cur_year (int): год, по которому нужно получить данные.
            cur_month (int): месяц, по которому нужно получить данные.
            csv_name (str): файл, в который будут добавляться данные.
        """
        cur_url = self.get_needed_url(cur_year, cur_month)
        print(cur_url)
        full_csv_path = self.url_to_csv(cur_url)
        with open(file=self.data_dir+"/"+csv_name, mode="a", encoding="utf-8-sig", newline='') as csv_basic_file:
            csv_base = csv.writer(csv_basic_file)
            with open(file=full_csv_path, mode="r", encoding="utf-8-sig") as csv_file:
                temp_file = csv.reader(csv_file)
                start_temp_line = next(temp_file)
                if len(self.index_of.items()) == 0:
                   self.get_indexes(start_temp_line)
                   csv_base.writerow(Currency_Values_Creator.start_basic_row)
                for temp_line in temp_file:
                    print(temp_line)
                    value = float(temp_line[self.index_of["Value"]].replace(",","."))
                    delimiter = int(temp_line[self.index_of["Nominal"]])
                    new_row = [cur_year, cur_month, temp_line[self.index_of["CharCode"]], round(value/delimiter, 10)]
                    csv_base.writerow(new_row)
                csv_file.close()
            csv_basic_file.close()

    def get_indexes(self, temp_start_line: list) -> None:
        """Получить индексы для нужных столбцов.
        Args:
            temp_start_line (list): та строка, из которой получаем индексы.
        """
        for field in Currency_Values_Creator.temp_needed_fields:
            try:
                field_index = temp_start_line.index(field)
                self.index_of[field] = field_index
            except:
                Error("MISSING_INDEX", "Can't find index of \"" + field + "\"", True, Timer("", 0))

    def create_csv(self, csv_name: str) -> None:
        """Создание полного csv-файла с валютами."""
        self.make_dir_if_needed()
        for cur_year in range(self.start_year, self.end_year+1):
            start_month_value, end_month_value = self.get_start_and_end_months(cur_year)
            for cur_month in range(start_month_value, end_month_value+1):
                self.save_data_from_xml(cur_year, cur_month, csv_name)


if __name__ == '__main__':
    values_creator = Currency_Values_Creator("api_data", "currency_csv.csv")

