from pathlib import Path

from depfinder import notebook_path_to_dependencies

notebook_path = Path('.')
notebooks = list(notebook_path.glob('**/*.ipynb'))

## Get modules that are absent on GoogleColab
# required = []

# for notebook in notebooks:
#     try:
#         ret = notebook_path_to_dependencies(notebook)
#     except Exception as err:
#         print(f"Could not parse {notebook=}. {err}")
#     required.extend(ret["required"])

# modules = sorted(set(required))

## go to colab with this list and run to obtain the absent list

# """
# import importlib
# for module in modules:
#     if importlib.util.find_spec(module) is None:
#         print(module)
# """

## update notebooks
import nbformat

absent = [
    'bagit',
    'cartopy',
    'cf-units',
    'cf_xarray',
    'compliance-checker',
    'erddapy',
    'geoplot',
    'gridgeo',
    'ioos-tools',
    'ioos_qc',
    'ipyleaflet',
    'iris',
    'netcdf4',
    'oceans',
    'odvc',
    'owslib',
    'palettable',
    'pocean-core',
    'pyobis',
    'pyoos',
    'pysgrid',
    'pyugrid',
    'pyworms',
    'retrying',
    'seawater',
    'zarr',
]


code = """\
import subprocess
import sys
COLAB = "google.colab" in sys.modules

def _install(package):
    if COLAB:
        ans = input(f"Install {{ package }}? [y/n]:")
        if ans.lower() in ["y", "yes"]:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", package])
            print(f"{{ package }} installed!")

def _colab_install_missing_deps(deps):
    import importlib
    for dep in deps:
        if importlib.util.find_spec(dep) is None:
            if dep == "iris":
                dep = "scitools-iris"
            _install(dep)

deps = {}
_colab_install_missing_deps(deps)"""


def update_notebook(notebook, code):
    nb = nbformat.read(notebook, as_version=4)

    new_cell = nbformat.v4.new_code_cell(code)
    new_cell.pop('id')  # cannot save mod nb with this
    new_cell['metadata'] = {'tags': ['remove-cell']}  # won't render on jupyterbook
    # nb.cells.insert(0, new_cell)
    nb.cells[0] = new_cell
    nbformat.write(nb, notebook, version=4)


for notebook in notebooks:
    if 'archived' not in str(notebook):
        try:
            required = notebook_path_to_dependencies(notebook)['required']
            missing_from_colab = [module for module in absent if module in required]
            update_notebook(notebook, code.format(missing_from_colab))
        except Exception as err:
            print(f"Could not parse {notebook=}. {err}")
            continue
