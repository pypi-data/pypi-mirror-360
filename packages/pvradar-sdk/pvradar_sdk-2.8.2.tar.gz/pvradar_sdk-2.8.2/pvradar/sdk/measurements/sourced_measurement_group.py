from functools import cached_property
from typing import Mapping, Optional, Any, override, Hashable
from pathlib import Path
import pandas as pd

from . import (
    fixed_design_spec_resource_type,
    tracker_design_spec_resource_type,
    AbstractMeasurementGroup,
    default_confidentiality,
)
from .. import PvradarLocation, PvradarSiteDesign, make_fixed_design, make_tracker_design
from ..common.op_pipeline import StdExecutor
from ..common.source import SourceManifest, AbstractSource, LocalSource
from ..common.pandas_utils import infer_freq_as_str
from ..modeling.basics import Confidentiality, ResourceRecord

# FIXME: Access to a protected member _list of a module
from ..modeling.resource_types._list import standard_mapping
from ..modeling.utils import is_attrs_convertible, attrs_as_descriptor_mapping, convert_by_attrs
from .measurement_processor import MeasurementProcessor


class SourcedMeasurementGroup(AbstractMeasurementGroup):
    @cached_property
    def source_manifest(self) -> SourceManifest | None:
        return self.source.get_source_manifest()

    @cached_property
    @override
    def org_id(self) -> Optional[str]:
        return self.source_manifest.org_id if self.source_manifest is not None else None

    @cached_property
    @override
    def confidentiality(self) -> Confidentiality:
        if self.source_manifest is not None and self.source_manifest.confidentiality is not None:
            return self.source_manifest.confidentiality
        return default_confidentiality

    def __init__(
        self,
        source: AbstractSource | Path | str,
        *,
        id: Optional[str] = None,
        location: Optional[PvradarLocation] = None,
        interval: Optional[str] = None,
        default_tz: Optional[str] = None,
        design: Optional[PvradarSiteDesign] = None,
        **kwargs,
    ):
        if isinstance(source, (str, Path)):
            source = LocalSource(source)
        self.source = source
        self.processor = MeasurementProcessor(source=source)
        recipes = self.processor.get_compiled_recipes()
        source_name = self.source.get_dirname()
        grouped = any(
            recipe.get('measurement_group_id') is not None and recipe.get('measurement_group_id') != source_name
            for recipe in recipes
        )

        # collect unique non-empty measurement_group_id from all recipes
        all_ids = {recipe.get('measurement_group_id') for recipe in recipes if recipe.get('measurement_group_id')}
        if len(all_ids) == 1 and id is None:
            id = all_ids.pop()

        if id is None:
            if grouped:
                raise ValueError(f'measurement_group_id undefined for "{source}". Please provide id=... argument')
            id = source_name
        if not grouped:
            for recipe in recipes:
                recipe['measurement_group_id'] = id
        self.executor = StdExecutor().register_op(self.source.to_op())
        self.recipes = []
        if isinstance(recipes, list) and len(recipes) > 0:
            design_recipe = None
            design_maker = None
            for recipe in recipes:
                resource_type = recipe.get('resource_type')
                measurement_group_id = recipe.get('measurement_group_id')
                if measurement_group_id == id or measurement_group_id is None:
                    self.recipes.append(recipe)
                    if resource_type == 'location':
                        location_json = self.executor.execute(ops=recipe.get('ops', []))
                        location = PvradarLocation(
                            latitude=location_json.get('latitude'), longitude=location_json.get('longitude')
                        )
                    elif resource_type == fixed_design_spec_resource_type:
                        design_recipe = recipe
                        design_maker = make_fixed_design
                    elif resource_type == tracker_design_spec_resource_type:
                        design_recipe = recipe
                        design_maker = make_tracker_design
            if design_recipe is not None and design_maker is not None:
                design = design_maker(**self.executor.execute(ops=design_recipe.get('ops', [])))
        super().__init__(
            id=id,
            location=location,
            interval=interval,
            default_tz=default_tz,
            design=design,
            **kwargs,
        )

    @override
    def measurement(self, subject: Any, label: Optional[str] = None) -> Any:
        if isinstance(subject, str):
            resource_type = subject
            user_requested_attrs = {'resource_type': resource_type}
        elif is_attrs_convertible(subject):
            user_requested_attrs = dict(attrs_as_descriptor_mapping(subject))
            resource_type = user_requested_attrs.get('resource_type', None)
        else:
            raise ValueError('Unsupported subject type for local measurement group: ' + str(subject))
        if resource_type is None:
            raise ValueError('Resource type is required for local measurement group.')
        recipes = self.recipes
        for recipe in recipes:
            if recipe.get('resource_type') != resource_type:
                continue
            resource = self.executor.execute(ops=recipe.get('ops', []))

            if isinstance(resource, (pd.Series, pd.DataFrame)):
                standard = dict(standard_mapping.get(resource_type, {}))  # pyright: ignore [reportCallIssue, reportArgumentType]
                standard_unit = standard.pop('to_unit', None)  # pyright: ignore [reportCallIssue, reportArgumentType]
                resource_unit = resource.attrs.get('unit', None)

                if standard_unit and resource_unit is None:
                    standard['unit'] = standard_unit  # pyright: ignore [reportArgumentType]

                compiled_attrs: dict[Hashable, Any] = {
                    **standard,
                    **recipe.get('attrs', {}),
                    'measurement_group_id': self.measurement_group_id,
                }
                if label is not None:
                    compiled_attrs['label'] = label
                resource.attrs = compiled_attrs
                if isinstance(resource.index, pd.DatetimeIndex):
                    if 'tz' in resource.attrs and resource.attrs['tz'] != self.default_tz:
                        resource.index = resource.index.tz_localize(None).tz_localize(resource.attrs['tz'])
                    if resource.index.tz is None:
                        resource.index = resource.index.tz_localize(self.default_tz)
                    else:
                        resource.index = resource.index.tz_convert(self.default_tz)
                    resource.attrs['tz'] = self.default_tz
                    inferred_freq = infer_freq_as_str(resource)
                    if inferred_freq is not None:
                        resource.attrs['freq'] = inferred_freq

                return convert_by_attrs(resource, user_requested_attrs)
            return resource
        raise ValueError(
            f'No measurement found for resource type "{resource_type}" in local measurement group "{self.measurement_group_id}".'
        )

    @property
    @override
    def resource_type_map(self) -> Mapping[str, ResourceRecord]:
        # go through recipes and for each resource type return just an empty dict
        # as we don't have any metadata about resources in local measurement group
        result: dict[str, ResourceRecord] = {}
        for recipe in self.recipes:
            resource_type = recipe.get('resource_type')
            if resource_type is not None and resource_type not in result:
                result[resource_type] = ResourceRecord(
                    resource_type=resource_type,
                    attrs=recipe.get('attrs', {}),
                )
        return result
