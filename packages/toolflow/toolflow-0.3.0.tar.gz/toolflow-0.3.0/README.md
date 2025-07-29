# Toolflow - Supercharge Any LLM SDK

[![PyPI version](https://badge.fury.io/py/toolflow.svg)](https://badge.fury.io/py/toolflow)
[![Python versions](https://img.shields.io/pypi/pyversions/toolflow.svg)](https://pypi.org/project/toolflow/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Connect on LinkedIn](https://img.shields.io/badge/LinkedIn-Isuru%20Wijesiri-blue?logo=linkedin)](https://www.linkedin.com/in/isuruwijesiri/)

**🔗 [GitHub](https://github.com/IsuruMaduranga/toolflow)** • **📘 [Examples](https://github.com/IsuruMaduranga/toolflow/tree/main/examples)** • **🔒 [Security](SECURITY.md)**

> **🚀 Stable API**: Version 0.3.x has a frozen public API. Breaking changes will bump to 0.4.0.

A lightweight drop-in wrapper for OpenAI and Anthropic SDKs that adds automatic parallel tool calling and structured Pydantic outputs **without breaking changes**.

## Why Toolflow?

Stop battling bloated frameworks. Toolflow supercharges the official SDKs you already use:

✅ **Drop-in replacement** - One line change, zero breaking changes  
✅ **Auto-parallel tools** - Functions execute concurrently (2-4x faster)  
✅ **Structured outputs** - Pass Pydantic models, get typed responses  
✅ **Advanced AI support** - OpenAI reasoning + Anthropic thinking modes  
✅ **Lightweight** - ~5MB vs ~50MB+ for other frameworks  
✅ **Unified interface** - Same code across providers  

## Installation

```bash
pip install toolflow
# Provider-specific installs
pip install toolflow[openai]      # OpenAI only
pip install toolflow[anthropic]   # Anthropic only
```

## Quick Start

```python
import toolflow
from openai import OpenAI
from pydantic import BaseModel
from typing import List

# Only change needed!
client = toolflow.from_openai(OpenAI())

# Define structured models
class CityWeather(BaseModel):
    city: str
    temperature: float
    condition: str

class WeatherRequest(BaseModel):
    cities: List[str]
    units: str

def get_weather(request: WeatherRequest) -> List[CityWeather]:
    """Get weather for multiple cities."""
    return [CityWeather(city=city, temperature=72.0, condition="Sunny") 
            for city in request.cities]

# Automatic parallel tool execution + structured output
result = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Get weather for NYC and London in Celsius"}],
    tools=[get_weather],
    response_format=List[CityWeather]
)
print(result)  # List of CityWeather objects
```

## Core Features

### 1. Auto-Parallel Tool Execution

Tools execute concurrently by default - **2-4x faster than sequential**:

```python
import time
from pydantic import BaseModel

class ApiRequest(BaseModel):
    query: str
    timeout: int

def slow_api_call(request: ApiRequest) -> str:
    time.sleep(1)  # Simulated API call
    return f"Result for {request.query}"

def fast_calculation(x: int, y: int) -> int:
    return x * y

# These execute in parallel (total time ~1 second)
result = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Call API with 'data' and calculate 10 * 5"}],
    tools=[slow_api_call, fast_calculation],
    parallel_tool_execution=True  # Default behavior
)
```

### 2. Structured Outputs (Like Instructor)

Get typed responses with Pydantic models:

```python
class TeamAnalysis(BaseModel):
    people: List[Person]
    average_age: float
    top_skills: List[str]

result = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Analyze team: John (30, Python), Sarah (25, Go)"}],
    response_format=TeamAnalysis
)
print(type(result))  # <class 'TeamAnalysis'>
print(result.average_age)  # 27.5
```

### 3. Response Modes

Choose between simplified or full SDK responses:

```python
# Simplified (default) - Direct content
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response)  # "Hello! How can I help you today?"

# Full SDK response
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}],
    full_response=True
)
print(response.choices[0].message.content)  # Original SDK behavior
```

## Advanced AI Capabilities

### OpenAI Reasoning Mode

Seamlessly integrate reasoning with tools and structured outputs:

```python
class AnalysisResult(BaseModel):
    solution: str
    reasoning_steps: List[str]
    confidence: float

result = client.chat.completions.create(
    model="o4-mini",
    reasoning_effort="medium",  # OpenAI reasoning
    messages=[{"role": "user", "content": "Analyze sales data and project 15% growth"}],
    tools=[calculate, analyze_data],
    response_format=AnalysisResult,
    parallel_tool_execution=True
)
```

### Anthropic Extended Thinking

```python
anthropic_client = toolflow.from_anthropic(Anthropic())

result = anthropic_client.messages.create(
    model="claude-3-5-sonnet-20241022",
    thinking=True,  # Extended thinking mode
    messages=[{"role": "user", "content": "Research AI trends and provide recommendations"}],
    tools=[search_web, analyze_trends],
    response_format=ResearchFindings,
    parallel_tool_execution=True
)
```

## Async Support

Mix sync and async tools with automatic optimization:

```python
import asyncio
from openai import AsyncOpenAI

client = toolflow.from_openai(AsyncOpenAI())

async def async_api_call(query: str) -> str:
    await asyncio.sleep(0.5)
    return f"Async result: {query}"

def sync_calculation(x: int, y: int) -> int:
    return x * y

async def main():
    result = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Call API and calculate 10*5"}],
        tools=[async_api_call, sync_calculation]  # Mixed sync/async
    )
    print(result)

asyncio.run(main())
```

## Streaming

Streaming works exactly like the official SDKs:

```python
# Simplified streaming
stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Write a story"}],
    tools=[search_web],
    stream=True
)

for chunk in stream:
    print(chunk, end="")  # Direct content

# Full response streaming
stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Write a story"}],
    stream=True,
    full_response=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## Migration Guide

### From OpenAI SDK
```python
# Before
from openai import OpenAI
client = OpenAI()

# After - one line change!
import toolflow
from openai import OpenAI
client = toolflow.from_openai(OpenAI())
```

### From Instructor
```python
# Before
import instructor
client = instructor.from_openai(OpenAI())

# After - same interface!
import toolflow
client = toolflow.from_openai(OpenAI())
```

## Configuration

### Performance Tuning

```python
import toolflow
from concurrent.futures import ThreadPoolExecutor

# Thread pool configuration
toolflow.set_max_workers(8)  # Default: 4
toolflow.set_executor(ThreadPoolExecutor(max_workers=16))

# Async streaming control
toolflow.set_async_yield_frequency(1)  # 0=disabled, 1=every chunk
```

### Internal Concurrency

Toolflow intelligently handles concurrency based on your environment:

```
SYNC OPERATIONS
├── Default: Parallel execution in ThreadPoolExecutor
    ├── Only supports sync tools
    ├── No custom executor → Global ThreadPoolExecutor (4 workers)
    ├── Change with toolflow.set_max_workers(workers)
    └── Custom executor with toolflow.set_executor(executor)

ASYNC OPERATIONS  
├── Default: Parallel execution optimized for async
    ├── Async tools → Uses asyncio.gather() for true concurrency
    ├── Sync tools → Uses asyncio.run_in_executor() with default thread pool ( or custom executor if set)
    └── Mixed tools → Combines both approaches automatically

STREAMING
├── Sync streaming → ThreadPoolExecutor for tool execution
└── Async streaming → Event loop yielding controlled by yield frequency
                     ├── 0 (default) → Trust provider libraries
                     └── N → Explicit asyncio.sleep(0) every N chunks
```

**Configuration Examples:**

```python
# High-performance custom executor
custom_executor = ThreadPoolExecutor(
    max_workers=16,
    thread_name_prefix="toolflow-custom-"
)
toolflow.set_executor(custom_executor)

# High-concurrency FastAPI deployment
toolflow.set_max_workers(12)              # More threads for parallel tools
toolflow.set_async_yield_frequency(1)     # Yield after every chunk

# Maximum performance setup
toolflow.set_max_workers(16)              # Maximum parallel tool execution
toolflow.set_async_yield_frequency(0)     # Trust provider libraries (default)
```

**When to adjust settings:**
- **High-concurrency deployments** (100+ simultaneous streams): Set yield frequency to `1`
- **I/O-heavy tools**: Increase `max_workers` to 8-16
- **CPU-intensive tools**: Keep `max_workers` at 4-6
- **Standard deployments**: Use defaults

### Enhanced Parameters

All standard SDK parameters work unchanged, plus:

```python
client.chat.completions.create(
    # Standard parameters (model, messages, temperature, etc.)
    
    # Toolflow enhancements
    tools=[...],                          # List of functions
    response_format=BaseModel,            # Pydantic model
    parallel_tool_execution=True,         # Enable concurrency
    max_tool_call_rounds=10,              # Safety limit
    max_response_format_retries=2,        # Retry limit
    graceful_error_handling=True,         # Handle errors gracefully
    full_response=False,                  # Response mode
)
```

## Performance Comparison

| Metric | Toolflow | Other Frameworks | Native SDK |
|--------|----------|------------------|------------|
| **Speed** | 2-4x faster | Variable | Baseline |
| **Memory** | +5MB | +50MB+ | Baseline |
| **Learning Curve** | Zero | Steep | N/A |
| **Migration** | One line | Complete rewrite | N/A |

## API Support

### Currently Supported
- ✅ **OpenAI**: Chat Completions, reasoning mode (`reasoning_effort`)
- ✅ **Anthropic**: Messages API, thinking mode (`thinking=True`)
- ✅ **Both**: Tool calling, streaming, structured outputs

### Coming Soon
- ⏳ **OpenAI Responses API** - New stateful API with hosted tools
- 🔄 **Other providers** - Groq, Gemini, etc.

## Error Handling

Tools handle errors gracefully by default:

```python
def unreliable_tool(data: str) -> str:
    if "error" in data:
        raise ValueError("Something went wrong!")
    return f"Success: {data}"

# Graceful handling (default)
result = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Process 'error data'"}],
    tools=[unreliable_tool],
    graceful_error_handling=True  # LLM receives error messages
)

# Strict handling
result = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Process 'error data'"}],
    tools=[unreliable_tool],
    graceful_error_handling=False  # Raises exceptions
)
```

## Development

```bash
# Install for development
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ && isort src/

# Type checking
mypy src/

# Live tests (requires API keys)
export OPENAI_API_KEY='your-key'
export ANTHROPIC_API_KEY='your-key'
python run_live_tests.py
```

## Security

Toolflow executes all tool functions **locally** on your machine. See our [Security Policy](SECURITY.md) for important security information and best practices.

## API Stability

**0.3.x Series (Current)**
- ✅ **Frozen Public API**: No breaking changes
- ✅ **Production Ready**: Stable for production use
- 🔄 **Feature Additions**: New features in minor releases

**0.4.0 and Beyond**
- ⚠️ **Breaking Changes**: Will bump to 0.4.0
- 📋 **Migration Guide**: Clear upgrade path provided

## Contributing

Contributions welcome! Please fork, create a feature branch, add tests, and submit a pull request.

## Author

Created by [Isuru Wijesiri](https://www.linkedin.com/in/isuruwijesiri/)  
🔗 [LinkedIn](https://www.linkedin.com/in/isuruwijesiri/) • [GitHub](https://github.com/IsuruMaduranga)

## License

MIT License - see LICENSE file for details.
