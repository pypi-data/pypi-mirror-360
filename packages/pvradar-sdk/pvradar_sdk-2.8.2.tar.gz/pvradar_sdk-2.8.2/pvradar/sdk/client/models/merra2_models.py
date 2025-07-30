from typing import Any, Annotated as A, TypeVar
import pandas as pd
import numpy as np
from pydantic import Field as F

from ...common.exceptions import DataUnavailableError
from ..api_query import Query
from ..client import PvradarClient
from pvlib.location import Location
from ...modeling.decorators import datasource, standard_resource_type
from ...modeling import R
from ...modeling.utils import auto_attr_table, convert_series_unit, rate_to_cumulative, ureg
from ..pvradar_resources import PvradarResourceType, SeriesConfigAttrs as S


# annotations redefined to account for non-standard 3h frequency
merra2_resource_annotations: dict[PvradarResourceType, Any] = {
    'air_density': A[float, F(ge=0), S(unit='kg/m^3', freq='3h')],
    'particle_mixing_ratio': A[pd.Series, F(ge=0), S(unit='kg/kg', param_names=['particle_name'], freq='3h')],
    'relative_humidity': A[float, S(resource_type='relative_humidity', unit='dimensionless', freq='3h')],
}

merra2_series_name_mapping: dict[str, PvradarResourceType | A[Any, Any]] = {
    # ----------------------------------------------------
    # MERRA2 - M2I3NVAER, merra2_aerosol_mixing_table
    #
    'AIRDENS': 'air_density',
    'BCPHILIC': 'particle_mixing_ratio',
    'BCPHOBIC': 'particle_mixing_ratio',
    'DU001': 'particle_mixing_ratio',
    'DU002': 'particle_mixing_ratio',
    'DU003': 'particle_mixing_ratio',
    'DU004': 'particle_mixing_ratio',
    'OCPHILIC': 'particle_mixing_ratio',
    'OCPHOBIC': 'particle_mixing_ratio',
    'SO4': 'particle_mixing_ratio',
    'SS001': 'particle_mixing_ratio',
    'SS002': 'particle_mixing_ratio',
    'SS003': 'particle_mixing_ratio',
    'SS004': 'particle_mixing_ratio',
    'RH': 'relative_humidity',
    # ----------------------------------------------------
    # MERRA2 - M2T1NXFLX, merra2_surface_flux_table
    #
    'PRECSNO': A[pd.Series, S(resource_type='snowfall_mass_rate', unit='kg/m^2/s', agg='mean', freq='h')],
    'PRECTOT': A[pd.Series, S(resource_type='rainfall_mass_rate', unit='kg/m^2/s', agg='mean', freq='h')],
    'PRECTOTCORR': A[pd.Series, S(resource_type='rainfall_mass_rate', unit='kg/m^2/s', agg='mean', freq='h')],
    # ----------------------------------------------------
    # MERRA2 - M2I1NXASM, merra2_meteo_table
    'T2M': A[pd.Series, S(resource_type='air_temperature', unit='degK', freq='h')],
    'U2M': A[pd.Series, S(resource_type='wind_speed', unit='m/s', agg='mean', freq='h')],
    'V2M': A[pd.Series, S(resource_type='wind_speed', unit='m/s', agg='mean', freq='h')],
    # ----------------------------------------------------
    # MERRA2 - M2T1NXLND, merra2_land_surface_table
    'SNODP': A[pd.Series, S(resource_type='snow_depth', unit='m', freq='h')],
}


def _auto_attr_table(df: pd.DataFrame) -> None:
    if df is None:
        return
    _remove_minutes_inplace(df)
    auto_attr_table(
        df,
        series_name_mapping=merra2_series_name_mapping,
        resource_annotations=merra2_resource_annotations,
    )
    for name in df:
        df[name].attrs['datasource'] = 'merra2'


def _remove_minutes_inplace(df: pd.DataFrame) -> None:
    if not len(df):
        return
    sample = df.index[0]
    if sample.minute != 0:
        df.index = df.index - pd.Timedelta(minutes=sample.minute)


# when requesting data from DB, we add 59min some tolerance to include data with minutes
# originally MERRA2 has data as 00:30, 01:30 ...
def _add_minute_tolerance(interval: pd.Interval) -> pd.Interval:
    minute = interval.right.minute
    result = pd.Interval(interval.left, interval.right + pd.Timedelta(minutes=59 - minute), closed=interval.closed)
    return result


# ----------------------------------------------------
# MERRA2 tables


@standard_resource_type(R.merra2_surface_flux_table)
@datasource('merra2')
def merra2_surface_flux_table(
    location: Location,
    interval: pd.Interval,
) -> pd.DataFrame:
    """Data extracted from MERRA2 M2T1NXFLX dataset"""
    interval = _add_minute_tolerance(interval)
    query = Query.from_site_environment(location=location, interval=interval)
    query.set_path('datasources/merra2/raw/M2T1NXFLX/csv')
    result = PvradarClient.instance().get_df(query, crop_interval=interval)
    if not len(result):
        raise DataUnavailableError(interval=interval, where='MERRA2 M2T1NXFLX dataset')
    _auto_attr_table(result)
    return result


@standard_resource_type(R.merra2_aerosol_mixing_table)
@datasource('merra2')
def merra2_aerosol_mixing_table(
    location: Location,
    interval: pd.Interval,
) -> pd.DataFrame:
    """
    Data extracted from MERRA2 M2I3NVAER dataset
    details: https://developers.google.com/earth-engine/datasets/catalog/NASA_GSFC_MERRA_aer_nv_2
    """
    interval = _add_minute_tolerance(interval)
    query = Query.from_site_environment(location=location, interval=interval)
    query.set_path('datasources/merra2/raw/M2I3NVAER/csv')
    result = PvradarClient.instance().get_df(query, crop_interval=interval)
    if not len(result):
        raise DataUnavailableError(interval=interval, where='MERRA2 M2I3NVAER dataset')
    _auto_attr_table(result)
    return result


@standard_resource_type(R.merra2_meteo_table)
@datasource('merra2')
def merra2_meteo_table(
    location: Location,
    interval: pd.Interval,
) -> pd.DataFrame:
    """
    Data extracted from M2I1NXASM dataset
    """
    interval = _add_minute_tolerance(interval)
    query = Query.from_site_environment(location=location, interval=interval)
    query.set_path('datasources/merra2/raw/M2I1NXASM/csv')
    result = PvradarClient.instance().get_df(query, crop_interval=interval)
    if not len(result):
        raise DataUnavailableError(interval=interval, where='MERRA2 M2I1NXASM dataset')
    _auto_attr_table(result)
    return result


@standard_resource_type(R.merra2_land_surface_table)
@datasource('merra2')
def merra2_land_surface_table(
    location: Location,
    interval: pd.Interval,
) -> pd.DataFrame:
    """
    Data extracted from M2T1NXLND dataset
    """
    interval = _add_minute_tolerance(interval)
    query = Query.from_site_environment(location=location, interval=interval)
    query.set_path('datasources/merra2/raw/M2T1NXLND/csv')
    result = PvradarClient.instance().get_df(query, crop_interval=interval)
    if not len(result):
        raise DataUnavailableError(interval=interval, where='MERRA2 M2T1NXLND dataset')
    _auto_attr_table(result)
    return result


# ----------------------------------------------------
# MERRA2 series (alphabetical order)

SeriesOrDf = TypeVar('T', pd.DataFrame, pd.Series)  # type: ignore


def _merra2_3h_to_1h(df: SeriesOrDf, interval: pd.Interval) -> SeriesOrDf:
    start_datetime = interval.left
    end_datetime = interval.right
    assert isinstance(start_datetime, pd.Timestamp)
    new_index = pd.date_range(start=start_datetime, end=end_datetime, freq='1h')
    df = df.reindex(new_index).interpolate().bfill()
    df.attrs['freq'] = '1h'
    return df


@standard_resource_type(R.air_density, use_default_freq=True)
@datasource('merra2')
def merra2_air_density(
    *,
    merra2_aerosol_mixing_table: A[pd.DataFrame, R.merra2_aerosol_mixing_table],
) -> pd.Series:
    return merra2_aerosol_mixing_table['AIRDENS']


@standard_resource_type(R.air_temperature, use_default_freq=True)
@datasource('merra2')
def merra2_air_temperature(
    *,
    merra2_meteo_table: A[pd.DataFrame, R.merra2_meteo_table],
) -> pd.Series:
    return convert_series_unit(merra2_meteo_table['T2M'], to_unit='degC')


@standard_resource_type(R.particle_mixing_ratio, use_default_freq=True)
@datasource('merra2')
def merra2_particle_mixing_ratio(
    *,
    merra2_aerosol_mixing_table: A[pd.DataFrame, R.merra2_aerosol_mixing_table],
    particle_name: str,
) -> pd.Series:
    if particle_name not in merra2_aerosol_mixing_table:
        raise ValueError(f'Particle {particle_name} not found in aerosol mixing table')
    return merra2_aerosol_mixing_table[particle_name]


@standard_resource_type(R.particle_volume_concentration, use_default_freq=True)
@datasource('merra2')
def merra2_particle_volume_concentration(
    *,
    merra2_aerosol_mixing_table: A[pd.DataFrame, R.merra2_aerosol_mixing_table],
    interval: pd.Interval,
    particle_name: str,
) -> pd.Series:
    if particle_name not in merra2_aerosol_mixing_table:
        raise ValueError(f'Particle {particle_name} not found in aerosol mixing table')
    mixing_ratio = merra2_aerosol_mixing_table[particle_name]
    air_density = merra2_air_density(merra2_aerosol_mixing_table=merra2_aerosol_mixing_table)
    result = mixing_ratio * air_density
    result = _merra2_3h_to_1h(result, interval)
    result.attrs['unit'] = 'kg/m^3'
    result.attrs['resource_type'] = 'particle_volume_concentration'
    return result


@standard_resource_type('pm10_volume_concentration', rename=False, use_default_freq=True)
@datasource('merra2')
def merra2_pm10_volume_concentration(
    *,
    merra2_aerosol_mixing_table: A[pd.DataFrame, R.merra2_aerosol_mixing_table],
    interval: pd.Interval,
) -> pd.Series:
    df = merra2_aerosol_mixing_table
    result = (
        1.375 * df['SO4']
        + df['BCPHOBIC']
        + df['BCPHILIC']
        + df['OCPHOBIC']
        + df['OCPHILIC']
        + df['DU001']
        + df['DU002']
        + df['DU003']
        + 0.74 * df['DU004']
        + df['SS001']
        + df['SS002']
        + df['SS003']
        + df['SS004']
    ) * df['AIRDENS']
    result = _merra2_3h_to_1h(result, interval)
    result.attrs['resource_type'] = 'pm10_volume_concentration'
    result.attrs['unit'] = 'kg/m^3'
    if 'particle_name' in result.attrs:
        del result.attrs['particle_name']
    result.name = 'pm10'
    return result


@standard_resource_type('pm2_5_volume_concentration', rename=False, use_default_freq=True)
@datasource('merra2')
def merra2_pm2_5_volume_concentration(
    *,
    merra2_aerosol_mixing_table: A[pd.DataFrame, R.merra2_aerosol_mixing_table],
    interval: pd.Interval,
) -> pd.Series:
    df = merra2_aerosol_mixing_table
    result = (
        1.375 * df['SO4']
        + df['BCPHOBIC']
        + df['BCPHILIC']
        + df['OCPHOBIC']
        + df['OCPHILIC']
        + df['DU001']
        + df['DU002']
        + 0.58 * df['DU003']
        + df['SS001']
        + df['SS002']
    ) * df['AIRDENS']
    result = _merra2_3h_to_1h(result, interval)
    result.attrs['resource_type'] = 'pm2_5_volume_concentration'
    result.attrs['unit'] = 'kg/m^3'
    if 'particle_name' in result.attrs:
        del result.attrs['particle_name']
    result.name = 'pm2_5'
    return result


@standard_resource_type(R.total_precipitation_mass_rate, use_default_freq=True)
@datasource('merra2')
def merra2_total_precipitation_mass_rate(
    merra2_surface_flux_table: A[pd.DataFrame, R.merra2_surface_flux_table],
) -> pd.Series:
    return merra2_surface_flux_table['PRECTOTCORR'].copy()


@standard_resource_type(R.total_precipitation, use_default_freq=True)
@datasource('merra2')
def merra2_total_precipitation(
    merra2_total_precipitation_mass_rate: A[
        pd.Series,
        R.total_precipitation_mass_rate(datasource='merra2', to_unit='kg/m^2/h'),
    ],
) -> pd.Series:
    # given that 1 kg/m^2 == 1mm of water, no need to convert units
    result = merra2_total_precipitation_mass_rate.copy()
    result.attrs['unit'] = 'mm'
    result.attrs['resource_type'] = 'total_precipitation'
    result.attrs['agg'] = 'sum'
    return result


@standard_resource_type(R.rainfall_mass_rate, use_default_freq=True)
@datasource('merra2')
def merra2_rainfall_mass(
    merra2_total_precipitation_mass_rate: A[pd.Series, R.total_precipitation_mass_rate(datasource='merra2')],
) -> pd.Series:
    return merra2_total_precipitation_mass_rate


@standard_resource_type(R.rainfall_rate, use_default_freq=True)
@datasource('merra2')
def merra2_rainfall_rate(
    rainfall_mass_rate: A[pd.Series, R.rainfall_mass_rate(datasource='merra2')],
) -> pd.Series:
    result = rainfall_mass_rate.copy()

    # given that 1 kg/m^2 == 1mm of water,
    # we only need to change the unit
    unit_object = ureg(rainfall_mass_rate.attrs['unit']) / ureg('kg/m^2') * ureg('mm')
    result.attrs['unit'] = str(unit_object)
    result.attrs['resource_type'] = 'rainfall_rate'
    return result


@standard_resource_type(R.rainfall, use_default_freq=True)
@datasource('merra2')
def merra2_rainfall(
    merra2_rainfall_rate: A[pd.Series, R.rainfall_rate(datasource='merra2')],
) -> pd.Series:
    result = rate_to_cumulative(merra2_rainfall_rate, resource_type='rainfall')
    return result


@standard_resource_type(R.relative_humidity, use_default_freq=True)
@datasource('merra2')
def merra2_relative_humidity(
    *,
    merra2_aerosol_mixing_table: A[pd.DataFrame, F(), R.merra2_aerosol_mixing_table],
    interval: pd.Interval,
) -> pd.Series:
    result = _merra2_3h_to_1h(merra2_aerosol_mixing_table['RH'], interval)
    return result


@standard_resource_type(R.snow_depth, use_default_freq=True)
@datasource('merra2')
def merra2_snow_depth(
    *,
    merra2_land_surface_table: A[pd.DataFrame, F(), R.merra2_land_surface_table],
) -> pd.Series:
    return merra2_land_surface_table['SNODP'].copy()


@standard_resource_type(R.snowfall_mass_rate, use_default_freq=True)
@datasource('merra2')
def merra2_snowfall_mass_rate(
    *,
    merra2_surface_flux_table: A[pd.DataFrame, F(), R.merra2_surface_flux_table],
) -> pd.Series:
    return merra2_surface_flux_table['PRECSNO'].copy()


@standard_resource_type(R.snowfall_rate, use_default_freq=True)
@datasource('merra2')
def merra2_snowfall_rate(
    *,
    snowfall_mass_rate: A[pd.Series, F(), R.snowfall_mass_rate],
    snow_density_value: A[float, F()] = 100,
) -> pd.Series:
    result = snowfall_mass_rate / snow_density_value
    unit_object = ureg(snowfall_mass_rate.attrs['unit']) / ureg('kg/m^3')
    result.attrs['unit'] = str(unit_object)
    result.attrs['resource_type'] = 'snowfall_rate'
    return result


@standard_resource_type(R.snowfall, use_default_freq=True)
@datasource('merra2')
def merra2_snowfall(
    *,
    snowfall_rate: A[pd.Series, F(), R.snowfall_rate],
) -> pd.Series:
    result = rate_to_cumulative(snowfall_rate, resource_type='snowfall')
    return result


@standard_resource_type(R.wind_speed, use_default_freq=True)
@datasource('merra2')
def merra2_wind_speed(
    *,
    merra2_meteo_table: A[pd.DataFrame, F(), R.merra2_meteo_table],
) -> pd.Series:
    u2m = merra2_meteo_table['U2M'].to_numpy()
    v2m = merra2_meteo_table['V2M'].to_numpy()
    total = np.sqrt(np.square(u2m) + np.square(v2m))
    result = pd.Series(total, index=merra2_meteo_table.index)
    result.attrs['unit'] = 'm/s'
    result.attrs['resource_type'] = 'wind_speed'
    result.attrs['agg'] = 'mean'
    return result
