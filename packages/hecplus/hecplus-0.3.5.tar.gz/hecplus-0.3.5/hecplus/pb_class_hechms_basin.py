#region Libraries

#%%
import copy

import pandas as pd
import numpy as np

from .pb_functions_hec import *
from .pb_functions_hechms import *

import dsplus as ds

# pd.set_option('display.max_columns', None)
pd.options.display.max_columns = None
pd.options.display.max_rows = 8
# pd.options.display.max_colwidth=None

#endregion -------------------------------------------------------------------------------------------------
#region Class

#%%
class HecHms_Basin:
    name = None
    name_basin = None

    file_hms_basin = None
    content_hms_basin = None

    df_subbasin_info = None
    df_reach_info = None
    df_junction_info = None
    df_reservoir_info = None
    df_element_info = None

    df_observed = None

    df_subbasin_params = None
    df_reach_params = None
    df_reservoir_params = None

    def __init__(self, name = '') -> None:
        self.name = name

    def read_from_file(self, file_hms_basin: str, read_element_info = True):
        '''Read HEC-HMS basin file contents. Updates 'file_hms_basin' and 'content_hms_basin'.

        Args:
            file_hms_basin (str): Basin filename (*.basin).
            read_element_info (bool, optional): If basin elements should be read. Defaults to True.
        '''
        content_hms_basin = ds.os_read_lines(file_hms_basin)

        name_basin = get_hec_text_after_header(content_hms_basin, 'Basin: ', return_dataframe=False).iloc[0]

        self.name_basin = name_basin
        self.file_hms_basin = file_hms_basin
        self.content_hms_basin = content_hms_basin

        if read_element_info:
            self.read_element_info()
        
    def read_element_info(self):
        '''Read basic info regarding each element, including downstream nodes. Updates 'df_subbasin_info', 'df_reach_info', 'df_junction_info', and 'df_element_info'.
        '''
        content_hms_basin = self.content_hms_basin

        df_subbasin = get_hec_text_after_header(content_hms_basin, 'Subbasin: ', col_names=['name'], col_name_index='index')
        df_reach = get_hec_text_after_header(content_hms_basin, 'Reach: ', col_names=['name'], col_name_index='index')
        df_junction = get_hec_text_after_header(content_hms_basin, 'Junction: ', col_names=['name'], col_name_index='index')
        df_reservoir = get_hec_text_after_header(content_hms_basin, 'Reservoir: ', col_names=['name'], col_name_index='index')
        df_sink = get_hec_text_after_header(content_hms_basin, 'Sink: ', col_names=['name'], col_name_index='index')
        df_ds = get_hec_text_after_header(content_hms_basin, 'Downstream: ', col_names=['name_ds'], col_name_index='index_ds')
        df_end = pd.DataFrame({'index_end': content_hms_basin.reset_index().index.to_series().loc[content_hms_basin.str.contains('End:')]})
        # df_x = get_hec_text_after_header(content_hms_basin, 'Canvas X: ', col_names=['x'], col_name_index='index_x')
        # df_y = get_hec_text_after_header(content_hms_basin, 'Canvas Y: ', col_names=['y'], col_name_index='index_y')
        # df_area = get_hec_text_after_header(content_hms_basin, 'Area: ', col_names=['area'], col_name_index='index_area')
        
        df_subbasin_info = df_subbasin\
            .pipe(pd.merge_asof, df_ds, left_on = 'index', right_on = 'index_ds', direction = 'forward')\
            .pipe(pd.merge_asof, df_end, left_on = 'index', right_on = 'index_end', direction = 'forward')\
            .sort_values(by = ['name'])\
            .drop(columns='index_ds', errors='ignore')
            # .pipe(pd.merge_asof, df_area, left_on = 'index', right_on = 'index_area', direction = 'forward')\
        
        df_reach_info = df_reach\
            .pipe(pd.merge_asof, df_ds, left_on = 'index', right_on = 'index_ds', direction = 'forward')\
            .pipe(pd.merge_asof, df_end, left_on = 'index', right_on = 'index_end', direction = 'forward')\
            .sort_values(by = ['name'])\
            .drop(columns='index_ds', errors='ignore')
        
        df_junction_only_info = df_junction\
            .pipe(pd.merge_asof, df_ds, left_on = 'index', right_on = 'index_ds', direction = 'forward')\
            .pipe(pd.merge_asof, df_end, left_on = 'index', right_on = 'index_end', direction = 'forward')\
            .sort_values(by = ['name'])\
            .drop(columns='index_ds', errors='ignore')
            # .pipe(pd.merge_asof, df_x, left_on = 'index', right_on = 'index_x', direction = 'forward')\
            # .pipe(pd.merge_asof, df_y, left_on = 'index', right_on = 'index_y', direction = 'forward')\
        
        df_reservoir_info = df_reservoir\
            .pipe(pd.merge_asof, df_ds, left_on = 'index', right_on = 'index_ds', direction = 'forward')\
            .pipe(pd.merge_asof, df_end, left_on = 'index', right_on = 'index_end', direction = 'forward')\
            .sort_values(by = ['name'])\
            .drop(columns='index_ds', errors='ignore')
            # .pipe(pd.merge_asof, df_x, left_on = 'index', right_on = 'index_x', direction = 'forward')\
            # .pipe(pd.merge_asof, df_y, left_on = 'index', right_on = 'index_y', direction = 'forward')\
        
        df_sink_info = df_sink\
            .pipe(ds.pd_merge_asof, df_ds, left_on = 'index', right_on = 'index_ds', direction = 'forward')\
            .pipe(ds.pd_merge_asof, df_end, left_on = 'index', right_on = 'index_end', direction = 'forward')\
            .sort_values(by = ['name'])\
            .drop(columns='index_ds', errors='ignore')
            # .pipe(pd.merge_asof, df_x, left_on = 'index', right_on = 'index_x', direction = 'forward')\
            # .pipe(pd.merge_asof, df_y, left_on = 'index', right_on = 'index_y', direction = 'forward')\
        
        df_junction_info = df_junction_only_info.assign(type = 'junction')\
            .pipe(ds.pd_concat_rows, df_reservoir_info.assign(type = 'reservoir'))\
            .pipe(ds.pd_concat_rows, df_sink_info.assign(type = 'sink'))
        
        df_element_info = pd.concat([df_subbasin_info.assign(type = 'subbasin'),
                                     df_reach_info.assign(type = 'reach'),
                                     df_junction_info])

        df_element_info = df_element_info\
            .assign(index = lambda x: pd.to_numeric(x['index'], errors='coerce'))\
            .assign(index_end = lambda x: pd.to_numeric(x['index_end'], errors='coerce'))
        # df_element_info = df_element_info\
        #     .assign(index = lambda x: np.int64(x['index']))\
        #     .assign(index_ds = lambda x: np.int64(x['index_ds']))\
        #     .assign(index_end = lambda x: np.int64(x['index_end']))

        self.df_subbasin_info = df_subbasin_info
        self.df_reach_info = df_reach_info
        self.df_junction_info = df_junction_info
        self.df_reservoir_info = df_reservoir_info
        self.df_element_info = df_element_info

    def get_observed(self):
        '''Get observed data and corresponding element. Updated 'df_observed'.
        '''
        content_hms_basin = self.content_hms_basin
        df_element_info = self.df_element_info

        df_observed = get_hec_text_after_header(content_hms_basin, 'Observed ', col_names=['name'], col_name_index='index')
        df_observed = df_observed\
            .drop('name', axis=1)\
            .pipe(ds.pd_concat_cols, df_observed['name'].str.split(': ', expand=True).set_axis(['type_observed', 'name_observed'], axis=1))
        
        temp_df_element_info = df_element_info.loc[:,['name', 'type', 'index']].rename(columns={'name': 'name_element'}).sort_values(by = 'index')
        df_observed = ds.pd_merge_asof(df_observed, 
                                    temp_df_element_info, 
                                    on = 'index',  
                                    direction='backward')
        
        self.df_observed = df_observed

    def get_us_single(self, v_element: str, max_iter = 1000) -> pd.DataFrame:
        '''Read upstream element for one given element. Use 'get_us()' for multiple elements.

        Args:
            v_element (str): Given element.
            max_iter (int, optional): Maximum number of upper levels to check. Defaults to 1000.

        Returns:
            DataFrame: Dataframe containing upstream elements. 
                'name_us' indicates upstream elements at all levels, 
                'name_usds' indicates the immediately downstream element of the element listed in 'name_us',
                'type' indicates the element type,
                'level' indicates the level upstream (starting from 1).
        '''
        df_element_info = self.df_element_info

        v_elements_current = v_element
        df_us = pd.DataFrame()
        for iter in np.arange(0, max_iter):
            temp_df_us = df_element_info\
                            .loc[lambda x: x['name_ds'].isin(pd.Series(v_elements_current))]\
                            .loc[:, ['name', 'name_ds', 'type']]\
                            .eval('level = @iter + 1')
            
            if temp_df_us.shape[0] == 0:
                break

            df_us = df_us.pipe(ds.pd_concat_rows, temp_df_us)
            v_elements_current = temp_df_us.loc[:, 'name']

        df_us = df_us.rename(columns={'name': 'name_us',
                                      'name_ds': 'name_usds'})
        
        return (df_us)

    def get_us(self, v_elements: str|list|np.ndarray|pd.Series, max_iter = 1000) -> pd.DataFrame:
        '''Read upstream element for given elements. Uses 'get_us_single()' as backend.

        Args:
            v_element (str | list | array | Series): Vector of given elements.
            max_iter (int, optional): Maximum number of upper levels to check. Defaults to 1000.

        Returns:
            DataFrame: Dataframe containing upstream elements. 
                'name_us' indicates upstream elements at all levels, 
                'name_usds' indicates the immediately downstream element of the element listed in 'name_us',
                'type' indicates the element type,
                'level' indicates the level upstream (starting from 1),
                'name' indicates the name of the one of the given elements.
        '''
        get_us_single = self.get_us_single

        v_elements = ds.pd_to_series(v_elements)

        df_us = pd.DataFrame()
        for v_element in v_elements:
            temp_df_us = get_us_single(v_element)

            df_us = df_us.pipe(ds.pd_concat_rows, temp_df_us.assign(name = v_element))

        return (df_us)
    
    def read_parameters(self):
        content_hms_basin = self.content_hms_basin
        df_element_info = self.df_element_info
        df_subbasin_info = self.df_subbasin_info
        df_reach_info = self.df_reach_info
        df_reservoir_info = self.df_reservoir_info

        df_subbasin_params = copy.deepcopy(df_subbasin_info)        
        df_reach_params = copy.deepcopy(df_reach_info)        
        df_reservoir_params = copy.deepcopy(df_reservoir_info)        
        
        temp_element_start = df_element_info['index'].min()
        temp_element_end = df_element_info['index_end'].max()
        # content_hms_basin.str.extract(r'([^:]+)')
        v_all = content_hms_basin.iloc[temp_element_start:temp_element_end].str.extract(r'(.*?)(?=:)').iloc[:,0]
        v_all = v_all\
            .drop_duplicates().reset_index(drop=True)\
            .dropna()\
            .str.strip()
        v_all = v_all[~v_all.isin(['Subbasin', 'Reach', 'Junction', 'Reservoir', 'Sink', 'Downstream', 'Canvas X', 'Canvas Y', 'From Canvas X', 'From Canvas Y', 'Last Modified Date', 'Last Modified Time', 'Latitude Degrees', 'Longitude Degrees'])].reset_index(drop=True)
        v_all = v_all[~v_all.str.startswith('End')].reset_index(drop=True)

        for v_all_current in v_all:
            # v_all_current = v_all.iloc[0]

            temp_df_current = get_hec_text_after_header(content_hms_basin, v_all_current + ': ', col_names = [v_all_current], col_name_index='index_join')
            
            temp_df_current_info = df_element_info\
                .loc[:,['index','index_end','type']]\
                .sort_values(['index'])\
                .pipe(pd.merge_asof, temp_df_current, left_on = 'index', right_on = 'index_join', direction = 'forward')\
                .loc[lambda x: x['index_end'] > x['index_join']]
            
            if temp_df_current_info['type'].isin(['subbasin']).any():
                df_subbasin_params = df_subbasin_params.merge(temp_df_current_info[['index', v_all_current]], how = 'left', on = 'index')
            if temp_df_current_info['type'].isin(['reach']).any():
                df_reach_params = df_reach_params.merge(temp_df_current_info[['index', v_all_current]], how = 'left', on = 'index')
            if temp_df_current_info['type'].isin(['reservoir']).any():
                df_reservoir_params = df_reservoir_params.merge(temp_df_current_info[['index', v_all_current]], how = 'left', on = 'index')

        self.df_subbasin_params = df_subbasin_params
        self.df_reach_params = df_reach_params
        self.df_reservoir_params = df_reservoir_params

#endregion -------------------------------------------------------------------------------------------------
