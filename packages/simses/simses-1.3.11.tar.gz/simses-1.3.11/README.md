# SimSES
SimSES (Simulation of stationary energy storage systems) is an open source modeling framework for simulating stationary energy storage systems.
Further information can be found in the accompanying research article: https://doi.org/10.1016/j.est.2021.103743. If you are using SimSES, or plan to do so, please cite this work.

## Setup and installation

### 1. Create a virtual environment
Create a virtual environment, for example with either
[venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment) or [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html), or directly through your IDE like [PyCharm](https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html#env-requirements) and [VS Code](https://code.visualstudio.com/docs/python/environments).

### 2. Install dependencies
Install `simses` and all other required python packages in your virtual environment. This can be done with a single command:
```
pip install -e .
```

### 3. Exemplary simulations
Visit [this page](simses/simulation/simulation_examples/readme.md) to read more about some exemplary simulations and setting up a simulation with pre-configured parameters.

## Acknowlegdements
The tool, originally developed in MATLAB, was initiated by Maik Naumann and Nam Truong, transferred to Python by Daniel Kucevic and Marc Möller and now continuously improved at the Chair of Electrical Energy Storage of the Technical University of Munich.
