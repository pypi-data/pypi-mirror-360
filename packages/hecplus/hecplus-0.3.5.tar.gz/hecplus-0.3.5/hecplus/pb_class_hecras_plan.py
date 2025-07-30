#region Libraries

#%%
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
class HecRas_Plan:
    name = None
    name_plan = None
    file_ras_plan = None
    content_ras_plan = None
    extension_geom = None
    extension_flow = None
    dttm_start = None
    dttm_end = None
    
    def __init__(self, name = '') -> None:
        self.name = name
    
    def read_from_file(self, file_ras_plan: str):
        content_ras_plan = ds.os_read_lines(file_ras_plan)

        name_plan = get_hec_text_after_header(content_ras_plan, 'Plan Title=', return_dataframe=False).iloc[0]

        extension_geom = get_hec_text_after_header(content_ras_plan, 'Geom File=', return_dataframe=False).iloc[0]
        extension_flow = get_hec_text_after_header(content_ras_plan, 'Flow File=', return_dataframe=False).iloc[0]

        df_date_str = get_hec_text_after_header(content_ras_plan, 'Simulation Date=', return_index=False, split_by=',')

        dttm_start = pd_to_datetime_hec(df_date_str.iloc[0, 0] + ' ' + df_date_str.iloc[0, 1])
        dttm_end = pd_to_datetime_hec(df_date_str.iloc[0, 2] + ' ' + df_date_str.iloc[0, 3])

        self.name_plan = name_plan
        self.file_ras_plan = file_ras_plan
        self.extension_geom = extension_geom
        self.extension_flow = extension_flow
        self.dttm_start = dttm_start
        self.dttm_end = dttm_end

#endregion -------------------------------------------------------------------------------------------------
