"""
Main
"""
import gc
import logging
import tempfile
from pathlib import Path

import pandas as pd

from arguments import Arguments
from model.inputs.input_loader import InputLoader
from model.inputs.pre_processing import (
    PreProcessEnergyDemand,
    PreProcessSolarIrradiance,
)
from model.linear_optimiser.optimiser import Optimiser

logger = logging.getLogger(__name__)


def run_model(args: Arguments):
    """
    Function that takes the Arguments dataclass object and runs the model.
    :param args:
    :return:
    """
    logger.info("Running model 🚀")
    # Load the data
    energy_demand_profile = InputLoader(pre_processor=PreProcessEnergyDemand()).read(
        args.energy_demand_profile_path
    )
    solar_irradiance = InputLoader(
        pre_processor=PreProcessSolarIrradiance(
            energy_demand_profile=energy_demand_profile
        )
    ).read(args.solar_irradiance_path)

    # Create a temporary directory to store pre-processed data (not sure why, but when passing the dataframes directly
    # to the optimiser, hits a recursion error. This seems to fix it).
    logger.info("Creating temporary directory to store pre-processed data")
    temp_dir = tempfile.mkdtemp()
    solar_irradiance.to_csv(Path(temp_dir, "solar_irradiance.csv"), index=False)
    energy_demand_profile.to_csv(
        Path(temp_dir, "energy_demand_profile.csv"), index=False
    )

    # Delete the dataframes to free up memory
    del solar_irradiance
    del energy_demand_profile
    gc.collect()

    # read the pre-processed data
    energy_demand_profile = pd.read_csv(temp_dir + "/energy_demand_profile.csv")
    solar_irradiance = pd.read_csv(temp_dir + "/solar_irradiance.csv")

    optimisation = Optimiser(
        time_slices=range(len(energy_demand_profile)),
        optimisation_objective=args.optimisation_objective,
        solar_size=args.solar_array_size,
        energy_demand=energy_demand_profile,
        solar_irradiance=solar_irradiance,
        battery_capex=args.battery_capex,
        solar_capex=args.solar_capex,
    )
    optimisation.create_optimisation_problem(
        battery_initial_capacity=args.initial_battery_capacity,
        battery_degradation_rate=args.battery_degradation_rate,
    )
    optimisation.solve()
    optimisation.plot_results(
        output_dir=args.output_path,
    )
    if args.output_path:
        optimisation.dump_results(
            output_path=args.output_path,
        )
