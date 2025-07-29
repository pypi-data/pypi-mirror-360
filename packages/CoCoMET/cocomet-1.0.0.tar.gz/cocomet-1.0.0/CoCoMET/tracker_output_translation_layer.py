#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 12:34:22 2024

@author: thahn
"""

# =============================================================================
# Modifies tracking output into the CoCoMET-US
# =============================================================================

from copy import deepcopy
from datetime import datetime

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.path import Path
from scipy.interpolate import interpn
from scipy.ndimage import center_of_mass
from tqdm import tqdm


def feature_id_to_US(
    features: gpd.GeoDataFrame, tracker: str
) -> gpd.GeoDataFrame | None:
    """


    Parameters
    ----------
    features : geopandas.geodataframe.GeoDataFrame
        The output from the feature detection step of a given tracker.
    tracker : str
        ["tobac"] The tracker used to generate the features.

    Raises
    ------
    Exception
        Exception if invalid tracker entered.

    Returns
    -------
    US_features : geopandas.geodataframe.GeoDataFrame
        A geodataframe matching the format of the CoCoMET-US feature detection specification.

    """

    if features is None:
        return None

    if tracker.lower() == "tobac":
        # Extract values from features
        frames = features.frame.values
        times = np.array(
            [datetime.fromisoformat(f.isoformat()) for f in features.time.values]
        )
        feature_ids = features.feature.values - 1
        north_souths = features.south_north.values
        east_wests = features.west_east.values
        latitudes = features.latitude.values
        longitudes = features.longitude.values
        projection_x = features.projection_x_coordinate.values
        projection_y = features.projection_y_coordinate.values
        geometries = features.geometry.values

        # Include 3D coordinates if present. If not, set all alt values as NaN
        if "altitude" in features and "vdim" in features:
            altitudes = features.altitude.values / 1000
            up_downs = features.vdim.values

        else:
            altitudes = np.repeat(np.nan, features.shape[0])
            up_downs = np.repeat(np.nan, features.shape[0])

        # Create GeoDataFrame according to US specification
        US_features = gpd.GeoDataFrame(
            data={
                "frame": frames,
                "time": times,
                "feature_id": feature_ids,
                "south_north": north_souths,
                "west_east": east_wests,
                "up_down": up_downs,
                "latitude": latitudes,
                "longitude": longitudes,
                "projection_x": projection_x,
                "projection_y": projection_y,
                "altitude": altitudes,
                "geometry": geometries,
            }
        )

        return US_features

    raise Exception(f"!=====Invalid Tracker, You Entered: {tracker.lower()}=====!")


def linking_to_US(tracks: gpd.GeoDataFrame, tracker: str) -> gpd.GeoDataFrame | None:
    """


    Parameters
    ----------
    tracks : geopandas.geodataframe.GeoDataFrame
        The output from the linking/tracking step of a given tracker.
    tracker : str
        ["tobac"] The tracker used to generate the links.

    Raises
    ------
    Exception
        Exception if invalid tracker entered.

    Returns
    -------
    US_tracks : geopandas.geodataframe.GeoDataFrame
        A geodataframe matching the format of the CoCoMET-US linking specification.

    """

    # TODO: figure out how to remove cells with -1 cell id

    if tracks is None:
        return None

    if tracker.lower() == "tobac":
        # Extract values from features
        frames = tracks.frame.values
        times = np.array(
            [datetime.fromisoformat(f.isoformat()) for f in tracks.time.values]
        )
        lifetimes = tracks.time_cell.values
        feature_ids = tracks.feature.values - 1
        cell_ids = tracks.cell.values - 1
        # Correct any -2 values, created as a result of shifting, back to -1
        cell_ids[cell_ids == -2] = -1
        north_souths = tracks.south_north.values
        east_wests = tracks.west_east.values
        latitudes = tracks.latitude.values
        longitudes = tracks.longitude.values
        projection_x = tracks.projection_x_coordinate.values
        projection_y = tracks.projection_y_coordinate.values
        geometries = tracks.geometry.values

        # Include 3D coordinates if present. If not, set all alt values as NaN
        if "altitude" in tracks and "vdim" in tracks:
            altitudes = tracks.altitude.values / 1000
            up_downs = tracks.vdim.values

        else:
            altitudes = np.repeat(np.nan, tracks.shape[0])
            up_downs = np.repeat(np.nan, tracks.shape[0])

        lifetime_percents = []

        # Loop over rows
        for row in tqdm(
            tracks.itertuples(index=True),
            desc="=====Performing tobac Linking to US====",
            total=tracks.shape[0],
        ):
            cell_id = row.cell
            cell_max_life = tracks[tracks["cell"] == cell_id]["time_cell"].values.max()
            # cell_max_life = tracks.query("cell==@row[1].cell").time_cell.values.max()
            # If only tracked one time, add -1 to lifetime_percent
            if cell_max_life == 0:
                lifetime_percents.append(-1)
            else:
                lifetime_percents.append(row.time_cell / cell_max_life)

        # Create GeoDataFrame according to US specification
        US_tracks = gpd.GeoDataFrame(
            data={
                "frame": frames,
                "time": times,
                "lifetime": lifetimes,
                "lifetime_percent": lifetime_percents,
                "feature_id": feature_ids,
                "cell_id": cell_ids,
                "south_north": north_souths,
                "west_east": east_wests,
                "up_down": up_downs,
                "latitude": latitudes,
                "longitude": longitudes,
                "projection_x": projection_x,
                "projection_y": projection_y,
                "altitude": altitudes,
                "geometry": geometries,
            }
        )

        return US_tracks

    raise Exception(f"!=====Invalid Tracker, You Entered: {tracker.lower()}=====!")


def segmentation_to_US(
    segmentation: xr.DataArray, US_tracks: gpd.GeoDataFrame, tracker: str
) -> xr.Dataset | None:
    """


    Parameters
    ----------
    segmentation : xarray.core.dataarray.DataArray
        The output from the segmentation step of a given tracker.
    US_tracks : geopandas.geodataframe.GeoDataFrame
        US standard tracking output.
    tracker : str
        ["tobac"] The tracker used to generate the features.

    Raises
    ------
    Exception
        Exception if invalid tracker entered.

    Returns
    -------
    xarray.core.dataset.Dataset
        An xarray dataset matching the format of the CoCoMET-US segmentation specification.

    """

    if segmentation is None or US_tracks is None:
        return None

    if tracker.lower() == "tobac":
        feature_segmentation = (segmentation - 1).rename("Feature_Segmentation")
        cell_segmentation = deepcopy(feature_segmentation).rename("Cell_Segmentation")

        frame_groups = US_tracks.groupby("frame")

        # Loop over tracks, replacing feature_id values with cell_id values in the cell_segmenation DataArray
        for frame in tqdm(
            frame_groups,
            desc="=====Performing tobac Segmentation to US=====",
            total=frame_groups.ngroups,
        ):
            cell_segmentation_frame = cell_segmentation[frame[0]].values
            # Loop over each feature in that frame
            for feature in frame[1].itertuples():
                # Replace the feature_id with the cell_id
                cell_segmentation_frame[
                    cell_segmentation_frame == feature.feature_id
                ] = feature.cell_id

        # Combine into one xarray Dataset and return

        # To check for both prescense of altitude and shape of altitude without throwing DNE error
        altitude_check_bool = False
        if "altitude" in segmentation.coords:
            if segmentation.altitude.shape != ():
                altitude_check_bool = True

        if "model_level_number" in segmentation.coords:
            if segmentation.model_level_number.shape != ():
                altitude_check_bool = True

        # Check if altitude is present
        if altitude_check_bool:
            return_ds = xr.combine_by_coords([feature_segmentation, cell_segmentation])

            # Check for NEXRAD, and rename accordingly
            if (
                "y" in segmentation.dims
                and "x" in segmentation.dims
                and "z" in segmentation.dims
                and "lat" in segmentation.coords
                and "lon" in segmentation.coords
            ):
                return_ds = return_ds.assign_coords(
                    altitude=("z", feature_segmentation.z.values),
                    up_down=("z", np.arange(0, feature_segmentation.z.shape[0])),
                )
                return_ds = return_ds.swap_dims(
                    {"z": "up_down", "y": "south_north", "x": "west_east"}
                ).rename({"lat": "latitude", "lon": "longitude"})
                return_ds = return_ds.drop_vars(["z", "x", "y", "model_level_number"])

                return return_ds[
                    [
                        "time",
                        "up_down",
                        "south_north",
                        "west_east",
                        "Feature_Segmentation",
                        "Cell_Segmentation",
                    ]
                ]

            # For WRF case
            else:
                # Change altitude values to indices
                # return_ds = xr.combine_by_coords([feature_segmentation,cell_segmentation]).assign_coords({"up_down":np.arange(0,feature_segmentation.altitude.shape[0])})
                return_ds = return_ds.assign_coords(
                    up_down=(
                        "altitude",
                        np.arange(0, feature_segmentation.altitude.shape[0]),
                    )
                )

                # Remove extra coordinates and rename altitude
                return_ds = return_ds.swap_dims({"altitude": "up_down"}).drop_vars(
                    ["model_level_number", "x", "y"]
                )
                return return_ds[
                    [
                        "time",
                        "up_down",
                        "south_north",
                        "west_east",
                        "Feature_Segmentation",
                        "Cell_Segmentation",
                    ]
                ]

        else:
            # Concat into one dataset and remove superflous coordinates
            return_ds = xr.combine_by_coords([feature_segmentation, cell_segmentation])

            # Check for GOES and rename accordingly
            if "sensor_band_bit_depth" in segmentation.attrs:
                # Rename t to time and rename x and y values to south_north and west_east, respectively. Rename lat and lon to latitude and longitude
                return_ds = (
                    return_ds.assign_coords(time=("t", return_ds.t.values))
                    .swap_dims({"t": "time"})
                    .drop_vars(["t"])
                )
                return_ds = return_ds.swap_dims(
                    {"y": "south_north", "x": "west_east"}
                ).rename({"lat": "latitude", "lon": "longitude"})

                return_ds = return_ds.drop_vars(["x", "y"])
                return return_ds[
                    [
                        "time",
                        "south_north",
                        "west_east",
                        "Feature_Segmentation",
                        "Cell_Segmentation",
                    ]
                ]

            # Check for NEXRAD, and rename accordingly
            elif (
                "y" in segmentation.dims
                and "x" in segmentation.dims
                and "lat" in segmentation.coords
                and "lon" in segmentation.coords
            ):
                return_ds = return_ds.swap_dims(
                    {"y": "south_north", "x": "west_east"}
                ).rename({"lat": "latitude", "lon": "longitude"})

                return_ds = return_ds.drop_vars(["x", "y"])
                return return_ds[
                    [
                        "time",
                        "south_north",
                        "west_east",
                        "Feature_Segmentation",
                        "Cell_Segmentation",
                    ]
                ]

            # For WRF case
            else:
                return_ds = return_ds.drop_vars(["x", "y"])
                return return_ds[
                    [
                        "time",
                        "south_north",
                        "west_east",
                        "Feature_Segmentation",
                        "Cell_Segmentation",
                    ]
                ]

    raise Exception(f"!=====Invalid Tracker, You Entered: {tracker.lower()}=====!")


def bulk_moaap_to_US(
    mask: xr.Dataset,
    projection_x_coords: np.ndarray,
    projection_y_coords: np.ndarray,
    convert_type: str = "cloud",
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, xr.Dataset] | None:
    """


    Parameters
    ----------
    mask : xarray.core.dataset.Dataset
        An xarray file which is the default output from MOAAP and contains the mask information for all tracked types.
    projection_x_coords : np.ndarray
        Numpy array of projection x coordinates.
    projection_y_coords : np.ndarray
        Numpy array of projection y coordinates.
    convert_type : str, optional
        ["MCS", "Cloud"] The type of tracking data to extract. The default is "cloud".

    Raises
    ------
    Exception
        Exception if invalid phenomena type entered.

    Returns
    -------
    US_features : geopandas.geodataframe.GeoDataFrame
        Features geopandas dataframe following CoCoMET-US specification.
    US_linking : geopandas.geodataframe.GeoDataFrame
        Linking geopandas dataframe following CoCoMET-US specification.
    US_segmentation_2d : xarray.core.dataset.Dataset
        Segmentation xarray dataset following CoCoMET-US specification.

    """

    # Get dt
    dt = np.median(np.diff(mask.time).astype("timedelta64[m]")).astype(int)

    # Get the numpy array that contains the object we care about's mask
    if convert_type.lower() == "cloud":
        if "BT_Objects" not in mask:
            return None

        mask_field = mask.BT_Objects.values

    elif convert_type.lower() == "mcs":
        if "MCS_Tb_Objects" not in mask:
            return None

        mask_field = mask.MCS_Tb_Objects.values

    else:
        raise Exception(
            f"!=====Invalid Phenomena Type Selected. You Entered: {convert_type.lower()}!====="
        )

    segment_feature_mask = np.zeros(mask_field.shape) - 1
    segment_cell_mask = np.zeros(mask_field.shape) - 1

    frames = []
    times = []
    feature_ids = [-1]
    cell_ids = []
    lifetimes = []
    lifetime_percents = []
    south_norths = []
    west_easts = []
    lats = []
    lons = []
    proj_xs = []
    proj_ys = []

    lifetime_dict = {}

    # Loop over frames
    for ii in tqdm(
        range(mask_field.shape[0]),
        desc="=====Converting MOAAP to US=====",
        total=mask_field.shape[0],
    ):
        # Get unique cell ids for this frame
        unique_cells = np.unique(mask_field[ii])[1:]

        segment_cell_mask[ii] = mask_field[ii] - 1

        # Loop over unique cell ids
        for cell_id in unique_cells:
            segment_feature_mask[ii][mask_field[ii] == cell_id] = feature_ids[-1] + 1

            # Append timing information and cell/feature ids
            frames.append(ii)
            times.append(pd.Timestamp(mask.time.values[ii]))

            feature_ids.append(feature_ids[-1] + 1)
            cell_ids.append(int(cell_id) - 1)

            # If cell has not yet been tracked, add it to the lifetime_dict
            if int(cell_id) - 1 not in lifetime_dict:
                lifetime_dict[int(cell_id) - 1] = {
                    "frame": [ii],
                    "lifetime": [pd.Timedelta(0)],
                }
                lifetimes.append(pd.Timedelta(0))

            else:
                new_time = lifetime_dict[int(cell_id) - 1]["lifetime"][-1] + (
                    pd.Timedelta(minutes=dt)
                    * (ii - lifetime_dict[int(cell_id) - 1]["frame"][-1])
                )
                lifetime_dict[int(cell_id) - 1]["lifetime"].append(new_time)
                lifetime_dict[int(cell_id) - 1]["frame"].append(ii)
                lifetimes.append(new_time)

            # Calculate cell centroid
            cell_mask = mask_field[ii] == cell_id
            centroid = center_of_mass(cell_mask)

            south_norths.append(centroid[0])
            west_easts.append(centroid[1])

    temp_linking = pd.DataFrame(data={"lifetime": lifetimes, "cell_id": cell_ids})

    # Loop over rows to calculate lifetime percents
    for row in tqdm(
        temp_linking.iterrows(),
        desc="=====Processing MOAAP Cell Lifetimes====",
        total=temp_linking.shape[0],
    ):
        cell_max_life = temp_linking.query(
            "cell_id==@row[1].cell_id"
        ).lifetime.values.max()

        # If only tracked one time, add -1 to lifetime_percent
        if cell_max_life == 0:
            lifetime_percents.append(-1)
        else:
            lifetime_percents.append(row[1].lifetime / cell_max_life)

    # Calculate lat and lons by interpolating over lat/lon fields
    lat_dims = (np.arange(0, mask.lat[0].shape[0]), np.arange(0, mask.lat[0].shape[1]))
    lon_dims = (np.arange(0, mask.lon[0].shape[0]), np.arange(0, mask.lon[0].shape[1]))

    lat = interpn(lat_dims, mask.lat[0].values, np.array([south_norths, west_easts]).T)
    lon = interpn(lon_dims, mask.lon[0].values, np.array([south_norths, west_easts]).T)

    lats.extend(lat)
    lons.extend(lon)

    # Calculate projection x and y coordinates via interpolating again
    proj_x_coords = np.arange(0, mask.lat[0].shape[1])
    proj_y_coords = np.arange(0, mask.lat[0].shape[0])

    new_proj_x = interpn([proj_x_coords], projection_x_coords, west_easts)
    new_proj_y = interpn([proj_y_coords], projection_y_coords, south_norths)

    proj_xs.extend(new_proj_x)
    proj_ys.extend(new_proj_y)

    # Create all dataframs and convert them to geodataframes
    US_features = pd.DataFrame(
        data={
            "frame": frames,
            "time": times,
            "feature_id": feature_ids[1:],
            "south_north": south_norths,
            "west_east": west_easts,
            "up_down": np.repeat(np.nan, len(frames)),
            "latitude": lats,
            "longitude": lons,
            "projection_x": new_proj_x,
            "projection_y": new_proj_y,
            "altitude": np.repeat(np.nan, len(frames)),
        }
    )

    US_features = gpd.GeoDataFrame(
        US_features,
        geometry=gpd.points_from_xy(US_features.longitude, US_features.latitude),
        crs="EPSG:4326",
    )

    US_linking = pd.DataFrame(
        data={
            "frame": frames,
            "time": times,
            "lifetime": lifetimes,
            "lifetime_percent": lifetime_percents,
            "feature_id": feature_ids[1:],
            "cell_id": cell_ids,
            "south_north": south_norths,
            "west_east": west_easts,
            "up_down": np.repeat(np.nan, len(frames)),
            "latitude": lats,
            "longitude": lons,
            "projection_x": new_proj_x,
            "projection_y": new_proj_y,
            "altitude": np.repeat(np.nan, len(frames)),
        }
    )

    US_linking = gpd.GeoDataFrame(
        US_linking,
        geometry=gpd.points_from_xy(US_linking.longitude, US_linking.latitude),
        crs="EPSG:4326",
    )

    # Now perform segmentation conversion
    US_segmentation_2d = xr.Dataset(
        coords=dict(
            time=mask.time.values,
            south_north=mask.yc.values,
            west_east=mask.xc.values,
            projection_y_coordinate=("south_north", projection_y_coords),
            projection_x_coordinate=("west_east", projection_x_coords),
            latitude=(["south_north", "west_east"], mask.lat[0].values),
            longitude=(["south_north", "west_east"], mask.lon[0].values),
        ),
        data_vars=dict(
            Feature_Segmentation=(
                ["time", "south_north", "west_east"],
                segment_feature_mask,
            ),
            Cell_Segmentation=(["time", "south_north", "west_east"], segment_cell_mask),
        ),
        attrs=dict(description="Mask for tracked objects from MOAAP"),
    )

    return (US_features, US_linking, US_segmentation_2d)


def bulk_tams_to_US(
    output: gpd.GeoDataFrame,
    latlon_coord_system: tuple[np.ndarray, np.ndarray],
    projection_x_coords: np.ndarray,
    projection_y_coords: np.ndarray,
    convert_type: str = "cloud",
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, xr.Dataset] | None:
    """


    Parameters
    ----------
    output : pd.DataFrame
        A geodataframe with geometry of tracked cloud objects
    latlon_coord_system : tuple[np.ndarray, np.ndarray]
        A tuple of the latitude and longitude coordinate numpy arrays
    projection_x_coords : np.ndarray
        A numpy array of the x projection coordinates.
    projection_y_coords : np.ndarray
        A numpy array of the y projection coordinates.
    convert_type : str, optional
        ["MCS", "Cloud"] The type of tracking data to extract. The default is "cloud".

    Raises
    ------
    Exception
        Exception if invalid phenomena type entered.

    Returns
    -------
    US_features : geopandas.geodataframe.GeoDataFrame
        Features geopandas dataframe following CoCoMET-US specification.
    US_linking : geopandas.geodataframe.GeoDataFrame
        Linking geopandas dataframe following CoCoMET-US specification.
    US_segmentation_2d : xarray.core.dataset.Dataset
        Segmentation xarray dataset following CoCoMET-US specification.
    """

    # Get the numpy array that contains the object we care about's mask
    if convert_type.lower() == "cloud":
        tracked_elements = output

    # TODO : fix this once you get gridding data aggregation working for TAMS. Also make it output[0] above
    # elif convert_type.lower() == "mcs":

    #     tracked_elements = output[1]

    else:
        raise Exception(
            f"!=====Invalid Phenomena Type Selected. You Entered: {convert_type.lower()}!====="
        )

    # Get dt
    dt = np.median(tracked_elements["dtime"].dt.total_seconds().astype(int))
    cell_mask = convert_df_to_mask(tracked_elements, latlon_coord_system)
    feature_mask = convert_cell_mask_to_feature_mask(cell_mask)

    frames = []
    times = []
    feature_ids = [-1]
    cell_ids = []
    lifetimes = []
    lifetime_percents = []
    south_norths = []
    west_easts = []
    lats = []
    lons = []
    new_proj_x = []
    new_proj_y = []

    lifetime_dict = {}

    # Iterate through each timestep
    for ii in tqdm(
        range(len(tracked_elements)),
        desc="=====Converting TAMS to US=====",
        total=len(tracked_elements),
    ):
        frame = tracked_elements["itime"][ii]
        frames.append(frame)
        times.append(tracked_elements["time"][ii])

        cell_id = int(tracked_elements["mcs_id"][ii])
        cell_ids.append(cell_id)

        lat = tracked_elements["geometry"][ii].centroid.y
        lon = tracked_elements["geometry"][ii].centroid.x
        lats.append(lat)
        lons.append(lon)

        latcoords = latlon_coord_system[0][frames[-1]].values
        loncoords = latlon_coord_system[1][frames[-1]].values

        # TODO: find a way to interpolate the grid coordinates from the latitude and longitude arrays
        # currently, _find_closest_latlon snaps to the closest grid coordinate for a given latitude and longitude coordiante
        closest_point = _find_closest_latlon(lat, lon, latcoords, loncoords)

        feature_ids.append(feature_mask[frame, *closest_point])

        south_norths.append(closest_point[0])
        west_easts.append(closest_point[1])

        new_proj_x.append(projection_x_coords[west_easts[-1]])
        new_proj_y.append(projection_y_coords[south_norths[-1]])

        # If cell has not yet been tracked, add it to the lifetime_dict
        if int(cell_id) not in lifetime_dict:
            lifetime_dict[int(cell_id)] = {
                "frame": [frame],
                "lifetime": [pd.Timedelta(0)],
            }
            lifetimes.append(pd.Timedelta(0))

        else:
            new_time = lifetime_dict[int(cell_id)]["lifetime"][-1] + (
                pd.Timedelta(minutes=dt)
                * (frame - lifetime_dict[int(cell_id)]["frame"][-1])
            )
            lifetime_dict[int(cell_id)]["lifetime"].append(new_time)
            lifetime_dict[int(cell_id)]["frame"].append(frame)
            lifetimes.append(new_time)

    temp_linking = pd.DataFrame(data={"lifetime": lifetimes, "cell_id": cell_ids})

    # Loop over rows to calculate lifetime percents
    for row in tqdm(
        temp_linking.iterrows(),
        desc="=====Processing TAMS Cell Lifetimes====",
        total=temp_linking.shape[0],
    ):
        cell_max_life = temp_linking.query(
            "cell_id==@row[1].cell_id"
        ).lifetime.values.max()

        # If only tracked one time, add -1 to lifetime_percent
        if cell_max_life == 0:
            lifetime_percents.append(-1)
        else:
            lifetime_percents.append(row[1].lifetime / cell_max_life)

    # Create all dataframs and convert them to geodataframes
    US_features = pd.DataFrame(
        data={
            "frame": frames,
            "time": times,
            "feature_id": feature_ids[1:],
            "south_north": south_norths,
            "west_east": west_easts,
            "up_down": np.repeat(np.nan, len(frames)),
            "latitude": lats,
            "longitude": lons,
            "projection_x": new_proj_x,
            "projection_y": new_proj_y,
            "altitude": np.repeat(np.nan, len(frames)),
        }
    )

    US_features = gpd.GeoDataFrame(
        US_features,
        geometry=gpd.points_from_xy(US_features.longitude, US_features.latitude),
        crs="EPSG:4326",
    )

    US_linking = pd.DataFrame(
        data={
            "frame": frames,
            "time": times,
            "lifetime": lifetimes,
            "lifetime_percent": lifetime_percents,
            "feature_id": feature_ids[1:],
            "cell_id": cell_ids,
            "south_north": south_norths,
            "west_east": west_easts,
            "up_down": np.repeat(np.nan, len(frames)),
            "latitude": lats,
            "longitude": lons,
            "projection_x": new_proj_x,
            "projection_y": new_proj_y,
            "altitude": np.repeat(np.nan, len(frames)),
        }
    )

    US_linking = gpd.GeoDataFrame(
        US_linking,
        geometry=gpd.points_from_xy(US_linking.longitude, US_linking.latitude),
        crs="EPSG:4326",
    )

    # Now perform segmentation conversion
    US_segmentation_2d = xr.Dataset(
        coords=dict(
            time=np.arange(latlon_coord_system[0].shape[0]),
            south_north=np.arange(latlon_coord_system[0].shape[1]),
            west_east=np.arange(latlon_coord_system[0].shape[2]),
            projection_y_coordinate=("south_north", projection_y_coords),
            projection_x_coordinate=("west_east", projection_x_coords),
            latitude=(["south_north", "west_east"], latlon_coord_system[0][0].values),
            longitude=(["south_north", "west_east"], latlon_coord_system[1][0].values),
        ),
        data_vars=dict(
            Feature_Segmentation=(
                ["time", "south_north", "west_east"],
                convert_cell_mask_to_feature_mask(cell_mask),
            ),
            Cell_Segmentation=(["time", "south_north", "west_east"], cell_mask),
        ),
        attrs=dict(description="Mask for tracked objects from TAMS"),
    )

    return (US_features, US_linking, US_segmentation_2d)


##################################################################################
##################################################################################
# Extra functions for converting TAMS dataframe into a mask


def _find_closest_latlon(lat_true, lon_true, lat_arr, lon_arr):
    # TODO : find a more exact way to do this - get an x, y position in grid coordinates
    #   given a latitude, a longitude, an array of latitudes, and an array of longitudes
    diff_arr_lat = np.abs(lat_arr - lat_true)
    diff_arr_lon = np.abs(lon_arr - lon_true)
    squared_diff_arr = diff_arr_lat**2 + diff_arr_lon**2
    closest_point = np.unravel_index(squared_diff_arr.argmin(), squared_diff_arr.shape)
    # return (closest_point[1], closest_point[0])
    return closest_point


def _points_from_polygons(polygons):
    from shapely.geometry import MultiPolygon

    points = []
    for mpoly in polygons:
        if isinstance(mpoly, MultiPolygon):
            polys = list(mpoly)
        else:
            polys = [mpoly]
        for polygon in polys:
            for point in polygon.exterior.coords:
                points.append(point)
            for interior in polygon.interiors:
                for point in interior.coords:
                    points.append(point)
    return points


def _return_gridpoints(points, latlon_coord_system):
    gridpoints = []
    latcoords = latlon_coord_system[0].values[0]
    loncoords = latlon_coord_system[1].values[0]
    for ilon, ilat in points:
        x, y = _find_closest_latlon(ilat, ilon, latcoords, loncoords)
        gridpoints.append((y, x))

    return gridpoints


def convert_df_to_mask(ce, latlon_coord_system):
    full_mask = np.zeros_like(latlon_coord_system[0].values)

    # TODO : this is really slow, find a better way to do this
    for frame in tqdm(np.unique(ce.itime),
                    desc="=====Converting TAMS Dataframe to Mask=====",
                    total = len(np.unique(ce.itime))):
        id_groups = ce[ce.itime == frame].groupby("mcs_id")

        for mcs_id, grouped_df in id_groups:
            points = _points_from_polygons(
                grouped_df.geometry
            )  # get the points in lat, lon
            gridpoints = _return_gridpoints(
                points, latlon_coord_system
            )  # convert the points to gridspace

            ny, nx = latlon_coord_system[0].shape[1:]
            poly_verts = gridpoints

            x, y = np.meshgrid(np.arange(nx), np.arange(ny))
            x, y = x.flatten(), y.flatten()

            points = np.vstack((x, y)).T

            path = Path(poly_verts)
            grid = path.contains_points(points)
            grid = grid.reshape((ny, nx))

            grid = np.array(grid, dtype=int) * (mcs_id + 1)

            non_zero_grid = grid != 0
            full_mask_in_frame = full_mask[frame]
            full_mask_in_frame[non_zero_grid] = grid[non_zero_grid]
    full_mask -= 1
    return full_mask


def convert_cell_mask_to_feature_mask(cell_mask):
    feature_mask = deepcopy(cell_mask)
    last_feature = 0
    for t in range(feature_mask.shape[0]):
        real_cell_bool = feature_mask[t] > -1
        feature_mask[t][real_cell_bool] += last_feature
        last_feature = np.max(feature_mask[t])

    return feature_mask
