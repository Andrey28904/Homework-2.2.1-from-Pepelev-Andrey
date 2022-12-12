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
        count_chars_after_point (str): кол-во знаков после запятой.
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


class CSV_Start:
    needed_fields = ["name", "salary_from", "salary_to", "salary_currency", "area_name", "published_at"]

    def __init__(self, input_values: InputCorrect):
        self.input_values = input_values
        with open(self.input_values.file_name, "r", encoding='utf-8-sig') as csv_file:
            file = csv.reader(csv_file)
            self.start_line = next(file)
            self.index_of = {}
            self.get_indexes()
            self.check_other_fields()
        csv_file.close()

    def get_indexes(self) -> None:
        for field in CSV_Start.needed_fields:
            try:
                field_index = self.start_line.index(field)
                self.index_of[field] = field_index
            except:
                Error("MISSING_INDEX", "Can't find index of \"" + field + "\"", True, self.input_values.timer)

    def check_other_fields(self) -> None:
        if len(self.index_of) != len(self.start_line):
            other_lines = [line for line in list(self.start_line) if line not in self.index_of.keys()]
            Error("ARGUMENT_WARNING", "There are additional fields in start_line: " + str(other_lines),
                  False, self.input_values.timer)


currency_to_rub = {
    "AZN": 35.68, "BYR": 23.91, "EUR": 59.90, "GEL": 21.74,
    "KGS": 0.76, "KZT": 0.13, "RUR": 1, "UAH": 1.64,
    "USD": 60.66, "UZS": 0.0055,
}


class Salary:
    """Информация о зарплате вакансии.

    Attributes:
        dic (dict): Словарь информации о зарплате.
    """
    def __init__(self, dic):
        """Инициализация объекта Salary. Перевод зарплаты в рубли (для последущего сравнения).

        Args:
            dic (dict): Словарь информации про зарплату.
        """
        self.salary_from = math.floor(float(dic["salary_from"]))
        self.salary_to = math.floor(float(dic["salary_to"]))
        self.salary_currency = dic["salary_currency"]
        middle_salary = (self.salary_to + self.salary_from) / 2
        self.salary_in_rur = currency_to_rub[self.salary_currency] * middle_salary


class Vacancy:
    """Информация о вакансии.

    Attributes:
        dic (dict): Словарь информации о зарплате.
    """
    def __init__(self, dic: dict):
        """Инициализация объекта Vacancy. Приведение к более удобному виду.

        Args:
            dic (dict): Словарь информации про зарплату.
        """
        self.dic = dic
        self.salary = Salary(dic)
        self.dic["year"] = int(dic["published_at"][:4])
        self.is_needed = dic["is_needed"]


class Year_Proc_Read:
    def __init__(self, csv_start: CSV_Start, csv_dir: str):
        self.csv_start = csv_start
        self.csv_dir = csv_dir
        self.year_process, self.year_queue = self.create_year_proc()

    def read_one_csv_file(self, year_queue: mp.Queue, file_name: str) -> None:
        """Читает один csv-файл и делает данные о нём.
        Args:
            queue (Queue): очередь для добавления данных.
            file_name (str): файл, из которого идет чтение.
        """
        with open(f"{self.csv_dir}/{file_name}", "r", encoding='utf-8-sig', newline='') as csv_file:
            file = csv.reader(csv_file)
            filtered_vacs = []
            year = int(file_name.replace("file_", "").replace(".csv", ""))
            for line in file:
                new_dict_line = dict(zip(self.csv_start.start_line, line))
                new_dict_line["is_needed"] = (new_dict_line["name"]).find(self.csv_start.input_values.prof) > -1
                vac = Vacancy(new_dict_line)
                filtered_vacs.append(vac)
            csv_file.close()
            all_count = len(filtered_vacs)
            all_sum = sum([vac.salary.salary_in_rur for vac in filtered_vacs])
            all_middle = math.floor(all_sum / all_count)
            needed_vacs = list(filter(lambda vacancy: vacancy.is_needed, filtered_vacs))
            needed_count = len(needed_vacs)
            needed_sum = sum([vac.salary.salary_in_rur for vac in needed_vacs])
            needed_middle = math.floor(needed_sum / needed_count)
        year_queue.put((year, all_count, all_middle, needed_count, needed_middle))

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
        return line[self.csv_start.index_of["published_at"]][:4]

    def year_proc(self, year_queue: mp.Queue) -> None:
        start_line_len = len(self.csv_start.start_line)
        procs = []
        with open(self.csv_start.input_values.file_name, "r", encoding='utf-8-sig') as csv_file:
            file = csv.reader(csv_file)
            next(file)
            next_line = next(file)
            current_year = self.get_year(next_line)
            data_years = [next_line]
            for line in file:
                if len(line) == start_line_len and "" not in line:
                    line_year = self.get_year(line)
                    if line_year != current_year:
                        new_csv = self.save_file(current_year, data_years)
                        proc = mp.Process(target=self.read_one_csv_file, args=(year_queue, new_csv))
                        proc.start()
                        procs.append(proc)
                        data_years = []
                        current_year = line_year
                    data_years.append(line)
            new_csv = self.save_file(current_year, data_years)
            proc = mp.Process(target=self.read_one_csv_file, args=(year_queue, new_csv))
            proc.start()
            procs.append(proc)
        csv_file.close()

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
        Year_Proc_Read.make_dir_if_needed(self.csv_dir)
        year_queue = mp.Queue()
        year_process = mp.Process(target=self.year_proc, args=(year_queue, ))
        year_process.start()
        return year_process, year_queue


class Area_Proc_Read:
    def __init__(self, csv_start: CSV_Start):
        self.csv_start = csv_start
        self.area_process, self.area_queue = self.create_area_proc()

    @staticmethod
    def get_sorted_dict(key_to_salary: dict):
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

    def area_proc(self, area_queue: mp.Queue) -> None:
        start_line_len = len(self.csv_start.start_line)
        area_to_sum = {}
        area_to_count = {}
        with open(self.csv_start.input_values.file_name, "r", encoding='utf-8-sig') as csv_file:
            file = csv.reader(csv_file)
            next(file)
            for line in file:
                if len(line) == start_line_len and "" not in line:
                    new_dict_line = dict(zip(self.csv_start.start_line, line))
                    new_dict_line["is_needed"] = None
                    vac = Vacancy(new_dict_line)
                    area_to_sum = Area_Proc_Read.try_to_add(area_to_sum, vac.dic["area_name"], vac.salary.salary_in_rur)
                    area_to_count = Area_Proc_Read.try_to_add(area_to_count, vac.dic["area_name"], 1)
        csv_file.close()
        area_to_middle_salary, area_to_piece = Area_Proc_Read.get_area_to_salary_and_piece(area_to_sum, area_to_count)
        area_to_middle_salary = Area_Proc_Read.get_sorted_dict(area_to_middle_salary)
        area_to_piece = Area_Proc_Read.get_sorted_dict(area_to_piece)
        area_queue.put([area_to_middle_salary, area_to_piece])

    def create_area_proc(self) -> (mp.Process, mp.Queue):
        area_queue = mp.Queue()
        area_process = mp.Process(target=self.area_proc, args=(area_queue,))
        area_process.start()
        return area_process, area_queue


class Image_Creator:
    def __init__(self, image_name: str, year_reader: Year_Proc_Read, area_reader: Area_Proc_Read):
        self.image_name = image_name
        self.image_path = os.getcwd() + "/" + image_name
        self.year_reader = year_reader
        self.area_reader = area_reader
        self.year_to_count = {}
        self.year_to_salary = {}
        self.year_to_count_needed = {}
        self.year_to_salary_needed = {}
        self.area_to_piece = {}
        self.area_to_salary = {}
        self.generate_image()

    def horizontal_bar(self, ax: Axes):
        """Функция создания горизонтальной диаграммы.
        Args:
            ax (Axes): Глобальная позиция графика (поле для рисования).
        """
        ax.set_title("Уровень зарплат по городам", fontsize=16)
        ax.grid(axis="x")
        keys = [key.replace(" ", "\n").replace("-", "-\n") for key in list(self.area_to_salary.keys())]
        ax.barh(keys, self.area_to_salary.values())
        ax.tick_params(axis='y', labelsize=6)
        ax.set_yticks(keys)
        ax.set_yticklabels(labels=keys,
                           verticalalignment="center", horizontalalignment="right")
        ax.invert_yaxis()

    def pie_diogramm(self, ax: Axes):
        """Функция создания круговой диаграммы.

        Args:
            ax (Axes): Глобальная позиция графика (поле для рисования).
        """
        ax.set_title("Доля вакансий по городам", fontsize=16)
        plt.rcParams['font.size'] = 8
        self.area_to_piece["Другие"] = 1 - sum([val for val in self.area_to_piece.values()])
        keys = list(self.area_to_piece.keys())
        ax.pie(x=list(self.area_to_piece.values()), labels=keys)
        ax.axis('equal')
        ax.tick_params(axis="both", labelsize=6)
        plt.rcParams['font.size'] = 16

    def count_area_data(self, area_reader: Area_Proc_Read, axis):
        area_reader.area_process.join()
        queue_data = area_reader.area_queue.get()
        self.area_to_salary = queue_data[0]
        self.area_to_piece = queue_data[1]
        self.horizontal_bar(axis[1, 0])
        self.pie_diogramm(axis[1, 1])

    def get_year_queue_data(self, ) -> (dict, dict, dict, dict):
        while not self.year_reader.year_queue.empty():
            data = self.year_reader.year_queue.get()
            self.year_to_count[data[0]] = data[1]
            self.year_to_salary[data[0]] = data[2]
            self.year_to_count_needed[data[0]] = data[3]
            self.year_to_salary_needed[data[0]] = data[4]

    @staticmethod
    def standart_bar(ax: Axes, keys1: list, keys2: list, values1: list,
                     values2: list, label1: str, label2: str, title: str):
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

    def sort_year_dicts(self):
        """Сортировка полученных данных"""
        self.year_to_count = Image_Creator.sort_dict_for_keys(self.year_to_count)
        self.year_to_salary = Image_Creator.sort_dict_for_keys(self.year_to_salary)
        self.year_to_count_needed = Image_Creator.sort_dict_for_keys(self.year_to_count_needed)
        self.year_to_salary_needed = Image_Creator.sort_dict_for_keys(self.year_to_salary_needed)

    def count_year_data(self, year_reader: Year_Proc_Read, axis):
        year_reader.year_process.join()
        queue_data = year_reader.year_queue
        self.get_year_queue_data()
        self.sort_year_dicts()
        self.standart_bar(axis[0, 0], self.year_to_salary.keys(), self.year_to_salary_needed.keys(),
                          self.year_to_salary.values(), self.year_to_salary_needed.values(),
                          "Средняя з/п", "з/п программист", "Уровень зарплат по годам")
        self.standart_bar(axis[0, 1], self.year_to_count.keys(), self.year_to_count_needed.keys(),
                          self.year_to_count.values(), self.year_to_count_needed.values(),
                          "Количество вакансий", "Количество вакансий программист", "Количество вакансий по годам")

    def generate_image(self):
        fig, axis = plt.subplots(2, 2)
        plt.rcParams['font.size'] = 8
        self.count_area_data(self.area_reader, axis)
        self.count_year_data(self.year_reader, axis)
        fig.set_size_inches(16, 9)
        fig.tight_layout(h_pad=2)
        fig.savefig(self.image_name)


class Report_PDF_MP:
    """Класс для создания png-графиков и pdf-файла.

    Attributes:
        data (DataSet): Посчитанные данные для графиков.
    """
    def __init__(self, pdf_name: str, image_creator: Image_Creator):
        """Инициализация класса Report. Структурирование данных для графиков и таблиц.

        Args:
            data (DataSet): Посчитанные данные для графиков.
        """
        self.image_data = image_creator
        self.generate_pdf(pdf_name)

    @staticmethod
    def get_percents(value):
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
    def get_table_data(image_data: Image_Creator):
        image_data.area_to_piece.pop("Другие")
        sheet_1_headers = ["Год", "Средняя зарплата", "Средняя зарплата - Программист",
                                "Количество вакансий", "Количество вакансий - Программист"]
        sheet_1_columns = [list(image_data.year_to_salary.keys()), list(image_data.year_to_salary.values()),
                           list(image_data.year_to_salary_needed.values()), list(image_data.year_to_count.values()),
                           list(image_data.year_to_count_needed.values())]
        sheet_1_rows = Report_PDF_MP.get_table_rows(sheet_1_columns)
        sheet_2_headers = ["Город", "Уровень зарплат", " ", "Город", "Доля вакансий"]
        sheet_2_columns = [list(image_data.area_to_salary.keys()), list(image_data.area_to_salary.values()),
                           ["" for _ in image_data.area_to_salary.keys()], list(image_data.area_to_piece.keys()),
                           list(map(Report_PDF_MP.get_percents, image_data.area_to_piece.values()))]
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
        config = pdfkit.configuration(wkhtmltopdf=r"C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")
        pdfkit.from_string(pdf_template, file_name, configuration=config, options={"enable-local-file-access": True})


if __name__ == '__main__':
    timer = Timer("Начало работы таймера", 3)
    input_values = InputCorrect(input("Введите название файла: "), input("Введите название профессии: "), timer)
    timer.reload_start_time()
    csv_start = CSV_Start(input_values)
    year_reader = Year_Proc_Read(csv_start, "csv")
    area_reader = Area_Proc_Read(csv_start)
    image_data = Image_Creator("graph_new_mp.png", year_reader, area_reader)
    report = Report_PDF_MP("report_new_multi.pdf", image_data)
    timer.write_time("Конец чтения файла.")
