"""
This file contains all code associated with pre-processing the input data.
"""

import pandas as pd

from model.constants import DATE_TIME, ENERGY_DEMAND, SOLAR_IRRADIANCE


class PreProcessorBase:
    """
    Pre-processor that converts the timestamp column to a datetime object.
    """

    def __init__(self):
        pass

    def pre_process(self, data: pd.DataFrame, column: str) -> pd.DataFrame:
        """
        Base pre-processing method. The following steps are applied:
            - The timestamp column is converted to a datetime object.
            - Duplicate timestamps are processed.
            - Data is re-sampled to half-hourly.
        :param data: Input data to pre-process
        :return: Pre-processed data
        """
        data[DATE_TIME] = pd.to_datetime(data[DATE_TIME], format="%d/%m/%Y %H:%M")
        data = self._process_duplicate_timestamps(data, column=column)

        return data

    @staticmethod
    def _process_duplicate_timestamps(data: pd.DataFrame, column: str) -> pd.DataFrame:
        """
        Method that processes duplicate timestamps in a dataframe. If duplicate timestamps have the same values then
        duplicate rows are dropped. If duplicate timestamps have different values then the average of the values is
        taken.

        :param data: Dataframe to process
        :param column: Column to process
        """
        # Find duplicate rows based on the timestamp column
        duplicate_rows = data[data[DATE_TIME].duplicated(keep=False)]
        if duplicate_rows.empty:
            return data
        # Get the unique timestamps
        unique_timestamps = duplicate_rows[DATE_TIME].unique()
        # Drop the duplicate timestamps from the original dataframe
        data = data[~data[DATE_TIME].isin(unique_timestamps)]

        processed_data = pd.DataFrame(columns=data.columns)
        for timestamp in unique_timestamps:
            # Get the rows with the timestamp
            rows = duplicate_rows[duplicate_rows[DATE_TIME] == timestamp]
            # If there is only one row then add it to the processed data
            if len(rows) == 1:
                processed_data = pd.concat([processed_data, rows], ignore_index=True)
            # If there are multiple rows then process the rows
            else:
                # Get the unique values
                unique_values = rows[column].unique()
                # If there is only one unique value then add the row to the processed data
                if len(unique_values) == 1:
                    if processed_data.empty:
                        processed_data = rows.drop_duplicates()
                    else:
                        processed_data = pd.concat(
                            [processed_data, rows.drop_duplicates()], ignore_index=True
                        )
                # If multiple values, then take the average
                else:
                    rows[column] = rows[column].mean()
                    if processed_data.empty:
                        processed_data = rows.drop_duplicates()
                    else:
                        processed_data = pd.concat(
                            [processed_data, rows.drop_duplicates()], ignore_index=True
                        )

        processed_data = pd.concat([processed_data, data])
        processed_data.sort_values(by=DATE_TIME, inplace=True)
        return processed_data


class PreProcessEnergyDemand(PreProcessorBase):
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
        data = super().pre_process(data, column=ENERGY_DEMAND)
        return data[data[DATE_TIME].dt.minute.isin([0, 30])]


class PreProcessSolarIrradiance(PreProcessorBase):
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
        data_with_converted_timestamp = super().pre_process(
            data, column=SOLAR_IRRADIANCE
        )

        data_with_converted_timestamp = self.fill_in_zero_values(
            data_with_converted_timestamp
        )

        data_with_converted_timestamp = data_with_converted_timestamp.set_index(
            DATE_TIME
        )

        # re-sample the solar irradiance data to half-hourly
        data_with_converted_timestamp = data_with_converted_timestamp.resample(
            "30min"
        ).bfill()

        orginal_columns = data_with_converted_timestamp.columns

        # Need to add the very last 30 minutes of the year to the end of the data
        new_timestamp = data_with_converted_timestamp.index[-1] + pd.Timedelta(
            minutes=30
        )
        last_value = data_with_converted_timestamp.iloc[-1][SOLAR_IRRADIANCE]
        new_row = pd.DataFrame({SOLAR_IRRADIANCE: [last_value]}, index=[new_timestamp])
        data_with_resampled_timestamp = pd.concat(
            [data_with_converted_timestamp, new_row]
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

    @staticmethod
    def fill_in_zero_values(solar_irradiance: pd.DataFrame) -> pd.DataFrame:
        """
        Method to loop through each day, compare the solar irradiance values to the previous day and if the solar
        irradiance values are zero for any time period that the previous day had values, then the solar irradiance
        values are replaced with the previous day's values.
        """
        days = solar_irradiance[DATE_TIME].dt.date.unique()
        # Loop through each day
        for day in days:
            # Get the solar irradiance data for the day
            solar_irradiance_day = solar_irradiance[
                solar_irradiance[DATE_TIME].dt.date == day
            ]
            # Get the previous day
            previous_day = day - pd.Timedelta(days=1)
            # Get the solar irradiance data for the previous day
            solar_irradiance_previous_day = solar_irradiance[
                solar_irradiance[DATE_TIME].dt.date == previous_day
            ]
            if solar_irradiance_previous_day.empty:
                continue
            # Loop through each time period
            for time_period in solar_irradiance_day[DATE_TIME].dt.time.unique():
                # Get the solar irradiance value for the time period
                solar_irradiance_value = solar_irradiance_day[
                    solar_irradiance_day[DATE_TIME].dt.time == time_period
                ][SOLAR_IRRADIANCE].values[0]
                # If the solar irradiance value is zero
                if solar_irradiance_value == 0:
                    # Get the solar irradiance value for the previous day
                    solar_irradiance_previous_day_value = solar_irradiance_previous_day[
                        solar_irradiance_previous_day[DATE_TIME].dt.time == time_period
                    ][SOLAR_IRRADIANCE].values[0]
                    # If the solar irradiance value for the previous day is not zero then replace the value
                    if solar_irradiance_previous_day_value != 0:
                        solar_irradiance.loc[
                            (solar_irradiance[DATE_TIME].dt.date == day)
                            & (solar_irradiance[DATE_TIME].dt.time == time_period),
                            SOLAR_IRRADIANCE,
                        ] = solar_irradiance_previous_day_value
        return solar_irradiance
