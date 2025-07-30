#region Libraries

#%%
import os

import pandas as pd
import numpy as np

import xml.etree.ElementTree as ET

from .pb_functions_hec import *
from .pb_functions_hecras import *
from .pb_class_hecras_plan import *
from .pb_class_hecras_flow_unsteady import *
from .pb_class_hecras_results import *

import dsplus as ds

# pd.set_option('display.max_columns', None)
pd.options.display.max_columns = None
pd.options.display.max_rows = 8
# pd.options.display.max_colwidth=None

#endregion -------------------------------------------------------------------------------------------------
#region Class

#%%
class HecRas:
    name = None
    name_project = None
    
    folder_ras = None
    
    filename = None
    file_prj = None
    file_rasmap = None
    file_crs = None

    df_files_geom = None
    df_files_flow_steady = None
    df_files_flow_unsteady = None
    df_files_plan = None

    df_flow_unsteady_info = None
    df_results_info = None

    df_results_msg_error = None

    crs_text = None

    df_bc_unsteady = None
    df_ic_unsteady = None
    df_observed_unsteady = None
    df_plan_info = None

    def __init__(self, name = '') -> None:
        self.name = name

    def read_from_folder(self, folder_ras: str):
        '''Read prj and rasmap files in HEC-RAS model folder. Updates 'file_prj' and 'file_rasmap'.

        Args:
            folder_ras (str): HEC-RAS model folder.
        '''
        files_ras_folder = ds.os_list_dir(folder_ras)

        files_prj = files_ras_folder.pipe(lambda x: x[x.str.contains('\\.prj$')])

        for file_prj in files_prj:
            content_prj = ds.os_read_lines(file_prj)
            if content_prj.iloc[0:1].str.startswith('Proj Title=').any():
                break

        file_rasmap = pd.Series(file_prj).str.replace('.prj', '.rasmap').iloc[0]
        
        filename = os.path.basename(file_prj).replace(r'.prj', '')

        self.folder_ras = folder_ras
        self.filename = filename
        self.file_prj = file_prj
        self.file_rasmap = file_rasmap

    def read_file_prj(self):
        '''Read key project files. Updates 'title_project', 'df_files_plan', 'df_files_geom', 'df_files_flow_steady', and 'df_files_flow_unsteady'.
        '''
        folder_ras = self.folder_ras
        filename = self.filename
        file_prj = self.file_prj

        content_prj = ds.os_read_lines(file_prj)

        name_project = get_hec_text_after_header(content_prj, 'Proj Title=', return_dataframe=False).iloc[0]

        df_current_plan = get_hec_text_after_header(content_prj, 'Current Plan=', col_names=['extension'], return_index=False)
        if df_current_plan.shape[0] == 0:
            df_current_plan = pd.DataFrame(dict(extension=[None]))
        
        df_files_plan = get_hec_text_after_header(content_prj, 'Plan File=', col_names=['extension'], return_index=False)
        if df_files_plan.shape[0] > 0:
            df_files_plan = df_files_plan\
                .assign(current = lambda x: np.where(x['extension'].isin(df_current_plan['extension']), 1, 0))\
                .assign(path_file = lambda x: ds.os_path_join(folder_ras, filename, x['extension']))\
                .assign(path_file_hdf = lambda x: ds.str_concat(x['path_file'], r'.hdf'))

        df_files_geom = get_hec_text_after_header(content_prj, 'Geom File=', col_names=['extension'], return_index=False)
        if df_files_geom.shape[0] > 0:
            df_files_geom = df_files_geom\
                .assign(path_file = lambda x: ds.os_path_join(folder_ras, filename, x['extension']))\
                .assign(path_file_hdf = lambda x: ds.str_concat(x['path_file'], r'.hdf'))
        
        df_files_flow_steady = get_hec_text_after_header(content_prj, 'Flow File=', col_names=['extension'], return_index=False)
        if df_files_flow_steady.shape[0] > 0:
            df_files_flow_steady = df_files_flow_steady\
                .assign(path_file = lambda x: ds.os_path_join(folder_ras, filename, x['extension']))\
                .assign(path_file_hdf = lambda x: ds.str_concat(x['path_file'], r'.hdf'))

        df_files_flow_unsteady = get_hec_text_after_header(content_prj, 'Unsteady File=', col_names=['extension'], return_index=False)
        if df_files_flow_unsteady.shape[0] > 0:
            df_files_flow_unsteady = df_files_flow_unsteady\
                .assign(path_file = lambda x: ds.os_path_join(folder_ras, filename, x['extension']))\
                .assign(path_file_hdf = lambda x: ds.str_concat(x['path_file'], r'.hdf'))
        
        self.name_project = name_project
        self.df_files_plan = df_files_plan
        self.df_files_geom = df_files_geom
        self.df_files_flow_steady = df_files_flow_steady
        self.df_files_flow_unsteady = df_files_flow_unsteady

    def read_file_rasmap(self):
        '''Read rasmap content. Updates 'file_crs', and 'crs_text'.
        '''
        #TODO
        folder_ras = self.folder_ras
        file_rasmap = self.file_rasmap
        
        xml_element_tree = ET.parse(file_rasmap)

        xml_root = xml_element_tree.getroot()  # Load your XML file
        
        file_crs = xml_root[1].get('Filename')
        if file_crs is not None:
            if file_crs[0] == '.':
                file_crs = os.path.join(folder_ras, file_crs[2:])
            else:
                file_crs = os.path.join(folder_ras, file_crs)
            # file_crs = file_crs.replace(r'^\.', folder_ras)
        
            with open(file_crs, "r") as f:
                crs_text = f.read()
        else:
            crs_text = None

        self.file_crs = file_crs
        self.crs_text = crs_text
        
    def read_plans(self):
        '''Read all plans. Updates 'df_plan_info'.
        '''
        # df_files_geom = self.df_files_geom
        # df_files_flow_steady = self.df_files_flow_steady
        # df_files_flow_unsteady = self.df_files_flow_unsteady
        df_files_plan = self.df_files_plan

        df_plan_info = df_files_plan\
            .assign(name_plan = None)\
            .assign(extension_geom = None)\
            .assign(extension_flow = None)\
            .assign(dttm_start = None)\
            .assign(dttm_end = None)

        for i, row in df_files_plan.iterrows():
            # i = 0
            # row = df_files_plan.iloc[0]

            file_plan = row['path_file']

            if os.path.isfile(file_plan):
                ras_plan = HecRas_Plan(name='temp')            
                ras_plan.read_from_file(file_plan)

                df_plan_info.iloc[i, lambda x: x.columns.get_loc('name_plan')] = ras_plan.name_plan
                df_plan_info.iloc[i, lambda x: x.columns.get_loc('extension_geom')] = ras_plan.extension_geom
                df_plan_info.iloc[i, lambda x: x.columns.get_loc('extension_flow')] = ras_plan.extension_flow
                df_plan_info.iloc[i, lambda x: x.columns.get_loc('dttm_start')] = ras_plan.dttm_start
                df_plan_info.iloc[i, lambda x: x.columns.get_loc('dttm_end')] = ras_plan.dttm_end
        
        df_plan_info = df_plan_info\
            .loc[:, ['name_plan',
                     'extension', 'extension_geom', 'extension_flow', 
                     'dttm_start', 'dttm_end',
                     ]]\
            .assign(duration = lambda x: x['dttm_end'] - x['dttm_start'])
        
        self.df_plan_info = df_plan_info

    def read_results(self):
        df_files_plan = self.df_files_plan        
        df_plan_info = self.df_plan_info
        
        df_results_info = pd.DataFrame()
        df_results_msg_error = pd.DataFrame()
        for i, row in df_files_plan.iterrows():
            # i = 0
            # row = df_files_plan.iloc[i]

            current_plan_name = df_plan_info.loc[lambda x: x['extension'] == row['extension']].loc[:, 'name_plan'].iloc[0]
            file_ras_plan_hdf = row['path_file_hdf']

            if os.path.isfile(file_ras_plan_hdf):
                ras_results = HecRas_Results(name = '')
                
                ras_results.read_from_file(file_ras_plan_hdf)

                if ras_results.flag_run_ended:
                    ras_results.read_run_time()
                    ras_results.read_computation_msg()

                    df_run_time = ras_results.df_run_time
                    
                    if ras_results.df_error_iter is not None:
                        max_wse_iter_error = ras_results.df_error_iter['error'].max()
                    else:
                        max_wse_iter_error = None

                    temp_df_results_info = pd.DataFrame(dict(name = [current_plan_name],
                                                             run_complete = [ras_results.flag_run_complete],
                                                             error_msg = [ras_results.flag_error_msg],
                                                             volume_error_p100 = [ras_results.volume_error_p100],
                                                             max_wse_iter_error = [max_wse_iter_error]))\
                                    .pipe(ds.pd_concat_cols, df_run_time)
                    df_results_info = df_results_info.pipe(ds.pd_concat_rows, temp_df_results_info)

                    if ras_results.flag_error_msg > 0:
                        temp_df_results_msg_error = ras_results.df_results_msg_error.assign(name = current_plan_name)
                        df_results_msg_error = df_results_msg_error.pipe(ds.pd_concat_rows, temp_df_results_msg_error)

        self.df_results_info = df_results_info
        self.df_results_msg_error = df_results_msg_error
        
    def read_flows_unsteady(self):
        '''Read all unsteady flows. Updates 'df_flow_unsteady_info', 'df_bc_unsteady', 'df_ic_unsteady', and 'df_observed_unsteady'.
        '''
        df_files_flow_unsteady = self.df_files_flow_unsteady

        df_flow_unsteady_info = df_files_flow_unsteady\
            .assign(name_flow = None)\
            .assign(use_restart = None)\
            .assign(file_restart = None)

        df_bc_unsteady = pd.DataFrame()
        df_ic_unsteady = pd.DataFrame()
        df_observed_unsteady = pd.DataFrame()
        for i, row in df_flow_unsteady_info.iterrows():
            # i = 0
            # row = df_flow_unsteady_info.iloc[i]
        
            file_flow_unsteady = row['path_file']
            ras_flow_unsteady = HecRas_Flow_Unsteady(name='temp')            
            ras_flow_unsteady.read_from_file(file_flow_unsteady)
        
            df_flow_unsteady_info.iloc[i, lambda x: x.columns.get_loc('name_flow')] = ras_flow_unsteady.name_flow
            df_flow_unsteady_info.iloc[i, lambda x: x.columns.get_loc('use_restart')] = ras_flow_unsteady.use_restart
            df_flow_unsteady_info.iloc[i, lambda x: x.columns.get_loc('file_restart')] = ras_flow_unsteady.file_restart

            df_bc_unsteady = df_bc_unsteady\
                .pipe(ds.pd_concat_rows,
                      ras_flow_unsteady.df_bc\
                        .assign(extension_flow = row['extension']))            
            df_ic_unsteady = df_ic_unsteady\
                .pipe(ds.pd_concat_rows,
                      ras_flow_unsteady.df_ic\
                        .assign(extension_flow = row['extension']))            
            df_observed_unsteady = df_observed_unsteady\
                .pipe(ds.pd_concat_rows,
                      ras_flow_unsteady.df_observed\
                        .assign(extension_flow = row['extension']))            
        
        df_flow_unsteady_info = df_flow_unsteady_info\
            .loc[:, ['name_flow',
                     'extension',
                     'use_restart', 'file_restart']]
        df_bc_unsteady = df_bc_unsteady.pipe(ds.pd_select, 'extension_flow, *')
        df_ic_unsteady = df_ic_unsteady.pipe(ds.pd_select, 'extension_flow, *')
        df_observed_unsteady = df_observed_unsteady.pipe(ds.pd_select, 'extension_flow, *')

        self.df_flow_unsteady_info = df_flow_unsteady_info
        self.df_bc_unsteady = df_bc_unsteady
        self.df_ic_unsteady = df_ic_unsteady
        self.df_observed_unsteady = df_observed_unsteady

#endregion -------------------------------------------------------------------------------------------------
