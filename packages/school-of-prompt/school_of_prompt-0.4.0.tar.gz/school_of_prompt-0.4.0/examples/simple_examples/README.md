# School of Prompt Examples

Complete, runnable examples demonstrating the `optimize()` API. Each example shows different features and use cases.

## Quick Start

1. **Set your API key:**
   ```bash
   export OPENAI_API_KEY="sk-your-key-here"
   ```

2. **Run any example:**
   ```bash
   python band_sentiment_analysis.py
   python student_performance_rating.py
   python rock_content_safety.py
   ```

## Examples

### `band_sentiment_analysis.py`
**Sentiment classification with default settings**
- Basic sentiment classification task
- Multiple prompt variants for comparison
- Uses default metrics (accuracy, F1-score)
- Demonstrates automatic task detection

### `student_performance_rating.py` 
**Regression task with custom metrics**
- Performance rating task (1-10 scale)
- MAE (Mean Absolute Error) evaluation
- Shows prediction vs actual comparison
- Custom model configuration

### `rock_content_safety.py`
**Content safety with custom metrics**
- Content classification with safety focus
- Custom metric implementation
- Model configuration (temperature=0.0)
- Multiple evaluation metrics

## Usage Pattern

Each example demonstrates the core API:

```python
from school_of_prompt import optimize

results = optimize(
    data="data.csv",
    task="classify sentiment",
    prompts=["Template 1", "Template 2"],
    api_key="sk-..."
)
```

## Extension Examples

See `rock_content_safety.py` for:
- **Custom metrics**: Domain-specific evaluation
- **Model configuration**: Temperature, max_tokens
- **Multiple metrics**: Combining standard and custom metrics

## Configuration Options

- Use `verbose=True` to see optimization progress
- Add `sample_size=100` to limit evaluation size
- Set `output_dir="results"` to save detailed results
- Configure models with `model={"name": "gpt-4", "temperature": 0.1}`

## Requirements

- OpenAI API key (set via environment variable)
- School of Prompt package installed
- Python 3.9+