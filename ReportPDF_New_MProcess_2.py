import csv, math
import shutil, os
import time

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

import multiprocessing as mp
import concurrent.futures as pool

from jinja2 import Template
import pdfkit

class Timer:
    """Класс для отслеживания скорости выполнения кода.
    Attributes:
        message (str): сообщение, обозначающие начало отсчета.
        count_chars_after_point (int): кол-во знаков после запятой.
    """
    def __init__(self, message: str, count_chars_after_point: int):
        """Инициализация класса. Начало отсчета и вывод надписи.
        Args:
            message (str): сообщение, обозначающие начало отсчета.
            count_chars_after_point (int): кол-во знаков после запятой.
        """
        self.start_time = time.time()
        self.last_time = self.start_time
        self.chars_count = count_chars_after_point
        print(message)

    def write_time(self, message: str) -> None:
        """Метод для выведения текущего времени от начала отсчета.
        Args:
            message (str): сопутствующее сообщение.
        """
        new_time = time.time()
        current_time = round(new_time-self.start_time, self.chars_count)
        time_between = round(new_time-self.last_time, self.chars_count)
        self.last_time = new_time
        print(f"{message}: {current_time} (+{time_between})")

    def reload_start_time(self) -> None:
        """Метод для сбрасывания отсчета таймера."""
        self.start_time = time.time()
        print("Таймер был сброшен!")


class Error:
    """Класс вывода ошибки и завершения программы с сообщением.
    Attributes:
        error_type (str): Тип ошибки.
        message (str): Текст сообщения.
        is_fatal (bool): решает, зваершить ли программу или нет.
        timer (Timer): Таймер для отслежвания времени.
    """
    def __init__(self, error_type: str, message: str, is_fatal: bool, timer: Timer):
        """Инициализация вывода ошибки и/или завершения программы с сообщением.
        Args:
            error_type (str): Тип ошибки.
            message (str): Текст сообщения.
            is_fatal (bool): решает, зваершить ли программу или нет.
            timer (Timer): Таймер для отслежвания времени.
        """
        if is_fatal:
            print(">>>=================ERROR===================<<<")
        else:
            print(">>>================WARNING==================<<<")
        timer.write_time("ERROR_TIME")
        print(f"{error_type}: {message}")
        print(">>>=========================================<<<")
        if is_fatal:
            exit(0)


class InputCorrect:
    """Проверка существования и заполненности файла.
    Attributes:
        file (str): Название csv-файла с данными.
        prof (str): Название профессии.
        timer (Timer): Таймер для отслеживания времени.
    """
    def __init__(self, file: str, prof: str, timer: Timer):
        """Инициализация объекта InputCorrect. Проверка на существование и заполненность файла.
        Args:
            file (str): Название csv-файла с данными.
            prof (str): Название профессии.
            timer (Timer): Таймер для отслеживания времени.
        """
        self.file_name = file
        self.prof = prof
        self.timer = timer
        self.check_file()

    def check_file(self) -> None:
        """Проверка на существование и заполненность файла."""
        with open(self.file_name, "r", encoding='utf-8-sig') as csv_file:
            file_iter = iter(csv.reader(csv_file))
            if next(file_iter, "none") == "none":
                Error("VOID_CSV_FILE","Пустой файл", True, self.timer)
            if next(file_iter, "none") == "none":
                Error("ONLY_START_LINE", "Нет записей", True, self.timer)


class Currency_Values_Reader:
    """Класс для чтения csv-валют и формирования словря с валютами.
    Attributes:
        csv_dir (str): директория с csv-файлом.
        csv_name (str): имя самого csv-файла.
    """
    start_basic_row = ["Year", "Month", "CharCode", "InRuR"]

    def __init__(self, csv_dir: str, csv_name: str):
        """Инициализация. создание нового параллельного процесса, который .
        Args:
            csv_dir (str): директория с csv-файлом.
            csv_name (str): имя самого csv-файла.
        """
        self.currency_dict = self.count_currency_dict(csv_dir, csv_name)

    def add_if_key_not_exist(self, cur_value_dict: dict, key: any) -> dict:
        """Функция проверки наличия ключа в словаре, и если его нет, то добавить.
        Args:
            cur_value_dict (dict): словарь, в котором проверяем наличие ключа key.
            key (any): сам ключ.
        """
        try:
            test = cur_value_dict[key]
        except:
            cur_value_dict[key] = {}
        return cur_value_dict

    def count_currency_dict(self, csv_dir: str, csv_name: str) -> dict:
        """Функция для обработки csv-файла с данными по валютам.
        Args:
            csv_queue (Queue): очередь, в которую будут положены данные.
            full_csv_name (str): полный путь до файла.
        Returns:
            dict: словарь с нужными данными по валютам.
        """
        exit_cur_dict = {}
        with open(file=csv_dir+"/"+csv_name, mode="r", encoding="utf-8-sig") as csv_file:
            file = csv.reader(csv_file)
            start_line = next(file)
            for line in file:
                line_dict = dict(zip(start_line, line))
                exit_cur_dict = self.add_if_key_not_exist(exit_cur_dict, line_dict["Year"])
                exit_cur_dict[line_dict["Year"]] = \
                    self.add_if_key_not_exist(exit_cur_dict[line_dict["Year"]], line_dict["Month"])
                exit_cur_dict[line_dict["Year"]][line_dict["Month"]] = \
                    self.add_if_key_not_exist(exit_cur_dict[line_dict["Year"]][line_dict["Month"]], line_dict["CharCode"])
                exit_cur_dict[line_dict["Year"]][line_dict["Month"]][line_dict["CharCode"]] = float(line_dict["InRuR"])
        return exit_cur_dict


class CSV_Start:
    """Класс для формирования первичных данных файла и валют.
    Attributes:
        input_values (InputCorrect): информация о файле и профессии.
    """
    needed_fields = ["name", "salary_from", "salary_to", "salary_currency", "area_name", "published_at"]
    new_needed_fields = ["name", "salary", "area_name", "published_at"]

    def __init__(self, input_values: InputCorrect, values_reader: Currency_Values_Reader):
        """Инициализация класса CSV_Start. Вычисление индексов и стартовой строки.
        Args:
            input_values (InputCorrect): информация о файле и профессии.
        """
        self.input_values = input_values
        self.values_reader = values_reader
        with open(self.input_values.file_name, "r", encoding='utf-8-sig') as csv_file:
            file = csv.reader(csv_file)
            self.start_line = next(file)
            self.index_of = {}
            self.get_indexes()
            self.check_other_fields()
            self.start_line_len = len(self.start_line)
            self.all_currencies = {}
            for line in file:
                if len(line) == self.start_line_len:
                    self.all_currencies = \
                        CSV_Start.try_to_add(self.all_currencies, line[self.index_of["salary_currency"]], 1)
        csv_file.close()

    def get_indexes(self) -> None:
        """Получить индексы для нужных столбцов."""
        for field in CSV_Start.needed_fields:
            try:
                field_index = self.start_line.index(field)
                self.index_of[field] = field_index
            except:
                Error("MISSING_INDEX", "Can't find index of \"" + field + "\"", True, self.input_values.timer)

    def check_other_fields(self) -> None:
        """Проверить наличие других столбцов."""
        if len(self.index_of) != len(self.start_line):
            other_lines = [line for line in list(self.start_line) if line not in self.index_of.keys()]
            Error("ARGUMENT_WARNING", "There are additional fields in start_line: " + str(other_lines),
                  False, self.input_values.timer)

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

    def is_numeric_value(self, line: list, index: str) -> bool:
        """Проерка, можно ли кастовать значение по индексу index к типу float.
        Args:
            line (list): вакансия-строка.
            index (str): значение позиции.
        Returns:
            bool: молжно ли кастовать к числу.
        """
        sal_norm = True
        try:
            float(line[self.index_of[index]])
        except:
            sal_norm = False
        return sal_norm

    def is_valid_vac(self, line: list) -> bool:
        """Проверка списка на соответствие требованиям вакансии.
        Args:
            line (list): список значений для проверки.
        Returns:
            bool: подходит ли список под вакансию или нет.
        """
        is_normal_len = len(line) == self.start_line_len
        line_cur = line[self.index_of["salary_currency"]]
        is_valid_cur = self.all_currencies[line_cur] > 5000
        sal_from = self.is_numeric_value(line, "salary_from")
        sal_to = self.is_numeric_value(line, "salary_to")
        year = line[self.index_of["published_at"]][:4]
        month = str(int(line[self.index_of["published_at"]][5:7]))
        try:
            test = self.values_reader.currency_dict[year][month][line_cur]
        except:
            return False
        return is_normal_len and is_valid_cur and (sal_from or sal_to)


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
        self.is_needed = dic["is_needed"]

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
        values_reader (Currency_Values_Reader): Словарь информации по валютам.
    """
    def __init__(self, dic: dict, values_reader: Currency_Values_Reader):
        """Инициализация объекта Vacancy_Big. Приведение к более удобному виду.
        Args:
            dic (dict): Словарь информации про зарплату.
            values_reader (Currency_Values_Reader): Словарь информации по валютам.
        """
        self.dic = dic
        self.salary = self.get_salary(values_reader)
        self.is_needed = dic["is_needed"]

    def get_salary(self, values_reader: Currency_Values_Reader) -> float:
        """Получить зарплату по новой формуле (левый-правый край, зарплата того года)
        Args:
            values_reader (Currency_Values_Reader): словарь с валютами.
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
        year = self.dic["published_at"][:4]
        month = str(int(self.dic["published_at"][5:7]))
        char = self.dic["salary_currency"]
        return values_reader.currency_dict[year][month][char] * middle_salary

    def get_small(self) -> Vacancy_Small:
        """Получить уменьшенную версию вакансии.
        Returns:
            Vacancy_Small: уменьшенная версия вакансии.
        """
        new_dict = {
            "name": self.dic["name"],
            "salary": self.salary,
            "area_name": self.dic["area_name"],
            "published_at": self.dic["published_at"],
            "is_needed": self.is_needed
        }
        return Vacancy_Small(new_dict)


class Year_Proc_Read:
    """Класс для счета данных по годам.
    Attributes:
        csv_start (CSV_Start): Начальные данные (индексы и первая строка).
        csv_dir (str): расположение будущих мини-файлов-csv.
    """
    def __init__(self, csv_start: CSV_Start, csv_dir: str):
        """Инициализация класса Area_Proc_Read. Формирование словарей город к сред. зарплате,
        город к доле вакансий в нем.
        Args:
            csv_start (CSV_Start): Начальные данные (индексы и первая строка).
            csv_dir (str): расположение будущих мини-файлов-csv.
        """
        self.csv_start = csv_start
        self.csv_dir = csv_dir
        self.year_process, self.year_queue = self.create_year_proc()

    def read_one_csv_file(self, year_queue: mp.Queue, read_queue: mp.Queue) -> None:
        """Читает один csv-файл и делает данные о нём.
        Args:
            queue (mp.Queue): очередь для добавления данных.
            read_queue (mp.Queue): очередь из файлов для чтения.
        """
        while not read_queue.empty():
            file_name = read_queue.get()
            self.csv_start.input_values.timer\
                .write_time("YEAR_PROCESS >>> [" + mp.current_process().name + "] Начало обработки файла \"" + file_name + "\"")
            with open(f"{self.csv_dir}/{file_name}", "r", encoding='utf-8-sig', newline='') as csv_file:
                file = csv.reader(csv_file)
                filtered_vacs = []
                year = int(file_name.replace("file_", "").replace(".csv", ""))
                for line in file:
                    new_dict_line = dict(zip(CSV_Start.new_needed_fields, line))
                    new_dict_line["is_needed"] = (new_dict_line["name"]).find(self.csv_start.input_values.prof) > -1
                    vac = Vacancy_Small(new_dict_line)
                    filtered_vacs.append(vac)
                csv_file.close()
                all_count = len(filtered_vacs)
                all_sum = sum([vac.salary for vac in filtered_vacs])
                all_middle = math.floor(all_sum / all_count)
                needed_vacs = list(filter(lambda vacancy: vacancy.is_needed, filtered_vacs))
                needed_count = len(needed_vacs)
                needed_sum = sum([vac.salary for vac in needed_vacs])
                needed_middle = math.floor(needed_sum / needed_count)
            year_queue.put((year, all_count, all_middle, needed_count, needed_middle))
            self.csv_start.input_values.timer\
                .write_time("YEAR_PROCESS >>> [" + mp.current_process().name + "] Конец \"" + file_name + "\"")

    def save_file(self, current_year: str, lines: list) -> str:
        """Сохраняет CSV-файл с конкретными годами
        Args:
            current_year (str): Текущий год.
            lines (list): Список вакансий этого года.
        Returns:
            str: название нового csv-чанка.
        """
        file_name = f"file_{current_year}.csv"
        with open(f"{self.csv_dir}/{file_name}", "w", encoding='utf-8-sig', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(lines)
        return file_name

    def get_year(self, line: list) -> str:
        """Получить значение года из записи.
        Args:
            line (list): Запись.
        Returns:
            str: значение года в виде 4 символов.
        """
        return line[self.csv_start.index_of["published_at"]][:4]

    def get_new_line(self, line: list) -> list:
        """Получить новый список под новую, более простую вакансию.
        Args:
            line (list): стандартная строка:
        Return:
            list: укороченный лист.
        """
        new_dict = dict(zip(self.csv_start.start_line, line))
        new_dict["is_needed"] = None
        new_vac = Vacancy_Big(new_dict, self.csv_start.values_reader)
        return new_vac.get_small().get_list()

    def year_proc(self, year_queue: mp.Queue) -> None:
        """Функция процесса, которая читает большой csv-файл и делит его на маленькие + создает процессы,
        которые читают эти маленькие файлы.
        Args:
            year_queue (mp.Queue): очередь, в которую будут складываться данные из файлов.
        """
        procs = []
        read_queue = mp.Queue()
        with open(self.csv_start.input_values.file_name, "r", encoding='utf-8-sig') as csv_file:
            file = csv.reader(csv_file)
            next(file)
            next_line = next(file)
            current_year = self.get_year(next_line)
            data_years = []
            if self.csv_start.is_valid_vac(next_line):
                data_years.append(self.get_new_line(next_line))
            for line in file:
                if self.csv_start.is_valid_vac(line):
                    line_year = self.get_year(line)
                    if line_year != current_year:
                        new_csv = self.save_file(current_year, data_years)
                        self.csv_start.input_values.timer. \
                            write_time("YEAR >> Создан файл \"" + new_csv + "\"")
                        read_queue.put(new_csv)
                        proc = mp.Process(target=self.read_one_csv_file, args=(year_queue, read_queue))
                        proc.start()
                        procs.append(proc)
                        data_years = []
                        current_year = line_year
                    data_years.append(self.get_new_line(line))
            new_csv = self.save_file(current_year, data_years)
            self.csv_start.input_values.timer. \
                write_time("YEAR >> Создан файл \"" + new_csv + "\"")
            read_queue.put(new_csv)
            if len(mp.active_children()) <= 0:
                proc = mp.Process(target=self.read_one_csv_file, args=(year_queue, read_queue))
                proc.start()
                procs.append(proc)
        csv_file.close()
        self.csv_start.input_values.timer.write_time("YEAR >> Файл прочитан, ожидаем конца всех подпроцессов")
        for proc in procs:
            proc.join()

    @staticmethod
    def make_dir_if_needed(csv_dir: str) -> None:
        """Удаляет директорию вместе с файлами в ней, создает новую директорию.
        Args:
            csv_dir (str): название папки (директории).
        """
        if os.path.exists(csv_dir):
            shutil.rmtree(csv_dir)
        os.mkdir(csv_dir)

    def create_year_proc(self) -> (mp.Process, mp.Queue):
        """Создание процесса для вычислений данных по годам.
        Returns:
            (mp.Process, mp.Queue): Созданный процесс и очередь с данными.
        """
        Year_Proc_Read.make_dir_if_needed(self.csv_dir)
        year_queue = mp.Queue()
        year_process = mp.Process(target=self.year_proc, args=(year_queue,))
        year_process.start()
        return year_process, year_queue


class Area_Proc_Read:
    """Класс для формирования данных по городам.
    Attributes:
        csv_start (CSV_Start): Начальные данные (индексы и первая строка).
    """
    def __init__(self, csv_start: CSV_Start):
        """Инициализация класса Area_Proc_Read. Формирование словарей город к сред. зарплате, город к доле вакансий в нем.
        Args:
            csv_start (CSV_Start): Начальные данные (индексы и первая строка).
        """
        self.csv_start = csv_start
        self.area_to_middle_salary, self.area_to_piece = self.area_proc()

    @staticmethod
    def get_sorted_dict(key_to_salary: dict) -> dict:
        """Отсортировать словарь по значениям по убыванию и вернуть только 10 ключ-значений.

        Args:
            key_to_salary (dict): Неотсортированный словарь.

        Returns:
            dict: Отсортированный словарь, в котором только 10 ключ-значений.
        """
        return dict(list(sorted(key_to_salary.items(), key=lambda item: item[1], reverse=True))[:10])

    @staticmethod
    def get_middle_salary(key_to_count: dict, key_to_sum: dict) -> dict:
        """Получить словарь с средними зарплатами.
        Args:
            key_to_count (dict): Словарь ключ/кол-во повторений.
            key_to_sum (dict): Словарь ключ/сумма.
        Returns:
            dict: Словарь с теми же ключами, но значения по ключам - средняя зарплата.
        """
        key_to_salary = {}
        for key, val in key_to_count.items():
            if val == 0:
                key_to_salary[key] = 0
            else:
                key_to_salary[key] = math.floor(key_to_sum[key] / val)
        return key_to_salary

    @staticmethod
    def get_area_to_salary_and_piece(area_to_sum: dict, area_to_count: dict) -> (dict, dict):
        """Универсальная функция для высчитывания средней зарплаты и количества по ключам.
        Args:
            area_to_sum (dict): Словарь город/сумма зарплаты в нем.
            area_to_count (dict): Словарь город/кол-во вакансий в нем.
        Returns:
            tuple: Кортеж из двух словарей: город/средняя зарплата, город/доля вакансий.
        """
        vacs_count = sum(area_to_count.values())
        area_to_count = dict(filter(lambda item: item[1] / vacs_count > 0.01, area_to_count.items()))
        area_to_middle_salary = Area_Proc_Read.get_middle_salary(area_to_count, area_to_sum)
        area_to_piece = {key: round(val / vacs_count, 4) for key, val in area_to_count.items()}
        return area_to_middle_salary, area_to_piece

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

    def area_proc(self) -> (dict, dict):
        """Чтение большого csv-файла и формаирование данных по городам.
        Returns:
            (dict, dict): город к средней зарплате, город к доле вакансий в нем.
        """
        area_to_sum = {}
        area_to_count = {}
        with open(self.csv_start.input_values.file_name, "r", encoding='utf-8-sig') as csv_file:
            file = csv.reader(csv_file)
            next(file)
            for line in file:
                if self.csv_start.is_valid_vac(line):
                    new_dict_line = dict(zip(self.csv_start.start_line, line))
                    new_dict_line["is_needed"] = None
                    vac = Vacancy_Big(new_dict_line, self.csv_start.values_reader)
                    area_to_sum = Area_Proc_Read.try_to_add(area_to_sum, vac.dic["area_name"], vac.salary)
                    area_to_count = Area_Proc_Read.try_to_add(area_to_count, vac.dic["area_name"], 1)
        csv_file.close()
        area_to_middle_salary, area_to_piece = Area_Proc_Read.get_area_to_salary_and_piece(area_to_sum, area_to_count)
        area_to_middle_salary = Area_Proc_Read.get_sorted_dict(area_to_middle_salary)
        area_to_piece = Area_Proc_Read.get_sorted_dict(area_to_piece)
        return area_to_middle_salary, area_to_piece


class Image_Creator:
    """Класс для создания png-графиков.
    Attributes:
        image_name (str): название будущего png с графиками.
        year_reader (Year_Proc_Read): Данные для графиков по годам.
        area_reader (Area_Proc_Read): Данные для графиков по городам.
    """
    def __init__(self, image_name: str, year_reader: Year_Proc_Read, area_reader: Area_Proc_Read):
        """Инициализация класса Image_Creator. Подготовка данных и формирование png-файла.
        Args:
            image_name (str): название будущего png с графиками.
            year_reader (Year_Proc_Read): Данные для графиков по годам.
            area_reader (Area_Proc_Read): Данные для графиков по городам.
        """
        self.image_name = image_name
        self.image_path = os.getcwd() + "/" + image_name
        self.year_reader = year_reader
        self.area_reader = area_reader
        self.year_to_count = {}
        self.year_to_salary = {}
        self.year_to_count_needed = {}
        self.year_to_salary_needed = {}
        self.generate_image()

    def horizontal_bar(self, ax: Axes) -> None:
        """Функция создания горизонтальной диаграммы.
        Args:
            ax (Axes): Глобальная позиция графика (поле для рисования).
        """
        ax.set_title("Уровень зарплат по городам", fontsize=16)
        ax.grid(axis="x")
        keys = [key.replace(" ", "\n").replace("-", "-\n") for key in list(self.area_reader.area_to_middle_salary.keys())]
        ax.barh(keys, self.area_reader.area_to_middle_salary.values())
        ax.tick_params(axis='y', labelsize=6)
        ax.set_yticks(keys)
        ax.set_yticklabels(labels=keys,
                           verticalalignment="center", horizontalalignment="right")
        ax.invert_yaxis()

    def pie_diogramm(self, ax: Axes) -> None:
        """Функция создания круговой диаграммы.
        Args:
            ax (Axes): Глобальная позиция графика (поле для рисования).
        """
        ax.set_title("Доля вакансий по городам", fontsize=16)
        plt.rcParams['font.size'] = 8
        self.area_reader.area_to_piece["Другие"] = 1 - sum([val for val in self.area_reader.area_to_piece.values()])
        keys = list(self.area_reader.area_to_piece.keys())
        ax.pie(x=list(self.area_reader.area_to_piece.values()), labels=keys)
        ax.axis('equal')
        ax.tick_params(axis="both", labelsize=6)
        plt.rcParams['font.size'] = 16

    def count_area_data(self, axis) -> None:
        """Построить графики по городам.
        Args:
            axis (Axis): Площадка для постройки графиков.
        """
        self.horizontal_bar(axis[1, 0])
        self.pie_diogramm(axis[1, 1])

    def get_year_queue_data(self) -> (dict, dict, dict, dict):
        """Достать из очереди все данные и распределить их по словарям.
        Returns:
            (dict, dict, dict, dict): Год к кол-ву, год к зарплате, год к кол-ву нужных проф. год к зарплате нужных проф.
        """
        while not self.year_reader.year_queue.empty():
            data = self.year_reader.year_queue.get()
            self.year_to_count[data[0]] = data[1]
            self.year_to_salary[data[0]] = data[2]
            self.year_to_count_needed[data[0]] = data[3]
            self.year_to_salary_needed[data[0]] = data[4]

    @staticmethod
    def standart_bar(ax: Axes, keys1: list, keys2: list, values1: list,
                     values2: list, label1: str, label2: str, title: str) -> None:
        """Функция создания 2-х обычных столбчатых диаграмм на одном поле.
        Args:
            ax (Axes): Глобальная позиция графика (поле для рисования).
            keys1 (list): Значения по оси Х для первого графика.
            keys2 (list): Значения по оси Х для второго графика.
            values1 (list): Значения по оси У для первого графика.
            values2 (list): Значения по оси У для второго графика.
            label1 (str): Легенда первого графика.
            label2 (str): Легенда второго графика.
            title (str): Название поля.
        """
        x1 = [key - 0.2 for key in keys1]
        x2 = [key + 0.2 for key in keys2]
        ax.bar(x1, values1, width=0.4, label=label1)
        ax.bar(x2, values2, width=0.4, label=label2)
        ax.legend()
        ax.set_title(title, fontsize=16)
        ax.grid(axis="y")
        ax.tick_params(axis='x', labelrotation=90)

    @staticmethod
    def sort_dict_for_keys(dic: dict) -> dict:
        """Вернуть отсортированный по ключам словарь.
        Args:
            dic (dict): Неотсортированный словарь.
        Returns:
            dict: Отсортированный словарь.
        """
        return dict(sorted(dic.items(), key=lambda item: item[0]))

    def sort_year_dicts(self) -> None:
        """Сортировка полученных данных."""
        self.year_to_count = Image_Creator.sort_dict_for_keys(self.year_to_count)
        self.year_to_salary = Image_Creator.sort_dict_for_keys(self.year_to_salary)
        self.year_to_count_needed = Image_Creator.sort_dict_for_keys(self.year_to_count_needed)
        self.year_to_salary_needed = Image_Creator.sort_dict_for_keys(self.year_to_salary_needed)

    def count_year_data(self, axis) -> None:
        """Построить графики по годам.
        Args:
            axis (Axis): Площадка для постройки графиков.
        """
        self.area_reader.csv_start.input_values.timer\
            .write_time("MAIN > Графики по городам построены. Ожидаем конец обработки по годам")
        self.year_reader.year_process.join()
        self.get_year_queue_data()
        self.sort_year_dicts()
        self.standart_bar(axis[0, 0], self.year_to_salary.keys(), self.year_to_salary_needed.keys(),
                          self.year_to_salary.values(), self.year_to_salary_needed.values(),
                          "Средняя з/п", "з/п программист", "Уровень зарплат по годам")
        self.standart_bar(axis[0, 1], self.year_to_count.keys(), self.year_to_count_needed.keys(),
                          self.year_to_count.values(), self.year_to_count_needed.values(),
                          "Количество вакансий", "Количество вакансий программист", "Количество вакансий по годам")

    def generate_image(self) -> None:
        """Создать картинку в формате png для будущего pdf-отчета."""
        fig, axis = plt.subplots(2, 2)
        plt.rcParams['font.size'] = 8
        self.count_area_data(axis)
        self.count_year_data(axis)
        fig.set_size_inches(16, 9)
        fig.tight_layout(h_pad=2)
        fig.savefig(self.image_name)


class Report_PDF_MP:
    """Класс для создания pdf-файла.
    Attributes:
        pdf_name (str): название будущего pdf-отчета.
        image_creator (Image_Creator): Посчитанные данные для графиков.
    """
    def __init__(self, pdf_name: str, image_creator: Image_Creator):
        """Инициализация класса Report_PDF_MP. Структурирование данных для графиков и таблиц.
        Args:
            pdf_name (str): название будущего pdf-отчета.
            image_creator (Image_Creator): Посчитанные данные для графиков.
        """
        self.image_data = image_creator
        self.generate_pdf(pdf_name)

    @staticmethod
    def get_percents(value: (int or float)) -> str:
        """Получить проценты из значения.
        Args:
            value (int or float): число от 0 до 1.
        Returns:
            str: Проценты с 2-мя цифрами после запятой и знаком '%'.
        """
        return f"{round(value * 100, 2)}%"

    @staticmethod
    def get_table_rows(columns: list):
        """Транспанирование списка списков - первод столбцов в строки.
        Args:
            columns (list): Список столбцов.
        Returns:
            list: Список строк.
        """
        rows_list = [["" for _ in range(len(columns))] for _ in range(len(columns[0]))]
        for col in range(len(columns)):
            for cell in range(len(columns[col])):
                rows_list[cell][col] = columns[col][cell]
        return rows_list

    @staticmethod
    def get_table_data(image_data: Image_Creator) -> (list, list, list, list):
        """Метод для получения значений ячеек таблиц.
        Args:
            image_data (Image_Creator): данные, которые нужно преобразовать в надлежащий вид.
        Returns:
            (list, list, list, list): Заголовки первой таблицы, остальные строки первой таблицы. Заголовки второй таблицы, отсальные строки второй таблицы.
        """
        image_data.area_reader.area_to_piece.pop("Другие")
        sheet_1_headers = ["Год", "Средняя зарплата", "Средняя зарплата - Программист",
                                "Количество вакансий", "Количество вакансий - Программист"]
        sheet_1_columns = [list(image_data.year_to_salary.keys()), list(image_data.year_to_salary.values()),
                           list(image_data.year_to_salary_needed.values()), list(image_data.year_to_count.values()),
                           list(image_data.year_to_count_needed.values())]
        sheet_1_rows = Report_PDF_MP.get_table_rows(sheet_1_columns)
        sheet_2_headers = ["Город", "Уровень зарплат", " ", "Город", "Доля вакансий"]
        sheet_2_columns = [list(image_data.area_reader.area_to_middle_salary.keys()),
                           list(image_data.area_reader.area_to_middle_salary.values()),
                           ["" for _ in image_data.area_reader.area_to_middle_salary.keys()],
                           list(image_data.area_reader.area_to_piece.keys()),
                           list(map(Report_PDF_MP.get_percents, image_data.area_reader.area_to_piece.values()))]
        sheet_2_rows = Report_PDF_MP.get_table_rows(sheet_2_columns)
        return sheet_1_headers, sheet_1_rows, sheet_2_headers, sheet_2_rows

    def generate_pdf(self, file_name: str):
        """Сгенерировать pdf-файл из получившихся данных, png-графиков, и HTML-шаблона с названием html_template.html.
        Args:
            file_name (str): Название pdf-файла с графиками и таблицами.
        """
        sheet_1_headers, sheet_1_rows, sheet_2_headers, sheet_2_rows = Report_PDF_MP.get_table_data(self.image_data)
        html = open("html_template.html").read()
        template = Template(html)
        keys_to_values = {
            "prof_name": "Аналитика по зарплатам и городам для профессии "
                         + self.image_data.area_reader.csv_start.input_values.prof,
            "image_name": self.image_data.image_path,
            "year_head": "Статистика по годам",
            "city_head": "Статистика по городам",
            "years_headers": sheet_1_headers,
            "years_rows": sheet_1_rows,
            "cities_headers": sheet_2_headers,
            "count_columns": len(sheet_2_headers),
            "cities_rows": sheet_2_rows
        }
        pdf_template = template.render(keys_to_values)
        self.image_data.area_reader.csv_start.input_values.timer.write_time("MAIN > Вызываем wkhtmltopdf.exe")
        config = pdfkit.configuration(wkhtmltopdf=r"C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")
        pdfkit.from_string(pdf_template, file_name, configuration=config, options={"enable-local-file-access": True})


if __name__ == '__main__':
    timer = Timer("MAIN > Начало работы таймера", 3)
    input_values = InputCorrect(input("Введите название файла: "), input("Введите название профессии: "), timer)

    timer.write_time("MAIN > Ввод окончен")
    timer.reload_start_time()

    values_reader = Currency_Values_Reader("api_data", "currency_csv.csv")
    timer.write_time("MAIN > начало формирования словарей с данными валют")

    csv_start = CSV_Start(input_values, values_reader)
    timer.write_time("MAIN > Первичная обработка завершена (первая строка + индексы)")

    year_reader = Year_Proc_Read(csv_start, "csv")
    timer.write_time("MAIN > Процесс по годам стартовал")

    area_reader = Area_Proc_Read(csv_start)
    timer.write_time("MAIN > обработка по городам завершена")

    image_data = Image_Creator("graph_new_mp_2.png", year_reader, area_reader)
    timer.write_time("MAIN > Данные готовы. Собираем PDF-отчет")

    report = Report_PDF_MP("report_new_multi_api.pdf", image_data)
    timer.write_time("MAIN > Обработка завершена. Отчет готов")
