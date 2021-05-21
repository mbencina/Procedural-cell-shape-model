# Procedural cell shape model

This project was done as a seminar work for a course in Advance Computer Graphics (Napredna računalniška grafika - NRG)

## Installation instructions

#### Requirements
- Python >= 3.9 (it should work with lower versions, but it was tested with 3.9).

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

