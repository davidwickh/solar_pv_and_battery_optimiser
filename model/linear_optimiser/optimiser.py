from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
import pulp as pl
from pulp import LpStatus

from model.constants import ENERGY_DEMAND, SOLAR_IRRADIANCE, OptimisationObjectives


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
    ) -> None:
        """
        Creates the optimisation problem.
        :return: None
        """
        # Define the problem
        if optimisation_objective == OptimisationObjectives.MINIMISE_BATTERY_CAP:
            self.problem = pl.LpProblem("BatterySizeMinimisation", pl.LpMinimize)
        elif (
            optimisation_objective
            == OptimisationObjectives.MINIMISE_BATTERY_AND_SOLAR_COST
        ):
            self.problem = pl.LpProblem("BatteryAndPVCostMinimisation", pl.LpMinimize)
        else:
            raise ValueError(
                f"Unknown optimisation objective: {optimisation_objective}"
            )

        # Define variables
        # Renewable electricity flow
        renewable_electricity_to_house = pl.LpVariable.dicts(
            name="renewable_electricity_to_house",
            indices=time_slices,
            lowBound=0,
            cat="Continuous",
        )
        renewable_electricity_to_battery = pl.LpVariable.dicts(
            name="renewable_electricity_to_battery",
            indices=time_slices,
            lowBound=0,
            cat="Continuous",
        )
        # Battery electricity flow
        battery_electricity_to_house = pl.LpVariable.dicts(
            name="battery_electricity_to_house",
            indices=time_slices,
            lowBound=0,
            cat="Continuous",
        )
        # Battery state of charge
        battery_state_of_charge = pl.LpVariable.dicts(
            name="battery_state_of_charge",
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
        if (
            optimisation_objective
            == OptimisationObjectives.MINIMISE_BATTERY_AND_SOLAR_COST
        ):
            # Solar capacity
            solar_size = pl.LpVariable(
                name="solar_capacity",
                lowBound=0,
                cat="Continuous",
            )
        elif optimisation_objective == OptimisationObjectives.MINIMISE_BATTERY_CAP:
            solar_size = solar_capacity
        else:
            raise ValueError(
                f"Unknown optimisation objective: {optimisation_objective}"
            )

        # Objective function
        if optimisation_objective == OptimisationObjectives.MINIMISE_BATTERY_CAP:
            self.problem += (
                pl.lpSum(battery_capacity),
                "Objective - minimise battery size",
            )
        elif (
            optimisation_objective
            == OptimisationObjectives.MINIMISE_BATTERY_AND_SOLAR_COST
        ):
            raise NotImplementedError
        else:
            raise ValueError(
                f"Unknown optimisation objective: {optimisation_objective}"
            )

        # Energy flow constraints
        for _t in time_slices:
            # Solar generation
            solar_generation = (
                solar_irradiance[SOLAR_IRRADIANCE][_t]
                * solar_size
                * solar_efficiency
                * 0.5
            )
            energy_demand_at_time = energy_demand.loc[_t, ENERGY_DEMAND]

            # Renewable electricity flow to house and battery must equal renewable generation
            self.problem += (
                renewable_electricity_to_house[_t]
                + renewable_electricity_to_battery[_t]
                <= solar_generation
            )
            # Electricity demand from house must be met
            self.problem += (
                renewable_electricity_to_house[_t] + battery_electricity_to_house[_t]
                == energy_demand_at_time
            )

            # Battery state of charge
            if _t == 0:  # Initial battery state of charge
                self.problem += battery_state_of_charge[_t] == battery_initial_capacity
            else:
                # Battery state of charge must be equal to the previous state plus the electricity flow to the battery
                # minus the electricity flow from the battery and the degradation
                battery_degradation = (
                    battery_degradation_rate * battery_state_of_charge[_t - 1]
                )
                self.problem += (
                    battery_state_of_charge[_t]
                    == battery_state_of_charge[_t - 1]
                    + renewable_electricity_to_battery[_t]
                    - battery_electricity_to_house[_t]
                    - battery_degradation
                )
            # Battery capacity must be greater than or equal to the battery state of charge
            self.problem += battery_state_of_charge[_t] <= battery_capacity

        self.problem.solve()

        # Print results
        print(f"Status: {LpStatus[self.problem.status]}")
        print(f"Objective: {pl.value(self.problem.objective)}")
        print(f"Battery capacity: {pl.value(battery_capacity)}")
        print(f"Solar size: {pl.value(solar_size)}")
        print(
            f"Renewable electricity to house: {sum(pl.value(renewable_electricity_to_house[t]) for t in time_slices)}"
        )
        print(
            f"Renewable electricity to battery: {sum(pl.value(renewable_electricity_to_battery[t]) for t in time_slices)}"
        )
        print(
            f"Battery electricity to house: {sum(pl.value(battery_electricity_to_house[t]) for t in time_slices)}"
        )
        print(
            f"Total House Demand: {sum(energy_demand.loc[t, ENERGY_DEMAND] for t in time_slices)}"
        )

        # plot results
        plt.figure(figsize=(10, 5))
        plt.plot(
            [pl.value(battery_state_of_charge[t]) for t in time_slices],
            label="Battery state of charge",
        )
        plt.plot(
            [pl.value(renewable_electricity_to_house[t]) for t in time_slices],
            label="Renewable electricity to house",
        )
        plt.plot(
            [pl.value(battery_electricity_to_house[t]) for t in time_slices],
            label="Battery electricity to house",
        )
        plt.plot(
            [
                pl.value(battery_electricity_to_house[t])
                + pl.value(renewable_electricity_to_house[t])
                for t in time_slices
            ],
            label="Total electricity to house",
        )
        plt.plot(
            [
                pl.value(battery_electricity_to_house[t])
                + pl.value(renewable_electricity_to_house[t])
                - energy_demand.loc[t, ENERGY_DEMAND]
                for t in time_slices
            ],
            label="Excess electricity",
        )
        plt.legend()
        plt.show()


if __name__ == "__main__":
    energy_demand = pd.read_csv(
        r"C:\Users\David.Wickham\PycharmProjects\solar_pv_and_battery_optimiser\energy_demand.csv"
    )
    solar_irradiance = pd.read_csv(
        r"C:\Users\David.Wickham\PycharmProjects\solar_pv_and_battery_optimiser\solar_irradiance.csv"
    )
    optimiser = Optimiser()
    optimiser.create_optimisation_problem(
        energy_demand=energy_demand,
        solar_irradiance=solar_irradiance,
        battery_initial_capacity=0,
        solar_capacity=10000000000000000000,
        optimisation_objective=OptimisationObjectives.MINIMISE_BATTERY_CAP,
        solar_efficiency=0.15,
        battery_degradation_rate=0.01,
        time_slices=range(len(energy_demand)),
    )
