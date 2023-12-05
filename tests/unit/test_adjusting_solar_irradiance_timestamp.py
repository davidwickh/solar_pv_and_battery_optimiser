"""
This file contains tests associated with adjusting the solar irradiance timestamps. As seen in the
MatchTimeStampsPreProcessor class.
"""
import numpy as np
import pandas as pd
import pytest

from model.constants import DATE_TIME, ENERGY_DEMAND, SOLAR_IRRADIANCE
from model.inputs.pre_processing import MatchTimeStampsPreProcessor


class TestAdjustingSolarIrradianceTimestamp:
    """
    Class containing tests associated with adjusting the solar irradiance timestamps.
    """

    @pytest.fixture(scope="class")
    def dummy_solar_irradiance_data(self) -> pd.DataFrame:
        """
        Creates dummy solar irradiance data.
        :return: Dummy solar irradiance data
        """
        return pd.DataFrame(
            {
                DATE_TIME: pd.date_range(
                    start="2020-01-01 00:00", end="2020-12-31 23:00", freq="H"
                ),
                SOLAR_IRRADIANCE: np.random.uniform(low=0, high=1, size=8784),
            }
        )

    @pytest.fixture(scope="class")
    def dummy_energy_demand_data(self) -> pd.DataFrame:
        """
        Creates dummy energy demand data.
        :return: Dummy energy demand data
        """
        return pd.DataFrame(
            {
                DATE_TIME: pd.date_range(
                    start="2014-05-10 00:00", end="2016-09-01 23:30", freq="30min"
                ),
                ENERGY_DEMAND: np.random.uniform(low=0, high=1, size=40608),
            }
        )

    def test_adjusting_solar_irradiance_timestamp(
        self,
        dummy_solar_irradiance_data: pd.DataFrame,
        dummy_energy_demand_data: pd.DataFrame,
    ) -> None:
        """
        Tests that the solar irradiance timestamps are adjusted correctly. The time stamps of the solar irradiance data
        should be adjusted (and repeated) to match the timestamps of the energy demand data.
        :param dummy_solar_irradiance_data: Dummy solar irradiance data
        :param dummy_energy_demand_data: Dummy energy demand data
        :return: None
        """
        # Arrange
        match_time_stamps_pre_processor = MatchTimeStampsPreProcessor(
            dummy_energy_demand_data
        )

        # Act
        adjusted_solar_irradiance_data = match_time_stamps_pre_processor.pre_process(
            dummy_solar_irradiance_data
        )

        # Assert
        pd.testing.assert_series_equal(
            adjusted_solar_irradiance_data[DATE_TIME],
            dummy_energy_demand_data[DATE_TIME],
        )
