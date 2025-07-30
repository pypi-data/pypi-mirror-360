"""
Simple interfaces for extending the framework.
Much simpler than the original abstract base classes.
"""

from typing import Any, Dict, List
from abc import ABC, abstractmethod


class CustomMetric(ABC):
    """Simple interface for custom metrics."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the metric."""
        pass

    @abstractmethod
    def calculate(self, predictions: List[Any], actuals: List[Any]) -> float:
        """Calculate metric score from predictions and actuals."""
        pass


class CustomDataSource(ABC):
    """Simple interface for custom data sources."""

    @abstractmethod
    def load(self) -> List[Dict[str, Any]]:
        """Load and return data as list of dictionaries."""
        pass


class CustomModel(ABC):
    """Simple interface for custom models."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate response from prompt."""
        pass


class CustomTask(ABC):
    """Simple interface for custom tasks."""

    @abstractmethod
    def format_prompt(self, template: str, sample: Dict[str, Any]) -> str:
        """Format prompt template with sample data."""
        pass

    @abstractmethod
    def extract_prediction(self, response: str) -> Any:
        """Extract prediction from model response."""
        pass

    @abstractmethod
    def get_ground_truth(self, sample: Dict[str, Any]) -> Any:
        """Extract ground truth from sample."""
        pass


# Built-in implementations for common cases
class SimpleMetric:
    """Built-in metric implementation."""

    def __init__(self, name: str, func):
        self.name = name
        self._func = func

    def calculate(self, predictions: List[Any], actuals: List[Any]) -> float:
        return self._func(predictions, actuals)


class SimpleDataSource:
    """Built-in data source implementation."""

    def __init__(self, data: List[Dict[str, Any]]):
        self._data = data

    def load(self) -> List[Dict[str, Any]]:
        return self._data


class SimpleModel:
    """Built-in model implementation."""

    def __init__(self, generate_func):
        self._generate = generate_func

    def generate(self, prompt: str) -> str:
        return self._generate(prompt)


class SimpleTask:
    """Built-in task implementation."""

    def __init__(self, format_func, extract_func, truth_func):
        self._format = format_func
        self._extract = extract_func
        self._truth = truth_func

    def format_prompt(self, template: str, sample: Dict[str, Any]) -> str:
        return self._format(template, sample)

    def extract_prediction(self, response: str) -> Any:
        return self._extract(response)

    def get_ground_truth(self, sample: Dict[str, Any]) -> Any:
        return self._truth(sample)
