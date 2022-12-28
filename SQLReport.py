import csv, math
import sqlite3
import pandas as pd


class SQLReport:
    """Класс для создания 6-ти запросов в базу данных.
    Attributes:
        db_name (str): имя базы данных с вакансиями.
        prof (str): название професии.
    """
    def __init__(self, db_name: str, prof: str):
        """Инициализация. Создание всех запросов и вывод результата на экран.
        Args:
            db_name (str): имя базы данных с вакансиями.
            prof (str): название професии.
        """
        self.connect = sqlite3.connect(db_name)
        self.print_salary_by_year()
        self.print_count_by_year()
        self.print_salary_by_year_needed(prof)
        self.print_count_by_year_needed(prof)
        self.print_salary_by_area()
        self.print_piece_by_area()

    def print_salary_by_year(self) -> None:
        """Создает запрос по средней зарплате всех вакансий по годам"""
        print(">>>>>>>>>>>>>>>>>>>>>>>Динамика уровня зарплат по годам<<<<<<<<<<<<<<<<<<<<<<<")
        sql_request = """
            SELECT strftime('%Y', published_at) as year, CAST(ROUND(AVG(salary)) AS INTEGER) as avg_salary
            FROM vacancies 
            GROUP BY strftime('%Y', published_at);
        """
        df = pd.read_sql(sql_request, self.connect)
        print(df)
        print(">>>>>>>>>>>>>>>>>>>>>>>=================================<<<<<<<<<<<<<<<<<<<<<<<", "\n")

    def print_count_by_year(self) -> None:
        """Создает запрос по количеству всех вакансий по годам"""
        print(">>>>>>>>>>>>>>>>>>>>>>>Динамика количества вакансий по годам<<<<<<<<<<<<<<<<<<<<<<<")
        sql_request = """
            SELECT strftime('%Y', published_at) as year, COUNT(*) as count
            FROM vacancies 
            GROUP BY strftime('%Y', published_at);
        """
        df = pd.read_sql(sql_request, self.connect)
        print(df)
        print(">>>>>>>>>>>>>>>>>>>>>>>=================================<<<<<<<<<<<<<<<<<<<<<<<", "\n")

    def print_salary_by_year_needed(self, prof: str) -> None:
        """Создает запрос по средней зарплате нужных вакансий по годам"""
        print(">>>>>>>>>>>>>>>>>>>>>>>Динамика уровня зарплат по годам для выбранной профессии<<<<<<<<<<<<<<<<<<<<<<<")
        sql_request = f" \
            SELECT strftime('%Y', published_at) as year, CAST(ROUND(AVG(salary)) AS INTEGER) as avg_salary \
            FROM vacancies \
            WHERE name LIKE '%{prof}%' \
            GROUP BY strftime('%Y', published_at); \
        "
        df = pd.read_sql(sql_request, self.connect)
        print(df)
        print(">>>>>>>>>>>>>>>>>>>>>>>=================================<<<<<<<<<<<<<<<<<<<<<<<", "\n")

    def print_count_by_year_needed(self, prof: str) -> None:
        """Создает запрос по количеству нужных вакансий по годам"""
        print(">>>>>>>>>>>>>>>>>>>>>>>Динамика количества вакансий по годам для выбранной профессии<<<<<<<<<<<<<<<<<<<<<<<")
        sql_request = f" \
            SELECT strftime('%Y', published_at) as year, COUNT(*) as count \
            FROM vacancies \
            WHERE name LIKE '%{prof}%' \
            GROUP BY strftime('%Y', published_at); \
        "
        df = pd.read_sql(sql_request, self.connect)
        print(df)
        print(">>>>>>>>>>>>>>>>>>>>>>>=================================<<<<<<<<<<<<<<<<<<<<<<<", "\n")

    def print_salary_by_area(self) -> None:
        """Создает запрос по средней зарплате в городах."""
        print(">>>>>>>>>>>>>>>>>>>>>>>Уровень зарплат по городам<<<<<<<<<<<<<<<<<<<<<<<")
        sql_request = """
            SELECT area_name, COUNT(*) as count, CAST(ROUND(AVG(salary)) AS INTEGER) as avg_salary
            FROM vacancies 
            GROUP BY area_name 
            HAVING count > (SELECT COUNT(*) FROM vacancies) / 100
            ORDER BY avg_salary DESC
            LIMIT 10;
        """
        df = pd.read_sql(sql_request, self.connect)
        print(df)
        print(">>>>>>>>>>>>>>>>>>>>>>>=================================<<<<<<<<<<<<<<<<<<<<<<<", "\n")

    def print_piece_by_area(self) -> None:
        """Создает запрос по доле городов."""
        print(">>>>>>>>>>>>>>>>>>>>>>>Доля вакансий по городам<<<<<<<<<<<<<<<<<<<<<<<")
        sql_request = """
            SELECT area_name, COUNT(*) as count, 
                CAST(ROUND(CAST(COUNT(*) AS REAL) / (SELECT COUNT(*) FROM vacancies) * 100, 4) AS VARCHAR) || '%' AS piece
            FROM vacancies 
            GROUP BY area_name 
            HAVING count > (SELECT COUNT(*) FROM vacancies) / 100
            ORDER BY COUNT(*) DESC
            LIMIT 10;
        """
        df = pd.read_sql(sql_request, self.connect)
        print(df)
        print(">>>>>>>>>>>>>>>>>>>>>>>=================================<<<<<<<<<<<<<<<<<<<<<<<", "\n")


def set_pandas_options():
    """Устанавливает настройки pandas, чтобы корректно отображать класс DataFrame в консоли."""
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.expand_frame_repr', False)


if __name__ == '__main__':
    set_pandas_options()
    file_name = "vacancies_big.db" #input("Введите название файла: ")
    prof_name = "Программист" #input("Введите название профессии: ")
    input_values = SQLReport(file_name, prof_name)