#region Libraries

#%%
import os

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
class HecHms:
    name = None
    folder_hms = None
    file_hms = None
    file_run = None
    file_gage = None
    df_hms = None
    df_run = None
    df_gage = None
    df_control = None

    def __init__(self, name = '') -> None:
        self.name = name

    def read_from_folder(self, folder_hms: str):
        '''Read HEC-HMS filenames. These include .hms, .run, and .gage files. Updates 'folder_hms', 'file_hms', 'file_run', and 'file_gage'.

        Args:
            folder_hms (str): HEC-HMS model folder.
        '''
        files_hms_folder = ds.os_list_dir(folder_hms)

        file_hms = files_hms_folder.pipe(lambda x: x[x.str.contains('\\.hms$')]).iloc[0]
        file_run = files_hms_folder.pipe(lambda x: x[x.str.contains('\\.run$')]).iloc[0]
        file_gage = files_hms_folder.pipe(lambda x: x[x.str.contains('\\.gage$')]).iloc[0]

        self.folder_hms = folder_hms
        self.file_hms = file_hms
        self.file_run = file_run
        self.file_gage = file_gage

    def read_file_hms(self):
        '''Read the content of the hms file. Updates 'df_hms'.
        '''
        folder_hms = self.folder_hms
        file_hms = self.file_hms

        content_hms = ds.os_read_lines(file_hms)
        
        temp_df_basin = get_hec_text_after_header(content_hms, 'Basin: ', col_names=['name']).assign(type = 'basin')
        temp_df_precip = get_hec_text_after_header(content_hms, 'Precipitation: ', col_names=['name']).assign(type = 'precipitation')
        temp_df_control = get_hec_text_after_header(content_hms, 'Control: ', col_names=['name']).assign(type = 'control')
        temp_df_filename = get_hec_text_after_header(content_hms, 'Filename: ', col_names=['name_file'], col_name_index='index_filename')
        temp_df_end = get_hec_text_after_header(content_hms, 'End:', col_name_index='index_end').loc[:, ['index_end']]
        
        temp_df_hms = pd.concat([temp_df_basin, temp_df_precip, temp_df_control], axis = 0).sort_values(by = 'index')
        
        df_hms = temp_df_hms\
            .pipe(pd.merge_asof, temp_df_filename, left_on = 'index', right_on = 'index_filename', direction='forward')\
            .pipe(pd.merge_asof, temp_df_end, left_on = 'index', right_on = 'index_end', direction='forward')\
            .assign(path_file = lambda x: ds.os_path_join(folder_hms, x['name_file']))\
            .pipe(ds.pd_select, 'index, index_filename, index_end, *')

        self.df_hms = df_hms

    def read_file_run(self):
        '''Read the content of the run file. Updates 'df_run'.
        '''
        folder_hms = self.folder_hms
        file_run = self.file_run

        content_run = ds.os_read_lines(file_run)
        
        temp_df_run = get_hec_text_after_header(content_run, 'Run: ', col_names=['name_run'])
        temp_df_file_log = get_hec_text_after_header(content_run, 'Log File: ', col_names=['file_log'])
        temp_df_file_dss = get_hec_text_after_header(content_run, 'DSS File: ', col_names=['file_dss'])
        temp_df_basin = get_hec_text_after_header(content_run, 'Basin: ', col_names=['name_basin'])
        temp_df_precip = get_hec_text_after_header(content_run, 'Precip: ', col_names=['name_precip'])
        temp_df_control = get_hec_text_after_header(content_run, 'Control: ', col_names=['name_control'])
        temp_df_end = get_hec_text_after_header(content_run, 'End:', col_name_index='index_end').loc[:, ['index_end']]
        
        df_run = temp_df_run\
            .pipe(pd.merge_asof, temp_df_file_log, on = 'index', direction='forward')\
            .pipe(pd.merge_asof, temp_df_file_dss, on = 'index', direction='forward')\
            .pipe(pd.merge_asof, temp_df_basin, on = 'index', direction='forward')\
            .pipe(pd.merge_asof, temp_df_precip, on = 'index', direction='forward')\
            .pipe(pd.merge_asof, temp_df_control, on = 'index', direction='forward')\
            .pipe(pd.merge_asof, temp_df_end, left_on = 'index', right_on = 'index_end', direction='forward')\
            .pipe(ds.pd_select, 'index, index_end, name_run, name_basin, name_precip, name_control, *')\
            .assign(path_log = lambda x: ds.os_path_join(folder_hms, x['file_log']))\
            .assign(path_dss = lambda x: ds.os_path_join(folder_hms, x['file_dss']))\
            .assign(path_results = lambda x: ds.str_concat(folder_hms, 
                                                           os.path.sep, 
                                                           'results', 
                                                           os.path.sep, 
                                                           'RUN_',
                                                           x['file_dss'].str.replace('dss', ''),
                                                           'results'))
                
        self.df_run = df_run

    def read_file_gage(self):
        '''Read the contents of the gage file. Updates 'df_gage'.
        '''
        folder_hms = self.folder_hms
        file_gage = self.file_gage

        content_gage = ds.os_read_lines(file_gage)

        temp_df_gage = get_hec_text_after_header(content_gage, 'Gage: ', col_names=['name_gage'])
        temp_df_type = get_hec_text_after_header(content_gage, 'Gage Type: ', col_names=['type_gage'])
        # temp_df_data_type = get_hec_text_after_header(content_gage, 'Gage: ', col_names=['name_gage'])
        temp_df_file_dss = get_hec_text_after_header(content_gage, 'DSS File Name: ', col_names=['file_dss'])
        temp_df_dss_path = get_hec_text_after_header(content_gage, 'DSS Pathname: ', col_names=['dss_path'])
        temp_df_end = get_hec_text_after_header(content_gage, 'End:', col_name_index='index_end').loc[:, ['index_end']]

        df_gage = temp_df_gage\
            .pipe(pd.merge_asof, temp_df_type, on = 'index', direction='forward')\
            .pipe(pd.merge_asof, temp_df_file_dss, on = 'index', direction='forward')\
            .pipe(pd.merge_asof, temp_df_dss_path, on = 'index', direction='forward')\
            .pipe(pd.merge_asof, temp_df_end, left_on = 'index', right_on = 'index_end', direction='forward')\
            .pipe(ds.pd_select, 'index, index_end, *')\
            .assign(path_dss = lambda x: ds.os_path_join(folder_hms, x['file_dss']))

        self.df_gage = df_gage

    def read_files_control(self):
        '''Read the contents of control files. Updates 'df_control'.
        '''        
        folder_hms = self.folder_hms
        df_hms = self.df_hms

        df_control = df_hms\
            .loc[lambda x: x['type'] == 'control', ['name', 'name_file', 'path_file']]\
            .rename(columns={'name': 'name_control'})

        # files_control = path_join(folder_hms, df_control['name_file'])
        files_control = df_control['path_file']

        temp_df_control_info = pd.DataFrame()
        for file_control in files_control:
            # file_control = files_control.iloc[0]
            content_control = ds.os_read_lines(file_control)

            temp_df_control_name = get_hec_text_after_header(content_control, 'Control: ', col_names=['name_control'])
            temp_df_date_start = get_hec_text_after_header(content_control, 'Start Date: ', col_names=['date_start'])
            temp_df_time_start = get_hec_text_after_header(content_control, 'Start Time: ', col_names=['time_start'])
            temp_df_date_end = get_hec_text_after_header(content_control, 'End Date: ', col_names=['date_end'])
            temp_df_time_end = get_hec_text_after_header(content_control, 'End Time: ', col_names=['time_end'])
            temp_df_end = get_hec_text_after_header(content_control, 'End:', col_name_index='index_end').loc[:, ['index_end']]

            temp_df_control = temp_df_control_name\
                .pipe(pd.merge_asof, temp_df_date_start, on = 'index', direction='forward')\
                .pipe(pd.merge_asof, temp_df_time_start, on = 'index', direction='forward')\
                .pipe(pd.merge_asof, temp_df_date_end, on = 'index', direction='forward')\
                .pipe(pd.merge_asof, temp_df_time_end, on = 'index', direction='forward')\
                .pipe(pd.merge_asof, temp_df_end, left_on = 'index', right_on = 'index_end', direction='forward')

            temp_df_control_info = temp_df_control_info.pipe(ds.pd_concat_rows, temp_df_control)

        df_control = df_control\
            .pipe(ds.pd_concat_cols, temp_df_control_info.drop('name_control', axis=1))\
            .assign(path_file = lambda x: ds.os_path_join(folder_hms, x['name_file']))\
            .pipe(ds.pd_select, 'index, index_end, *, name_file, path_file')

        self.df_control = df_control

#endregion -------------------------------------------------------------------------------------------------
