import csv, re, prettytable
from math import floor
from prettytable import PrettyTable


def do_exit(message):
    print(message)
    exit(0)


class All_Used_Dicts():
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
    def __init__(self, dic):
        self.salary_from = floor(float(dic["salary_from"]))
        self.salary_to = floor(float(dic["salary_to"]))
        self.salary_gross = "Без вычета налогов" if dic["salary_gross"] == "True" else "С вычетом налогов"
        self.salary_currency = dic["salary_currency"]
        self.salary_cur_ru = All_Used_Dicts.transformate[self.salary_currency]

    def get_rur_salary(self):
        middle_salary = (self.salary_to + self.salary_from) / 2
        return All_Used_Dicts.currency_to_rub[self.salary_currency] * middle_salary

    def get_number_with_delimiter(self, number: int) -> str:
        return '{:,}'.format(number).replace(",", " ")

    def get_full_salary(self) -> str:
        start = self.get_number_with_delimiter(self.salary_from)
        end = self.get_number_with_delimiter(self.salary_to)
        return f"{start} - {end} ({self.salary_cur_ru}) ({self.salary_gross})"


class Vacancy:
    def __init__(self, dic: dict):
        self.dic = dic
        self.skills = dic["key_skills"].split("\n")
        self.exp = All_Used_Dicts.transformate[dic["experience_id"]]
        self.prem = All_Used_Dicts.transformate[dic["premium"]]
        self.salary = Salary(dic)
        time_vals = dic["published_at"].split("T")[0].split("-")
        self.time = f"{time_vals[2]}.{time_vals[1]}.{time_vals[0]}"

    def clean_val(self, val: str) -> str:
        return val if len(val) < 100 else val[:100] + "..."

    def get_list(self) -> list:
        s = self
        vals = [s.dic["name"], s.dic["description"], s.dic["key_skills"], s.exp,
                s.prem, s.dic["employer_name"], s.salary.get_full_salary(), s.dic["area_name"], s.time]
        return list(map(s.clean_val, vals))


class InputConect:
    def __init__(self, file_name, filter_param, sort_param, reverse_sort, start_end, columns):
        self.in_file_name = file_name
        self.in_filter_param = filter_param
        self.in_sort_param = sort_param
        self.in_reverse_sort = reverse_sort
        self.in_start_end = start_end
        self.in_columns = columns
        self.check_inputs_and_add_info()

    def check_inputs_and_add_info(self):
        self.check_file()
        self.check_filter()
        self.check_sort()
        self.add_start_end()
        self.add_columns()

    def check_file(self):
        with open(self.in_file_name, "r", encoding='utf-8-sig', newline='') as csv_file:
            file_iter = iter(csv.reader(csv_file))
            if next(file_iter, "none") == "none": do_exit("Пустой файл")
            if next(file_iter, "none") == "none": do_exit("Нет данных")

    def check_filter(self):
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
        if self.in_sort_param != "":
            if self.in_sort_param not in All_Used_Dicts.filters.keys(): do_exit("Параметр сортировки некорректен")
        else: self.in_sort_param = "VOID_SORT"
        if self.in_reverse_sort not in ["", "Да", "Нет"]: do_exit("Порядок сортировки задан некорректно")
        self.reverse_sort = True if self.in_reverse_sort == "Да" else False

    def add_start_end(self):
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
        if self.in_columns == "": self.columns = list(All_Used_Dicts.header_to_ru.values())
        else: self.columns = ["№"] + self.in_columns.split(", ")


class DataSet:
    def __init__(self):
        self.input_values = InputConect(input("Введите название файла: "), input("Введите параметр фильтрации: "),
                            input("Введите параметр сортировки: "), input("Обратный порядок сортировки (Да / Нет): "),
                            input("Введите диапазон вывода: "), input("Введите требуемые столбцы: "))
        self.csv_reader()
        self.csv_filter()
        self.sort_vacancies()
        self.print_vacancies()

    def csv_reader(self):
        with open(self.input_values.in_file_name, "r", encoding='utf-8-sig', newline='') as csv_file:
            file = csv.reader(csv_file)
            self.start_line = next(file)
            self.other_lines = [line for line in file
                           if not ("" in line) and len(line) == len(self.start_line)]

    def clear_field_from_html_and_spaces(self, field) -> str:
        new_field = re.sub(r"\<[^>]*\>", '', field).strip()
        if new_field.find("\n") > -1:
            new_field = new_field.replace("\r", "")
        else:
            new_field = re.sub(r'\s+', ' ', new_field)
        return new_field

    def csv_filter(self):
        self.filtered_vacancies = []
        for line in self.other_lines:
            new_dict_line = dict(zip(self.start_line, map(self.clear_field_from_html_and_spaces, line)))
            vac = Vacancy(new_dict_line)
            try:
                is_correct_vac = \
                    All_Used_Dicts.filter_key_to_function[self.input_values.filter_key](vac, self.input_values)
            except:
                is_correct_vac = vac.dic[self.input_values.filter_key] == self.input_values.filter_param
            if is_correct_vac: self.filtered_vacancies.append(vac)

    def get_sort_function(self):
        try:
            func = All_Used_Dicts.sort_key_to_function[self.input_values.in_sort_param]
        except:
            func = lambda vac: vac.dic[All_Used_Dicts.filters[self.input_values.in_sort_param]]
        return func

    def sort_vacancies(self):
        self.filtered_vacancies.sort(key=self.get_sort_function(),
                               reverse=self.input_values.reverse_sort)

    def print_vacancies(self):
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
    DataSet()