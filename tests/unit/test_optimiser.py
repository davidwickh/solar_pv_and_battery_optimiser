"""
File containing tests for the optimiser
"""
import pandas as pd
import pulp as pl
import pytest

from model.constants import ENERGY_DEMAND, SOLAR_IRRADIANCE, OptimisationObjectives
from model.linear_optimiser.optimiser import Optimiser


class TestOptimiser:
    """
    Class containing tests for the optimiser.
    """

    @pytest.fixture(scope="class")
    def dummy_optimiser_min_battery_size(self) -> Optimiser:
        """
        Creates a dummy optimiser.
        :return: Dummy optimiser
        """
        return Optimiser(
            time_slices=range(10),
            optimisation_objective=OptimisationObjectives.MINIMISE_BATTERY_CAP,
            solar_size=10,
            solar_capex=100,
            battery_capex=100,
            energy_demand=pd.DataFrame(
                {
                    ENERGY_DEMAND: [1] * 10,
                }
            ),
            solar_irradiance=pd.DataFrame(
                {
                    SOLAR_IRRADIANCE: [1] * 10,
                }
            ),
        )

    @pytest.fixture(scope="class")
    def dummy_optimiser_min_cost(self) -> Optimiser:
        """
        Creates a dummy optimiser.
        :return: Dummy optimiser
        """
        return Optimiser(
            time_slices=range(10),
            optimisation_objective=OptimisationObjectives.MINIMISE_BATTERY_AND_SOLAR_COST,
            solar_size=10,
            solar_capex=100,
            battery_capex=100,
            energy_demand=pd.DataFrame(
                {
                    ENERGY_DEMAND: [1] * 10,
                }
            ),
            solar_irradiance=pd.DataFrame(
                {
                    SOLAR_IRRADIANCE: [1] * 10,
                }
            ),
        )

    def test_optimiser_min_battery_size(
        self, dummy_optimiser_min_battery_size: Optimiser
    ) -> None:
        """
        Test the optimiser successfully builds the optimisation problem. When optimising for the minimum battery size,
        the optimiser should set the solar size as defined in the input arguments (10). Furthermore, the solar and
        battery CAPEX should be None.
        :param dummy_optimiser_min_battery_size: Dummy optimiser
        :return: None
        """
        # Arrange
        # Act
        dummy_optimiser_min_battery_size.create_optimisation_problem(
            battery_initial_capacity=0,
            battery_degradation_rate=0.01,
            solar_efficiency=0.2,
        )
        # Assert
        assert dummy_optimiser_min_battery_size.variables.solar_size == 10
        assert dummy_optimiser_min_battery_size.problem is not None
        assert dummy_optimiser_min_battery_size.solar_capex is None
        assert dummy_optimiser_min_battery_size.battery_capex is None

    def test_optimiser_min_cost(self, dummy_optimiser_min_cost: Optimiser) -> None:
        """
        Test the optimiser successfully builds the optimisation problem. When optimising for the minimum cost,
        the solar size should be an optimisation variable.
        """
        # Arrange
        # Act
        dummy_optimiser_min_cost.create_optimisation_problem(
            battery_initial_capacity=0,
            battery_degradation_rate=0.01,
            solar_efficiency=0.2,
        )
        # Assert
        assert isinstance(dummy_optimiser_min_cost.variables.solar_size, pl.LpVariable)
        assert dummy_optimiser_min_cost.problem is not None
