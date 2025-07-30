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

### 🎛️ **Level 1: More Control**
Add configuration without complexity.

```python
results = optimize(
    data="student_performances.csv",
    task="rate performance from 1-10",
    prompts="prompts/performance_variants.txt",  # Read from file
    model={
        "name": "gpt-4", 
        "temperature": 0.1,
        "max_tokens": 50
    },
    metrics=["mae", "accuracy"],
    sample_size=1000,
    api_key="sk-..."
)
```

### 🔧 **Level 2: Full Extension**
Custom everything for advanced use cases.

```python
from school_of_prompt import optimize, CustomMetric, CustomDataSource

class RockStarMetric(CustomMetric):
    name = "rock_star_score"
    
    def calculate(self, predictions, actuals):
        # Your domain-specific metric
        return calculate_rock_star_potential(predictions, actuals)

results = optimize(
    data=CustomDataSource(my_database),
    task=MyCustomTask(),
    prompts=dynamic_prompt_generator,
    model=my_llm_wrapper,
    metrics=[RockStarMetric(), "accuracy"],
    api_key="sk-..."
)
```

## Smart Defaults

The framework automatically handles common scenarios:

### 📊 **Auto Data Loading**
- **CSV files**: `data="band_reviews.csv"`
- **JSONL files**: `data="performances.jsonl"`
- **DataFrames**: `data=my_dataframe`
- **Custom sources**: `data=MyDataSource()`

### 🎯 **Auto Task Detection**
- **"classify sentiment"** → Sentiment classification
- **"rate from 1-10"** → Performance rating task  
- **"categorize content"** → Multi-class classification
- **"generate summary"** → Text generation

### 📏 **Auto Metrics Selection**
- **Classification** → Accuracy, F1-score
- **Regression** → MAE, RMSE
- **Generation** → BLEU, ROUGE (coming soon)

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

class MyRockMetric(CustomMetric):
    name = "rock_factor"
    def calculate(self, predictions, actuals):
        return calculate_rock_awesomeness(predictions, actuals)

class MyDataSource(CustomDataSource):
    def load(self):
        return load_from_rock_database()

class MyModel(CustomModel):
    def generate(self, prompt):
        return my_rock_llm_call(prompt)

class MyTask(CustomTask):
    def format_prompt(self, template, sample):
        return template.format(**sample)
    
    def extract_prediction(self, response):
        return parse_rock_response(response)
    
    def get_ground_truth(self, sample):
        return sample["rock_rating"]
```

## Roadmap

- **More Models**: Anthropic Claude, local models, Azure OpenAI
- **More Metrics**: BLEU, ROUGE, custom domain metrics  
- **Auto Optimization**: Genetic algorithms, Bayesian optimization
- **Batch Processing**: Handle large datasets efficiently
- **Caching**: Speed up repeated evaluations

## Contributing

We'd love your help! Rock on and contribute to make this even better.

## License

MIT License. Rock freely! 🤘

---

**School of Prompt: Where prompts learn to rock!** 🎸

*"You're not hardcore unless you optimize hardcore!"* - Dewey Finn (probably)