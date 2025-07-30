#region Libraries

#%%
import copy

from enum import Enum

import pandas as pd
import numpy as np

import geopandas as gpd
from shapely import geometry
from shapely import ops
import rtree
# from osgeo import gdal
import rasterio
import rasterstats as rs

import xarray as xr
import rioxarray as rxr

import plotly.express as px

from typing import Literal

from .pb_functions_general import *
from .pb_functions_pandas import *
from .pb_functions_plotly import *

#endregion -----------------------------------------------------------------------------------------
#region Variables

#%%
class Options_epsg(Enum):
    wgs84 = 4326
    nad83_LA_north = 3451
    nad83_LA_south = 3452
    nad83_11_LA_north = 6477
    nad83_11_LA_south = 6479
    nad83_TX_north = 2275
    nad83_TX_n_central = 2276
    nad83_TX_central = 2277
    nad83_TX_s_central = 2278
    nad83_TX_south = 2279
    nad83_11_TX_north = 6582
    nad83_11_TX_n_central = 6584
    nad83_11_TX_central = 6578
    nad83_11_TX_s_central = 6588
    nad83_11_TX_south = 6586

#%%
class Options_px_basemap(Enum):
    carto_positron = 'carto-positron'
    carto_darkmatter = 'carto-darkmatter'
    satellite = 'mapbox-satellite'
    none = 'white-bg'
    open_street_map = 'open-street-map'
    satellite_esri = 'satellite_esri'
    satellite_usda = 'satellite_usda'
    satellite_national_map = 'satellite_national_map'

#%%
class Options_px_tiles(Enum):
    satellite_esri = 'https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
    satellite_usda = 'https://gis.apfo.usda.gov/arcgis/rest/services/NAIP/USDA_CONUS_PRIME/ImageServer/tile/{z}/{y}/{x}'
    satellite_national_map = 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}'

#endregion -----------------------------------------------------------------------------------------
#region Functions: Dataframe and sp Conversion

#%%
def sp_points_from_df_xy(df_xy: pd.DataFrame, column_x = 'x', column_y = 'y', crs: Any = None) -> gpd.GeoDataFrame:
    '''Create points geodataframe.

    Args:
        df_xy (DataFrame): Dataframe with x and y columns.
        column_x (str): Name of column with x values. Defaults to 'x'.
        column_y (str): Name of column with y values. Defaults to 'y'.
        crs (any, optional): CRS that can be assiged to geodataframe. Defaults to None.

    Returns:
        gpd.GeoDataFrame: Points geodataframe with all columns from df_xy.

    Examples:
        >>> sp_points = sp_points_from_df_xy(df)
        >>> sp_points = sp_points_from_df_xy(df, column_x='longitude', column_y='latitude', crs=4326)
    '''

    sp_points = gpd.GeoDataFrame(df_xy,
                                 geometry=gpd.points_from_xy(df_xy[column_x], df_xy[column_y]))

    if crs is not None:
        sp_points.crs = crs

    return (sp_points)

#%%
def sp_lines_from_df_xy(df_xy: pd.DataFrame, column_x = 'x', column_y = 'y', column_group: str = None, keep_columns = False, crs = None) -> gpd.GeoDataFrame:
    '''Create polylines geodataframe.

    Args:
        df_xy (DataFrame): Dataframe with x and y columns.
        column_x (str): Name of column with x values. Defaults to 'x'.
        column_y (str): Name of column with y values. Defaults to 'y'.
        column_group (str, optional): Column name to use as group. Defaults to None. If None, all points become one single polyline.
        keep_columns (bool): Whether to keep all columns from 'df_xy'. Defaults to False.
        crs (any, optional): CRS that can be assiged to geodataframe. Defaults to None.

    Returns:
        gpd.GeoDataFrame: Polyline geodataframe without columns from df_xy.

    Examples:
        >>> sp_lines = sp_lines_from_df_xy(df, column_group='group')
        >>> sp_lines = sp_lines_from_df_xy(df, column_group='group', keep_columns=True, column_x='longitude', column_y='latitude', crs=4326)
    '''
    sp_points = gpd.GeoDataFrame(df_xy,
                                 geometry=gpd.points_from_xy(df_xy[column_x], df_xy[column_y]))
    temp_group_column = copy.copy(column_group)
    if column_group is None:
        column_group = 'temp___group'
        sp_points = sp_points.assign(**{column_group: 1})
    sp_lines = \
        (sp_points
            .groupby(column_group)['geometry']
            .apply(lambda _: geometry.LineString(list(_)))
            .reset_index()
        )
    if temp_group_column is None:
        sp_lines = sp_lines.drop(column_group, axis=1)
    if keep_columns:
        if column_group is None:
            sp_lines = sp_lines.pipe(pd_concat_cols, df_xy.iloc[[0]], cols_drop = [column_x, column_y])
        else:
            # df_xy = df_xy.groupby('index_info').head(1).reset_index(drop=True)
            df_xy = df_xy.groupby(column_group).head(1).reset_index(drop=True)
            sp_lines = sp_lines.merge(df_xy, how='left', on=column_group).drop([column_x, column_y], axis=1)

    if crs is not None:
        sp_lines.crs = crs

    return (sp_lines)

#%%
def sp_lines_from_df_xy_from_to(df_xy: pd.DataFrame, column_x_from = 'x_from', column_y_from = 'y_from', column_x_to = 'x_to', column_y_to = 'y_to', crs = None) -> gpd.GeoDataFrame:
    '''Create polylines geodataframe using from- and to-coordinate columns.

    Args:
        df_xy (pd.DataFrame): Dataframe with from- and to-coordinates
        column_x_from (str, optional): Name of column with from-x values. Defaults to 'x_from'.
        column_y_from (str, optional): Name of column with from-y values. Defaults to 'y_from'.
        column_x_to (str, optional): Name of column with to-x values. Defaults to 'x_to'.
        column_y_to (str, optional): Name of column with to-y values. Defaults to 'y_to'.
        crs (any, optional): CRS that can be assiged to geodataframe. Defaults to None.

    Returns:
        gpd.GeoDataFrame: Polyline geodataframe without columns from df_xy.

    Examples:
        >>> sp_lines = sp_lines_from_df_xy(df, 'x_start', 'y_start', 'x_end', 'y_end', crs=4326)
    '''
    df_xy = \
    (df_xy
        .assign(geometry = lambda _: _.apply(lambda row: geometry.LineString([(row[column_x_from], row[column_y_from]), (row[column_x_to], row[column_y_to])]), axis=1))        
    )

    sp_lines = gpd.GeoDataFrame(df_xy)

    if crs is not None:
        sp_lines.crs = crs

    return (sp_lines)

#%%
def sp_polygons_from_df_xy(df_xy: pd.DataFrame, column_x = 'x', column_y = 'y', column_group: str = None, keep_columns = False, crs = None) -> gpd.GeoDataFrame:
    '''Create polygons geodataframe.

    Args:
        df_xy (DataFrame): Dataframe with x and y columns.
        column_x (str): Name of column with x values. Defaults to 'x'.
        column_y (str): Name of column with y values. Defaults to 'y'.
        column_group (str, optional): Column name to use as group. Defaults to None. If None, all points become one single polygon. Starting and ending coordinates are joined by a closing line.
        keep_columns (bool): Whether to keep all columns from 'df_xy'. Defaults to False.
        crs (any, optional): CRS that can be assiged to geodataframe. Defaults to None.

    Returns:
        gpd.GeoDataFrame: Polygon geodataframe without columns from df_xy.

    Examples:
        >>> sp_polygons = sp_polygons_from_df_xy(df, column_group='group')
        >>> sp_polygons = sp_polygons_from_df_xy(df, column_group='group', keep_columns=True, column_x='longitude', column_y='latitude', crs=4326)
    '''
    sp_points = gpd.GeoDataFrame(df_xy,
                                 geometry=gpd.points_from_xy(df_xy[column_x], df_xy[column_y]))
    temp_group_column = copy.copy(column_group)
    if column_group is None:
        column_group = 'temp___group'
        sp_points = sp_points.assign(**{column_group: 1})
    sp_polygons = \
        (sp_points
            .groupby(column_group)['geometry']
            .apply(lambda _: geometry.Polygon(list(_)))
            .reset_index()
        )
    if temp_group_column is None:
        sp_polygons = sp_polygons.drop(column_group, axis=1)
    if keep_columns:
        if column_group is None:
            sp_polygons = sp_polygons.pipe(pd_concat_cols, df_xy.iloc[[0]], cols_drop = [column_x, column_y])
        else:
            df_xy = df_xy.groupby('index_info').head(1).reset_index(drop=True)
            sp_polygons = sp_polygons.merge(df_xy, how='left', on=column_group).drop([column_x, column_y], axis=1)

    if crs is not None:
        sp_polygons.crs = crs

    return (sp_polygons)

#%%
def sp_to_df_xy(sp: gpd.GeoDataFrame, explode:bool = True, cols_to_keep:str|list|np.ndarray|pd.Series = None, cols_keep_all:bool = False) -> pd.DataFrame:
    '''Convert geodataframe to dataframe of x and y values.

    Args:
        sp (GeoDataFrame): Geodataframe.
        explode (bool, optional): Whether to explode geometry. Defaults to True
        cols_to_keep (str | list | np.ndarray | pd.Series, optional): Vector of columns to keep from 'sp'. Defaults to None.
        cols_keep_all (bool, optional): Whether to keep all columns from 'sp'. Defaults to False.

    Returns:
        pd.DataFrame: Dataframe with columns: 'id_geom' indicating individual geometry parts, 'id_sp' indicating index of 'sp', 'id_part' indicating individual geometry parts for each index of 'sp', 'x' indicating x-coordinates, and 'y' indicating y-coordinates. Other columns from 'sp' may be included.

    Notes:
        - 'id_geom' is f'{id_sp}__{id_part}' and is unique.
        - If all geometry are singlepart, each entry in 'id' will be unique, and 'id_part' will all be 0.
        - For a multipart geometry, 'id_sp' will be the same, and 'id_part' will be unique.
        - If 'cols_keep_all' is True, 'cols_to_keep' is ignored.

    Examples:
        >>> sp_to_df_xy(sp_points)
        >>> sp_to_df_xy(sp_lines)
        >>> sp_to_df_xy(sp_polygons)
        >>> sp_to_df_xy(sp_points, cols_to_keep='City')
        >>> sp_to_df_xy(sp_points, cols_to_keep=['City', 'Country'])
        >>> sp_to_df_xy(sp_points, cols_keep_all=True)
    '''
    # df_xy = \
    #     (sp
    #         .explode(index_parts=True)
    #         .get_coordinates()
    #         .reset_index()
    #         .rename(columns={'level_0': 'index',
    #                         'level_1': 'index_part'})
    #         .assign(id_geom=lambda _: str_concat(_['index'], '__', _['index_part']))
    #         .pipe(pd_select_simple, 'id_geom')
    #     )
    cols_to_keep_extra = None
    if explode:
        sp = sp_explode(sp)
        cols_to_keep_extra = ['id_geom', 'id_sp', 'id_part']
        cols_to_keep = set_union_series(cols_to_keep, cols_to_keep_extra)
    df_xy = \
        (sp
            .get_coordinates()
            .reset_index()
        )

    if cols_keep_all:
        cols_to_keep = sp.drop(columns='geometry').columns
    if cols_to_keep is not None:
        cols_to_keep = pd_to_series(cols_to_keep)

        df_xy = df_xy.merge(sp[cols_to_keep].reset_index(), on='index')

    if cols_to_keep_extra is not None:
        df_xy = df_xy.pipe(pd_select_simple, ['index', *cols_to_keep_extra])
    return df_xy

#endregion -----------------------------------------------------------------------------------------
#region Functions: Vector Combination

#%%
def sp_intersects(sp_1: gpd.GeoDataFrame, sp_2: gpd.GeoDataFrame) -> pd.DataFrame:
    '''Check if geometries intersect.

    Args:
        sp_1 (gpd.GeoDataFrame): First geometry.
        sp_2 (gpd.GeoDataFrame): Second geometry.

    Returns:
        pd.DataFrame: Dataframe with a column, 'intersects' which is True if two geometries intersect and False if they don't. Attributes from both geometries are included.

    Notes:
        - Each individual feature pairs are tested. So if 'sp_1' has m features and 'sp_2' has n features, the resulting dataframe will have m*n rows.
    '''
    # df_intersects = pd.DataFrame()
    # for i, row_i in sp_1.iterrows():
    #     for j, row_j in sp_2.iterrows():
    #         check = row_i.geometry.intersects(row_j.geometry)

    #         temp_df_intersects = \
    #         (pd_concat_cols_multiple(
    #             sp_1.iloc[[i]].drop(columns='geometry'),
    #             sp_2.iloc[[j]].drop(columns='geometry'),
    #             )
    #             .assign(intersects = [check])
    #         )

    #         df_intersects = df_intersects.pipe(pd_concat_rows, temp_df_intersects)

    df_intersects = pd.DataFrame()
    pbar = tqdm(total=sp_1.shape[0])
    for i, poly_1 in sp_1.reset_index(drop=True).iterrows():
        _intersects = poly_1.geometry.intersects(sp_2.geometry)
    
        _df_2 = sp_2.drop(columns='geometry')
        _df_1 = pd.concat([sp_1.iloc[[i]].drop(columns='geometry')]*_df_2.shape[0], ignore_index=True)
    
        _df_intersects = pd_concat_cols(_df_1, _df_2).assign(intersects = _intersects)
    
        df_intersects = df_intersects.pipe(pd_concat_rows, _df_intersects)

        pbar.update(1)

    pbar.close()

    return df_intersects

#%%
def sp_intersects_summary(sp_1: gpd.GeoDataFrame, sp_2: gpd.GeoDataFrame, count = False, return_series = False) -> np.ndarray | pd.Series:
    '''Check if geometries in 'sp_1' intersect any of the geometries in 'sp_2'. Uses 'sp_intersects()' as a backend.

    Args:
        sp_1 (gpd.GeoDataFrame): First geometry.
        sp_2 (gpd.GeoDataFrame): Second geometry.
        count (bool, False): Whether to return True/False or count (number of intersersections). Defaults to False (returns True/False).
        return_series (bool, False): Whether to return numpy array or pandas series. Defaults to False (return numpy array).

    Returns:
        np.ndarray | pd.Series: An array or series of True/False values (or intersection counts) indicating if (or how many times) each feature in 'sp_1' intersects any feature in 'sp_2'. The length of this array is the same as the number of features (rows) in 'sp_1'.
    '''
    sp_1 = sp_1.assign(_sn = lambda _: np.arange(_.shape[0]))

    df_intersects = sp_intersects(sp_1, sp_2)

    v_intersects = \
    (df_intersects
        .groupby('_sn')
        ['intersects']
        .sum()
    )

    if not return_series:
        v_intersects = v_intersects.to_numpy()

    if not count:
        v_intersects = (v_intersects > 0)

    return v_intersects

#%%
def sp_get_within(sp_from: gpd.GeoDataFrame, sp_to: gpd.GeoDataFrame = None, distance_within: float = 0) -> gpd.GeoDataFrame:
    '''Get geometry features (in 'sp_from') within a certain distance of another geoemtry (in 'sp_to').

    Args:
        sp_from (gpd.GeoDataFrame): Geometry of features from which to get within-features.
        sp_to (gpd.GeoDataFrame, optional): Geometry of features to which to get the within-features. Defaults to None, i.e. use 'sp_from'.
        distance_within (float, optional): Distance within which to check closeness. Defaults to 0.

    Returns:
        gpd.GeoDataFrame: Geometry of close features.

    Notes:
        - Result has columns from 'sp_from' (all except geometry) and 'sp_to' (all).
        - If 'sp_to' is None:
            - 'sp_from' is used as of 'sp_to',
            - within-serach is not done for corresponding features in both, 'sp_from' and 'sp_to',
            - columns in 'sp_from' are prefixed '_1' and columns in 'sp_to' are prefixed '_2' (except geometry column which is unchanged)
        - For reach feature in 'sp_from', the features in 'so_to' within 'distance_within' are filtered.
        - A column named 'distance' is added which shows the distance between the features in 'sp_from' and 'sp_to'.
    '''
    _flag_self = False
    if sp_to is None:
        sp_to = sp_from.copy()
        sp_from = sp_from.add_suffix('_1').rename(columns={'geometry_1': 'geometry'})
        sp_to = sp_to.add_suffix('_2').rename(columns={'geometry_2': 'geometry'})
        _flag_self = True

    spatial_index = rtree.index.Index()
    for i, point in enumerate(sp_to.geometry):
        spatial_index.insert(i, point.bounds)
    
    sp_within = gpd.GeoDataFrame()
    pbar = tqdm(total=sp_from.shape[0])
    for i in range(sp_from.shape[0]):
        _c_sp_from = sp_from.iloc[[i]]

        _within = np.array(list(spatial_index.intersection(_c_sp_from.iloc[0].geometry.buffer(distance_within).bounds)))

        if _flag_self:
            _within = _within[_within != i]

        if len(_within) > 0:
            if _flag_self:
                _within = _within[_within != i]
            
            _c_sp_to = sp_to.iloc[_within]

            distances = _c_sp_from.iloc[0].geometry.distance(_c_sp_to.geometry)

            _c_sp_to = \
            (_c_sp_to
                .assign(distances = distances)
                .loc[lambda _: _.distances <= distance_within]
                .sort_values('distances')
            )

            if _c_sp_to.shape[0] > 0:
                _c_sp_from = pd_repeat_rows(_c_sp_from.drop(columns='geometry'), _c_sp_to.shape[0])

                _t_sp_within = pd_concat_cols(_c_sp_from, _c_sp_to)

                sp_within = sp_within.pipe(pd_concat_rows, _t_sp_within)

        pbar.update(1)

    pbar.close()

    sp_within = gpd.GeoDataFrame(sp_within, crs = sp_from.crs)

    return sp_within

#%%
def sp_get_nearest(sp_from: gpd.GeoDataFrame, sp_to: gpd.GeoDataFrame = None, distance_within: float = 0) -> gpd.GeoDataFrame:
    '''Get geometry features (in 'sp_from') nearest to another geoemtry (in 'sp_to').

    Args:
        sp_from (gpd.GeoDataFrame): Geometry of features from which to get the nearest features.
        sp_to (gpd.GeoDataFrame, optional): Geometry of features to which to get the nearest features. Defaults to None, i.e. use 'sp_from'.

    Returns:
        gpd.GeoDataFrame: Geometry of nearest features.

    Notes:
        - Result has columns from 'sp_from' (all except geometry) and 'sp_to' (all).
        - If 'sp_to' is None:
            - 'sp_from' is used as of 'sp_to',
            - within-serach is not done for corresponding features in both, 'sp_from' and 'sp_to',
            - columns in 'sp_from' are prefixed '_1' and columns in 'sp_to' are prefixed '_2' (except geometry column which is unchanged)
        - For reach feature in 'sp_from', the nearest features in 'so_to' are filtered.
    '''
    _flag_self = False
    if sp_to is None:
        sp_to = sp_from.copy()
        sp_from = sp_from.add_suffix('_1').rename(columns={'geometry_1': 'geometry'})
        sp_to = sp_to.add_suffix('_2').rename(columns={'geometry_2': 'geometry'})
        _flag_self = True

    spatial_index = rtree.index.Index()
    for i, point in enumerate(sp_to.geometry):
        spatial_index.insert(i, point.bounds)
    
    sp_nearest = gpd.GeoDataFrame()
    pbar = tqdm(total=sp_from.shape[0])
    for i in range(sp_from.shape[0]):
        _c_sp_from = sp_from.iloc[[i]]

        if _flag_self:
            spatial_index.delete(i, sp_to.geometry.iloc[i].bounds)
            _nearest = np.array(list(spatial_index.nearest(_c_sp_from.iloc[0].geometry.bounds)))
            spatial_index.insert(i, sp_to.geometry.iloc[i].bounds)
        else:
            _nearest = np.array(list(spatial_index.nearest(_c_sp_from.iloc[0].geometry.bounds)))

        if len(_nearest) > 0:
            _c_sp_to = sp_to.iloc[_nearest]

            _c_sp_from = pd_repeat_rows(_c_sp_from.drop(columns='geometry'), _c_sp_to.shape[0])

            _t_sp_nearest = pd_concat_cols(_c_sp_from, _c_sp_to)

            sp_nearest = sp_nearest.pipe(pd_concat_rows, _t_sp_nearest)

        pbar.update(1)
    
    pbar.close()

    sp_nearest = gpd.GeoDataFrame(sp_nearest, crs = sp_from.crs)

    return sp_nearest

#endregion -----------------------------------------------------------------------------------------
#region Functions: Chainage

#%%
#TODO Make this work with multiple lines
def sp_get_chainage(sp_line: gpd.GeoDataFrame, sp_points: gpd.GeoDataFrame, return_series=True) -> np.ndarray | pd.Series:
    '''Get chainage of points on a polyline.

    Args:
        sp_line (GeoDataFrame): Polyline geodataframe with single feature. For multiple features, first feature is used.
        sp_points (GeoDataFrame): Points geodataframe.
        return_series (bool, optional): Return series (if True) or list (if False). Defaults to True.

    Returns:
        np.ndarray | pd.Series of float: Array or series of chainages. Same unit as geodataframe.
    '''
    chainage = [sp_line.geometry.iloc[0].project(sp_point) for sp_point in sp_points.geometry]
    # chainage = [sp_line.geometry.project(sp_point).iloc[0] for sp_point in sp_points.geometry]
    if return_series:
        return (pd.Series(chainage))
    else:
        return (np.array(chainage))

#%%
#TODO Make this work with multiple lines based on a group column
def sp_get_chainage_from_df_xy(df_xy: pd.DataFrame, col_group: str=None) -> pd.DataFrame:
    '''Get chainage from dataframe.

    Args:
        df_xy (DataFrame): Dataframe with 'x' and 'y' columns.
        col_grou (str): Column to group the values by. Chainage is calculated for each group separately.

    Returns:
        pd.DataFrame: Dataframe with three appended columns: 'dist' (distance from previous point), 'chainage' (chainage from first point), and 'chainage_normalized' (chainage normalized between 0 and 1).
    '''
    df_chainage = \
        (df_xy
            .assign(diff_x = lambda _: _['x'].diff().fillna(0))
            .assign(diff_y = lambda _: _['y'].diff().fillna(0))
            .assign(dist = lambda _: np.sqrt(_['diff_x']**2 + _['diff_y']**2))
            .assign(chainage = lambda _: _['dist'].cumsum())
            .drop(['diff_x', 'diff_y'], axis=1)
        )
    
    if col_group is not None:
        df_chainage = \
        (df_chainage
            .assign(chainage = lambda _: _['chainage'] - _.groupby(col_group)['chainage'].transform('min'))
            .assign(chainage_normalized = lambda _: _['chainage'] / _.groupby(col_group)['chainage'].transform('max'))
        )
    else:
        df_chainage = \
        (df_chainage
            .assign(chainage_normalized = lambda _: _['chainage'] / _['chainage'].max())
        )
        
    return (df_chainage)

#endregion -----------------------------------------------------------------------------------------
#region Functions: Zonal Stats

#%%
def sp_zonal_stats_points(sp_points: gpd.GeoDataFrame, files_raster: str|list|np.ndarray|pd.Series, col_names: str|list|np.ndarray|pd.Series = None, id_cols: str|list|np.ndarray|pd.Series = None) -> np.ndarray|pd.DataFrame:
    '''Get raster values at points.

    Args:
        sp_points (GeoDataFrame): Geodataframe of points.
        files_raster (str | list | np.ndarray | pd.Series of str): Vector of raster file(s).
        col_names (str | list | np.ndarray | pd.Series): Vector of column names. Should be same length as 'files_raster'. Defaults to None.
        id_cols (str | list | np.ndarray | pd.Series): Vector of columns from 'sp_poly' to append to results. Only useful when 'files_raster' is not str. Defaults to None.

    Returns:
        np.ndarray | pd.DataFrame: The raster values at points.

    Notes:
        - If 'files_raster' is a string, an array of raster values is returned in same order 'sp_points'.
        - If 'files_raster' is a vector, a dataframe of raster values is returned. The rows indicate the features in 'sp_points' in order. The columns indicate the 'files_raster' in order.

    Examples:
        >>> sp_zonal_stats_points(sp_points, files_rasters[0])
        >>> sp_zonal_stats_points(sp_points, files_rasters, id_cols='name', col_names=os_basename(files_raster, keep_extension=False))
    '''
    df_xy = sp_points.geometry.get_coordinates()
    coords = [(x,y) for x, y in zip(df_xy.x, df_xy.y)]

    if isinstance(files_raster, str):
        with rasterio.open(files_raster) as f:
            temp_values = [val[0] for val in f.sample(coords)] # https://rasterio.readthedocs.io/en/latest/api/rasterio._io.html#rasterio._io.DatasetReaderBase.sample
        temp_values = np.array(temp_values)

        return (temp_values)
    else:
        df_values = []
        for file_raster in files_raster:
            with rasterio.open(file_raster) as f:
                df_values.append([val[0] for val in f.sample(coords)]) # https://rasterio.readthedocs.io/en/latest/api/rasterio._io.html#rasterio._io.DatasetReaderBase.sample
        df_values = pd.DataFrame(df_values).T

        if col_names is not None:
            df_values = df_values.pipe(pd_set_colnames, col_names)

        if id_cols is not None:
            id_cols = pd_to_series(id_cols)
            df_values = df_values.pipe(pd_concat_cols, sp_points.loc[:, id_cols]).pipe(pd_select_simple, id_cols.tolist())

        return (df_values)

#%%
def sp_zonal_stats_line(sp_lines: gpd.GeoDataFrame, files_raster: str|list|np.ndarray|pd.Series, spacing: float, id_cols: str|list|np.ndarray|pd.Series = None, files_raster_mapped: str|list|np.ndarray|pd.Series = None, filename_colname = 'file', smoothen_span: float = None) -> pd.DataFrame:
    '''Get raster values at lines. Values are sampled at start and end point and points in-between separated by provided 'spacing'.

    Args:
        sp_lines (GeoDataFrame): Geodataframe of lines.
        files_raster (str | list | np.ndarray | pd.Series): Vector of raster file(s).
        spacing (float): Spacing along line to sample raster values at.
        id_cols (str | list | np.ndarray | pd.Series): Vector of columns from 'sp_lines' to append to results. Defaults to None.
        files_raster_mapped (str | list | np.ndarray | pd.Series): Vector of proxies for 'files_raster'. Should be same length as 'files_raster'. Only comes into play when 'files_raster' is not None. Defaults to None.
        filename_colname (str): Name of column that indicates the corresponding raster file. Only comes into play when 'files_raster' is not None. Defaults to 'file'.
        smoothen_span (float, optional): Proportion of number of points for local weighted smoothing. Defaults to None. No smoothing is done if set to None.

    Returns:
        pd.DataFrame: The raster values at each sampled point.

    Examples:
        >>> sp_zonal_stats_line(sp_roads, files_raster[0], spacing=500)
        >>> sp_zonal_stats_line(sp_roads, [files_raster[0]], spacing=500)
        >>> sp_zonal_stats_line(sp_roads, files_raster, spacing=500)
        >>> sp_zonal_stats_line(sp_roads,
                                files_raster,
                                spacing=500,
                                id_cols='FULLNAME',
                                files_raster_mapped=os_basename(files_raster))
    '''
    files_raster_is_str = True if isinstance(files_raster, str) else False

    files_raster = pd_to_series(files_raster)
    if files_raster_mapped is None:
        files_raster_mapped = pd_to_series(files_raster)

    df_profile = pd.DataFrame()
    for i in np.arange(0, sp_lines.shape[0]):
        sp_line = sp_lines.iloc[[i]]
        sp_points = sp_get_points_along_line(sp_line, spacing = spacing)

        for j, file_raster in enumerate(files_raster):
            sp_points = sp_points.assign(elev = sp_zonal_stats_points(sp_points, file_raster))

            temp_df_profile = sp_points.pipe(pd_drop, 'geometry')

            if smoothen_span is not None:
                # window_length = int(np.round(temp_df_profile.shape[0]*smoothen_span))
                # temp_df_profile = temp_df_profile.assign(elev_sm = lambda _: savgol_filter(_['elev'], window_length, 2))
                temp_df_profile = temp_df_profile.assign(elev_sm = lambda _: smoothen_line(_['elev'], window_count=smoothen_span))

            if not files_raster_is_str:
                temp_df_profile = temp_df_profile.assign(**{filename_colname: files_raster_mapped[j]})

            if id_cols is not None:
                id_cols = pd_to_series(id_cols)

                temp_df = sp_line[id_cols].reset_index(drop=True)
                temp_df = temp_df.loc[temp_df.index.repeat(temp_df_profile.shape[0])]

                temp_df_profile = temp_df_profile.pipe(pd_concat_cols, temp_df)

            df_profile = df_profile.pipe(pd_concat_rows, temp_df_profile)

    if files_raster_is_str:
        df_profile = df_profile.pipe(pd_select_simple, id_cols)
    else:
        df_profile = df_profile.pipe(pd_select_simple, filename_colname).pipe(pd_select_simple, id_cols)

    return (df_profile)

#%%
def sp_zonal_stats_poly(sp_poly: gpd.GeoDataFrame, files_raster: str|list|np.ndarray|pd.Series, stats: str|list=['min', 'max', 'mean', 'sum', 'median', 'majority'], id_cols: str|list|np.ndarray|pd.Series = None, files_raster_mapped: str|list|np.ndarray|pd.Series = None, filename_colname = 'file') -> np.ndarray|pd.DataFrame|dict:
    '''Get raster value summaries at polygons.

    Args:
        sp_poly (GeoDataFrame): Geodataframe of polygons.
        files_raster (str | list | np.ndarray | pd.Series): Vector of raster file(s)
        stats (str | list of str): Stat to use. Defaults to ['min', 'max', 'mean', 'sum', 'median', 'majority']. Acceptable values for the list are: 'sum', 'std', 'median', 'majority', 'minority', 'unique', 'range', 'nodata', 'percentile'. Percentile statistic can be used by specifying 'percentile_<q>' where <q> can be a floating point number between 0 and 100.
        id_cols (str | list | np.ndarray | pd.Series): Vector of columns from 'sp_poly' to append to results. Doesn't come into play if both 'files_raster' and 'stats' are str. Defaults to None.
        files_raster_mapped (str | list | np.ndarray | pd.Series): Vector of proxies for 'files_raster'. Should be same length as 'files_raster'. Defaults to None.
        filename_colname (str): Name of column that indicates the corresponding raster file. Only comes into play when 'files_raster' and 'stats' are both not str. Defalts to 'file'.

    Returns:
        np.ndarray | pd.DataFrame | dict: The summary of raster values by specified statistics at each polygon.

    Notes:
        - If 'files_raster' is a string and 'stats' is a string, an array of raster values is returned in same order 'sp_poly'.
        - If 'files_raster' is a vector and 'stats' is a string, a dataframe of raster values is returned. The rows indicate the 'sp_poly' in order. The columns indicate the 'files_raster' in order.
        - If 'files_raster' is a string and 'stats' is a vector, a dataframe of raster values is returned. The rows indicate the 'sp_poly' in order. The columns indicate the 'stats' in order. 'files_raster_mapped' is used as column names if not None.
        - If 'files_raster' is a vector and 'stats' is a vector, a dataframe of raster values is returned. Each item is a dictionary corresponding to the raster value for each file in order. The rows indicate 'sp_poly' in order. The columns indicate the 'stats' in order. An additional column, 'filename_colname' indicates the corresponding raster file. 'files_raster_mapped' used instead of filenames if it's not None.

    Examples:
        >>> sp_zonal_stats_poly(sp_poly,
                                files_rasters[0],
                                stats = 'sum')
        >>> sp_zonal_stats_poly(sp_poly,
                                files_rasters[0],
                                stats = ['sum'],
                                id_cols = 'name')
        >>> sp_zonal_stats_poly(sp_poly,
                                files_rasters[0],
                                stats = ['sum', 'mean'],
                                id_cols = 'name',
                                files_raster_mapped=os_basename(files_raster, keep_extension=False))
        >>> sp_zonal_stats_poly(sp_poly,
                                files_rasters,
                                stats = 'mean',
                                id_cols = 'name',
                                files_raster_mapped=os_basename(files_raster, keep_extension=False))
        >>> sp_zonal_stats_poly(sp_poly,
                                files_rasters,
                                stats = ['mean'],
                                id_cols = 'name',
                                filename_colname='type',
                                files_raster_mapped=os_basename(files_raster, keep_extension=False))
        >>> sp_zonal_stats_poly(sp_poly,
                                files_rasters,
                                stats = ['sum', 'mean'],
                                id_cols = 'name',
                                filename_colname='type',
                                files_raster_mapped=os_basename(files_raster, keep_extension=False))
    '''
    if isinstance(files_raster, str):
        if isinstance(stats, str):
            v_values = rs.zonal_stats(sp_poly, files_raster, stats=[stats])
            v_values = pd.DataFrame(v_values).iloc[:, 0].to_numpy()

            return (v_values)
        else:
            df_values = rs.zonal_stats(sp_poly, files_raster, stats=stats)
            df_values = pd.DataFrame(df_values)

            if id_cols is not None:
                id_cols = pd_to_series(id_cols)
                df_values = df_values.pipe(pd_concat_cols, sp_poly.loc[:, id_cols]).pipe(pd_select_simple, id_cols.tolist())

            return (df_values)
    else:
        if files_raster_mapped is not None:
            files_raster_mapped = pd_to_series(files_raster_mapped)
        if isinstance(stats, str):
            df_values = []
            for file_raster in files_raster:
                temp_values = rs.zonal_stats(sp_poly, file_raster, stats=[stats])
                temp_values = pd.DataFrame(temp_values).iloc[:, 0]
                df_values.append(temp_values.to_list())
            df_values = pd.DataFrame(df_values).T

            if files_raster_mapped is not None:
                df_values = df_values.pipe(pd_set_colnames, files_raster_mapped)

            if id_cols is not None:
                id_cols = pd_to_series(id_cols)
                df_values = df_values.pipe(pd_concat_cols, sp_poly.loc[:, id_cols]).pipe(pd_select_simple, id_cols.tolist())

            return (df_values)
        else:
            df_values = pd.DataFrame()
            for i, file_raster in enumerate(files_raster):
                if files_raster_mapped is not None:
                    file_raster_mapped = files_raster_mapped.iloc[i]
                else:
                    file_raster_mapped = file_raster
                temp_df_values = rs.zonal_stats(sp_poly, file_raster, stats=stats)
                temp_df_values = pd.DataFrame(temp_df_values).assign(**{filename_colname: file_raster_mapped})

                if id_cols is not None:
                    id_cols = pd_to_series(id_cols)
                    temp_df_values = temp_df_values.pipe(pd_concat_cols, sp_poly.loc[:, id_cols]).pipe(pd_select_simple, id_cols.tolist())

                df_values = df_values.pipe(pd_concat_rows, temp_df_values)

            return (df_values)

#%%
def sp_zonal_stats_point_xr(xr_data: xr.DataArray, method: Literal['linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'quintic', 'polynomial', 'pchip', 'barycentric', 'krogh', 'akima', 'makima'] = 'linear', col_time='time', **coords) -> pd.DataFrame:
    '''Get values at a point from an xarray- dataset.

    Args:
        xr_data (xr.DataArray): xarray data array.
        method (Literal[&#39;linear&#39;, &#39;nearest&#39;, &#39;zero&#39;, &#39;slinear&#39;, &#39;quadratic&#39;, &#39;cubic&#39;, &#39;quintic&#39;, &#39;polynomial&#39;, &#39;pchip&#39;, &#39;barycentric&#39;, &#39;krogh&#39;, &#39;akima&#39;, &#39;makima&#39;], optional): Interpolation method to use. Defaults to 'linear'.
        col_time (str, optional): Name of time column. Defaults to 'time'.
        **coords: x and y coordinates.

    Returns:
        pd.DataFrame: Dataframe with two columns: 'time' and 'values'.

    Examples:
        >>> sp_zonal_stats_point_xr(xr_data, latitude=29.74, longitude=-90.75)
    '''
    _xr = xr_data.interp(**coords, method=method)
    _values = _xr.values
    _time = _xr[col_time].values

    df = pd.DataFrame(dict(time = _time, values = _values))

    return df

#endregion -----------------------------------------------------------------------------------------
#region Functions: Spatial Operations

#%%
#TODO handle units
def sp_buffer(sp: gpd.GeoDataFrame, distance: float) -> gpd.GeoDataFrame:
    '''Buffer a geodataframe.

    Args:
        sp (gpd.GeoDataFrame): Geodataframe to buffer.
        distance (float): Buffer distance. Unit should match the crs of 'sp'.

    Returns:
        gpd.GeoDataFrame: Buffered geodataframe with same attribute table as 'sp'.
    '''
    buffered = sp.buffer(distance)
    sp_buffered = gpd.GeoDataFrame(sp.drop(columns='geometry'), geometry=buffered)
    
    return sp_buffered

#endregion -----------------------------------------------------------------------------------------
#region Functions: Concat

#%%
def sp_concat_rows(sp1: gpd.GeoDataFrame, sp2: gpd.GeoDataFrame, ignore_index = True) -> gpd.GeoDataFrame:
    '''Concatenate geodataframes by rows. Mainly useful for piping with 'pd.pipe()'. Wrapper around 'pd.concat()'. If one of the geodataframes is blank, the other is returned, ensuring no change in datatype like with 'pd.concat()'. The crs of 'sp1' is used if exists. Otherwise, crs of 'sp2' is used.

    Args:
        sp1 (gpd.GeoDataFrame): Geodataframe.
        sp2 (gpd.GeoDataFrame): Geodataframe.
        ignore_index (bool):  If True, do not use the index values along the concatenation axis. The resulting axis will be labeled 0, ..., n - 1. Defaults to True.

    Returns:
         (gpd.GeoDataFrame): Concatenated geodataframe.

    Examples:
        >>> sp_concat_rows(sp1, sp2)
        >>> sp1.pipe(sp_concat_rows, sp2)
    '''
    crs = None
    if not sp1.empty:
        if sp1.crs is not None:
            crs = sp1.crs
    if crs is None:
        if not sp2.empty:
            if sp2.crs is not None:
                crs = sp2.crs
    sp = gpd.GeoDataFrame(pd.concat([sp1, sp2], axis=0, ignore_index=ignore_index))
    sp.crs = crs
    return (sp)

#endregion -----------------------------------------------------------------------------------------
#region Functions: Others

#%%
def sp_explode(sp: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    '''Explodes geodataframe.

    Args:
        sp (gpd.GeoDataFrame): Geodataframe with one or more features.

    Returns:
        gpd.GeoDataFrame: Exploded geodataframe with additional columns: 'id_geom' indicating individual geometry parts, 'id_sp' indicating index of 'sp', and 'id_part' indicating individual geometry parts for each index of 'sp'.

    Notes:
        - 'id_geom' is f'{id_sp}__{id_part}' and is unique.
        - If all geometry are singlepart, each entry in 'id' will be unique, and 'id_part' will all be 0.
        - For a multipart geometry, 'id_sp' will be the same, and 'id_part' will be unique.

    Examples:
        >>> sp_explode(sp_points)
    '''
    sp_exploded = \
        (sp
            .explode(index_parts=True)
            .reset_index()
            .rename(columns={'level_0': 'id_sp',
                            'level_1': 'id_part'})
            .assign(id_geom=lambda _: str_concat(_['id_sp'], '__', _['id_part']))
            .pipe(pd_select_simple, 'id_geom')
        )
    
    sp_exploded.crs = sp.crs

    return sp_exploded

#%%
def sp_offset_line_poly(sp: gpd.GeoDataFrame, distance: float, join_style: Literal['mitre', 'round', 'bevel']='mitre', id_col:str=None) -> gpd.GeoDataFrame:
    '''Offset polyline or polygon.

    Args:
        sp (gpd.GeoDataFrame): Polyline or polygon geodataframe with one or more features.
        distance (numeric): Distance to offset by. Same unit as gdf. Positive means offset left. Direction is determined by following the direction of the given geometric points.
        join_style (str, optional): Join style for corners between line segments. Acceptable values are 'round' (rounded corner), 'mitre' (sharp corner), and 'bevel' (bevelled corner). Defaults to 'mitre'.
        id_col (str, optional): Column name to use as id column. This column is added to the output with corresponding values taken from 'sp_lines'.

    Returns:
        gpd.GeoDataFrame: Polyline or polygon geodataframe with offsetted feature.
    '''
    sp_offset_all = gpd.GeoDataFrame()
    for i, row in sp.reset_index(drop=True).iterrows():
        sp_current = sp.iloc[[i]]

        sp_offset = gpd.GeoDataFrame.from_features(gpd.GeoSeries([sp_current.geometry.iloc[0].offset_curve(distance, join_style=join_style)]))
    
        if id_col is not None:
            sp_offset[id_col] = row[id_col]

        sp_offset_all = sp_offset_all.pipe(pd_concat_rows, sp_offset)

    sp_offset_all.crs = sp.crs
    
    return (sp_offset_all)

#%%
def sp_get_nearest_points(sp_line: gpd.GeoDataFrame, sp_points: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    '''Get nearest points on a polyline.

    Args:
        sp_line (GeoDataFrame): Polyline geodataframe with single feature. For multiple features, first feature is used.
        sp_points (GeoDataFrame): Points geodataframe.

    Returns:
        GeoDataFrame: Points geodaframe.
    '''
    v_pts_nearest = [ops.nearest_points(sp_pts_geometry, sp_line.geometry.iloc[0])[1] for sp_pts_geometry in sp_points.geometry]
    sp_points_nearest = gpd.GeoDataFrame(geometry = v_pts_nearest)
    sp_points_nearest.crs = sp_points.crs

    return (sp_points_nearest)
    
#%%
def sp_get_points_along_line(sp_lines: gpd.GeoDataFrame, v_distances_normalized: list|np.ndarray|pd.Series=None, count: int=None, spacing: float=None, spacing_normalized: float=None, include_ends=True, id_col:str=None) -> gpd.GeoDataFrame:
    '''Generate points along polyline.

    Args:
        sp_line (gpd.GeoDataFrame): Polyline geodataframe with one of more feature(s).
        v_distances (list | np.ndarray | pd.Series of float, optional): Vector of normalized distances ([0, 1]). Defaults to None. 0 means start of line and 1 means end.
        count (int, optional): Number of points to generate. Defaults to None.
        spacing (float, optional): Spacing between each point in absolute units. Defaults to None.
        spacing_normalized (float, optional): Spacing between each point in relative units ([0, 1]). Defaults to None.
        include_ends (bool, optional): Indicates where points at the ends (start and end) need to be included. Defaults to True. Overridden when 'v_distances_normalized' is used.
        id_col (str, optional): Column name to use as id column. This column is added to the output with corresponding values taken from 'sp_lines'.

    Returns:
        gpd.GeoDataFrame: Geodataframe of points. The geodataframe has two columns: 'chainage_normalized' and 'chainage', listing normalized chainages and absolute chainages for each point.

    Notes:
        - Only one of 'v_distances_normalized', 'spacing', 'spacing_normalized', and 'count' should be defined.
        - Priority order: 'v_distances_normalized' > 'spacing' > 'spacing_normalized' > 'count'.
        - 'include_ends' is overridden if 'v_distances_normalized' is used. Include 0 and 1 in 'v_distances_normalized' if ends are to be included.
        - 'include_ends = True' results in 'count' and not ('count' + 2) points if 'count' is used.
        - 'spacing' and 'spacing_normlized' start spacing form the starting point, so the spacing at the end might be smaller than specified.

    Examples:
        >>> sp_get_points_along_line(temp_sp_line, v_distances_normalized=[0,0.1,0.5,0.75,1])
        >>> sp_get_points_along_line(temp_sp_line, count=10, include_ends=False)
        >>> sp_get_points_along_line(temp_sp_line, spacing_normalized=0.3)
        >>> sp_get_points_along_line(temp_sp_line, spacing=1, include_ends=True)
        >>> sp_get_points_along_line(temp_sp_lines, spacing=1, include_ends=True, id_col='index')
    '''
    sp_points_all = gpd.GeoDataFrame()
    for i, row in sp_lines.reset_index(drop=True).iterrows():
        sp_line = sp_lines.iloc[[i]]

        temp_length = sp_line.length
        if v_distances_normalized is None:
            if count is not None:
                if include_ends:
                    v_distances_normalized = np.linspace(0,1,count)
                else:
                    v_distances_normalized = np.linspace(0,1,count+2)
                    v_distances_normalized = v_distances_normalized[1:len(v_distances_normalized)-1]
            if spacing is not None:
                spacing_normalized = spacing/temp_length.iloc[0]
            if spacing_normalized is not None:
                if include_ends:
                    v_distances_normalized = np.append(np.arange(0,1,spacing_normalized), 1)
                else:
                    v_distances_normalized = np.arange(spacing_normalized,1,spacing_normalized)
        v_distances_normalized = np.array(v_distances_normalized)
        sp_points = gpd.GeoDataFrame.from_features(gpd.GeoSeries([sp_line.geometry.iloc[0].interpolate(distance, normalized=True) for distance in v_distances_normalized]))
        sp_points = sp_points.eval('chainage_normalized = @v_distances_normalized').assign(chainage = lambda _: _['chainage_normalized']*temp_length.iloc[0])

        if id_col is not None:
            sp_points[id_col] = row[id_col]

        sp_points_all = sp_points_all.pipe(pd_concat_rows, sp_points)

    sp_points_all.crs = sp_lines.crs

    return (sp_points_all)

#%%
def sp_get_transects_along_line(sp_lines: gpd.GeoDataFrame, sp_line_pts: gpd.GeoDataFrame, dist_l: float, dist_r: float = None, method: Literal['perpendicular', 'offset']='perpendicular', join_col:str=None, id_col:str=None) -> gpd.GeoDataFrame:
    '''Generate transects along polyline.

    Args:
        sp_line (gpd.GeoDataFrame): Polyline geodataframe with one of more feature(s).
        sp_line_pts (gpd.GeoDataFrame): Geodataframe with points along the line. Use 'sp_get_points_along_line()' to generate points.
        dist_l (float): Length of transect in left direction.
        dist_r (float, optional): Lenght of transect in right direction. If not set, this is set to be equal to 'dist_l'. Defaults to None.
        method (Literal[&#39;perpendicular&#39;, &#39;offset&#39;], optional): Method used to create transects. Defaults to 'perpendicular'.
        join_col (str, optional): This attribute is necessary when the 'sp_line' has more than one feature as this is used to link 'sp_line' with 'sp_line_points'.
        id_col (str, optional): Column name of 'sp_line_pts' to use as id column. This column is added to the output with corresponding values taken from 'sp_lines'.

    Notes:
        - method='perpendicular': This creates perpendicular transects.
        - method='offset': This offsets the line on both sides and joins corresponding points in the offset lines.

    Returns:
        gpd.GeoDataFrame: Geodataframe of transects.

    Examples:
        >>> sp_xs2 = sp_get_transects_along_line(sp_line, sp_line_pts, 500, 1000)
        >>> sp_xs2 = sp_get_transects_along_line(sp_line, sp_line_pts, 500, method='offset')
        >>> sp_xs2 = sp_get_transects_along_line(sp_lines, sp_line_pts, 500, id_col='index')
    '''
    if dist_r is None:
        dist_r = dist_l
    
    if join_col is None:
        if sp_lines.shape[0] != 1:
            raise Exception('"join_col" is not specified even though provided polyline has multiple features!')
    
    sp_xs_all = gpd.GeoDataFrame()
    for i, row in sp_lines.reset_index(drop=True).iterrows():
        sp_line = sp_lines.iloc[[i]]

        if join_col is None:
            sp_line_pts_current = sp_line_pts
        else:
            sp_line_pts_current = sp_line_pts.loc[lambda _: _[join_col] == sp_line[join_col].iloc[0]]

        if method == 'perpendicular':
            sp_line_pts_updated = \
            (sp_line_pts_current
                .pipe(pd_concat_cols, sp_to_df_xy(sp_line_pts_current))
                .assign(x_diff_backward = lambda _: _['x'].diff(),
                        y_diff_backward = lambda _: _['y'].diff())
                .assign(x_diff_forward = lambda _: _['x_diff_backward'].shift(-1),
                        y_diff_forward = lambda _: _['y_diff_backward'].shift(-1))
                .assign(slope_backward = lambda _: np.arctan2(_['y_diff_backward'], _['x_diff_backward']))
                .assign(slope_forward = lambda _: np.arctan2(_['y_diff_forward'], _['x_diff_forward']))
                .assign(slope_rad = lambda _: pd_case_when(_['slope_backward'].isna(), _['slope_forward'],
                                                        _['slope_forward'].isna(), _['slope_backward'],
                                                        True, (_['slope_backward'] + _['slope_forward'])/2))
                .pipe(pd_select, 'geometry:chainage, x, y, slope_rad')
            )

            df_xs_pts = \
            (sp_line_pts_updated
                .reset_index()
                .assign(angle1=lambda _: _['slope_rad'] + np.pi/2,
                        x1=lambda _: _['x'] + dist_l*np.cos(_['angle1']),
                        y1=lambda _: _['y'] + dist_l*np.sin(_['angle1']),
                        angle2=lambda _: _['slope_rad'] - np.pi/2,
                        x2=lambda _: _['x'] + dist_r*np.cos(_['angle2']),
                        y2=lambda _: _['y'] + dist_r*np.sin(_['angle2']))
                [['index', 'slope_rad', 'angle1', 'angle2', 'x1', 'x2', 'y1', 'y2']]
            )
            df_xs_l = \
            (df_xs_pts
                [['index', 'x1', 'y1']]
                .assign(type='left')
                .rename(columns={'x1': 'x', 'y1': 'y'})
            )
            df_xs_r = \
            (df_xs_pts
                [['index', 'x2', 'y2']]
                .assign(type='right')
                .rename(columns={'x2': 'x', 'y2': 'y'})
            )
            df_xs = pd_concat_rows(df_xs_l, df_xs_r).sort_values(['index', 'type'])
            sp_xs = sp_lines_from_df_xy(df_xs, column_group='index', crs=sp_line_pts.crs)
        elif method == 'offset':
            sp_line_l = sp_offset_line_poly(sp_line, dist_l, 'round')
            sp_line_r = sp_offset_line_poly(sp_line, -dist_r, 'round')
            
            sp_line_pts_l = sp_get_nearest_points(sp_line_l, sp_line_pts)
            sp_line_pts_r = sp_get_nearest_points(sp_line_r, sp_line_pts)

            # v_distances_normalized = sp_get_chainage(sp_line, sp_line_pts_current)
            # v_distances_normalized = v_distances_normalized/max(v_distances_normalized)

            # sp_line_pts_l = sp_get_points_along_line(sp_line_l, v_distances_normalized=v_distances_normalized)
            # sp_line_pts_r = sp_get_points_along_line(sp_line_r, v_distances_normalized=v_distances_normalized)
            
            from shapely.geometry import LineString
            sp_xs = gpd.GeoDataFrame()
            # Create a LineString geometry for each pair of start and end points
            sp_xs['geometry'] = sp_line_pts_l.apply(lambda x: LineString([x.geometry, sp_line_pts_r.loc[x.name].geometry]), axis=1)
            sp_xs.crs = sp_line_pts.crs

        if join_col is not None:
            sp_xs[join_col] = sp_line_pts_current[join_col].to_numpy()
        if id_col is not None:
            sp_xs[id_col] = sp_line_pts_current[id_col].to_numpy()

        sp_xs_all = sp_xs_all.pipe(pd_concat_rows, sp_xs)

    sp_xs_all.crs = sp_line.crs

    return (sp_xs_all)

#%%
def sp_get_mid_lines(sp_lines: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    '''Generate bisector lines between each successive lines in 'sp_lines'.

    Args:
        sp_line (gpd.GeoDataFrame): Polyline geodataframe with two of more feature(s).

    Returns:
        gpd.GeoDataFrame: Polyline geodataframe with bisected lines.
    '''
    sp_xs_mids = []
    # Iterate through the lines and create new lines that bisect the space between consecutive lines
    for i in range(len(sp_lines) - 1):
        temp_sp_line1 = sp_lines.iloc[[i]]
        temp_sp_line2 = sp_lines.iloc[[i+1]]

        temp_df_xy1 = sp_to_df_xy(temp_sp_line1)
        temp_df_xy2 = sp_to_df_xy(temp_sp_line2)

        temp_df_xy1 = sp_get_chainage_from_df_xy(temp_df_xy1)
        temp_df_xy2 = sp_get_chainage_from_df_xy(temp_df_xy2)

        temp_df_xy1 = temp_df_xy1.assign(chainage = lambda _: _.chainage/np.max(_.chainage))
        temp_df_xy2 = temp_df_xy2.assign(chainage = lambda _: _.chainage/np.max(_.chainage))

        temp_chainages = sorted(set(temp_df_xy1['chainage'].to_list() + temp_df_xy2['chainage'].to_list()))

        temp_sp_line1 = sp_get_points_along_line(temp_sp_line1, temp_chainages)
        temp_sp_line2 = sp_get_points_along_line(temp_sp_line2, temp_chainages)

        temp_df_xy1 = sp_to_df_xy(temp_sp_line1)
        temp_df_xy2 = sp_to_df_xy(temp_sp_line2)

        # Get the coordinates of the lines
        temp_coords1 = temp_df_xy1[['x', 'y']].to_numpy()
        temp_coords2 = temp_df_xy2[['x', 'y']].to_numpy()
        
        # Find the midpoints of each segment in the lines
        temp_new_line_coords = (temp_coords1 + temp_coords2)/2

        # # Find the midpoints of each segment in the lines
        # temp_midpoints1 = [get_midpoint(temp_coords1[j], temp_coords1[j + 1]) for j in range(len(temp_coords1) - 1)]
        # temp_midpoints2 = [get_midpoint(temp_coords2[j], temp_coords2[j + 1]) for j in range(len(temp_coords2) - 1)]
        
        # Create a new line connecting the midpoints of the two lines
        # temp_new_line_coords = [get_midpoint(temp_midpoints1[j], temp_midpoints2[j]) for j in range(min(len(temp_midpoints1), len(temp_midpoints2)))]
        temp_new_line = geometry.LineString(temp_new_line_coords)
        sp_xs_mids.append(temp_new_line)

    # Create a new GeoDataFrame with the new lines
    sp_xs_mids = gpd.GeoDataFrame(geometry=sp_xs_mids, crs=sp_lines.crs)

    return (sp_xs_mids)

#endregion -----------------------------------------------------------------------------------------
#region Functions: Plotly

#TODO Documentation for add_*.

#%%
class px_Map(px_Plot):
    '''An interface for declaratively creating plotly maps.

    Following are the main methods:
        - add_*(): Add different traces. Not all traces have been implemented. Main ones are:
            - add_sp_points(): Add points geodataframe.
            - add_sp_polylines(): Add polylines geodataframe.
            - add_sp_polygons(): Add polygons geodataframe.
            - add_sp_poygon_borders(): Add polygons geodataframe as borders.
            - add_sp_basemap(): Add basemap.
        - add(): Add traces directly from plotly trace objects.
        - label(): Add x and y labels and plot title.
        - legend(): Update legend properties.
        - colorbar(): Update colorbar legend properties.
        - size(): Update plot size.
        - layout(): Update layout properties.
        - show(): Show plot.
        - get_fig(): Get figure object.

    Examples:
        >>> (px_Map(sp=sp_states, zoom=2.5)
                .add_sp_polygons(sp_states,
                                color='water_prop',
                                legend_name='States',
                                hover_skip=True)
                .add_sp_polylines(sp_roads,
                                color_value='red',
                                width_value=3,
                                legend_name='Roads',
                                hover_name='FULLNAME',
                                hover_data=dict(x=False,
                                                y=False,
                                                id_geom=False,
                                                LINEARID=True))
                .add_sp_points(sp_capitals,
                               color_value='green',
                               size_value=8,
                               legend_name='Capitals',
                               hover_name='name',
                               hover_data=['state'])
                .add_sp_polygon_borders(sp_states,
                                        line_color='black',
                                        line_width=2,
                                        legend_name='States Boundary')
                .add_sp_basemap(Options_px_basemap.carto_darkmatter.value)
                .legend(x_anchor='right',
                        y_anchor='bottom',
                        x=1,
                        y=0.1)
                .colorbar(title='Water%',
                        orientation='h',
                        x_anchor='left',
                        y_anchor='bottom',
                        x=0,
                        y=0,
                        thickness=10,
                        len=0.5)
                .layout(margins=[0,0,0,0])
                .show()
            )
    '''
    fig = None

    def __init__(self,
                 sp=None,
                 center_lon=-95.7129,
                 center_lat=37.0902,
                 zoom=2.5,
                 **kwargs) -> None:
        if sp is not None:
            if sp.crs.to_epsg() != Options_epsg.wgs84.value:
                sp = sp.to_crs(Options_epsg.wgs84.value)

            temp_centroid = gpd.GeoDataFrame(geometry=sp.centroid)
            center_lon = temp_centroid.geometry.x.mean()
            center_lat = temp_centroid.geometry.y.mean()
        fig = px.choropleth_mapbox(center=dict(lon=center_lon,
                                               lat=center_lat),
                                   zoom=zoom,
                                   **kwargs)

        self.fig = fig

        self.add_sp_basemap(Options_px_basemap.none.value)

    def add_sp_basemap(self, basemap: str) -> Self:
        '''Add basemap.

        Args:
            basemap (str): Use `Options_px_basemap`. Or see 'Base Maps in layout.mapbox.style' in https://plotly.com/python/mapbox-layers/.

        Returns:
            Self: Self object.
        '''
        fig = self.fig

        if pd.Series(dir(Options_px_tiles)).str.contains(basemap).any():
            fig.update_layout(
                mapbox_style="white-bg",
                mapbox_layers=[
                    {
                        "below": "traces",
                        "sourcetype": "raster",
                        # "sourceattribution": "United States Geological Survey",
                        "source": [Options_px_tiles[basemap].value],
                    }
                ],
            )
        else:
            fig.update_layout(mapbox_style=basemap)

        return self

    def _dec_add_sp():
        '''Decorator to make the following updates:
            - Geodataframe coordiantes.
            - Hover arguemnts
        '''
        def inner(func):
            def wrapper(self, *args, **kwargs):
                kwargs = combine_arguments(func, [0, *args], kwargs)
                kwargs.pop('self')

                update_crs = kwargs['update_crs']

                if update_crs:
                    sp = kwargs['sp']

                    if sp.crs.to_epsg() != Options_epsg.wgs84.value:
                        sp = sp.to_crs(Options_epsg.wgs84.value)

                    kwargs['sp'] = sp

                trace = func(self, **kwargs)

                hover_skip_check = kwargs['hover_skip']

                if hover_skip_check:
                    trace = \
                    (trace
                        .update_traces(hoverinfo='skip',
                                       hovertemplate=None)
                    )

                self.add(trace)

                return self
            return wrapper
        return inner

    @_dec_add_sp()
    def add_sp_points(self,
                      sp,
                      color_value = None,
                      size_value = None,
                      symbol_value = None,
                      legend_name = None,
                      legend_show = True,
                      hover_skip = False,
                      update_crs = True,
                      **kwargs) -> Self:
        sp = sp.copy()
        sp['x'] = sp.geometry.x
        sp['y'] = sp.geometry.y
        trace = px.scatter_mapbox(sp,
                                #   lon=sp.geometry.x,
                                #   lat=sp.geometry.y,
                                  lon=sp['x'],
                                  lat=sp['y'],
                                  **kwargs)
        if color_value is not None:
            trace = \
            (trace
                .update_traces(marker=dict(color=color_value))
            )
        if size_value is not None:
            trace = \
            (trace
                .update_traces(marker=dict(size=size_value))
            )
        if symbol_value is not None:
            trace = \
            (trace
                .update_traces(marker=dict(symbol=symbol_value))
            )
        if legend_name is not None:
            if ('color' not in kwargs) and ('size' not in kwargs):
                trace = \
                (trace
                    .update_traces(name=legend_name,
                                   showlegend=legend_show)
                )
            else:
                trace = \
                (trace
                    .update_traces(legendgroup=legend_name,
                                   legendgrouptitle_text=legend_name,
                                   showlegend=legend_show)
                )

        return trace

    @_dec_add_sp()
    def add_sp_polylines(self,
                         sp,
                         color_value = None,
                         width_value = None,
                         dash_value = None,
                         legend_name = None,
                         legend_show = True,
                         hover_skip = False,
                         update_crs = True,
                         **kwargs) -> Self:
        df_lines_xy = sp_to_df_xy(sp, cols_keep_all=True)
        trace = px.line_mapbox(df_lines_xy,
                               lon=df_lines_xy['x'],
                               lat=df_lines_xy['y'],
                               line_group=df_lines_xy['id_geom'],
                               **kwargs)
        if color_value is not None:
            trace = \
            (trace
                .update_traces(line=dict(color=color_value))
            )
        if width_value is not None:
            trace = \
            (trace
                .update_traces(line=dict(width=width_value))
            )
        if dash_value is not None:
            trace = \
            (trace
                .update_traces(line=dict(dash=dash_value))
            )
        if legend_name is not None:
            if 'color' not in kwargs:
                trace = \
                (trace
                    .update_traces(name=legend_name,
                                   legendgroup=legend_name,
                                   showlegend=legend_show)
                )
            else:
                trace = \
                (trace
                    .update_traces(legendgroup=legend_name,
                                   legendgrouptitle_text=legend_name,
                                   showlegend=legend_show)
                )
        if 'color' not in kwargs:
            for i in range(len(trace.data)):
                if i == 0:
                    trace.data[i].showlegend = legend_show
                else:
                    trace.data[i].showlegend = False

        return trace

    @_dec_add_sp()
    def add_sp_polygons(self,
                        sp,
                        color_value = None,
                        line_color = None,
                        line_width = None,
                        line_dash = None,
                        legend_name = None,
                        legend_show = True,
                        hover_skip = False,
                        update_crs = True,
                        **kwargs) -> Self:
        if color_value is not None:
            kwargs['color_discrete_sequence'] = [color_value, color_value]
        trace = px.choropleth_mapbox(sp,
                                     locations=sp.index,
                                     geojson=sp.geometry,
                                     **kwargs)
        if line_color is not None:
            trace = \
            (trace
                .update_traces(marker=dict(line=dict(color=line_color)))
            )
        if line_width is not None:
            trace = \
            (trace
                .update_traces(marker=dict(line=dict(width=line_width)))
            )
        if line_dash is not None:
            trace = \
            (trace
                .update_traces(marker=dict(line=dict(dash=line_dash)))
            )
        if legend_name is not None:
            if 'color' not in kwargs:
                trace = \
                (trace
                    .update_traces(name=legend_name,
                                   legendgroup=legend_name,
                                   showlegend=legend_show)
                )
            else:
                trace = \
                (trace
                    .update_traces(legendgroup=legend_name,
                                   legendgrouptitle_text=legend_name,
                                   showlegend=legend_show)
                )

        return trace

    @_dec_add_sp()
    def add_sp_polygon_borders(self,
                               sp,
                               line_color = None,
                               line_width = None,
                               line_dash = None,
                               legend_name = None,
                               legend_show = True,
                               hover_skip = True,
                               update_crs = True,
                               **kwargs) -> Self:
        df_polygons_xy = sp_to_df_xy(sp, cols_keep_all=True)
        trace = px.line_mapbox(df_polygons_xy,
                               lon=df_polygons_xy['x'],
                               lat=df_polygons_xy['y'],
                               line_group=df_polygons_xy['id_geom'])
        if line_color is not None:
            trace = \
            (trace
                .update_traces(line=dict(color=line_color))
            )
        if line_width is not None:
            trace = \
            (trace
                .update_traces(line=dict(width=line_width))
            )
        if line_dash is not None:
            trace = \
            (trace
                .update_traces(line=dict(dash=line_dash))
            )
        if legend_name is not None:
            if 'color' not in kwargs:
                trace = \
                (trace
                    .update_traces(name=legend_name,
                                   legendgroup=legend_name,
                                   showlegend=legend_show)
                )
            else:
                trace = \
                (trace
                    .update_traces(legendgroup=legend_name,
                                   legendgrouptitle_text=legend_name,
                                   showlegend=legend_show)
                )
        if 'color' not in kwargs:
            for i in range(len(trace.data)):
                if i == 0:
                    trace.data[i].showlegend = legend_show
                else:
                    trace.data[i].showlegend = False

        return trace

#endregion -----------------------------------------------------------------------------------------
#region Archive

#%%
def sp_intersection(sp_1: gpd.GeoDataFrame, sp_2: gpd.GeoDataFrame, multipart = False) -> gpd.GeoDataFrame:
    '''Use gpd.overlay() instead of this. Get intersection of two geometries.

    Args:
        sp_1 (gpd.GeoDataFrame): First geometry.
        sp_2 (gpd.GeoDataFrame): Second geometry.
        multipart (bool, optional): Whether to include multippart geometries. If set to False, the intersected geometry is exploded usign 'sp_explode()'. Defaults to False.

    Returns:
        gpd.GeoDataFrame: Intersected geometry. Attributes from both geometries are included.
    '''
    sp_intersect = pd.DataFrame()
    for i, row_i in sp_1.iterrows():
        for j, row_j in sp_2.iterrows():
            if row_i.geometry.intersects(row_j.geometry):
                temp_sp_intersect = row_i.geometry.intersection(row_j.geometry)

                temp_sp_intersect = \
                (pd_concat_cols_multiple(
                    sp_1.iloc[[i]].drop(columns='geometry'),
                    sp_2.iloc[[j]].drop(columns='geometry'),
                    )
                    .assign(geometry = [temp_sp_intersect])
                )

                sp_intersect = sp_intersect.pipe(pd_concat_rows, temp_sp_intersect)

    sp_intersect = gpd.GeoDataFrame(sp_intersect, geometry='geometry')
    sp_intersect.crs = sp_1.crs

    if not multipart:
        sp_intersect = sp_explode(sp_intersect)

    return sp_intersect

#%%
def px_sp_create_map(sp = None, center_lon=-95.7129, center_lat=37.0902, zoom=2.5, **kwargs):
    if sp is not None:
        if sp.crs.to_epsg() != Options_epsg.wgs84.value:
            sp = sp.to_crs(Options_epsg.wgs84.value)

        temp_centroid = gpd.GeoDataFrame(geometry=sp.centroid)
        center_lon = temp_centroid.geometry.x.mean()
        center_lat = temp_centroid.geometry.y.mean()
        # temp_bounds = sp.bounds
        # temp_del_x = temp_bounds['maxx'].max() - temp_bounds['minx'].min()
        # temp_del_y = temp_bounds['maxy'].max() - temp_bounds['miny'].min()
        # zoom_x = 360/temp_del_x
        # zoom_y = 180/temp_del_y
    fig = px.choropleth_mapbox(center=dict(lon=center_lon,
                                           lat=center_lat),
                               zoom=zoom,
                               **kwargs)
    return fig

#%%
def px_add_trace_data(fig_original, *figs):
    # TODO not working (only takes first fig)
    for fig in figs:
        for i in range(len(fig.data)):
            fig_original.add_trace(fig.data[i])
        return fig_original

#%%
def px_sp_basemap(fig, basemap):
    if pd.Series(dir(Options_px_tiles)).str.contains(basemap).any():
        fig.update_layout(
            mapbox_style="white-bg",
            mapbox_layers=[
                {
                    "below": "traces",
                    "sourcetype": "raster",
                    # "sourceattribution": "United States Geological Survey",
                    "source": [Options_px_tiles[basemap].value],
                }
            ],
        )
    else:
        fig.update_layout(mapbox_style=basemap)

#%%
def px_sp_points(sp_points,
                 color_value = None,
                 size_value = None,
                 symbol_value = None,
                 legend_name = None,
                 hover_skip = False,
                 update_crs = True,
                 **kwargs):
    if update_crs:
        if sp_points.crs.to_epsg() != Options_epsg.wgs84.value:
            sp_points = sp_points.to_crs(Options_epsg.wgs84.value)
    fig = px.scatter_mapbox(sp_points,
                            lon=sp_points.geometry.x,
                            lat=sp_points.geometry.y,
                            **kwargs)
    if color_value is not None:
        fig = fig\
            .update_traces(marker=dict(color=color_value))
    if size_value is not None:
        fig = fig\
            .update_traces(marker=dict(size=size_value))
    if symbol_value is not None:
        fig = fig\
            .update_traces(marker=dict(symbol=symbol_value))
    if legend_name is not None:
        if ('color' not in kwargs) and ('size' not in kwargs):
            fig = fig\
                .update_traces(name=legend_name,
                               showlegend=True)
        else:
            fig = fig\
                .update_traces(legendgroup=legend_name,
                               legendgrouptitle_text=legend_name,
                               showlegend=True)
    if hover_skip:
        fig = fig\
            .update_traces(hoverinfo='skip',
                           hovertemplate=None)
    return fig

#%%
def px_sp_polylines(sp_lines,
                    color_value = None,
                    width_value = None,
                    dash_value = None,
                    legend_name = None,
                    hover_skip = False,
                    update_crs = True,
                    **kwargs):
    if update_crs:
        if sp_lines.crs.to_epsg() != Options_epsg.wgs84.value:
            sp_lines = sp_lines.to_crs(Options_epsg.wgs84.value)
    df_lines_xy = sp_to_df_xy(sp_lines, cols_keep_all=True)
    fig = px.line_mapbox(df_lines_xy,
                         lon=df_lines_xy['x'],
                         lat=df_lines_xy['y'],
                         line_group=df_lines_xy['id_geom'],
                         **kwargs)
    if color_value is not None:
        fig = fig\
            .update_traces(line=dict(color=color_value))
    if width_value is not None:
        fig = fig\
            .update_traces(line=dict(width=width_value))
    if dash_value is not None:
        fig = fig\
            .update_traces(line=dict(dash=dash_value))
    if legend_name is not None:
        if 'color' not in kwargs:
            fig = fig\
                .update_traces(name=legend_name,
                               legendgroup=legend_name,
                               showlegend=True)
        else:
            fig = fig\
                .update_traces(legendgroup=legend_name,
                               legendgrouptitle_text=legend_name,
                               showlegend=True)
    if 'color' not in kwargs:
        for i in range(len(fig.data)):
            if i == 0:
                fig.data[i].showlegend = True
            else:
                fig.data[i].showlegend = False
    if hover_skip:
        fig = fig\
            .update_traces(hoverinfo='skip',
                           hovertemplate=None)
    return fig

#%%
def px_sp_polygons(sp_polygons,
                   color_value = None,
                   line_color = None,
                   line_width = None,
                   line_dash = None,
                   legend_name = None,
                   hover_skip = False,
                   update_crs = True,
                   **kwargs):
    if update_crs:
        if sp_polygons.crs.to_epsg() != Options_epsg.wgs84.value:
            sp_polygons = sp_polygons.to_crs(Options_epsg.wgs84.value)
    if color_value is not None:
        kwargs['color_discrete_sequence'] = [color_value, color_value]
    fig = px.choropleth_mapbox(sp_polygons,
                               locations=sp_polygons.index,
                               geojson=sp_polygons.geometry,
                               **kwargs)
    if line_color is not None:
        fig = fig\
            .update_traces(marker=dict(line=dict(color=line_color)))
    if line_width is not None:
        fig = fig\
            .update_traces(marker=dict(line=dict(width=line_width)))
    if line_dash is not None:
        fig = fig\
            .update_traces(marker=dict(line=dict(dash=line_dash)))
    if legend_name is not None:
        if 'color' not in kwargs:
            fig = fig\
                .update_traces(name=legend_name,
                               legendgroup=legend_name,
                               showlegend=True)
        else:
            fig = fig\
                .update_traces(legendgroup=legend_name,
                               legendgrouptitle_text=legend_name,
                               showlegend=True)
    if hover_skip:
        fig = fig\
            .update_traces(hoverinfo='skip',
                           hovertemplate=None)
    return fig

#%%
def px_sp_polygon_borders(sp_polygons,
                          line_color = None,
                          line_width = None,
                          line_dash = None,
                          legend_name = None,
                          hover_skip = True,
                          update_crs = True,
                          **kwargs):
    if update_crs:
        if sp_polygons.crs.to_epsg() != Options_epsg.wgs84.value:
            sp_polygons = sp_polygons.to_crs(Options_epsg.wgs84.value)
    df_polygons_xy = sp_to_df_xy(sp_polygons, cols_keep_all=True)
    fig = px.line_mapbox(df_polygons_xy,
                         lon=df_polygons_xy['x'],
                         lat=df_polygons_xy['y'],
                         line_group=df_polygons_xy['id_geom'])
    if line_color is not None:
        fig = fig\
            .update_traces(line=dict(color=line_color))
    if line_width is not None:
        fig = fig\
            .update_traces(line=dict(width=line_width))
    if line_dash is not None:
        fig = fig\
            .update_traces(line=dict(dash=line_dash))
    if legend_name is not None:
        if 'color' not in kwargs:
            fig = fig\
                .update_traces(name=legend_name,
                               legendgroup=legend_name,
                               showlegend=True)
        else:
            fig = fig\
                .update_traces(legendgroup=legend_name,
                               legendgrouptitle_text=legend_name,
                               showlegend=True)
    if 'color' not in kwargs:
        for i in range(len(fig.data)):
            if i == 0:
                fig.data[i].showlegend = True
            else:
                fig.data[i].showlegend = False
    if hover_skip:
        fig = fig\
            .update_traces(hoverinfo='skip',
                           hovertemplate=None)
    return fig

#%%
# options_epsg = dict(wgs84 = 4326, nad83_LA_north = 3451, nad83_LA_south = 3452)
# class Options_epsg:
#     wgs84 = 4326
#     nad83_LA_north = 3451
#     nad83_LA_south = 3452

# #%%
# def zonal_stats_poly_multiple(sp_poly: gpd.GeoDataFrame, file_raster: str=None, files_raster: list|np.ndarray|pd.Series=None, stats=['min', 'max', 'mean', 'sum', 'median', 'majority']):
#     '''Get raster value summaries at polygons.

#     Args:
#         sp_poly (GeoDataFrame): Geodataframe of polygons.
#         file_raster (str, optional): Raster file. Defaults to None.
#         stats (list of str): Stat to use. Defaults to ['min', 'max', 'mean', 'sum', 'median', 'majority']. Acceptable values for the list are: 'sum', 'std', 'median', 'majority', 'minority', 'unique', 'range', 'nodata', 'percentile'. Percentile statistic can be used by specifying 'percentile_<q>' where <q> can be a floating point number between 0 and 100.

#     Returns:
#         pd.DataFrame: The summary of raster values by specified statistics at each polygon.

#     Notes:
#         - Only one of file_raster or files_raster need to be specified.
#         - The columns indicate the 'stats' in order. The rows indicate the 'sp_poly' in order.

#     Examples:
#         >>> zonal_stats_poly(sp_points, files_raster_tif[0], stats = 'median')
#         >>> zonal_stats_poly(sp_points, files_raster_tif[0], stats = ['sum', 'mean']).assign(id = sp_points['id'])
#     '''
#     if files_raster is None:
#         df_values = rs.zonal_stats(sp_poly, file_raster, stats=stats)
#         df_values = pd.DataFrame(df_values)

#         return (df_values)
#     else:
#         d_values = dict()
#         for file_raster in files_raster:
#             df_values = rs.zonal_stats(sp_poly, file_raster, stats=stats)
#             df_values = pd.DataFrame(df_values)

#             d_values[file_raster] = df_values

#         return (d_values)

# #%%
# def zonal_stats_poly_single(sp_poly: gpd.GeoDataFrame, file_raster: str=None, files_raster: list|np.ndarray|pd.Series=None, stats='sum'):
#     '''Get raster value summary at polygons.

#     Args:
#         sp_poly (GeoDataFrame): Geodataframe of polygons.
#         file_raster (str, optional): Raster file. Defaults to None.
#         files_raster (list | np.ndarray | pd.Series of str, optional): Vector of raster files. Defaults to None.
#         stats (str): Stat to use. Defaults to 'sum'. Acceptable values are: 'sum', 'std', 'median', 'majority', 'minority', 'unique', 'range', 'nodata', 'percentile'. Percentile statistic can be used by specifying 'percentile_<q>' where <q> can be a floating point number between 0 and 100.

#     Returns:
#         pd.Series | pd.DataFrame: The summary of raster values by specified statistics at each polygon.

#     Notes:
#         - Only one of file_raster or files_raster need to be specified.
#         - If 'file_raster' is used, a series of raster values is returned in same order 'sp_poly'.
#         - If 'files_raster' is used, a dataframe of raster values is returned. The columns indicate the 'sp_poly' in order. The row indicate the 'files_raster' in order.

#     Examples:
#         >>> zonal_stats_poly_single(sp_points, files_raster_tif[0], stats = 'median')
#         >>> zonal_stats_poly_single(sp_points, files_raster=files_raster_tif, stats = 'median').set_axis(sp_points['id'], axis = 1).assign(file = os.path.basename(files_raster_tif)
#     '''
#     if files_raster is None:
#         temp_values = rs.zonal_stats(sp_poly, file_raster, stats=[stats])
#         temp_values = pd.DataFrame(temp_values).iloc[:, 0]

#         return (temp_values)

#     else:
#         df_values = []
#         for file_raster in files_raster:
#             temp_values = rs.zonal_stats(sp_poly, file_raster, stats=[stats])
#             temp_values = pd.DataFrame(temp_values).iloc[:, 0]
#             df_values.append(temp_values.to_list())
#         df_values = pd.DataFrame(df_values)

#         return (df_values)

# #%%
# def zonal_stats_points(sp_points: gpd.GeoDataFrame, file_raster: str=None, files_raster: list|np.ndarray|pd.Series=None) -> pd.Series|pd.DataFrame:
#     '''Get raster values at points.

#     Args:
#         sp_points (GeoDataFrame): Geodataframe of points.
#         file_raster (str, optional): Raster file. Defaults to None.
#         files_raster (list | np.ndarray | pd.Series of str, optional): Vector of raster files. Defaults to None.

#     Returns:
#         pd.Series | pd.DataFrame: The raster values at points.

#     Notes:
#         - Only one of file_raster or files_raster need to be specified.
#         - If 'file_raster' is used, a series of raster values is returned in same order 'sp_points'.
#         - If 'files_raster' is used, a dataframe of raster values is returned. The columns indicate the 'sp_points' in order. The row indicate the 'files_raster' in order.

#     Examples:
#         >>> zonal_stats_points(sp_points, files_raster_tif[0])
#         >>> zonal_stats_points(sp_points, files_raster=files_raster_tif).set_axis(sp_points['id'], axis = 1).assign(file = os.path.basename(files_raster_tif))
#     '''
#     df_xy = sp_points.geometry.get_coordinates()
#     coords = [(x,y) for x, y in zip(df_xy.x, df_xy.y)]

#     if files_raster is None:
#         with rasterio.open(file_raster) as f:
#             temp_values = [val[0] for val in f.sample(coords)]
#         temp_values = pd.Series(temp_values)

#         return (temp_values)
#     else:
#         df_values = []
#         for file_raster in files_raster:
#             with rasterio.open(file_raster) as f:
#                 df_values.append([val[0] for val in f.sample(coords)])
#         df_values = pd.DataFrame(df_values)

#         return (df_values)

#endregion -----------------------------------------------------------------------------------------
