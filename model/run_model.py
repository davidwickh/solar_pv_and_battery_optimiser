"""
Main
"""
import gc
import logging
from pathlib import Path

import pandas as pd

from arguments import Arguments
from model.constants import DATE_TIME, OptimisationObjectives
from model.inputs.input_loader import InputLoader
from model.inputs.pre_processing import MatchTimeStampsPreProcessor, FilterNonHalfHourlyData
from model.linear_optimiser.optimiser import Optimiser
import tempfile

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

    # Create a temporary directory to store pre-processed data (not sure why, but when passing the dataframes directly
    # to the optimiser, hits a recursion error. This seems to fix it).
    logger.info("Creating temporary directory to store pre-processed data")
    temp_dir = tempfile.mkdtemp()
    solar_irradiance.to_csv(Path(temp_dir, "solar_irradiance.csv"), index=False)
    energy_demand_profile.to_csv(Path(temp_dir, "energy_demand_profile.csv"), index=False)

    del solar_irradiance
    del energy_demand_profile

    gc.collect()

    # read the pre-processed data
    energy_demand_profile = pd.read_csv(temp_dir + "/energy_demand_profile.csv")
    solar_irradiance = pd.read_csv(temp_dir + "/solar_irradiance.csv")

    Optimiser().create_optimisation_problem(
        energy_demand=energy_demand_profile,
        solar_irradiance=solar_irradiance,
        battery_initial_capacity=args.initial_battery_capacity,
        solar_capacity=args.solar_array_size,
        optimisation_objective=OptimisationObjectives.MINIMISE_BATTERY_CAP,
        solar_efficiency=0.15,
        battery_degradation_rate=0.01,
        time_slices=range(len(energy_demand_profile)),
    )
