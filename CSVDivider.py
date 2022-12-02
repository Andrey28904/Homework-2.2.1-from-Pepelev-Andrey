import csv, os


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
    """
    def __init__(self, file: str):
        """Инициализация объекта InputCorrect. Проверка на существование и заполненность файла.

        Args:
            file (str): Название csv-файла с данными.
        """
        self.in_file_name = file
        self.check_file()

    def check_file(self):
        """Проверка на существование и заполненность файла."""
        with open(self.in_file_name, "r", encoding='utf-8-sig', newline='') as csv_file:
            file_iter = iter(csv.reader(csv_file))
            if next(file_iter, "none") == "none": do_exit("Пустой файл")
            if next(file_iter, "none") == "none": do_exit("Нет данных")


class DataSet_Divider:
    """Считывание файла и формирование удобной структуры данных.

    Attributes:
        input_data (InputCorrect): Неразделенный файл и его первая строка.
        csv_dir (str): Папка расположения CSV-файлов.
    """
    def __init__(self, input_data: InputCorrect, csv_dir: str):
        """Инициализация класса DataSet. Чтение. Разделение на разные файлы.

        Args:
            input_data (InputCorrect): Неразделенный файл и его первая строка.
            csv_dir (str): Папка расположения CSV-файлов.
        """
        self.input_values = input_data
        self.dir = csv_dir
        self.csv_reader()
        self.csv_divide()

    def csv_reader(self):
        """Чтение файла и первичная фильтрация (пропуск невалидных строк)."""
        with open(self.input_values.in_file_name, "r", encoding='utf-8-sig', newline='') as csv_file:
            file = csv.reader(csv_file)
            self.start_line = next(file)
            self.other_lines = [line for line in file
                                if not ("" in line) and len(line) == len(self.start_line)]
            self.year_index = self.start_line.index("published_at")

    @staticmethod
    def get_year_method_3(data: str):
        """Функция вычисления года через индексы в строке.

        Args:
            data (str): дата вакансии в виде строки из csv-файла.

        Returns:
            str: Год - 4 цифры.
        """
        return data[:4]

    def save_file(self, current_year: str, lines: list):
        """Сохраняет CSV-файл с конкретными годами

        Args:
            current_year (str): Текущий год.
            lines (list): Список вакансий этого года.
        """
        with open(f"{self.dir}/file_{current_year}.csv", "a", encoding='utf-8-sig', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(lines)

    def csv_divide(self):
        """Разделяет данные на csv-файлы по годам"""
        current_year = DataSet_Divider.get_year_method_3(self.other_lines[0][self.year_index])
        current_index = 0
        data_years = [[]]
        for line in self.other_lines:
            line_year = DataSet_Divider.get_year_method_3(line[self.year_index])
            if line_year != current_year:
                self.save_file(current_year, data_years[current_index])
                current_year = line_year
                current_index += 1
                data_years.append([])
            data_years[current_index].append(line)
        self.save_file(current_year, data_years[current_index])


def divide_csv_file(csv_dir: str):
    """Проверяет наличие CSV-файла и разделяет его по годам на много файлов
    Args:
        csv_dir (str): папка расположения всех csv-файлов.
    """
    input_data = InputCorrect(input("Введите название файла: "))
    if os.path.exists(csv_dir):
        import shutil
        shutil.rmtree(csv_dir)
    os.mkdir(csv_dir)
    data_set = DataSet_Divider(input_data, csv_dir)
    return data_set


if __name__ == '__main__':
    divide_csv_file("csv")

