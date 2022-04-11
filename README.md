

This example simulates a simplified model of an inertial confinement fusion reactor using two different neutronics geometries method.

- A CAD model is made and automatically converted to a DAGMC geometry that is then used in OpenMC for a neutronics simulation.
- A Constructive Solid Geometry (CSG) is made made in OpenMC and used for a neutronics simulation directly.


# Prerequisites

This minimal example makes use of Conda to manage and install the packages.

You will need one of these conda distributions to be installed or work within a [Docker image](https://hub.docker.com/r/continuumio/miniconda3)

- [Miniconda](https://docs.conda.io/en/latest/miniconda.html)

- [Anaconda](https://www.anaconda.com/)

- [Miniforge](https://github.com/conda-forge/miniforge)

- [Miniconda](https://docs.conda.io/en/latest/miniconda.html)

# First clone the repository
```bash
git clone https://github.com/shimwell/neutronics_geomentry_comparision_simulation.git
cd neutronics_geomentry_comparision_simulation
```

# Making the DAGMC model for OpenMC and Shift

Make an environment for the model preparation
```
conda env create -f environment_cad.yml
conda activate env_cad
```

Then run the script for making the DAGMC model.
```bash
python scripts/1_create_dagmc_geometry.py
```

Optionally you can inspect the DAGMC file at this stage by converting the h5m file to a vtk file and opening this with [Paraview](https://www.paraview.org/). There should be several h5m made, this example command converts just one of them
```
mbconvert dagmc_1_openmc.h5m dagmc.vtk
paraview dagmc.vtk
```
![DAGMC model image](https://user-images.githubusercontent.com/8583900/159698979-3665e14b-ca42-4df2-8a1e-deee6597efc0.png)

# Simulating the model in OpenMC

First make an environment for simulation.

```
conda env create -f environment_neutronics.yml
conda activate env_neutronics
```

Then run the DAGMC simulation which will produce a statepoint.10.h5 file that contains the simulation outputs.
```bash
python python scripts/2_openmc_simulation_with_dagmc_geometry.py
```

Then run the CSG simulation which will produce a statepoint.10.h5 file that contains the simulation outputs.
```bash
python python scripts scripts/3_openmc_simulation_with_csg_geometry.py
```
