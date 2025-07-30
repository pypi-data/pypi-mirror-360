#region Libraries

#%%
import pandas as pd
import numpy as np

import h5py
import rashdf

import dsplus as ds

pd.options.display.max_columns = None
pd.options.display.max_rows = 8

#endregion -------------------------------------------------------------------------------------------------
#region Functions

#%%
def reset_ras_2d_bridge_profiles(content_geom: pd.Series) -> pd.Series:
    '''Remove profiles from SA2D connections in HEC-RAS geometry.

    Args:
        content_geom (pd.Series): Geometry contents.

    Returns:
        pd.Series: Geometry contents with profiles in SA2D removed.
    '''
    index_conn = content_geom[content_geom.str.startswith('Conn')].index
    index_conn_br_se = content_geom[content_geom.str.startswith('Conn BR: BR SE=')].index
    index_conn_xs_se = content_geom[content_geom.str.startswith('Conn BR: XS SE=')].index
    index_conn_clf = content_geom[content_geom.str.startswith('Connection Centerline Profile=')].index
    index_connection = content_geom[content_geom.str.startswith('Connection=')].index

    content_geom_updated = content_geom.copy()

    for index_current in index_conn_clf:
        index_current_end = index_conn[index_conn > index_current].min() - 1
        content_geom_updated[index_current:index_current_end + 1] = 'XXXXX'

    for index_current in index_conn_br_se:
        index_current_end = index_conn[index_conn > index_current].min() - 1
        content_geom_updated[index_current:index_current_end + 1] = 'XXXXX'

    for index_current in index_conn_xs_se:
        index_current_end = index_conn[index_conn > index_current].min() - 1
        content_geom_updated[index_current:index_current_end + 1] = 'XXXXX'

    content_geom_updated = content_geom_updated[content_geom_updated != 'XXXXX']

    return content_geom_updated


#endregion -----------------------------------------------------------------------------------------
