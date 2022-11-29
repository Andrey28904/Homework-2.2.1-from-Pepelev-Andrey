import csv, re, prettytable
from math import floor
from prettytable import PrettyTable

import doctest

if __name__ == '__main__':
    doctest.testmod()


def do_exit(message):
    """Преднамеренное завершение программы с выводом сообщения в консоль.

    Args:
        message (str): Текст сообщения.
    """
    print(message)
    exit(0)


class All_Used_Dicts():
    """Класс для всех используемых в задаче словарей.\n

    transformate (dict): Перевод с тегов на русский язык.\n
    exp_to_int (dict): Словарь для сортировки по опыту работы.\n
    filters (dict): Перевод фильтрующего слова в тег зарплаты.\n
    header_to_ru (dict): Перевод тега зарплаты в русское название столбца.\n
    currency_to_rub (dict): Конвертация любой валюты в рубли.\n
    filter_key_to_function (dict): Тег зарплаты к фильтрующей функции.\n
    sort_key_to_function (dict): Русское слово к сортирующей функции.
    """
    transformate = {
        "AZN": "Манаты", "BYR": "Белорусские рубли", "EUR": "Евро",
        "GEL": "Грузинский лари", "KGS": "Киргизский сом", "KZT": "Тенге",
        "RUR": "Рубли", "UAH": "Гривны", "USD": "Доллары",
        "UZS": "Узбекский сум", "False": "Нет", "True": "Да",
        "FALSE": "Нет", "noExperience": "Нет опыта",
        "between1And3": "От 1 года до 3 лет",
        "between3And6": "От 3 до 6 лет", "moreThan6": "Более 6 лет"
    }
    exp_to_int = {
        "Нет опыта": 1, "От 1 года до 3 лет": 2,
        "От 3 до 6 лет": 3, "Более 6 лет": 4
    }
    filters = {
        "Навыки": "key_skills", "Оклад": "salary", "Дата публикации вакансии": "published_at",
        "Опыт работы": "experience_id", "Премиум-вакансия": "premium",
        "Идентификатор валюты оклада": "salary_currency", "Название": "name",
        "Название региона": "area_name", "Компания": "employer_name"
    }
    header_to_ru = {
        "№": "№", "name": "Название", "description": "Описание",
        "key_skills": "Навыки", "experience_id": "Опыт работы",
        "premium": "Премиум-вакансия", "employer_name": "Компания", "salary": "Оклад",
        "area_name": "Название региона", "published_at": "Дата публикации вакансии"
    }
    currency_to_rub = {
        "AZN": 35.68, "BYR": 23.91, "EUR": 59.90, "GEL": 21.74,
        "KGS": 0.76, "KZT": 0.13, "RUR": 1, "UAH": 1.64,
        "USD": 60.66, "UZS": 0.0055,
    }
    filter_key_to_function = {
        "key_skills": lambda vac, input_vals: all([skill in vac.skills for skill in input_vals.filter_skills]),
        "salary": lambda vac, input_vals: int(input_vals.filter_param) >= vac.salary.salary_from and
                                          int(input_vals.filter_param) <= vac.salary.salary_to,
        "salary_currency": lambda vac, input_vals: input_vals.filter_param == vac.salary.salary_cur_ru,
        "experience_id": lambda vac, input_vals: vac.exp == input_vals.filter_param,
        "premium": lambda vac, input_vals: vac.prem == input_vals.filter_param,
        "published_at": lambda vac, input_vals: vac.time == input_vals.filter_param,
        "VOID_FILTER": lambda vac, input_vals: True
    }
    sort_key_to_function = {
        "Оклад": lambda vac: vac.salary.get_rur_salary(),
        "Навыки": lambda vac: len(vac.skills),
        "Опыт работы": lambda vac: All_Used_Dicts.exp_to_int[vac.exp],
        "VOID_SORT": lambda vac: 0
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
        self.salary_from = floor(float(dic["salary_from"]))
        self.salary_to = floor(float(dic["salary_to"]))
        self.salary_gross = "Без вычета налогов" if dic["salary_gross"] == "True" else "С вычетом налогов"
        self.salary_currency = dic["salary_currency"]
        self.salary_cur_ru = All_Used_Dicts.transformate[self.salary_currency]

    def get_rur_salary(self):
        """Функция перевода валюты в рубли.
        >>> Salary({"salary_from": 10, "salary_to": 20, "salary_currency": "RUR", "salary_gross": "True"}).get_rur_salary()
        15.0
        >>> Salary({"salary_from": 10, "salary_to": 20, "salary_currency": "EUR", "salary_gross": "True"}).get_rur_salary()
        898.5
        >>> Salary({"salary_from": "10", "salary_to": "20", "salary_currency": "RUR", "salary_gross": "True"}).get_rur_salary()
        15.0
        >>> Salary({"salary_from": "10", "salary_to": "20", "salary_currency": "KGS", "salary_gross": "True"}).get_rur_salary()
        11.4
        """
        middle_salary = (self.salary_to + self.salary_from) / 2
        return All_Used_Dicts.currency_to_rub[self.salary_currency] * middle_salary

    @staticmethod
    def get_number_with_delimiter(number: int) -> str:
        """Получить зарплату с пробелами через каждые 3 символа.

        Args:
            number (int): входное число.

        Returns:
            str: форматированное число.
        >>> Salary.get_number_with_delimiter(100)
        '100'
        >>> Salary.get_number_with_delimiter(1000)
        '1 000'
        >>> Salary.get_number_with_delimiter(1000000)
        '1 000 000'
        >>> Salary.get_number_with_delimiter(1000000000)
        '1 000 000 000'
        """
        return '{:,}'.format(number).replace(",", " ")

    def get_full_salary(self) -> str:
        """Получить полную зарплату по шаблону:\n
        <зарплата от> - <зарплата до> (<валюта>) (<есть ли вычет налогов>).

        Returns:
            str: Полная зарплата."""
        start = Salary.get_number_with_delimiter(self.salary_from)
        end = Salary.get_number_with_delimiter(self.salary_to)
        return f"{start} - {end} ({self.salary_cur_ru}) ({self.salary_gross})"


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
        self.skills = dic["key_skills"].split("\n")
        self.exp = All_Used_Dicts.transformate[dic["experience_id"]]
        self.prem = All_Used_Dicts.transformate[dic["premium"]]
        self.salary = Salary(dic)
        time_vals = dic["published_at"].split("T")[0].split("-")
        self.time = f"{time_vals[2]}.{time_vals[1]}.{time_vals[0]}"

    @staticmethod
    def clean_val(val: str) -> str:
        """Обрезать строку, если ее длинна >= 100 символам.

        Args:
            val (str): Входная строка.

        Returns:
            str: Обрезанная строка.
        >>> Vacancy.clean_val("abc")
        'abc'
        >>> Vacancy.clean_val("a"*100)
        'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa...'
        >>> Vacancy.clean_val("b"*99)
        'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        """
        return val if len(val) < 100 else val[:100] + "..."

    def get_list(self) -> list:
        """Получить список всех обрезанных данных вакансии.

        Returns:
            list: Список всех обрезанных данных вакансии.
        """
        s = self
        vals = [s.dic["name"], s.dic["description"], s.dic["key_skills"], s.exp,
                s.prem, s.dic["employer_name"], s.salary.get_full_salary(), s.dic["area_name"], s.time]
        return list(map(Vacancy.clean_val, vals))


class InputCorrect:
    """Проверка корректности ввода и существования файла.

    Attributes:
        file_name (str): Название csv-файла с данными.
        filter_param (str): Параметр фильтрации.
        sort_param (str): Параметр сортировки.
        reverse_sort (str): Обратная сортировка.
        start_end (str): Промежуток вывода.
        columns (str): Выводимые столбцы.
    """
    def __init__(self, file_name, filter_param, sort_param, reverse_sort, start_end, columns):
        """Инициализация объекта InputCorrect. Проверка на ошибки ввода.

        Args:
            file_name (str): Название csv-файла с данными.
            filter_param (str): Параметр фильтрации.
            sort_param (str): Параметр сортировки.
            reverse_sort (str): Обратная сортировка.
            start_end (str): Промежуток вывода.
            columns (str): Выводимые столбцы.
        """
        self.in_file_name = file_name
        self.in_filter_param = filter_param
        self.in_sort_param = sort_param
        self.in_reverse_sort = reverse_sort
        self.in_start_end = start_end
        self.in_columns = columns
        self.check_inputs_and_add_info()

    def check_inputs_and_add_info(self):
        """Проверка корректности ввода."""
        self.check_file()
        self.check_filter()
        self.check_sort()
        self.add_start_end()
        self.add_columns()

    def check_file(self):
        """Проверка корректности файла."""
        with open(self.in_file_name, "r", encoding='utf-8-sig', newline='') as csv_file:
            file_iter = iter(csv.reader(csv_file))
            if next(file_iter, "none") == "none": do_exit("Пустой файл")
            if next(file_iter, "none") == "none": do_exit("Нет данных")

    def check_filter(self):
        """Проверка корректности параметра фильтрации."""
        if self.in_filter_param != "":
            filter_param_split = self.in_filter_param.split(": ")
            if len(filter_param_split) <= 1: do_exit("Формат ввода некорректен")
            try: self.filter_key = All_Used_Dicts.filters[filter_param_split[0]]
            except: do_exit("Параметр поиска некорректен")
            self.filter_param = filter_param_split[1]
            self.filter_skills = filter_param_split[1].split(", ")
        else:
            self.filter_key = "VOID_FILTER"

    def check_sort(self):
        """Проверка корректности параметра сортировки."""
        if self.in_sort_param != "":
            if self.in_sort_param not in All_Used_Dicts.filters.keys(): do_exit("Параметр сортировки некорректен")
        else: self.in_sort_param = "VOID_SORT"
        if self.in_reverse_sort not in ["", "Да", "Нет"]: do_exit("Порядок сортировки задан некорректно")
        self.reverse_sort = True if self.in_reverse_sort == "Да" else False

    def add_start_end(self):
        """Выделение начального и конечного индекса отображения таблицы."""
        self.end = -1
        if self.in_start_end != "":
            start_end = self.in_start_end.split()
            if len(start_end) >= 1:
                self.start = int(start_end[0])
            if len(start_end) >= 2:
                self.end = int(start_end[1])
        else:
            self.start = 1

    def add_columns(self):
        """Добавление выводимых стобцов."""
        if self.in_columns == "": self.columns = list(All_Used_Dicts.header_to_ru.values())
        else: self.columns = ["№"] + self.in_columns.split(", ")


class DataSet:
    """Считывание файла и формирование удобной структуры данных."""
    def __init__(self):
        """Инициализация класса DataSet. Считывание. Фильтрация. Сортировка. Вывод."""
        self.input_values = InputCorrect(input("Введите название файла: "), input("Введите параметр фильтрации: "),
                            input("Введите параметр сортировки: "), input("Обратный порядок сортировки (Да / Нет): "),
                            input("Введите диапазон вывода: "), input("Введите требуемые столбцы: "))
        self.csv_reader()
        self.csv_filter()
        self.sort_vacancies()
        self.print_vacancies()

    def csv_reader(self):
        """Считывание csv-файла с первичной фильтрацией (пропуск невалидных строк)."""
        with open(self.input_values.in_file_name, "r", encoding='utf-8-sig', newline='') as csv_file:
            file = csv.reader(csv_file)
            self.start_line = next(file)
            self.other_lines = [line for line in file
                           if not ("" in line) and len(line) == len(self.start_line)]

    @staticmethod
    def clear_field_from_html_and_spaces(field: str) -> str:
        """Функция удаления HTML-тегов и лишних пробелов из поля.

        Args:
            field (str): Очищаемое поле.

        Returns:
            str: Очищенное поле.
        >>> DataSet.clear_field_from_html_and_spaces("abc")
        'abc'
        >>> DataSet.clear_field_from_html_and_spaces("<div>abc</div>")
        'abc'
        >>> DataSet.clear_field_from_html_and_spaces("<div>abc")
        'abc'
        >>> DataSet.clear_field_from_html_and_spaces("   abc  ")
        'abc'
        >>> DataSet.clear_field_from_html_and_spaces(" abc     abd")
        'abc abd'
        >>> DataSet.clear_field_from_html_and_spaces(" <div><strong><i>  abc <i>  abd  <string>")
        'abc abd'
        >>> DataSet.clear_field_from_html_and_spaces(" <div> abc <iqewqljl> <  div   > abd <i>")
        'abc abd'
        """
        new_field = re.sub(r"\<[^>]*\>", '', field).strip()
        if new_field.find("\n") > -1:
            new_field = new_field.replace("\r", "")
        else:
            new_field = re.sub(r'\s+', ' ', new_field)
        return new_field

    def csv_filter(self):
        """Фильтрация данных по параметру фильтрации."""
        self.filtered_vacancies = []
        for line in self.other_lines:
            new_dict_line = dict(zip(self.start_line, map(DataSet.clear_field_from_html_and_spaces, line)))
            vac = Vacancy(new_dict_line)
            try:
                is_correct_vac = \
                    All_Used_Dicts.filter_key_to_function[self.input_values.filter_key](vac, self.input_values)
            except:
                is_correct_vac = vac.dic[self.input_values.filter_key] == self.input_values.filter_param
            if is_correct_vac: self.filtered_vacancies.append(vac)

    def get_sort_function(self):
        """Получение функции фильтрации.

        Returns:
            Func: Если заготовленной функции нет, то вернуть стандартную.
        """
        try:
            func = All_Used_Dicts.sort_key_to_function[self.input_values.in_sort_param]
        except:
            func = lambda vac: vac.dic[All_Used_Dicts.filters[self.input_values.in_sort_param]]
        return func

    def sort_vacancies(self):
        """Отсортировать вакансии по соответствующему параметру."""
        self.filtered_vacancies.sort(key=self.get_sort_function(),
                                     reverse=self.input_values.reverse_sort)

    def print_vacancies(self):
        """Напечатать вакансии в виде таблицы PrettyTable."""
        vac_len = len(self.filtered_vacancies)
        if vac_len <= 0: do_exit("Ничего не найдено")
        if self.input_values.end == -1: self.input_values.end = vac_len + 1
        exit_table = PrettyTable(align="l", hrules=prettytable.ALL)
        exit_table.field_names = All_Used_Dicts.header_to_ru.values()
        exit_table.max_width = 20
        [exit_table.add_row([i + 1] + self.filtered_vacancies[i].get_list()) for i in range(vac_len)]
        print(exit_table.get_string(start=self.input_values.start - 1, end=self.input_values.end - 1,
                                    fields=self.input_values.columns))


def create_table():
    """Создать и напечатать таблицу PrettyTable."""
    DataSet()