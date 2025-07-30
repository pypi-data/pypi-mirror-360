"""
YouTube Age Rating with Enterprise Features
Example showcasing School of Prompt v0.3.0 advanced capabilities.

This example demonstrates:
- Multi-dataset workflows (training/validation/test)
- Advanced metrics (tolerance-based, statistical)
- Cross-validation and statistical significance testing
- Data enrichment and preprocessing
- Comprehensive analysis and recommendations
- Production caching and error handling
"""

import os

import pandas as pd

from school_of_prompt import optimize
from school_of_prompt.core.config import create_sample_config_file
from school_of_prompt.data.registry import get_data_registry


def create_sample_youtube_data():
    """Create sample YouTube video data for demonstration."""

    # Sample YouTube video data
    youtube_data = [
        {
            "title": "Fun Kids Animation",
            "description": "Colorful cartoon for children",
            "age_rating": 3,
        },
        {
            "title": "Educational Math Tutorial",
            "description": "Learn basic arithmetic",
            "age_rating": 6,
        },
        {
            "title": "Teen Dance Challenge",
            "description": "Popular dance moves tutorial",
            "age_rating": 13,
        },
        {
            "title": "Horror Movie Trailer",
            "description": "Scary scenes and jump scares",
            "age_rating": 17,
        },
        {
            "title": "Baby Lullaby Songs",
            "description": "Soothing music for babies",
            "age_rating": 0,
        },
        {
            "title": "Action Movie Clips",
            "description": "Intense fight scenes",
            "age_rating": 15,
        },
        {
            "title": "Science Experiment",
            "description": "Safe chemistry experiments",
            "age_rating": 8,
        },
        {
            "title": "Gaming Strategy Guide",
            "description": "Advanced gaming tips",
            "age_rating": 12,
        },
        {
            "title": "Cooking for Beginners",
            "description": "Simple recipe tutorial",
            "age_rating": 10,
        },
        {
            "title": "Mature Documentary",
            "description": "Adult themes and content",
            "age_rating": 18,
        },
        {
            "title": "Nursery Rhymes",
            "description": "Classic children's songs",
            "age_rating": 2,
        },
        {
            "title": "Teen Fashion Tips",
            "description": "Style advice for teenagers",
            "age_rating": 14,
        },
        {
            "title": "Adult Comedy Special",
            "description": "Mature humor and language",
            "age_rating": 18,
        },
        {
            "title": "Elementary Science",
            "description": "Basic science concepts",
            "age_rating": 7,
        },
        {
            "title": "High School Drama",
            "description": "Teen relationship stories",
            "age_rating": 13,
        },
    ]

    # Create training/validation/test splits
    train_data = youtube_data[:10]
    val_data = youtube_data[10:12]
    test_data = youtube_data[12:]

    # Save datasets
    os.makedirs("datasets", exist_ok=True)
    pd.DataFrame(train_data).to_csv("datasets/youtube_train.csv", index=False)
    pd.DataFrame(val_data).to_csv("datasets/youtube_val.csv", index=False)
    pd.DataFrame(test_data).to_csv("datasets/youtube_test.csv", index=False)

    print("✅ Created sample YouTube datasets:")
    print(f"  📁 Training: {len(train_data)} videos")
    print(f"  📁 Validation: {len(val_data)} videos")
    print(f"  📁 Test: {len(test_data)} videos")


def register_custom_enrichers():
    """Register custom data enrichment functions for YouTube content."""

    def extract_youtube_features(data):
        """Extract YouTube-specific features."""
        for item in data:
            title = item.get("title", "")
            description = item.get("description", "")

            # Content type classification
            if any(
                word in title.lower()
                for word in ["kids", "children", "baby", "nursery"]
            ):
                item["content_type"] = "children"
            elif any(
                word in title.lower() for word in ["teen", "teenager", "high school"]
            ):
                item["content_type"] = "teen"
            elif any(
                word in title.lower()
                for word in ["adult", "mature", "horror", "comedy special"]
            ):
                item["content_type"] = "adult"
            else:
                item["content_type"] = "general"

            # Content intensity
            intense_words = ["action", "horror", "scary", "intense", "fight", "mature"]
            calm_words = ["lullaby", "calm", "peaceful", "educational", "tutorial"]

            intense_count = sum(
                1
                for word in intense_words
                if word in (title + " " + description).lower()
            )
            calm_count = sum(
                1 for word in calm_words if word in (title + " " + description).lower()
            )

            item["intensity_score"] = intense_count - calm_count

            # Educational flag
            educational_words = [
                "tutorial",
                "learn",
                "educational",
                "science",
                "math",
                "cooking",
            ]
            item["is_educational"] = any(
                word in (title + " " + description).lower()
                for word in educational_words
            )

        return data

    # Register the enricher
    registry = get_data_registry()
    registry.register_enricher("youtube_features", extract_youtube_features)
    print("✅ Registered custom YouTube data enricher")


def run_enterprise_optimization():
    """Run enterprise-grade prompt optimization for YouTube age rating."""

    print("\n🚀 Running Enterprise YouTube Age Rating Optimization")
    print("=" * 60)

    # Define prompt variants to test
    youtube_prompts = [
        "What is the appropriate age rating (0-18) for this video: {title} - {description}",
        "Age rating for: {title}. Description: {description}. Rate from 0-18:",
        "Minimum age for this content: {title}",
        "Rate age appropriateness (0-18): {title}",
        "YouTube age rating: {title} | {description}",
    ]

    # Run optimization with all enterprise features
    results = optimize(
        # Multi-dataset approach
        data={
            "training": "datasets/youtube_train.csv",
            "validation": "datasets/youtube_val.csv",
            "test": "datasets/youtube_test.csv",
        },
        # Task configuration
        task="rate age appropriateness from 0-18",
        prompts=youtube_prompts,
        # Advanced metrics
        metrics=[
            "mae",
            "within_1",
            "within_2",
            "r2_score",
            "valid_rate",
            "prediction_confidence",
        ],
        # Statistical rigor
        cross_validation=True,
        k_fold=3,
        # Data enhancement
        enrichers=["youtube_features", "text_length", "readability"],
        preprocessors=["clean_text", "normalize_labels"],
        sampling_strategy="stratified",
        # Production features
        cache_enabled=True,
        parallel_evaluation=True,
        batch_size=50,
        # Comprehensive analysis
        comprehensive_analysis=True,
        # Output configuration
        output_dir="experiments/youtube_age_rating",
        verbose=True,
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    return results


def analyze_results(results):
    """Analyze and display comprehensive results."""

    print("\n" + "🏆" * 60)
    print("COMPREHENSIVE ANALYSIS RESULTS")
    print("🏆" * 60)

    # Basic results
    print(f"\n📊 Best Prompt: {results['best_prompt'][:80]}...")
    print(f"📈 Best Score (MAE): {results['best_score']:.3f}")

    # Multi-dataset results
    if "datasets" in results:
        print(f"\n📁 Multi-Dataset Performance:")
        for dataset_name, dataset_results in results["datasets"].items():
            print(f"  {dataset_name}: {dataset_results['best_score']:.3f}")

    # Cross-validation results
    if "cross_validation" in results:
        cv_results = results["cross_validation"]
        print(f"\n🔄 Cross-Validation Results:")
        print(f"  K-Fold: {cv_results['k_fold']}")
        for metric, score in cv_results["mean_scores"].items():
            std = cv_results["std_scores"].get(metric, 0)
            print(f"  {metric}: {score:.3f} ± {std:.3f}")

    # Comprehensive analysis
    if "comprehensive_analysis" in results:
        analysis = results["comprehensive_analysis"]

        print(f"\n🔍 Statistical Significance Testing:")
        for test_name, test_result in analysis["statistical_significance"].items():
            significance = (
                "✅ Significant" if test_result["significant"] else "❌ Not Significant"
            )
            print(f"  {test_name}: p={test_result['p_value']:.3f} {significance}")

        print(f"\n🚨 Error Analysis:")
        error_analysis = analysis["error_analysis"]
        print(f"  Total Errors: {error_analysis['total_errors']}")
        print(f"  Error Rate: {error_analysis['error_rate']:.2%}")

        if error_analysis["common_errors"]:
            print(f"  Most Common Error: {error_analysis['common_errors'][0]}")

        print(f"\n📊 Performance Breakdown:")
        breakdown = analysis["performance_breakdown"]
        print(f"  Overall Score: {breakdown['overall_score']:.3f}")

        if breakdown["by_category"]:
            print(f"  By Category: {breakdown['by_category']}")

        if breakdown["by_difficulty"]:
            print(f"  By Difficulty: {breakdown['by_difficulty']}")

        print(f"\n💡 Recommendations:")
        for i, recommendation in enumerate(analysis["recommendations"], 1):
            print(f"  {i}. {recommendation}")


def main():
    """Main execution function."""

    print("🎸 School of Prompt v0.3.0 - Enterprise YouTube Age Rating Demo")
    print("=" * 70)

    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Please set OPENAI_API_KEY environment variable")
        print("   This demo will run but API calls will fail")
        print("   Set: export OPENAI_API_KEY='sk-your-key-here'")
        print()

    try:
        # Setup
        create_sample_youtube_data()
        register_custom_enrichers()

        # Run enterprise optimization
        results = run_enterprise_optimization()

        # Analyze results
        analyze_results(results)

        print(f"\n✅ Enterprise optimization complete!")
        print(f"📁 Results saved to: experiments/youtube_age_rating/")

    except Exception as e:
        print(f"❌ Error during optimization: {e}")
        print("💡 Make sure you have set OPENAI_API_KEY environment variable")

    finally:
        # Cleanup
        import shutil

        if os.path.exists("datasets"):
            shutil.rmtree("datasets")
        print("🧹 Cleaned up demo files")


if __name__ == "__main__":
    main()
