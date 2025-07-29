# LightImpact
[![PyPI version](https://badge.fury.io/py/lightimpact.svg?v=0.1.3)](https://pypi.org/project/lightimpact/0.1.3/)

**LightImpact** is an open-source Python library for calculating the **Energy Reduction Value (ERV)** of lightweight automotive components applied in both internal combustion vehicles (ICVs) and electric vehicles (EVs), based on WLTP driving cycle data.
Developed for life cycle assessment (LCA) modeling in the **MM4R** research project at RWTH Aachen University.

## Features
- Physics-based mechanical work calculation
- WLTP-compliant ERV computation
- Compatible with both ICVs and EVs
- Customizable input parameters
- Suitable for integration into LCA workflows

## Installation
Make sure you have [Python](https://www.python.org/downloads/) installed. Then, you can install LightImpact as follows:

Either globally on your system:

```bash
pip3 install lightimpact
```

Or, if you prefer to install it in a virtual environment:

```bash
python3 -m venv lightimpact-env

# On MacOS/Linux
source lightimpact-env/bin/activate
# On Windows
lightimpact-env\Scripts\activate

pip install lightimpact
```

## Example Usage
After installation, you can use LightImpact in your Python scripts. Here's a simple example of how to run a case with custom parameters:
```python
from lightimpact.core import run_lightimpact_case

custom_params = {
    "m_vehicle": 1800,
    "cw": 0.28,
    "A_frontal": 2.3,
    "ds": 25.0,
    "c_fuel_WLTP": 9.5
}

run_lightimpact_case("WLTP_data/Time-Speed-Profile_WLTP_Class3b.csv", custom_params)
```

Running this code will calculate the total mechanical work, the differential efficiency factor, and ERV for both EV and ICV. It will output the results to the console.

## License
Licensed under the MIT License (c) 2025 Suzana Ostojic

## About
LightImpact was developed for use within the MM4R research project at the RWTH Aachen University.  
Contact: [suzana.ostojic@inab.rwth-aachen.de](mailto:suzana.ostojic@inab.rwth-aachen.de)
GitHub: [github.com/suzanaostojic/LightImpact-MM4R](https://github.com/suzanaostojic/LightImpact-MM4R)  
PyPI: [pypi.org/project/lightimpact](https://pypi.org/project/lightimpact)