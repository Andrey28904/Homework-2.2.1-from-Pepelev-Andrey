import csv


class RefactorAPICSV:
    """Коасс для обработки csv в другой формат csv
    Attributes:
        full_path_to_csv(str): старый файл.
        new_csv_path(str): новый файл.
    """
    start_basic_row = {"Year" : 0, "Month": 1, "CharCode": 2, "InRuR": 3}

    def __init__(self, full_path_to_csv: str, new_csv_path: str):
        """Обработка старого файла и создание нового.
        Args:
            full_path_to_csv(str): старый файл.
            new_csv_path(str): новый файл.
        """
        self.full_path_to_csv = full_path_to_csv
        self.new_csv_path = new_csv_path
        self.get_new_csv()

    def get_all_currencies(self) -> list:
        """Получить список всех валют за все время.
        Returns:
            list: список валют.
        """
        all_currencies = []
        with open(file=self.full_path_to_csv, mode="r", encoding="utf-8-sig") as csv_file:
            lines = csv.reader(csv_file)
            next(lines)
            for line in lines:
                new_charcode = line[RefactorAPICSV.start_basic_row["CharCode"]]
                if new_charcode not in all_currencies:
                    all_currencies.append(new_charcode)
        csv_file.close()
        return all_currencies

    def get_year_month(self, line: list) -> str:
        """Получить новый формат времени из списка.
        Args:
            line(list): список с данными об одной валюте.
        Returns:
            str: новый формат даты.
        """
        month = line[1]
        if int(month) < 10:
            month = "0"+month
        return f"{line[0]}-{month}"

    def save_data(self, all_lines: list) -> None:
        """сохранить обработанные данные.
        Args:
            all_lines(list): строки для сохренения.
        """
        with open(file=self.new_csv_path, mode="w", encoding="utf-8-sig", newline='') as csv_basic_file:
            csv_base = csv.writer(csv_basic_file)
            csv_base.writerows(all_lines)
        csv_basic_file.close()


    def get_new_csv(self) -> str:
        """обработать старый файл и получить новые строки + сохранить их."""
        all_currencies = ["RUR"] + self.get_all_currencies()
        all_new_lines = []
        all_new_lines.append(["Data"] + all_currencies)
        with open(file=self.full_path_to_csv, mode="r", encoding="utf-8-sig") as csv_file:
            lines = csv.reader(csv_file)
            next(lines)
            current_cur_to_inrur = {cur: None for cur in all_currencies}
            current_cur_to_inrur["RUR"] = 1
            first_line = next(lines)
            current_cur_to_inrur[first_line[2]] = first_line[3]
            current_year_month = self.get_year_month(first_line)
            for line in lines:
                year_month = self.get_year_month(line)
                if current_year_month == year_month:
                    current_cur_to_inrur[line[2]] = line[3]
                else:
                    all_new_lines.append([current_year_month] + list(current_cur_to_inrur.values()))
                    current_cur_to_inrur = {cur: None for cur in all_currencies}
                    current_cur_to_inrur["RUR"] = 1
                    current_year_month = year_month
                current_cur_to_inrur[line[2]] = line[3]
        self.save_data(all_new_lines)


if __name__ == '__main__':
    refactor = RefactorAPICSV("api_data/currency_csv.csv", "api_data/new_currencies.csv")