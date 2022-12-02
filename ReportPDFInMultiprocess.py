import time

import csv, re, math, os
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import multiprocessing as mp

from jinja2 import Template
import pdfkit


def do_exit(message):
    """Преднамеренное завершение программы с выводом сообщения в консоль.

    Args:
        message (str): Текст сообщения.
    """
    print(message)
    exit(0)


class InputCorrect:
    """Проверка существования и заполненности файла.

    Attributes:
        file (str): Название csv-файла с данными.
        prof (str): Название профессии.
    """
    def __init__(self, file: str, prof: str):
        """Инициализация объекта InputCorrect. Проверка на существование и заполненность файла.

        Args:
            file (str): Название csv-файла с данными.
            prof (str): Название профессии.
        """
        self.in_file_name = file
        self.prof = prof
        self.check_file()

    def check_file(self):
        """Проверка на существование и заполненность файла."""
        with open(self.in_file_name, "r", encoding='utf-8-sig', newline='') as csv_file:
            file_iter = iter(csv.reader(csv_file))
            if next(file_iter, "none") == "none": do_exit("Пустой файл")
            if next(file_iter, "none") == "none": do_exit("Нет данных")


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


class DataSet:
    """Считывание файла и формирование удобной структуры данных.

    Attributes:
        csv_dir (str): папка расположения всех csv-файлов.
        prof (str): Название профессии.
        file_name (str): Название большого файла с данными.
    """
    def __init__(self, csv_dir: str, prof: str, file_name: str):
        """Инициализация класса DataSet. Чтение. Фильтрация. Форматирование.

        Args:
            csv_dir (str): папка расположения всех csv-файлов.
            prof (str): Название профессии.
            file_name (str): Название большого файла с данными.
        """
        self.csv_dir = csv_dir
        self.prof = prof

        self.start_line = []
        self.year_to_count = {}
        self.year_to_salary = {}
        self.year_to_count_needed = {}
        self.year_to_salary_needed = {}
        self.area_to_salary = {}
        self.area_to_piece = {}

        area_to_sum, area_to_count = self.csv_divide(file_name)

        self.count_area_data(area_to_sum, area_to_count)
        self.sort_year_dicts()

    def csv_reader(self, read_queue: mp.Queue):
        """Чтение данных и складывание их результатов воедино.
        Args:
            read_queue (Queue): очередь из данных.
        """
        while not read_queue.empty():
            data = read_queue.get()
            self.year_to_count[data[0]] = data[1]
            self.year_to_salary[data[0]] = data[2]
            self.year_to_count_needed[data[0]] = data[3]
            self.year_to_salary_needed[data[0]] = data[4]

    def save_file(self, current_year: str, lines: list):
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

    def read_one_csv_file(self, queue: mp.Queue, file_name: str):
        """Читает один csv-файл и делает данные о нём.
        Args:
            queue (Queue): очередь для добавления данных.
            file_name (str): файл, из которого идет чтение.
        """
        print("start: "+file_name)
        with open(f"{self.csv_dir}/{file_name}", "r", encoding='utf-8-sig', newline='') as csv_file:
            file = csv.reader(csv_file)
            filtered_vacs = []
            year = int(file_name.replace("file_", "").replace(".csv", ""))
            for line in file:
                new_dict_line = dict(zip(self.start_line, line))
                new_dict_line["is_needed"] = (new_dict_line["name"]).find(self.prof) > -1
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
            queue.put((year, all_count, all_middle, needed_count, needed_middle))
        print("stop: " + file_name)

    def csv_divide(self, file_name: str):
        """Разделяет данные на csv-файлы по годам
        Args:
            file_name (str): название большого файла с данными.
        Returns:
            (dict, dict): словарь город/вся зарплата, словарь город/кол-во вакансий.
        """
        read_queue = mp.Queue()
        area_to_sum = {}
        area_to_count = {}
        procs = []
        with open(file_name, "r", encoding='utf-8-sig', newline='') as csv_file:
            file = csv.reader(csv_file)
            self.start_line = next(file)
            year_index = self.start_line.index("published_at")
            next_line = next(file)
            current_year = int(next_line[year_index][:4])
            data_years = [next_line]
            for line in file:
                if not ("" in line) and len(line) == len(self.start_line):
                    new_dict_line = dict(zip(self.start_line, line))
                    new_dict_line["is_needed"] = None
                    vac = Vacancy(new_dict_line)
                    area_to_sum = DataSet.try_to_add(area_to_sum, vac.dic["area_name"], vac.salary.salary_in_rur)
                    area_to_count = DataSet.try_to_add(area_to_count, vac.dic["area_name"], 1)
                    if vac.dic["year"] != current_year:
                        new_csv = self.save_file(current_year, data_years)
                        data_years = []
                        print("save " + str(current_year))
                        proc = mp.Process(target=self.read_one_csv_file, args=(read_queue, new_csv))
                        proc.start()
                        procs.append(proc)
                        current_year = vac.dic["year"]
                    data_years.append(line)
            new_csv = self.save_file(str(current_year), data_years)
            proc = mp.Process(target=self.read_one_csv_file, args=(read_queue, new_csv))
            procs.append(proc)
            proc.start()
            csv_file.close()
            for proc in procs:
                proc.join()
            self.csv_reader(read_queue)
            return area_to_sum, area_to_count

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
        self.year_to_count = DataSet.sort_dict_for_keys(self.year_to_count)
        self.year_to_salary = DataSet.sort_dict_for_keys(self.year_to_salary)
        self.year_to_count_needed = DataSet.sort_dict_for_keys(self.year_to_count_needed)
        self.year_to_salary_needed = DataSet.sort_dict_for_keys(self.year_to_salary_needed)
        self.area_to_piece = DataSet.get_sorted_dict(self.area_to_piece)
        self.area_to_salary = DataSet.get_sorted_dict(self.area_to_salary)

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
        area_to_middle_salary = DataSet.get_middle_salary(area_to_count, area_to_sum)
        area_to_piece = {key: round(val / vacs_count, 4) for key, val in area_to_count.items()}
        return area_to_middle_salary, area_to_piece

    def count_area_data(self, area_to_sum: dict, area_to_count: dict):
        """Считает дополнительные данные для графиков и таблиц. (города)
        Args:
            area_to_sum (dict): словарь город/суммарная зарплата.
            area_to_count (dict): словарь город/кол-во вакансий в нем.
        """
        self.area_to_salary, self.area_to_piece = \
            DataSet.get_area_to_salary_and_piece(area_to_sum, area_to_count)


class Report:
    """Класс для создания png-графиков и pdf-файла.

    Attributes:
        data (DataSet): Посчитанные данные для графиков.
    """
    def __init__(self, data: DataSet):
        """Инициализация класса Report. Структурирование данных для графиков и таблиц.

        Args:
            data (DataSet): Посчитанные данные для графиков.
        """
        self.data = data
        self.sheet_1_headers = ["Год", "Средняя зарплата", "Средняя зарплата - Программист",
                                "Количество вакансий", "Количество вакансий - Программист"]
        sheet_1_columns = [list(data.year_to_salary.keys()), list(data.year_to_salary.values()),
                           list(data.year_to_salary_needed.values()), list(data.year_to_count.values()),
                           list(data.year_to_count_needed.values())]
        self.sheet_1_rows = self.get_table_rows(sheet_1_columns)
        self.sheet_2_headers = ["Город", "Уровень зарплат", " ", "Город", "Доля вакансий"]
        sheet_2_columns = [list(data.area_to_salary.keys()), list(data.area_to_salary.values()),
                           ["" for _ in data.area_to_salary.keys()], list(data.area_to_piece.keys()),
                           list(map(self.get_percents, data.area_to_piece.values()))]
        self.sheet_2_rows = self.get_table_rows(sheet_2_columns)

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

    def standart_bar(self, ax: Axes, keys1, keys2, values1, values2, label1, label2, title):
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

    def horizontal_bar(self, ax: Axes):
        """Функция создания горизонтальной диаграммы.
        Args:
            ax (Axes): Глобальная позиция графика (поле для рисования).
        """
        ax.set_title("Уровень зарплат по городам", fontsize=16)
        ax.grid(axis="x")
        keys = [key.replace(" ", "\n").replace("-", "-\n") for key in list(self.data.area_to_salary.keys())]
        ax.barh(keys, self.data.area_to_salary.values())
        ax.tick_params(axis='y', labelsize=6)
        ax.set_yticks(keys)
        ax.set_yticklabels(labels=keys,
                           verticalalignment="center", horizontalalignment="right")
        ax.invert_yaxis()

    def pie_diogramm(self, ax: Axes, plt):
        """Функция создания круговой диаграммы.

        Args:
            ax (Axes): Глобальная позиция графика (поле для рисования).
            plt (Plot): Общее поле для рисования всех графиков.
        """
        ax.set_title("Доля вакансий по городам", fontsize=16)
        plt.rcParams['font.size'] = 8
        dic = self.data.area_to_piece
        dic["Другие"] = 1 - sum([val for val in dic.values()])
        keys = list(dic.keys())
        ax.pie(x=list(dic.values()), labels=keys)
        ax.axis('equal')
        ax.tick_params(axis="both", labelsize=6)
        plt.rcParams['font.size'] = 16

    def generate_image(self, file_name: str):
        """Функция создания png-файла с графиками.

        Args:
            file_name (str): название получившегося файла.
        """
        fig, axis = plt.subplots(2, 2)
        plt.rcParams['font.size'] = 8
        self.standart_bar(axis[0, 0], self.data.year_to_salary.keys(), self.data.year_to_salary_needed.keys(),
                          self.data.year_to_salary.values(), self.data.year_to_salary_needed.values(),
                          "Средняя з/п", "з/п программист", "Уровень зарплат по годам")
        self.standart_bar(axis[0, 1], self.data.year_to_count.keys(), self.data.year_to_count_needed.keys(),
                          self.data.year_to_count.values(), self.data.year_to_count_needed.values(),
                          "Количество вакансий", "Количество вакансий программист", "Количество вакансий по годам")
        self.horizontal_bar(axis[1, 0])
        self.pie_diogramm(axis[1, 1], plt)
        fig.set_size_inches(16, 9)
        fig.tight_layout(h_pad=2)
        fig.savefig(file_name)

    def generate_pdf(self, file_name: str):
        """Сгенерировать pdf-файл из получившихся данных, png-графиков, и HTML-шаблона с названием html_template.html.

        Args:
            file_name (str): Название pdf-файла с графиками и таблицами.
        """
        image_name = "graph.png"
        self.generate_image(image_name)
        html = open("html_template.html").read()
        template = Template(html)
        keys_to_values = {
            "prof_name": "Аналитика по зарплатам и городам для профессии " + self.data.prof,
            "image_name": "C:/Users/Shira/PycharmProjects/pythonProject_4/pythonProject_6_3/" + image_name,
            "year_head": "Статистика по годам",
            "city_head": "Статистика по городам",
            "years_headers": self.sheet_1_headers,
            "years_rows": self.sheet_1_rows,
            "cities_headers": self.sheet_2_headers,
            "count_columns": len(self.sheet_2_headers),
            "cities_rows": self.sheet_2_rows
        }
        pdf_template = template.render(keys_to_values)
        config = pdfkit.configuration(wkhtmltopdf=r"C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")
        pdfkit.from_string(pdf_template, file_name, configuration=config, options={"enable-local-file-access": True})


def create_pdf(csv_dir: str, file_name: str):
    file_csv_name = input("Введите название файла: ")
    prof = input("Введите название профессии: ")
    start_time = time.time()
    if os.path.exists(csv_dir):
        import shutil
        shutil.rmtree(csv_dir)
    os.mkdir(csv_dir)
    print("start!")
    data_set = DataSet(csv_dir, prof, file_csv_name)
    print("read_data: " + str(time.time() - start_time))
    report = Report(data_set)
    print("report_init: " + str(time.time() - start_time))
    report.generate_pdf(file_name)
    print("pdf done: " + str(time.time() - start_time))


if __name__ == '__main__':
    create_pdf("csv", "report_multi.pdf")
