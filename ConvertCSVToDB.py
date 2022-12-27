import pandas as pd
import os, shutil
import sqlite3


class DBConverter:
    """Класс для конвертации csv в db.
    Attributes:
        full_csv_path(str): путь до файла csv.
        db_path(str): путь до директории с базой данных.
        db_name(str): название базы данных.
    """
    def __init__(self, full_csv_path: str, db_path: str, db_name: str):
        """Инициализация. создание базы данных из csv-файла.
        Args:
            full_csv_path(str): путь до файла csv.
            db_path(str): путь до директории с базой данных.
            db_name(str): название базы данных.
        """
        self.full_csv_path = full_csv_path
        self.db_path = db_path
        self.db_name = db_name
        self.convert_csv()

    @staticmethod
    def make_dir_if_needed(dir: str) -> None:
        """Создание нужной дериктории."""
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.mkdir(dir)

    def convert_csv(self):
        """Конверация csv с валютами в db с валютами."""
        DBConverter.make_dir_if_needed(self.db_path)
        full_db_path = self.db_path+"/"+self.db_name
        con = sqlite3.connect(full_db_path)
        con.execute("DROP TABLE IF EXISTS currencies")
        pd.read_csv(self.full_csv_path).to_sql("currencies", con, index=False)


if __name__ == '__main__':
    converter = DBConverter("api_data/new_currencies.csv", "db", "currencies_db.db")
