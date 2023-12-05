"""
File containing code associated with creating the objective function for the linear optimiser.
"""
import pulp as pl


class ObjectiveFunction:
    """
    Class containing the various objective functions that can be used for the linear optimiser.
    """

    @staticmethod
    def minimise_battery_capacity(battery_capacity: pl.LpVariable, problem: pl.LpProblem) -> None:
        """
        Minimises the battery size.
        :param problem: Linear optimisation problem
        :return: None
        """
        problem += pl.lpSum(battery_capacity), "Objective - minimise battery size"
