# Groundit

**Add verifiability and trustworthiness to AI outputs with source references and confidence scores.**

Groundit transforms AI data extraction into auditable, verifiable outputs. Every extracted value comes with confidence scores based on token probabilities and source quotes linking back to the original document.


## Key Features

- **Source Tracking**: Every extracted value includes the source quote (and its starting and ending char index) from the source document
- **Confidence Scoring**: Token-level probability analysis provides confidence scores for extracted data
- **Type Preservation**: Works seamlessly with Pydantic models and JSON schemas
- **Simple API**: One function call handles the complete extraction pipeline

## Installation

```bash
uv add groundit
```

## Quick Start

```python
from groundit import groundit
from pydantic import BaseModel, Field

os.environ["OPENAI_API_KEY"] = "sk-..."

# Define your data model
class Patient(BaseModel):
    name: str = Field(description="Patient's full name")
    age: int = Field(description="Patient's age in years")
    diagnosis: str = Field(description="Primary diagnosis")

# Your source document
document = """
Patient: John Smith, 45 years old
Primary diagnosis: Type 2 Diabetes
Treatment plan: Metformin 500mg twice daily
"""

# Extract with confidence and source tracking
result = groundit(
    document=document,
    extraction_schema=Patient
)

print(result)
```

**Output:**
```python
{
    'name': {
        'value': 'John Smith',
        'source_quote': 'Patient: John Smith',
        'value_confidence': 0.95,
        'source_quote_confidence': 0.98
        'source_span': [10,25]
    },
    'age': {
        'value': 45,
        'source_quote': '45 years old',
        'value_confidence': 0.92,
        'source_quote_confidence': 0.94,
        'source_span': [30,45]
    },
    'diagnosis': {
        'value': 'Type 2 Diabetes',
        'source_quote': 'Type 2 Diabetes',
        'value_confidence': 0.97,
        'source_quote_confidence': 0.99,
        'source_span': [47,62]
    }
}
```

## How It Works

1. **Schema Transformation**: Your Pydantic model or JSON schema is automatically enhanced to capture source information
2. **LLM Extraction**: Data is extracted using OpenAI's structured output APIs with logprobs enabled
3. **Confidence Analysis**: Token probabilities are aggregated into confidence scores using configurable strategies
4. **Source Mapping**: Extracted values are linked back to their origin text in the source document

## Advanced Usage

### Custom Configuration

```python
from groundit import groundit, joint_probability_aggregator

result = groundit(
    document=document,
    extraction_schema=Patient,
    extraction_prompt="Custom extraction instructions...",
    llm_model="openai/gpt-4.1",
    probability_aggregator=joint_probability_aggregator
)
```

### JSON Schema Support

```python
# Works with JSON schemas too
json_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"}
    }
}

result = groundit(
    document=document,
    extraction_schema=json_schema
)
```

### Hugging Face / Mistral example

```python
import os
from groundit import groundit
from pydantic import BaseModel, Field

# 🔑  Set your HF token (or `huggingface-cli login` beforehand)
os.environ["HUGGINGFACE_API_KEY"] = "hf_your_token_here"

class Patient(BaseModel):
    first_name: str = Field(description="Given name")
    last_name: str = Field(description="Family name")

doc = "John Doe, 1990-01-01, male"

result = groundit(
    document=doc,
    extraction_model=Patient,
    llm_model="huggingface/nebius/mistralai/Mistral-Small-3.1-24B-Instruct-2503",
)

print(result)
```

### Verbalized Confidence (for models without logprobs)

For models that don't provide token probabilities (like Claude/Anthropic models), you can use verbalized confidence:

```python
import os
from groundit import groundit
from pydantic import BaseModel, Field

# Set your Anthropic API key
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."

class Patient(BaseModel):
    first_name: str = Field(description="Given name")
    last_name: str = Field(description="Family name")
    age: int = Field(description="Age in years")

document = "Patient John Smith, 45 years old, diagnosed with diabetes"

# Use verbalized confidence with Claude
result = groundit(
    document=document,
    extraction_model=Patient,
    llm_model="anthropic/claude-sonnet-4-20250514",
    verbalized_confidence=True  # Enable verbalized confidence
)

print(result)
```

**Output with verbalized confidence:**
```python
{
    'first_name': {
        'value': 'John',
        'source_quote': 'Patient John Smith',
        'value_confidence': 0.95,
        'source_quote_confidence': 0.98,
        'source_span': [8, 23]
    },
    'last_name': {
        'value': 'Smith',
        'source_quote': 'John Smith',
        'value_confidence': 0.92,
        'source_quote_confidence': 0.94,
        'source_span': [13, 23]
    },
    'age': {
        'value': 45,
        'source_quote': '45 years old',
        'value_confidence': 0.90,
        'source_quote_confidence': 0.96,
        'source_span': [25, 37]
    }
}
```

## Requirements

- Python 3.12+
- API key for your chosen LLM provider:
  - `OPENAI_API_KEY` for OpenAI models
  - `ANTHROPIC_API_KEY` for Anthropic/Claude models
  - `HUGGINGFACE_API_KEY` for Hugging Face models
  - `GEMINI_API_KEY` for Google Gemini models

## Standalone Confidence Scoring

For non-extraction tasks that still produce structured outputs, you can use confidence scoring independently:

```python
from groundit import add_confidence_scores
import json
from openai import OpenAI

# Your existing structured output workflow
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Analyze this data and provide insights"}
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "analysis",
            "schema": {
                "type": "object",
                "properties": {
                    "insights": {"type": "array", "items": {"type": "string"}},
                    "confidence": {"type": "string"}
                }
            }
        }
    },
    logprobs=True
)

# Add confidence scores to the structured output
structured_output = json.loads(response.choices[0].message.content)
tokens = response.choices[0].logprobs.content

result_with_confidence = add_confidence_scores(
    extraction_result=structured_output,
    tokens=tokens
)

print(result_with_confidence)
# Each field now includes confidence scores based on token probabilities
```

## Acknowledgments

This project was bootstrapped using implementation ideas from [structured-logprobs](https://github.com/arena-ai/structured-logprobs).

## License

MIT License - see [LICENSE](LICENSE) file for details.
