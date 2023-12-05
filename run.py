"""
Main entry point for the model from the cli.
"""
import argparse
from pathlib import Path

from arguments import Arguments
from model.run_model import run_model
from utils import setup_logger


def main():
    """
    Main entry point for the model.
    :return:
    """
    arg_parser = argparse.ArgumentParser(description="Model arguments.")
    arg_parser.add_argument(
        "--solar_irradiance_path", type=Path, help="Path to the solar irradiance data."
    )
    arg_parser.add_argument(
        "--energy_demand_profile_path",
        type=Path,
        help="Path to the energy demand profile.",
    )
    arg_parser.add_argument(
        "--logging_level", type=str, default="INFO", help="Logging level to use."
    )
    arg_parser.add_argument(
        "--solar_array_size",
        type=float,
        default=1.0,
        help="Size of the solar array in kW. NOTE should only be used when optimising the battery size only",
    )
    arg_parser.add_argument(
        "--initial_battery_capacity",
        type=float,
        default=0.0,
        help="Initial battery capacity in kWh",
    )

    args = arg_parser.parse_args()
    setup_logger(args.logging_level)
    args = Arguments.process_arguments(args)
    run_model(args)


if __name__ == "__main__":
    main()
