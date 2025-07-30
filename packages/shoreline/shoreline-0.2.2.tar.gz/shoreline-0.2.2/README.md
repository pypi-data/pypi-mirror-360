# NATURESCAPES `shoreline` Package
![PyPI - Format](https://img.shields.io/pypi/format/shoreline?link=https%3A%2F%2Fpypi.org%2Fproject%2Fshoreline%2F)

This is the repo for the Naturescapes `shoreline` package and research notebooks.

Utilities for ray casting, working with LineString resolution, and clipping rays have been organized as a Python package in the `src` directory. The main interface is provided by the `ShorelineAnalyzer` class.

**The minimum supported Python version is Python 3.10**.

## Usage (see `shoreline.ipynb` for example)
```python
from shoreline import ShorelineAnalyzer

# Create a new analyzer
analyzer = ShorelineAnalyzer()
sa = ShorelineAnalyzer(
    crs="EPSG:25829",
    shoreline="geodata/ireland/gadm36_IRL_shp/gadm36_IRL_0.shp",
    tideline="geodata/cleanup/Calculated Contours Backup/vorf_lat_simplified.gpkg",
    hat=2.09,
    lat=-2.44,
    wave_period=3.0,
    wave_height=2.0,
    ray_resolution=10,
    smoothing_window=500, # optional, defaults to 250
    origin_angle=0, # angle at which waves travel towards LAT; 0 is north, positive is clockwise
    origin_distance=1500 # distance in m from LAT bbox at which wave rays originate 
)
analysis = sa.evaluate()
# we now have a result object containing analysis metadata (.metadata), as well as geometries
# and summary stats
# call help(analysis) for more

# we can plot results if we're using a notebook. pl is a tuple of Matplotlib figures
pl = analysis.visualise_coastal_slopes()
# this gives us a (map, stats) tuple. Each figure can be saved
pl[0].savefig("dublin.png", dpi=300, bbox_inches="tight")
# you can also call the analysis.summary_stats property
# the computed ray and slope DataFrame is available as analysis.ray_data
```

## AnalysisResult Object Fields

The `AnalysisResult` object returned by `sa.evaluate()` contains the following fields:

### Metadata
- `metadata`: Dictionary containing analysis parameters including:
  - `timestamp`: ISO format timestamp of analysis
  - `analysis_crs`: The coordinate reference system used
  - `lat`/`hat`: Lowest/Highest Astronomical Tide values
  - `lat_crs`/`hat_crs`: Original CRS of LAT/HAT data
  - `wave_period`/`wave_height`: Wave parameters
  - `ray_resolution`: Resolution of ray casting in metres
  - `smoothing_window`: Window size used for smoothing

### Geometry Data
- `lat_line`: GeoDataFrame containing the LAT (Lowest Astronomical Tide) line
- `shore_line`: GeoDataFrame containing the HAT (Highest Astronomical Tide) shoreline
- `origin_rays`: GeoDataFrame containing the original rays before intersection
- `slopes`: GeoDataFrame containing the trimmed rays with calculated metrics (see below)
- `shoaling`: GeoDataFrame containing the line where waves begin shoaling
- `breaking`: GeoDataFrame containing the line where waves break
- `intertidal`: GeoDataFrame containing the intertidal zone polygon
- `score`: GeoDataFrame containing a LineString with impact intensity scores
- `intersections`: List of any ray intersections that were removed

### The `slopes` DataFrame
This is the main analysis output containing trimmed rays with the following columns:
- `geometry`: LineString geometries of rays from LAT to HAT
- `length`: Length of each ray in metres
- `start_depth`/`end_depth`: Depths at LAT and HAT
- `slope`: Gradient (rise/run)
- `slope_degrees`: Slope angle in degrees
- `slope_radians`: Slope angle in radians
- `slope_degrees_normalised`: Normalised slope values (0-1)
- `distance_to_breaking`: Distance from HAT to breaking line
- `distance_to_shoaling`: Distance from HAT to shoaling line
- `shoal_break_width`: Width between shoaling and breaking lines
- `distance_to_breaking_normalised`: Inverted normalised values (shorter = higher score)
- `distance_to_shoaling_normalised`: Inverted normalised values (shorter = higher score)
- `shoal_break_width_normalised`: Inverted normalised values (narrower = higher score)
- `geom_mean_normalised`: Geometric mean of the four normalised metrics, representing overall impact intensity (higher = more intense)

### Summary Statistics
- `metrics`: Array of calculated gradient metrics
- `friendly_metrics`: Dictionary version of metrics with descriptive names
- `pcbreaks`: Percentile breakpoints used for visualisation [10, 25, 50, 75, 90, 95]

### Methods
- `visualise_coastal_slopes()`: Returns a tuple of (map_figure, stats_figure) for visualisation
- `summary_stats`: Property that returns formatted summary statistics

## Sample output from [`shoreline.ipynb`](isobath_to_onshore.ipynb) (Dublin Bay)
![Dublin Bay](standard.png "Dublin Bay, with smoothed rays cast offshore to onshore")

## Sample output of a ray intersecting isobaths [`ray_slope.ipynb`](ray_slope.ipynb)
![Ray / Slope](ray_slope.png "Using a divergent colour scheme to visualise slope orientation")

# Installation
`uv add shoreline` or `pip install shoreline`

## Installing for local development
This project is developed using [`uv`](https://docs.astral.sh/uv/),  but should work with just pip. The use of a virtualenv is advised.

```shell
uv venv
source .venv/bin/activate
uv sync --all-extras

uv add --dev ipykernel
uv run ipython kernel install --user --env VIRTUAL_ENV $(pwd)/.venv --name=shoreline
uv run --with jupyter jupyter lab
```
When creating a notebook, select the **`shoreline`** kernel from the dropdown. Then use e.g. `!uv add pydantic` to add pydantic to the project's dependencies, or `!uv pip install pydantic` to install pydantic into the project's virtual environment without persisting the change to the project `pyproject.toml` or `uv.lock files`. Either command will make import pydantic work within the notebook

### Anaconda
For Anaconda users: you will probably have to pull the requirements out of `pyproject.toml`. Sorry!

## Testing
The smoothing algorithm is relatively well covered by tests (see `tests/test_utils.py`). Run `pytest` in the root dir in order to test if you'd like to tinker with it.

## Data
Are in the [`geodata`](geodata) folder.

## Copyright
Stephan Hügel / Naturescapes, 2025

## Funding
The NATURESCAPES project is funded by the European Union under Grant Agreement No 10108434
