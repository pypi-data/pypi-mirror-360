"""
Auto model creation with smart defaults.
"""

from typing import Union, Dict, Any
from ..core.simple_interfaces import SimpleModel


def auto_create_model(
    model: Union[str, Dict[str, Any], SimpleModel],
    api_key: str
) -> SimpleModel:
    """
    Auto-create model with smart defaults.

    Args:
        model: Model name, config dict, or custom model instance
        api_key: API key for the model

    Returns:
        SimpleModel instance
    """

    if isinstance(model, SimpleModel):
        return model

    if isinstance(model, str):
        # Simple model name - use defaults
        return _create_openai_model(model, api_key)

    if isinstance(model, dict):
        # Model config dict
        provider = model.get('provider', 'openai')
        name = model.get('name', 'gpt-3.5-turbo')

        if provider == 'openai':
            return _create_openai_model(name, api_key, **model)
        elif provider == 'anthropic':
            return _create_anthropic_model(name, api_key, **model)
        else:
            raise ValueError(f"Unsupported model provider: {provider}")

    raise ValueError(f"Unsupported model type: {type(model)}")


def _create_openai_model(name: str, api_key: str, **kwargs) -> SimpleModel:
    """Create OpenAI model with smart defaults."""

    try:
        import openai
    except ImportError:
        raise ImportError(
            "openai package required. Install with: pip install openai")

    client = openai.OpenAI(api_key=api_key)

    # Extract model parameters
    temperature = kwargs.get('temperature', 0.0)
    max_tokens = kwargs.get('max_tokens', 150)

    def generate_func(prompt: str) -> str:
        try:
            response = client.completions.create(
                model=name,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].text.strip()
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")

    return SimpleModel(generate_func)


def _create_anthropic_model(name: str, api_key: str, **kwargs) -> SimpleModel:
    """Create Anthropic model with smart defaults."""

    try:
        import anthropic
    except ImportError:
        raise ImportError(
            "anthropic package required. Install with: pip install anthropic")

    client = anthropic.Anthropic(api_key=api_key)

    # Extract model parameters
    temperature = kwargs.get('temperature', 0.0)
    max_tokens = kwargs.get('max_tokens', 150)

    def generate_func(prompt: str) -> str:
        try:
            response = client.completions.create(
                model=name,
                prompt=prompt,
                temperature=temperature,
                max_tokens_to_sample=max_tokens
            )
            return response.completion.strip()
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {e}")

    return SimpleModel(generate_func)
