#region Libraries

#%%
import re

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
class HecRas_Results:
    name = None

    v_hdf_groups = None
    v_hdf_datasets = None

    flag_run_ended = None
    flag_run_complete = None
    flag_error_msg = None

    df_results_msg_error = None

    v_result_msg = None

    name_plan = None
    name_flow = None
    name_geom = None
    extension_geom = None
    extension_flow = None
    extension_plan = None
    file_ras_plan_hdf = None
    dttm_start = None
    dttm_end = None

    df_run_time_raw = None
    df_run_time = None

    volume_error = None
    volume_error_p100 = None
    df_error_iter = None

    df_ts_sa2d = None
    df_ts_ref_lines = None
    df_ts_ref_points = None

    df_observed_flow = None
    df_observed_stage = None
    df_observed_hwm = None
    
    def __init__(self, name = '') -> None:
        self.name = name

    def read_from_file(self, file_ras_plan_hdf: str, read_initial = True):
        '''Read plan hdf file (results). Updates 'file_ras_plan_hdf' and optionally 'v_hdf_datasets', 'v_hdf_groups', 'flag_run_ended', 'name_plan', 'name_flow', 'name_geom', 'extension_geom', 'extension_flow', 'extension_plan', 'dttm_start', and 'dttm_end'.

        Args:
            read_initial (bool, optional): Whether to only set updates 'file_ras_plan_hdf' or other variables too. Defaults to True (update other variables too).
            file_ras_plan_hdf (str): Plan hdf filename.
        '''
        self.file_ras_plan_hdf = file_ras_plan_hdf

        if read_initial:
            v_hdf_datasets = hdf_read_datasets(file_ras_plan_hdf)
            v_hdf_groups = hdf_read_groups(file_ras_plan_hdf)
            flag_run_ended = v_hdf_groups.str.contains('Plan Data/Plan Information').any() and v_hdf_groups.str.contains('Results/Summary').any()

            if flag_run_ended:
                dict_plan_info = hdf_read_attributes(file_ras_plan_hdf, 'Plan Data/Plan Information')

                name_plan = dict_plan_info['Plan Name']
                name_flow = dict_plan_info['Flow Title']
                name_geom = dict_plan_info['Geometry Title']
                extension_geom = dict_plan_info['Geometry Filename']
                extension_flow = dict_plan_info['Flow Filename']
                extension_plan = dict_plan_info['Plan Filename']
                dttm_start = pd_to_datetime_hec(dict_plan_info['Simulation End Time'])
                dttm_end = pd_to_datetime_hec(dict_plan_info['Simulation Start Time'])

                self.v_hdf_groups = v_hdf_groups
                self.v_hdf_datasets = v_hdf_datasets
                self.name_plan = name_plan
                self.name_flow = name_flow
                self.name_geom = name_geom
                self.extension_geom = extension_geom
                self.extension_flow = extension_flow
                self.extension_plan = extension_plan
                self.file_ras_plan_hdf = file_ras_plan_hdf
                self.dttm_start = dttm_start
                self.dttm_end = dttm_end
            self.v_hdf_datasets = v_hdf_datasets
            self.v_hdf_groups = v_hdf_groups
            self.flag_run_ended = flag_run_ended

    def read_run_time(self):
        '''Read run times. Updates 'df_run_time_raw' and 'df_run_time'.
        '''
        file_ras_plan_hdf = self.file_ras_plan_hdf

        df_run_time_raw = hdf_read_df(file_ras_plan_hdf, 'Results/Summary/Compute Processes')
        df_run_time_raw = df_run_time_raw\
            .loc[:, ['Process', 'Compute Time (ms)']]\
            .pipe(ds.pd_set_colnames, ['process', 'runtime_hr'])\
            .assign(runtime_hr = lambda x: x['runtime_hr']/(1000*60*60))

        run_time_preprocess_hr = df_run_time_raw.loc[lambda x: x['process'].isin(['Completing Geometry', 'Preprocessing Geometry', 'Completing Event Conditions', 'Completing Geometry, Flow and Plan']), 'runtime_hr'].sum()
        run_time_flow_hr = df_run_time_raw.loc[lambda x: x['process'].isin(['Unsteady Flow Computations', 'Steady Flow Computations']), 'runtime_hr'].sum()
        run_time_postprocess_hr = df_run_time_raw.loc[lambda x: x['process'].isin(['Post-Processing', 'Generating Time Series Post Process']), 'runtime_hr'].sum()
        run_time_total_hr = df_run_time_raw['runtime_hr'].sum()
        df_run_time = pd.DataFrame(dict(run_time_preprocess_hr = [run_time_preprocess_hr],
                                        run_time_flow_hr = [run_time_flow_hr],
                                        run_time_postprocess_hr = [run_time_postprocess_hr],
                                        run_time_total_hr = [run_time_total_hr]))

        self.df_run_time_raw = df_run_time_raw
        self.df_run_time = df_run_time

    def read_computation_msg(self):
        file_ras_plan_hdf = self.file_ras_plan_hdf

        result_msg = hdf_read_df(file_ras_plan_hdf, 'Results/Summary/Compute Messages (text)')
        result_msg = pd.Series(result_msg.iloc[0,0].split('\r\n'))

        # Finished run
        flag_run_complete = \
        (result_msg
            .str.contains('Finished Unsteady|Steady Flow Simulation').any()
        )

        # Error in run
        # flag_error_msg = result_msg\
        #     .pipe(lambda x: x[~x.str.contains('Overall Volume Accounting Error in Acre Feet:')])\
        #     .pipe(lambda x: x[~x.str.contains('Overall Volume Accounting Error as percentage:')])\
        #     .pipe(lambda x: x[~x.str.contains('The maximum cell wsel error was')])\
        #     .pipe(lambda _: _[~_.str.contains('Maximum iteration location		Cell	 WSEL	ERROR	ITERATIONS')])\
        #     .str.contains('Error', case=False).sum()
        
        # Error in run
        result_msg_error = \
        (result_msg
            .pipe(lambda x: x[~x.str.contains('Overall Volume Accounting Error in Acre Feet:')])
            .pipe(lambda x: x[~x.str.contains('Overall Volume Accounting Error as percentage:')])
            .pipe(lambda x: x[~x.str.contains('The maximum cell wsel error was')])
            .pipe(lambda _: _[~_.str.contains('Maximum iteration location		Cell	 WSEL	ERROR	ITERATIONS')])
            .pipe(lambda _: _[~_.str.contains('Maximum iteration location		RS (or Cell)	 WSEL	ERROR	ITERATIONS', regex = False)])
            .pipe(lambda _: _[~_.str.contains(r'Maximum iteration location\t\tRS \(or Cell\)\t WSEL\tERROR\tITERATIONS')])
        )
        result_msg_error = result_msg_error[(result_msg_error.str.contains('Error', case=False)) | (result_msg_error.str.contains('went unstable', case=False))]
        # df_result_msg_error = result_msg_error.reset_index().pipe(ds.ds.pd_set_colnames, [['index', 'msg']])
        df_results_msg_error = result_msg_error.reset_index().set_axis([['index', 'msg']], axis=1)

        flag_error_msg = len(result_msg_error)

        # Volume accounting error
        volume_error = get_hec_text_after_header(result_msg, 'Overall Volume Accounting Error in Acre Feet:')
        if volume_error.shape[0] == 0:
            volume_error = None
        else:
            volume_error = ds.as_numeric(volume_error.iloc[0,1])
        volume_error_p100 = get_hec_text_after_header(result_msg, 'Overall Volume Accounting Error as percentage:')
        if volume_error_p100.shape[0] == 0:
            volume_error_p100 = None
        else:
            volume_error_p100 = ds.as_numeric(volume_error_p100.iloc[0,1])

        # Iteration error
        if volume_error is not None:
            if len(result_msg.pipe(lambda x: x[x.str.contains('Maximum iteration location')])) > 0:
                index_start = result_msg.pipe(lambda x: x[x.str.contains('Maximum iteration location')]).index.to_series().iloc[0] + 2
                index_end = result_msg.pipe(lambda x: x[x.str.contains('Overall Volume Accounting Error in Acre Feet:')]).index.to_series().iloc[0] - 2
                result_msg_iter = result_msg.loc[index_start:index_end]
                result_msg_iter = result_msg_iter[result_msg_iter != '']
                result_msg_iter.str.replace('\t', ' ').str.split(' ', expand = True)
                df_error_iter = result_msg_iter.str.split('\t', expand = True)
                df_error_iter = df_error_iter\
                    .reset_index(drop=True)\
                    .pipe(ds.pd_set_colnames, ['x', 'id2', 'id3', 'wse', 'error', 'iter'])\
                    .assign(dttm = lambda x: x['x'].str.slice(0, 18))\
                    .assign(id1 = lambda x: x['x'].str.slice(19))\
                    .pipe(ds.pd_select_simple, ['dttm', 'id1'], cols_drop = 'x')\
                    .assign(error = lambda x: ds.as_numeric(x['error']))\
                    .assign(iter = lambda x: ds.as_numeric(x['iter']))
            else:
                df_error_iter = None
        else:
            df_error_iter = None

        self.v_result_msg = result_msg
        self.flag_run_complete = flag_run_complete
        self.flag_error_msg = flag_error_msg
        self.df_results_msg_error = df_results_msg_error
        self.volume_error = volume_error
        self.volume_error_p100 = volume_error_p100
        self.df_error_iter = df_error_iter

    def read_ts_sa2d(self):
        '''Read SA2D timeseries results. Updates 'df_ts_sa2d'.
        '''
        file_ras_plan_hdf = self.file_ras_plan_hdf
        v_hdf_groups = self.v_hdf_groups

        df_dttm = hdf_read_df(file_ras_plan_hdf, pathname='Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/Time Date Stamp')
        v_dttm = pd_to_datetime_hec(df_dttm.iloc[:, 0])

        v_groups_sa2d = v_hdf_groups.pipe(lambda x: x[x.str.contains('Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/2D Bridges/')])
        v_name_sa2d = get_hec_text_after_header(v_groups_sa2d, 'Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/2D Bridges/', return_dataframe=False)

        df_ts_sa2d = pd.DataFrame()
        for i, current_groups_sa2d in v_groups_sa2d.items():
            # current_groups_sa2d = v_groups_sa2d.iloc[0]

            temp_df = hdf_read_df(file_ras_plan_hdf, current_groups_sa2d + '/Structure Variables')
            temp_df = temp_df\
                .pipe(ds.pd_set_colnames, ['flow', 'wsel_us', 'wsel_ds'])\
                .assign(name_sa2d = v_name_sa2d[i],
                        dttm = v_dttm)

            df_ts_sa2d = ds.pd_concat_rows(df_ts_sa2d, temp_df)

        df_ts_sa2d = df_ts_sa2d.pipe(ds.pd_select_simple, cols_before = ['name_sa2d', 'dttm'])

        self.df_ts_sa2d = df_ts_sa2d

    def read_ts_ref_lines(self):
        '''Read reference line timeseries results. Updates 'df_ts_ref_lines'.
        '''
        file_ras_plan_hdf = self.file_ras_plan_hdf

        df_dttm = hdf_read_df(file_ras_plan_hdf, pathname='Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/Time Date Stamp')
        v_dttm = pd_to_datetime_hec(df_dttm.iloc[:, 0])

        df_name = hdf_read_df(file_ras_plan_hdf, 'Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/Reference Lines/Name')
        df_flow = hdf_read_df(file_ras_plan_hdf, 'Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/Reference Lines/Flow')
        df_wsel = hdf_read_df(file_ras_plan_hdf, 'Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/Reference Lines/Water Surface')

        df_ref_line_flow = df_flow\
            .set_axis(df_name.iloc[:, 0], axis=1)\
            .assign(dttm = v_dttm)\
            .melt(id_vars='dttm',
                  var_name='name',
                  value_name='q_cfs')\
            .pipe(ds.pd_select_simple, ['name', 'dttm'])

        df_ref_line_wsel = df_wsel\
            .set_axis(df_name.iloc[:, 0], axis=1)\
            .assign(dttm = v_dttm)\
            .melt(id_vars='dttm',
                  var_name='name',
                  value_name='wsel_ft')\
            .pipe(ds.pd_select_simple, ['name', 'dttm'])

        df_ts_ref_lines = pd.merge(df_ref_line_flow, df_ref_line_wsel,
                                   on = ['name', 'dttm'])

        df_ts_ref_lines = df_ts_ref_lines\
            .pipe(lambda x: ds.pd_split_column(x, '|', 'name', ['Name', 'SA/2D']))\
            .rename(columns={'name': 'id'})\
            .pipe(ds.pd_select_simple, ['id', 'Name', 'SA/2D'])

        self.df_ts_ref_lines = df_ts_ref_lines

    def read_ts_ref_points(self):
        '''Read reference point timeseries results. Updates 'df_ts_ref_points'.
        '''
        file_ras_plan_hdf = self.file_ras_plan_hdf

        df_dttm = hdf_read_df(file_ras_plan_hdf, pathname='Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/Time Date Stamp')
        v_dttm = pd_to_datetime_hec(df_dttm.iloc[:, 0])

        df_name = hdf_read_df(file_ras_plan_hdf, 'Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/Reference Points/Name')
        df_velocity = hdf_read_df(file_ras_plan_hdf, 'Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/Reference Points/Velocity')
        df_wsel = hdf_read_df(file_ras_plan_hdf, 'Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/Reference Points/Water Surface')

        df_ref_point_flow = df_velocity\
            .set_axis(df_name.iloc[:, 0], axis=1)\
            .assign(dttm = v_dttm)\
            .melt(id_vars='dttm',
                  var_name='name',
                  value_name='v_fps')\
            .pipe(ds.pd_select_simple, ['name', 'dttm'])

        df_ref_point_wsel = df_wsel\
            .set_axis(df_name.iloc[:, 0], axis=1)\
            .assign(dttm = v_dttm)\
            .melt(id_vars='dttm',
                  var_name='name',
                  value_name='wsel_ft')\
            .pipe(ds.pd_select_simple, ['name', 'dttm'])

        df_ts_ref_points = pd.merge(df_ref_point_flow, df_ref_point_wsel,
                                    on = ['name', 'dttm'])

        df_ts_ref_points = df_ts_ref_points\
            .pipe(lambda x: ds.pd_split_column(x, '|', 'name', ['Name', 'SA/2D']))\
            .rename(columns={'name': 'id'})\
            .pipe(ds.pd_select_simple, ['id', 'Name', 'SA/2D'])

        self.df_ts_ref_points = df_ts_ref_points

    def read_observed(self):
        '''Read observed data. Updates 'df_observed_flow', 'df_observed_stage', and 'df_observed_hwm'.
        '''
        file_ras_plan_hdf = self.file_ras_plan_hdf

        v_hdf_datasets = self.v_hdf_datasets
        v_hdf_groups = self.v_hdf_groups

        df_observed_flow = pd.DataFrame()
        df_observed_stage = pd.DataFrame()
        df_observed_hwm = pd.DataFrame()

        if v_hdf_groups.str.contains('Event Conditions/Observed Data/Flow').any():
            df_observed_flow_attributes = hdf_read_df(file_ras_plan_hdf, 'Event Conditions/Observed Data/Flow/Attributes')

            if df_observed_flow_attributes.shape[0] > 0:
                for i, row in df_observed_flow_attributes.iterrows():
                    # i = 1
                    # row = df_observed_flow_attributes.iloc[i]

                    current_pathname = 'Event Conditions/Observed Data/Flow/' + row['Dataset']
                    if v_hdf_datasets.str.contains(current_pathname).any():
                        current_df_observed_flow_attributes = hdf_read_df(file_ras_plan_hdf, current_pathname)
                        current_df_observed_flow_attributes = current_df_observed_flow_attributes.assign(type = row['Type'],
                                                                                                         name = row['Name'])
                        df_observed_flow = df_observed_flow.pipe(ds.pd_concat_rows, current_df_observed_flow_attributes)

                if df_observed_flow.shape[0] > 0:
                    df_observed_flow = df_observed_flow\
                        .pipe(ds.pd_set_colnames, ['dttm', 'sim_time', 'q_cfs', 'type', 'name'])\
                        .pipe(ds.pd_select_simple, ['type', 'name'])\
                        .assign(dttm = lambda x: pd_to_datetime_hec(x['dttm']))

        if v_hdf_groups.str.contains('Event Conditions/Observed Data/Stage').any():
            df_observed_stage_attributes = hdf_read_df(file_ras_plan_hdf, 'Event Conditions/Observed Data/Stage/Attributes')

            if df_observed_stage_attributes.shape[0] > 0:
                for i, row in df_observed_stage_attributes.iterrows():
                    # i = 9
                    # row = df_observed_stage_attributes.iloc[i]

                    current_pathname = 'Event Conditions/Observed Data/Stage/' + row['Dataset']
                    if v_hdf_datasets.str.contains(re.escape(current_pathname)).any():
                        current_df_observed_stage_attributes = hdf_read_df(file_ras_plan_hdf, current_pathname)
                        current_df_observed_stage_attributes = current_df_observed_stage_attributes.assign(type = row['Type'],
                                                                                                           name = row['Name'])
                        df_observed_stage = df_observed_stage.pipe(ds.pd_concat_rows, current_df_observed_stage_attributes)

                if df_observed_stage.shape[0] > 0:
                    df_observed_stage = df_observed_stage\
                        .pipe(ds.pd_set_colnames, ['dttm', 'sim_time', 'wsel_ft', 'type', 'name'])\
                        .pipe(ds.pd_select_simple, ['type', 'name'])\
                        .assign(dttm = lambda x: pd_to_datetime_hec(x['dttm']))

        if v_hdf_groups.str.contains('Event Conditions/Observed Data/High Water Mark').any():
            df_observed_hwm_attributes = hdf_read_df(file_ras_plan_hdf, 'Event Conditions/Observed Data/High Water Mark/Attributes')

            if df_observed_hwm_attributes.shape[0] > 0:
                df_observed_hwm = df_observed_hwm_attributes.pipe(ds.pd_set_colnames, ['type', 'name', 'value'])

        self.df_observed_flow = df_observed_flow
        self.df_observed_stage = df_observed_stage
        self.df_observed_hwm = df_observed_hwm
        
#endregion -------------------------------------------------------------------------------------------------
#region Archive

#%%
# def read_ts_sa2d(self):
#     file_ras_plan_hdf = self.file_ras_plan_hdf
#     v_hdf_groups = self.v_hdf_groups

#     df_dttm = hdf_read_df(file_ras_plan_hdf, 'Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/Time Date Stamp', decode_binary_str=True)
#     v_dttm = pd_to_datetime_hec(df_dttm.iloc[:, 0])

#     v_groups_sa2d = v_hdf_groups.pipe(lambda x: x[x.str.contains('Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/2D Bridges/')])
#     v_name_sa2d = get_hec_text_after_header(v_groups_sa2d, 'Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/2D Bridges/', return_dataframe=False)

#     df_ts_sa2d = pd.DataFrame()
#     for i, current_groups_sa2d in v_groups_sa2d.items():
#         # current_groups_sa2d = v_groups_sa2d.iloc[0]

#         # df_wsel_ds = hdf_read_df(file_ras_plan_hdf, current_groups_sa2d + '/Cell WS DS')
#         # v_wsel_ds = df_wsel_ds.mean(axis=1)

#         # df_wsel_us = hdf_read_df(file_ras_plan_hdf, current_groups_sa2d + '/Cell WS US')
#         # v_wsel_us = df_wsel_us.mean(axis=1)

#         # df_flow = hdf_read_df(file_ras_plan_hdf, current_groups_sa2d + '/Face Flow')
#         # v_flow = df_flow.sum(axis=1)

#         # temp_df = pd.DataFrame(dict(name_sa2d = v_name_sa2d[i],
#         #                             dttm = v_dttm,
#         #                             wsel_us = v_wsel_us,
#         #                             wsel_ds = v_wsel_ds,
#         #                             flow = v_flow))

#endregion -------------------------------------------------------------------------------------------------
