import csv, re, math
import datetime, time

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from jinja2 import Template
import pdfkit

import doctest


def do_exit(message):
    """Преднамеренное завершение программы с выводом сообщения в консоль.

    Args:
        message (str): Текст сообщения.
    """
    print(message)
    exit(0)


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
        self.dic["year"] = int(Vacancy.get_year_method_3(dic["published_at"]))
        self.is_needed = dic["is_needed"]

    #@staticmethod
    #def get_year_method_1(data: str):
    #    """Функция вычисления года через класс datetime.
    #
    #    Args:
    #        data (str): дата вакансии в виде строки из csv-файла.
    #
    #    Returns:
    #        str: Год - 4 цифры.
    #    """
    #    date = datetime.datetime.strptime(data, "%Y-%m-%dT%H:%M:%S%z")
    #    return date.year

    #@staticmethod
    #def get_year_method_2(data: str):
    #    """Функция вычисления года через метод split().
    #
    #    Args:
    #        data (str): дата вакансии в виде строки из csv-файла.
    #
    #    Returns:
    #        str: Год - 4 цифры.
    #    """
    #    return data.split("T")[0].split("-")[0]

    @staticmethod
    def get_year_method_3(data: str):
        """Функция вычисления года через индексы в строке.

        Args:
            data (str): дата вакансии в виде строки из csv-файла.

        Returns:
            str: Год - 4 цифры.
        """
        return data[:4]


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
        self.in_prof_name = prof
        self.check_file()

    def check_file(self):
        """Проверка на существование и заполненность файла."""
        with open(self.in_file_name, "r", encoding='utf-8-sig', newline='') as csv_file:
            file_iter = iter(csv.reader(csv_file))
            if next(file_iter, "none") == "none": do_exit("Пустой файл")
            if next(file_iter, "none") == "none": do_exit("Нет данных")


class DataSet:
    """Считывание файла и формирование удобной структуры данных.

    Attributes:
        file (str): Название csv-файла с данными.
        prof (str): Название профессии.
    """
    def __init__(self, file: str, prof: str):
        """Инициализация класса DataSet. Чтение. Фильтрация. Форматирование.

        Args:
            file (str): Название csv-файла с данными.
            prof (str): Название профессии.
        """
        self.input_values = InputCorrect(file, prof)
        self.csv_reader()
        self.csv_filter()
        self.get_years()
        self.count_graph_data()

    def csv_reader(self):
        """Чтение файла и первичная фильтрация (пропуск невалидных строк)."""
        with open(self.input_values.in_file_name, "r", encoding='utf-8-sig', newline='') as csv_file:
            file = csv.reader(csv_file)
            self.start_line = next(file)
            self.other_lines = [line for line in file
                                if not ("" in line) and len(line) == len(self.start_line)]

    def csv_filter(self):
        """Формирование списка всех вакансий и списка нужных вакансий."""
        self.filtered_vacancies = []
        for line in self.other_lines:
            new_dict_line = dict(zip(self.start_line, line))
            new_dict_line["is_needed"] = new_dict_line["name"].find(self.input_values.in_prof_name) > -1
            vac = Vacancy(new_dict_line)
            self.filtered_vacancies.append(vac)
        self.needed_vacancies = list(filter(lambda vac: vac.is_needed, self.filtered_vacancies))

    def get_years(self):
        """Отсортированный список всех уникальных лет, которые есть в файле."""
        self.all_years = list(set([vac.dic["year"] for vac in self.filtered_vacancies]))
        self.all_years.sort()

    @staticmethod
    def try_to_add(dic: dict, key, val) -> dict:
        """Попытка добавить в словарь значение по ключу или создать новый ключ, если его не было.

        Args:
            dic (dict): Словарь, в который добавляется ключ или значение по ключу.
            key: Ключ.
            val: Значение.

        Returns:
            dict: Изменный словарь.
        >>> DataSet.try_to_add({"a": 10}, "a", 5)
        {'a': 15}
        >>> DataSet.try_to_add({"a": 10}, "b", 5)
        {'a': 10, 'b': 5}
        >>> DataSet.try_to_add({"a": 10}, "a", -5)
        {'a': 5}
        >>> DataSet.try_to_add({}, "a", 5)
        {'a': 5}
        >>> DataSet.try_to_add({"a": 5, "b": 10}, "a", 20)
        {'a': 25, 'b': 10}
        >>> DataSet.try_to_add({"a": 5, "b": 10}, "b", 40)
        {'a': 5, 'b': 50}
        >>> DataSet.try_to_add({2022: 10, 2023: 0}, 2022, 5)
        {2022: 15, 2023: 0}
        >>> DataSet.try_to_add({2022: 0}, "a", 5)
        {2022: 0, 'a': 5}
        >>> DataSet.try_to_add({2022: 0, "a": 5}, 2022, 100)
        {2022: 100, 'a': 5}
        """
        try:
            dic[key] += val
        except:
            dic[key] = val
        return dic

    @staticmethod
    def get_middle_salary(key_to_count: dict, key_to_sum: dict) -> dict:
        """Получить словарь с средними зарплатами.

        Args:
            key_to_count (dict): Словарь ключ/кол-во повторений.
            key_to_sum (dict): Словарь ключ/сумма.

        Returns:
            dict: Словарь с теми же ключами, но значения по ключам - средняя зарплата.
        >>> DataSet.get_middle_salary({2022: 10}, {2022: 120})
        {2022: 12}
        >>> DataSet.get_middle_salary({2022: 10, 2023: 1}, {2022: 100, 2023: 10})
        {2022: 10, 2023: 10}
        >>> DataSet.get_middle_salary({"2022": 10, 2023: 2}, {"2022": 100, 2023: 10})
        {'2022': 10, 2023: 5}
        >>> DataSet.get_middle_salary({2022: 0}, {2022: 0})
        {2022: 0}
        >>> DataSet.get_middle_salary({2022: 0, 2023: 10}, {2022: 0, 2023: 1200})
        {2022: 0, 2023: 120}
        >>> DataSet.get_middle_salary({2022: 5}, {2022: -50})
        {2022: -10}
        """
        key_to_salary = {}
        for key, val in key_to_count.items():
            if val == 0:
                key_to_salary[key] = 0
            else:
                key_to_salary[key] = math.floor(key_to_sum[key] / val)
        return key_to_salary

    @staticmethod
    def update_keys(years: list, key_to_count: dict) -> dict:
        """Обновить словарь и добавить ключи (года) со значением 0, если их нет в словаре.

        Args:
            years (list): Список лет. Год - добавляемый в словарь ключ.
            key_to_count (dict): Словарь с возможно отсутствующими ключами.

        Returns:
            dict: Словарь с заполненными пропусками.
        >>> DataSet.update_keys([2022], {})
        {2022: 0}
        >>> DataSet.update_keys([2022], {2022: 10})
        {2022: 10}
        >>> DataSet.update_keys([2022, 2023], {2022: 10})
        {2022: 10, 2023: 0}
        >>> DataSet.update_keys([2022, 2023], {2022: 10, 2023: 20})
        {2022: 10, 2023: 20}
        >>> DataSet.update_keys([2022], {2022: 10, 2023: 20})
        {2022: 10, 2023: 20}
        >>> DataSet.update_keys([2022, 2023, 2024, 2025], {})
        {2022: 0, 2023: 0, 2024: 0, 2025: 0}
        """
        for key in years:
            if key not in key_to_count.keys():
                key_to_count[key] = 0
        return key_to_count

    @staticmethod
    def get_key_to_salary_and_count(years: list, vacs: list, key_str: str, is_area: bool) -> (dict, dict):
        """Универсальная функция для высчитывания средней зарплаты и количества по ключам.

        Args:
            years (list): Список лет. год - ключ для добавления в словарь.
            vacs (list): Список нужных вакансий.
            key_str (str): Ключ внутри словаря вакансии, по которому идет рассчет.
            is_area (bool): Если да, то отбрасывать маловакантные города.

        Returns:
            tuple: Кортеж из двух словарей: ключ/средняя зарплата, ключ/кол-во повторений.
        """
        key_to_sum = {}
        key_to_count = {}
        for vac in vacs:
            key_to_sum = DataSet.try_to_add(key_to_sum, vac.dic[key_str], vac.salary.salary_in_rur)
            key_to_count = DataSet.try_to_add(key_to_count, vac.dic[key_str], 1)
        if is_area:
            key_to_count = dict(filter(lambda item: item[1] / len(vacs) > 0.01, key_to_count.items()))
        else:
            key_to_sum = DataSet.update_keys(years, key_to_sum)
            key_to_count = DataSet.update_keys(years,key_to_count)
        key_to_middle_salary = DataSet.get_middle_salary(key_to_count, key_to_sum)
        return key_to_middle_salary, key_to_count

    @staticmethod
    def get_sorted_dict(key_to_salary: dict):
        """Отсортировать словарь по значениям по убыванию и вернуть только 10 ключ-значений.

        Args:
            key_to_salary (dict): Неотсортированный словарь.

        Returns:
            dict: Отсортированный словарь, в котором только 10 ключ-значений.
        >>> DataSet.get_sorted_dict({})
        {}
        >>> DataSet.get_sorted_dict({"Мск": 10})
        {'Мск': 10}
        >>> DataSet.get_sorted_dict({"Екб": 10, "Мск": 20})
        {'Мск': 20, 'Екб': 10}
        >>> DataSet.get_sorted_dict({"Екб": 20, "Мск": 20})
        {'Екб': 20, 'Мск': 20}
        >>> DataSet.get_sorted_dict({"a": 5, "b": 4, "c": 5})
        {'a': 5, 'c': 5, 'b': 4}
        >>> DataSet.get_sorted_dict({"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "h": 7, "t": 8, "k": 9, "o": 10, "l": 11})
        {'l': 11, 'o': 10, 'k': 9, 't': 8, 'h': 7, 'f': 6, 'e': 5, 'd': 4, 'c': 3, 'b': 2}
        >>> DataSet.get_sorted_dict({"a": 1, "b": 3, "c": 5, "d": 2, "e": 8, "f": 4, "h": 9, "t": 10, "k": 6, "o": 7, "l": 11})
        {'l': 11, 't': 10, 'h': 9, 'e': 8, 'o': 7, 'k': 6, 'c': 5, 'f': 4, 'b': 3, 'd': 2}
        """
        return dict(list(sorted(key_to_salary.items(), key=lambda item: item[1], reverse=True))[:10])

    def count_graph_data(self):
        """Считает данные для графиков и таблиц."""
        count_vacs = len(self.filtered_vacancies)
        self.year_to_salary, self.year_to_count = \
            self.get_key_to_salary_and_count(self.all_years, self.filtered_vacancies, "year", False)
        self.year_to_salary_needed, self.year_to_count_needed = \
            self.get_key_to_salary_and_count(self.all_years, self.needed_vacancies, "year", False)
        self.area_to_salary, self.area_to_count = \
            self.get_key_to_salary_and_count(self.all_years, self.filtered_vacancies, "area_name", True)
        self.area_to_salary = self.get_sorted_dict(self.area_to_salary)
        self.area_to_piece = {key: round(val / count_vacs, 4) for key, val in self.area_to_count.items()}
        self.area_to_piece = self.get_sorted_dict(self.area_to_piece)


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
        >>> Report.get_percents(0)
        '0%'
        >>> Report.get_percents(1)
        '100%'
        >>> Report.get_percents(0.5)
        '50.0%'
        >>> Report.get_percents(0.753)
        '75.3%'
        >>> Report.get_percents(0.7001)
        '70.01%'
        >>> Report.get_percents(0.70015)
        '70.02%'
        """
        return f"{round(value * 100, 2)}%"

    @staticmethod
    def get_table_rows(columns: list):
        """Транспанирование списка списков - первод столбцов в строки.

        Args:
            columns (list): Список столбцов.

        Returns:
            list: Список строк.
        >>> Report.get_table_rows([[1]])
        [[1]]
        >>> Report.get_table_rows([[1, 1], [2, 2]])
        [[1, 2], [1, 2]]
        >>> Report.get_table_rows([[1, 2, 3], [1, 2, 3], [1, 2, 3]])
        [[1, 1, 1], [2, 2, 2], [3, 3, 3]]
        >>> Report.get_table_rows([[1, 2, 3], [1, 2, 3], [1, 2, 10]])
        [[1, 1, 1], [2, 2, 2], [3, 3, 10]]
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
            "prof_name": self.data.input_values.in_prof_name,
            "image_name": image_name,
            "years_headers": self.sheet_1_headers,
            "years_rows": self.sheet_1_rows,
            "cities_headers": self.sheet_2_headers,
            "count_columns": len(self.sheet_2_headers),
            "cities_rows": self.sheet_2_rows
        }
        pdf_template = template.render(keys_to_values)
        config = pdfkit.configuration(wkhtmltopdf=r"C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")
        pdfkit.from_string(pdf_template, file_name, configuration=config, options={"enable-local-file-access": True})


def create_pdf():
    """Функция создания pdf-файла-отчета."""
    file_name = input("Введите название файла: ")
    prof = input("Введите название профессии: ")
    start_time = time.time()
    print("start!")
    report_data = Report(DataSet(file_name, prof))
    print("data done: " + str(time.time() - start_time))
    report_data.generate_pdf("report.pdf")
    print("pdf done: " + str(time.time() - start_time))


if __name__ == '__main__':
    #doctest.testmod()
    create_pdf()
