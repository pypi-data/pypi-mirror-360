#region Libraries

#%%
import pandas as pd
import numpy as np

from .pb_functions_hec import *
from .pb_class_hecras_controller import *
from .pb_class_hecras import *
from .pb_class_hecras_geom import *
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
class HecRas_Geom_review:
    def __init__(self, name = '') -> None:
        self.name = name

        folder_ras = None
        file_ras_geom = None
    
    def read_from_folder(self, folder_ras: str = None, file_ras_geom: str = None):
        self.folder_ras = folder_ras
        self.file_ras_geom = file_ras_geom

    # def 

#endregion -------------------------------------------------------------------------------------------------
