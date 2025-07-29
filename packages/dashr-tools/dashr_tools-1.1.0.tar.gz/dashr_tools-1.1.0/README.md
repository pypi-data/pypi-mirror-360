# DASHR Tools

[![pipeline status](https://gitlab.oit.duke.edu/biomechanics/dashr-tools/badges/main/pipeline.svg)](https://gitlab.oit.duke.edu/biomechanics/dashr-tools/-/commits/main)
[![coverage report](https://gitlab.oit.duke.edu/biomechanics/dashr-tools/badges/main/coverage.svg)](https://gitlab.oit.duke.edu/biomechanics/dashr-tools/-/commits/main)
[![Latest Release](https://gitlab.oit.duke.edu/biomechanics/dashr-tools/-/badges/release.svg)](https://gitlab.oit.duke.edu/biomechanics/dashr-tools/-/releases)


This repository will contain tools and utilities to facilitate work with the Data Acquisition System for Head Response (DASHR) from Duke University's Injury Biomechanics Laboratory.

## Installation
There are two options to running and using the `dashr_tools` methods. The preferred method is using `poetry` to install
the package locally. Alternatively, you can copy the `dashr_tools` folder to your local development directory. 
Packages must be installed manually for this to work.

### Poetry installation
These installation instructions assume that you have an appropriate version of python already installed to your machine. 
`dashr_tools` requires python >= 3.12, and poetry version 2.0.1 or greater. `poetry` can be installed with `pip`, `conda` or `pipx`:
```commandline
pipx install poetry
# conda install poetry
# pip install poetry
```

With `poetry` installed...
```commandline
poetry install
```

You may run into an issue where your current version of poetry/python conflict with the bundled `poetry.lock` file. In that 
case, you may run `poetry lock` to rebuild that file. Worst case, delete the `poetry.lock` and run `poetry install` to rebuild
the environment. 

After installing, you may run any of the tools locally from this project folder. To use the `dashr_tools` elsewhere, you must
build and install based on the instructions for your desired package manager (e.g. `pip`)

```commandline
poetry build 
pip install  dist\dashr_tool-X.X.X-y.whl
```
Replace "X.X.X" and "y" with the appropriate build labels based on your local configuration. The python wheel should be in 
the dist folder.

## Reading DASHR files
The DASHR system produces raw binary (`.bin`) files. Each file contains a header with metadata, followed by acceleration, 
angular velocity, and auxiliary sensor data.
There are two versions of the DASHR system, which are automatically detected by the included package. One version contains
three axes of "high-range" acceleration data ($\pm$ 200g), three axes of angular velocity data ($\pm$ 4000 deg/s), temperature,
and ambient light. The other version additionally has three axes of "low-range" acceleration ($\pm$ 32g). The DASHR saves
data incrementally in fixed-size files. These must be stitched together to collect the full data trace from long collection 
sessions.

The `DASHRData` class can be used to load DASHR data files and folders.

```python
from dashr_tools import DASHRData
dashr_data = DASHRData(folder_path)
dashr_df = dashr_data.to_dataframe()
print(dashr_df.head())
print(dashr_df.columns, dashr_df.shape)
```

Alternatively, to load DASHR data, either single files can be imported, or an entire folder can be loaded at once.


To view compiled data, individual channels can be accessed from the `DASHRData` object:

```python
dashr_data.x_acceleration
dashr_data.z_gyro
dashr_data.temperature
```

```python
from dashr_tools.bin_reader import read_single, read_folder

# Read a single data file
filename = "C:/Some/Path/to/DASHR/Data/L0.bin"
single_file = read_single(filename) # returns a DASHRData object

# Read a full folder
folder_path = "C:/Some/Path/to/DASHR/Data"
dashr_data = read_folder(folder_path) # returns a DASHRData object
```


Each `DASHRData` can be operated on as a `pandas` `DataFrame` object with either `DASHRData.dataframe` or `DASHRData.to_dataframe()`.
As well, data can be dumped to disc using `DASHRData.to_csv()`. The `dataframe` object can be saved to any desired file format
using `pandas` built-ins.

# Device clock management
A commandline utility is provided to ensure DASHR timestamps are properly configured. The DASHR system has a real time clock (RTC)
which must be set through a serial connection to a computer. The `SerialConnection.py` script will run for 30 seconds (configurable in the script)
and will open communication with any detected DASHR devices, and will reset the clock to the current time. Accuracy is to within
one second. Currently, this only works with one device at a time.

# License
Code within this repository may not be used without the permission of a current member of the Duke University Injury Biomechanics Laboratory.

For questions as of February 6, 2025, contact Mitchell Abrams.