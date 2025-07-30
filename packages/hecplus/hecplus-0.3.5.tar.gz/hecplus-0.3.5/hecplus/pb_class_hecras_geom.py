#region Libraries

#%%
import pandas as pd
import numpy as np

from typing import Any

from .pb_functions_hec import *
from .pb_functions_hecras import *
from .pb_class_hecras_plan import *
from .pb_class_hecras_flow_unsteady import *

import dsplus as ds

# pd.set_option('display.max_columns', None)
pd.options.display.max_columns = None
pd.options.display.max_rows = 8
# pd.options.display.max_colwidth=None

#endregion -------------------------------------------------------------------------------------------------
#region Class

#%%
class HecRas_Geom:
    name = None
    name_geom = None
    file_ras_geom = None
    file_ras_geom_hdf = None
    content_ras_geom = None

    v_hdf_groups = None
    v_hdf_datasets = None

    sp_cl = None
    df_cl_attributes = None
    df_cl_xy = None

    sp_xs = None
    df_xs_attributes = None
    df_xs_xy = None
    df_xs_staelev = None
    df_xs_manning = None
    df_xs_ineffective = None
    df_xs_blocked = None
    sp_xs_ineffective = None
    sp_xs_blocked = None

    sp_struct = None
    df_struct_xy = None
    df_struct_attributes = None
    df_struct_coeff = None
    df_struct_staelev = None
    df_struct_pier_attrib = None
    df_struct_pier_data = None
    df_struct_abut_data = None
    df_struct_culvert_attrib = None
    df_struct_culvert_barrel_attrib = None
    df_struct_culvert_barrel_xy = None

    sp_2d_area_pts = None
    sp_2d_area = None
    sp_breaklines = None
    sp_refinements = None
    sp_cell_poly = None

    df_ref_point_attributes = None
    df_ref_point_xy = None
    sp_ref_points = None
    
    df_ref_line_attributes = None
    df_ref_line_xy = None
    sp_ref_lines = None

    df_bc_attributes = None
    df_bc_xy = None
    sp_bc = None
    
    crs = None #TODO

    def __init__(self, name = '') -> None:
        self.name = name

    def set_crs(self, crs: Any) -> None:
        '''Update coordinate system.

        Args:
            crs (Any): Coordinate system to use (proj4string, epsg code, etc.)

        Notes:
            - Does not update all current geodataframes. Only applies to newer geodataframes.
        '''
        self.crs = crs
    
    def read_from_file(self, file_ras_geom: str):
        '''Read geometry file. Updates 'content_ras_geom', 'file_ras_geom', and 'file_ras_geom_hdf'.

        Args:
            file_ras_geom (str): Geometry filename.

        Examples:
            >>> read_from_file('geom.g01')
        '''
        content_ras_geom = ds.os_read_lines(file_ras_geom)

        file_ras_geom_hdf = file_ras_geom + '.hdf'

        v_hdf_groups = hdf_read_groups(file_ras_geom_hdf)
        v_hdf_datasets = hdf_read_datasets(file_ras_geom_hdf)

        self.content_ras_geom = content_ras_geom
        self.file_ras_geom = file_ras_geom
        self.file_ras_geom_hdf = file_ras_geom_hdf
        self.v_hdf_groups = v_hdf_groups
        self.v_hdf_datasets = v_hdf_datasets

    def read_cl(self):
        '''Read centerlines. Updates 'sp_cl', 'df_cl_attributes', and 'df_cl_xy'.
        '''
        file_ras_geom_hdf = self.file_ras_geom_hdf
        v_hdf_datasets = self.v_hdf_datasets
        crs = self.crs

        if v_hdf_datasets.str.contains('Geometry/River Centerlines/Attributes').any():
            df_cl_attributes = hdf_read_df(file_ras_geom_hdf, 'Geometry/River Centerlines/Attributes').reset_index()
            df_cl_xy = hdf_read_info_value(file_ras_geom_hdf, 
                                        'Geometry/River Centerlines/Polyline Info', 
                                        'Geometry/River Centerlines/Polyline Points',
                                        col_names_values=['x', 'y'],
                                        df_attributes=df_cl_attributes.loc[:, 'index':'Reach Name'])
            sp_cl = ds.sp_lines_from_df_xy(df_cl_xy, column_group='index_info', keep_columns=True)

            if crs is not None:
                sp_cl.crs = crs

            self.sp_cl = sp_cl
            self.df_cl_attributes = df_cl_attributes
            self.df_cl_xy = df_cl_xy

    def read_xs(self):
        '''Read cross-sections. Updates 'sp_xs', 'df_xs_attributes', 'df_xs_xy', 'df_xs_staelev', 'df_xs_manning', 'df_xs_ineffective', 'df_xs_blocked', 'sp_xs_ineffective', and 'sp_xs_blocked'.
        '''
        file_ras_geom_hdf = self.file_ras_geom_hdf
        v_hdf_datasets = self.v_hdf_datasets
        crs = self.crs

        if v_hdf_datasets.str.contains('Geometry/Cross Sections/Attributes').any():
            df_xs_attributes = hdf_read_df(file_ras_geom_hdf, 'Geometry/Cross Sections/Attributes').reset_index()

            temp_df_xs_attributes = df_xs_attributes.loc[:, 'index':'RS']

            df_xs_xy = hdf_read_info_value(file_ras_geom_hdf, 
                                        'Geometry/Cross Sections/Polyline Info', 
                                        'Geometry/Cross Sections/Polyline Points',
                                        col_names_values=['x', 'y'],
                                        df_attributes=temp_df_xs_attributes)
            sp_xs = ds.sp_lines_from_df_xy(df_xs_xy, column_group='index_info', keep_columns=True)

            if v_hdf_datasets.str.contains("Geometry/Cross Sections/Station Elevation Values").any():
                df_xs_staelev = hdf_read_info_value(file_ras_geom_hdf, 
                                                    "Geometry/Cross Sections/Station Elevation Info", 
                                                    "Geometry/Cross Sections/Station Elevation Values",
                                                    col_names_values=['Sta', 'Elevation'],
                                                    df_attributes=temp_df_xs_attributes)
            else:
                df_xs_staelev = None

            df_xs_manning = hdf_read_info_value(file_ras_geom_hdf, 
                                                "Geometry/Cross Sections/Manning's n Info", 
                                                "Geometry/Cross Sections/Manning's n Values",
                                                col_names_values=['Sta', 'Manning n'],
                                                df_attributes=temp_df_xs_attributes)

            if v_hdf_datasets.str.contains("Geometry/Cross Sections/Ineffective Blocks").any():
                df_xs_ineffective = hdf_read_info_value(file_ras_geom_hdf, 
                                                        "Geometry/Cross Sections/Ineffective Info", 
                                                        "Geometry/Cross Sections/Ineffective Blocks",
                                                        df_attributes=temp_df_xs_attributes)
            else:
                df_xs_ineffective = None

            if v_hdf_datasets.str.contains("Geometry/Cross Sections/Obstruction Blocks").any():
                df_xs_blocked = hdf_read_info_value(file_ras_geom_hdf, 
                                                    "Geometry/Cross Sections/Obstruction Info", 
                                                    "Geometry/Cross Sections/Obstruction Blocks",
                                                    df_attributes=temp_df_xs_attributes)
            else:
                df_xs_blocked = None

            if v_hdf_datasets.str.contains("Geometry/Ineffective Flow Areas/Attributes").any():
                df_xs_ineffective_attributes = hdf_read_df(file_ras_geom_hdf, 'Geometry/Ineffective Flow Areas/Attributes').reset_index()
                df_xs_ineffective_xy = hdf_read_info_value(file_ras_geom_hdf, 
                                                           "Geometry/Ineffective Flow Areas/Polygon Info", 
                                                           "Geometry/Ineffective Flow Areas/Polygon Points",
                                                           col_names_values=['x', 'y', 'Elev'],
                                                           df_attributes=df_xs_ineffective_attributes)
                sp_xs_ineffective = df_xs_ineffective_xy\
                    .drop('Elev', axis = 1)\
                    .pipe(ds.sp_polygons_from_df_xy, column_group = 'index_info', keep_columns = True)
            else:
                sp_xs_ineffective = None

            if v_hdf_datasets.str.contains("Geometry/Blocked Obstruction/Attributes").any():
                df_xs_blocked_attributes = hdf_read_df(file_ras_geom_hdf, 'Geometry/Blocked Obstruction/Attributes').reset_index()
                df_xs_blocked_xy = hdf_read_info_value(file_ras_geom_hdf, 
                                                       "Geometry/Blocked Obstruction/Polygon Info", 
                                                       "Geometry/Blocked Obstruction/Polygon Points",
                                                       col_names_values=['x', 'y', 'Elev'],
                                                       df_attributes=df_xs_blocked_attributes)
                sp_xs_blocked = df_xs_blocked_xy\
                    .drop('Elev', axis = 1)\
                    .pipe(ds.sp_polygons_from_df_xy, column_group = 'index_info', keep_columns = True)
            else:
                sp_xs_blocked = None

            if crs is not None:
                sp_xs.crs = crs

            self.sp_xs = sp_xs
            self.df_xs_attributes = df_xs_attributes
            self.df_xs_xy = df_xs_xy
            self.df_xs_staelev = df_xs_staelev
            self.df_xs_manning = df_xs_manning
            self.df_xs_ineffective = df_xs_ineffective
            self.df_xs_blocked = df_xs_blocked
            self.sp_xs_ineffective = sp_xs_ineffective
            self.sp_xs_blocked = sp_xs_blocked

    def read_structures(self):
        '''Read structures. Updates 'sp_struct', 'df_struct_xy', 'df_struct_attributes', 'df_struct_coeff', 'df_struct_staelev', 'df_struct_pier_attrib', 'df_struct_pier_data', 'df_struct_abut_data', 'df_struct_culvert_attrib', 'df_struct_culvert_barrel_attrib', and 'df_struct_culvert_barrel_xy'.
        '''
        file_ras_geom_hdf = self.file_ras_geom_hdf
        v_hdf_datasets = self.v_hdf_datasets
        crs = self.crs

        if v_hdf_datasets.str.contains('Geometry/Structures/Attributes').any():
            df_struct_attributes = hdf_read_df(file_ras_geom_hdf, 'Geometry/Structures/Attributes').reset_index()
            # temp_df_struct_attributes = df_struct_attributes.pipe(lambda x: ds.pd_select_simple(x, ['index', *pd_cols_archive(x, 'River', 'Groupname')], remaining=False))
            temp_df_struct_attributes = df_struct_attributes.pipe(lambda x: ds.pd_select_simple(x, ['index', *ds.pd_cols(x, 'River:Groupname')], remaining=False))

            df_struct_info = hdf_read_df(file_ras_geom_hdf, 'Geometry/Structures/Table Info')

            if v_hdf_datasets.str.contains('Geometry/Structures/Centerline Points').any():
                df_struct_xy = hdf_read_info_value(file_ras_geom_hdf,
                                                'Geometry/Structures/Centerline Info',
                                                'Geometry/Structures/Centerline Points',
                                                col_names_values=['x', 'y'],
                                                df_attributes=temp_df_struct_attributes)            
                sp_struct = ds.sp_lines_from_df_xy(df_struct_xy, column_group='index_info', keep_columns=True)

                if crs is not None:
                    sp_struct.crs = crs
            else:
                df_struct_xy = None
                sp_struct = None

            df_struct_coeff = hdf_read_df(file_ras_geom_hdf, 'Geometry/Structures/Bridge Coefficient Attributes')
            df_struct_coeff = df_struct_coeff\
                .merge(temp_df_struct_attributes, how='left', left_on='Structure ID', right_on='index')\
                .pipe(ds.pd_select_simple, cols_before = ['Structure ID', *temp_df_struct_attributes.columns])        

            if v_hdf_datasets.str.contains('Geometry/Structures/Profile Data').any():
                temp_df_profile_1 = df_struct_info[['Centerline Profile (Index)', 'Centerline Profile (Count)']].set_axis(['index_start', 'count'], axis=1).assign(type = 'Centerline')
                temp_df_profile_2 = df_struct_info[['US XS Profile (Index)', 'US XS Profile (Count)']].set_axis(['index_start', 'count'], axis=1).assign(type = 'US XS')
                temp_df_profile_3 = df_struct_info[['US BR Profile (Index)', 'US BR Profile (Count)']].set_axis(['index_start', 'count'], axis=1).assign(type = 'US BR')
                temp_df_profile_4 = df_struct_info[['US BR Weir Profile (Index)', 'US BR Weir Profile (Count)']].set_axis(['index_start', 'count'], axis=1).assign(type = 'US BR Weir')
                temp_df_profile_5 = df_struct_info[['US BR Lid Profile (Index)', 'US BR Lid Profile (Count)']].set_axis(['index_start', 'count'], axis=1).assign(type = 'US BR Lid')
                temp_df_profile_6 = df_struct_info[['DS XS Profile (Index)', 'DS XS Profile (Count)']].set_axis(['index_start', 'count'], axis=1).assign(type = 'DS XS')
                temp_df_profile_7 = df_struct_info[['DS BR Profile (Index)', 'DS BR Profile (Count)']].set_axis(['index_start', 'count'], axis=1).assign(type = 'DS BR')
                temp_df_profile_8 = df_struct_info[['DS BR Weir Profile (Index)', 'DS BR Weir Profile (Count)']].set_axis(['index_start', 'count'], axis=1).assign(type = 'DS BR Weir')
                temp_df_profile_9 = df_struct_info[['DS BR Lid Profile (Index)', 'DS BR Lid Profile (Count)']].set_axis(['index_start', 'count'], axis=1).assign(type = 'DS BR Lid')        
                temp_df_profile_info = pd.concat([temp_df_profile_1, temp_df_profile_2, temp_df_profile_3, temp_df_profile_4, temp_df_profile_5, temp_df_profile_6, temp_df_profile_7, temp_df_profile_8, temp_df_profile_9]).sort_values(['index_start'])
                temp_df_profile_values = hdf_read_df(file_ras_geom_hdf, 'Geometry/Structures/Profile Data').set_axis(['Sta', 'Elevation'], axis=1)
                df_struct_staelev = hdf_read_info_value(df_info=temp_df_profile_info,
                                                        df_values=temp_df_profile_values,
                                                        df_attributes=temp_df_struct_attributes,
                                                        info_columns_to_keep = 'type')
            else:
                df_struct_staelev = None

            if v_hdf_datasets.str.contains('Geometry/Structures/Pier Attributes').any():
                df_struct_pier_attrib = hdf_read_df(file_ras_geom_hdf, 'Geometry/Structures/Pier Attributes')
                df_struct_pier_attrib = df_struct_pier_attrib\
                    .merge(temp_df_struct_attributes, how='left', left_on='Structure ID', right_on='index')\
                    .pipe(ds.pd_select_simple, cols_before = ['Structure ID', *temp_df_struct_attributes.columns])\
                    .drop('index', axis=1)
            else:
                df_struct_pier_attrib = None

            if v_hdf_datasets.str.contains('Geometry/Structures/Pier Data').any():
                temp_df_profile_1 = df_struct_pier_attrib[['US Profile (Index)', 'US Profile (Count)']].set_axis(['index_start', 'count'], axis=1).assign(type = 'US')
                temp_df_profile_2 = df_struct_pier_attrib[['DS Profile (Index)', 'DS Profile (Count)']].set_axis(['index_start', 'count'], axis=1).assign(type = 'DS')
                temp_df_profile_info = pd.concat([temp_df_profile_1, temp_df_profile_2]).sort_values(['index_start'])
                temp_df_profile_values = hdf_read_df(file_ras_geom_hdf, 'Geometry/Structures/Pier Data').set_axis(['Width', 'Elevation'], axis=1)
                df_struct_pier_data = hdf_read_info_value(df_info=temp_df_profile_info,
                                                        df_values=temp_df_profile_values,
                                                        df_attributes=df_struct_pier_attrib.loc[:, 'Structure ID':'Groupname'].reset_index(),
                                                        info_columns_to_keep='type')
            else:
                df_struct_pier_data = None

            if v_hdf_datasets.str.contains('Geometry/Structures/Abutment Attributes').any():
                df_struct_abut_attrib = hdf_read_df(file_ras_geom_hdf, 'Geometry/Structures/Abutment Attributes')
                df_struct_abut_attrib = df_struct_abut_attrib\
                    .merge(temp_df_struct_attributes, how='left', left_on='Structure ID', right_on='index')\
                    .pipe(ds.pd_select_simple, cols_before = ['Structure ID', *temp_df_struct_attributes.columns])\
                    .drop('index', axis=1)
                
                temp_df_profile_1 = df_struct_abut_attrib[['US Profile (Index)', 'US Profile (Count)']].set_axis(['index_start', 'count'], axis=1).assign(type = 'US')
                temp_df_profile_2 = df_struct_abut_attrib[['DS Profile (Index)', 'DS Profile (Count)']].set_axis(['index_start', 'count'], axis=1).assign(type = 'DS')
                temp_df_profile_info = pd.concat([temp_df_profile_1, temp_df_profile_2]).sort_values(['index_start'])
                temp_df_profile_values = hdf_read_df(file_ras_geom_hdf, 'Geometry/Structures/Abutment Data').set_axis(['Sta', 'Elevation'], axis=1)
                df_struct_abut_data = hdf_read_info_value(df_info=temp_df_profile_info,
                                                        df_values=temp_df_profile_values,
                                                        df_attributes=df_struct_abut_attrib.loc[:, 'Structure ID':'Groupname'].reset_index(),
                                                        info_columns_to_keep='type')
            else:
                df_struct_abut_attrib = None
                df_struct_abut_data = None
            
            if v_hdf_datasets.str.contains('Geometry/Structures/Culvert Groups/Attributes').any():
                df_struct_culvert_attrib = hdf_read_df(file_ras_geom_hdf, 'Geometry/Structures/Culvert Groups/Attributes')
                df_struct_culvert_attrib = df_struct_culvert_attrib\
                    .merge(temp_df_struct_attributes, how='left', left_on='Structure ID', right_on='index')\
                    .pipe(ds.pd_select_simple, cols_before = ['Structure ID', *temp_df_struct_attributes.columns])\
                    .drop('index', axis=1)
            
                temp_df_struct_culvert_attrib = df_struct_culvert_attrib[['Name']].reset_index()
                df_struct_culvert_barrel_attrib = hdf_read_df(file_ras_geom_hdf, 'Geometry/Structures/Culvert Groups/Barrels/Attributes')
                df_struct_culvert_barrel_attrib = df_struct_culvert_barrel_attrib\
                    .merge(temp_df_struct_attributes, how='left', left_on='Structure ID', right_on='index')\
                    .pipe(ds.pd_select_simple, cols_before = ['Structure ID', *temp_df_struct_attributes.columns])\
                    .drop('index', axis=1)\
                    .merge(temp_df_struct_culvert_attrib.rename(columns={'Name': 'Name_Group'}), how='left', left_on='Culvert Group ID', right_on='index')\
                    .pipe(ds.pd_select_simple, cols_before = ['Structure ID', *temp_df_struct_attributes.columns, 'Culvert Group ID', *temp_df_struct_culvert_attrib.rename(columns={'Name': 'Name_Group'})])\
                    .drop('index', axis=1)
                
                if v_hdf_datasets.str.contains('Geometry/Structures/Culvert Groups/Barrels/Centerline Points').any():
                    df_struct_culvert_barrel_xy = hdf_read_info_value(file_ras_geom_hdf,
                                        'Geometry/Structures/Culvert Groups/Barrels/Centerline Info',
                                        'Geometry/Structures/Culvert Groups/Barrels/Centerline Points',
                                        col_names_values=['x', 'y'],
                                        df_attributes=df_struct_culvert_barrel_attrib.loc[:, 'Structure ID':'Name'].reset_index())
                else:
                    df_struct_culvert_barrel_xy = None
            else:
                df_struct_culvert_attrib = None
                df_struct_culvert_barrel_attrib = None
                df_struct_culvert_barrel_xy = None
                   
            self.sp_struct = sp_struct
            self.df_struct_xy = df_struct_xy
            self.df_struct_attributes = df_struct_attributes
            self.df_struct_coeff = df_struct_coeff
            self.df_struct_staelev = df_struct_staelev
            self.df_struct_pier_attrib = df_struct_pier_attrib
            self.df_struct_pier_data = df_struct_pier_data
            self.df_struct_abut_data = df_struct_abut_data
            self.df_struct_culvert_attrib = df_struct_culvert_attrib
            self.df_struct_culvert_barrel_attrib = df_struct_culvert_barrel_attrib
            self.df_struct_culvert_barrel_xy = df_struct_culvert_barrel_xy

    def read_2d_area(self):
        '''Read 2d flow area. Returns 'sp_2d_area_pts', 'sp_2d_area', 'sp_breaklines', and 'sp_refinements'.
        '''
        file_ras_geom_hdf = self.file_ras_geom_hdf
        v_hdf_datasets = self.v_hdf_datasets
        crs = self.crs

        if v_hdf_datasets.str.contains('Geometry/2D Flow Areas/Attributes').any():
            df_2d_area_attributes = hdf_read_df(file_ras_geom_hdf, 'Geometry/2D Flow Areas/Attributes').reset_index()
            df_2d_area_xy = hdf_read_info_value(file_hdf=file_ras_geom_hdf, 
                                                pathname_info='Geometry/2D Flow Areas/Polygon Info', 
                                                pathname_values='Geometry/2D Flow Areas/Polygon Points',
                                                col_names_values=['x', 'y'],
                                                df_attributes=df_2d_area_attributes.loc[:, 'index':'Name'])
            sp_2d_area = ds.sp_polygons_from_df_xy(df_2d_area_xy, column_group='index_info', keep_columns=True)

            df_2d_area_pts_xy = hdf_read_info_value(file_ras_geom_hdf, 
                                                    'Geometry/2D Flow Areas/Cell Info', 
                                                    'Geometry/2D Flow Areas/Cell Points',
                                                     col_names_values=['x', 'y'],
                                                     df_attributes=df_2d_area_attributes.loc[:, 'index':'Name'])
            
            sp_2d_area_pts = ds.sp_points_from_df_xy(df_2d_area_pts_xy)

            if crs is not None:
                sp_2d_area.crs = crs
                sp_2d_area.crs = crs
        else:
            sp_2d_area = None
            sp_2d_area_pts = None

        if v_hdf_datasets.str.contains('Geometry/2D Flow Area Break Lines/Attributes').any():
            df_breakline_attributes = hdf_read_df(file_ras_geom_hdf, 'Geometry/2D Flow Area Break Lines/Attributes').reset_index()
            df_breakline_xy = hdf_read_info_value(file_ras_geom_hdf, 
                                        'Geometry/2D Flow Area Break Lines/Polyline Info', 
                                        'Geometry/2D Flow Area Break Lines/Polyline Points',
                                        col_names_values=['x', 'y'],
                                        df_attributes=df_breakline_attributes.loc[:, 'index':'Name'])
            sp_breaklines = ds.sp_lines_from_df_xy(df_breakline_xy, column_group='index_info', keep_columns=True)

            if crs is not None:
                sp_breaklines.crs = crs
        else:
            sp_breaklines = None
        
        if v_hdf_datasets.str.contains('Geometry/2D Flow Area Refinement Regions/Attributes').any():
            df_refinement_attributes = hdf_read_df(file_ras_geom_hdf, 'Geometry/2D Flow Area Refinement Regions/Attributes').reset_index()
            df_refinement_xy = hdf_read_info_value(file_ras_geom_hdf, 
                                        'Geometry/2D Flow Area Refinement Regions/Polygon Info', 
                                        'Geometry/2D Flow Area Refinement Regions/Polygon Points',
                                        col_names_values=['x', 'y'],
                                        df_attributes=df_refinement_attributes.loc[:, 'index':'Name'])
            sp_refinements = ds.sp_polygons_from_df_xy(df_refinement_xy, column_group='index_info', keep_columns=True)
            
            if crs is not None:
                sp_refinements.crs = crs
        else:
            sp_refinements = None

        self.sp_2d_area_pts = sp_2d_area_pts
        self.sp_2d_area = sp_2d_area
        self.sp_breaklines = sp_breaklines
        self.sp_refinements = sp_refinements
    
    def read_ref_points(self):
        '''Read reference points. Updates 'df_ref_point_attributes', 'df_ref_point_xy', and 'sp_ref_points'.
        '''
        file_ras_geom_hdf = self.file_ras_geom_hdf
        v_hdf_datasets = self.v_hdf_datasets
        crs = self.crs
        
        if v_hdf_datasets.str.contains('Geometry/Reference Points/Attributes').any():
            df_ref_point_attributes = hdf_read_df(file_ras_geom_hdf, 'Geometry/Reference Points/Attributes').reset_index()
            df_ref_point_attributes = df_ref_point_attributes.assign(id = lambda x: ds.str_concat(x['Name'], '|', x['SA/2D'])).pipe(ds.pd_select_simple, ['id'])
            df_ref_point_xy = hdf_read_df(file_ras_geom_hdf, 'Geometry/Reference Points/Points').reset_index()
            df_ref_point_xy = df_ref_point_xy\
                .set_axis(['index', 'x', 'y'], axis=1)\
                .pipe(ds.pd_concat_cols, df_ref_point_attributes[['id', 'Name', 'SA/2D']])\
                .pipe(ds.pd_select_simple, ['id', 'Name', 'SA/2D'])
            sp_ref_points = ds.sp_points_from_df_xy(df_ref_point_xy)

            if crs is not None:
                sp_ref_points.crs = crs

            self.df_ref_point_attributes = df_ref_point_attributes
            self.df_ref_point_xy = df_ref_point_xy
            self.sp_ref_points = sp_ref_points

    def read_ref_lines(self):
        '''Read reference points. Updates 'df_ref_line_attributes', 'df_ref_line_xy', and 'sp_ref_lines'.
        '''
        file_ras_geom_hdf = self.file_ras_geom_hdf
        v_hdf_datasets = self.v_hdf_datasets
        crs = self.crs
        
        if v_hdf_datasets.str.contains('Geometry/Reference Lines/Attributes').any():
            df_ref_line_attributes = hdf_read_df(file_ras_geom_hdf, 'Geometry/Reference Lines/Attributes').reset_index()
            df_ref_line_attributes = df_ref_line_attributes.assign(id = lambda x: ds.str_concat(x['Name'], '|', x['SA-2D'])).pipe(ds.pd_select_simple, ['id'])
            df_ref_line_xy = hdf_read_info_value(file_ras_geom_hdf, 
                                                 'Geometry/Reference Lines/Polyline Info', 
                                                 'Geometry/Reference Lines/Polyline Points',
                                                 col_names_values=['x', 'y'],
                                                 df_attributes=df_ref_line_attributes.loc[:, 'id':'SA-2D'])
            sp_ref_lines = ds.sp_lines_from_df_xy(df_ref_line_xy, column_group='index_info', keep_columns=True)

            if crs is not None:
                sp_ref_lines.crs = crs

            self.df_ref_line_attributes = df_ref_line_attributes
            self.df_ref_line_xy = df_ref_line_xy
            self.sp_ref_lines = sp_ref_lines

    def read_bc(self):
        '''Read boundary condtion lines. Updates 'df_bc_attributes', 'df_bc_xy', and 'sp_bc'.
        '''
        file_ras_geom_hdf = self.file_ras_geom_hdf
        v_hdf_datasets = self.v_hdf_datasets
        crs = self.crs
        
        if v_hdf_datasets.str.contains('Geometry/Boundary Condition Lines/Attributes').any():
            df_bc_attributes = hdf_read_df(file_ras_geom_hdf, 'Geometry/Boundary Condition Lines/Attributes').reset_index()
            df_bc_attributes = df_bc_attributes.assign(id = lambda x: ds.str_concat(x['Name'], '|', x['SA-2D'])).pipe(ds.pd_select_simple, ['id'])
            df_bc_xy = hdf_read_info_value(file_ras_geom_hdf, 
                                           'Geometry/Boundary Condition Lines/Polyline Info', 
                                           'Geometry/Boundary Condition Lines/Polyline Points',
                                           col_names_values=['x', 'y'],
                                           df_attributes=df_bc_attributes.loc[:, 'id':'Type'])
            sp_bc = ds.sp_lines_from_df_xy(df_bc_xy, column_group='index_info', keep_columns=True)

            if crs is not None:
                sp_bc.crs = crs

            self.df_bc_attributes = df_bc_attributes
            self.df_bc_xy = df_bc_xy
            self.sp_bc = sp_bc

    def read_cell_faces(self):
        '''Read mesh cell faces. Updates 'sp_cell_faces'.
        '''
        file_ras_geom_hdf = self.file_ras_geom_hdf
        v_hdf_datasets = self.v_hdf_datasets
        crs = self.crs
        sp_2d_area = self.sp_2d_area
        
        v_perimeters = sp_2d_area['Name']
        sp_cell_poly = None
        df_face_line_xy = pd.DataFrame()
        for name_perimeter in v_perimeters:
            if v_hdf_datasets.str.contains(f'Geometry/2D Flow Areas/{name_perimeter}/FacePoints Coordinate').any():
                df_face_xy = hdf_read_df(file_ras_geom_hdf, f'Geometry/2D Flow Areas/{name_perimeter}/FacePoints Coordinate').reset_index()
                df_face_info = hdf_read_df(file_ras_geom_hdf, f'Geometry/2D Flow Areas/{name_perimeter}/Cells Face and Orientation Info').reset_index()
                df_face_join = hdf_read_df(file_ras_geom_hdf, f'Geometry/2D Flow Areas/{name_perimeter}/Cells FacePoint Indexes').reset_index()

                df_face_info = \
                (df_face_info
                    .set_axis(['index', 'cum', 'count'], axis=1)
                    .loc[lambda _: _['count'] > 1]
                )

                df_face_join_main = \
                (df_face_join
                    .loc[lambda _: _['index'].isin(df_face_info['index'])]
                    .melt(id_vars='index', var_name='sn', value_name='index_xy')
                    .sort_values(['index', 'sn'])
                    .loc[lambda _: _['index_xy'] != -1]
                    .merge(df_face_xy.rename(columns={'index': 'index_xy', 0: 'x', 1: 'y'}), on='index_xy', how='left')
                )

                current_sp_cell_poly = ds.sp_polygons_from_df_xy(df_face_join_main[['index', 'x', 'y']], column_group='index', crs=crs).assign(name_2d_area = name_perimeter)

                if sp_cell_poly is None:
                    sp_cell_poly = current_sp_cell_poly
                else:
                    sp_cell_poly = sp_cell_poly.pipe(ds.pd_concat_rows, current_sp_cell_poly)

                current_df_face_xy = \
                (df_face_join_main
                    [['x', 'y']]
                    .assign(x_next = lambda _: _['x'].shift(-1))
                    .assign(y_next = lambda _: _['y'].shift(-1))
                    .dropna()
                )

                df_face_line_xy = df_face_line_xy.pipe(ds.pd_concat_rows, current_df_face_xy)

        if df_face_line_xy is not None:
            (df_face_line_xy
                .drop_duplicates()
                .assign(rn = lambda _: np.arange(_.shape[0]))
                .melt()
            )
            pass

        self.sp_cell_poly = sp_cell_poly
    
#endregion -------------------------------------------------------------------------------------------------
#region Notes

# HEC-RAS 6.3.1
# Completed attributes
'Geometry/2D Flow Area Break Lines/Attributes'
'Geometry/2D Flow Area Break Lines/Polyline Info'
'Geometry/2D Flow Area Break Lines/Polyline Points'

'Geometry/2D Flow Area Refinement Regions/Attributes'
'Geometry/2D Flow Area Refinement Regions/Polygon Info'
'Geometry/2D Flow Area Refinement Regions/Polygon Points'

'Geometry/2D Flow Areas/Attributes'
'Geometry/2D Flow Areas/Cell Info'
'Geometry/2D Flow Areas/Cell Points'
'Geometry/2D Flow Areas/Polygon Info'
'Geometry/2D Flow Areas/Polygon Points'

'Geometry/Cross Sections/Attributes'
"Geometry/Cross Sections/Ineffective Info"
"Geometry/Cross Sections/Ineffective Blocks"
"Geometry/Cross Sections/Manning's n Info"
"Geometry/Cross Sections/Manning's n Values"
"Geometry/Cross Sections/Obstruction Info"
"Geometry/Cross Sections/Obstruction Blocks"
'Geometry/Cross Sections/Polyline Info'
'Geometry/Cross Sections/Polyline Points'
"Geometry/Cross Sections/Station Elevation Info"
"Geometry/Cross Sections/Station Elevation Values"

'Geometry/Reference Lines/Attributes'
'Geometry/Reference Lines/Polyline Info'
'Geometry/Reference Lines/Polyline Points'

'Geometry/Reference Points/Attributes'
'Geometry/Reference Points/Points'

'Geometry/River Centerlines/Attributes'
'Geometry/River Centerlines/Polyline Info'
'Geometry/River Centerlines/Polyline Points'

'Geometry/Structures/Abutment Attributes'
'Geometry/Structures/Abutment Data'
'Geometry/Structures/Attributes'
'Geometry/Structures/Bridge Coefficient Attributes'
'Geometry/Structures/Centerline Info'
'Geometry/Structures/Centerline Points'
'Geometry/Structures/Culvert Groups/Attributes'
'Geometry/Structures/Culvert Groups/Barrels/Attributes'
'Geometry/Structures/Culvert Groups/Barrels/Centerline Info'
'Geometry/Structures/Culvert Groups/Barrels/Centerline Points'
'Geometry/Structures/Pier Attributes'
'Geometry/Structures/Pier Data'
'Geometry/Structures/Profile Data'
'Geometry/Structures/Table Info'

#endregion -------------------------------------------------------------------------------------------------
