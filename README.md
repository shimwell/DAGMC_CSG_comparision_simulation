<!-- [![CI with install](https://github.com/shimwell/cad-to-dagmc-to-openmc-example/actions/workflows/ci_with_install.yml/badge.svg)](https://github.com/shimwell/cad-to-dagmc-to-openmc-example/actions/workflows/ci_with_install.yml) -->

This example simulates a simplified model of an inertial confinement fusion reactor.


This example simulates a 90 degree sector model of a fusion reactor with
reflecting surfaces.

- A CAD model is made and automatically converted to a DAGMC geometry that is then used in OpenMC for a neutronics simulation.
- The neutronics simulation obtains the tritium breeding ratio and a 3D map of tritium production.
- The simulation outputs are post processed to display the results and produce a VTK file for visualization.


:point_right: :video_camera: [Link to video tutorial for this repository](https://youtu.be/QKTZpplFTw8) :video_camera:

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

# Making the DAGMC model

Make an environment for the model preparation
```
conda env create -f environment_cad.yml
conda activate env_cad
```

Then run the script for making the DAGMC model.
```bash
python 1_creation_of_dagmc_geometry.py
```

Then open the ```dagmc.html``` file in an internet browser to view the CAD created

![CAD geometry image](https://github.com/Shimwell/fusion_example_for_openmc_using_paramak/blob/main/reactor.png?raw=true)

Optionally you can inspect the DAGMC file at this stage by converting the h5m file to a vtk file and opening this with [Paraview](https://www.paraview.org/)
```
mbconvert dagmc.h5m dagmc.vtk
paraview dagmc.vtk
```
![DAGMC model image](https://user-images.githubusercontent.com/8583900/159941242-9d57e55d-e800-4bdb-81eb-9085eae70960.png)

# Simulating the model in OpenMC

First make an environment for simulation.

```
conda env create -f environment_neutronics.yml
conda activate env_neutronics
```

Then run the simulation which will produce a statepoint.10.h5 file that contains the simulation outputs
```bash
python 2_run_openmc_dagmc_simulation.py
```

Then run the post processing script that should output the Tritium Breeding Ratio to the terminal and make a VTK showing the neutron interactions resulting in tritium production
```bash
python 3_extract_results.py
```
