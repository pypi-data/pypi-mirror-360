<img src="https://github.com/PyGLImER/PyGLImER/raw/master/docs/chapters/figures/logo_horizontal_colour.png" alt="PyGLImER logo" width="600"/>

[![Build Status](https://github.com/PyGLImER/PyGLImER/actions/workflows/test_on_push.yml/badge.svg?branch=master)](https://github.com/PyGLImER/PyGLImER/actions/workflows/test_on_push.yml) [![Documentation Status](https://github.com/PyGLImER/PyGLImER/actions/workflows/deploy_gh_pages.yml/badge.svg)](https://github.com/PyGLImER/PyGLImER/actions/workflows/deploy_gh_pages.yml) [![License: EUPL v1.2](https://img.shields.io/badge/license-EUPL--1.2-blue)](https://joinup.ec.europa.eu/collection/eupl/introduction-eupl-licence) [![codecov](https://codecov.io/gh/PyGLImER/PyGLImER/branch/master/graph/badge.svg?token=9WK7ZKIZ6N)](https://codecov.io/gh/PyGLImER/PyGLImER)

---

## A workflow to create a global database for Ps and Sp receiver function imaging of crustal and upper mantle discontinuties 

PyGLImER **automates receiver function (RF) processing from download of raw waveform data to common conversion point (CCP) imaging with a minimum amount of user interference.**

The implementation includes:

+ Functions to download raw waveform data from FDSN providers
+ Functions to feed in local waveform data
+ An adaptable preprocessing scheme, including various rotational algorithms
+ A variety of deconvolution algorithms (user-defined algorithms possible)
+ An implementation of the iasp91 and GyPSum velocity models for depth migration (user-defined models are accepted)
+ A new, particularly efficient Common Conversion Point Stacking algorithm
+ A variety of plotting tools to explore datasets and to create prublication ready figures
+ Efficient and fast processing and data management, support multi-processing, MPI, and HDF5

As developers, we are particularly concerned to create an **automated, adaptable, efficient, and, yet, easy-to-use** toolkit.

The project is largely based on the [ObsPy](https://github.com/obspy/obspy) project and can be seen as a more powerful and user-friendly
successor of the [GLImER](http://stephanerondenay.com/glimer-web.html) project.

## Installation of this package

### Installation from PyPi
PyGLImER is now deployed on PyPi and can simply be installed using:

```bash
pip install pyglimer
```

### Installation from source code
To obtain the latest updates, you can install PyGLImER from the source code, available on GitHub.

⚠️ **Developers should download the ``dev`` branch**

```bash
# Download via wget or web-browser
wget https://github.com/PyGLImER/PyGLImER/archive/refs/heads/master.zip

# For developers
wget https://github.com/PyGLImER/PyGLImER/archive/refs/heads/dev.zip

# unzip the package
unzip master.zip  # or dev.zip, depending on branch

# Change directory to the same directory that this repo is in (i.e., same directory as setup.py)
cd PyGLImER-master  # That's the standard name the folder should have

# Create the conda environment and install dependencies
conda env create -f environment.yml

# Activate the conda environment
conda activate pyglimer

# Install your package
pip install -e .
```

Optionally, you can test the package by running

```bash
pytest -p no:logging tests
```

## Getting started
Access PyGLImER's documentation [here](https://pyglimer.github.io/PyGLImER/).

PyGLImER comes with a few tutorials (Jupyter notebooks). You can find those in the `examples/` directory.

## What it looks like
With PyGLImER, we facilitate processing extremely large amounts of teleseismic data. This enables us to create large scale CCP sections as shown for P-to-S and S-to-P receiver function data in the plot below:

| <img src="https://github.com/PyGLImER/PyGLImER/raw/master/docs/chapters/figures/map_w_ccp_sections.png" alt="Map With CCP sections" width="600"/> |
|:--:| 
| *FIG: Seismic broadband stations with available receiver functions are plotted as downward-pointing red triangles. The locations of the shown cross-sections are demarked as bold black lines. Cross-sections A, B, and D are created from S receiver functions stacked by common conversion point, whereas cross-section C shows a slice through a P receiver function common conversion point stack. Data begin to fade to grey if the respective gridpoint is hit by fewer than 25 rays. Note that the vertical exaggeration varies from panel to panel.* |

PyGLImER also comes with a toolset to create publication ready figures:

| <img src="https://github.com/PyGLImER/PyGLImER/raw/master/docs/chapters/figures/combined.jpg" alt="Combined Stack and Section" width="400"/> |
|:--:|
| *FIG: Single station stack and receiver functions sorted by epicentral distance from P receiver function for station GE.DAG.* |

| <img src="https://github.com/PyGLImER/PyGLImER/raw/master/docs/chapters/figures/distr.jpg" alt="Distribution of back-azimuth and rayparameters" width="600"/> |
|:--:|
| *FIG: Distribution of back-azimuth and rayparameter for the P receiver functions from GE.DAG as shown above.* |

## Reporting Bugs / Contact the developers
This version is an early release. If you encounter any issues or unexpected behaviour, please [open an issue](https://github.com/PyGLImER/PyGLImER/issues/new) here on GitHub or [contact the developers](mailto:makus@gfz-potsdam.de).

## Citing PyGLImER
If you use PyGLImER to produce content for your publication, please consider citing us. For the time being, please cite our [AGU abstract](https://www.essoar.org/doi/10.1002/essoar.10506417.1).

## Latest
We are happy to announced that PyGLImER has been awarded an [ORFEUS](http://orfeus-eu.org/) software development grant and are looking forward to further develop this project.
