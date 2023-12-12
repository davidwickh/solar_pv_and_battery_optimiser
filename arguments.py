"""This file contains the command line arguments for the program."""

import argparse
from dataclasses import dataclass, field
from pathlib import Path

from model.constants import OptimisationObjectives


@dataclass
class Arguments:  # pylint: disable=too-many-instance-attributes
    """Dataclass to process and store command line arguments."""

    solar_irradiance_path: Path = field(default_factory=Path)
    energy_demand_profile_path: Path = field(default_factory=Path)
    output_path: Path = field(default_factory=Path)
    solar_array_size: float = field(default_factory=float)
    initial_battery_capacity: float = field(default_factory=float)
    battery_degradation_rate: float = field(default_factory=float)
    battery_capex: float = field(default_factory=float)
    solar_capex: float = field(default_factory=float)
    optimisation_objective: OptimisationObjectives = field(
        default_factory=OptimisationObjectives
    )

    @classmethod
    def process_arguments(cls, args: argparse.Namespace) -> "Arguments":
        """
        Takes the command line arguments as an argparse.Namespace object and returns an Arguments
        dataclass object.
        :param args:
        :return:
        """
        return cls(
            solar_irradiance_path=Path(args.solar_irradiance_path),
            energy_demand_profile_path=Path(args.energy_demand_profile_path),
            output_path=Path(args.output_path),
            solar_array_size=args.solar_array_size,
            initial_battery_capacity=args.initial_battery_capacity,
            battery_degradation_rate=args.battery_degradation_rate,
            battery_capex=args.battery_capex,
            solar_capex=args.solar_capex,
            optimisation_objective=args.optimisation_objective,
        )
