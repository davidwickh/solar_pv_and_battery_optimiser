from typing import Optional

import pandas as pd
import pulp as pl

from model.constants import ENERGY_DEMAND, SOLAR_GENERATION, OptimisationObjectives, SOLAR_IRRADIANCE


class Optimiser:
    """
    Class containing code associated with the linear optimiser.
    """

    problem: pl.LpProblem = None

    def create_optimisation_problem(
            self,
            energy_demand: pd.DataFrame,
            solar_irradiance: pd.DataFrame,
            battery_initial_capacity: float,
            battery_degradation_rate: float,
            optimisation_objective: OptimisationObjectives,
            time_slices: range,
            solar_capacity: Optional[float] = None,
            solar_efficiency: Optional[float] = 0.15,
    ):
        """
        Creates the optimisation problem.
        :return: None
        """
        # Define the problem
        if optimisation_objective == OptimisationObjectives.MINIMISE_BATTERY_CAP:
            self.problem = pl.LpProblem("BatterySizeMinimisation", pl.LpMinimize)
        elif optimisation_objective == OptimisationObjectives.MINIMISE_BATTERY_AND_SOLAR_COST:
            self.problem = pl.LpProblem("BatteryAndPVCostMinimisation", pl.LpMinimize)
        else:
            raise ValueError(f"Unknown optimisation objective: {optimisation_objective}")

        # Define variables
        # Renewable electricity flow
        renewable_electricity_to_house = pl.LpVariable.dicts(
            name="renewable_electricity_to_house_{_t}",
            indices=time_slices,
            lowBound=0,
            cat="Continuous",
        )
        renewable_electricity_to_battery = pl.LpVariable.dicts(
            name="renewable_electricity_to_battery_{_t}",
            indices=time_slices,
            lowBound=0,
            cat="Continuous",
        )
        # Battery electricity flow
        battery_electricity_to_house = pl.LpVariable.dicts(
            name="battery_electricity_to_house_{_t}",
            indices=time_slices,
            lowBound=0,
            cat="Continuous",
        )
        # Battery state of charge
        battery_state_of_charge = pl.LpVariable.dicts(
            name="battery_state_of_charge_{_t}",
            indices=time_slices,
            lowBound=0,
            cat="Continuous",
        )
        # Battery capacity
        battery_capacity = pl.LpVariable(
            name="battery_capacity",
            lowBound=0,
            cat="Continuous",
        )
        if optimisation_objective == OptimisationObjectives.MINIMISE_BATTERY_AND_SOLAR_COST:
            # Solar capacity
            solar_capacity_var = pl.LpVariable(
                name="solar_capacity",
                lowBound=0,
                cat="Continuous",
            )
        elif optimisation_objective == OptimisationObjectives.MINIMISE_BATTERY_CAP:
            solar_capacity_var = solar_capacity
        else:
            raise ValueError(f"Unknown optimisation objective: {optimisation_objective}")

        # Objective function
        if optimisation_objective == OptimisationObjectives.MINIMISE_BATTERY_CAP:
            self.problem += pl.lpSum(battery_capacity), "Objective - minimise battery size"
        elif optimisation_objective == OptimisationObjectives.MINIMISE_BATTERY_AND_SOLAR_COST:
            raise NotImplementedError
        else:
            raise ValueError(f"Unknown optimisation objective: {optimisation_objective}")

        # Energy flow constraints
        for _t in time_slices:
            # Solar generation
            solar_generation = solar_irradiance[SOLAR_IRRADIANCE][_t] * solar_capacity_var * solar_efficiency
            energy_demand_at_time = energy_demand.loc[_t, ENERGY_DEMAND]

            # Variables
            renewable_electricity_to_house_t = renewable_electricity_to_house[_t]
            battery_electricity_to_house_t = battery_electricity_to_house[_t]

            # Add constraints

            # Renewable electricity flow to house and battery must equal renewable generation
            self.problem += (
                    renewable_electricity_to_house[_t]
                    + renewable_electricity_to_battery[_t] <= solar_generation
            )
            # Electricity demand from house must be met
            # self.problem += renewable_electricity_to_house_t + battery_electricity_to_house_t == energy_demand_at_time
            # Battery state of charge
            if _t == 0: # Initial battery state of charge
                self.problem += battery_state_of_charge[_t] == battery_initial_capacity
            else:
                # Battery state of charge must be equal to the previous state plus the electricity flow to the battery
                    # minus the electricity flow from the battery and the degradation
                battery_degradation = battery_degradation_rate * battery_state_of_charge[_t - 1]
                self.problem += (
                        battery_state_of_charge[_t]
                        == battery_state_of_charge[_t - 1]
                        + renewable_electricity_to_battery[_t]
                        - battery_electricity_to_house[_t]
                        - battery_degradation
                )
            # Battery capacity must be greater than or equal to the battery state of charge
            self.problem += battery_state_of_charge[_t] <= battery_capacity



    def solve(self):
        """
        Solves the optimisation problem.
        :return: None
        """
        self.problem.solve()
        print(pl.LpStatus[self.problem.status])
        print(pl.value(self.problem.objective))
        for v in self.problem.variables():
            print(v.name, "=", v.varValue)
