import os
import yaml
import tomllib
import json
import configparser
import xml.etree.ElementTree as ET

from dotenv import load_dotenv
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Union, Dict, List, Optional


class Config:
    """
    Singleton class that loads and provides access to application configuration.

    Loads environment variables from a `.env` file and merges configuration from
    all `*.yaml`, `*.yml`, `*.toml`, `*.xml` or `*.json` files, in the current directory.
    """
    _instance = None
    _config: SimpleNamespace

    def __new__(cls) -> "Config":
        """
        Creates a singleton instance of the Config class.

        Returns:
            Config: A singleton Config instance.
        """
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self, config_paths: Optional[List[str]] = None) -> None:
        """
        Loads environment variables from `.env` and configuration from all matching config files
        in the root directory and in the 'config' subdirectory.

        Merges configuration from all YAML, TOML, JSON, INI, and XML files.

        Args:
            config_paths (Optional[List[str]]): Optional list of paths to project specific config files.
        """
        # Directories to search
        search_dirs = [Path("."), Path("config"), Path("configuration"), Path("conf"), Path("cfg"), Path("env"), Path("environment")]
        additional_search_dirs = [Path(path) for path in config_paths] if config_paths else []
        search_dirs.extend(additional_search_dirs)

        # Load .env files from all search directories (first found takes precedence)
        for search_dir in search_dirs:
            env_path = search_dir / ".env"
            if env_path.exists():
                load_dotenv(dotenv_path=env_path, override=False)

        # Map environment variables
        env_vars = {
            key: value for key, value in os.environ.items()
            if key.isidentifier()
        }
        self._env = self._dict_to_namespace(env_vars)        

        # Collect config files from all locations
        patterns = ["*.toml", "*.yaml", "*.yml", "*.json", "*.ini", "*.xml"]
        config_files = []

        for search_dir in search_dirs:
            for pattern in patterns:
                config_files.extend(sorted(search_dir.glob(pattern)))

        merged_config: Dict[str, Any] = {}

        for file_path in config_files:
            if file_path.suffix == ".ini":
                parser = configparser.ConfigParser()
                parser.read(file_path)
                data = {section: dict(parser[section]) for section in parser.sections()}
            else:
                with open(file_path, "rb") as f:
                    if file_path.suffix in [".yaml", ".yml"]:
                        data = yaml.safe_load(f)
                    elif file_path.suffix == ".toml":
                        data = tomllib.load(f)
                    elif file_path.suffix == ".json":
                        data = json.load(f)
                    elif file_path.suffix == ".xml":
                        tree = ET.parse(f)
                        root = tree.getroot()
                        data = self._xml_to_dict(root)
                    else:
                        continue

            if data:
                merged_config = self._deep_merge_dicts(merged_config, data)

        self._config = self._dict_to_namespace(merged_config)

    def _xml_to_dict(self, elem: ET.Element) -> Dict[str, Any]:
        """
        Recursively converts an XML element and its children into a dictionary,
        merging attributes as regular keys.

        Args:
            elem (ET.Element): The XML element to convert.

        Returns:
            Dict[str, Any]: A dictionary representation of the XML tree.
        """
        d = {}

        # Process children
        children = list(elem)
        if children:
            child_dict = {}
            for child in children:
                child_data = self._xml_to_dict(child)
                for k, v in child_data.items():
                    if k in child_dict:
                        if not isinstance(child_dict[k], list):
                            child_dict[k] = [child_dict[k]]
                        child_dict[k].append(v)
                    else:
                        child_dict[k] = v
            d.update(child_dict)

        # Add attributes directly
        if elem.attrib:
            d.update({k.lower(): v for k, v in elem.attrib.items()})

        # Add text content if no children
        text = elem.text.strip() if elem.text else ""
        if text and not children:
            d["value"] = text

        return {elem.tag.lower(): d or text}

    def _deep_merge_dicts(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merges two dictionaries.

        Args:
            base (Dict[str, Any]): The base dictionary to merge into.
            override (Dict[str, Any]): The dictionary with override values.

        Returns:
            Dict[str, Any]: A merged dictionary with nested updates.
        """
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge_dicts(result[key], value)
            else:
                result[key] = value
        return result

    def _dict_to_namespace(self, d: Any) -> Union[SimpleNamespace, list, Any]:
        """
        Recursively converts a dictionary to a nested SimpleNamespace.

        Args:
            d (Any): The dictionary or list to convert.

        Returns:
            Union[SimpleNamespace, list, Any]: A nested structure with SimpleNamespaces for dicts.
        """
        if isinstance(d, dict):
            return SimpleNamespace(**{str(k).lower(): self._dict_to_namespace(v) for k, v in d.items()})
        elif isinstance(d, list):
            return [self._dict_to_namespace(i) for i in d]
        else:
            return d

    def get(self) -> SimpleNamespace:
        """
        Retrieves the loaded configuration with an additional 'env' namespace.

        Returns:
            SimpleNamespace: A namespace with config plus an `env` namespace inside.
        """
        cfg = self._config
        setattr(cfg, "os", SimpleNamespace())
        setattr(cfg.os, "env", self._env)
        return cfg

    def reload(self, config_paths: Optional[List[str]] = None) -> None:
        """
        Reloads the configuration from the `.env` and matching YAML/TOML/JSON/XML files.

        This is useful if the configuration files are updated while the application is running.

        Args:
            config_paths (Optional[List[str]]): Optional list of paths to project specific config files.
        """
        self._load(config_paths)
