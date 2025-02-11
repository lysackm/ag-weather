# test suite for process_dat.py
import unittest
import pandas as pd
import process_dat
import datetime


class TestApplyLowerThresholds(unittest.TestCase):
    def setUp(self) -> None:
        self.df = pd.DataFrame(data={'col1': range(5),
                                     'col2': range(5, 10),
                                     "col3": range(-5, 5, 2),
                                     "col4": [0, "string", 2, None, 7]})

    def test_use_lower_threshold_removes_below_threshold(self):
        lower_thresholds = {"col1": 2}
        df = process_dat.apply_lower_thresholds(self.df, lower_thresholds, "test_id")
        self.assertEqual(list(df["col1"].values), ["NaN", "NaN", 2, 3, 4])

    def test_use_lower_threshold_replaces_with_NaN(self):
        lower_thresholds = {"col1": 2}
        df = process_dat.apply_lower_thresholds(self.df, lower_thresholds, "test_id")
        self.assertEqual(df["col1"][0], "NaN")
        self.assertEqual(df["col1"][1], "NaN")

    def test_use_lower_threshold_does_not_replace_threshold(self):
        lower_thresholds = {"col1": 2}
        df = process_dat.apply_lower_thresholds(self.df, lower_thresholds, "test_id")
        self.assertEqual(df["col1"][2], 2)

    def test_use_lower_threshold_with_threshold_below_lowest_value(self):
        lower_thresholds = {"col2": 1}
        df = process_dat.apply_lower_thresholds(self.df, lower_thresholds, "test_id")
        self.assertEqual(list(df["col2"].values), [5, 6, 7, 8, 9])

    def test_use_lower_threshold_negative_threshold(self):
        lower_thresholds = {"col3": -2}
        df = process_dat.apply_lower_thresholds(self.df, lower_thresholds, "test_id")
        self.assertEqual(df["col3"][0], "NaN")
        self.assertEqual(df["col3"][1], "NaN")
        self.assertEqual(df["col3"][2], -1)

    def test_use_lower_threshold_applied_to_several_columns(self):
        lower_thresholds = {"col1": 1, "col2": 6, "col3": -4}
        df = process_dat.apply_lower_thresholds(self.df, lower_thresholds, "test_id")
        self.assertEqual(list(df["col1"].values), ["NaN", 1, 2, 3, 4])
        self.assertEqual(list(df["col2"].values), ["NaN", 6, 7, 8, 9])
        self.assertEqual(list(df["col3"].values), ["NaN", -3, -1, 1, 3])

    def test_use_lower_threshold_use_incorrect_column(self):
        lower_thresholds = {"invalid_column": 0}
        with self.assertLogs(process_dat.logger.logger, level="WARNING"):
            process_dat.apply_lower_thresholds(self.df, lower_thresholds, "test_id")

    def test_use_lower_threshold_incorrect_lower_threshold_type(self):
        lower_thresholds = 3
        with self.assertLogs(process_dat.logger.logger, level="WARNING"):
            df = process_dat.apply_lower_thresholds(self.df, lower_thresholds, "test_id")

        self.assertEqual(list(df["col1"].values), [0, 1, 2, 3, 4])
        self.assertEqual(list(df["col2"].values), [5, 6, 7, 8, 9])
        self.assertEqual(list(df["col3"].values), [-5, -3, -1, 1, 3])

    def test_use_lower_threshold_skip_non_numerical_thresholds(self):
        lower_thresholds = {"col4": 1}
        df = process_dat.apply_lower_thresholds(self.df, lower_thresholds, "test_id")
        self.assertEqual(list(df["col4"].values), ["NaN", "string", 2, None, 7])

    def test_use_lower_threshold_substitution_value(self):
        lower_thresholds = {"col1": 2}
        df = process_dat.apply_lower_thresholds(self.df, lower_thresholds, "test_id", substitution="test")
        self.assertEqual(list(df["col1"].values), ["test", "test", 2, 3, 4])


class TestApplyUpperThresholds(unittest.TestCase):
    def setUp(self) -> None:
        self.df = pd.DataFrame(data={'col1': range(5),
                                     'col2': range(5, 10),
                                     "col3": range(-5, 5, 2),
                                     "col4": [0, "string", 2, None, 7]})

    def test_use_upper_threshold_removes_below_threshold(self):
        upper_thresholds = {"col1": 2}
        df = process_dat.apply_upper_thresholds(self.df, upper_thresholds, "test_id")
        self.assertEqual(list(df["col1"].values), [0, 1, 2, "NaN", "NaN"])

    def test_use_upper_threshold_replaces_with_NaN(self):
        upper_thresholds = {"col1": 2}
        df = process_dat.apply_upper_thresholds(self.df, upper_thresholds, "test_id")
        self.assertEqual(df["col1"][3], "NaN")
        self.assertEqual(df["col1"][4], "NaN")

    def test_use_upper_threshold_does_not_replace_threshold(self):
        upper_thresholds = {"col1": 2}
        df = process_dat.apply_upper_thresholds(self.df, upper_thresholds, "test_id")
        self.assertEqual(df["col1"][2], 2)

    def test_use_upper_threshold_with_threshold_above_highest_value(self):
        upper_thresholds = {"col2": 20}
        df = process_dat.apply_upper_thresholds(self.df, upper_thresholds, "test_id")
        self.assertEqual(list(df["col2"].values), [5, 6, 7, 8, 9])

    def test_use_upper_threshold_negative_threshold(self):
        upper_thresholds = {"col3": -2}
        df = process_dat.apply_upper_thresholds(self.df, upper_thresholds, "test_id")
        self.assertEqual(list(df["col3"].values), [-5, -3, "NaN", "NaN", "NaN"])

    def test_use_upper_threshold_applied_to_several_columns(self):
        upper_thresholds = {"col1": 3, "col2": 8, "col3": 1}
        df = process_dat.apply_upper_thresholds(self.df, upper_thresholds, "test_id")
        self.assertEqual(list(df["col1"].values), [0, 1, 2, 3, "NaN"])
        self.assertEqual(list(df["col2"].values), [5, 6, 7, 8, "NaN"])
        self.assertEqual(list(df["col3"].values), [-5, -3, -1, 1, "NaN"])

    def test_use_upper_threshold_use_incorrect_column(self):
        upper_thresholds = {"invalid_column": 0}
        with self.assertLogs(process_dat.logger.logger, level="WARNING"):
            process_dat.apply_upper_thresholds(self.df, upper_thresholds, "test_id")

    def test_use_upper_threshold_incorrect_upper_threshold_type(self):
        upper_thresholds = 3
        with self.assertLogs(process_dat.logger.logger, level="WARNING"):
            df = process_dat.apply_upper_thresholds(self.df, upper_thresholds, "test_id")

        self.assertEqual(list(df["col1"].values), [0, 1, 2, 3, 4])
        self.assertEqual(list(df["col2"].values), [5, 6, 7, 8, 9])
        self.assertEqual(list(df["col3"].values), [-5, -3, -1, 1, 3])

    def test_use_upper_threshold_skip_non_numerical_thresholds(self):
        upper_thresholds = {"col4": 4}
        df = process_dat.apply_upper_thresholds(self.df, upper_thresholds, "test_id")
        self.assertEqual(list(df["col4"].values), [0, "string", 2, None, "NaN"])

    def test_use_upper_threshold_substitution_value(self):
        upper_thresholds = {"col1": 2}
        df = process_dat.apply_upper_thresholds(self.df, upper_thresholds, "test_id", substitution="test")
        self.assertEqual(list(df["col1"].values), [0, 1, 2, "test", "test"])


class TestApplyTransformations(unittest.TestCase):
    def setUp(self) -> None:
        self.df = pd.DataFrame(data={'col1': range(5),
                                     'col2': range(5, 10),
                                     "col3": range(-5, 5, 2),
                                     "col4": [0, "string", 2, None, 7]})

    def test_apply_transformation_str_transformation(self):
        transformations = {"col1": "test", "col2": "test2"}
        df = process_dat.apply_transformations(self.df, transformations, "test_id")
        col1 = ["test"] * 5
        col2 = ["test2"] * 5
        self.assertEqual(list(df["col1"].values), col1)
        self.assertEqual(list(df["col2"].values), col2)

    def test_apply_transformation_numeric_transformation_on_numeric_column(self):
        transformations = {"col1": 2, "col2": 3.0}
        df = process_dat.apply_transformations(self.df, transformations, "test_id")
        self.assertEqual(list(df["col1"].values), [0, 2, 4, 6, 8])
        self.assertEqual(list(df["col2"].values), [15, 18, 21, 24, 27])

    def test_apply_transformation_numeric_transformation_on_mixed_type_column(self):
        transformations = {"col4": 2, "col1": 2}
        df = process_dat.apply_transformations(self.df, transformations, "test_id")
        self.assertEqual(list(df["col1"].values), [0, 2, 4, 6, 8])
        self.assertEqual(list(df["col4"].values), [0, "string", 4, None, 14])

    def test_apply_transformation_numeric_transformation_on_mixed_type_column_logged(self):
        transformations = {"col4": 2}
        with self.assertLogs(process_dat.logger.logger, level="WARNING"):
            df = process_dat.apply_transformations(self.df, transformations, "test_id")
        self.assertEqual(list(df["col4"].values), [0, "string", 4, None, 14])

    def test_apply_transformation_invalid_column_logged(self):
        transformations = {"invalid_column": 2}
        with self.assertLogs(process_dat.logger.logger, level="ERROR"):
            process_dat.apply_transformations(self.df, transformations, "test_id")

    def test_apply_transformation_invalid_column_continued(self):
        transformations = {"col1": 2, "invalid_column": 2, "col2": 3}
        with self.assertLogs(process_dat.logger.logger, level="ERROR"):
            df = process_dat.apply_transformations(self.df, transformations, "test_id")
        self.assertEqual(list(df["col1"].values), [0, 2, 4, 6, 8])
        self.assertEqual(list(df["col2"].values), [15, 18, 21, 24, 27])

    def test_apply_transformation_unimplemented_type_logged(self):
        transformations = {"col1": []}
        with self.assertLogs(process_dat.logger.logger, level="WARNING"):
            process_dat.apply_transformations(self.df, transformations, "test_id")

    def test_apply_transformation_unimplemented_type_continue(self):
        transformations = {"col1": [], "col2": 2}
        df = process_dat.apply_transformations(self.df, transformations, "test_id")
        self.assertEqual(list(df["col1"].values), [0, 1, 2, 3, 4])
        self.assertEqual(list(df["col2"].values), [10, 12, 14, 16, 18])


class TestFormatTimeColumns(unittest.TestCase):
    def setUp(self) -> None:
        base = datetime.datetime(2000, 1, 1)
        self.df = pd.DataFrame(data={"time": [base + datetime.timedelta(days=x) for x in range(4)]})
        self.timestamp = self.df["time"]

    def test_format_time_column_format_date_column_from_regex(self):
        df_metadata_dict = {"date_format": "%Y/%m/%d"}
        column = "formatted_date"
        format_key = "date_format"
        process_dat.format_time_column(self.df, self.timestamp, df_metadata_dict, column, format_key)
        expected_output = ["2000/01/01", "2000/01/02", "2000/01/03", "2000/01/04"]
        self.assertEqual(list(self.df["formatted_date"].values), expected_output)

    def test_format_time_column_format_time_column(self):
        df_metadata_dict = {}
        column = "TIME"
        format_key = "date_format"
        process_dat.format_time_column(self.df, self.timestamp, df_metadata_dict, column, format_key)
        expected_output = [datetime.time(0, 0)] * 4
        self.assertEqual(list(self.df["TIME"].values), expected_output)

    def test_format_time_column_format_date_column(self):
        df_metadata_dict = {}
        column = "DATE"
        format_key = "date_format"
        process_dat.format_time_column(self.df, self.timestamp, df_metadata_dict, column, format_key)
        expected_output = [datetime.date(2000, 1, 1), datetime.date(2000, 1, 2), datetime.date(2000, 1, 3), datetime.date(2000, 1, 4)]
        self.assertEqual(list(self.df["DATE"].values), expected_output)


class TestDateProcessing(unittest.TestCase):
    def setUp(self) -> None:
        self.df = pd.DataFrame(data={"TMSTAMP": ["2024-04-01 01:01:00", "2024-04-02 02:02:00", "2024-04-03 03:03:00", "2024-04-04 04:04:00"]})

    def test_date_processing_creates_columns(self):
        df_metadata = {
            "date_format": "%Y/%m/%d",
            "time_format": "%H:%M:%S",
            "timestamp_format": "%Y/%m/%d %H:%M:%S"
        }
        df = process_dat.date_processing(self.df, df_metadata)
        assert({"DATE", "TMSTAMP", "TIME"} <= set(df.columns))

    def test_date_processing_with_formatting(self):
        df_metadata = {
            "date_format": "%Y/%m/%d",
            "time_format": "%H:%M:%S",
            "timestamp_format": "%Y/%m/%d %H:%M:%S"
        }

        df = process_dat.date_processing(self.df, df_metadata)
        formatted_date = ["2024/04/01", "2024/04/02", "2024/04/03", "2024/04/04"]
        formatted_time = ["01:01:00", "02:02:00", "03:03:00", "04:04:00"]
        formatted_tmstamp = ["2024/04/01 01:01:00", "2024/04/02 02:02:00", "2024/04/03 03:03:00", "2024/04/04 04:04:00"]
        self.assertEqual(list(df["DATE"].values), formatted_date)
        self.assertEqual(list(df["TIME"].values), formatted_time)
        self.assertEqual(list(df["TMSTAMP"].values), formatted_tmstamp)

    def test_date_processing_empty_metadata_adds_columns(self):
        df = process_dat.date_processing(self.df)
        assert({"DATE", "TMSTAMP", "TIME"} <= set(df.columns))

    def test_date_processing_empty_metadata_doesnt_format(self):
        df = process_dat.date_processing(self.df)
        unformatted_date = [datetime.date(2024, 4, 1), datetime.date(2024, 4, 2), datetime.date(2024, 4, 3), datetime.date(2024, 4, 4)]
        unformatted_time = [datetime.time(1, 1), datetime.time(2, 2), datetime.time(3, 3), datetime.time(4, 4)]
        unformatted_tmstamp = ["2024-04-01 01:01:00", "2024-04-02 02:02:00", "2024-04-03 03:03:00", "2024-04-04 04:04:00"]
        self.assertEqual(list(df["DATE"].values), unformatted_date)
        self.assertEqual(list(df["TIME"].values), unformatted_time)
        self.assertEqual(list(df["TMSTAMP"].values), unformatted_tmstamp)

    @unittest.skip("Safety net has not been created. Assumed that TMSTAMP will be a all valid dates")
    def test_date_processing_incorrect_date_format(self):
        self.df = pd.DataFrame(data={"TMSTAMP": ["invalid date", "2024-04-02 02:02:00", "2024-04-03 03:03:00", "2024-04-04 04:04:00"]})
        df_metadata = {
            "date_format": "%Y/%m/%d",
            "time_format": "%H:%M:%S",
            "timestamp_format": "%Y/%m/%d %H:%M:%S"
        }

        df = process_dat.date_processing(self.df, df_metadata)
        formatted_date = ["2024/04/01", "2024/04/02", "2024/04/03", "2024/04/04"]
        formatted_time = ["01:01:00", "02:02:00", "03:03:00", "04:04:00"]
        formatted_tmstamp = ["2024/04/01 01:01:00", "2024/04/02 02:02:00", "2024/04/03 03:03:00", "2024/04/04 04:04:00"]
        assert(list(df["DATE"].values) == formatted_date)
        self.assertEqual(list(df["TIME"].values), formatted_time)
        self.assertEqual(list(df["TMSTAMP"].values), formatted_tmstamp)


class TestDfDataOperations(unittest.TestCase):
    def setUp(self) -> None:
        self.df = pd.DataFrame(data={'col1': range(5)})
        self.df_metadata = {
            "id": "test_id"
        }

    def test_df_data_operations_applies_operations(self):
        self.df_metadata["lower_thresholds"] = {"col1": 1}
        self.df_metadata["upper_thresholds"] = {"col1": 3}
        self.df_metadata["transformations"] = {"col1": 2}

        df = process_dat.df_data_operations(self.df, self.df_metadata)
        self.assertEqual(list(df["col1"].values), ["NaN", 2, 4, 6, "NaN"])

    def test_df_data_operations_no_operations(self):
        df = process_dat.df_data_operations(self.df, self.df_metadata)
        self.assertEqual(list(df["col1"].values), [0, 1, 2, 3, 4])


class TestCopyIndividualStnData(unittest.TestCase):
    def setUp(self) -> None:
        str("do something")
        # TODO, make integration tests for processing individual stations


class TestInvertDict(unittest.TestCase):
    def test_invert_dict(self):
        dictionary = {1: 2}
        dictionary = process_dat.invert_dict(dictionary)
        self.assertEqual(dictionary, {2: 1})


class TestProcessRow(unittest.TestCase):
    def test_process_row_float_truncated(self):
        format_str = "{:.1f}"
        value = 2.3412
        value = process_dat.process_row(value, format_str)
        self.assertEqual(value, "2.3")

    def test_process_row_float_trailing_zeros(self):
        format_str = "{:.2f}"
        value = float(2)
        value = process_dat.process_row(value, format_str)
        self.assertEqual(value, "2.00")

    def test_process_row_float_na_value(self):
        format_str = "{:.1f}"
        value = pd.NA
        value = process_dat.process_row(value, format_str)
        self.assertEqual(value, "")

    def test_process_row_non_float(self):
        format_str = "{:.1f}"
        value = ""
        value = process_dat.process_row(value, format_str)
        self.assertEqual(value, "")

    def test_process_row_leading_space(self):
        format_str = "{:^ .1f}"
        value = float(2)
        value = process_dat.process_row(value, format_str)
        self.assertEqual(value, "")

    @unittest.skip("Safety net has not been created. Convert ints to floats")
    def test_process_row_int_input(self):
        format_str = "{:^ .1f}"
        value = 2
        value = process_dat.process_row(value, format_str)
        self.assertEqual(value, "2.0")


class TestProcessConcatData(unittest.TestCase):
    def setUp(self) -> None:
        self.df = {

        }


if __name__ == "__main__":
    unittest.main()
