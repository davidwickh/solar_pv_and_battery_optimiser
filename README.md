# Solar PV and Battery Optimiser

## Overview
This repo contains a solar PV and battery optimiser.

## Installation
To install the optimiser, run the following commands:
1. clone the repo to your local machine
2. navigate to the repo directory
3. create and activate a virtual environment using the following commands:
```bash
python3 -m venv venv
source venv/bin/activate
```
4. install the requirements using the following command:
```bash
pip install -r requirements.txt
```

## Usage
### Inputs
The optimiser requires the following inputs:
1. **Solar irradiance** - the solar irradiance in W/m2. An example of this input can be seen below
![img.png](docs/img.png)
- **Energy demand profile** - the energy demand profile in kWh. An example of this input can be seen 
below
![img_1.png](docs/img_1.png)

### Arguments
The optimiser takes the following arguments (these can be seen by running `python run.py --help` in the commandline):
- `--solar_irradiance_path` - the path to the solar irradiance csv file
- `--energy_demand_profile_path` - the path to the energy demand profile csv file
- `--logging_level` - the logging level to use (default is `INFO`)
- `--output_path` - the path to save the optimisation results to 
- `--solar_array_size` - the size of the solar array in m2
- `--initial_battery_capacity` - the initial battery capacity in kWh
- `--battery_degredation_rate` - the battery degradation rate in kWh of electricity per kWh of battery capacity
- `--optimisation_objective` - the optimisation objective to use (either `minimise_battery_cap` or `minimise_battery_and_solar_cost`)
- `--battery_capex` - the battery capex in £/kWh
- `--solar_capex` - the solar capex in £/m2

### Outputs
The optimiser outputs the following:
- **Optimisation results** - the optimisation results are saved as a CSV to the `output_path` specified in the arguments.
- **Optimisation plots** - the optimisation results are also plotted and saved to the `output_path` specified in the arguments.
- **Commandline logs** - a summary of some of the optimisation results are also logged to the commandline.
