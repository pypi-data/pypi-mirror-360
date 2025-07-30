#region Libraries

#%%
import win32com.client as w32
from typing import Literal, Any

#endregion -------------------------------------------------------------------------------------------------
#region Class

#%%
class HecRas_Controller:
    '''Control HEC-RAS. Wrapper around HEC-RAS controller.

    Examples:
        >>> ras = HecRas_Controller('6.3.1')
        >>> ras.program_open()
        >>> ras.project_open(file_prj)
        >>> ras.plan_get_names()
        >>> ras.plan_set_current(ras.v_plan_names[0])
        >>> ras.compute_run_current_plan()
        >>> ras.project_save()
        >>> ras.project_close()
        >>> ras.program_close()
    '''
    ras = None

    name = None

    file_prj = None

    v_plan_names = None

    ras_run_msg = None

    def __init__(self, version:Literal['5.0.7', '6.3.1', '6.5', '6.6']='6.6', name:str='') -> None:
        '''Initialize with name and HEC-RAS version.

        Args:
            version (Literal[&#39;5.0.7&#39;, &#39;6.3.1&#39;, &#39;6.5&#39;], optional): HEC-RAS version. Defaults to '6.3.1'.
            name (str, optional): Name. Defaults to ''.
        '''
        if version == '5.0.7':
            version_text = '507'
        elif version == '6.3.1':
            version_text = '631'
        elif version == '6.5':
            version_text = '65'
        elif version == '6.6':
            version_text = '66'
        else:
            raise Exception('Incorrect HEC-RAS Version')

        ras = w32.Dispatch(f'RAS{version_text}.HECRASController')

        self.name = name
        self.ras = ras

    def program_open(self) -> None:
        '''Open HEC-RAS program.
        '''
        ras = self.ras

        ras.ShowRas()

    def program_close(self) -> None:
        '''Close HEC-RAS program.
        '''
        ras = self.ras

        ras.QuitRas()

    def project_open(self, file_prj:str) -> None:
        '''Open HEC-RAS project. Updates 'file_prj'.

        Args:
            file_prj (str): Project prj file.
        '''
        ras = self.ras

        ras.Project_Open(file_prj)

        self.file_prj = file_prj

    def project_close(self) -> None:
        '''Close currently open HEC-RAS project. Resets 'file_prj'.
        '''
        ras = self.ras

        ras.Project_Close()

        self.file_prj = None

    def project_save(self) -> None:
        '''Save currentluy open HEC-RAS project.
        '''
        ras = self.ras

        ras.Project_save()

    def compute_run_current_plan(self) -> tuple:
        '''Compute current HEC-RAS plan.
        ''' 
        ras = self.ras

        ras_run_msg = ras.Compute_CurrentPlan(None, None, True)

        self.ras_run_msg = ras_run_msg
        
        return ras_run_msg

    def plan_get_names(self) -> None:
        '''Get names of plans. Updates 'v_plan_names'.
        '''
        ras = self.ras

        v_plan_names = ras.Plan_Names()[1]

        self.v_plan_names = v_plan_names

    def plan_set_current(self, name_plan:str) -> None:
        '''Set current plan.

        Args:
            name_plan (str): Name of current plan. Can use 'plan_get_names()' to save plan names to 'v_plan_names'.
        '''
        ras = self.ras

        ras.Plan_SetCurrent(name_plan)

#endregion -------------------------------------------------------------------------------------------------
