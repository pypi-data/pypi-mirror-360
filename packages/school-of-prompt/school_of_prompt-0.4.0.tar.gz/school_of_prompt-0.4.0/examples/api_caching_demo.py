"""
API Data Source Caching Demo
Demonstrates intelligent caching for external API data sources.

This example shows how School of Prompt automatically caches API responses
to avoid repeated calls, rate limiting, and API costs.
"""

import os
import time

from school_of_prompt import optimize
from school_of_prompt.data.registry import get_data_registry


def demo_api_caching():
    """Demonstrate API caching with YouTube and Reddit data sources."""

    print("🎬 API Data Source Caching Demo")
    print("=" * 50)

    # Get the data registry
    registry = get_data_registry()

    # Create YouTube data source with caching enabled
    youtube_source = registry.get_source(
        "youtube",
        api_key="demo_key_12345678",  # In real use, use actual API key
        query="prompt engineering tutorials",
        max_results=15,
        cache_enabled=True,
        cache_expiry="6h",  # Cache for 6 hours
    )

    # Create Reddit data source with caching
    reddit_source = registry.get_source(
        "reddit",
        subreddit="MachineLearning",
        limit=20,
        sort="hot",
        cache_enabled=True,
        cache_expiry="2h",  # Cache for 2 hours
    )

    print("\n🌐 First API Call (will fetch from 'API')")
    print("-" * 40)

    # First call - will simulate API fetch and cache result
    start_time = time.time()
    youtube_data = youtube_source.load()
    first_call_time = time.time() - start_time

    print(f"📊 YouTube data: {len(youtube_data)} videos")
    print(f"⏱️  First call took: {first_call_time:.2f} seconds")

    print("\n💾 Second API Call (should use cache)")
    print("-" * 40)

    # Second call - should use cached data (much faster)
    start_time = time.time()
    youtube_data_cached = youtube_source.load()
    second_call_time = time.time() - start_time

    print(f"📊 YouTube data: {len(youtube_data_cached)} videos")
    print(f"⚡ Second call took: {second_call_time:.2f} seconds")
    print(
        f"🚀 Speed improvement: {first_call_time / max(second_call_time, 0.001):.1f}x faster"
    )

    print("\n📱 Reddit API Caching Test")
    print("-" * 40)

    # Test Reddit source caching
    start_time = time.time()
    reddit_data = reddit_source.load()
    reddit_first_time = time.time() - start_time

    start_time = time.time()
    reddit_data_cached = reddit_source.load()
    reddit_second_time = time.time() - start_time

    print(f"📊 Reddit data: {len(reddit_data)} posts")
    print(
        f"⏱️  First call: {reddit_first_time:.2f}s, Second call: {reddit_second_time:.2f}s"
    )
    print(
        f"🚀 Speed improvement: {reddit_first_time / max(reddit_second_time, 0.001):.1f}x faster"
    )

    return youtube_data, reddit_data


def demo_cached_optimization():
    """Demonstrate optimization with cached API data sources."""

    print("\n\n🎯 Optimization with Cached API Data")
    print("=" * 50)

    # Note: This would use cached data if available from previous runs
    results = optimize(
        # Use YouTube API data source with caching
        data={
            "youtube": {
                "source": "youtube",
                "api_key": "demo_key_12345678",
                "query": "AI content rating",
                "max_results": 10,
                "cache_enabled": True,
                "cache_expiry": "6h",
            }
        },
        task="rate content appropriateness from 0-18",
        prompts=[
            "What age rating is appropriate for: {title}",
            "Age rating for content: {title} - {description}",
            "Minimum age for: {title}",
        ],
        # Advanced metrics
        metrics=["mae", "within_1", "within_2", "valid_rate"],
        # Cache LLM calls too
        cache_enabled=True,
        # Use sample API key (in real use, set OPENAI_API_KEY)
        api_key=os.getenv("OPENAI_API_KEY", "demo_key_for_testing"),
    )

    print(f"✅ Optimization complete!")
    print(f"📊 Best prompt: {results.get('best_prompt', 'N/A')[:60]}...")
    print(f"📈 Best score: {results.get('best_score', 'N/A')}")

    return results


def demo_cache_configuration():
    """Demonstrate different cache configurations for API sources."""

    print("\n\n⚙️ Cache Configuration Options")
    print("=" * 50)

    registry = get_data_registry()

    # Short-term cache (good for rapidly changing data)
    youtube_short = registry.get_source(
        "youtube",
        api_key="demo_key",
        query="trending topics",
        cache_enabled=True,
        cache_expiry="30m",  # 30 minutes
    )

    # Long-term cache (good for stable data)
    youtube_long = registry.get_source(
        "youtube",
        api_key="demo_key",
        query="educational content",
        cache_enabled=True,
        cache_expiry="24h",  # 24 hours
    )

    # No cache (always fresh data)
    youtube_no_cache = registry.get_source(
        "youtube", api_key="demo_key", query="live content", cache_enabled=False
    )

    print("✅ Configuration examples:")
    print("  🕰️  Short-term cache (30m): Good for trending/rapidly changing data")
    print("  📅 Long-term cache (24h): Good for stable/educational content")
    print("  🔄 No cache: Always fresh data for live/real-time content")

    # Show cache statistics
    if hasattr(youtube_short.cache, "get_stats"):
        stats = youtube_short.cache.get_stats()
        print(f"\n📊 Cache statistics: {stats}")


def main():
    """Run all caching demos."""

    print("🎸 School of Prompt - API Caching Capabilities Demo")
    print("=" * 60)
    print()
    print("This demo shows how School of Prompt provides intelligent caching")
    print("for external API data sources like YouTube and Reddit.")
    print()

    try:
        # Demo basic API caching
        youtube_data, reddit_data = demo_api_caching()

        # Demo cache configuration options
        demo_cache_configuration()

        print("\n\n🎯 Key Benefits of API Caching:")
        print("✅ Faster repeated experiments (avoid redundant API calls)")
        print("✅ Reduced API costs (pay once, use multiple times)")
        print("✅ Rate limit protection (avoid hitting API quotas)")
        print("✅ Offline capability (work with cached data)")
        print("✅ Configurable expiry (balance freshness vs performance)")

        print(
            f"\n💡 Pro Tip: API data is cached in '.cache/school_of_prompt/api_data/'"
        )
        print(f"    You can safely delete this folder to clear all API caches.")

    except Exception as e:
        print(f"❌ Demo error: {e}")
        print("💡 This is a demonstration - in real use, provide actual API keys")


if __name__ == "__main__":
    main()
