"""This file contains the command line arguments for the program."""

import argparse
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Arguments:
    """Dataclass to process and store command line arguments."""

    solar_irradiance_path: Path = field(default_factory=Path)
    energy_demand_profile_path: Path = field(default_factory=Path)
    solar_array_size: float = field(default_factory=float)
    initial_battery_capacity: float = field(default_factory=float)

    @classmethod
    def process_arguments(cls, args: argparse.Namespace) -> "Arguments":
        """
        Takes the command line arguments as an argparse.Namespace object and returns an Arguments dataclass object.
        :param args:
        :return:
        """
        return cls(
            solar_irradiance_path=Path(args.solar_irradiance_path),
            energy_demand_profile_path=Path(args.energy_demand_profile_path),
            solar_array_size=args.solar_array_size,
            initial_battery_capacity=args.initial_battery_capacity,
        )
