#region Libraries

#%%
import os
import pandas as pd
import numpy as np

from .pb_functions_hec import *
from .pb_functions_hecras import *

import dsplus as ds

# pd.set_option('display.max_columns', None)
pd.options.display.max_columns = None
pd.options.display.max_rows = 8
# pd.options.display.max_colwidth=None

#endregion -------------------------------------------------------------------------------------------------
#region Class

#%%
class HecRas_Flow_Unsteady:
    name = None
    name_flow = None
    file_ras_flow = None
    content_ras_flow = None
    use_restart = None
    file_restart = None
    df_bc = None
    df_ic = None
    df_observed = None
    
    def __init__(self, name = '') -> None:
        self.name = name
    
    def read_from_file(self, file_ras_flow: str):
        content_ras_flow = ds.os_read_lines(file_ras_flow)
        
        name_flow = get_hec_text_after_header(content_ras_flow, 'Flow Title=', return_dataframe=False).iloc[0]

        self.name_flow = name_flow
        self.file_ras_flow = file_ras_flow
        self.content_ras_flow = content_ras_flow

        self.read_bc()
        self.read_ic()
        self.read_observed()
        
    def read_bc(self):
        file_ras_flow = self.file_ras_flow
        content_ras_flow = self.content_ras_flow

        try:
            use_restart = get_hec_text_after_header(content_ras_flow, 'Use Restart=', return_dataframe=False).iloc[0]
            file_restart = get_hec_text_after_header(content_ras_flow, 'Restart Filename=', return_dataframe=False).iloc[0]
        except Exception as e:
            use_restart = None
            file_restart = None

        df_bc = get_hec_text_after_header(content_ras_flow, 
                                          'Boundary Location=', 
                                          split_by=',',
                                          col_names=['river', 'reach', 'xs', 'unk3', 'unk4', 'name_2d_area', 'unk6', 'name_bc', 'unk8'])
        
        df_friction_slope = get_hec_text_after_header(content_ras_flow, 
                                                      'Friction Slope=', 
                                                      split_by=',',
                                                      col_names = ['slope', 'unk1'])        
        df_flow_min = get_hec_text_after_header(content_ras_flow, 
                                                'Flow Hydrograph QMin=', 
                                                split_by=',',
                                                col_names=['flow_min'])
        df_flow_mult = get_hec_text_after_header(content_ras_flow, 
                                                 'Flow Hydrograph QMult=', 
                                                 split_by=',',
                                                 col_names=['flow_multiplier'])
        df_flow_slope = get_hec_text_after_header(content_ras_flow, 
                                                  'Flow Hydrograph Slope=', 
                                                  split_by=',',
                                                  col_names=['flow_slope'])
        df_use_initial_stage = get_hec_text_after_header(content_ras_flow, 
                                                          'Stage Hydrograph Use Initial Stage=', 
                                                          split_by=',',
                                                          col_names=['use_initial_stage'])
        df_stage_hydrograph_tw_check = get_hec_text_after_header(content_ras_flow, 
                                                                 'Stage Hydrograph TW Check=', 
                                                                 split_by=',',
                                                                 col_names=['tw_check'])
        df_fixed_start = get_hec_text_after_header(content_ras_flow, 
                                                   'Use Fixed Start Time=', 
                                                   split_by=',',
                                                   col_names=['fixed_start'])
        df_interval = get_hec_text_after_header(content_ras_flow, 
                                                'Interval=', 
                                                split_by=',',
                                                col_names=['interval'])
        df_use_dss = get_hec_text_after_header(content_ras_flow, 
                                               'Use DSS=', 
                                               split_by=',',
                                               col_names=['use_dss'])
        df_file_dss = get_hec_text_after_header(content_ras_flow, 
                                                'DSS File=', 
                                                split_by=',',
                                                col_names=['file_dss'])
        df_dss_path = get_hec_text_after_header(content_ras_flow, 
                                                'DSS Path=', 
                                                split_by=',',
                                                col_names=['dss_path'])
        
        df_bc = df_bc\
            .pipe(ds.pd_merge_asof, df_friction_slope, on='index', one_to_many=True)\
            .pipe(ds.pd_merge_asof, df_flow_min, on='index', one_to_many=True)\
            .pipe(ds.pd_merge_asof, df_flow_mult, on='index', one_to_many=True)\
            .pipe(ds.pd_merge_asof, df_flow_slope, on='index', one_to_many=True)\
            .pipe(ds.pd_merge_asof, df_use_initial_stage, on='index', one_to_many=True)\
            .pipe(ds.pd_merge_asof, df_stage_hydrograph_tw_check, on='index', one_to_many=True)\
            .pipe(ds.pd_merge_asof, df_fixed_start, on='index', one_to_many=True)\
            .pipe(ds.pd_merge_asof, df_interval, on='index', one_to_many=True)\
            .pipe(ds.pd_merge_asof, df_use_dss, on='index', one_to_many=True)\
            .pipe(ds.pd_merge_asof, df_file_dss, on='index', one_to_many=True)\
            .pipe(ds.pd_merge_asof, df_dss_path, on='index', one_to_many=True)
        
        if isinstance(df_bc['file_dss'].iloc[0], str):        
            df_bc = df_bc\
                .assign(file_dss = lambda x: x['file_dss'].str.replace('.\\', os.path.dirname(file_ras_flow) + '\\'))
        
        self.use_restart = use_restart
        self.file_restart = file_restart
        self.df_bc = df_bc

    def read_ic(self):
        #TODO
        # file_ras_flow = self.file_ras_flow
        content_ras_flow = self.content_ras_flow

        df_ic = get_hec_text_after_header(content_ras_flow, 
                                          'Initial Flow Loc', 
                                          split_by=',')
        
        self.df_ic = df_ic

    def read_observed(self):
        file_ras_flow = self.file_ras_flow
        content_ras_flow = self.content_ras_flow

        temp_content_ras_flow = content_ras_flow.str.replace('|', '')

        df_name = get_hec_text_after_header(temp_content_ras_flow, r'Observed Time Series=StageTS Name=', col_names=['name'])
        df_source = get_hec_text_after_header(temp_content_ras_flow, r'Observed Time Series=StageTS Source=', col_names=['source'])
        df_file_dss = get_hec_text_after_header(temp_content_ras_flow, r'Observed Time Series=StageTS DSS Filename=', col_names=['file_dss'])
        df_dss_path = get_hec_text_after_header(temp_content_ras_flow, r'Observed Time Series=StageTS DSS Pathname=', col_names=['dss_path'])
        df_observed_stage = df_name\
            .pipe(ds.pd_merge_asof, df_source, on = 'index', one_to_many=True)\
            .pipe(ds.pd_merge_asof, df_file_dss, on = 'index', one_to_many=True)\
            .pipe(ds.pd_merge_asof, df_dss_path, on = 'index', one_to_many=True)\
            .assign(type = 'stage')
        
        df_name = get_hec_text_after_header(temp_content_ras_flow, r'Observed Time Series=FlowTS Name=', col_names=['name'])
        df_source = get_hec_text_after_header(temp_content_ras_flow, r'Observed Time Series=FlowTS Source=', col_names=['source'])
        df_file_dss = get_hec_text_after_header(temp_content_ras_flow, r'Observed Time Series=FlowTS DSS Filename=', col_names=['file_dss'])
        df_dss_path = get_hec_text_after_header(temp_content_ras_flow, r'Observed Time Series=FlowTS DSS Pathname=', col_names=['dss_path'])
        df_observed_flow = df_name\
            .pipe(ds.pd_merge_asof, df_source, on = 'index', one_to_many=True)\
            .pipe(ds.pd_merge_asof, df_file_dss, on = 'index', one_to_many=True)\
            .pipe(ds.pd_merge_asof, df_dss_path, on = 'index', one_to_many=True)\
            .assign(type = 'flow')
        
        df_observed = pd.DataFrame()
        if df_observed_stage.shape[0] + df_observed_flow.shape[0] > 0:
            df_observed = df_observed_stage.pipe(ds.pd_concat_rows, df_observed_flow)\
                .assign(ref_type = lambda x: np.where('Ref Line:' in x['name'], 'ref line', 'ref point'))\
                .assign(name = lambda x: x['name'].str.replace('Ref Line:', '').str.replace('Ref Point:', '').str.strip())\
                .pipe(ds.pd_select, 'index, type, ref_type, *')
            if isinstance(df_observed['file_dss'].iloc[0], str):        
                df_observed = df_observed\
                    .assign(file_dss = lambda x: x['file_dss'].str.replace('.\\', os.path.dirname(file_ras_flow) + '\\'))\

        self.df_observed = df_observed

#endregion -------------------------------------------------------------------------------------------------
