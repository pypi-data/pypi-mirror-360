#region Libraries

#%%
import pandas as pd
import numpy as np

import xml.etree.cElementTree as ET

from .pb_functions_hec import *

import dsplus as ds

pd.options.display.max_columns = None
pd.options.display.max_rows = 8

#endregion -------------------------------------------------------------------------------------------------
#region Functions: XML Results

#%%
def xml_parse_basin_element(element_basin) -> pd.DataFrame:
    '''Return a dataframe of summary results for selected basin element. Mainly a backend for get_hms_results_summary().

    Args:
        element_basin (XML element): XML element.

    Returns:
        DataFrame: Dataframe of summary results.

    Examples:
        >>> content_results_xml = ET.parse(file_results_xml).getroot()
        >>> element_basin = content_results_xml.find('BasinElement[@name="S_6"]')
        >>> df = xml_parse_basin_element(element_basin)
    '''
    name = element_basin.get("name")
    type = element_basin.get("type")
    area_drainage = float(element_basin.find(".//DrainageArea").get("area"))
    qpeak = float(element_basin.find(".//StatisticMeasure[@type='Outflow Maximum']").get("value"))
    dep = float(element_basin.find(".//StatisticMeasure[@type='Outflow Depth']").get("value"))
    vol = float(element_basin.find(".//StatisticMeasure[@type='Outflow Volume']").get("value"))
    tpeak = pd_to_datetime_hec(element_basin.find(".//StatisticMeasure[@type='Outflow Maximum Time']").get("value"))
    rmse_std = ds.error_to_na(lambda: float(element_basin.find(".//StatisticMeasure[@type='Observed Flow RMSE Stdev']").get("value")))
    nse = ds.error_to_na(lambda: float(element_basin.find(".//StatisticMeasure[@type='Observed Flow Nash Sutcliffe']").get("value")))
    pbias = ds.error_to_na(lambda: float(element_basin.find(".//StatisticMeasure[@type='Observed Flow Percent Bias']").get("value")))
    r = ds.error_to_na(lambda: float(element_basin.find(".//StatisticMeasure[@type='Observed Flow Coefficient of Determination']").get("value")))
    qpeak_obs = ds.error_to_na(lambda: float(element_basin.find(".//StatisticMeasure[@type='Observed Flow Maximum']").get("value")))
    dep_obs = ds.error_to_na(lambda: float(element_basin.find(".//StatisticMeasure[@type='Observed Flow Depth']").get("value")))
    vol_obs = ds.error_to_na(lambda: float(element_basin.find(".//StatisticMeasure[@type='Observed Flow Volume']").get("value")))
    tpeak_obs = ds.error_to_na(lambda: pd_to_datetime_hec(element_basin.find(".//StatisticMeasure[@type='Observed Flow Maximum Time']").get("value")))
    dep_precip = ds.error_to_na(lambda: float(element_basin.find(".//StatisticMeasure[@type='Precipitation Total']").get("value")))
    vol_precip = ds.error_to_na(lambda: float(element_basin.find(".//StatisticMeasure[@type='Precipitation Volume']").get("value")))
    elev_pool = ds.error_to_na(lambda: float(element_basin.find(".//StatisticMeasure[@type='Pool Elevation Maximum']").get("value")))
    elev_pool_obs = ds.error_to_na(lambda: float(element_basin.find(".//StatisticMeasure[@type='Observed Pool Elevation Maximum']").get("value")))

    df = pd.DataFrame({
        'name': [name],
        'type': [type],
        'area_drainage_sqmi': [area_drainage],
        'precip_in': [dep_precip],
        'precip_acft': [vol_precip],
        'tpeak': [tpeak],
        'qpeak_cfs': [qpeak],
        'vol_in': [dep],
        'vol_acft': [vol],
        'elev_pool_ft': [elev_pool],
        'tpeak_obs': [tpeak_obs],
        'qpeak_obs_cfs': [qpeak_obs],
        'vol_obs_in': [dep_obs],
        'vol_obs_acft': [vol_obs],
        'elev_pool_obs_ft': [elev_pool_obs],
        'rmse_std': [rmse_std],
        'nse': [nse],
        'pbias': [pbias],
        'r': [r]
    })

    return (df)

#%%
def get_hms_results_summary(file_results_xml: str = None, content_results_xml = None, elements: str|list|np.ndarray|pd.Series=None) -> pd.DataFrame:
    '''Return a dataframe of summary results for all or selected basin elements.
    
    Args:
        file_results_xml: Filename of summary results file. Defaults to None.
        content_results_xml (XML element tree): XML element tree. Typically read as ET.parse(file_results_xml).getroot(). Defaults to None.
        elements (str | list | array | Series): Vector of elements to get results for. Defaults to None. If None is used, all elements will be used.
    
    Returns:
        DataFrame: Dataframe of summary results.

    Examples:
        >>> content_results_xml = ET.parse(file_results_xml).getroot()
        >>> df = get_hms_results_summary(content_results_xml)
        >>> df = get_hms_results_summary(content_results_xml, elements=['S_6', 'S_7'])
    '''
    if content_results_xml is None:
        content_results_xml = ET.parse(file_results_xml).getroot()

    df_hms_results_summary = pd.DataFrame()

    if elements is None:
        elements_basin = content_results_xml.findall('BasinElement')
    else:
        elements = ds.pd_to_series(elements).to_list()
        elements_basin = [element for element in content_results_xml.findall('BasinElement') if element.get('name') in elements]

    for element_basin in elements_basin:
        df = xml_parse_basin_element(element_basin)
        df_hms_results_summary = df_hms_results_summary.pipe(ds.pd_concat_rows, df)

    return (df_hms_results_summary)

#endregion -------------------------------------------------------------------------------------------------
