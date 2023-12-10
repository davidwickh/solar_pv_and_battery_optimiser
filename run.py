"""
Main entry point for the model from the cli.
"""
import argparse
from pathlib import Path

from arguments import Arguments
from model.constants import OptimisationObjectives
from model.run_model import run_model
from utils import setup_logger


class ValidateOptimisationObjective(argparse.Action):
    """
    Custom action to validate the optimisation objective. Ensures that the battery capex and solar
    capex are specified when optimising the total CAPEX of the system.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        if (
            namespace.optimisation_objective
            == OptimisationObjectives.MINIMISE_BATTERY_CAP
        ):
            # Make sure the battery capex and solar capex is not
            if namespace.battery_capex is None or namespace.solar_capex is None:
                raise argparse.ArgumentTypeError(
                    "Battery capex and solar capex must be specified when optimising the battery "
                    "capacity."
                )
        else:
            if namespace.battery_capex is not None or namespace.solar_capex is not None:
                raise argparse.ArgumentTypeError(
                    "Battery capex and solar capex must be specified when optimising the battery "
                    "and solar CAPEX."
                )
            return values


def main():
    """
    Main entry point for the model.
    :return:
    """
    arg_parser = argparse.ArgumentParser(description="Model arguments.")
    inputs_args = arg_parser.add_argument_group(title="Inputs")
    # Solar irradiance data
    inputs_args.add_argument(
        "--solar_irradiance_path",
        type=Path,
        help="Path to the solar irradiance data.",
        required=True,
    )
    # Energy demand profile
    inputs_args.add_argument(
        "--energy_demand_profile_path",
        type=Path,
        help="Path to the energy demand profile.",
        required=True,
    )
    inputs_args.add_argument(
        "--output_path", type=Path, help="Path to the output directory.", required=True,
    )
    # Logging level
    arg_parser.add_argument(
        "--logging_level", type=str, default="INFO", help="Logging level to use."
    )
    # Optimisation parameters
    optimisation_params = arg_parser.add_argument_group(title="Optimisation parameters")
    optimisation_params.add_argument(
        "--solar_array_size",
        type=float,
        default=100000.0,
        help="Size of the solar array in m^2. NOTE should only be used when optimising the battery "
        "size.",
        action=ValidateOptimisationObjective,
    )
    optimisation_params.add_argument(
        "--initial_battery_capacity",
        type=float,
        default=0.0,
        help="Initial battery capacity in kWh",
    )
    optimisation_params.add_argument(
        "--battery_degradation_rate",
        type=float,
        default=0.01,
        help="Battery degradation rate, in (kWh lost/kWh stored)",
    )
    optimisation_params.add_argument(
        "--optimisation_objective",
        type=str,
        default=OptimisationObjectives.MINIMISE_BATTERY_CAP,
        help="Optimisation objective",
        choices=[e for e in OptimisationObjectives],
        action=ValidateOptimisationObjective,
    )
    optimisation_params.add_argument(
        "--battery_capex", type=float, help="Battery capex (£/kWh)",
    )
    optimisation_params.add_argument(
        "--solar_capex", type=float, help="Solar capex (£/m2)",
    )

    args = arg_parser.parse_args()
    setup_logger(args.logging_level)
    args = Arguments.process_arguments(args)
    run_model(args)


if __name__ == "__main__":
    main()
