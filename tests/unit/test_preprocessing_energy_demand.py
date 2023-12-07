"""
File containing tests for pre-processing the energy demand data
"""
import numpy as np
import pandas as pd
import pytest

from model.constants import DATE_TIME, ENERGY_DEMAND
from model.inputs.pre_processing import FilterNonHalfHourlyData


class TestPreProcessingEnergyDemand:
    """
    Class containing tests for pre-processing the energy demand data
    """

    @pytest.fixture(scope="class")
    def dummy_energy_demand_data(self) -> pd.DataFrame:
        """
        Creates dummy energy demand data. The raw data should have some data points that are not on the half hour.
        :return: Dummy energy demand data
        """
        df = pd.DataFrame(
            {
                DATE_TIME: pd.date_range(
                    start="2014-05-10 00:00", end="2016-09-01 23:30", freq="30min"
                ),
                ENERGY_DEMAND: np.random.uniform(low=0, high=1, size=40608),
            }
        )
        # Add some data points that are not on the half hour
        df.loc[0, DATE_TIME] = pd.to_datetime("2014-05-10 00:15")
        df.loc[1, DATE_TIME] = pd.to_datetime("2014-05-10 00:45")

        return df

    def test_filtering_non_half_hourly_data(
        self, dummy_energy_demand_data: pd.DataFrame
    ) -> None:
        """
        The FilterNonHalfHourlyData class should filter out any data points that are not on the half hour.

        The two data points that are not on the half hour should be removed.
        :param dummy_energy_demand_data: Dummy energy demand data
        :return: None
        """
        # Arrange
        # Act
        filtered_data = FilterNonHalfHourlyData().pre_process(dummy_energy_demand_data)
        # Assert
        assert len(filtered_data) == 40606
        assert filtered_data[DATE_TIME].iloc[0] == pd.to_datetime("2014-05-10 01:00")
        assert filtered_data[DATE_TIME].iloc[1] == pd.to_datetime("2014-05-10 01:30")
        assert filtered_data[DATE_TIME].iloc[-1] == pd.to_datetime("2016-09-01 23:30")
