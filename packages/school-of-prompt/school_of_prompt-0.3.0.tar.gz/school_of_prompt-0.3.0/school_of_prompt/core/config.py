"""
Configuration management for the prompt optimization framework.
Enhanced with advanced features and validation.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
import yaml
import json
import os
from dataclasses import dataclass, field


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

    # Enhanced configuration properties
    @property
    def sampling_strategy(self) -> str:
        """Get sampling strategy for dataset."""
        return self.evaluation_config.get("sampling_strategy", "random")

    @property
    def sample_size(self) -> Optional[int]:
        """Get sample size for evaluation."""
        return self.evaluation_config.get("sample_size")

    @property
    def cross_validation(self) -> bool:
        """Whether to use cross-validation."""
        return self.evaluation_config.get("cross_validation", False)

    @property
    def k_fold(self) -> int:
        """Number of folds for cross-validation."""
        return self.evaluation_config.get("k_fold", 5)

    @property
    def cache_enabled(self) -> bool:
        """Whether caching is enabled."""
        return self.config.get("cache", {}).get("enabled", True)

    @property
    def cache_expiry(self) -> str:
        """Cache expiry time."""
        return self.config.get("cache", {}).get("expiry", "24h")

    @property
    def batch_size(self) -> int:
        """Batch size for processing."""
        return self.config.get("batch_processing", {}).get("chunk_size", 100)

    @property
    def parallel_evaluation(self) -> bool:
        """Whether to use parallel evaluation."""
        return self.config.get("batch_processing", {}).get("parallel_evaluation", False)

    @property
    def export_formats(self) -> List[str]:
        """Export formats for results."""
        return self.output_config.get("export_formats", ["json"])

    @property
    def save_detailed_results(self) -> bool:
        """Whether to save detailed results."""
        return self.output_config.get("save_detailed_results", True)

    @property
    def save_prompt_samples(self) -> bool:
        """Whether to save prompt samples."""
        return self.output_config.get("save_prompt_samples", False)

    def get_datasets(self) -> Dict[str, str]:
        """Get dataset configuration for multi-dataset support."""
        datasets = self.config.get("datasets", {})
        if not datasets and self.dataset_path:
            # Single dataset fallback
            datasets = {"main": self.dataset_path}
        return datasets

    def get_recommended_metrics_for_task(self) -> List[str]:
        """Get recommended metrics based on task configuration."""
        # Basic recommendations without importing metrics module
        task_type = self.task_type.lower()
        
        if task_type in ["classification", "sentiment", "categorization"]:
            return ["accuracy", "f1_score", "precision", "recall", "valid_rate"]
        
        elif task_type in ["regression", "rating", "scoring"]:
            base_metrics = ["mae", "rmse", "r2_score", "median_error"]
            
            # Add tolerance metrics based on target range
            if self.target_range:
                range_size = self.target_range[1] - self.target_range[0]
                if range_size <= 10:  # Small range (e.g., 1-10 rating)
                    base_metrics.extend(["within_1", "within_2"])
                elif range_size <= 20:  # Medium range (e.g., 0-18 age)
                    base_metrics.extend(["within_2", "within_3"])
                else:  # Large range
                    base_metrics.extend(["within_5"])
            
            return base_metrics
        
        elif task_type in ["generation", "summarization", "text_gen"]:
            return ["response_quality", "token_efficiency", "valid_rate"]
        
        else:
            # Default comprehensive set
            return ["accuracy", "mae", "valid_rate", "response_quality"]

    def validate(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        # Required fields
        if not self.task_name:
            issues.append("task.name is required")
        
        if not self.task_type:
            issues.append("task.type is required")
        
        # Dataset validation
        datasets = self.get_datasets()
        if not datasets:
            issues.append("At least one dataset must be specified")
        
        for name, path in datasets.items():
            if not Path(path).exists():
                issues.append(f"Dataset '{name}' not found at path: {path}")
        
        # Metrics validation
        if not self.evaluation_metrics:
            issues.append("evaluation.metrics must be specified")
        
        # API key validation
        if self.llm_provider == "openai" and not os.getenv("OPENAI_API_KEY"):
            issues.append("OPENAI_API_KEY environment variable is required")
        
        return issues

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.config.copy()

    def merge_with_defaults(self, defaults: Dict[str, Any]) -> "FrameworkConfig":
        """Merge configuration with defaults."""
        merged = self._deep_merge(defaults, self.config)
        return FrameworkConfig(config_dict=merged)

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result


@dataclass
class OptimizationConfig:
    """Structured configuration for optimization parameters."""
    
    # Task configuration
    task_name: str = "unnamed_task"
    task_type: str = "regression"
    target_range: Optional[Tuple[float, float]] = None
    
    # Data configuration
    datasets: Dict[str, str] = field(default_factory=dict)
    sampling_strategy: str = "random"
    sample_size: Optional[int] = None
    
    # Model configuration
    model_name: str = "gpt-3.5-turbo"
    model_provider: str = "openai"
    model_params: Dict[str, Any] = field(default_factory=dict)
    
    # Evaluation configuration
    metrics: List[str] = field(default_factory=list)
    cross_validation: bool = False
    k_fold: int = 5
    
    # Performance configuration
    cache_enabled: bool = True
    cache_expiry: str = "24h"
    batch_size: int = 100
    parallel_evaluation: bool = False
    
    # Output configuration
    output_dir: str = "experiments"
    export_formats: List[str] = field(default_factory=lambda: ["json"])
    save_detailed_results: bool = True
    save_prompt_samples: bool = False
    
    def to_framework_config(self) -> FrameworkConfig:
        """Convert to FrameworkConfig format."""
        config_dict = {
            "task": {
                "name": self.task_name,
                "type": self.task_type,
                "target_range": list(self.target_range) if self.target_range else None
            },
            "datasets": self.datasets,
            "evaluation": {
                "metrics": self.metrics,
                "sampling_strategy": self.sampling_strategy,
                "sample_size": self.sample_size,
                "cross_validation": self.cross_validation,
                "k_fold": self.k_fold
            },
            "llm": {
                "provider": self.model_provider,
                "model": self.model_name,
                "params": self.model_params
            },
            "cache": {
                "enabled": self.cache_enabled,
                "expiry": self.cache_expiry
            },
            "batch_processing": {
                "chunk_size": self.batch_size,
                "parallel_evaluation": self.parallel_evaluation
            },
            "output": {
                "directory": self.output_dir,
                "export_formats": self.export_formats,
                "save_detailed_results": self.save_detailed_results,
                "save_prompt_samples": self.save_prompt_samples
            }
        }
        return FrameworkConfig(config_dict=config_dict)


def create_default_config() -> OptimizationConfig:
    """Create a default configuration."""
    return OptimizationConfig(
        task_name="default_task",
        task_type="regression",
        datasets={"main": "data.csv"},
        metrics=["accuracy", "mae"],
        model_name="gpt-3.5-turbo",
        output_dir="experiments"
    )


def load_config_from_file(config_path: str) -> FrameworkConfig:
    """Load configuration from file with validation."""
    config = FrameworkConfig(config_path=config_path)
    
    # Validate configuration
    issues = config.validate()
    if issues:
        raise ValueError(f"Configuration validation failed: {issues}")
    
    return config


def create_sample_config_file(output_path: str) -> None:
    """Create a sample configuration file."""
    sample_config = {
        "task": {
            "name": "youtube_age_rating",
            "type": "regression",
            "target_range": [0, 18]
        },
        "datasets": {
            "training": "datasets/youtube_train.csv",
            "validation": "datasets/youtube_val.csv",
            "test": "datasets/youtube_test.csv"
        },
        "evaluation": {
            "metrics": ["mae", "accuracy", "within_1", "valid_rate"],
            "sampling_strategy": "stratified",
            "sample_size": 1000,
            "cross_validation": True,
            "k_fold": 5
        },
        "llm": {
            "provider": "openai",
            "model": "gpt-4",
            "params": {
                "temperature": 0.0,
                "max_tokens": 50
            }
        },
        "cache": {
            "enabled": True,
            "expiry": "24h"
        },
        "batch_processing": {
            "chunk_size": 100,
            "parallel_evaluation": True
        },
        "output": {
            "directory": "experiments/youtube_age_rating",
            "export_formats": ["json", "csv", "html_report"],
            "save_detailed_results": True,
            "save_prompt_samples": True
        }
    }
    
    with open(output_path, 'w') as f:
        yaml.dump(sample_config, f, default_flow_style=False, indent=2)
