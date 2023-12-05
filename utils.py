"""
Util functions used throughout the project.
"""
from dataclasses import dataclass, field

import pandas as pd

from model.constants import DATE_TIME


def setup_logger(logging_level: str = "INFO"):
    """
    Sets up the logger for the project.

    Args:
        logging_level (str): The logging level to use.
    """
    import logging

    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%m-%d %H:%M:%S",
    )


@dataclass
class DateTimeToNumeric:
    """
    Dataclass that converts a datetime object to a numeric value.
    """

    datetime_column: pd.Series
    mapping: dict

    @classmethod
    def create(cls, datetime_column: pd.Series) -> "DateTimeToNumeric":
        """
        Creates a DateTimeToNumeric object. Take a datetime column and created a mapping between the datetime and
        numeric values.
        :param datetime_column:
        :return:
        """
        mapping = {datetime: i for i, datetime in enumerate(datetime_column.unique())}
        return cls(datetime_column, mapping)

    def convert_to_numeric(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Converts the datetime column to a numeric column.
        :return:
        """
        return data[DATE_TIME].map(self.mapping)

    def convert_to_datetime(
        self, data: pd.DataFrame, numeric_column: pd.Series
    ) -> pd.DataFrame:
        """
        Converts the numeric column to a datetime column.
        :param numeric_column:
        :return:
        """
        return data[numeric_column].map({v: k for k, v in self.mapping.items()})
