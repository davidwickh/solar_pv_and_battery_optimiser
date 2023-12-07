"""
This file contains tests for the optimiser_variables module.
"""

import pytest

from model.constants import OptimisationObjectives
from model.linear_optimiser.variables import OptimiserVariables


class TestOptimiserVariables:
    """
    Class containing tests for the OptimiserVariables class.
    """

    @pytest.fixture(scope="class")
    def optimiser_variables(self) -> OptimiserVariables:
        """
        Creates an OptimiserVariables object.
        :return: OptimiserVariables object
        """
        return OptimiserVariables.create_variables(
            time_slices=range(10),
            optimisation_objective=OptimisationObjectives.MINIMISE_BATTERY_CAP,
            solar_size=10,
        )

    def test_create_variables(self, optimiser_variables: OptimiserVariables) -> None:
        """
        Tests that the variables are created correctly.
        """
        assert len(optimiser_variables.renewable_electricity_to_house) == 10
        assert len(optimiser_variables.renewable_electricity_to_battery) == 10
        assert len(optimiser_variables.battery_electricity_to_house) == 10
        assert len(optimiser_variables.battery_state_of_charge) == 10
        assert optimiser_variables.solar_size == 10
