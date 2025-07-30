"""
Configuration management for the prompt optimization framework.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml
import json


class FrameworkConfig:
    """Configuration manager for the prompt optimization framework."""

    def __init__(
            self,
            config_path: Optional[str] = None,
            config_dict: Optional[Dict] = None):
        if config_dict:
            self.config = config_dict
        elif config_path:
            self.config = self._load_config(config_path)
        else:
            raise ValueError(
                "Either config_path or config_dict must be provided")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file."""
        path = Path(config_path)

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        if path.suffix == '.yaml' or path.suffix == '.yml':
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        elif path.suffix == '.json':
            with open(path, 'r') as f:
                return json.load(f)
        else:
            raise ValueError(f"Unsupported config file format: {path.suffix}")

    # Task configuration
    @property
    def task_name(self) -> str:
        return self.config.get("task", {}).get("name", "unnamed_task")

    @property
    def task_type(self) -> str:
        return self.config.get("task", {}).get("type", "regression")

    @property
    def target_range(self) -> Optional[List[float]]:
        return self.config.get("task", {}).get("target_range")

    # Data source configuration
    @property
    def data_source_config(self) -> Dict[str, Any]:
        return self.config.get("data_source", {})

    @property
    def data_source_type(self) -> str:
        return self.data_source_config.get("type", "generic")

    @property
    def enrichment_analyzers(self) -> List[str]:
        return self.data_source_config.get("enrichment", [])

    # Dataset configuration
    @property
    def dataset_config(self) -> Dict[str, Any]:
        return self.config.get("dataset", {})

    @property
    def dataset_path(self) -> str:
        return self.dataset_config.get("path", "")

    # Evaluation configuration
    @property
    def evaluation_config(self) -> Dict[str, Any]:
        return self.config.get("evaluation", {})

    @property
    def evaluation_metrics(self) -> List[str]:
        return self.evaluation_config.get("metrics", ["mae"])

    @property
    def prompt_variants(self) -> List[str]:
        return self.evaluation_config.get("variants", ["baseline"])

    # LLM configuration
    @property
    def llm_config(self) -> Dict[str, Any]:
        return self.config.get("llm", {})

    @property
    def llm_provider(self) -> str:
        return self.llm_config.get("provider", "openai")

    @property
    def llm_model(self) -> str:
        return self.llm_config.get("model", "gpt-3.5-turbo-instruct")

    # Output configuration
    @property
    def output_config(self) -> Dict[str, Any]:
        return self.config.get("output", {})

    @property
    def output_dir(self) -> str:
        return self.output_config.get("directory", "04_experiments/benchmarks")

    # API keys and credentials
    @property
    def api_keys_path(self) -> str:
        return self.config.get("api_keys_path", "config/api_keys.json")

    def get_api_keys(self) -> Dict[str, str]:
        """Load API keys from file."""
        try:
            with open(self.api_keys_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"API keys file not found: {
                    self.api_keys_path}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value
