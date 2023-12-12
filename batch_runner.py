import logging
import os
from pathlib import Path
from multiprocessing import Pool

import pandas as pd

initial_battery_capacities = range(0, 25, 5)
battery_degradation_rates = [0.001, 0.005, 0.01, 0.015, 0.02]
solar_array_sizes = range(500, 5000, 500)
output_path = Path(os.getcwd(), "output")
task_1_output = Path(output_path, "task_1")
task_1_output_sensitivity = Path(task_1_output, "senstivity_analysis")


logger = logging.getLogger(__name__)

def run_simulation(args):
    solar_array_size, battery_degradation_rate, initial_battery_capacity, sub_dir = args
    os.system(
        f"""python3 run.py --solar_irradiance_path="/Users/David/Downloads/CS_energy_assessment_solar_irradiance.csv" --energy_demand_profile_path="/Users/David/Downloads/CS_energy_assessment_electricity_smart_meter.csv" --solar_array_size={solar_array_size} --output_path={sub_dir} --battery_degradation_rate={battery_degradation_rate} --initial_battery_capacity={initial_battery_capacity} --optimisation_objective='minimise_battery_cap'"""
    )


def batch_run():
    if not os.path.exists("output"):
        os.mkdir("output")

    if not os.path.exists(Path(output_path, "task_1")):
        os.mkdir(Path(output_path, "task_1"))

    if not os.path.exists(task_1_output_sensitivity):
        os.mkdir(task_1_output_sensitivity)

    # Prepare arguments for multiprocessing
    args = []
    for solar_array_size in solar_array_sizes:
        for battery_degradation_rate in battery_degradation_rates:
            for initial_battery_capacity in initial_battery_capacities:
                sub_dir_str = f"{solar_array_size}_{battery_degradation_rate}_{initial_battery_capacity}"
                sub_dir = Path(task_1_output_sensitivity, sub_dir_str)
                args.append((solar_array_size, battery_degradation_rate, initial_battery_capacity, sub_dir))

    # Use multiprocessing to run simulations in parallel
    with Pool() as p:
        p.map(run_simulation, args)


def analyze_simulation(args):
    logger.info(f"Analyzing simulation: {args}")
    solar_array_size, battery_degradation_rate, initial_battery_capacity, sub_dir = args
    df = pd.read_csv(Path(sub_dir[0], "optimisation_output.csv"))
    battery_cap = df["battery_capacity"].iloc[0]
    results_df = pd.DataFrame(
        data={
            "solar_array_size": solar_array_size,
            "battery_degradation_rate": battery_degradation_rate,
            "initial_battery_capacity": initial_battery_capacity,
            "battery_capacity": battery_cap,
        },
    )
    return results_df


def batch_analysis():
    # Prepare arguments for multiprocessing
    args = []
    for solar_array_size in solar_array_sizes:
        for battery_degradation_rate in battery_degradation_rates:
            for initial_battery_capacity in initial_battery_capacities:
                sub_dir_str = f"{solar_array_size}_{battery_degradation_rate}_{initial_battery_capacity}"
                sub_dir = Path(task_1_output_sensitivity, sub_dir_str)
                args.append(([solar_array_size], [battery_degradation_rate], [initial_battery_capacity], [sub_dir]))

    # Use multiprocessing to run analysis in parallel
    with Pool() as p:
        results = p.map(analyze_simulation, args)

    # Concatenate all dataframes
    df_all = pd.concat(results)

    # Save to csv
    print("Saving to csv")
    df_all.to_csv(Path(task_1_output, "sensitivity_analysis.csv"), index=False)


if __name__ == "__main__":
    # Set up logger
    logging.basicConfig(
        level="INFO",
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%m-%d %H:%M:%S",
    )
    batch_analysis()
