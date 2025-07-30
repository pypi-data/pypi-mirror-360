#region Libraries

#%%
import pandas as pd
import numpy as np

import h5py

import dsplus as ds

pd.options.display.max_columns = None
pd.options.display.max_rows = 8

#endregion -------------------------------------------------------------------------------------------------
#region Functions: HDF

#%%
def hdf_read_df(file_hdf: str, pathname: str, return_df = True, decode_binary_str = True, col_names: list|np.ndarray|pd.Series = None) -> pd.DataFrame | np.ndarray:
    '''Read table from HEC hdf file.

    Args:
        file_hdf (str): Filename of HEC hdf file.
        pathname (str): Pathname of dataset within hdf file.
        return_df (bool): Whether to return dataframe or numpy array. Defaults to True.
        decode_binary_str (bool): Whether any object column should be decoded from binary. Defaults to True.
        col_names (list | array | Series): Column names for output. Defaults to None (use column names for source).

    Returns:
        DataFrame | np.ndarray: Dataframe or numpy array.

    Examples:
        >>> hdf_read_df(file_hdf, 'Geometry/2D Flow Areas/Attributes')
        >>> hdf_read_df(file_hdf, 'Modifications/Channels/Profile Values', col_names=['stn', 'elev'])
    '''
    with h5py.File(file_hdf, 'r') as f:
        hdf_file = f[pathname]
        df = hdf_file[:]

    df = pd.DataFrame(df)

    if return_df:
        if decode_binary_str:
            for col, dtype in df.dtypes.items():
                if np.issubdtype(dtype, np.bytes_) | (dtype == object):
                    df[col] = [x.decode('ascii') for x in df[col]]
            # df = df.applymap(lambda x: x.decode('ascii') if np.issubdtype(x, np.bytes_) else x)
            # df = df.applymap(lambda x: x.decode() if isinstance(x, object) else x)
            # temp_df = df.select_dtypes('object')
            # for col in temp_df:
            #     df[col] = [x.decode('ascii') for x in temp_df[col]]
            # for col, dtype in df.dtypes.items():
            #     if isinstance(dtype, object):
            #         print ('yes')
            #         df[col] = [x.decode('ascii') for x in temp_df[col]]

        if col_names is not None:
            df = df\
                .pipe(ds.pd_set_colnames, col_names)

    return (df)  

#%%
def hdf_read_groups(file_hdf: str, return_series = True) -> list|pd.Series:
    '''Read pathnames of all groups in HEC hdf file.

    Args:
        file_hdf (str): Filename of HEC hdf file.
        return_series (bool, optional): Whether to return series or list. Defaults to True.

    Returns:
        list|Series: List or series of all group paths.
    '''
    temp_list = []
    def func(name, obj):
        if isinstance(obj, h5py.Group):
            temp_list.append(name)
    with h5py.File(file_hdf, 'r') as f:
        f.visititems(func)

    if return_series:
        return (pd.Series(temp_list))
    else:
        return (temp_list)
  
#%%
def hdf_read_datasets(file_hdf: str, return_series = True) -> list|pd.Series:
    '''Read pathnames of all datasets in HEC hdf file.

    Args:
        file_hdf (str): Filename of HEC hdf file.
        return_series (bool, optional): Whether to return series or list. Defaults to True.

    Returns:
        list|Series: List or series of all dataset paths.
    '''
    temp_list = []
    def func(name, obj):
        if isinstance(obj, h5py.Dataset):
            temp_list.append(name)
    with h5py.File(file_hdf, 'r') as f:
        f.visititems(func)

    if return_series:
        return (pd.Series(temp_list))
    else:
        return (temp_list)

#%%
def hdf_read_attributes(file_hdf: str, pathname: str, decode_binary_str = True) -> dict:
    '''Read attributes of dataset or group in HEC hdf file.

    Args:
        file_hdf (str): Filename of HEC hdf file.
        pathname (str): Pathname of dataset or group withing hdf file.
        decode_binary_str (bool, optional): Whether any object column should be decoded from binary. Defaults to True.

    Returns:
        dict: Dictionary whose keys are attribute names and values are attribute values.
    '''
    dict_attr = {}
    with h5py.File(file_hdf, 'r') as f:
        hdf_file = f[pathname]

        for key, value in hdf_file.attrs.items():
            if decode_binary_str:
                if isinstance(value, np.ndarray) and np.issubdtype(value.dtype, np.bytes_):
                    value = [x.decode('ascii') for x in value]
                elif np.issubdtype(value.dtype, np.bytes_):
                    value = value.decode('ascii')
            dict_attr[key] = value

    return (dict_attr)

#%%
def hdf_read_info_value(file_hdf: str=None, pathname_info: str=None, pathname_values: str=None, df_info: pd.DataFrame=None, df_values: pd.DataFrame=None, col_names_values: str|list|np.ndarray|pd.Series=None, df_attributes: pd.DataFrame=None, info_columns_to_keep: str|list|np.ndarray|pd.Series=None) -> pd.DataFrame:
    '''Read info-value pair from HEC Hdf file.

    Args:
        file_hdf (str, optional): Filename of HEC hdf file. Defaults to None.
        pathname_info (str, optional): Pathname of info dataset within hdf file. Defaults to None.
        pathname_values (str, optional): Pathname of values dataset within hdf file. Defaults to None.
        df_info (DataFrame, optional): Info dataframe. Defaults to None. First column should be starting index, and second column should be row count. Index should be reset beforehand (without keeping the without column).
        df_values (DataFrame, optional): Values dataframe. Defaults to None.
        col_names_values (str | list | array | Series): Column names for 'df_values'. Defaults to None.
        info_columns_to_keep (str | list | array | Series): Columns from 'df_info' to keep. Defaults to None.
        df_attributes (DataFrame): Attributes dataframe to join to 'df_values' with 'index' column. If 'index' column is not present, dataframe index is used instead. Defaults to None.

    Returns:
        DataFrame: Values dataframe with a new columns: 'index_info', which gives the corresponding index for each value.

    Notes:
        - Input can be either ('file_hdf', 'pathname_info', 'pathname_values') or ('df_info', 'df_values').
        - 'col_names_values' is usually needed if 'df_values' is not provided. Otherwise, column names in 'df_values' are overwritten.
        - 'df_attributes' is fully optional.
        - In cases where info and parts table are present, simply use info table and ignore parts table for this function to work.

    Examples
        >>> hdf_read_info_value(file_hdf, 
                                'Geometry/Cross Sections/Polyline Info', 
                                'Geometry/Cross Sections/Polyline Points')
        >>> hdf_read_info_value(file_hdf, 
                                'Geometry/Cross Sections/Polyline Info', 
                                'Geometry/Cross Sections/Polyline Points',
                                col_names_values=['x', 'y'])
        >>> hdf_read_info_value(file_hdf, 
                                'Geometry/Cross Sections/Polyline Info', 
                                'Geometry/Cross Sections/Polyline Points',
                                col_names_values=['x', 'y'],
                                df_attributes=df_attributes)
    '''
    if file_hdf is not None:
        df_info = hdf_read_df(file_hdf, pathname_info)
        df_values = hdf_read_df(file_hdf, pathname_values)

    df_info = \
    (df_info
        .rename(columns={df_info.columns[1]: 'count'})
        # .pipe(ds.pd_set_colnames, ['index_start', 'count'])
        .loc[lambda _: _['count'] > 0]
    )

    df_index_start = \
    (df_info
        .iloc[:,[0]]
        .reset_index()
        .set_axis(['index_info', 'index_start'], axis=1)
        .assign(index_start = lambda x: x['index_start'].pipe(np.int64))
    )
    if info_columns_to_keep is not None:
        info_columns_to_keep = ds.pd_to_series(info_columns_to_keep)
        df_index_start = df_index_start.pipe(ds.pd_concat_cols, df_info[info_columns_to_keep])
    df_values = df_values\
        .reset_index()\
        .pipe(ds.pd_merge_asof, df_index_start, left_on = 'index', right_on = 'index_start', direction='backward')\
        .pipe(ds.pd_select, 'index_info, *, -index, -index_start')

    if col_names_values is not None:
        df_values = df_values\
            .pipe(ds.pd_set_colnames, ['index_info', *col_names_values])
            # .set_axis(['index_info', *col_names_values], axis=1)\
    
    if df_attributes is not None:
        if 'index' not in df_attributes.columns:
            df_attributes = df_attributes.reset_index()
        col_attributes = df_attributes.columns.to_list()
        df_values = df_values\
            .merge(df_attributes, left_on='index_info', right_on='index', how='left')\
            .pipe(ds.pd_select_simple, ['index_info', *col_attributes])\
            .drop('index', axis=1)
        # df_values = df_values\
        #     .pipe(pd_merge_asof, df_attributes, left_on='index_info', right_on='index', direction = 'backward')\
        #     .pipe(pd_select_simple, ['index_info', *col_attributes])\
        #     .drop('index', axis=1)
        
    # if info_columns_to_keep is not None:
    #     df_info
        
    #     df_values = pd_merge_asof(df_values.reset_index(),
    #                   temp_df_profile_info[['index_start', 'type']].assign(index_start = lambda x: np.int64(x['index_start'])),
    #                   left_on='index',
    #                   right_on='index_start',
    #                   direction='backward')\
    #         .drop(['index', 'index_start'], axis=1)
    
    return (df_values)

#%%
def hdf_update_df(file_hdf: str, pathname: str, df: pd.DataFrame = None, v: np.ndarray = None, check_col: bool = True) -> None:
    '''Update HDF Dataset with DataFrame or numpy array.

    Args:
        file_hdf (str): Filename of HEC hdf file to update.
        pathname (str): Pathname of dataset within hdf file to update.
        df (pd.DataFrame, optional): DataFrame to update HDF dataset with. Defaults to None.
        v (np.ndarray, optional): Numpy array to update HDF dataset with. Defaults to None.
        check_col (bool, optional): Whether to check if number of columns match. Defaults to True.

    Notes:
        - One of 'df' or 'values' should be provided.
        - Make sure the number of columns match the existing dataset. 
    '''
    with h5py.File(file_hdf, 'r+') as hdf_file:
        hdf_dataset = hdf_file[pathname]
        if df is not None:
            # for col in df.columns:
            #     if df[col].dtype == object:
            #         df[col] = df[col].str.encode('ascii')
            if len(hdf_dataset.shape) == 2:
                if check_col:
                    if hdf_dataset.shape[1] != df.shape[1]:
                        raise ValueError(f'Number of columns in dataframe ({df.shape[1]}) does not match number of columns in HDF dataset ({hdf_dataset.shape[1]}).')
                hdf_dataset.shape = df.shape
                hdf_dataset[:] = df.values.copy()
            else:
                hdf_dataset.shape = (df.shape[0],)
                hdf_dataset[:] = [tuple(row) for row in df.to_numpy()]
        else:
            if check_col:
                if hdf_dataset.shape[1] != v.shape[1]:
                    raise ValueError(f'Number of columns in dataframe ({df.shape[1]}) does not match number of columns in HDF dataset ({hdf_dataset.shape[1]}).')
            hdf_dataset.shape = v.shape
            hdf_dataset[:] = v.copy()

#%%
def hdf_generate_info_value(df: pd.DataFrame, col_index: str = 'index_info') -> dict:
    '''Get info table from a dataframe.

    Args:
        df (pd.DataFrame): Dataframe.
        col_index (str, optional): Column name for index. Defaults to 'index_info'.

    Returns:
        dict: Dictionary with info ('df_info') and value ('df_value') dataframes.
    '''
    df_info = \
    (df
        .pipe(ds.pd_add_row_number)
        .groupby(col_index)
        .agg(n=(col_index, 'size'),
             sn=('sn', 'first'))
        .reset_index()
        .sort_values('sn')
        .drop(columns='sn')
        .assign(n_cum = lambda _: _.n.cumsum().shift(1, fill_value=0))
        [['n_cum', 'n']]
        .pipe(ds.pd_set_colnames, [0, 1])
    )
    df_value = df.drop(columns=col_index)
    return dict(df_info = df_info, df_value = df_value)

#%%
def hdf_generate_info_parts_value(df: pd.DataFrame, col_index: str = 'index_info') -> dict:
    '''Get info and parts tables from a dataframe.

    Args:
        df (pd.DataFrame): Dataframe.
        col_index (str, optional): Column name for index. Defaults to 'index_info'.

    Returns:
        dict: Dictionary with info ('df_info'), parts ('df_parts'), and value ('df_value') dataframes.
    '''
    df_info = \
    (df
        .pipe(ds.pd_add_row_number)
        .groupby(col_index)
        .agg(n=(col_index, 'size'),
             sn=('sn', 'first'))
        .reset_index()
        .sort_values('sn')
        .drop(columns='sn')
        .assign(n_cum = lambda _: _.n.cumsum().shift(1, fill_value=0))
        [['n_cum', 'n']]
        .pipe(ds.pd_add_row_number, place_first=False)
        .assign(x = 1)
        .pipe(ds.pd_set_colnames, [0, 1, 2, 3])
    )
    df_parts = \
    (df_info
        .iloc[:, [1]]
        .assign(x = 0)
        .pipe(ds.pd_select, 'x,*')
        .pipe(ds.pd_set_colnames, [0, 1])
    )
    df_value = df.drop(columns=col_index)
    return dict(df_info = df_info, df_parts = df_parts, df_value = df_value)

#%%
def hdf_compare(file_hdf_1: str, file_hdf_2: str) -> dict:
    '''Compare two hdf files.

    Args:
        file_hdf_1 (str): Filename of first hdf file.
        file_hdf_2 (str): Filename of second hdf file.

    Returns:
        dict: Dictionary with three keys: 'v_pathnames_1_only' (pathnames only in first hdf file), 'v_pathnames_2_only' (pathnames only in second hdf file), and 'v_pathnames_diff' (pathnames in both where the tables are different).
    '''
    v_datasets_1 = hdf_read_datasets(file_hdf_1)
    v_datasets_2 = hdf_read_datasets(file_hdf_2)

    v_pathnames_1_only = ds.set_diff(v_datasets_1, v_datasets_2)
    v_pathnames_2_only = ds.set_diff(v_datasets_2, v_datasets_1)

    v_datasets = ds.set_intersection(v_datasets_1, v_datasets_2)

    v_pathnames_diff = []
    _dataset = v_datasets[0]
    for _dataset in v_datasets:
        _df_1 = hdf_read_df(file_hdf_1, _dataset)
        _df_2 = hdf_read_df(file_hdf_2, _dataset)

        _test = _df_1.equals(_df_2)

        if not _test:
            v_pathnames_diff.append(_dataset)

    d_hdf_diff = dict(
        v_pathnames_1_only = v_pathnames_1_only,
        v_pathnames_2_only = v_pathnames_2_only,
        v_pathnames_diff = v_pathnames_diff,
    )

    return d_hdf_diff

#endregion -------------------------------------------------------------------------------------------------
#region Functions: HEC Datetime

#%%
def pd_to_datetime_hec(dttm_str: str|list|np.ndarray|pd.Series) -> pd.Timestamp:
    '''Convert datetime string from HEC programs to pandas datetime object. This mainly deals with 24 hour time format used by HEC.

    Args:
        dttm_str (str | list | array | Series): Datetime string or vector of datatime string.

    Returns:
        Timestamp: Pandas datetime object (if 'dttm_str' is str) or vector of pandas datetime objects (if 'dttm_str' is not str).

    Examples:
        >>> temp_dttm = '03Jan2019, 24:00:00'
        >>> pd.to_datetime(temp_dttm) # Error
        >>> pd_to_datetime_hec(temp_dttm) # Timestamp('2019-01-04 00:00:00')
        >>> pd_to_datetime_hec(['03Jan2019, 24:00:00', '04Jan2019, 1:00:00'])
        >>> pd_to_datetime_hec('03Jan2019 24:00')
        >>> pd_to_datetime_hec('03Jan2019 2400')
    '''
    # single date string
    if isinstance(dttm_str, str):
        # separate out date and time
        date_string, time_string_raw = dttm_str.split(' ') 
        # convert time "XXXX" to "XX:XX"
        if ':' not in time_string_raw:
            pairs = [time_string_raw[i:i+2] for i in range(0, len(time_string_raw), 2)]
            time_string_raw = ':'.join(pairs)
        # convert time "XX:XX" to "XX:XX:XX" (dd:mm:ss)
        time_string = np.select(time_string_raw.count(':') == np.array([0,1,2]), 
                                [time_string_raw + ':00:00', 
                                 time_string_raw + ':00', 
                                 time_string_raw],
                                 time_string_raw).item()
        # convert time to timedelta and add to date
        dttm = pd.to_datetime(date_string) + pd.to_timedelta(time_string)
    # vector of date strings
    else:
        dttm = pd.Series()
        for current_dttm_str in dttm_str:
            # recursive call
            current_dttm = pd_to_datetime_hec(current_dttm_str)

            dttm = ds.pd_concat_series(dttm, current_dttm)

        dttm = dttm.reset_index(drop=True)
    return (dttm)

#endregion -------------------------------------------------------------------------------------------------
#region Functions: HEC Text Wrangling

#%%
def get_hec_text_after_header(content_hec: pd.Series, 
                              text_header: str, 
                              ignore_case = True,
                              allow_preceeding_space = True,
                              strip = True, 
                              split_by: str = None, 
                              first_after_split = False, 
                              numeric_convert = False, 
                              return_dataframe = True, 
                              return_index = True, 
                              col_names: list = None, 
                              col_name_index: str = None) -> pd.Series|pd.DataFrame:
    '''Get text after a given header text from series of string.

    Args:
        content_hec (Series): Series of string. Typically a result of os_read_lines().
        text_header (str): Header text to match.
        ignore_case (bool): If case of the header text should be ignored when matching. Defaults to True
        allow_preceeding_space (bool): Allow whitespace before. Defaults to True.
        strip (bool, optional): Should the text be stripped (leading and trailing spaces removed). Defaults to True.
        split_by (str, optional): Separator to Split each text by. Defaults to None. None means string is not split.
        first_after_split (bool, optional): Only keep each first value after splitting. Defaults to False.
        numeric_convert (bool, optional): Convert each value to number. Defaults to False.
        return_dataframe (bool, optional): Return dataframe. Defaults to True. False means return series.
        return_index (bool, optional): Return index locations. Defaults to True.
        col_names (list, optional): Column names for data frame (except the index column). Defaults to None. Set to None to get default names.
        col_name_index (str, optional): Column name for index column. Defaults to None.

    Returns:
        Series or DataFrame: Series or Dataframe of text after header.

    Notes:
        If split_by is True and first_after_split is False, a dataframe is returned and return_dataframe is ignored.

    Examples:
        >>> content_hms_basin = os_read_lines(file_hms_basin)
        >>> get_hec_text_after_header(content_hms_basin, 'Subbasin: ', col_names=['name_subbasin'], col_name_index='index_subbasin')
        >>> content_ras_geom = os_read_lines(file_hec)
        >>> get_hec_text_after_header(content_ras_geom, 'Connection=', split_by=',', first_after_split=False, col_names=['name_sa2d', 'x', 'y'])
        >>> get_hec_text_after_header(content_ras_geom, 'Conn BR: XS SE=1,', split_by=',', first_after_split=False, col_names=['n_row'])
    '''
    regex_text_header = fr'^\s*{text_header}.*' if allow_preceeding_space else fr'^{text_header}.*'

    text_result = content_hec\
        .loc[lambda x: x.str.contains(regex_text_header, case=not ignore_case)]\
        .str.replace(text_header, '', case=not ignore_case)
    
    if len(text_result) == 0:
        if return_dataframe:
            df = pd.DataFrame()
            if return_index:
                df = df.assign(index = None)
                if col_name_index is not None:
                    df = df.rename(columns={'index': col_name_index})
                if col_names is not None:
                    for col_name in col_names:
                        df = df.assign(**{col_name: None})
            return (df)
        else:
            return (pd.Series())

    if split_by is not None:
        text_result = text_result.str.split(split_by, expand=True)

        if strip:
            text_result = text_result.apply(lambda x: x.str.strip())

        if first_after_split:
            if return_dataframe:
                text_result = text_result.iloc[:, 0:1]
            else:
                text_result = text_result.iloc[:, 0]
    else:
        if strip:
            text_result = text_result.str.strip()

        if return_dataframe:
            text_result = text_result.to_frame()

    if (return_dataframe) | (split_by is not None):
        if (col_names is not None) & (text_result.shape[0] > 0):
            # text_result = text_result.set_axis(col_names, axis = 1)
            text_result = text_result.pipe(ds.pd_set_colnames, col_names)

        text_result = text_result.reset_index(drop = not return_index)
        if return_index:
            if col_name_index is not None:
                text_result = text_result.rename(columns={'index': col_name_index})

        if numeric_convert:
            text_result = text_result.apply(lambda x: pd.to_numeric(x, errors='coerce'))

    elif numeric_convert:
        text_result = pd.to_numeric(text_result, errors='coerce')

    return(text_result)

#%%
def hecras_text_to_df(content_hec: pd.Series, 
                      index_start: int = None, 
                      n_row: int = None, 
                      length: int = 8, 
                      n_col: int = 2, 
                      by_row: bool = True, 
                      add_attribute: bool = False, 
                      col_names=['chainage', 'elev']):
    '''Convert HECRAS text to data frame.

    Args:
        content_hec (Series): Series of string. Typically a result of os_read_lines().
        index_start (int, optional): Line index where the text starts. Only needed if 'content_hec' isn't just the filtered text. Defaults to None (first line).
        n_row (int, optional): Number of rows in the resulting dataframe. Used to determine the line where the text ends. Only needed if 'content_hec' isn't just the filtered text. Defaults to None (calculate based on all text in 'content_hec').
        length (int, optional): Character length of each value. Defaults to 8.
        n_col (int, optional): Number of columns in the resulting dataframe. Defaults to 2.
        by_row (bool, optional): True means values are left to right row by row; False means values are top to bottom column by column. Defaults to True.
        add_attribute (bool, optional): Whether to add attributes to the output, including starting and ending index and number of lines. Defaults to False.
        col_names (list, optional): Names for the columns. Defaults to ['chainage', 'elev'].

    Returns:
        DataFrame: Dataframe of values.

    Examples:
        >>> content_ras_geom = os_read_lines(file_hec)
        >>> df_conn_br_1 = get_hec_text_after_header(content_ras_geom, 'Conn BR: XS SE=1,', split_by=',', first_after_split=False, col_names=['n_row'])
        >>> hecras_text_to_df(content_ras_geom, index_start=df_conn_br_1['index'].iloc[0], n_row=df_conn_br_1['n_row'].iloc[0])
    '''
    
    if index_start is not None:
        temp_length = len(content_hec[index_start])
        temp_count_per_length = temp_length / (length * n_col)
        temp_lines = int(np.ceil(n_row / temp_count_per_length))
        index_end = index_start + temp_lines - 1
        content_hec = content_hec[index_start:index_end + 1]
    
    text_combined = ''.join(content_hec)
    values = [text_combined[i:i+length].strip() for i in range(0, len(text_combined), length)]
    values = list(map(float, values))
    
    if by_row:
        df = pd.DataFrame(np.array(values).reshape(-1, n_col), columns=col_names)
    else:
        df = pd.DataFrame(np.array(values).reshape(n_col, -1).T, columns=col_names)
    
    if index_start is not None and add_attribute:
        df.attrs['index_start'] = index_start
        df.attrs['index_end'] = index_end
        df.attrs['n_lines'] = index_end - index_start + 1
    
    return df

#%%
def df_to_hecras_text(df: pd.DataFrame, 
                      length: int = 8, 
                      count_per_line: int = 10, 
                      len_per_line: int = None, 
                      by_row: bool = True) -> pd.Series:
    '''Convert dataframe to HECRAS text.

    Args:
        df (pd.DataFrame): Dataframe.
        length (int, optional): Character width of each value. Defaults to 8.
        count_per_line (int, optional): Number of values per line. Defaults to 10.
        len_per_line (int, optional): Character width of each line. Defaults to None.
        by_row (bool, optional): True means values are left to right row by row; False means values are top to bottom column by column. Defaults to True.

    Notes:
        - len_per_line, if inputted, takes precedence over count_per_line.

    Returns:
        pd.Series: Series with text formatted for HEC-RAS.
    '''
    m = df.to_numpy()
    
    if by_row:
        m = m.T
    # v = m.flatten()
    # v_ = m[2]

    text_hecras_lines = []
    for v_ in m:
        v = pd.Series(v_).astype(str).str.rjust(length).str[:length]
        # ['' if isinstance(x, float) and np.isnan(x) else x for x in v]
        # [x if isinstance(x, str) else '' for x in v]
        v = ['        ' if x == '     nan' else x for x in v]
        text_hecras = ''.join([x for x in v])
    
        if len_per_line is not None:
            count_per_line = round(len_per_line / length)
        else:
            len_per_line = count_per_line * length
        
        index_start = np.arange(0, len(text_hecras), len_per_line)
        index_end = index_start + len_per_line
        
        temp_text_hecras_lines = [text_hecras[start:end] for start, end in zip(index_start, index_end)]

        text_hecras_lines += temp_text_hecras_lines
    
    return text_hecras_lines

#%%
def hec_insert_text(content: pd.Series, 
                    text_insert: str|list|np.ndarray|pd.Series, 
                    index_start: int, 
                    index_end: int = None,
                    n_lines_remove: int = None,
                    reset_index: bool = True) -> pd.Series:
    '''Insert text or vector of text into existing series.

    Args:
        content (pd.Series): Existing series to insert text into.
        text_insert (str | list | np.ndarray | pd.Series): Text or vector of text to insert.
        index_start (int): Index of 'content' where 'text_insert' has to be inserted.
        index_end (int, optional): Index of 'content' from which to resume after inserting 'text_insert'. If set to None, this is calculated based on 'n_lines_remove'. Defaults to None.
        n_lines_remove (int, optional): Numbher of lines to remove. This is used to calculate 'index_end' if 'index_end' is None. If 'index_end' is not None, this is used. If this is None, this is replaced by length of 'text_insert'. Defaults to None.
        reset_index (bool, optional): Whether to keep the original index. If False, the index for 'text_insert' is set to repeating 'a'. Defaults to True.

    Returns:
        pd.Series: Series with inserted text.

    Notes:
        - If 'index_end' is provided, 'n_lines_remove' is discarded.
        - If n_lines_remove is:
            - None, number of lines removed will be equal to length of 'text_insert';
            - zero, no lines will be removed;
            - any number, given number of lines will be removed.
        - If reset_index is False and:
            - length of text_insert is equal to 'n_lines_remove', index remains unchanged (carried over from 'content' as is);
            - length of text_insert is less than to 'n_lines_remove', additional index after length of text_insert is removed from the removed lines;
            - length of text_insert is less than to 'n_lines_remove', the last index from the removed lines is repeated.

    Examples:
        >>> hec_insert_text(content_geom, 'Connection=123,,', index_start=1000)
        >>> hec_insert_text(content_geom, 'Connection=123,,', index_start=1000, reset_index=False)
        >>> hec_insert_text(content_geom, ['Connection=123,,', 'a', 'b'], index_start=1000, index_end=1005)
        >>> hec_insert_text(content_geom, ['Connection=123,,', 'a', 'b'], index_start=1000, n_lines_remove=0)
    '''
    v_text_insert = ds.pd_to_series(text_insert)

    if index_end is None:
        if n_lines_remove is None:
            n_lines_remove = len(v_text_insert)
        index_end = index_start + n_lines_remove
        
    if reset_index:
        v_text_insert.index = np.repeat('a', len(v_text_insert))
    else:
        index_replace = content.loc[index_start:index_end-1].index.to_numpy()
        if index_end is not None:
            n_lines_remove = index_start - index_end
        if len(text_insert) < n_lines_remove:
            index_replace = index_replace[:len(text_insert)]
        elif len(text_insert) > n_lines_remove:
            index_replace = np.append(index_replace, np.repeat(index_replace[-1], len(text_insert) - n_lines_remove))
        v_text_insert.index = index_replace

    content_updated = \
    pd.concat([
        content.loc[:index_start-1],
        v_text_insert,
        content.loc[index_end:]
    ])

    return content_updated

#endregion -------------------------------------------------------------------------------------------------
#region Legacy

#%%
read_hdf_df = hdf_read_df
read_hdf_groups = hdf_read_groups
read_hdf_datasets = hdf_read_datasets
read_hdf_attributes = hdf_read_attributes
read_hdf_info_value = hdf_read_info_value

#endregion -----------------------------------------------------------------------------------------
