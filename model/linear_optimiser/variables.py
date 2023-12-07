"""
File containing all the variables for the linear optimiser
"""
import logging
from dataclasses import dataclass, field
from typing import Union

import pulp as pl

from model.constants import OptimisationObjectives

logger = logging.getLogger(__name__)


@dataclass
class OptimiserVariables:
    """
    Class to store the variables for the optimiser
    """
    renewable_electricity_to_house: pl.LpVariable = field(default_factory=pl.LpVariable, init=False)
    renewable_electricity_to_battery: pl.LpVariable = field(default_factory=pl.LpVariable, init=False)
    battery_electricity_to_house: pl.LpVariable = field(default_factory=pl.LpVariable, init=False)
    battery_state_of_charge: pl.LpVariable = field(default_factory=pl.LpVariable, init=False)
    battery_capacity: pl.LpVariable = field(default_factory=pl.LpVariable, init=False)
    solar_size: Union[float, pl.LpVariable] = field(default_factory=pl.LpVariable, init=False)

    @classmethod
    def create_variables(
            cls,
            time_slices: range,
            optimisation_objective: OptimisationObjectives,
            solar_size: float = None,
    ) -> "OptimiserVariables":
        """
        Function to create the variables for the optimiser.
        :param time_slices: Time slices to optimise over
        :param optimisation_objective: Optimisation objective
        :param solar_size: Size of the solar array in m^2
        :return: None
        """
        cls.renewable_electricity_to_house = pl.LpVariable.dicts(
            name="renewable_electricity_to_house",
            indices=time_slices,
            lowBound=0,
            cat="Continuous",
        )
        cls.renewable_electricity_to_battery = pl.LpVariable.dicts(
            name="renewable_electricity_to_battery",
            indices=time_slices,
            lowBound=0,
            cat="Continuous",
        )
        cls.battery_electricity_to_house = pl.LpVariable.dicts(
            name="battery_electricity_to_house",
            indices=time_slices,
            lowBound=0,
            cat="Continuous",
        )
        cls.battery_state_of_charge = pl.LpVariable.dicts(
            name="battery_state_of_charge",
            indices=time_slices,
            lowBound=0,
            cat="Continuous",
        )
        cls.battery_capacity = pl.LpVariable(
            name="battery_capacity",
            lowBound=0,
            cat="Continuous",
        )
        if optimisation_objective == OptimisationObjectives.MINIMISE_BATTERY_AND_SOLAR_COST:
            if solar_size:
                logger.info(f"A solar size of {solar_size} was provided as an input argument, however, the"
                            f" optimisation objective is to minimise battery and solar costs. Therefore, this solar"
                            f" size will be ignored and the solar size will be optimised over.")
            cls.solar_size = pl.LpVariable(
                name="solar_capacity",
                lowBound=0,
                cat="Continuous",
            )
        elif optimisation_objective == OptimisationObjectives.MINIMISE_BATTERY_CAP:
            cls.solar_size = solar_size
        else:
            raise ValueError(
                f"Unknown optimisation objective: {optimisation_objective}"
            )
        return cls
