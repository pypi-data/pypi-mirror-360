import json
import yaml
import tomli_w
import configparser
import xml.etree.ElementTree as ET

from types import SimpleNamespace
from typing import Any, Union, List
from pathlib import Path
from enum import Enum


class ConfigFormat(Enum):
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    INI = "ini"
    XML = "xml"


def _namespace_to_dict(obj: Any) -> Any:
    """Recursively convert a SimpleNamespace or nested collection to a dictionary.

    Args:
        obj: The object to convert.

    Returns:
        The converted object as a dictionary, list, or primitive.
    """
    if isinstance(obj, SimpleNamespace):
        return {k: _namespace_to_dict(v) for k, v in vars(obj).items()}
    elif isinstance(obj, dict):
        return {k: _namespace_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_namespace_to_dict(item) for item in obj]
    else:
        return obj


def _filter_dict(data: Any, exclude: List[str]) -> Any:
    """Recursively remove specified keys from a dictionary or list.

    Args:
        data: The data structure (dict or list) to filter.
        exclude: List of keys to exclude from the dictionary.

    Returns:
        The filtered data with specified keys removed.
    """
    if isinstance(data, dict):
        return {k: _filter_dict(v, exclude) for k, v in data.items() if k not in exclude}
    elif isinstance(data, list):
        return [_filter_dict(item, exclude) for item in data]
    else:
        return data


def _dict_to_xml_element(name: str, data: Any) -> ET.Element:
    """Recursively convert a dictionary or list into an XML Element.

    Args:
        name: Name of the root XML element.
        data: Data to convert (dict, list, or primitive).

    Returns:
        An xml.etree.ElementTree.Element representing the data.
    """
    element = ET.Element(name)
    if isinstance(data, dict):
        for key, val in data.items():
            child = _dict_to_xml_element(key, val)
            element.append(child)
    elif isinstance(data, list):
        for item in data:
            child = _dict_to_xml_element("item", item)
            element.append(child)
    else:
        element.text = str(data)
    return element


def write_config(
    config: Union[dict, SimpleNamespace],
    filename: str,
    format: ConfigFormat,
    exclude_keys: List[str] = None
) -> None:
    """Write configuration data to a file in the specified format.

    Args:
        config: Dictionary or SimpleNamespace containing the configuration data.
        filename: Path to the target output file.
        format: Format to write ('json', 'yaml', 'toml', 'ini', or 'xml').
        exclude_keys: Optional; list of top-level keys to exclude from output.

    Raises:
        ValueError: If the provided format is unsupported.
    """
    exclude_keys = exclude_keys or []
    data = _namespace_to_dict(config)
    filtered = _filter_dict(data, exclude_keys)

    path = Path(filename)
    if format == ConfigFormat.JSON:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(filtered, f, indent=2)

    elif format == ConfigFormat.YAML:
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(filtered, f, sort_keys=False)

    elif format == ConfigFormat.TOML:
        with open(path, "wb") as f:
            f.write(tomli_w.dumps(filtered).encode("utf-8"))

    elif format == ConfigFormat.INI:
        config_parser = configparser.ConfigParser()

        for section, values in filtered.items():
            if isinstance(values, dict):
                config_parser[section] = {str(k): str(v) for k, v in values.items()}
            else:
                config_parser["DEFAULT"][section] = str(values)

        with open(path, "w", encoding="utf-8") as f:
            config_parser.write(f)
    elif format == ConfigFormat.XML:
        root = _dict_to_xml_element("config", filtered)
        tree = ET.ElementTree(root)
        tree.write(path, encoding="utf-8", xml_declaration=True)
    else:
        raise ValueError(f"Unsupported format: {format}")
