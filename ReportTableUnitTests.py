from unittest import TestCase
from ReportTable import *

class ReportTableUnitTests(TestCase):
    def test_get_rur_salary_with_int_and_rur(self):
        self.assertEqual(Salary({"salary_from": 10, "salary_to": 20,
                                 "salary_currency": "RUR", "salary_gross": "True"}).get_rur_salary(), 15.0)

    def test_get_rur_salary_with_int_and_eur(self):
        self.assertEqual(Salary({"salary_from": 10, "salary_to": 20,
                                 "salary_currency": "EUR", "salary_gross": "True"}).get_rur_salary(), 898.5)

    def test_get_rur_salary_with_str_and_rur(self):
        self.assertEqual(Salary({"salary_from": "10", "salary_to": "20",
                                 "salary_currency": "RUR", "salary_gross": "True"}).get_rur_salary(), 15.0)

    def test_get_rur_salary_with_str_and_kgs(self):
        self.assertEqual(Salary({"salary_from": "10", "salary_to": "20",
                                 "salary_currency": "KGS", "salary_gross": "True"}).get_rur_salary(), 11.4)

    def test_get_number_with_delimiter_100(self):
        self.assertEqual(Salary.get_number_with_delimiter(100), "100")

    def test_get_number_with_delimiter_1000(self):
        self.assertEqual(Salary.get_number_with_delimiter(1000), "1 000")

    def test_get_number_with_delimiter_1000000(self):
        self.assertEqual(Salary.get_number_with_delimiter(1000000), "1 000 000")

    def test_get_number_with_delimiter_100000000(self):
        self.assertEqual(Salary.get_number_with_delimiter(1000000000), "1 000 000 000")

    def test_clean_val_simple(self):
        self.assertEqual(Vacancy.clean_val("abc"), "abc")

    def test_clean_val_100_a(self):
        self.assertEqual(Vacancy.clean_val("a"*100),
                         'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa...')

    def test_clean_val_99_b(self):
        self.assertEqual(Vacancy.clean_val("b"*99),
                         'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb')

    def test_clean_html_and_spaces_simple(self):
        self.assertEqual(DataSet.clear_field_from_html_and_spaces("abc"), "abc")

    def test_clean_html_and_spaces_with_double_tag(self):
        self.assertEqual(DataSet.clear_field_from_html_and_spaces("<div>abc</div>"), 'abc')

    def test_clean_html_and_spaces_with_one_tag(self):
        self.assertEqual(DataSet.clear_field_from_html_and_spaces("<div>abc"), 'abc')

    def test_clean_html_and_spaces_with_spaces(self):
        self.assertEqual(DataSet.clear_field_from_html_and_spaces("   abc  "), "abc")

    def test_clean_html_and_spaces_with_spaces_and_two_words(self):
        self.assertEqual(DataSet.clear_field_from_html_and_spaces(" abc     abd"), 'abc abd')

    def test_clean_html_and_spaces_with_many_spaces_and_tags(self):
        self.assertEqual(DataSet.clear_field_from_html_and_spaces(" <div><strong><i>  abc <i>  abd  <string>"), 'abc abd')

    def test_clean_html_and_spaces_with_many_spaces_and_tags_and_incorrect_tag(self):
        self.assertEqual(DataSet.clear_field_from_html_and_spaces(" <div> abc <iqewqljl> <  div   > abd <i>"), 'abc abd')