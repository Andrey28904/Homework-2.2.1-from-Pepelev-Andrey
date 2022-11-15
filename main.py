import csv, re, math

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from jinja2 import Template
import pdfkit


def do_exit(message):
    print(message)
    exit(0)


currency_to_rub = {
    "AZN": 35.68, "BYR": 23.91, "EUR": 59.90, "GEL": 21.74,
    "KGS": 0.76, "KZT": 0.13, "RUR": 1, "UAH": 1.64,
    "USD": 60.66, "UZS": 0.0055,
}


class Salary:
    def __init__(self, dic):
        self.salary_from = math.floor(float(dic["salary_from"]))
        self.salary_to = math.floor(float(dic["salary_to"]))
        self.salary_currency = dic["salary_currency"]
        middle_salary = (self.salary_to + self.salary_from) / 2
        self.salary_in_rur = currency_to_rub[self.salary_currency] * middle_salary


class Vacancy:
    def __init__(self, dic: dict):
        self.dic = dic
        self.salary = Salary(dic)
        self.dic["year"] = int(dic["published_at"][:4])
        self.is_needed = dic["is_needed"]


class InputConect:
    def __init__(self):
        self.in_file_name = input("Введите название файла: ")
        self.in_prof_name = input("Введите название профессии: ")
        self.check_file()

    def check_file(self):
        with open(self.in_file_name, "r", encoding='utf-8-sig', newline='') as csv_file:
            file_iter = iter(csv.reader(csv_file))
            if next(file_iter, "none") == "none": do_exit("Пустой файл")
            if next(file_iter, "none") == "none": do_exit("Нет данных")


class DataSet:
    def __init__(self):
        self.input_values = InputConect()
        self.csv_reader()
        self.csv_filter()
        self.get_years()
        self.count_graph_data()

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
            new_dict_line = dict(zip(self.start_line, line))
            new_dict_line["is_needed"] = new_dict_line["name"].find(self.input_values.in_prof_name) > -1
            vac = Vacancy(new_dict_line)
            self.filtered_vacancies.append(vac)
        self.needed_vacancies = list(filter(lambda vac: vac.is_needed, self.filtered_vacancies))

    def get_years(self):
        self.all_years = list(set([vac.dic["year"] for vac in self.filtered_vacancies]))
        self.all_years.sort()

    def try_to_add(self, dic: dict, key, val) -> dict:
        try:
            dic[key] += val
        except:
            dic[key] = val
        return dic

    def get_middle_salary(self, count: dict, sum: dict) -> dict:
        key_to_salary = {}
        for key, val in count.items():
            if val == 0:
                key_to_salary[key] = 0
            else:
                key_to_salary[key] = math.floor(sum[key] / val)
        return key_to_salary

    def update_keys(self, key_to_count: dict) -> dict:
        for key in self.all_years:
            if key not in key_to_count.keys():
                key_to_count[key] = 0
        return key_to_count

    def get_key_to_salary_and_count(self, vacs: list, key_str: str, is_area: bool) -> (dict, dict):
        key_to_sum = {}
        key_to_count = {}
        for vac in vacs:
            key_to_sum = self.try_to_add(key_to_sum, vac.dic[key_str], vac.salary.salary_in_rur)
            key_to_count = self.try_to_add(key_to_count, vac.dic[key_str], 1)
        if is_area:
            key_to_count = dict(filter(lambda item: item[1] / len(vacs) > 0.01, key_to_count.items()))
        else:
            key_to_sum = self.update_keys(key_to_sum)
            key_to_count = self.update_keys(key_to_count)
        key_to_middle_salary = self.get_middle_salary(key_to_count, key_to_sum)
        return key_to_middle_salary, key_to_count

    def get_sorted_dict(self, key_to_salary: dict):
        return dict(list(sorted(key_to_salary.items(), key=lambda item: item[1], reverse=True))[:10])

    def count_graph_data(self):
        count_vacs = len(self.filtered_vacancies)
        self.year_to_salary, self.year_to_count = \
            self.get_key_to_salary_and_count(self.filtered_vacancies, "year", False)
        self.year_to_salary_needed, self.year_to_count_needed = \
            self.get_key_to_salary_and_count(self.needed_vacancies, "year", False)
        self.area_to_salary, self.area_to_count = \
            self.get_key_to_salary_and_count(self.filtered_vacancies, "area_name", True)
        self.area_to_salary = self.get_sorted_dict(self.area_to_salary)
        self.area_to_piece = {key: round(val / count_vacs, 4) for key, val in self.area_to_count.items()}
        self.area_to_piece = self.get_sorted_dict(self.area_to_piece)


class Report:
    def __init__(self, data: DataSet):
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

    def get_percents(self, value):
        return f"{round(value * 100, 2)}%"

    def get_table_rows(self, columns: list):
        rows_list = [["" for _ in range(len(columns))] for _ in range(len(columns[0]))]
        for col in range(len(columns)):
            for cell in range(len(columns[col])):
                rows_list[cell][col] = columns[col][cell]
        return rows_list

    def standart_bar(self, ax: Axes, keys1, keys2, values1, values2, label1, label2, title):
        x1 = [key - 0.2 for key in keys1]
        x2 = [key + 0.2 for key in keys2]
        ax.bar(x1, values1, width=0.4, label=label1)
        ax.bar(x2, values2, width=0.4, label=label2)
        ax.legend()
        ax.set_title(title, fontsize=16)
        ax.grid(axis="y")
        ax.tick_params(axis='x', labelrotation=90)

    def horizontal_bar(self, ax: Axes):
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
        fig, axis = plt.subplots(2, 2)
        plt.rcParams['font.size'] = 8
        self.standart_bar(axis[0, 0], self.data.year_to_salary.keys(), self.data.year_to_salary_needed.keys(),
                          self.data.year_to_count.values(), self.data.year_to_count_needed.values(),
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


report_data = Report(DataSet())
report_data.generate_pdf("report.pdf")