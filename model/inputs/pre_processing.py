"""
This file contains all code associated with pre-processing the input data.
"""

import pandas as pd

from model.constants import DATE_TIME, SOLAR_IRRADIANCE


class PreProcessorBase:
    """
    Pre-processor that converts the timestamp column to a datetime object.
    """

    def __init__(self):
        pass

    def pre_process(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Converts the timestamp column to a datetime object.
        :param data: Input data to pre-process
        :return: Pre-processed data
        """
        data[DATE_TIME] = pd.to_datetime(data[DATE_TIME], format="mixed")
        return data


class FilterNonHalfHourlyData(PreProcessorBase):
    """
    Pre-processor that filters out non-half-hourly data.

    NOTE - mainly intended for user on the energy demand data.
    """

    def __init__(self):
        super().__init__()

    def pre_process(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Filters out non-half-hourly data.
        :param data: Input data to pre-process
        :return: Pre-processed data
        """
        data = super().pre_process(data)
        return data[data[DATE_TIME].dt.minute.isin([0, 30])]


class MatchTimeStampsPreProcessor(PreProcessorBase):
    """
    Pre-processor that matches the timestamps of the solar irradiance and energy demand data.

    NOTE - mainly intended for use on the solar irradiance data.
    """

    def __init__(self, energy_demand_profile: pd.DataFrame):
        super().__init__()
        self.energy_demand_profile = energy_demand_profile.copy().set_index(DATE_TIME)

    def pre_process(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Matches the timestamps of the solar irradiance and energy demand data.

        This pre-processing consists of two steps:
            - The timestamps of the solar irradiance data are hourly, whereas the timestamps of the energy demand data
                are half-hourly. Therefore, the solar irradiance data is re-sampled to half-hourly.
            - The timestamps of the solar irradiance is not in the same year as the energy demand data. Furthermore,
                the solar irradiance data is only for one year, whereas the energy demand data is for multiple years.
                Therefore, the solar irradiance data is shifted and repeated to match the timestamps of the energy
                demand data.
        :param data: Input data to pre-process
        :return: Pre-processed data
        """
        # Convert the timestamp column to a datetime object
        data_with_converted_timestamp = super().pre_process(data)

        data_with_converted_timestamp.set_index(DATE_TIME, inplace=True)
        orginal_columns = data_with_converted_timestamp.columns
        # re-sample the solar irradiance data to half-hourly
        data_with_resampled_timestamp = data_with_converted_timestamp.resample(
            "30min"
        ).bfill()
        # Need to add the very last 30 minutes of the year to the end of the data
        new_timestamp = data_with_resampled_timestamp.index[-1] + pd.Timedelta(
            minutes=30
        )
        last_value = data_with_resampled_timestamp.iloc[-1][SOLAR_IRRADIANCE]
        new_row = pd.DataFrame({SOLAR_IRRADIANCE: [last_value]}, index=[new_timestamp])
        data_with_resampled_timestamp = pd.concat(
            [data_with_resampled_timestamp, new_row]
        )

        # Get the years of the energy demand data and the year of the solar irradiance data
        energy_demand_years = self.energy_demand_profile.index.year.unique()

        # Shift and repeat the solar irradiance data to match the energy demand data
        shifted_and_repeated_solar_irradiance_list = []
        for year in energy_demand_years:
            # Change the year of the solar irradiance data to match the year
            shifted_solar_irradiance = data_with_resampled_timestamp.copy()
            for row in shifted_solar_irradiance.index:
                try:
                    shifted_solar_irradiance.at[row, DATE_TIME] = row.replace(year=year)
                except ValueError:
                    # If the date does not exist in the year, then it must be a leap year and drop
                    # the 29th of February
                    if row.month == 2 and row.day == 29:
                        shifted_solar_irradiance.drop(row, inplace=True)
                    else:
                        raise ValueError(
                            f"Unknown error occurred when changing the year of the solar irradiance data to {year}"
                        )
            # replace the index with the datetime column
            shifted_solar_irradiance.set_index(DATE_TIME, inplace=True)
            shifted_and_repeated_solar_irradiance_list.append(shifted_solar_irradiance)

        shifted_and_repeated_solar_irradiance = pd.concat(
            shifted_and_repeated_solar_irradiance_list
        )

        # merge the solar irradiance data with the energy demand data
        shifted_and_repeated_solar_irradiance = self.energy_demand_profile.merge(
            shifted_and_repeated_solar_irradiance,
            left_index=True,
            right_index=True,
            how="left",
        )
        # If there are any missing values raise an error
        if shifted_and_repeated_solar_irradiance.isna().values.any():
            raise ValueError(
                "There are missing values in the energy demand profile after merging the solar irradiance data"
            )
        # Drop the consumption column
        shifted_and_repeated_solar_irradiance = shifted_and_repeated_solar_irradiance[
            orginal_columns
        ]
        # Reset the index
        shifted_and_repeated_solar_irradiance.reset_index(inplace=True)

        return shifted_and_repeated_solar_irradiance
