import argparse
import copy
import json
import os
import re
from typing import Any, Callable, Dict, Generic, Optional, Type, TypeVar
from dotenv import load_dotenv, dotenv_values
from pydantic import BaseModel
import yaml
import json

S = TypeVar("S")

DYNAMIC_PATTERN = re.compile(r"(\{\{.*?\}\})")

class SettingsLoader(Generic[S]):
    def __init__(self, settings_model: Type[S], settings_path: str):
        self.settings_model = settings_model
        self.settings_path = settings_path
        self.args_model: Optional[BaseModel] = None
        self.missing_data: list[str] = []
        self.custom_loaders: dict[str, Callable[[str], dict[str, str]]] = {}
        self.source_keys: list[str] = ['this']

    def with_args(self, args_model: BaseModel):
        self.args_model = args_model
        return self
    
    def with_custom_source_loaders(self, loaders: dict[str, Callable[[str], dict[str, str]]] = {}):
        self.custom_loaders = loaders
        return self
    
    def _load_sources(self, loaders) -> Dict[str, Dict[str, Any]]:
        loaded_sources: Dict[str, Dict[str, Any]] = {}
        for source_key, source_files in loaders.items():
            loaded_sources[source_key] = {}
            self.source_keys.append(source_key)

            if source_files is not None:
                for file_path in source_files:
                    # Determine file format by extension
                    if file_path.endswith((".yaml", ".yml")):
                        with open(file_path, "r") as sf:
                            data = yaml.safe_load(sf)
                    elif file_path.endswith(".json"):
                        with open(file_path, "r") as sf:
                            data = json.load(sf)
                    elif file_path.endswith(".env"):
                        data = dotenv_values(file_path)
                    else:
                        for file_extension, cb_loader in self.custom_loaders.items():
                            if file_path.endswith(f".{file_extension}"):
                                data = cb_loader(file_path)

                    data_formatted = self._replace_this_with_source_key(data, source_key)
                    loaded_sources[source_key].update(data_formatted)
            else:
                if source_key == 'env':
                    load_dotenv()
                    data = {k: v for k, v in os.environ.items()}
                    loaded_sources['env'] = self._replace_this_with_source_key(data, source_key)
                elif source_key == 'args' and self.args_model is not None:
                    parser = argparse.ArgumentParser()
                    for name, arg_type in self.args_model.__annotations__.items():
                        if arg_type is bool:
                          parser.add_argument(f"--{name}", nargs="?", const=True)
                        else:
                            parser.add_argument(f"--{name}")
                    args = parser.parse_args()
                    cli_args_dict = {k: v for k, v in vars(args).items() if v is not None}
                    loaded_sources['args'] = self._replace_this_with_source_key(cli_args_dict, source_key)
        
        return loaded_sources
    
    def _replace_this_with_source_key(self, data, replacement, target_substring="this."):
        if isinstance(data, dict):
            return {
                k: self._replace_this_with_source_key(v, replacement, target_substring)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [
                self._replace_this_with_source_key(item, replacement, target_substring)
                for item in data
            ]
        elif isinstance(data, str):
            if target_substring in data:
                return data.replace(target_substring, replacement + ".")
            return data
        else:
            return data

    #get (nested) value from dict given a key path
    def _get_value(self, source, key_path):
        keys = key_path.split('.')
        current = source

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                # If current is a dynamic placeholder like "{{something}}"
                if isinstance(current, str) and current.strip().startswith("{{") and current.strip().endswith("}}"):
                    inner = current.strip()[2:-2].strip()
                    path = ".".join(keys)
                    return f"{{{{{inner}.{path}}}}}"

                return None
        return current
    
    def _has_unresolved_field(self, data: Any) -> bool:
        if isinstance(data, dict):
            for value in data.values():
                if self._has_unresolved_field(value):
                    return True
        elif isinstance(data, list):
            for item in data:
                if self._has_unresolved_field(item):
                    return True
        elif isinstance(data, str):
            if DYNAMIC_PATTERN.fullmatch(data.strip()):
                return True
        return False
    
    #extract all dynamic vars and output in format such that reconstruction is possible
    def _split_and_extract(self, data) -> tuple[list[str], list[bool]]:
        parts = DYNAMIC_PATTERN.split(data)
        extracted = []
        is_dynamic = []
        for part in parts:
            if not part: continue

            if DYNAMIC_PATTERN.fullmatch(part): #gives {{...}}
                extracted.append(part)
                is_dynamic.append(True)
            else:
                extracted.append(part)
                is_dynamic.append(False)

        return extracted, is_dynamic

    def _resolve_dynamic_values(self, data: Any, context: Dict[str, Dict[str, Any]], path: str = ""):
        if isinstance(data, dict):
            resolved = {}
            for k, v in data.items():
                current_path = f"{path}.{k}" if path else k
                resolved_value = self._resolve_dynamic_values(v, context, path=current_path)
                if resolved_value is not None:
                    resolved[k] = resolved_value

            if "__base__" in resolved: #When __base__ is used additonal fields are not allowed. Only fields overwrites are allowed.
                base = resolved.pop("__base__")
                result = copy.deepcopy(base)

                #Recursively merge overwrites into the base
                def deep_update(d, u):
                    for k, v in u.items():
                        if isinstance(v, dict) and isinstance(d.get(k), dict): deep_update(d[k], v)
                        else: d[k] = v
                    return d
                
                resolved = deep_update(result, resolved)

            return resolved
        elif isinstance(data, list):
            return [
                self._resolve_dynamic_values(item, context, path=f"{path}[{idx}]") #TODO: check if this is correct
                for idx, item in enumerate(data)
            ]
        elif isinstance(data, str):
            parts, is_dynamic_flags = self._split_and_extract(data)
            result = None

            if len(parts) > 0:
                for part, is_dynamic in zip(parts, is_dynamic_flags):
                    if not is_dynamic: 
                        if result is None: result = part
                        else: result = result + part
                    else:
                        content = part[2:-2].strip()
                        placeholders = [p.strip() for p in content.split(">")]
                        found = False

                        for i, placeholder in enumerate(placeholders):
                            is_last = (i == len(placeholders) - 1)

                            for source_key in self.source_keys:
                                prefix = source_key + "."
                                key_path = None

                                if placeholder.startswith(prefix): key_path = placeholder[len(prefix):]
                                elif placeholder == source_key: key_path = path.rsplit('.', 1)[-1]

                                if key_path is not None:
                                    source = context.get(source_key)
                                    if source is None:
                                        self.missing_data.append(source_key)
                                        return None
                                    value = self._get_value(source, key_path)
                                    if self._has_unresolved_field(value):
                                        value = self._resolve_dynamic_values(value, context, path)

                                    #if value is not string, then there is only 1 possible true result
                                    if isinstance(value, str): 
                                        if result is None: result = value
                                        else: result = result + value
                                    elif is_last: return value

                                    if value is not None: found = True
                                    break
                            if found: break

            return result
        else:
            return data

    def load(self):
        with open(self.settings_path, "r") as f:
            settings = yaml.safe_load(f)

        loaders = settings.pop("settings_loader", {})
        loaders['env'] = None
        loaders['args'] = None

        loaded_sources = self._load_sources(loaders)
        loaded_sources['this'] = settings
        self.source_keys.sort(key=len, reverse=True) #if you have key ai and ai_extra, you first want to match on ai_extra
        
        resolved_settings = self._resolve_dynamic_values(settings, loaded_sources)

        if self.missing_data:
            print(f"Warning: the following sources were not found: {', '.join(self.missing_data)}")

        return self.settings_model(**resolved_settings)