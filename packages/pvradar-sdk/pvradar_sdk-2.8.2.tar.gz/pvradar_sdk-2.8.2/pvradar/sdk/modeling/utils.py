import re
from typing import Annotated, Any, Mapping, Optional, TypeGuard, TypeVar, cast
import pandas as pd
import pint
from datetime import datetime

from ..common.pandas_utils import is_series_or_frame
from .basics import AggFunctionName, DataType, Attrs, ModelParamAttrs, SPECIAL_FREQS
from .introspection import attrs_from_annotation
from ..client.pvradar_resources import PvradarResourceType
from .resource_type_helpers import ResourceTypeClass, ResourceTypeDescriptor

ureg = pint.UnitRegistry()
ureg.define('fraction = 100 * percent = 1')


def to_series(values: pd.Series | list[float]) -> pd.Series:
    if isinstance(values, pd.Series):
        return values
    if isinstance(values, list):
        return pd.Series(values)
    raise ValueError(f'Unsupported type while converting to series: {type(values)}')


def convert_series_unit(
    series: pd.Series,
    *,
    to_unit: str,
    from_unit: Optional[str] = None,
) -> pd.Series:
    if from_unit is None:
        from_unit = series.attrs.get('unit', None)
        if from_unit is None:
            raise ValueError(f'from_unit must be provided or series must have a unit attribute on series {series.name}')
    if from_unit == to_unit:
        return series
    try:
        from_unit_object = ureg(from_unit)
        to_unit_object = ureg(to_unit)

        # TODO: we need more logic here
        # this is a workaround to speedup unit conversion
        # but it works bad for units requiring more complex conversion
        # we can built-in special case - as soon as we see suspicious unit (like degF), use the safe and slow way
        # new_series = series.apply(lambda x: (x * from_unit_object).to(to_unit_object).magnitude)
        magnitude = from_unit_object.to(to_unit_object).magnitude
        if from_unit == 'degK' or from_unit == 'degC':
            new_series = series + magnitude - 1
        else:
            new_series = series * magnitude

        new_series.attrs['unit'] = to_unit
        return new_series
    except Exception as e:
        raise ValueError(f'Failed to convert unit for {series.name}: {e}') from e


def get_time_basis(unit: str) -> str | None:
    match = re.search(r'\/(s|m|h|d|day|month|yr|year)$', unit)
    if not match:
        return None
    return match.group(1)


_resample_to_unit: dict[str, str] = {
    'min': 'minute',
    'h': 'hour',
    'H': 'hour',
    '1D': 'day',
    'd': 'day',
    '1d': 'day',
    'M': 'month',
    'ME': 'month',
    'MS': 'month',
    '1M': 'month',
}


def _pure_resample_series(
    series: pd.Series,
    scaling: Annotated[float, 'scaling factor of to/from freq, i.e. for day to hour it is 24'],
    to_freq: str,
    agg: AggFunctionName,
    is_upsampling: bool,
    *,
    interval: Optional[pd.Interval] = None,
    interpolate: Annotated[bool, 'use linear interpolation when upsampling'] = False,
) -> pd.Series:
    inherited_attrs = series.attrs.copy()
    if is_upsampling:
        if interval and interval.right > series.index[-1]:
            adjusted_right = interval.right.floor(to_freq)
            if adjusted_right > series.index[-1]:
                series = pd.concat([series, pd.Series([series.iloc[-1]], index=[adjusted_right])])
        if agg == 'sum':
            result = series.resample(to_freq).asfreq().ffill()
            result = result / scaling
        elif agg == 'mean':
            if interpolate:
                if isinstance(series, pd.DataFrame):
                    raise ValueError('upsampling interpolation is not supported for DataFrame. Did you mean pd.Series here?')
                result = series.resample(to_freq).interpolate(method='linear')
            else:
                result = series.resample(to_freq).asfreq().ffill()
        else:
            raise ValueError(f'Unsupported aggregation for interpolated upsampling: {agg}')
    else:
        if agg == 'sum':
            result = series.resample(to_freq).sum()
        elif agg == 'mean':
            result = series.resample(to_freq).mean()
        elif agg == 'min':
            result = series.resample(to_freq).min()
        elif agg == 'max':
            result = series.resample(to_freq).max()
        else:
            raise ValueError(f'Unsupported aggregation: {agg}')
    result.attrs = inherited_attrs
    return result


def resample_series(
    series: pd.Series,
    *,
    freq: str,
    agg: Optional[AggFunctionName] = None,
    interval: Optional[pd.Interval] = None,
    adjust_unit: bool = False,
    interpolate: Annotated[Optional[bool], 'use linear interpolation when upsampling'] = None,
    validate: Annotated[bool, 'ensure rate and cumulative resources are not aggregated in a wrong way'] = False,
) -> pd.Series:
    if len(series) <= 1:
        return series
    if not isinstance(series.index, pd.DatetimeIndex):
        raise ValueError('resample_series() only supports series with datetime index')

    current_agg = series.attrs.get('agg', None)
    if agg is None:
        agg = current_agg or 'mean'
    assert agg is not None

    if validate:
        if current_agg == 'mean' and agg == 'sum':
            raise ValueError('Cannot resample from rate to cumulative (mean to sum), use rate_to_cumulative() instead')
        if current_agg == 'sum' and agg == 'mean':
            raise ValueError('Conversion of cumulative to rate (sum to mean) is not supported')

    from_freq = series.attrs.get('freq', None)
    if not from_freq:
        # infer freq from just 2 elements
        if len(series) > 1:
            from_freq = pd.to_timedelta(series.index[1] - series.index[0])
        else:
            raise ValueError('series must have a freq attribute or at least 2 elements to infer freq')
    from_offset = pd.tseries.frequencies.to_offset(from_freq)
    if from_offset is None:
        raise ValueError(f'Failed to infer as a valid freq {from_freq}')

    to_freq_offset = pd.tseries.frequencies.to_offset(freq)
    if to_freq_offset is None:
        raise ValueError(f'Target freq invalid {freq}')

    if series.index.freq and to_freq_offset == from_offset:
        # no need to resample
        return series

    ## below we multiply by 12 to avoid getting 31 scaling because it happens to be a january
    reference_date = pd.Timestamp('1990-01-01')
    delta_from = (reference_date + 12 * from_offset) - reference_date
    delta_to = (reference_date + 12 * to_freq_offset) - reference_date

    is_upsampling = delta_to < delta_from
    scaling = delta_from / delta_to
    if interpolate is None:
        interpolate = is_upsampling and agg == 'mean'

    result = _pure_resample_series(series, scaling, freq, agg, is_upsampling, interpolate=interpolate, interval=interval)

    if 'unit' in result.attrs and adjust_unit:
        if agg != 'sum':
            raise ValueError('adjust_unit is only supported for sum aggregation')
        denominator = get_time_basis(series.attrs['unit'])
        if denominator:
            replacement = _resample_to_unit.get(freq, freq)
            result.attrs['unit'] = re.sub(r'\/([^/]+)$', f'/{replacement}', result.attrs['unit'])

    result.attrs['agg'] = agg
    result.attrs['freq'] = freq

    return result


def convert_by_attrs(
    value: Any,
    param_attrs: Mapping[str, Any],
    *,
    interval: Optional[pd.Interval] = None,
) -> Any:
    if 'set_unit' in param_attrs and value is not None:
        if isinstance(value, pd.Series):
            value.attrs['unit'] = param_attrs['set_unit']
        else:
            raise ValueError(f'set_unit is only supported for pd.Series values, got: {type(value)}')
    if 'to_unit' in param_attrs and value is not None:
        if isinstance(value, pd.Series):
            if 'unit' in value.attrs:
                value = convert_series_unit(value, to_unit=param_attrs['to_unit'])
            else:
                value.attrs['unit'] = param_attrs['to_unit']
        else:
            raise ValueError(f'to_unit is only supported for pd.Series values, got: {type(value)}')
    if 'to_freq' in param_attrs and value is not None:
        if param_attrs['to_freq'] not in SPECIAL_FREQS:
            if isinstance(value, pd.Series):
                value = resample_series(
                    value,
                    freq=param_attrs['to_freq'],
                    agg=param_attrs['agg'] if 'agg' in param_attrs else None,
                    interval=interval,
                )
            else:
                raise ValueError(f'to_freq is only supported for pd.Series values, got: {type(value)}')
    if 'label' in param_attrs and is_series_or_frame(value):
        value.attrs['label'] = param_attrs['label']
    return value


def datetime_from_dict(d: dict[str, Any], field_name: str) -> datetime | None:
    value = d.get(field_name)
    if value:
        assert isinstance(value, str)
        return datetime.fromisoformat(value)


def auto_attr_series(
    series: pd.Series,
    *,
    series_name_mapping: Optional[dict[Any, str | Annotated[Any, Any]]] = None,
    resource_annotations: Optional[dict[Any, Any]] = None,
    as_name: Optional[str] = None,
    **kwargs,
) -> None:
    """check if series has a known name, and if yes then add attrs unless already present"""
    if series_name_mapping is None:
        series_name_mapping = {}
    if resource_annotations is None:
        resource_annotations = {}
    assert series_name_mapping is not None
    assert resource_annotations is not None

    name = series.name if as_name is None else as_name
    resource_type = name
    if name in series_name_mapping:
        annotation = series_name_mapping[name]
        if isinstance(annotation, str):
            resource_type = series_name_mapping[name]
            annotation = resource_annotations[series_name_mapping[name]]
        attrs = attrs_from_annotation(annotation)
        if attrs and 'param_names' in attrs and 'particle_name' in attrs['param_names']:
            attrs['particle_name'] = name  # type: ignore
    elif name in resource_annotations:
        attrs = attrs_from_annotation(resource_annotations[name])
    else:
        return
    if attrs is not None:
        if 'resource_type' not in series.attrs and 'resource_type' not in attrs:
            series.attrs['resource_type'] = resource_type
        for k, v in attrs.items():
            if k == 'param_names':
                continue
            if k not in series.attrs:
                series.attrs[k] = v
        if 'agg' not in series.attrs:
            series.attrs['agg'] = 'mean'
        for k, v in kwargs.items():
            if k not in series.attrs:
                series.attrs[k] = v


def auto_attr_table(
    series: pd.DataFrame,
    *,
    series_name_mapping: dict[Any, str | Annotated[Any, Any]] = {},
    resource_annotations: dict[Any, Any],
    **kwargs,
) -> None:
    for col in series.columns:
        auto_attr_series(
            series[col],
            series_name_mapping=series_name_mapping,
            resource_annotations=resource_annotations,
            **kwargs,
        )


_rate_to_cumulative: dict[PvradarResourceType, PvradarResourceType] = {
    'rainfall_mass_rate': 'rainfall',
}

_freq_to_unit = {
    'h': 'hour',
    '1h': 'hour',
    'D': 'day',
    '1D': 'day',
    'd': 'day',
    '1d': 'day',
    'M': 'month',
    'MS': 'month',
    'ME': 'month',
    '1M': 'month',
}


def rate_to_cumulative(series: pd.Series, *, freq: Optional[str] = None, resource_type: Optional[str] = None) -> pd.Series:
    to_freq = freq
    to_resource_type = resource_type

    from_resource = series.attrs.get('resource_type')
    if not from_resource:
        raise ValueError('series must have a resource_type attribute')

    from_freq = series.attrs.get('freq', None)
    if not from_freq:
        raise ValueError('series must have a freq attribute')

    from_unit = series.attrs.get('unit', None)
    if not from_unit:
        raise ValueError('series must have a unit attribute')

    if to_resource_type is None:
        to_resource_type = _rate_to_cumulative.get(from_resource)
        if to_resource_type is None:
            raise ValueError(f'No known conversion for resource type: {from_resource}')
    if to_freq is None:
        to_freq = from_freq
    assert to_freq is not None

    if 'agg' in series.attrs and series.attrs['agg'] != 'mean':
        raise ValueError("current agg attribute if {series.attrs['agg']} but only mean is supported")

    from_time_basis = get_time_basis(from_unit)
    if from_time_basis is None:
        raise ValueError(f'Unsupported time basis in unit {from_unit}')
    to_unit = re.sub(rf'\/{from_time_basis}$', '', from_unit)

    if len(series):
        from_quantity = ureg.Quantity(1, from_time_basis)

        from_freq_unit = _freq_to_unit.get(from_freq)
        if not from_freq_unit:
            raise ValueError(f'Unsupported freq {from_freq}')
        from_freq_quantity = ureg.Quantity(1, from_freq_unit)

        normalized_series = series * float(from_freq_quantity.to(from_quantity).magnitude)
        if normalized_series is None:
            raise ValueError('after normalization the series is empty')
        resampled = normalized_series.resample(to_freq).sum()
    else:
        resampled = series.copy()

    resampled.attrs['unit'] = to_unit
    resampled.attrs['resource_type'] = to_resource_type
    resampled.attrs['freq'] = to_freq
    resampled.attrs['agg'] = 'sum'
    return resampled


SeriesOrFrame = TypeVar('SeriesOrFrame', pd.Series, pd.DataFrame)


def safe_copy(df: SeriesOrFrame) -> SeriesOrFrame:
    if isinstance(df, pd.Series):
        return df.copy()
    if isinstance(df, pd.DataFrame):
        result = pd.DataFrame()
        for col in df.columns:
            result[col] = df[col].copy()
            result[col].attrs = df[col].attrs.copy()
        result.attrs = df.attrs.copy()
        return result  # type: ignore
    raise ValueError(f'Unsupported type for safe_copy: {type(df)}')


def dtype_to_data_type(dtype: Any) -> DataType:
    if str(dtype).startswith('datetime'):
        return 'datetime'
    if dtype == 'float64':
        return 'float'
    if dtype == 'int64':
        return 'int'
    return dtype  # type: ignore


def attrs_as_descriptor_mapping(attrs: Any) -> Mapping[str, Any]:
    if isinstance(attrs, ResourceTypeDescriptor):
        return attrs.as_dict()
    elif isinstance(attrs, ResourceTypeClass):
        return {'resource_type': attrs.standard['resource_type']}
    elif isinstance(attrs, Mapping):
        return attrs
    else:
        raise ValueError(f'Unsupported type for attrs: {type(attrs)}')


def match_attrs(subject_attrs: Any, against_attrs: Any) -> bool:
    subject_attrs = attrs_as_descriptor_mapping(subject_attrs)
    against_attrs = attrs_as_descriptor_mapping(against_attrs)
    fields = ['resource_type', 'agg', 'datasource']
    for field in fields:
        if field in against_attrs:
            if subject_attrs.get(field) != against_attrs[field]:
                return False
    return True


def is_attrs_convertible(subject: Any) -> TypeGuard[Mapping[str, Any] | ResourceTypeClass | ResourceTypeDescriptor]:
    return isinstance(subject, (Mapping, ResourceTypeClass, ResourceTypeDescriptor))


def extract_model_param_attrs(attrs: Any) -> ModelParamAttrs:
    std_keys = [
        'resource_type',
        'datasource',
        'agg',
    ]
    params = {}
    result = {k: attrs[k] for k in std_keys if k in attrs}
    if 'dataset' in attrs:
        params['dataset'] = attrs['dataset']
    if params:
        result['params'] = params
    return cast(ModelParamAttrs, result)


def convert_to_resource(
    resource: SeriesOrFrame, attrs: dict | Attrs | ResourceTypeClass | ResourceTypeDescriptor
) -> SeriesOrFrame:
    new_attrs = attrs_as_descriptor_mapping(attrs)
    resource = convert_by_attrs(safe_copy(resource), new_attrs)
    inherited = ['resource_type', 'agg', 'datasource']
    for k in inherited:
        if k in new_attrs:
            resource.attrs[k] = new_attrs[k]
    return resource


def convert_power_to_energy_Wh(
    power: pd.Series,
    energy_resource_type: str,
) -> pd.Series:
    from_freq = power.attrs.get('freq', None)
    if not from_freq:
        assert isinstance(power.index, pd.DatetimeIndex)
        # infer freq from just 2 elements
        if len(power) > 1:
            from_freq = pd.to_timedelta(power.index[1] - power.index[0])
        else:
            raise ValueError('power must have a freq attribute or at least 2 elements to infer freq')
    if not from_freq:
        raise ValueError('power series must have a freq in series.attrs')

    from_offset = pd.tseries.frequencies.to_offset(from_freq)
    to_freq_offset = pd.tseries.frequencies.to_offset('h')

    assert from_offset is not None
    assert to_freq_offset is not None

    reference_date = pd.Timestamp('1990-01-01')
    delta_from = (reference_date + 12 * from_offset) - reference_date
    delta_to = (reference_date + 12 * to_freq_offset) - reference_date

    scaling = delta_from / delta_to

    energy_attrs = power.attrs.copy()
    energy = power * scaling

    energy_attrs['unit'] = power.attrs['unit'] + 'h'
    energy_attrs['agg'] = 'sum'
    energy_attrs['resource_type'] = energy_resource_type

    energy.attrs = energy_attrs
    return energy
