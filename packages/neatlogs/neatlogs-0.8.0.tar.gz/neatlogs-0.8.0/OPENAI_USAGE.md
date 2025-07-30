# OpenAI Provider Usage

This document explains how to use the OpenAI provider for monkey patching OpenAI API calls in the NeatLogs library.

## Overview

The OpenAI provider allows you to intercept and log all calls to the OpenAI API using the new client-based approach (v1.0.0+), similar to how the LiteLLM provider works. It supports both synchronous and asynchronous API calls.

## Installation

Make sure you have the required dependencies:

```bash
pip install openai>=1.0.0
```

## Basic Usage

### Method 1: Using the OpenAIProvider directly

```python
from neatlogs.openai import OpenAIProvider

# Create a provider instance
provider = OpenAIProvider(
    trace_id="your-trace-id",
    api_key="your-neatlogs-api-key",
    tags=["production", "openai"]
)

# Enable logging (patches the OpenAI API)
provider.override()

# Now all OpenAI API calls will be logged
from openai import OpenAI
client = OpenAI(api_key="your-openai-api-key")

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Get conversation history
history = provider.get_conversation_history()

# Clean up when done
provider.undo_override()
```

### Method 2: Using the LLMTracker (Recommended)

```python
from neatlogs.llm import LLMTracker

# Create a tracker instance
tracker = LLMTracker(api_key="your-neatlogs-api-key")

# Add tags
tracker.add_tags(["production", "openai"])

# Override APIs (will automatically detect and patch OpenAI)
tracker.override_api()

# Make OpenAI API calls
from openai import OpenAI
client = OpenAI(api_key="your-openai-api-key")

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Stop instrumenting when done
tracker.stop_instrumenting()
```

## Supported API Calls

The OpenAI provider supports the following API calls:

### Synchronous Calls

- `client.chat.completions.create()` - Chat completions API
- `client.completions.create()` - Legacy completions API

### Asynchronous Calls

- `client.chat.completions.create()` - Async chat completions API
- `client.completions.create()` - Async legacy completions API

## Features

### 1. Automatic Logging

All API calls are automatically logged with:

- Input parameters (messages, model, etc.)
- Response data
- Timestamps
- Token usage
- Error information (if any)

### 2. Conversation History

Access recent conversations in memory:

```python
# Get all recent conversations
history = provider.get_conversation_history()

# Get last 10 conversations
recent = provider.get_conversation_history(limit=10)
```

### 3. Error Handling

Errors in API calls are automatically captured and logged:

```python
try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello!"}]
    )
except Exception as e:
    # Error is automatically logged
    print(f"Error: {e}")
```

### 4. Background Logging

All logs are sent to the NeatLogs server in background threads, so your application performance is not affected.

## API Reference

### OpenAIProvider

#### `__init__(trace_id, client=None, api_key=None, tags=None)`

Initialize the provider.

- `trace_id` (str): Unique identifier for the tracking session
- `client` (str, optional): Client identifier
- `api_key` (str): Your NeatLogs API key
- `tags` (list, optional): List of tags to associate with the session

#### `override()`

Patches the OpenAI client classes to enable logging.

#### `undo_override()`

Restores the original OpenAI client methods.

#### `get_conversation_history(limit=None)`

Returns recent conversation history.

- `limit` (int, optional): Maximum number of conversations to return

#### `handle_error(e, kwargs)`

Handles errors in API calls.

## Examples

### Chat Completions (Recommended)

```python
from neatlogs.openai import OpenAIProvider
from openai import OpenAI

provider = OpenAIProvider(trace_id="chat-test", api_key="your-neatlogs-api-key")
provider.override()

client = OpenAI(api_key="your-openai-api-key")

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ],
    max_tokens=100
)

print(response.choices[0].message.content)
provider.undo_override()
```

### Legacy Completions

```python
from neatlogs.openai import OpenAIProvider
from openai import OpenAI

provider = OpenAIProvider(trace_id="completion-test", api_key="your-neatlogs-api-key")
provider.override()

client = OpenAI(api_key="your-openai-api-key")

response = client.completions.create(
    model="gpt-3.5-turbo-instruct",
    prompt="Write a short poem about coding:",
    max_tokens=100,
    temperature=0.7
)

print(response.choices[0].text)
provider.undo_override()
```

### Async Support

```python
import asyncio
from neatlogs.openai import OpenAIProvider
from openai import AsyncOpenAI

async def async_example():
    provider = OpenAIProvider(
        trace_id="async-test",
        api_key="your-neatlogs-api-key"
    )

    provider.override()

    client = AsyncOpenAI(api_key="your-openai-api-key")

    # Async chat completion
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello async!"}]
    )

    print(response.choices[0].message.content)

    provider.undo_override()

# Run the async example
asyncio.run(async_example())
```

## Integration with Existing Code

The OpenAI provider is designed to work seamlessly with existing OpenAI code. Simply add the provider initialization and override calls around your existing API usage:

```python
# Your existing code
from openai import OpenAI
client = OpenAI(api_key="your-openai-api-key")

# Add NeatLogs provider
from neatlogs.openai import OpenAIProvider
provider = OpenAIProvider(trace_id="my-app", api_key="neatlogs-key")
provider.override()

# Your existing API calls (now automatically logged)
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Clean up when done
provider.undo_override()
```

## Migration from Old API

If you're migrating from the old OpenAI API structure, here are the key changes:

### Old API (Deprecated)

```python
import openai
openai.api_key = "your-key"
response = openai.ChatCompletion.create(...)
```

### New API (Current)

```python
from openai import OpenAI
client = OpenAI(api_key="your-key")
response = client.chat.completions.create(...)
```

The NeatLogs provider automatically handles both the old and new API structures, but it's recommended to use the new client-based approach.

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'openai'**

   - Install the OpenAI package: `pip install openai>=1.0.0`

2. **API calls not being logged**

   - Make sure to call `provider.override()` before creating client instances
   - Check that the OpenAI module is imported after calling `override()`

3. **Permission errors**

   - Ensure your NeatLogs API key is correct
   - Check that your OpenAI API key is valid

4. **Client not found errors**
   - Make sure you're using the new client-based approach: `from openai import OpenAI`

### Debug Mode

Enable debug logging to see what's happening:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Then use the provider as normal
provider = OpenAIProvider(...)
provider.override()
```

## Best Practices

1. **Always clean up**: Call `undo_override()` when you're done to restore the original API methods.

2. **Use unique trace IDs**: Each session should have a unique trace ID for proper tracking.

3. **Add meaningful tags**: Use tags to categorize and filter your logs.

4. **Handle errors gracefully**: The provider will log errors automatically, but you should still handle them in your application.

5. **Test in development**: Always test the provider in a development environment before using in production.

6. **Use the new client-based API**: The new `OpenAI()` client is the recommended approach for all new code.

## Supported Models

The provider works with all OpenAI models that support the chat completions or completions APIs:

- GPT-4 and GPT-4 Turbo
- GPT-3.5 Turbo
- GPT-3.5 Turbo Instruct
- And other OpenAI models
