# LEOHS: Landsat Harmonization using GEE
# Copyright (C) 2025 Galen Richardson
# This file is licensed under GPL-3.0-or-later
import warnings,joblib
from importlib.resources import files
from datetime import datetime
from .io import SR_TOA_geeNames, time_tracker
from .wrs import create_overlap_df
from .points import create_sampling_points
from .sampling import create_big_gdf
from .regression import process_all_regressions
def get_internal_wrs_path():
    wrs_dir = files('leohs.data')
    return str(wrs_dir / 'WRS_overlaps.shp')
def run_leohs(Aoi_shp_path, Save_folder_path, SR_or_TOA, months, years, sample_points_n,
              maxCloudCover=50,Regression_types=["OLS"], CFMask_filtering=True, Water=True, Snow=True):
    import ee,os
    from importlib.metadata import version
    pkg_version = version("leohs")
    ee.Authenticate()
    ee.Initialize()
    warnings.filterwarnings("ignore")
    wrs_shp_path = get_internal_wrs_path() #get the wrs path from internal
    logs=[]
    logs.append(f"LEOHS version {pkg_version}")
    print(f'Running leohs {pkg_version}')
    total_start=datetime.now()
    num_cores=min(joblib.cpu_count(), 16) - 2
    LS7, LS8=SR_TOA_geeNames(SR_or_TOA)
    Max_img_samples,Pixel_difference=10,1
    # Step 1: Create WRS grid
    overlap_df, frequency_gdf, full_AOI, logs = create_overlap_df(Aoi_shp_path, wrs_shp_path, Save_folder_path,SR_or_TOA, LS7, LS8,
                                                                  months,years,maxCloudCover,num_cores,logs)
    # Step 2: Create sampling points
    Sample_points_gdf, overlap_points_gdf, logs = create_sampling_points(full_AOI, sample_points_n, frequency_gdf, num_cores, logs)
    # Step 3: Sample pixel values
    big_gdf, logs = create_big_gdf(overlap_points_gdf, overlap_df, Max_img_samples, LS7, LS8, SR_or_TOA, num_cores,
                             CFMask_filtering, Water, Snow, Pixel_difference, Save_folder_path, logs)
    # Step 4: Run regressions
    logs = process_all_regressions(big_gdf, Regression_types, num_cores, Save_folder_path,SR_or_TOA, logs)
    #Finishing up
    total_time = time_tracker(total_start)# Logging
    logs.append(f"Total run time: {total_time}")
    with open(os.path.join(Save_folder_path,f'{SR_or_TOA.upper()}_LEOHS_harmonization.txt'), 'a') as file:
        file.write("\n=== LEOHS Processing Log ===")
        for line in logs:
            file.write("\n"+line)
    print(f"Logs have been saved to {Save_folder_path}, Total run time: {total_time} ")