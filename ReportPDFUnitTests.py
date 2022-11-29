from unittest import TestCase
from ReportPDF import *

class ReportPDFUnitTests(TestCase):
    def test_try_to_add_with_the_same_once_key(self):
        self.assertEqual(DataSet.try_to_add({"a": 10}, "a", 5), {'a': 15})

    def test_try_to_add_with_the_different_keys(self):
        self.assertEqual(DataSet.try_to_add({"a": 10}, "b", 5), {'a': 10, 'b': 5})

    def test_try_to_add_with_add_negative_value(self):
        self.assertEqual(DataSet.try_to_add({"a": 10}, "a", -5), {'a': 5})

    def test_try_to_add_with_empty_dict(self):
        self.assertEqual(DataSet.try_to_add({}, "a", 5), {'a': 5})

    def test_try_to_add_with_two_tags_add_one_tag_value(self):
        self.assertEqual(DataSet.try_to_add({"a": 5, "b": 10}, "a", 20), {'a': 25, 'b': 10})

    def test_try_to_add_with_two_tags_add_other_one_tag_value(self):
        self.assertEqual(DataSet.try_to_add({"a": 5, "b": 10}, "b", 40), {'a': 5, 'b': 50})

    def test_try_to_add_with_two_tags_and_keys_is_integers(self):
        self.assertEqual(DataSet.try_to_add({2022: 10, 2023: 0}, 2022, 5), {2022: 15, 2023: 0})

    def test_try_to_add_with_different_keys_types(self):
        self.assertEqual(DataSet.try_to_add({2022: 0}, "a", 5), {2022: 0, 'a': 5})

    def test_try_to_add_with_different_keys_types_and_the_same_key(self):
        self.assertEqual(DataSet.try_to_add({2022: 0, "a": 5}, 2022, 100), {2022: 100, 'a': 5})

    def test_get_middle_salary_with_one_key_value(self):
        self.assertEqual(DataSet.get_middle_salary({2022: 10}, {2022: 120}), {2022: 12})

    def test_get_middle_salary_with_two_keys_values(self):
        self.assertEqual(DataSet.get_middle_salary({2022: 10, 2023: 1}, {2022: 100, 2023: 10}), {2022: 10, 2023: 10})

    def test_get_middle_salary_with_two_different_key_types(self):
        self.assertEqual(DataSet.get_middle_salary({"2022": 10, 2023: 2}, {"2022": 100, 2023: 10}), {'2022': 10, 2023: 5})

    def test_get_middle_salary_with_zero_by_zero(self):
        self.assertEqual(DataSet.get_middle_salary({2022: 0}, {2022: 0}), {2022: 0})

    def test_get_middle_salary_with_zero_by_zero_and_normal_key_value(self):
        self.assertEqual(DataSet.get_middle_salary({2022: 0, 2023: 10}, {2022: 0, 2023: 1200}), {2022: 0, 2023: 120})

    def test_get_middle_salary_with_negative_value(self):
        self.assertEqual(DataSet.get_middle_salary({2022: 5}, {2022: -50}), {2022: -10})

    def test_update_with_empty_dict(self):
        self.assertEqual(DataSet.update_keys([2022], {}), {2022: 0})

    def test_update_with_one_key(self):
        self.assertEqual(DataSet.update_keys([2022], {2022: 10}), {2022: 10})

    def test_update_with_one_missed_key(self):
        self.assertEqual(DataSet.update_keys([2022, 2023], {2022: 10}), {2022: 10, 2023: 0})

    def test_update_with_two_keys(self):
        self.assertEqual(DataSet.update_keys([2022, 2023], {2022: 10, 2023: 20}), {2022: 10, 2023: 20})

    def test_update_with_two_keys_and_other_key_in_dict(self):
        self.assertEqual(DataSet.update_keys([2022], {2022: 10, 2023: 20}), {2022: 10, 2023: 20})

    def test_update_with_empty_dict_and_four_keys(self):
        self.assertEqual(DataSet.update_keys([2022, 2023, 2024, 2025], {}), {2022: 0, 2023: 0, 2024: 0, 2025: 0})

    def test_get_sorted_dict_with_empty_dict(self):
        self.assertEqual(DataSet.get_sorted_dict({}), {})

    def test_get_sorted_dict_with_one_key(self):
        self.assertEqual(DataSet.get_sorted_dict({"Мск": 10}), {'Мск': 10})

    def test_get_sorted_dict_with_two_keys(self):
        self.assertEqual(DataSet.get_sorted_dict({"Екб": 10, "Мск": 20}), {'Мск': 20, 'Екб': 10})

    def test_get_sorted_dict_with_two_keys_with_same_value(self):
        self.assertEqual(DataSet.get_sorted_dict({"Екб": 20, "Мск": 20}), {'Екб': 20, 'Мск': 20})

    def test_get_sorted_dict_with_three_keys_and_two_with_same_value(self):
        self.assertEqual(DataSet.get_sorted_dict({"a": 5, "b": 4, "c": 5}), {'a': 5, 'c': 5, 'b': 4})

    def test_get_sorted_dict_with_11_keys(self):
        self.assertEqual(DataSet.get_sorted_dict({"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "h": 7, "t": 8, "k": 9, "o": 10, "l": 11}),
                         {'l': 11, 'o': 10, 'k': 9, 't': 8, 'h': 7, 'f': 6, 'e': 5, 'd': 4, 'c': 3, 'b': 2})

    def test_get_sorted_dict_with_11_random_keys(self):
        self.assertEqual(DataSet.get_sorted_dict({"a": 1, "b": 3, "c": 5, "d": 2, "e": 8, "f": 4, "h": 9, "t": 10, "k": 6, "o": 7, "l": 11}),
                         {'l': 11, 't': 10, 'h': 9, 'e': 8, 'o': 7, 'k': 6, 'c': 5, 'f': 4, 'b': 3, 'd': 2})

    def test_get_percents_from_zero(self):
        self.assertEqual(Report.get_percents(0), "0%")

    def test_get_percents_from_one(self):
        self.assertEqual(Report.get_percents(1), "100%")

    def test_get_percents_from_half(self):
        self.assertEqual(Report.get_percents(0.5), "50.0%")

    def test_get_percents_with_float_percents(self):
        self.assertEqual(Report.get_percents(0.753), '75.3%')

    def test_get_percents_with_super_float_percents(self):
        self.assertEqual(Report.get_percents(0.7001), '70.01%')

    def test_get_percents_with_round_super_float_percents(self):
        self.assertEqual(Report.get_percents(0.70015), '70.02%')

    def test_get_table_rows_with_table_from_one_elem(self):
        self.assertEqual(Report.get_table_rows([[1]]), [[1]])

    def test_get_table_rows_with_2_x_2(self):
        self.assertEqual(Report.get_table_rows([[1, 1], [2, 2]]), [[1, 2], [1, 2]])

    def test_get_table_rows_with_3_x_3(self):
        self.assertEqual(Report.get_table_rows([[1, 2, 3], [1, 2, 3], [1, 2, 3]]), [[1, 1, 1], [2, 2, 2], [3, 3, 3]])

    def test_get_table_rows_with_3_x_3_with_number_in_the_corner(self):
        self.assertEqual(Report.get_table_rows([[1, 2, 3], [1, 2, 3], [1, 2, 10]]), [[1, 1, 1], [2, 2, 2], [3, 3, 10]])