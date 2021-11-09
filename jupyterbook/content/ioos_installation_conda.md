# Installing the IOOS conda environment

For IOOS python users we recommend the free
[Miniconda](http://conda.pydata.org/miniconda.html) Python distribution,
a lightweight version of the [Anaconda Scientific Python Distribution](https://store.continuum.io/cshop/anaconda/).
While the full Anaconda distribution will also work,
it's faster to install Miniconda,
and you install only the packages you need.
If for some reason you decide later that you want the full Anaconda distribution,
you can install it by typing `conda install anaconda` using miniconda.

## Install

Download and install the appropriate Miniconda installer from [http://conda.pydata.org/miniconda.html](http://conda.pydata.org/miniconda.html).
With conda you can create environments that use any Python version (e.g. Python 2.7 or Python 3.x),
so install the latest Python 3.x and if find out later you need a Python 2.7 environment,
you can create one.
Windows users also need to choose between 32-bit (old Windows XP) or 64-bit (modern Windows) versions.

### Windows

Run the installer
Choose _Just Me_ (not _All Users_),
and choose a Install Location owned by you.
The default `%USERPROFILE%\AppData\Local\Continuum\Miniconda3` is fine,
but kind of long,
so if you have created some shorter directory like `c:\programs` that you own,
you might choose `c:\programs\Miniconda3`.

On the "Advanced Installation Options" screen,
leave the boxes checked if you want Miniconda 3 to be your default python.
If you are going to be switching from Python 2 to Python 3 or perhaps some other Python distribution,
it is best uncheck the boxes and use the `Anaconda Command Prompt` or `Anaconda Navigator` (see below for instructions) to start Anaconda.

### Linux/macOS

Copy-and-paste this in the terminal:

```shell
if [[ $(uname) == "Darwin" ]]; then
  url=https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
elif [[ $(uname) == "Linux" ]]; then
  url=https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
fi
curl $url -o miniconda.sh
sh miniconda.sh
export PATH=$HOME/miniconda3/bin:$PATH
```

and use all the default options, except for the license agreement where you must actively change it to `yes`.

## Create the IOOS conda environment

Download the [environment.yml](https://raw.githubusercontent.com/ioos/ioos_code_lab/main/.binder/environment.yml),
or the [environment-python_and_r.yml](https://raw.githubusercontent.com/ioos/ioos_code_lab/main/.binder/environment-python_and_r.yml) for a bigger environment with the R packages,
by right clicking with the mouse and choosing `save as...`,
or, on `macOS` and `Linux`, use these commands to download:

```bash
url=https://raw.githubusercontent.com/ioos/ioos_code_lab/main/.binder/environment.yml
curl $url -o environment.yml
```

Then from the directory where you saved the file above,
type the following commands in the terminal or Windows command prompt:

```bash
conda config --add channels conda-forge --force
conda config --set channel_priority strict
conda update --yes --all
conda env create --quiet --file environment.yml
```

The last line creates the IOOS environment,
and since lots of packages are downloaded,
you should probably go get a coffee.

Once the environment is done building, you can activate it by typing:

```bash
conda activate IOOS
```

## Exiting the IOOS environment

If you want to leave the IOOS environment and return to the root environment,
you can type

```bash
conda deactivate
```

## Updating the IOOS environment

To update an existing environment you can do,

```bash
conda update --all --yes
```

Sometimes that operation can be slow if you have a really old version of the environment, or even impossible to update.
In that case we recommend removing and re-creating the environment. To remove an existing environment you have to run:

```shell
conda env remove -name IOOS
```

and follow the instructions from above to re-create. Note that you don't need to re-install miniconda.
Just download a fresh version of the environment file and re-create it.

## Why we use and recommend conda

Conda users can just `conda install`,
which installs not only binary packages for their platform,
but the binary libraries they depend on.
So it's easier than `pip install` and, thanks to binary relocation,
more powerful than python wheels.
System-level installation of libraries and admin privileges are not required.
Check out [Travis Oliphant's blog piece](http://technicaldiscovery.blogspot.com/2013/12/why-i-promote-conda.html) for more info.

## How to get help

- Raise an issue [here](https://github.com/ioos/ioos_code_lab/issues)
- Please get help on the [IOOS-tech Google Group](https://groups.google.com/forum/?hl=en#!forum/ioos_tech)

## Appendix: conda-lock

Locking environments can be useful for reproducibility, Continuous Integration (CI), or when one requires faster installation.
The reason is because a locked environment saves the "solved" list of packages and only downloads them.
Making it much faster than creating from the environment file and ensuring that the same packages from the time you locked will be used.

To lock an environment you will need to install conda-lock,

```shell
conda install conda-lock
```

then execute the locking command targeting the environment file you want to lock and the platforms, like:

```shell
conda-lock -f environment.yml -p osx-64 -p linux-64 -p win-64
```

In the example above we are locking for macOS, Linux and Windows.
