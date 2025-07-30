# 🌍 LEOHS: Landsat Earth Observation Harmonization Script

**LEOHS** is a Python package for harmonizing Landsat 7 and 8 imagery using Google Earth Engine (GEE).
The harmonization functions generated from this tool can be used for long term landsat time series analysis.
LEOHS is designed specifically to create harmonization functions optimized for **user-defined study areas, time periods, and sampling parameters**.

---

## 🔧 Requirements

- **Python 3.10** — LEOHS must be run in its own environment
- an active **Google Earth Engine** account
- an area of interest shapefile

---

## 📦 Installation

### 1. Create a clean Python 3.10 environment (recommended name: `leohs_env`)
```bash
conda create -n leohs_env python=3.10 -y
conda activate leohs_env
```
### 2. Install LEOHS
```bash
pip install leohs
```
## 🚀 Example Usage
```python
import leohs
leohs.run_leohs(
    Aoi_shp_path=r"E:\Canada.shp",
    Save_folder_path=r"E:\Canada_output",
    SR_or_TOA="SR",
    months=[6,7,8],
    years=[2017],
    sample_points_n=100000)
```
## 🔧 `run_leohs` Parameters

- `Aoi_shp_path` *(str)*:  
  Path to your input AOI shapefile.
  
- `Save_folder_path` *(str)*:  
  Path to the output folder where results will be saved.
  
- `SR_or_TOA` *(str)*:  
  Type of Landsat imagery to process. Choose `"SR"` or `"TOA"`.

- `months` *(list of int)*:  
  List of months to include in image filtering (e.g., `[1,2,3,4,5,6,7,8,9,10,11,12]`).

- `years` *(list of int)*:  
  List of years to include in filtering (e.g., `[2013,2014,2015,2016,2017,2018,2019,2020,2021,2022]`).

- `sample_points_n` *(int)*:  
  Number of sample points to generate (e.g., `100000`). Max: **1,000,000**.

- `maxCloudCover` *(int, optional, default=50)*:  
  Maximum cloud cover (%) for image filtering.

- `Regression_types` *(list of str, optional, default=["OLS"])*:  
  List of regression models to run. Valid values: `"OLS"`, `"RMA"`, `"TS"`.

- `CFMask_filtering` *(bool, optional, default=True)*:  
  Whether to apply CFMask filtering (cloud, water, snow masking).

- `Water` *(bool, optional, default=True)*:  
  Allow water pixels (only effective if `CFMask_filtering=True`).

- `Snow` *(bool, optional, default=True)*:  
  Allow snow pixels (only effective if `CFMask_filtering=True`).
## 🛰️ Outputs

The following files are exported to the specified `Save_folder_path`:

- **Text log** (`TOA_LEOHS_harmonization.txt`):  
  Contains regression equations for each band, processing time, and diagnostic logs.

- **Heatmaps** (`.png` files):  
  Visualizations of pixel distributions between Landsat 7 and 8 for each band.

- **Sample point shapefile** (`.shp`, `.dbf`, `.shx`, etc.):  
  Contains the sampled locations and their associated pixel values.

- **Pixel and pair data** (`.csv`):  
  - Sampled pixel values for all matched images  
  - Image pair metadata (e.g., dates, paths, overlap score)

## 🐛 Known Issues

- **Google Earth Engine computation timeout**  
  Occasionally, you may encounter an `ee.EEException: Computation timed out` error. This can happen when GEE servers are under heavy load.  
  🛠️ **Recommended fix**: Simply wait a bit of time, and re-run `leohs.run_leohs(...)`. The issue usually resolves itself on retry.

## 📂 Additional Resources

Additional scripts for applying LEOHS, as well as global harmonization equations, can be found in the companion repository:  
🔗 [https://github.com/galenrichardson/LEOHS](https://github.com/galenrichardson/LEOHS)


## 📑 License

This project is licensed under the  
**GNU General Public License v3.0 or later (GPL-3.0-or-later)**  
© 2025 Galen Richardson

See the full license text in the [`LICENSE`](./LICENSE) file or at [gnu.org/licenses/gpl-3.0](https://www.gnu.org/licenses/gpl-3.0.html).

---

## 📬 Contact

**Author**: Galen Richardson  
**Email**: [galenrichardsonam@gmail.com](mailto:galenrichardsonam@gmail.com)
> Feel free to reach out for questions, bug reports, suggestions, or collaboration ideas.

