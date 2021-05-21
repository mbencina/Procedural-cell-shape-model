# Procedural cell shape model
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project was done as a seminar work for a course in Advanced Computer Graphics (Napredna računalniška grafika - NRG).  

### Project description
The goal of this seminar is to create a procedural model of call membrane shape extracted from real-life cell data. The
cell data can be obtained from Allan Cell institute database [1], where thousands of cells are labeled, and their shape
can be extracted and used for defining the membrane model parameters. Use statistical shape modeling (e.g. [3]) to
define a cell shape. The model must allow users to customize the basic cell shape parameters while retaining the
randomness of shape through model seed parameter. You can get a basic idea of what cells look like in [2].

## Installation instructions

#### Requirements
- Python >= 3.9 (it should work with lower versions, but it was tested with 3.9).  

Please also note that not all dependencies listed in _requirements.txt_ are actually required for running the project.

### Windows

Create and activate a virtual environment:

```bash
py -m venv venv
```

```bash
venv\Scripts\activate.bat
```

Install dependencies from _requirements.txt_:

```bash
pip install -r requirements.txt
```

To deactivate the environment run `deactivate`.

### Linux and MacOS

Create and activate a virtual environment:
```bash
virtualenv env
```

```bash
source env/bin/activate
```

Install dependencies from _requirements.txt_:

```bash
pip install -r requirements.txt
```
To deactivate the environment run `deactivate`.

## Running the project
After installation you can run the project using:
```bash
python main.py
```  

#### Adjustable basic cell shape parameters
You can adjust some parameters at the beginning of `main()` funcion in the file `main.py`

## References
[1] Membrane (CAAX). url: https://www.allencell.org/data-downloading.html  
[2] A. Kessel, “The Living Cell Gallery”. url: https://amit1b.wordpress.com/the-molecules-of-life/10-the-livingcell-gallery/  
[3] T. Vrtovec, D. Tomaževič, B. Likar, L. Travnik, F. Pernuš, “Automated Construction Of 3D Statistical Shape Models”, Image Analysis & Stereology, 2004.  

