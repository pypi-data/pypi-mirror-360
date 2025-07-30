"""
Data source registry system for pluggable data sources.
Enables custom data sources and enrichment pipelines.
"""

from typing import Dict, Type, List, Any, Optional, Callable
from abc import ABC, abstractmethod
from ..core.simple_interfaces import CustomDataSource
import pandas as pd


class DataSourceRegistry:
    """Registry for custom data sources and enrichment pipelines."""
    
    def __init__(self):
        self._sources: Dict[str, Type[CustomDataSource]] = {}
        self._enrichers: Dict[str, Callable] = {}
        self._preprocessors: Dict[str, Callable] = {}
        
        # Register built-in sources
        self._register_builtin_sources()
        self._register_builtin_enrichers()
    
    def register_source(self, name: str, source_class: Type[CustomDataSource]) -> None:
        """Register a custom data source."""
        if not issubclass(source_class, CustomDataSource):
            raise ValueError(f"Source class must inherit from CustomDataSource")
        
        self._sources[name] = source_class
    
    def register_enricher(self, name: str, enricher_func: Callable) -> None:
        """Register a data enrichment function."""
        self._enrichers[name] = enricher_func
    
    def register_preprocessor(self, name: str, preprocessor_func: Callable) -> None:
        """Register a data preprocessing function."""
        self._preprocessors[name] = preprocessor_func
    
    def get_source(self, name: str, **kwargs) -> CustomDataSource:
        """Get a registered data source instance."""
        if name not in self._sources:
            raise ValueError(f"Unknown data source: {name}")
        
        return self._sources[name](**kwargs)
    
    def get_enrichment_pipeline(self, enrichers: List[str]) -> Callable:
        """Create an enrichment pipeline from multiple enrichers."""
        def pipeline(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            result = data
            for enricher_name in enrichers:
                if enricher_name not in self._enrichers:
                    raise ValueError(f"Unknown enricher: {enricher_name}")
                result = self._enrichers[enricher_name](result)
            return result
        
        return pipeline
    
    def get_preprocessing_pipeline(self, preprocessors: List[str]) -> Callable:
        """Create a preprocessing pipeline from multiple preprocessors."""
        def pipeline(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            result = data
            for preprocessor_name in preprocessors:
                if preprocessor_name not in self._preprocessors:
                    raise ValueError(f"Unknown preprocessor: {preprocessor_name}")
                result = self._preprocessors[preprocessor_name](result)
            return result
        
        return pipeline
    
    def list_sources(self) -> List[str]:
        """List all registered data sources."""
        return list(self._sources.keys())
    
    def list_enrichers(self) -> List[str]:
        """List all registered enrichers."""
        return list(self._enrichers.keys())
    
    def list_preprocessors(self) -> List[str]:
        """List all registered preprocessors."""
        return list(self._preprocessors.keys())
    
    def _register_builtin_sources(self) -> None:
        """Register built-in data sources."""
        self.register_source("csv", CSVDataSource)
        self.register_source("jsonl", JSONLDataSource)
        self.register_source("pandas", PandasDataSource)
        self.register_source("youtube", YouTubeDataSource)
        self.register_source("reddit", RedditDataSource)
    
    def _register_builtin_enrichers(self) -> None:
        """Register built-in enrichment functions."""
        self.register_enricher("text_length", add_text_length)
        self.register_enricher("word_count", add_word_count)
        self.register_enricher("sentiment_features", add_sentiment_features)
        self.register_enricher("readability", add_readability_metrics)
        self.register_enricher("domain_extraction", extract_domain_features)
        
        # Register preprocessors
        self.register_preprocessor("clean_text", clean_text_data)
        self.register_preprocessor("normalize_labels", normalize_labels)
        self.register_preprocessor("remove_duplicates", remove_duplicate_entries)
        self.register_preprocessor("balance_dataset", balance_dataset)


# Built-in data sources
class CSVDataSource(CustomDataSource):
    """CSV file data source."""
    
    def __init__(self, path: str, **kwargs):
        self.path = path
        self.kwargs = kwargs
    
    def load(self) -> List[Dict[str, Any]]:
        """Load data from CSV file."""
        df = pd.read_csv(self.path, **self.kwargs)
        return df.to_dict('records')


class JSONLDataSource(CustomDataSource):
    """JSONL file data source."""
    
    def __init__(self, path: str):
        self.path = path
    
    def load(self) -> List[Dict[str, Any]]:
        """Load data from JSONL file."""
        import json
        data = []
        with open(self.path, 'r') as f:
            for line in f:
                data.append(json.loads(line.strip()))
        return data


class PandasDataSource(CustomDataSource):
    """Pandas DataFrame data source."""
    
    def __init__(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe
    
    def load(self) -> List[Dict[str, Any]]:
        """Load data from pandas DataFrame."""
        return self.dataframe.to_dict('records')


class YouTubeDataSource(CustomDataSource):
    """YouTube data source (placeholder for API integration)."""
    
    def __init__(self, api_key: str, query: str, max_results: int = 100):
        self.api_key = api_key
        self.query = query
        self.max_results = max_results
    
    def load(self) -> List[Dict[str, Any]]:
        """Load data from YouTube API."""
        # Placeholder implementation
        # In real implementation, this would use YouTube Data API
        return [
            {
                "title": f"Sample YouTube video {i}",
                "description": f"Sample description for video {i}",
                "view_count": 1000 * i,
                "like_count": 100 * i,
                "age_rating": 13 if i % 2 else 8
            }
            for i in range(min(self.max_results, 10))
        ]


class RedditDataSource(CustomDataSource):
    """Reddit data source (placeholder for API integration)."""
    
    def __init__(self, subreddit: str, limit: int = 100):
        self.subreddit = subreddit
        self.limit = limit
    
    def load(self) -> List[Dict[str, Any]]:
        """Load data from Reddit API."""
        # Placeholder implementation
        # In real implementation, this would use Reddit API (PRAW)
        return [
            {
                "title": f"Sample Reddit post {i}",
                "text": f"Sample content for post {i}",
                "score": 50 * i,
                "num_comments": 10 * i,
                "sentiment": "positive" if i % 2 else "negative"
            }
            for i in range(min(self.limit, 10))
        ]


# Built-in enrichment functions
def add_text_length(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add text length features to data."""
    for item in data:
        # Look for text fields and add length
        for key, value in item.items():
            if isinstance(value, str) and key in ['text', 'content', 'description', 'title']:
                item[f"{key}_length"] = len(value)
    return data


def add_word_count(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add word count features to data."""
    for item in data:
        for key, value in item.items():
            if isinstance(value, str) and key in ['text', 'content', 'description', 'title']:
                item[f"{key}_word_count"] = len(value.split())
    return data


def add_sentiment_features(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add basic sentiment features to data."""
    # Simple keyword-based sentiment (in real implementation, use proper sentiment analysis)
    positive_words = ['good', 'great', 'excellent', 'amazing', 'awesome', 'love', 'like']
    negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'horrible']
    
    for item in data:
        for key, value in item.items():
            if isinstance(value, str) and key in ['text', 'content', 'description', 'title']:
                text_lower = value.lower()
                positive_count = sum(1 for word in positive_words if word in text_lower)
                negative_count = sum(1 for word in negative_words if word in text_lower)
                
                item[f"{key}_positive_sentiment"] = positive_count
                item[f"{key}_negative_sentiment"] = negative_count
                item[f"{key}_sentiment_score"] = positive_count - negative_count
    return data


def add_readability_metrics(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add basic readability metrics to data."""
    for item in data:
        for key, value in item.items():
            if isinstance(value, str) and key in ['text', 'content', 'description']:
                sentences = value.count('.') + value.count('!') + value.count('?')
                words = len(value.split())
                
                # Simple readability approximation
                if sentences > 0:
                    avg_words_per_sentence = words / sentences
                    item[f"{key}_avg_words_per_sentence"] = avg_words_per_sentence
                    
                    # Simple complexity score
                    long_words = len([w for w in value.split() if len(w) > 6])
                    complexity = (long_words / words) if words > 0 else 0
                    item[f"{key}_complexity"] = complexity
    return data


def extract_domain_features(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract domain-specific features."""
    for item in data:
        # YouTube-specific features
        if 'view_count' in item:
            item['popularity_category'] = 'high' if item['view_count'] > 100000 else 'medium' if item['view_count'] > 10000 else 'low'
        
        # Reddit-specific features
        if 'score' in item:
            item['engagement_level'] = 'high' if item['score'] > 100 else 'medium' if item['score'] > 10 else 'low'
        
        # General content features
        if 'title' in item:
            title = item['title'].lower()
            item['has_question'] = '?' in title
            item['has_exclamation'] = '!' in title
            item['title_caps_ratio'] = sum(1 for c in item['title'] if c.isupper()) / len(item['title']) if item['title'] else 0
    
    return data


# Built-in preprocessing functions
def clean_text_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Clean text fields in data."""
    import re
    
    for item in data:
        for key, value in item.items():
            if isinstance(value, str) and key in ['text', 'content', 'description', 'title']:
                # Basic text cleaning
                cleaned = re.sub(r'http\S+', '', value)  # Remove URLs
                cleaned = re.sub(r'@\w+', '', cleaned)   # Remove mentions
                cleaned = re.sub(r'#\w+', '', cleaned)   # Remove hashtags
                cleaned = re.sub(r'\s+', ' ', cleaned)   # Normalize whitespace
                cleaned = cleaned.strip()
                item[key] = cleaned
    
    return data


def normalize_labels(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalize label values."""
    for item in data:
        # Normalize common label fields
        for label_field in ['label', 'target', 'class', 'sentiment']:
            if label_field in item:
                value = item[label_field]
                if isinstance(value, str):
                    # Normalize text labels
                    item[label_field] = value.lower().strip()
                elif isinstance(value, (int, float)):
                    # Ensure numeric labels are properly typed
                    item[label_field] = float(value)
    
    return data


def remove_duplicate_entries(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate entries from data."""
    seen = set()
    unique_data = []
    
    for item in data:
        # Create a simple hash of the item for deduplication
        # Use text content as primary deduplication key
        content_key = None
        for key in ['text', 'content', 'description', 'title']:
            if key in item:
                content_key = item[key]
                break
        
        if content_key and content_key not in seen:
            seen.add(content_key)
            unique_data.append(item)
        elif not content_key:
            # If no text content, keep the item
            unique_data.append(item)
    
    return unique_data


def balance_dataset(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Balance dataset by label distribution."""
    # Find the primary label field
    label_field = None
    for field in ['label', 'target', 'class', 'sentiment']:
        if field in data[0] if data else {}:
            label_field = field
            break
    
    if not label_field:
        return data  # No label field found, return as is
    
    # Group by label
    label_groups = {}
    for item in data:
        label = item[label_field]
        if label not in label_groups:
            label_groups[label] = []
        label_groups[label].append(item)
    
    # Find minimum group size
    min_size = min(len(group) for group in label_groups.values())
    
    # Sample equal number from each group
    balanced_data = []
    for group in label_groups.values():
        # Simple random sampling (in practice, might want stratified sampling)
        import random
        balanced_data.extend(random.sample(group, min_size))
    
    return balanced_data


# Global registry instance
data_registry = DataSourceRegistry()


def get_data_registry() -> DataSourceRegistry:
    """Get the global data source registry."""
    return data_registry