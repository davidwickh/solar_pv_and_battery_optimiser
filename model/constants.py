from aenum import Constant

# Column Names
SOLAR_IRRADIANCE = "solar_irradiance (W/m)"
DATE_TIME = "date_time"
ENERGY_DEMAND = "consumption_kwh"
SOLAR_GENERATION = "solar_generation"


class OptimisationObjectives(Constant):
    MINIMISE_BATTERY_CAP = "minimise_battery_cap"
    MINIMISE_BATTERY_AND_SOLAR_COST = "minimise_battery_and_solar_cost"
