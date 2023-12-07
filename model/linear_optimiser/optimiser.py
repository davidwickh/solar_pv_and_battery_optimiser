import logging
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
import pulp as pl
from pulp import LpStatus

from model.constants import ENERGY_DEMAND, SOLAR_IRRADIANCE, OptimisationObjectives
from model.linear_optimiser.variables import OptimiserVariables

logger = logging.getLogger(__name__)


class Optimiser:
    """
    Class containing code associated with the linear optimiser.
    """

    problem: pl.LpProblem = None
    variables: OptimiserVariables

    def __init__(
            self,
            energy_demand: pd.DataFrame,
            solar_irradiance: pd.DataFrame,
            time_slices: range,
            optimisation_objective: OptimisationObjectives,
            solar_size: float = None,
            solar_capex: Optional[float] = None,
            battery_capex: Optional[float] = None,
    ):
        """
        Initialises the optimiser by creating the optimiser variables.
        :param energy_demand: Energy demand profile (kWh)
        :param solar_irradiance: Solar irradiance profile (W/m2)
        :param time_slices: Time slices to optimise over
        :param optimisation_objective: Optimisation objective
        :param solar_size: Size of the solar array in m^2 (only used when optimising the battery size)
        :param solar_capex: Solar capex (£/m2) (only used when optimising the battery and PV costs)
        :param battery_capex: Battery capex (£/kWh) (only used when optimising the battery and PV costs)
        """
        self.energy_demand = energy_demand
        self.solar_irradiance = solar_irradiance
        self.variables = OptimiserVariables.create_variables(
            time_slices=time_slices,
            optimisation_objective=optimisation_objective,
            solar_size=solar_size,
        )
        self.optimisation_objective = optimisation_objective
        self.time_slices = time_slices
        if self.optimisation_objective == OptimisationObjectives.MINIMISE_BATTERY_AND_SOLAR_COST:
            self.solar_capex = solar_capex
            self.battery_capex = battery_capex
        elif self.optimisation_objective == OptimisationObjectives.MINIMISE_BATTERY_CAP:
            self.solar_capex = None
            self.battery_capex = None

    def create_optimisation_problem(
            self,
            battery_initial_capacity: float,
            battery_degradation_rate: float,
            solar_efficiency: Optional[float] = 0.15,
    ) -> None:
        """
        Main entry point to the optimiser. Calls the following functions:
            - define the object function
            - define the constraints
        :param battery_initial_capacity: Initial battery capacity (kWh)
        :param battery_degradation_rate: Battery degradation rate, in (kWh/kWh)
        :param battery_capex: Battery capex (£/kWh)
        :param solar_capex: Solar capex (£/m2)
        :param solar_efficiency: Solar efficiency (%). Default is 15%.
        :return: None
        """
        self._define_problem()
        self._define_objective_function(
            battery_capex=self.battery_capex,
            solar_capex=self.solar_capex,
        )
        # Define the constraints
        for _t in self.time_slices:
            # Solar generation
            solar_generation = (
                    self.solar_irradiance[SOLAR_IRRADIANCE][_t]
                    * self.variables.solar_size
                    * solar_efficiency
                    * 0.5
            )
            # Renewable electricity flow to house and battery must equal renewable generation
            self.problem += (
                    self.variables.renewable_electricity_to_house[_t]
                    + self.variables.renewable_electricity_to_battery[_t]
                    <= solar_generation
            )
            # Electricity demand from house must be met
            self.problem += (
                    self.variables.renewable_electricity_to_house[_t] + self.variables.battery_electricity_to_house[_t]
                    == self.energy_demand.loc[_t, ENERGY_DEMAND]
            )
            # Battery state of charge
            if _t == 0:  # Initial battery state of charge
                self.problem += self.variables.battery_state_of_charge[_t] == battery_initial_capacity
            else:
                # Battery state of charge must be equal to the previous state plus the electricity flow to the battery
                # minus the electricity flow from the battery and the degradation
                battery_degradation = (
                        battery_degradation_rate * (1 - self.variables.battery_state_of_charge[_t - 1])
                )
                self.problem += (
                        self.variables.battery_state_of_charge[_t]
                        == self.variables.battery_state_of_charge[_t - 1]
                        + self.variables.renewable_electricity_to_battery[_t]
                        - self.variables.battery_electricity_to_house[_t]
                        - battery_degradation
                )
            # Battery capacity must be greater than or equal to the battery state of charge
            self.problem += self.variables.battery_state_of_charge[_t] <= self.variables.battery_capacity

    def solve(self) -> None:
        """
        Method to solve the optimisation problem.
        """
        if self.problem is None:
            raise ValueError("Optimisation problem has not been defined.")
        else:
            self.problem.solve()
            logger.info(f"Status: {LpStatus[self.problem.status]}")
            logger.info(f"Objective: {pl.value(self.problem.objective)}")
            logger.info(f"Battery capacity: {pl.value(self.variables.battery_capacity)}")
            logger.info(f"Solar size: {pl.value(self.variables.solar_size)}")
            if self.optimisation_objective == OptimisationObjectives.MINIMISE_BATTERY_AND_SOLAR_COST:
                logger.info(f"Total cost: {pl.value(self.problem.objective)}")
                logger.info(f"Battery cost: {pl.value(self.variables.battery_capacity) * self.battery_capex}")
                logger.info(f"Solar cost: {pl.value(self.variables.solar_size) * self.solar_capex}")

    def plot_results(self) -> None:
        """
        Method to plot the results of the optimisation problem.
        """
        # plot results
        plt.figure(figsize=(10, 5))
        plt.plot(
            [pl.value(self.variables.battery_state_of_charge[t]) for t in self.time_slices],
            label="Battery state of charge",
        )
        plt.plot(
            [pl.value(self.variables.renewable_electricity_to_house[t]) for t in self.time_slices],
            label="Renewable electricity to house",
        )
        plt.plot(
            [pl.value(self.variables.battery_electricity_to_house[t]) for t in self.time_slices],
            label="Battery electricity to house",
        )
        plt.plot(
            [
                pl.value(self.variables.battery_electricity_to_house[t])
                + pl.value(self.variables.renewable_electricity_to_house[t])
                for t in self.time_slices
            ],
            label="Total electricity to house",
        )
        plt.plot(
            [
                pl.value(self.variables.battery_electricity_to_house[t])
                + pl.value(self.variables.renewable_electricity_to_house[t])
                - self.energy_demand.loc[t, ENERGY_DEMAND]
                for t in self.time_slices
            ],
            label="Excess electricity",
        )
        plt.legend()
        plt.show()

    def dump_results(self, output_path: Path) -> None:
        """
        Method to dump the results of the optimisation problem to a csv.
        :param output_path: Path to dump the results to.
        """
        results = pd.DataFrame(
            {
                "battery_state_of_charge": [
                    pl.value(self.variables.battery_state_of_charge[t])
                    for t in self.time_slices
                ],
                "renewable_electricity_to_house": [
                    pl.value(self.variables.renewable_electricity_to_house[t])
                    for t in self.time_slices
                ],
                "battery_electricity_to_house": [
                    pl.value(self.variables.battery_electricity_to_house[t])
                    for t in self.time_slices
                ],
                "total_electricity_to_house": [
                    pl.value(self.variables.battery_electricity_to_house[t])
                    + pl.value(self.variables.renewable_electricity_to_house[t])
                    for t in self.time_slices
                ],
                "excess_electricity": [
                    pl.value(self.variables.battery_electricity_to_house[t])
                    + pl.value(self.variables.renewable_electricity_to_house[t])
                    - self.energy_demand.loc[t, ENERGY_DEMAND]
                    for t in self.time_slices
                ],
                "battery_capacity": pl.value(self.variables.battery_capacity),
                "solar_size": pl.value(self.variables.solar_size),
            }
        )
        if self.optimisation_objective == OptimisationObjectives.MINIMISE_BATTERY_AND_SOLAR_COST:
            results["total_cost"] = pl.value(self.problem.objective)
            results["battery_cost"] = pl.value(self.variables.battery_capacity) * self.battery_capex
            results["solar_cost"] = pl.value(self.variables.solar_size) * self.solar_capex

        results.to_csv(output_path, index=False)


    def _define_problem(self):
        """
        Method to define and create the optimisation problem attribute.
        """
        if self.optimisation_objective == OptimisationObjectives.MINIMISE_BATTERY_CAP:
            self.problem = pl.LpProblem("BatterySizeMinimisation", pl.LpMinimize)
        elif (
                self.optimisation_objective
                == OptimisationObjectives.MINIMISE_BATTERY_AND_SOLAR_COST
        ):
            self.problem = pl.LpProblem("BatteryAndPVCostMinimisation", pl.LpMinimize)
        else:
            raise ValueError(
                f"Unknown optimisation objective: {self.optimisation_objective}"
            )

    def _define_objective_function(
            self,
            battery_capex: Optional[float] = None,
            solar_capex: Optional[float] = None,
    ) -> None:
        """
        Method to define the objective function and to add to the problem attribute.
        :param battery_capex: Battery capex (£/kWh)
        :param solar_capex: Solar capex (£/m2)
        :return: None
        """
        if self.optimisation_objective == OptimisationObjectives.MINIMISE_BATTERY_CAP:
            if battery_capex:
                logger.info("Battery capex has been provided as an input argument, however, the optimisation objective"
                            "is to minimise battery size. Therefore, this battery capex will be ignored.")
            if solar_capex:
                logger.info("Solar capex has been provided as an input argument, however, the optimisation objective"
                            "is to minimise battery size. Therefore, this solar capex will be ignored.")
            self.problem += self.variables.battery_capacity
        elif (
                self.optimisation_objective
                == OptimisationObjectives.MINIMISE_BATTERY_AND_SOLAR_COST
        ):
            self.problem += (
                    self.variables.battery_capacity * battery_capex
                    + self.variables.solar_size * solar_capex
            )
        else:
            raise ValueError(
                f"Unknown optimisation objective: {self.optimisation_objective}"
            )
