#region Libraries

#%%
import pandas as pd
import numpy as np

from pydsstools.heclib.dss import HecDss

import dsplus as ds

pd.options.display.max_columns = None
pd.options.display.max_rows = 8

#endregion -------------------------------------------------------------------------------------------------
#region Functions: DSS

#%%
def dss_read_catalog(file_dss: str) -> pd.Series:
    '''Read dss path list.

    Args:
        file_dss (str): Dss file name.

    Returns:
        Series: Series of all pathnames.
    '''
    with HecDss.Open(file_dss) as f:
        list_path = f.getPathnameList("/*/*/*/*/*/*/",sort=1)
    
    list_path = pd.Series(list_path)

    return (list_path)

#%%
def dss_split_pathnames(v_pathnames: str|list|np.ndarray|pd.Series, keep_pathname = True) -> pd.DataFrame:
    '''Split pathname into individual paths.

    Args:
        v_pathnames (str | list | array | Series): Vector of pathnames.
        keep_pathname (bool): Whether original pathnames should be kept as a column. Defaults to True.

    Returns:
        DataFrame: Dataframe of paths. Column names go from 'A' to 'F'.
    '''
    v_pathnames = ds.pd_to_series(v_pathnames)

    df = v_pathnames.str.split('/', expand=True)\
        .iloc[:, 1:7]\
        .set_axis(['A','B','C','D','E','F'], axis=1)\
        
    if keep_pathname:
        df = df\
            .assign(pathname = v_pathnames)\
            .pipe(ds.pd_select, '*, pathname')

    return (df)

#%%
def dss_read_ts(file_dss, v_pathnames: str|list|np.ndarray|pd.Series, keep_pathname: bool=None, remove_time_part: bool=True, clean_missing: bool = True, threshold_missing = 1e10) -> pd.DataFrame:
    '''Read dss timeseries for one or multiple pathnames.

    Args:
        file_dss (_type_): Dss filename.
        v_pathnames (str | list | array | Series): Pathname or vector of pathnames.
        keep_pathname (bool): Whether pathnames should be kept as a column. Defaults to None. None means that the pathname will only be kept when 'v_pathname' consists of multiple pathnames.
        remove_time_part (bool): Remove the part in path with time so that full timeseries is read.
        clean_missing (bool): Whether missing values should be converted to np.nan.
        threshold_missing (float): Threshold to identify missing values. Anything outside of [1/threshold_missing, threshold_missing] is identified as missing.

    Returns:
        DataFrame: Dataframe with timeseries data for each pathname.

    Examples:
        >>> dss_read_ts(file_dss, v_pathnames.iloc[0])
        >>> dss_read_ts(file_dss, v_pathnames.iloc[0], keep_pathname=True)
        >>> dss_read_ts(file_dss, v_pathnames.iloc[0:3])
    '''
    v_pathnames = ds.pd_to_series(v_pathnames)

    df_ts = pd.DataFrame()
    for pathname in v_pathnames:
        if remove_time_part:
            parts = pathname.split('/')
            parts[4] = ''
            pathname = '/'.join(parts)
        with HecDss.Open(file_dss) as f:
            ts = f.read_ts(pathname, trim_missing=True)
        temp_df_ts = pd.DataFrame({'dttm': pd.to_datetime(ts.pytimes), 
                                   'value': ts.values})

        if ((keep_pathname is None) & (len(v_pathnames) > 1)) | ((keep_pathname is not None) & (keep_pathname==True)):
            temp_df_ts = temp_df_ts.assign(pathname = pathname).pipe(ds.pd_select, 'pathname, *')

        df_ts = df_ts.pipe(ds.pd_concat_rows, temp_df_ts)
    
    if clean_missing:
        df_ts = df_ts\
            .assign(value = lambda x: np.where((x['value'] > threshold_missing) | (x['value'] < 1/threshold_missing), np.nan, x['value']))

    return (df_ts)

#endregion -------------------------------------------------------------------------------------------------
#region Legacy

#%%
read_dss_catalog = dss_read_catalog
read_dss_ts = dss_read_ts
split_dss_pathnames = dss_split_pathnames

#endregion -----------------------------------------------------------------------------------------
