import ReportPDF, ReportTable


def main():
    type_of_report = input("Введите тип отчета (Вакансии/Статистика): ")
    if type_of_report == "Вакансии":
        ReportTable.create_table()
    elif type_of_report == "Статистика":
        ReportPDF.create_pdf()
    else:
        print("Неверный тип отчета!")
        exit(0)


<<<<<<< HEAD
testing_merge_conflict_value = "Alyona crash Vasya's code"
||||||| f621660
testing_merge_conflict_value = "Standart Value"
=======
testing_merge_conflict_value = "Vasya code change this value"
>>>>>>> merge_conflict_branch
main()
