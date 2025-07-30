# School of Prompt 🎸

**Simple, powerful prompt optimization with minimal boilerplate.**

*Inspired by School of Rock - where every prompt can become a legend.*

## Quick Start

```python
from school_of_prompt import optimize

# That's it! One function call to optimize prompts
results = optimize(
    data="band_reviews.csv",
    task="classify sentiment", 
    prompts=["How does this fan feel about our band?", "Is this review positive or negative?"],
    api_key="sk-..."
)

print(f"Best prompt: {results['best_prompt']}")
print(f"Accuracy: {results['best_score']:.2f}")
```

## Installation

```bash
pip install school-of-prompt
```

## Features

## Features

### 🚀 **Level 0: Dead Simple**
Perfect for quick experiments and getting started.

```python
results = optimize(
    data="band_reviews.csv",
    task="classify sentiment",
    prompts=["How do fans feel about this?", "Analyze sentiment"],
    api_key="sk-..."
)
```

### 🎛️ **Level 1: Configuration-Driven**
Enterprise-grade configuration with YAML files.

```python
# Use YAML configuration for complex setups
results = optimize(config="youtube_age_rating.yaml")

# Or enhanced API with advanced features
results = optimize(
    data="student_performances.csv",
    task="rate performance from 1-10",
    prompts="prompts/performance_variants.txt",
    model={"name": "gpt-4", "temperature": 0.1},
    metrics=["mae", "within_1", "within_2", "valid_rate"],  # Advanced metrics
    sampling_strategy="stratified",  # Smart sampling
    cross_validation=True,  # Statistical rigor
    k_fold=5,
    cache_enabled=True,  # Production caching
    comprehensive_analysis=True,  # Deep insights
    api_key="sk-..."
)
```

### 🔧 **Level 2: Enterprise & Multi-Dataset**
Full enterprise features with custom implementations.

```python
from school_of_prompt import optimize, CustomMetric
from school_of_prompt.data.registry import get_data_registry

# Register custom data enrichers
registry = get_data_registry()
registry.register_enricher("domain_features", extract_youtube_features)

# Multi-dataset enterprise workflow
results = optimize(
    data={
        "training": "datasets/youtube_train.csv",
        "validation": "datasets/youtube_val.csv", 
        "test": "datasets/youtube_test.csv"
    },
    task="rate age appropriateness from 0-18",
    prompts=["Age rating for: {title}", "Appropriate age: {title}"],
    metrics=["mae", "within_1", "within_2", "r2_score", "valid_rate"],
    enrichers=["text_length", "readability", "domain_features"],
    preprocessors=["clean_text", "normalize_labels"],
    cross_validation=True,
    comprehensive_analysis=True,
    parallel_evaluation=True,
    api_key="sk-..."
)

# Access advanced analysis
print(f"Statistical significance: {results['comprehensive_analysis']['statistical_significance']}")
print(f"Error patterns: {results['comprehensive_analysis']['error_analysis']}")
print(f"Recommendations: {results['comprehensive_analysis']['recommendations']}")
```

## 🏢 Enterprise Features

### 📊 **Advanced Metrics & Evaluation**
- **Tolerance-based**: `within_1`, `within_2`, `within_3` for ±N accuracy
- **Domain-specific**: `valid_rate`, `token_efficiency`, `response_quality`
- **Statistical**: `r2_score`, `prediction_confidence`, `error_std`, `median_error`
- **Significance testing**: Paired t-tests between prompt variants
- **Confidence intervals**: Statistical confidence for all results

### ⚙️ **Configuration-Driven Approach**
```yaml
# youtube_age_rating.yaml
task:
  name: "youtube_age_rating"
  type: "regression" 
  target_range: [0, 18]

datasets:
  training: "datasets/youtube_train.csv"
  validation: "datasets/youtube_val.csv"
  test: "datasets/youtube_test.csv"

evaluation:
  metrics: ["mae", "within_1", "within_2", "valid_rate"]
  sampling_strategy: "stratified"
  cross_validation: true
  k_fold: 5

cache:
  enabled: true
  expiry: "24h"

batch_processing:
  parallel_evaluation: true
  chunk_size: 100
```

### 🚀 **Production-Ready Features**
- **Intelligent caching**: 24h expiry, size management, LRU eviction
- **Batch processing**: Parallel evaluation with progress tracking
- **Error handling**: Retry logic, circuit breakers, graceful degradation
- **Multi-dataset workflows**: Training/validation/test dataset support
- **Cross-validation**: K-fold cross-validation for robust evaluation

### 🔍 **Comprehensive Analysis**
- **Error pattern detection**: Common errors, bias analysis, prediction patterns
- **Performance breakdown**: Analysis by category, difficulty, content length
- **Statistical significance**: Rigorous testing between prompt variants
- **Actionable recommendations**: Data-driven suggestions for improvement

## Smart Defaults

The framework automatically handles common scenarios:

### 📊 **Auto Data Loading & Enrichment**
- **CSV files**: `data="band_reviews.csv"`
- **JSONL files**: `data="performances.jsonl"`
- **DataFrames**: `data=my_dataframe`
- **Multi-datasets**: `data={"train": "train.csv", "test": "test.csv"}`
- **Custom sources**: `data=MyDataSource()`
- **Enrichment pipeline**: Automatic text analysis, readability, sentiment features
- **Preprocessing**: Text cleaning, label normalization, deduplication
- **Smart sampling**: Random, stratified, and balanced sampling strategies

### 🎯 **Auto Task Detection**
- **"classify sentiment"** → Sentiment classification
- **"rate from 1-10"** → Performance rating task  
- **"categorize content"** → Multi-class classification
- **"generate summary"** → Text generation

### 📏 **Auto Metrics Selection**
- **Classification** → Accuracy, F1-score, precision, recall, valid_rate
- **Regression** → MAE, RMSE, R²-score, within_1, within_2, within_3
- **Generation** → response_quality, token_efficiency, valid_rate
- **All tasks** → Automatic selection based on task type and target range

### 🤖 **Auto Model Setup**
- **String**: `model="gpt-4"` 
- **Config**: `model={"name": "gpt-4", "temperature": 0.1}`
- **Custom**: `model=MyModel()`

## Rock Star Examples

### 🎸 Band Review Sentiment Analysis
```python
results = optimize(
    data="fan_reviews.csv",
    task="classify sentiment",
    prompts=[
        "How does this fan feel about our band performance?",
        "Is this review positive, negative, or neutral?",
        "Fan reaction analysis: {review}"
    ],
    api_key=os.getenv("OPENAI_API_KEY")
)
```

### 🥁 Student Performance Rating
```python
results = optimize(
    data="student_performances.csv", 
    task="rate performance from 1-10",
    prompts=[
        "Rate this {instrument} performance from 1-10: {performance}",
        "As a rock teacher, how would you score this?",
        "School of Rock grade: {performance}"
    ],
    model="gpt-4",
    metrics=["mae", "accuracy"]
)
```

### 🛡️ Content Safety for Young Rockers
```python
results = optimize(
    data="song_lyrics.csv",
    task="classify content as school-appropriate", 
    prompts="prompts/safety_check.txt",
    model={
        "name": "gpt-4",
        "temperature": 0.0,
        "max_tokens": 20
    },
    sample_size=500
)
```

### 🎬 Age Rating Classification
```python
results = optimize(
    data="youtube_videos.csv",
    task="rate appropriate age from 0-18",
    prompts=[
        "What age is appropriate for: {title} - {description}",
        "Age rating for: {title}. Content: {description}",
        "Minimum age for this content: {title}"
    ],
    model="gpt-3.5-turbo",
    metrics=["mae", "accuracy"]
)
```

## API Reference

### `optimize()`

The main optimization function - rock your prompts!

**Parameters:**
- **`data`** *(str|DataFrame|CustomDataSource)*: Your dataset
- **`task`** *(str|CustomTask)*: Task description or custom task
- **`prompts`** *(str|List[str]|Path)*: Prompt variants to test
- **`model`** *(str|dict|CustomModel)*: Model configuration
- **`metrics`** *(List[str]|List[CustomMetric])*: Evaluation metrics
- **`api_key`** *(str)*: API key (or set `OPENAI_API_KEY` env var)
- **`sample_size`** *(int)*: Limit evaluation to N samples
- **`random_seed`** *(int)*: For reproducible sampling
- **`output_dir`** *(str)*: Save detailed results
- **`verbose`** *(bool)*: Print progress

**Returns:**
```python
{
    "best_prompt": "How does this fan feel about our band?",
    "best_score": 0.892,
    "prompts": {
        "prompt_1": {"scores": {"accuracy": 0.856, "f1_score": 0.834}},
        "prompt_2": {"scores": {"accuracy": 0.892, "f1_score": 0.889}}
    },
    "summary": {"metrics": {...}},
    "details": [...]
}
```

## Environment Setup

```bash
# Set your API key
export OPENAI_API_KEY="sk-your-key-here"

# Or pass directly
results = optimize(..., api_key="sk-your-key-here")
```

## Data Format

Your data should have:
- **Input columns**: Text or features to analyze
- **Label column**: Ground truth (named `label`, `target`, `class`, etc.)

**CSV Example:**
```csv
review,sentiment
"The band was amazing!",positive
"Terrible performance.",negative
"It was okay.",neutral
```

**JSONL Example:**
```json
{"review": "The band was amazing!", "sentiment": "positive"}
{"review": "Terrible performance.", "sentiment": "negative"}
```

## Extension Points

For advanced rockers who need custom behavior:

```python
from school_of_prompt import CustomMetric, CustomDataSource, CustomModel, CustomTask
from school_of_prompt.data.registry import get_data_registry

# Custom metrics with domain-specific logic
class MyRockMetric(CustomMetric):
    name = "rock_factor"
    def calculate(self, predictions, actuals):
        return calculate_rock_awesomeness(predictions, actuals)

# Register custom data enrichers
registry = get_data_registry()
registry.register_enricher("rock_features", extract_rock_features)
registry.register_preprocessor("rock_cleaner", clean_rock_data)

# Custom data sources with enrichment
class MyDataSource(CustomDataSource):
    def load(self):
        return load_from_rock_database()

# Enterprise workflow with custom components
results = optimize(
    data=MyDataSource(),
    task=MyCustomTask(),
    prompts=dynamic_prompt_generator,
    metrics=[MyRockMetric(), "accuracy", "within_1"],
    enrichers=["rock_features", "text_length"],
    preprocessors=["rock_cleaner", "normalize_labels"],
    cross_validation=True,
    comprehensive_analysis=True,
    api_key="sk-..."
)
```

## 🎯 What's New in v0.3.0

### ✅ **Completed Enterprise Features**
- ✅ **Advanced Metrics**: Tolerance-based, domain-specific, statistical metrics
- ✅ **Configuration System**: Full YAML configuration support  
- ✅ **Production Features**: Intelligent caching, batch processing, error handling
- ✅ **Multi-Dataset Support**: Training/validation/test workflows
- ✅ **Cross-Validation**: K-fold cross-validation with statistical rigor
- ✅ **Comprehensive Analysis**: Statistical significance, error patterns, recommendations
- ✅ **Data Registry**: Pluggable data sources and enrichment pipelines

### 🔮 **Future Roadmap**
- **More Models**: Anthropic Claude, local models, Azure OpenAI
- **Auto Optimization**: Genetic algorithms, Bayesian optimization  
- **Real-time Evaluation**: Streaming evaluation for large datasets
- **Advanced Visualizations**: Interactive charts and dashboards

## Contributing

We'd love your help! Rock on and contribute to make this even better.

## License

MIT License. Rock freely! 🤘

---

**School of Prompt: Where prompts learn to rock!** 🎸

*"You're not hardcore unless you optimize hardcore!"* - Dewey Finn (probably)