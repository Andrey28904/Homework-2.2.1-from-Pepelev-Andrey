import requests
import pandas as pd
import os, shutil
import csv
import json
import multiprocessing as mp

class HH_Vacancies:
    """Класс для получения вакансий с помощью API hh.ru.
    Attributes:
        data_dir (str): расположение будущего csv-файла.
        csv_name (str): название будущего csv-файла.
    """
    headers = ["name", "salary_from", "salary_to", "salary_currency", "area_name", "published_at"]

    def __init__(self, data_dir: str, csv_name: str):
        """Инициализация. создани директории и работа с API.
        Args:
            data_dir (str): расположение будущего csv-файла.
            csv_name (str): название будущего csv-файла.
        """
        self.data_dir = data_dir
        self.csv_name = csv_name
        HH_Vacancies.make_dir_if_needed(data_dir)
        self.all_files = self.create_processes()
        self.save_vacs()

    @staticmethod
    def make_dir_if_needed(dir: str) -> None:
        """Создание нужной дериктории."""
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.mkdir(dir)

    def get_salary_value(self, dic_vac: dict, param: str) -> str:
        """Попытаться получить конкретное значение param зарплаты. Если нет, то вернуть пустую строку.
        Args:
            dic_vac(dict): словарь с данными.
            param(str): параметр зарплаты.
        Returns:
            str: найденный параметр или пустая строка.
        """
        value = dic_vac["salary"][param]
        if value == None:
            return ""
        return value

    def try_to_get_salary(self, dic_vac: dict) -> list:
        """Попытаться получить значения зарплаты. Если нет, то вернуть массив с пустыми данными.
        Args:
            dic_vac(dict): словарь с данными.
        Returns:
            list: список значений зарплаты.
        """
        if dic_vac["salary"] == None:
            return ["", "", ""]
        return [self.get_salary_value(dic_vac, "from"),
                self.get_salary_value(dic_vac, "to"),
                self.get_salary_value(dic_vac, "currency")]

    def process_json_data(self, vacs_json: pd.DataFrame) -> list:
        """получить из json словарь и переработать его в список вакансий.
        Args:
            vacs_json (pd.DataFrame): json-дата с вакансиями.
        Returns:
            list: список вакансий.
        """
        all_vacs_data = []
        for json_data in vacs_json.values:
            dic_vac = json_data[0]
            new_vac_line = [dic_vac["name"]] + self.try_to_get_salary(dic_vac)
            new_vac_line += [dic_vac["area"]["name"], dic_vac["published_at"]]
            all_vacs_data.append(new_vac_line)
            print(new_vac_line)
        return all_vacs_data

    def get_vacancies(self, j: int, file_path: str) -> None:
        """Функция для одного процесса. делает запросы, созраняет результат в маленький файл с полным именем file_path
        Args:
            j (int): текущий период.
            file_path (str): имя будущего csv-файла.
        """
        page_from = 0
        page_to = 100
        all_vacs_data = []
        for i in range(page_from, page_to):
            while(True):
                new_url = f"https://api.hh.ru/vacancies?per_page=20&page={i}&specialization=1&period={j}"
                req = requests.get(new_url)
                if req.status_code == 200:
                    break
                if req.status_code == 403:
                    json_error = pd.read_json(req.content.decode())
                    error_value = json_error.values[0][0]["captcha_url"]
                    print(error_value + "&backurl=" + new_url)
                else:
                    print(str(req.status_code) + " -> " + req.text)
            vacs_json = pd.read_json(req.content.decode())
            all_vacs_data += self.process_json_data(vacs_json)
        with open(file=file_path, mode="w", encoding="utf-8-sig", newline='') as csv_basic_file:
            csv_base = csv.writer(csv_basic_file)
            csv_base.writerows(all_vacs_data)

    def create_processes(self) -> list:
        """создание параллельной обработки периодов с помощью 30-ти процессов.
        Returns:
            list: список всех маленьких файлов, которые надо обработать.
        """
        all_procs = []
        all_files = []
        temp_dir = self.data_dir+"/temp"
        HH_Vacancies.make_dir_if_needed(temp_dir)
        for j in range(1, 31):
            file_path = temp_dir + "/file_" + str(j) + ".csv"
            print(file_path)
            all_files.append(file_path)
            proc = mp.Process(target=self.get_vacancies, args=(j, file_path))
            proc.start()
            all_procs.append(proc)
        for proc in all_procs:
            proc.join()
        return all_files

    def save_vacs(self):
        """Сохранение всех маленьких файлов в один большой."""
        all_vacs = []
        for file in self.all_files:
            with open(file=file, mode="r", encoding="utf-8-sig") as csv_file:
                lines = csv.reader(csv_file)
                all_vacs += [line for line in lines]
        with open(file=self.data_dir+"/"+self.csv_name, mode="a", encoding="utf-8-sig", newline='') as csv_basic_file:
            csv_base = csv.writer(csv_basic_file)
            csv_base.writerow(HH_Vacancies.headers)
            csv_base.writerows(all_vacs)


if __name__ == '__main__':
    vacancies_data = HH_Vacancies("api_hh", "vacancies_from_hh.csv")