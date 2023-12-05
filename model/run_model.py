"""
Main
"""
import gc
import logging

from arguments import Arguments
from model.constants import DATE_TIME, OptimisationObjectives
from model.inputs.input_loader import InputLoader
from model.inputs.pre_processing import MatchTimeStampsPreProcessor, FilterNonHalfHourlyData
from model.linear_optimiser.optimiser import Optimiser
from utils import DateTimeToNumeric

logger = logging.getLogger(__name__)


def run_model(args: Arguments):
    """
    Function that takes the Arguments dataclass object and runs the model.
    :param args:
    :return:
    """
    logger.info("Running model 🚀")
    # Load the data
    energy_demand_profile = InputLoader(pre_processor=FilterNonHalfHourlyData()).read(
        args.energy_demand_profile_path
    )
    solar_irradiance = InputLoader(
        pre_processor=MatchTimeStampsPreProcessor(
            energy_demand_profile=energy_demand_profile
        )
    ).read(args.solar_irradiance_path)

    gc.collect()

    # Create the optimisation problem
    optimiser = Optimiser().create_optimisation_problem(
        energy_demand=energy_demand_profile,
        solar_irradiance=solar_irradiance,
        battery_initial_capacity=args.initial_battery_capacity,
        solar_capacity=args.solar_array_size,
        optimisation_objective=OptimisationObjectives.MINIMISE_BATTERY_CAP,
        solar_efficiency=0.15,
        battery_degradation_rate=0.01,
        time_slices=range(len(energy_demand_profile)),
    )
    optimiser.solve()
