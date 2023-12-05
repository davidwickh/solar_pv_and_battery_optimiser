"""
File contains code associated with battery constraints and variables for the linear optimiser.
"""

import logging
import pulp as pl

logger = logging.getLogger(__name__)


class Battery:
    """
    Class containing all constraints and variables associated with the battery.
    """

    def __init__(self, battery_degradation_rate: float, initial_capacity: float) -> None:
        """
        Initialises the Battery class.

        :param battery_degradation_rate: The rate at which the battery degrades per unit of energy throughput
        """
        self.battery_capacity = pl.LpVariable("battery_capacity", lowBound=0, cat="Continuous")
        self.battery_degradation = battery_degradation_rate
        self.initial_capacity = initial_capacity

    def
