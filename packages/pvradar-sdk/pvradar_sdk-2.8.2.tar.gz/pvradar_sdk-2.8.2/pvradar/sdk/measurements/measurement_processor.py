import copy
import re
import orjson
from pathlib import Path
import pandas as pd
from dataclasses import field, dataclass
from typing import Any

from .types import MeasurementManifest, MeasurementRecipe
from ..common.source import AbstractSource, LocalSource
from ..common.op_pipeline import StdExecutor


@dataclass(kw_only=True)
class Instruction:
    type: str
    args: list[Any] = field(default_factory=list)
    spread: bool = False


def parse_instruction(string: str) -> Instruction | None:
    spread = False
    if string.startswith('...'):
        spread = True
        string = string[3:]
    if string.startswith('!'):
        string = string[1:]
        if string.startswith('include:'):
            include_path = string[len('include:') :]
            return Instruction(type='include', args=[include_path], spread=spread)
        elif string.startswith('var:'):
            var_name = string[len('var:') :]
            return Instruction(type='var', args=[var_name], spread=spread)
        elif string.startswith('list_files:'):
            target_path = string[len('list_files:') :]
            return Instruction(type='list_files', args=[target_path], spread=spread)
        elif string.startswith('for '):
            match = re.match(r'for\s+(\w+)\s+in\s+(\w+):\s*(\w+)', string)
            if match:
                return Instruction(
                    type='for',
                    args=[match.group(1), match.group(2), match.group(3)],
                    spread=spread,
                )


class MeasurementProcessor:
    def __init__(self, source: AbstractSource | str | Path) -> None:
        if isinstance(source, (str, Path)):
            source = LocalSource(source)
        self.source = source
        manifest = source.get_measurement_manifest()
        assert manifest is not None, f'MeasurementManifest expects measurements.json in the source {source}'
        self.manifest: MeasurementManifest = manifest
        self._instruction_was_run = False
        self.executor = StdExecutor().register_op(self.source.to_op())

    def run_instruction(self, instruction: Instruction) -> Any:
        if instruction.type == 'include':
            raw_data = self.source.get_file_contents(instruction.args[0])
            filename = instruction.args[0]
            if filename.endswith('.json'):
                return orjson.loads(raw_data)
            raise (ValueError(f'Unsupported file type for include: {filename}'))

        elif instruction.type == 'var':

            def get_field(data, path):
                keys = path.split('.')
                for key in keys:
                    if isinstance(data, list):
                        key = int(key)
                    data = data[key]
                return data

            var_name = instruction.args[0]
            if self.manifest.vars is None:
                raise ValueError('Cannot replace var {var_name} because manifest has no vars defined')
            chunks = var_name.split('.')
            if chunks[0] not in self.manifest.vars:
                raise ValueError(f'var {chunks[0]} not found in measurement manifest')
            var = self.manifest.vars[chunks[0]]
            if len(chunks) > 1:
                var = get_field(var, '.'.join(chunks[1:]))
            return var

        elif instruction.type == 'list_files':
            target_path = instruction.args[0]
            files = self.source.list_files(target_path)
            if not files:
                raise ValueError(f'No files found in the path: {target_path}')
            return files

        elif instruction.type == 'for':
            if len(instruction.args) != 3:
                raise ValueError(f'Invalid for instruction args: {instruction.args}')
            var_name, iterable_name, target_name = instruction.args
            if self.manifest.vars is None or iterable_name not in self.manifest.vars:
                raise ValueError(f'Cannot iterate over {iterable_name}, it is not defined in manifest vars')
            iterable = self.compile_object(self.manifest.vars[iterable_name])
            old_vars = self.manifest.vars
            self.manifest.vars = copy.deepcopy(old_vars)

            result = []
            target_code = '!var:' + target_name

            for item in iterable:
                self.manifest.vars[var_name] = item
                self._instruction_was_run = True
                run_result = self.compile_object(target_code)
                result.append(run_result)

            self.manifest.vars = old_vars  # restore original vars
            return result
        else:
            raise ValueError(f'Unknown instruction type: {instruction.type}')

    def compile_object(self, object: Any) -> Any:
        MAX_ITERATION_DEPTH = 30
        counter = 0
        # max nested iteration is allowed
        while counter < MAX_ITERATION_DEPTH:
            self._instruction_was_run = False
            object = self._nested_compile(object)
            if not self._instruction_was_run:
                return object
            counter += 1

        raise ValueError(f'Max iteration depth {MAX_ITERATION_DEPTH} reached, possible infinite loop detected')

    def _nested_compile(self, object: Any) -> Any:
        object = copy.deepcopy(object)
        # iteratively and recursively go through dicts and list identifying str field and elements
        # if the str, then parse it as an instruction
        # if it is an instruction then run it and replace the str with the result
        # if the instruction is spread and the str was an element of a list, then spread the result into the list
        if isinstance(object, str):
            instruction = parse_instruction(object)
            if instruction:
                result = self.run_instruction(instruction)
                self._instruction_was_run = True
                if instruction.spread:
                    # spread without a list is treated as flattening the result
                    flat = []
                    if not isinstance(result, list):
                        raise ValueError(f'Spread instruction {instruction} must return a list, got {type(result)}')
                    for item in result:
                        if isinstance(item, list):
                            flat.extend(item)
                        else:
                            flat.append(item)
                    return flat
                else:
                    return result
        elif isinstance(object, dict):
            for key, value in object.items():
                object[key] = self._nested_compile(value)
        elif isinstance(object, list):
            for i, value in enumerate(object):
                if isinstance(value, str):
                    instruction = parse_instruction(value)
                    if instruction:
                        result = self.run_instruction(instruction)
                        self._instruction_was_run = True
                        if instruction.spread:
                            if not isinstance(result, list):
                                raise ValueError(f'Spread instruction {instruction} must return a list, got {type(result)}')
                            object[i : i + 1] = result
                        else:
                            object[i] = result
                else:
                    object[i] = self._nested_compile(value)

        return object

    def get_compiled_recipes(self) -> list[MeasurementRecipe]:
        compiled_recipes = self.compile_object(self.manifest.recipes)
        for index, recipe in enumerate(compiled_recipes):
            compiled_recipes[index] = MeasurementRecipe(recipe)
        return compiled_recipes

    def to_df(self, only_series: bool = False) -> pd.DataFrame:
        compiled_recipes = self.get_compiled_recipes()
        data = []
        for recipe in compiled_recipes:
            resource_type = recipe.get('resource_type')
            if only_series and resource_type in ('location', 'fixed_design_spec', 'tracker_design_spec'):
                continue
            entry = {
                'measurement_group_id': recipe.get('measurement_group_id', ''),
                'resource_type': resource_type,
                'freq': recipe['attrs'].get('freq', '') if 'attrs' in recipe else '',
            }
            data.append(entry)
        result = pd.DataFrame(data)
        result.sort_values(by=['measurement_group_id', 'resource_type'], inplace=True)
        result.set_index(['measurement_group_id', 'resource_type'], inplace=True)
        return result
