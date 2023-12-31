"""
Constants used in the model
"""
from aenum import Constant

# Column Names
SOLAR_IRRADIANCE = "solar_irradiance (W/m)"
DATE_TIME = "date_time"
ENERGY_DEMAND = "consumption_kwh"
SOLAR_GENERATION = "solar_generation"
Wh_TO_KWh = 1 / 1000  # pylint: disable=invalid-name


class OptimisationObjectives(Constant):  # pylint: disable=too-few-public-methods
    """
    Enum containing the different optimisation objectives
    """

    MINIMISE_BATTERY_CAP = "minimise_battery_cap"
    MINIMISE_BATTERY_AND_SOLAR_COST = "minimise_battery_and_solar_cost"
