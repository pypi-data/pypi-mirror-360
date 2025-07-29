# Allotaxonometer through Python


<p align="center">
  <img src="Allotax.png" alt="Allotax icon" width="300px"/>
</p>
<p align="center" style="font-size: 10px; color: gray;">
  <i>Allotax icon created by Julia W. Zimmerman</i>
</p>

The `py-allotax` implements a python interface to the `allotaxonometer-ui` library. This tool provides a way for users to input data and arguments and receive back a saved plot! The tool is designed to be used in a command line or in a python notebook in a few lines of code (see usage instructions at the bottom).


<div style="clear: both;"></div>
<br>

Table of contents:
- [Installation](#installation)
- [Usage instructions](#usage-instructions)
- [Developer Notes](#developer-notes)
- [Frequent questions or issues](#frequent-questions-or-issues)
- [Repo structure notes](#repo-structure-notes)
- [Resources](#resources)



## Installation

1. Requires `python3.11` or greater.

1. If JavaScript tool installs are needed (never used or installed `npm`, `nvm`, `node`):
    1. [Install `nvm`](https://github.com/nvm-sh/nvm?tab=readme-ov-file#installing-and-updating). `nvm` is a node version manager that streamlines installing the other 2.
    - Otherwise (not recommended): [steps to individually install `node` and `npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).
1. Once you have `nvm`, install the latest of both `node` and `npm` with:
    ```bash
    nvm install --lts
    ```
1. Activate your desired python environment.

1. Install package:
    ```bash
    pip3 install py-allotax
    ```


> Note:
> We use `puppeteer.js` under the hood, which is going to download a compatible Chrome during installation.

## Usage instructions

If working in a python notebook or script, you can install the package and use the function directly. Example data must be downloaded from the `example_data` directory to run the example below and those found in the `examples.ipynb`. [boys 2022](example_data/boys_2022.csv) and [boys 2023](example_data/boys_2023.json) are the examples used below.

```python
import os
from py_allotax.generate_svg import generate_svg

data_path1 = os.path.join("example_data", "boys_2022.json")
data_path2 = os.path.join("example_data", "boys_2023.json")

generate_svg(data_path1, data_path2, "test.pdf", "0.17", "Boys 2022", "Boys 2023")
```

If running the example, you can check your result against the [example output](example_charts).

To get help, you can run `?py_allotax.generate_svg.generate_svg` in a notebook cell to see argument descriptions.

> [!WARNING]
> Your own data must be in the `.json` format (see json examples in `example_data/`). If you have a `.csv` file, you can convert it to `.json` using `utils.convert_csv_data` (see `examples.ipynb`).


## Developer Notes
### Dependency Manager
[pdm](https://pdm-project.org/latest/#installation) is required for the build and testing.

### Setup
Once `pdm` is installed, run:
```
pdm sync
```
to install all python dependencies.

### Testing

To test the package without building and installing it, `cd` to py-allotax, install the node modules, then run:
```
pdm add -e . -dG dev
pdm run test # benchmarks excluded
```
These commands will add the package in editable mode as a development dependency then execute the tests written in the `tests` dir.

### Benchmarking

To benchmark the package:
```
pdm run benchmark
```
These commands will add the package in editable mode as a development dependency then execute the tests written in the `tests` dir.

### Package Build
Clone this repo and install the requirements:

```bash
git clone https://github.com/compstorylab/py-allotax.git &&
cd py-allotax &&
./scripts/build.sh
```

You should see a `.whl` file in the newly created `dist` directory.

## Frequent questions or issues

How much data can I run in this tool?
- The py-allotax supports approximately 2 GB of data. We recommend checking the size of your data files.

Will any data format work?
- There are specific column/variable names, and the data must be in `.json` format. The column names and formats vary across a few of the allotaxonometer tools, so there is a data format conversion function in `utils.py` to go from `.csv` to `.json`. See `examples.ipynb` for how to convert your data from `.csv` to `.json`.

Terminal says there is no `nvm` after installing it.
- Restart your terminal to activate it.

Terminal says there is no `node` even after I have already run `py-allotax` methods.
- This seems to happen when switching environments or changing branches. You can simply re-run the installs. You should already have `nvm` and be able to start from there.

I work in a high performance computing (HPC) environment (e.g., UVM's VACC) and the PDF won't render.
- In a HPC env, we discovered that a conda environment won't be able to discover your chromium location---a requirement to render the graph in a PDF. We recommend these solutions: 1) working locally instead, 2) in the HPC environment, run `get_rtd` only to get results and work with the data, 3) use the graph option to get the HTML only because you can open these in your own browser and screenshot or print if few are needed, or 4) the advanced workaround instructions below (we do not recommend as a first resort because the user will need to discover multiple paths).

    <details>
    <summary>Click for advanced workaround instructions to render PDFs in an HPC environment. Please note the default paths here are examples and will not be correct for your exact env; user will need to discover their exact paths for their env, python version, and chromium version. Get in touch if this is your only option.</summary>

    - **After following the normal installation steps, use the steps below, but amend the path for your username, conda environment containing the py_allotax library, python version, and chromium distribution.**
    1. Install this additional package in your env. This should let you do the convert data and RTD functions only **(you can stop here if PDF is unneeded)**.
        ```
        conda install -c conda-forge nodejs
        ```
    1. Get your py_allotax env location (paste it somewhere retrievable):
        ```
        conda info --envs | grep pyallotax
        ```
    1. Find your python version:
        ```
        python --version
        ```
    1. Change directories to your py_allotax env location:
        ```
        cd $HOME/miniconda3/envs/pyallotax/lib/python3.13/site-packages/py_allotax/
        ```
    1. Start by making a folder in this location:
        ```
        mkdir chrome
        ```
    1. Get the chromium executable location and copy its output (paste this path somewhere retrievable):
        ```
        node -e "console.log(require('puppeteer').executablePath())"
        ```
    1. Next steps need to be done carefully with your paths. This will copy the chromium files from its location into your py_allotax env location. The first path is the chromium location, and the second path is your py_allotax library location in your env:
        1. ```scp -r $HOME/.cache/puppeteer/chrome $HOME/miniconda3/envs/pyallotax/lib/python3.13/site-packages/py_allotax/chrome```
        1. ```scp -r $HOME/.cache/puppeteer/chrome-headless-shell $HOME/miniconda3/envs/pyallotax/lib/python3.13/site-packages/py_allotax/chrome```
        1. ```chmod +x $HOME/miniconda3/envs/pyallotax/lib/python3.13/site-packages/py_allotax/chrome/chrome/linux-138.0.7204.49/chrome-linux64/chrome```
        1. ```chmod +x $HOME/miniconda3/envs/pyallotax/lib/python3.13/site-packages/py_allotax/chrome/chrome-headless-shell/linux-138.0.7204.49/chrome-headless-shell-linux64/chrome-headless-shell```

    1. In your own script or python notebook, set this variable (replace with the location your copied the chromium location to within your py_allotax env)
        ```
        os.environ["PUPPETEER_EXECUTABLE_PATH"] = "~/miniconda3/envs/pyallotax/lib/python3.13/site-packages/py_allotax/chrome/chrome/linux-138.0.7204.49/chrome-linux64/chrome”
        ```

    </details>


I use Google colab or online-based coding environments only.
- Currently, this tool's dependencies may be difficult to install in an online environment. We recommend using Python virtual environments or Anaconda to create and manage Python environments locally. See below some shell instructions to get started with a Python virtual environment.

    <details>
    <summary>Click for Python virtual environment instructions</summary>

    - Navigate to ('change directory' with `cd`) the folder where your coding or related work lives. These instructions will create a folder here containing your environment, `env`. Inside the folder, python’s virtual environment library, `venv`, will create files and download libraries. Each time you activate this environment, you have access to its libraries and can manage them.
        ```
        cd path-to-create-env
        ```
    - Generate an `env` with a name such as `allotax_env`:
        ```
        python3 -m venv <name_of_env>
        ```
    - Activate (source) the `env`; unless you automate this step, you will need to do this each time you restart your shell or change `env`.
        - In the directory where your `env` is, enter `pwd` (print working directory) to get its full path. Copy that path and fill in below, leaving the `bin/activate` at the end:
            ```
            source /replace-wth-path-to/name_of_env/bin/activate
            ```
        - Now you can install the python packages needed or do other library management (type `pip help` for more commands).
    - You are set up to use a coding application (IDE) or command line to run this tool. If you do not have Anaconda, we recommend VS Code (where you can work with `.ipynb` files as you might in Jupyter or Colab).
    </details>


Where do I find the output?
- It is at the path you specified (argument provided) when you ran the `generate_svg`.

<br>
<br>

Users accessing these tools is our primary goal, so feel free to contact us by submitting an issue in the repo, emailing, or reaching out in one of our Slack spaces. Include these notes on your issue:
1. What exactly you did and steps leading up to it, and
2. Things you may have tried, and
3. The exact error message(s).


## Repo structure notes
- Inside `src`:
    - `generate_svg.py` is the main script to generate the pdf. You can run this from command line or in a notebook.
- Outside `src`: you can download `example_data` and `example_charts` and a notebook to run pre-constructed examples that use the library.


## Resources

- [Allotaxonometer-ui main package](https://github.com/Vermont-Complex-Systems/allotaxonometer-ui).
- [Allotaxonometer web app](https://vermont-complex-systems.github.io/complex-stories/allotaxonometry) which replaces the [old webpage](https://allotax.vercel.app/).
- The work and paper leading to these tools is [here](https://doi.org/10.1140/epjds/s13688-023-00400-x) with another paper describing the [allotaxonometer ecosystem of tools](https://arxiv.org/abs/2506.21808).

