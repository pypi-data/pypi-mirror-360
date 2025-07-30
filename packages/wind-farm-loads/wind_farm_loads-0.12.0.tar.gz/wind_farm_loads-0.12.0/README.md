# Wind farm load surrogate

[![pipeline status](https://gitlab.windenergy.dtu.dk/surrogate-models/wind-farm-loads/badges/main/pipeline.svg)](https://gitlab.windenergy.dtu.dk/surrogate-models/wind-farm-loads/-/commits/main)
[![coverage report](https://gitlab.windenergy.dtu.dk/surrogate-models/wind-farm-loads/badges/main/coverage.svg)](https://gitlab.windenergy.dtu.dk/surrogate-models/wind-farm-loads/-/commits/main)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Couple a load surrogate model with PyWake and Floris.

The documentation is available at
https://surrogate-models.pages.windenergy.dtu.dk/wind-farm-loads/

## Installation instructions

The dependencies are managed with [Poetry](https://python-poetry.org/), and some are marked as optional.
To install all dependencies type
```
poetry install --all-extras
```
It is also possible to install only some optional dependencies, with
```
poetry install --extras "<option_1> <option_2>"
```
For example
```
poetry install --extras "pywake spyder"
```

The optional dependencies are listed in the following table

| Name          | Description                                            |
|---------------|--------------------------------------------------------|
| `pywake`      | Add PyWake                                             |
| `floris`      | Add Floris                                             |
| `spyder`      | Enable the use of Spyder with this virtual environment |
| `test`        | Enable testing                                         |
| `code_style`  | Enable code style checking                             |
| `docs`        | Enable building the documentation                      |
| `profiler`    | Enable time and memory profiler                        |

This package relies on [`surrogates-interface`](https://surrogate-models.pages.windenergy.dtu.dk/surrogate-models-interface/) to evaluate the loads. It is the responsibility of the user to select which surrogate model library to install. At the time of writing, the options are:

- `surrogates-interface[tf]` ➡️ TensorFlow
- `surrogates-interface[torch]` ➡️ PyTorch
- `surrogates-interface[smt]` ➡️ SMT

Poetry will write the location of the virtual environment. This is useful to delete it when it's not needed anymore, and also to select the python executable from Spyder.

To use Spyder go to Tools / Preferences / Python interpreter. Select "Use the following Python interpreter" and enter the path to python.exe in the virtual environment. It should look like `%userprofile%\AppData\Local\pypoetry\Cache\virtualenvs\wind-farm-loads-yjbA2zDm-py3.11.11\Scripts\python.exe`.

To run any command there are two options:

- Activate the virtual environment. That is, open a new command prompt, and then enter `%userprofile%\AppData\Local\pypoetry\Cache\virtualenvs\wind-farm-loads-yjbA2zDm-py3.12\Scripts\activate.bat`.
- Always write `poetry run` before anything. For example `poetry run python my_script.py`.
