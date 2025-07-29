#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 15:00:59 2024

@author: thahn
"""

# =============================================================================
# This contains all of the functions to calculate basic bulk cell statistics (ETH, area, etc.) from CoCoMET-US data
# =============================================================================

import logging
from copy import deepcopy

import numpy as np
import pandas as pd
import xarray as xr
from tqdm import tqdm


# Calculate nearest item in list to given pivot
def find_nearest(array: np.ndarray, pivot) -> int:
    array = np.asarray(array)
    idx = (np.abs(array - pivot)).argmin()
    return idx


def calculate_var_max_height(
    analysis_object: dict,
    threshold: float,
    variable: str | None = None,
    cell_footprint_height: float = 2,
    quantile: float = 0.95,
    **args: dict,
) -> pd.DataFrame | None:
    """


    Parameters
    ----------
    analysis_object : dict
        A  CoMET-US standard analysis object containing at least US_tracks and US_segmentation_2d or US_segmentation_3d, and segmentation_xarray.
    threshold : float
        The value which needs to be exceeded to count towards the var top height. I.e. 15 for reflectivity.
    variable : str, optional
        The variable from the input segmentation_xarray which should be used for calculating var_max_height. The default is None.
    cell_footprint_height : float, optional
        The height used to calculate the cell area to determine where to calculate var_max_heights. The default is 2km.
    quantile : float, optional
        The percentile of calculated max heights to return. The default is 0.95.
    **args : dict
        Throw away inputs.

    Raises
    ------
    Exception
        Exception if missing segmentation data from the analysis object.

    Returns
    -------
    pandas.core.frame.DataFrame
        A pandas dataframe with the following rows: frame, feature_id, cell_id, max_height in km.

    """

    # If input variable field is 2D return None. Also, if DataArray, use those values for calculations. If Dataset, use tracking_var to get variable
    if type(analysis_object["segmentation_xarray"]) == xr.core.dataarray.DataArray:
        if len(analysis_object["segmentation_xarray"].shape) != 4:
            logging.warning("!=====Input Variable is not 3D=====!")
            return None

        variable_field = analysis_object["segmentation_xarray"]

    else:
        if len(analysis_object["segmentation_xarray"][variable].shape) != 4:
            logging.warning("!=====Input Variable is not 3D=====!")
            return None

        variable_field = analysis_object["segmentation_xarray"][variable]

    # If 3D segmentation is available, use that to calculate cell footprint, otherwise use 2D segmentation
    if analysis_object["US_segmentation_3d"] is not None:
        height_index = find_nearest(
            analysis_object["US_segmentation_3d"].altitude.values,
            cell_footprint_height * 1000,
        )

        footprint_data = analysis_object["US_segmentation_3d"].Feature_Segmentation[
            :, height_index
        ]

    elif analysis_object["US_segmentation_2d"] is not None:
        footprint_data = analysis_object["US_segmentation_2d"].Feature_Segmentation

    else:
        raise ValueError("!=====Missing Segmentation Input=====!")

    # Pull out your tracks DataFrame
    Tracks = analysis_object["US_tracks"]

    # Build lookup dicts
    features_by_frame = (Tracks.groupby("frame")["feature_id"].apply(list).to_dict())
    cell_by_frame_feat = (Tracks.groupby(["frame", "feature_id"])["cell_id"].min().to_dict())

    # Convert DataArrays to NumPy once
    footprint_np = footprint_data.values      
    var_np = variable_field.values      
    altitudes = variable_field.altitude.values  

    # Prepare the output dict
    max_height_info = {
        "frame": [],
        "feature_id": [],
        "cell_id": [],
        "max_height": [],
    }  # in km

    frame_groups = analysis_object["US_tracks"].groupby("frame")

    # Loop over frames → features
    for frame in tqdm(
        features_by_frame.keys(),
        desc=f"=====Calculating Max Heights=====",
        total=len(features_by_frame),
    ):
        for feature_id in features_by_frame[frame]:
            # get the precomputed cell_id
            cell_id = cell_by_frame_feat[(frame, feature_id)]

            # find all (y,x) pixels in this footprint
            idxs = np.argwhere(footprint_np[frame] == feature_id)
            if idxs.size == 0:
                max_height = np.nan
            else:
                # for each footprint pixel, find the highest altitude index > threshold
                heights = []
                for iy, ix in idxs:
                    col = var_np[frame, :, iy, ix] 
                    above = np.where(col > threshold)[0]
                    if above.size:
                        max_idx = above.max()
                        heights.append(altitudes[max_idx])
                    else:
                        heights.append(np.nan)

                # reduce by quantile (and convert to km)
                if np.all(np.isnan(heights)):
                    max_height = np.nan
                else:
                    max_height = np.nanquantile(heights, quantile) / 1000

            # append results
            max_height_info["frame"].append(frame)
            max_height_info["feature_id"].append(feature_id)
            max_height_info["cell_id"].append(cell_id)
            max_height_info["max_height"].append(max_height)

    # Return a DataFrame
    return pd.DataFrame(max_height_info)


def calculate_max_intensity(
    analysis_object: dict,
    variable: str | None = None,
    cell_footprint_height: float | None = None,
    **args,
) -> pd.DataFrame | None:
    """


    Parameters
    ----------
    analysis_object : dict
        A  CoCoMET-US standard analysis object containing at least US_tracks and US_segmentation_2d or US_segmentation_3d, and segmentation_xarray.
    variable : str, optional
        The variable from the input segmentation_xarray which should be used for calculating var_max_height. The default is None.
    cell_footprint_height : float, optional
        The height used to determine the location of which cells to calculate the max_intensity of. If None, will calculate the max_intensity of all cells. The default is None.
    quantile : float, optional
        The percentile of calculated max heights to return. The default is 0.95.
    **args : dict
        Throw away inputs.

    Raises
    ------
    Exception
        Exception if missing segmentation data from the analysis object.
        Exception if there is more than one frame associated with a feature id

    Returns
    -------
    pandas.core.frame.DataFrame
        A pandas dataframe with the following rows: frame, feature_id, cell_id, max_intensity where max_intensity is in the unit of the variable.

    """

    # If DataArray, use those values for calculations. If Dataset, use tracking_var to get variable
    if type(analysis_object["segmentation_xarray"]) == xr.core.dataarray.DataArray:
        variable_field = analysis_object["segmentation_xarray"]

    else:
        variable_field = analysis_object["segmentation_xarray"][variable]

    # If 3D segmentation is available, use that to calculate cell footprint, otherwise use 2D segmentation
    if analysis_object["US_segmentation_3d"] is not None:
        segmentation = analysis_object["US_segmentation_3d"].Feature_Segmentation
        segmentation = analysis_object["US_segmentation_3d"].Feature_Segmentation

        if cell_footprint_height is not None:
            height_index = find_nearest(
                analysis_object["US_segmentation_3d"].altitude.values,
                cell_footprint_height * 1000,
            )

            features_across_footprint = np.unique(segmentation[:, height_index])[1:]

        else:
            features_across_footprint = np.unique(segmentation)[1:]

    elif analysis_object["US_segmentation_2d"] is not None:
        segmentation = analysis_object["US_segmentation_2d"].Feature_Segmentation
        features_across_footprint = np.unique(segmentation)[1:]

    else:
        raise ValueError("!=====Missing Segmentation Input=====!")

    max_intensity_info = {
        "frame": [],
        "feature_id": [],
        "cell_id": [],
        "max_intensity": [],
    }
    Tracks = analysis_object["US_tracks"]

    # Lookup dict to avoid groupby
    frames_by_feat = dict(zip(Tracks["feature_id"], Tracks["frame"]))
    cells_by_feat  = dict(zip(Tracks["feature_id"], Tracks["cell_id"]))

    # Convert DataArrays to plain NumPy arrays once
    seg_np = segmentation.values         # shape (n_frames, H, W)
    var_np = variable_field.values       # same shape

    # Loop over each frame, then apply a mask for the cell/feature, then within that find the highest val
    for feature_id, frame in tqdm(
        frames_by_feat.items(),
        desc="=====Calculating Max Intensity=====",
        total=len(frames_by_feat),
    ):
        # If feature covers your footprint set, compute its max; else NaN
        if feature_id in features_across_footprint:
            # mask & reduce in pure NumPy
            one_feat = np.where(
                seg_np[frame] == feature_id,
                var_np[frame],
                0,
            )
            max_val = np.nanmax(one_feat)
        else:
            max_val = np.nan

        # Append straight from our dicts no more groupby inside
        max_intensity_info["frame"].append(frame)
        max_intensity_info["feature_id"].append(feature_id)
        max_intensity_info["cell_id"].append(cells_by_feat[feature_id])
        max_intensity_info["max_intensity"].append(max_val)

    return pd.DataFrame(max_intensity_info)


def calculate_area(
    analysis_object: dict,
    height: float = 2,
    variable: str | None = None,
    threshold: float | None = None,
    **args: dict,
) -> pd.DataFrame:
    """


    Parameters
    ----------
    analysis_object : dict
        A CoCoMET-US standard analysis object containing at least US_tracks and US_segmentation_2d or US_segmentation_3d.
    height : float, optional
        The height which is used to calculate the area of cells. The default is 2km.
    variable : str, optional
        Variable to which we should apply the threshold. The default is None.
    threshold : float, optional
        Value of which the area should be greater than. The default is None.
    **args : dict
        Throw away variables.

    Raises
    ------
    Exception
        Exception if missing segmentation input from the analysis object.

    Returns
    -------
    pandas.core.frame.DataFrame
        A pandas dataframe with the following rows: frame, feature_id, cell_id, area where area is in km^2.

    """

    # If 3D segmentation is available, use that at given height, otherwise use 2D segmentation
    if analysis_object["US_segmentation_3d"] is not None:
        height_index = find_nearest(
            analysis_object["US_segmentation_3d"].altitude.values, height * 1000
        )

        mask = analysis_object["US_segmentation_3d"].Feature_Segmentation[
            :, height_index
        ]

    elif analysis_object["US_segmentation_2d"] is not None:
        mask = analysis_object["US_segmentation_2d"].Feature_Segmentation

    else:
        raise ValueError("!=====Missing Segmentation Input=====!")

    # Enforce threshold if present
    if threshold is not None:
        # Load background varaible
        if type(analysis_object["segmentation_xarray"]) == xr.core.dataarray.DataArray:
            variable_field = analysis_object["segmentation_xarray"]
        else:
            variable_field = analysis_object["segmentation_xarray"][variable]

        if len(variable_field.shape) == 4:
            height_index = find_nearest(
                analysis_object["segmentation_xarray"]["altitude"].values, height * 1000
            )

            variable_field = variable_field[:, height_index]

        mask.values[variable_field.values < threshold] = -1

    area_info = {"frame": [], "feature_id": [], "cell_id": [], "area": []}  # in km^2

    # We first calculate the area of each individual cell
    # First get the size of each dimension
    x_dim_sizes = np.abs(np.diff(mask.projection_x_coordinate))
    y_dim_sizes = np.abs(np.diff(mask.projection_y_coordinate))

    # These are one cell too small due to how diff works, so infer last cell size using the same cell size as the previous cell
    # x_dim_sizes.append(x_dim_sizes[-1])
    x_dim_sizes = np.append(x_dim_sizes, x_dim_sizes[-1])
    y_dim_sizes = np.append(y_dim_sizes, y_dim_sizes[-1])

    # Multiply each cell by the other to get an area for one individual cell
    cell_areas = np.outer(y_dim_sizes, x_dim_sizes)

    frame_groups = analysis_object["US_tracks"].groupby("frame")

    # Loop over frames
    for ii, frame in tqdm(
        enumerate(frame_groups),
        desc="=====Calculating Areas=====",
        total=frame_groups.ngroups,
    ):
        # Loop over each feature
        for feature in frame[1].groupby("feature_id"):
            # Get valid indices of a given features
            proper_indices = np.argwhere(mask[frame[0]].values == feature[0])

            # Cells which have no segmented output should get a NaN
            if len(proper_indices) == 0:
                area_info["frame"].append(frame[0])
                area_info["feature_id"].append(feature[0])
                area_info["cell_id"].append(feature[1]["cell_id"].min())
                area_info["area"].append(np.nan)
                continue

            # Sum up all the areas that comprise it
            total = np.sum([cell_areas[iy, ix] for iy, ix in proper_indices])

            # Push info to dictionary
            area_info["frame"].append(frame[0])
            area_info["feature_id"].append(feature[0])
            area_info["cell_id"].append(feature[1]["cell_id"].min())
            area_info["area"].append(total / 1e6)

    return pd.DataFrame(area_info)


def calculate_volume(
    analysis_object: dict,
    variable: str | None = None,
    threshold: float | None = None,
    **args: dict,
) -> pd.DataFrame:
    """


    Parameters
    ----------
    analysis_object : dict
        A CoCoMET-US standard analysis object containing at least US_tracks and US_segmentation_3d.
    variable : str, optional
        Variable to which we should apply the threshold. The default is None.
    threshold : float, optional
        Value of which the area should be greater than. The default is None.
    **args : dict
        Throw away variables.

    Raises
    ------
    Exception
        Exception if missing segmentation input from the analysis object.

    Returns
    -------
    pandas.core.frame.DataFrame
        A pandas dataframe with the following rows: frame, feature_id, cell_id, volume where area is in km^3.

    """

    if analysis_object["US_segmentation_3d"] is None:
        raise ValueError(
            "!=====3D Segmentation Data is Required for Volume Calculation=====!"
        )

    mask = analysis_object["US_segmentation_3d"].Feature_Segmentation

    if threshold is not None:
        # Load background varaible
        if type(analysis_object["segmentation_xarray"]) == xr.core.dataarray.DataArray:
            variable_field = analysis_object["segmentation_xarray"]
        else:
            variable_field = analysis_object["segmentation_xarray"][variable]

        if len(variable_field.shape) != 4:
            raise ValueError(
                "=====Must have a 3D segmentation_xarray for threshold application====="
            )

        # Enforce threshold
        mask.values[variable_field.values < threshold] = -1

    volume_info = {
        "frame": [],
        "feature_id": [],
        "cell_id": [],
        "volume": [],  # in km^3
    }

    # We first calculate the area of each individual cell
    # First get the size of each dimension
    x_dim_sizes = np.diff(mask.projection_x_coordinate)
    y_dim_sizes = np.diff(mask.projection_y_coordinate)
    z_dim_sizes = np.diff(mask.altitude)

    # These are one cell too small due to how diff works, so infer last cell size using the same cell size as the previous cell
    # x_dim_sizes.append(x_dim_sizes[-1])
    x_dim_sizes = np.append(x_dim_sizes, x_dim_sizes[-1])
    y_dim_sizes = np.append(y_dim_sizes, y_dim_sizes[-1])
    z_dim_sizes = np.append(z_dim_sizes, z_dim_sizes[-1])

    # use Einstein sum notation to get volume of cells
    cell_volumes = np.einsum("i,j,k->ijk", z_dim_sizes, y_dim_sizes, x_dim_sizes)

    frame_groups = analysis_object["US_tracks"].groupby("frame")

    # Loop over frames
    for ii, frame in tqdm(
        enumerate(frame_groups),
        desc="=====Calculating Volumes=====",
        total=frame_groups.ngroups,
    ):
        # Loop over each feature
        for feature in frame[1].groupby("feature_id"):
            # Get valid indices of a given features
            proper_indices = np.argwhere(mask[frame[0]].values == feature[0])

            # Cells which have no segmented output should get a NaN
            if len(proper_indices) == 0:
                volume_info["frame"].append(frame[0])
                volume_info["feature_id"].append(feature[0])
                volume_info["cell_id"].append(feature[1]["cell_id"].min())
                volume_info["volume"].append(np.nan)
                continue

            # Sum up all the volumes that comprise it
            total = np.sum([cell_volumes[iz, iy, ix] for iz, iy, ix in proper_indices])

            # Push info to dictionary
            volume_info["frame"].append(frame[0])
            volume_info["feature_id"].append(feature[0])
            volume_info["cell_id"].append(feature[1]["cell_id"].min())
            volume_info["volume"].append(total / 1e9)

    return pd.DataFrame(volume_info)


def calculate_velocity(
    analysis_object: dict,
    **args: dict,
) -> pd.DataFrame:
    """


    Parameters
    ----------
    analysis_object : dict
        A CoCoMET-US standard analysis object containing at least US_tracks and tracking_xarray.
    **args : dict
        Throw away variables.

    Raises
    ------
    Exception
        Exception if missing tracks input from the analysis object.

    Returns
    -------
    pandas.core.frame.DataFrame
        A pandas dataframe with the following rows: frame, feature_id, cell_id, velocity where velocity is in m/s or m/frame.

    """

    if analysis_object["US_tracks"] is None:
        raise ValueError("!=====Tracks Data is Required for Velocity Calculation=====!")

    # Check if altitude values are present
    dim = 2
    if "up_down" in analysis_object["US_tracks"]:
        if np.isfinite(np.nanmax(analysis_object["US_tracks"]["up_down"])):
            dim = 3

    # Get dt
    if ("tracking_xarray" in analysis_object) and (
        "DT" in analysis_object["tracking_xarray"].attrs
    ):
        dt_from_tracking = analysis_object["tracking_xarray"].attrs["DT"]  # in s
    else:
        dt_from_tracking = 1.0
        logging.warning("Could not find DT in dataset, computing velocity in m/frame")

    def calculate_row_velocity(row1, row2, dt_arr, dim):
        # given 2 rows of the tracks dataframe, compute the distance between the 2 in 3 components:
        x1 = row1["projection_x"]
        x2 = row2["projection_x"]
        y1 = row1["projection_y"]
        y2 = row2["projection_y"]

        # f2 = row1["frame"]
        # f1 = row2["frame"]

        t1 = row1["time"]
        t2 = row2["time"]

        dt = (
            t2 - t1
        ).total_seconds()  # If a cell is not tracked for a frame, account for this (e.x. cell is in frame 1 and 3)

        distancecomps = ((y2 - y1), (x2 - x1))
        distance = np.sqrt(distancecomps[0] ** 2 + distancecomps[1] ** 2)

        velocity = ((y2 - y1) / dt, (x2 - x1) / dt)
        speed = np.sqrt((velocity[0]) ** 2 + (velocity[1]) ** 2)

        if dim == 3:
            z1 = row1["altitude"] * 1000
            z2 = row2["altitude"] * 1000

            distancecomps = ((z2 - z1), (y2 - y1), (x2 - x1))
            distance = np.sqrt(
                distancecomps[0] ** 2 + distancecomps[1] ** 2 + distancecomps[2] ** 2
            )

            velocity = ((z2 - z1) / dt, (y2 - y1) / dt, (x2 - x1) / dt)
            speed = np.sqrt(velocity[0] ** 2 + velocity[1] ** 2 + velocity[2] ** 2)

        return (distancecomps, distance, velocity, speed)

    Tracks = deepcopy(analysis_object["US_tracks"])
    velocity_info = {
        "frame": [],
        "feature_id": [],
        "cell_id": [],
        "velocity": [],  # in m / s
        "speed": [],  # in m / s
    }

    # Make dt into an array
    if type(dt_from_tracking) is list or type(dt_from_tracking) is np.ndarray:
        # Check that the number of frames and the number of dt"s are the same
        dt_array = list(dt_from_tracking)  # append the last value from the list
        dt_array.append(dt_from_tracking[-1])
    else:
        dt_array = np.ones(len(np.unique(Tracks["frame"])) + 1) * dt_from_tracking

    for cell in tqdm(
        Tracks.groupby("cell_id"),
        desc="=====Calculating Cell Velocities=====",
        total=len(np.unique(Tracks.cell_id.values)),
    ):
        for ii in range(len(cell[1].feature_id.values)):
            # check if last row
            if ii == (len(cell[1].feature_id.values) - 1):
                velocity_info["frame"].append(cell[1].iloc[ii].frame)
                velocity_info["feature_id"].append(cell[1].iloc[ii].feature_id)
                velocity_info["cell_id"].append(cell[0])
                velocity_info["velocity"].append(np.nan)
                velocity_info["speed"].append(np.nan)
                continue

            # else calculate speed / velocity based off of next frame
            dat_out = calculate_row_velocity(
                cell[1].iloc[ii], cell[1].iloc[ii + 1], dt_array, dim
            )

            velocity_info["frame"].append(cell[1].iloc[ii].frame)
            velocity_info["feature_id"].append(cell[1].iloc[ii].feature_id)
            velocity_info["cell_id"].append(cell[0])
            velocity_info["velocity"].append(dat_out[-2])
            velocity_info["speed"].append(dat_out[-1])

    # for i in tqdm(
    #     Tracks.index,
    #     desc="=====Calculating Cell Velocities=====",
    #     total=len(Tracks.index),
    # ):
    #     cell_id = Tracks.iloc[i]["cell_id"]
    #     frame = Tracks.iloc[i]["frame"]
    #     feature_id = Tracks.iloc[i]["feature_id"]

    #     velocity_info["frame"].append(frame)
    #     velocity_info["feature_id"].append(feature_id)
    #     velocity_info["cell_id"].append(cell_id)

    #     if Tracks.iloc[i]["frame"] == np.min(Tracks["frame"]) and cell_id != -1:
    #         velocity_info["velocity"].append(tuple(np.zeros(dim)))
    #         velocity_info["speed"].append(0)

    #     # why?????????
    #     elif cell_id not in Tracks[:i]["cell_id"].values:  # check if this is a new cell
    #         # if new, look for closest cell in same frame to copy velocity from
    #         same_frame_index_list = Tracks.index[
    #             Tracks["frame"] == Tracks.iloc[i]["frame"]
    #         ].tolist()
    #         same_frame_index_list.remove(i)
    #         if len(same_frame_index_list) == 0:
    #             velocity_info["velocity"].append(tuple(np.zeros(dim)))
    #             velocity_info["speed"].append(0)
    #             continue

    #         min_distance = np.inf
    #         closest_vel = tuple(np.zeros(dim))
    #         closest_speed = 0
    #         for j in same_frame_index_list:
    #             target_row = Tracks.iloc[j]
    #             if len(velocity_info["velocity"]) < j:
    #                 continue

    #             target_velocity = velocity_info["velocity"][j]
    #             target_speed = velocity_info["speed"][j]

    #             distance = calculate_row_velocity(
    #                 Tracks.iloc[i], target_row, dt_array, dim
    #             )[1]

    #             if distance < min_distance:
    #                 min_distance = distance
    #                 closest_vel = target_velocity
    #                 closest_speed = target_speed

    #         # If there are no other cells in the frame, append 0
    #         velocity_info["velocity"].append(closest_vel)
    #         velocity_info["speed"].append(closest_speed)

    #     else:
    #         # if the cell is not new, determine velocity from the change in position from previous frame
    #         index = np.argwhere(Tracks[:i]["cell_id"].values == cell_id)[-1][
    #             0
    #         ]  # index of previous row with same cell id
    #         velocity_speed = calculate_row_velocity(
    #             Tracks.iloc[i], Tracks.iloc[index], dt_array, dim
    #         )[2:]
    #         velocity_info["velocity"].append(velocity_speed[0])
    #         velocity_info["speed"].append(velocity_speed[1])

    # for i in Tracks.index:
    #     cell_id = Tracks.iloc[i]["cell_id"]
    #     if velocity_info["velocity"][i] == tuple(
    #         np.zeros(dim)
    #     ):  # go back and look at where velocity was set to zero and see if we can extrapolate backwards
    #         index_list = list(np.argwhere(Tracks["cell_id"].values == cell_id))
    #         index_list.remove(i)
    #         if len(index_list) == 0:
    #             continue
    #         velocity_info["velocity"][i] = velocity_info["velocity"][index_list[0][0]]
    #         velocity_info["speed"][i] = velocity_info["speed"][index_list[0][0]]

    velocity_info_df = pd.DataFrame(velocity_info)

    return velocity_info_df


def calculate_cell_growth(
    analysis_object: dict,
    variable: str,
    threshold: float | None = None,
    **args: dict,
) -> pd.DataFrame:
    """


    Parameters
    ----------
    analysis_object : dict
        A CoCoMET-US standard analysis object containing at least US_tracks.
    variable : str
        Variable to which we should apply the threshold.
    threshold : float, optional
        Value of which the area should be greater than. The default is None.
    **args : dict
        Throw away variables.

    Raises
    ------
    Exception
        Exception if missing tracks input from the analysis object.
        Exception if the segmentation data is not 2D or 3D.

    Returns
    -------
    pandas.core.frame.DataFrame
        A pandas dataframe with the following rows: frame, feature_id, cell_id, cell_growth where cell_growth is in m^3 / s.

    """

    if analysis_object["US_tracks"] is None:
        raise ValueError("!=====Tracks Data is Required for Velocity Calculation=====!")

    def _variable_lookup(analysis_object, var, **args):

        if var == "var_max_height":
            variable = "max_height"
            return calculate_var_max_height(analysis_object, **args)["max_height"]
        elif var == "max_intensity":
            return calculate_max_intensity(analysis_object, **args)["max_intensity"]
        elif var == "area":
            return calculate_area(analysis_object, **args)["area"]
        elif var == "volume":
            return calculate_volume(analysis_object, **args)["volume"]
        elif var == "velocity" or var == "speed":
            variable = "speed"
            return calculate_velocity(analysis_object, **args)["speed"]
        elif var == "perimeter":
            return calculate_perimeter(analysis_object, **args)["perimeter"]
        elif var == "convexity":
            return calculate_irregularity(analysis_object, **args)["convexity"]
        elif var == "sphericity":
            return calculate_irregularity(analysis_object, **args)["sphericity"]
        else:
            raise KeyError("!=====Invalid variable for cell growth rate=====!")

    # Check if the code is 3D
    if analysis_object["US_segmentation_3d"] is not None:

        dim = 3

        # If there is a given variable use that
        # TODO: there's definitely a better way to do this. in _variable_lookup maybe if variable is None default to either volume or area
        var = _variable_lookup(analysis_object, var=variable, **args)

    # If there is no 3D segmentation check if there is 2D
    elif analysis_object["US_segmentation_2d"] is not None:

        dim = 2

        # If there is a given variable use that
        if variable != None:
            if variable in args:
                var = args[variable][variable]
            else:
                var = _variable_lookup(analysis_object, var=variable, **args)

        # If there is no variable, default to area
        else:
            if "area" in args:
                var = args["area"]["area"]
            else:
                var = _variable_lookup(analysis_object, var="area", **args)

    else:
        raise Exception("!=====Missing Segmentation Input=====!")

    # Get Tracks
    Tracks = analysis_object["US_tracks"]
    Tracks_with_var = deepcopy(Tracks).join(var)

    # Get dt
    if ("tracking_xarray" in analysis_object) and (
        "DT" in analysis_object["tracking_xarray"].attrs
    ):
        dt_from_tracking = analysis_object["tracking_xarray"].attrs["DT"]  # in s
    else:
        dt_from_tracking = 1.0
        logging.warning("Could not find DT in dataset, computing velocity in m/frame")

    # Cell Growth Rate
    cell_growth_info = {"frame": [], "feature_id": [], "cell_id": [], "cell_growth": []}

    # List all of the unique cells and make sure there are no non-physical cells
    cell_groups = Tracks_with_var.groupby("cell_id")

    for cell_id, cell_g in tqdm(
        cell_groups,
        desc="=====Calculating Cell Growth Rates=====",
        total=len(cell_groups),
    ):
        cell_feature_arr = np.array(cell_g["feature_id"]).tolist()
        cell_frame_arr = np.array(cell_g["frame"]).tolist()
        cell_arr = [cell_id] * len(cell_frame_arr)
        cell_var_arr = np.array(cell_g[cell_g.columns[-1]])

        cell_lifetime_arr = np.array(
            cell_g["lifetime"] / np.timedelta64(1, "s")
        )  # convert from ns to s

        # If the cell only lives for one frame, make sure each other array is also one frame, then append nan
        if len(cell_lifetime_arr) == 1:
            assert len(cell_frame_arr) == 1
            assert len(cell_feature_arr) == 1
            assert len(cell_arr) == 1

            cell_growth_info["frame"].append(cell_frame_arr[0])
            cell_growth_info["feature_id"].append(cell_feature_arr[0])
            cell_growth_info["cell_id"].append(cell_arr[0])
            cell_growth_info["cell_growth"].append(np.nan)
            continue

        # If the cell lasts for more than one frame, calculate delta var and delta t
        dvar = cell_var_arr[1:] - cell_var_arr[:-1]
        if type(dt_from_tracking) == np.ndarray or type(dt_from_tracking) == list:

            if type(dt_from_tracking) != np.ndarray:
                dt_from_tracking = np.array(dt_from_tracking)
            # the line below does not work if cell frames are discontinuous
            # dt = dt_from_tracking[cell_frame_arr[0] : cell_frame_arr[-1]] 

            # instead use
            dt = []
            for find, f in enumerate(cell_frame_arr[:-1]):
                dt_across_many_frames = np.sum(dt_from_tracking[f : cell_frame_arr[ find + 1 ]])
                dt.append(dt_across_many_frames)

        else:
            dt = np.diff(cell_frame_arr) * dt_from_tracking

        # The eth/t slope is the growth rate
        slope = dvar / dt
        slope = slope.tolist()
        slope.append(np.nan)

        # Iterate through each element and append them to the info array
        cell_growth_info["frame"].extend(cell_frame_arr)
        cell_growth_info["feature_id"].extend(cell_feature_arr)
        cell_growth_info["cell_id"].extend(cell_arr)
        cell_growth_info["cell_growth"].extend(slope)

    cell_growth_df = pd.DataFrame(cell_growth_info)
    uncut_feature_list = np.unique(cell_growth_df["feature_id"].values)

    # Enforce the threshold
    if threshold is not None:
        # Load background varaible
        if type(analysis_object["segmentation_xarray"]) == xr.core.dataarray.DataArray:
            variable_field = analysis_object["segmentation_xarray"]
        else:
            variable_field = analysis_object["segmentation_xarray"][variable]

        if len(variable_field.shape) != 4 and len(variable_field.shape) != 3:
            raise ValueError("=====The segmentation must be 2D or 3D=====")

        feature_mask = analysis_object[f"US_segmentation_{dim}d"].Feature_Segmentation
        feature_mask.values[variable_field.values < threshold] = -1
        uncut_feature_list = np.unique(feature_mask)[1:]  # don"t use -1
        cell_growth_df = cell_growth_df[
            cell_growth_df["feature_id"].isin(uncut_feature_list)
        ]

    cell_growth_df.sort_values("feature_id", inplace=True)
    cell_growth_df.set_index(np.arange(len(cell_growth_df["feature_id"])), inplace=True)

    return cell_growth_df


def calculate_perimeter(  # TODO: split into surface area and perimeter
    analysis_object: dict,
    variable: str | None = None,
    threshold: float | None = None,
    **args: dict,
) -> pd.DataFrame:
    """

    Parameters
    ----------
    analysis_object : dict
        A CoCoMET-US standard analysis object containing at least US_tracks.
    variable : str, optional
        Variable to which we should apply the threshold. The default is None.
    threshold : float, optional
        Value of which the area should be greater than. The default is None.
    **args : dict
        Throw away variables.

    Raises
    ------
    Exception
        Exception if missing tracks input from the analysis object.
        Exception if the segmentation data is not 2D or 3D.

    Returns
    -------
    pandas.core.frame.DataFrame
        A pandas dataframe with the following rows: frame, feature_id, cell_id, perimeter where perimeter is in km.

    """

    if analysis_object["US_tracks"] is None:
        raise Exception("!=====Tracks Data is Required for Perimeter Calculation=====!")

    # Check if there is 2D segmentation
    if "height" in args and analysis_object["US_segmentation_3d"] is not None:
        altitudes = analysis_object["segmentation_xarray"]["altitudes"]

        height_index = find_nearest(altitudes, args["height"] * 1000)
        feature_seg = analysis_object["US_segmentation_3d"].Feature_Segmentation[
            :, height_index
        ]

        # define some useful variables
        proj_x = analysis_object[f"US_segmentation_3d"].projection_x_coordinate
        proj_y = analysis_object[f"US_segmentation_3d"].projection_y_coordinate

    elif analysis_object["US_segmentation_2d"] is not None:
        feature_seg = analysis_object["US_segmentation_2d"].Feature_Segmentation

        # define some useful variables
        proj_x = analysis_object[f"US_segmentation_2d"].projection_x_coordinate
        proj_y = analysis_object[f"US_segmentation_2d"].projection_y_coordinate

    else:
        raise Exception(
            "!=====Missing Invalid Segmentation Input, needs either 2D segmetation or 3D segmentation with height [km] parameter=====!"
        )

    perimeter_info = {"frame": [], "feature_id": [], "cell_id": [], "perimeter": []}
    Tracks = analysis_object["US_tracks"]

    for ii in tqdm(
        range(len(Tracks)),
        desc="=====Calculating 2D Feature Perimeters=====",
        total=len(Tracks),
    ):
        feature_id = Tracks["feature_id"][ii]
        frame = Tracks["frame"][ii]
        cell_id = Tracks["cell_id"][ii]

        x_dim_sizes = np.diff(proj_x) / 1000  # m->km
        y_dim_sizes = np.diff(proj_y) / 1000  # m->km

        # These are one cell too small due to how diff works, so infer last cell size using the same cell size as the previous cell
        x_dim_sizes = np.append(x_dim_sizes, x_dim_sizes[-1])
        y_dim_sizes = np.append(y_dim_sizes, y_dim_sizes[-1])

        perims = 0  # this is to keep track of the amount of the perimeter that is shared with another cell
        # key is feature id of other cell, value is the shared perimeter

        feature_seg_in_frame = feature_seg[frame].values

        for ny, nx in np.argwhere(feature_seg_in_frame == feature_id):
            for mx in (nx - 1, nx + 1):
                if (
                    mx in range(feature_seg_in_frame.shape[1])
                    and feature_seg_in_frame[ny, mx] != feature_id
                ):
                    perims += y_dim_sizes[ny]

            for my in (ny - 1, ny + 1):
                if (
                    my in range(feature_seg_in_frame.shape[0])
                    and feature_seg_in_frame[my, nx] != feature_id
                ):
                    perims += x_dim_sizes[nx]

        perimeter_info["frame"].append(frame)
        perimeter_info["feature_id"].append(feature_id)
        perimeter_info["cell_id"].append(cell_id)
        perimeter_info["perimeter"].append(perims)

    perimeter_df = pd.DataFrame(perimeter_info)
    # Enforce the threshold
    if threshold is not None:
        # Load background varaible
        if type(analysis_object["segmentation_xarray"]) == xr.core.dataarray.DataArray:
            variable_field = analysis_object["segmentation_xarray"]
        else:
            variable_field = analysis_object["segmentation_xarray"][variable]

        if len(variable_field.shape) != 3:
            raise ValueError("=====The segmentation must be 2D=====")

        feature_mask = analysis_object["US_segmentation_2d"].Feature_Segmentation
        # TODO: if user only has 3D segmentation and height for perimeter and has a threshold set
        feature_mask.values[variable_field.values < threshold] = -1
        uncut_feature_list = np.unique(feature_mask)[1:]  # don"t use -1
        perimeter_df = perimeter_df[perimeter_df["feature_id"].isin(uncut_feature_list)]

    return perimeter_df


def calculate_surface_area(
    analysis_object: dict,
    variable: str | None = None,
    threshold: float | None = None,
    **args: dict,
) -> pd.DataFrame:
    """

    Parameters
    ----------
    analysis_object : dict
        A CoCoMET-US standard analysis object containing at least US_tracks.
    variable : str, optional
        Variable to which we should apply the threshold. The default is None.
    threshold : float, optional
        Value of which the area should be greater than. The default is None.
    **args : dict
        Throw away variables.

    Raises
    ------
    Exception
        Exception if missing tracks input from the analysis object.
        Exception if the segmentation data is not 2D or 3D.

    Returns
    -------
    pandas.core.frame.DataFrame
        A pandas dataframe with the following rows: frame, feature_id, cell_id, surface_area where surface_area is in km^2.

    """

    if analysis_object["US_tracks"] is None:
        raise Exception(
            "!=====Tracks Data is Required for Surface Area Calculation=====!"
        )

    # Check if there is 3D segmentation
    if analysis_object["US_segmentation_3d"] is not None:
        feature_seg = analysis_object["US_segmentation_3d"].Feature_Segmentation

    else:
        raise Exception("!=====Missing 3D Segmentation Input=====!")

    surface_area_info = {
        "frame": [],
        "feature_id": [],
        "cell_id": [],
        "surface_area": [],
    }
    Tracks = analysis_object["US_tracks"]

    # define some useful variables
    proj_x = analysis_object["US_segmentation_3d"].projection_x_coordinate
    proj_y = analysis_object["US_segmentation_3d"].projection_y_coordinate
    altitude = analysis_object["US_segmentation_3d"].altitude

    for ii in tqdm(
        range(len(Tracks)),
        desc="=====Calculating Feature Surface Areas=====",
        total=len(Tracks),
    ):
        feature_id = Tracks["feature_id"][ii]
        frame = Tracks["frame"][ii]
        cell_id = Tracks["cell_id"][ii]

        x_dim_sizes = np.diff(proj_x) / 1000  # m->km
        y_dim_sizes = np.diff(proj_y) / 1000  # m->km
        z_dim_sizes = np.diff(altitude) / 1000  # m->km

        # These are one cell too small due to how diff works, so infer last cell size using the same cell size as the previous cell
        x_dim_sizes = np.append(x_dim_sizes, x_dim_sizes[-1])
        y_dim_sizes = np.append(y_dim_sizes, y_dim_sizes[-1])
        z_dim_sizes = np.append(z_dim_sizes, z_dim_sizes[-1])

        surface_areas = 0  # this is to keep track of the amount of the surface_area that is shared with another cell
        # key is feature id of other cell, value is the shared surface_area

        feature_seg_in_frame = feature_seg[frame].values

        for nz, ny, nx in np.argwhere(feature_seg_in_frame == feature_id):
            for mx in (nx - 1, nx + 1):
                if (
                    mx in range(feature_seg_in_frame.shape[2])
                    and feature_seg_in_frame[nz, ny, mx] != feature_id
                ):
                    surface_areas += y_dim_sizes[ny] * z_dim_sizes[nz]

            for my in (ny - 1, ny + 1):
                if (
                    my in range(feature_seg_in_frame.shape[1])
                    and feature_seg_in_frame[nz, my, nx] != feature_id
                ):
                    surface_areas += x_dim_sizes[nx] * z_dim_sizes[nz]

            for mz in (nz - 1, nz + 1):
                if (
                    mz in range(feature_seg_in_frame.shape[0])
                    and feature_seg_in_frame[mz, ny, nx] != feature_id
                ):
                    surface_areas += x_dim_sizes[nx] * y_dim_sizes[ny]

        surface_area_info["frame"].append(frame)
        surface_area_info["feature_id"].append(feature_id)
        surface_area_info["cell_id"].append(cell_id)
        surface_area_info["surface_area"].append(surface_areas)

    surface_area_df = pd.DataFrame(surface_area_info)

    # Enforce the threshold
    if threshold is not None:
        # Load background varaible
        if type(analysis_object["segmentation_xarray"]) == xr.core.dataarray.DataArray:
            variable_field = analysis_object["segmentation_xarray"]
        else:
            variable_field = analysis_object["segmentation_xarray"][variable]

        if len(variable_field.shape) != 4:
            raise ValueError("=====The segmentation must be 3D=====")

        feature_mask = analysis_object[f"US_segmentation_3d"].Feature_Segmentation
        feature_mask.values[variable_field.values < threshold] = -1
        uncut_feature_list = np.unique(feature_mask)[1:]  # don"t use -1
        surface_area_df = surface_area_df[
            surface_area_df["feature_id"].isin(uncut_feature_list)
        ]

    return surface_area_df


def calculate_irregularity(
    analysis_object: dict,
    irregularity_metrics: str | list[str],
    variable: str | None = None,
    threshold: float | None = None,
    segmentation_type: str = None,
    **args: dict,
) -> pd.DataFrame:
    """


    Parameters
    ----------
    analysis_object : dict
        A CoCoMET-US standard analysis object containing at least US_tracks and US_segmentation_2d or US_segmentation_3d.
    irregularity_metrics: str | list[str]
        A string or list of strings for which irregularity metric to calculate.
        The implemented metrics are:
            "sphericity",
            "convexity",
    variable : str, optional
        Variable to which we should apply the threshold. The default is None.
    threshold : float, optional
        Value of which the area should be greater than. The default is None.
    segmentation_type : str, optional
        Whether to calculate 2d or 3d convexity if convexity in irregularity_matrics. If None, will use 3d segmentation if it is available, or 2d segmentation if 3d segmentation is unavailable. The default is None.
    **args : dict
        Throw away variables.

    Raises
    ------
    KeyError
        KeyError if there are no found implemented irregularity metrics.
    Exception
        Exception if no segmentation data is found.

    Returns
    -------
    pandas.core.frame.DataFrame
        A pandas dataframe with the following rows: frame, feature_id, cell_id, irregularity.

    """
    from .irregularity import convexity, sphericity

    if type(irregularity_metrics) != list:
        irregularity_metrics = [irregularity_metrics]

    # A list of the currently implemented irregularity metrics
    implemented_metrics = ["sphericity", "convexity"]

    overlap = set(implemented_metrics) & set(irregularity_metrics)
    if len(overlap) == 0:
        raise KeyError("Found No Implemented Irregularity Metric")

    list_of_irregularities = []

    # Calculate convexity
    if "convexity" in irregularity_metrics:
        if "perimeter" in args:
            perimeter_df = args["perimeter"]["perimeter"]
        else:
            perimeter_df = calculate_perimeter(analysis_object)["perimeter"]

        list_of_irregularities.append(
            convexity.convexity(analysis_object, perimeter_df, segmentation_type)
        )

    # Calculate sphericity
    if "sphericity" in irregularity_metrics:
        # Get volume and perimeter dataframes
        if "volume" in args:
            volume_df = args["volume"]["volume"]
        else:
            volume_df = calculate_volume(analysis_object, None, None, **args)["volume"]

        if "perimeter" in args:
            perimeter_df = args[
                "perimeter"
            ]  # takes the entire perimeter df, not just perimeter values
        else:
            perimeter_df = calculate_perimeter(analysis_object, None, None **args)

        list_of_irregularities.append(sphericity.sphericity(perimeter_df, volume_df))

    # Enforce the threshold
    if analysis_object["US_segmentation_3d"] is not None:
        uncut_feature_list = np.unique(
            analysis_object["US_segmentation_3d"].Feature_Segmentation
        )[
            1:
        ]  # don"t use -1
    elif analysis_object["US_segmentation_2d"] is not None:
        uncut_feature_list = np.unique(
            analysis_object["US_segmentation_2d"].Feature_Segmentation[1:]
        )
    else:
        raise ValueError("!=====Missing US Segmentation Data=====!")

    if threshold is not None:
        # Load background varaible
        if type(analysis_object["segmentation_xarray"]) == xr.core.dataarray.DataArray:
            variable_field = analysis_object["segmentation_xarray"]
        else:
            variable_field = analysis_object["segmentation_xarray"][variable]

        feature_mask = analysis_object["US_segmentation_3d"].Feature_Segmentation
        feature_mask.values[variable_field.values < threshold] = -1
        uncut_feature_list = np.unique(feature_mask)[1:]  # don"t use -1

    irregularity_info_df = list_of_irregularities[0]

    # if there are more irregularity metrics, add them as a column to the irregularity info dataframe
    if len(list_of_irregularities) > 1:
        for df in list_of_irregularities[1:]:
            irregularity_info_df = irregularity_info_df.join(df[df.keys()[-1]])

    irregularity_info_df = irregularity_info_df[
        irregularity_info_df["feature_id"].isin(uncut_feature_list)
    ]

    return irregularity_info_df
