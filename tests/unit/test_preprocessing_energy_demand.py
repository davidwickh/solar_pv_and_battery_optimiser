"""
File containing tests for pre-processing the energy demand data
"""
import numpy as np
import pandas as pd
import pytest

from model.constants import DATE_TIME, ENERGY_DEMAND
from model.inputs.pre_processing import PreProcessEnergyDemand


class TestPreProcessingEnergyDemand:
    """
    Class containing tests for pre-processing the energy demand data. The tests are:
    - Filtering out non-half-hourly data
    - Removing duplicate timestamps by
        - If the values are the same then just take the first value
        - If the values are different then take the average of the values
    """

    @pytest.fixture(scope="class")
    def dummy_energy_demand_data_non_hh_timestamp(self) -> pd.DataFrame:
        """
        Creates dummy energy demand data with some values that are not on the half hour.
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

    @pytest.fixture(scope="class")
    def dummy_energy_demand_data_duplicate_timestamps_same_values(self) -> pd.DataFrame:
        """
        Creates dummy energy demand data with duplicate timestamps and the same values.
        """
        df = pd.DataFrame(
            {
                DATE_TIME: pd.date_range(
                    start="2014-05-10 00:00",
                    end="2014-05-10 23:30",
                    freq="30min",
                ),
                ENERGY_DEMAND: np.ones(48),
            }
        )
        # Add some duplicate timestamps
        duplicate_timestamps = pd.DataFrame(
            {
                DATE_TIME: pd.date_range(
                    start="2014-05-10 00:00",
                    end="2014-05-10 01:00",
                    freq="30min",
                ),
                ENERGY_DEMAND: [1, 1, 1],
            }
        )
        df = pd.concat([df, duplicate_timestamps])
        return df

    @pytest.fixture(scope="class")
    def dummy_energy_demand_data_duplicate_timestamps_diff_values(self) -> pd.DataFrame:
        """
        Creates dummy energy demand data with duplicate timestamps and different.
        """
        df = pd.DataFrame(
            {
                DATE_TIME: pd.date_range(
                    start="2014-05-10 00:00",
                    end="2014-05-10 23:30",
                    freq="30min",
                ),
                ENERGY_DEMAND: np.ones(48),
            }
        )
        # Add some duplicate timestamps
        duplicate_timestamps = pd.DataFrame(
            {
                DATE_TIME: pd.date_range(
                    start="2014-05-10 00:00",
                    end="2014-05-10 01:00",
                    freq="30min",
                ),
                ENERGY_DEMAND: [2, 3, 4],
            }
        )
        df = pd.concat([df, duplicate_timestamps])
        return df

    def test_filtering_non_half_hourly_data(
        self, dummy_energy_demand_data_non_hh_timestamp
    ) -> None:
        """
        The FilterNonHalfHourlyData class should filter out any data points that are not on the half hour.

        The two data points that are not on the half hour should be removed.
        :param dummy_energy_demand_data: Dummy energy demand data
        :return: None
        """
        # Arrange
        # Act
        filtered_data = PreProcessEnergyDemand().pre_process(
            dummy_energy_demand_data_non_hh_timestamp
        )
        # Assert
        assert len(filtered_data) == 40606
        assert filtered_data[DATE_TIME].iloc[0] == pd.to_datetime("2014-05-10 01:00")
        assert filtered_data[DATE_TIME].iloc[1] == pd.to_datetime("2014-05-10 01:30")
        assert filtered_data[DATE_TIME].iloc[-1] == pd.to_datetime("2016-09-01 23:30")

    def test_removing_duplicate_timestamps_same_values(
        self, dummy_energy_demand_data_duplicate_timestamps_same_values
    ) -> None:
        """
        The RemoveDuplicateTimestamps class should remove duplicate timestamps where the values are the same.

        The duplicate timestamps should be removed.
        :param dummy_energy_demand_data_duplicate_timestamps_same_values: Dummy energy demand data
        :return: None
        """
        # Arrange
        # Act
        filtered_data = PreProcessEnergyDemand().pre_process(
            dummy_energy_demand_data_duplicate_timestamps_same_values
        )
        # Assert
        assert len(filtered_data) == 48
        assert (
            filtered_data.loc[
                filtered_data[DATE_TIME] == pd.to_datetime("2014-05-10 00:00"),
                ENERGY_DEMAND,
            ].iloc[0]
            == 1
        )
        assert (
            filtered_data.loc[
                filtered_data[DATE_TIME] == pd.to_datetime("2014-05-10 00:30"),
                ENERGY_DEMAND,
            ].iloc[0]
            == 1
        )
        assert (
            filtered_data.loc[
                filtered_data[DATE_TIME] == pd.to_datetime("2014-05-10 01:00"),
                ENERGY_DEMAND,
            ].iloc[0]
            == 1
        )

    def test_removing_duplicate_timestamps_diff_values(
        self, dummy_energy_demand_data_duplicate_timestamps_diff_values
    ) -> None:
        """
        The RemoveDuplicateTimestamps class should calculate the average duplicate timestamps where the values are the
        different.

        The duplicate timestamps should be removed.
        :param dummy_energy_demand_data_duplicate_timestamps_diff_values: Dummy energy demand data
        :return: None
        """
        # Arrange
        # Act
        filtered_data = PreProcessEnergyDemand().pre_process(
            dummy_energy_demand_data_duplicate_timestamps_diff_values
        )
        # Assert
        assert len(filtered_data) == 48
        assert (
            filtered_data.loc[
                filtered_data[DATE_TIME] == pd.to_datetime("2014-05-10 00:00"),
                ENERGY_DEMAND,
            ].iloc[0]
            == 1.5
        )
        assert (
            filtered_data.loc[
                filtered_data[DATE_TIME] == pd.to_datetime("2014-05-10 00:30"),
                ENERGY_DEMAND,
            ].iloc[0]
            == 2
        )
        assert (
            filtered_data.loc[
                filtered_data[DATE_TIME] == pd.to_datetime("2014-05-10 01:00"),
                ENERGY_DEMAND,
            ].iloc[0]
            == 2.5
        )
