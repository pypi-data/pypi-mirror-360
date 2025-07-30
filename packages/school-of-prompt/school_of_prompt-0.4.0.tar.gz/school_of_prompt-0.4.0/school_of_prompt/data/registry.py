"""
Data source registry system for pluggable data sources.
Enables custom data sources and enrichment pipelines.
"""

import hashlib
import json
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type

import pandas as pd

from ..core.simple_interfaces import CustomDataSource
from ..production.cache import IntelligentCache


class CachedAPIDataSource(CustomDataSource):
    """Base class for API data sources with intelligent caching."""

    def __init__(self, cache_enabled: bool = True, cache_expiry: str = "24h", **kwargs):
        self.cache_enabled = cache_enabled
        self.cache_expiry = cache_expiry
        self.cache = (
            IntelligentCache(
                cache_dir=".cache/school_of_prompt/api_data",
                default_expiry=cache_expiry,
                enabled=cache_enabled,
            )
            if cache_enabled
            else None
        )

        # Store API parameters for cache key generation
        self.api_params = kwargs

    def load(self) -> List[Dict[str, Any]]:
        """Load data with caching support."""
        if not self.cache_enabled:
            return self._fetch_from_api()

        # Generate cache key from API parameters
        cache_key = self._generate_cache_key()

        # Try to get from cache first
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            print(f"✅ Using cached data for {self.__class__.__name__}")
            return cached_data

        # Fetch from API and cache the result
        print(f"🌐 Fetching fresh data from {self.__class__.__name__} API")
        data = self._fetch_from_api()

        if data:
            self.cache.set(cache_key, data, expiry=self.cache_expiry)
            print(f"💾 Cached {len(data)} items from {self.__class__.__name__}")

        return data

    def _generate_cache_key(self) -> str:
        """Generate a unique cache key from API parameters."""
        # Create a stable hash from API parameters
        key_data = {"source_class": self.__class__.__name__, "params": self.api_params}
        key_str = json.dumps(key_data, sort_keys=True)
        # Use SHA256 for cache key generation (not for security, just uniqueness)
        return hashlib.sha256(key_str.encode()).hexdigest()[
            :16
        ]  # Truncate for readability

    def _fetch_from_api(self) -> List[Dict[str, Any]]:
        """Fetch data from the actual API. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement _fetch_from_api")


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
        return df.to_dict("records")


class JSONLDataSource(CustomDataSource):
    """JSONL file data source."""

    def __init__(self, path: str):
        self.path = path

    def load(self) -> List[Dict[str, Any]]:
        """Load data from JSONL file."""
        import json

        data = []
        with open(self.path, "r") as f:
            for line in f:
                data.append(json.loads(line.strip()))
        return data


class PandasDataSource(CustomDataSource):
    """Pandas DataFrame data source."""

    def __init__(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe

    def load(self) -> List[Dict[str, Any]]:
        """Load data from pandas DataFrame."""
        return self.dataframe.to_dict("records")


class YouTubeDataSource(CachedAPIDataSource):
    """YouTube data source with intelligent caching."""

    def __init__(
        self,
        api_key: str,
        query: str,
        max_results: int = 100,
        cache_enabled: bool = True,
        cache_expiry: str = "6h",
    ):
        # Store specific parameters for this API
        super().__init__(
            cache_enabled=cache_enabled,
            cache_expiry=cache_expiry,
            api_key=api_key[:8] + "...",  # Don't cache full API key for security
            query=query,
            max_results=max_results,
        )
        self.api_key = api_key
        self.query = query
        self.max_results = max_results

    def _fetch_from_api(self) -> List[Dict[str, Any]]:
        """Fetch data from YouTube API."""
        # Placeholder implementation - in real use, this would call YouTube Data API
        # Example using google-api-python-client:
        #
        # from googleapiclient.discovery import build
        # youtube = build('youtube', 'v3', developerKey=self.api_key)
        # request = youtube.search().list(
        #     part='snippet',
        #     q=self.query,
        #     maxResults=self.max_results,
        #     type='video'
        # )
        # response = request.execute()
        # return [self._parse_youtube_item(item) for item in response['items']]

        # For now, return sample data that simulates real API response
        import time

        time.sleep(0.5)  # Simulate API call delay

        return [
            {
                "video_id": f"video_{i}_{hash(self.query) % 10000}",
                "title": f"YouTube video about '{self.query}' #{i}",
                "description": f"This is a sample video description for query '{self.query}' - video {i}",
                "channel_title": f"Channel_{i % 5}",
                "view_count": 1000 * (i + 1),
                "like_count": 100 * (i + 1),
                "published_at": f"2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
                "duration": f"PT{(i % 10) + 1}M{(i % 60)}S",
                "age_rating": 13 if i % 3 == 0 else (8 if i % 2 == 0 else 16),
            }
            for i in range(min(self.max_results, 20))
        ]


class RedditDataSource(CachedAPIDataSource):
    """Reddit data source with intelligent caching."""

    def __init__(
        self,
        subreddit: str,
        limit: int = 100,
        sort: str = "hot",
        cache_enabled: bool = True,
        cache_expiry: str = "2h",
    ):
        # Store specific parameters for this API
        super().__init__(
            cache_enabled=cache_enabled,
            cache_expiry=cache_expiry,
            subreddit=subreddit,
            limit=limit,
            sort=sort,
        )
        self.subreddit = subreddit
        self.limit = limit
        self.sort = sort

    def _fetch_from_api(self) -> List[Dict[str, Any]]:
        """Fetch data from Reddit API."""
        # Placeholder implementation - in real use, this would use PRAW:
        #
        # import praw
        # reddit = praw.Reddit(
        #     client_id=self.client_id,
        #     client_secret=self.client_secret,
        #     user_agent=self.user_agent
        # )
        # subreddit = reddit.subreddit(self.subreddit)
        # posts = getattr(subreddit, self.sort)(limit=self.limit)
        # return [self._parse_reddit_post(post) for post in posts]

        # For now, return sample data that simulates real API response
        import time

        time.sleep(0.3)  # Simulate API call delay

        return [
            {
                "post_id": f"post_{i}_{hash(self.subreddit) % 10000}",
                "title": f"Reddit post from r/{self.subreddit} #{i}",
                "text": f"This is sample content from r/{self.subreddit} post {i}. "
                * (i % 3 + 1),
                "author": f"user_{i % 10}",
                "score": max(1, 50 * i - (i % 7) * 20),  # Simulate varying scores
                "upvote_ratio": 0.8 + (i % 20) * 0.01,
                "num_comments": 10 * (i + 1),
                "created_utc": f"2024-07-{(i % 30) + 1:02d}T{(i % 24):02d}:00:00Z",
                "subreddit": self.subreddit,
                "url": f"https://reddit.com/r/{self.subreddit}/comments/sample_{i}",
                "is_video": i % 8 == 0,
                "over_18": i % 15 == 0,
                "sentiment": (
                    "positive"
                    if i % 3 == 0
                    else ("negative" if i % 3 == 1 else "neutral")
                ),
            }
            for i in range(min(self.limit, 25))
        ]


# Built-in enrichment functions
def add_text_length(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add text length features to data."""
    for item in data:
        # Look for text fields and add length
        for key, value in item.items():
            if isinstance(value, str) and key in [
                "text",
                "content",
                "description",
                "title",
            ]:
                item[f"{key}_length"] = len(value)
    return data


def add_word_count(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add word count features to data."""
    for item in data:
        for key, value in item.items():
            if isinstance(value, str) and key in [
                "text",
                "content",
                "description",
                "title",
            ]:
                item[f"{key}_word_count"] = len(value.split())
    return data


def add_sentiment_features(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add basic sentiment features to data."""
    # Simple keyword-based sentiment (in real implementation, use proper sentiment analysis)
    positive_words = [
        "good",
        "great",
        "excellent",
        "amazing",
        "awesome",
        "love",
        "like",
    ]
    negative_words = ["bad", "terrible", "awful", "hate", "dislike", "horrible"]

    for item in data:
        for key, value in item.items():
            if isinstance(value, str) and key in [
                "text",
                "content",
                "description",
                "title",
            ]:
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
            if isinstance(value, str) and key in ["text", "content", "description"]:
                sentences = value.count(".") + value.count("!") + value.count("?")
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
        if "view_count" in item:
            item["popularity_category"] = (
                "high"
                if item["view_count"] > 100000
                else "medium" if item["view_count"] > 10000 else "low"
            )

        # Reddit-specific features
        if "score" in item:
            item["engagement_level"] = (
                "high"
                if item["score"] > 100
                else "medium" if item["score"] > 10 else "low"
            )

        # General content features
        if "title" in item:
            title = item["title"].lower()
            item["has_question"] = "?" in title
            item["has_exclamation"] = "!" in title
            item["title_caps_ratio"] = (
                sum(1 for c in item["title"] if c.isupper()) / len(item["title"])
                if item["title"]
                else 0
            )

    return data


# Built-in preprocessing functions
def clean_text_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Clean text fields in data."""
    import re

    for item in data:
        for key, value in item.items():
            if isinstance(value, str) and key in [
                "text",
                "content",
                "description",
                "title",
            ]:
                # Basic text cleaning
                cleaned = re.sub(r"http\S+", "", value)  # Remove URLs
                cleaned = re.sub(r"@\w+", "", cleaned)  # Remove mentions
                cleaned = re.sub(r"#\w+", "", cleaned)  # Remove hashtags
                cleaned = re.sub(r"\s+", " ", cleaned)  # Normalize whitespace
                cleaned = cleaned.strip()
                item[key] = cleaned

    return data


def normalize_labels(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalize label values."""
    for item in data:
        # Normalize common label fields
        for label_field in ["label", "target", "class", "sentiment"]:
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
        for key in ["text", "content", "description", "title"]:
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
    for field in ["label", "target", "class", "sentiment"]:
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

        balanced_data.extend(
            random.sample(group, min_size)
        )  # nosec B311

    return balanced_data


# Global registry instance
data_registry = DataSourceRegistry()


def get_data_registry() -> DataSourceRegistry:
    """Get the global data source registry."""
    return data_registry
