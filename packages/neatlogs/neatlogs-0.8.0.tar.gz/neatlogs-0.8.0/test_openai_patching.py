#!/usr/bin/env python3
"""
Test script to demonstrate OpenAI API monkey patching functionality.
This script shows how to use the OpenAIProvider to intercept and log OpenAI API calls.
"""

import os
from neatlogs.openai import OpenAIProvider
import traceback

def test_openai_patching():
    """
    Test the OpenAI provider by making API calls and checking the logging.
    """
    # Set up your OpenAI API key (you'll need to set this environment variable)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    # Create a provider instance
    provider = OpenAIProvider(
        trace_id="test-openai-123", 
        api_key="your-neatlogs-api-key",  # Replace with your NeatLogs API key
        tags=["test", "openai", "demo"]
    )
    
    print("Setting up OpenAI provider...")
    
    # Enable logging (this patches the OpenAI API)
    provider.override()
    
    print("OpenAI API has been patched. Any calls to OpenAI client will now be logged.")
    
    try:
        # Import OpenAI after patching
        from openai import OpenAI
        
        # Create client instance
        client = OpenAI(api_key=api_key)
        
        print("\nMaking a test chat completion API call...")
        
        # Make a test chat completion API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello! What is the capital of India."}
            ],
            max_tokens=50
        )
        
        print(f"\nChat completion response received: {response.choices[0].message.content}")
        
        print("\nMaking a test completion API call...")
        
        # Make a test completion API call (using the older completions endpoint)
        completion_response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt="What is the capital of France?",
            max_tokens=50
        )
        
        print(f"\nCompletion response received: {completion_response.choices[0].text}")
        
        # Get conversation history
        print("\nGetting conversation history...")
        history = provider.get_conversation_history()
        print(f"Number of logged interactions: {len(history)}")
        
        if history:
            latest = history[-1]
            print(f"Latest interaction:")
            print(f"  Model: {latest['model']}")
            print(f"  Timestamp: {latest['timestamp']}")
            print(f"  Prompt: {latest['prompt']}")
            print(f"  Completion: {latest['completion'][:100]}...")
        
    except ImportError:
        print("OpenAI package not installed. Please install it with: pip install openai")
    except Exception as e:
        print(f"Error during API call: {e}")
        print(traceback.format_exc())
    
    finally:
        # Clean up - restore original methods
        print("\nCleaning up...")
        provider.undo_override()
        print("OpenAI API has been restored to original state.")

def test_async_openai_patching():
    """
    Test async OpenAI API calls using the new client structure.
    """
    import asyncio
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    provider = OpenAIProvider(
        trace_id="test-openai-async-123", 
        api_key="your-neatlogs-api-key",
        tags=["test", "openai", "async", "demo"]
    )
    
    print("Setting up OpenAI provider for async calls...")
    provider.override()
    
    async def make_async_call():
        try:
            from openai import AsyncOpenAI
            
            # Create async client instance
            client = AsyncOpenAI(api_key=api_key)
            
            print("\nMaking an async test API call...")
            
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Hello! This is an async test message."}
                ],
                max_tokens=50
            )
            
            print(f"\nAsync response received: {response.choices[0].message.content}")
            
            # Get conversation history
            history = provider.get_conversation_history()
            print(f"Number of logged interactions: {len(history)}")
            
        except ImportError:
            print("OpenAI package not installed or doesn't support async calls.")
        except Exception as e:
            print(f"Error during async API call: {e}")
            print(traceback.format_exc())
        finally:
            provider.undo_override()
            print("Async OpenAI API has been restored.")
    
    # Run the async test
    asyncio.run(make_async_call())

def test_completion_api():
    """
    Test the older completions API (not chat completions).
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    provider = OpenAIProvider(
        trace_id="test-completion-123", 
        api_key="your-neatlogs-api-key",
        tags=["test", "completion", "demo"]
    )
    
    print("Setting up OpenAI provider for completion API...")
    provider.override()
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        print("\nMaking a completion API call...")
        
        # Test the completions API (older style)
        response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt="Write a short poem about coding:",
            max_tokens=100,
            temperature=0.7
        )
        
        print(f"\nCompletion response: {response.choices[0].text}")
        print(f"Usage: {dict(response).get('usage')}")
        
        # Get conversation history
        history = provider.get_conversation_history()
        print(f"\nNumber of logged interactions: {len(history)}")
        
    except Exception as e:
        print(f"Error during completion API call: {e}")
        print(traceback.format_exc())
    finally:
        provider.undo_override()
        print("Completion API has been restored.")

if __name__ == "__main__":
    print("Testing OpenAI API monkey patching...")
    print("=" * 50)
    
    # Test synchronous calls
    test_openai_patching()
    
    print("\n" + "=" * 50)
    print("Testing completion API...")
    
    # Test completion API
    # test_completion_api()
    
    print("\n" + "=" * 50)
    print("Testing async OpenAI API monkey patching...")
    
    # Test async calls
    # test_async_openai_patching()
    
    print("\n" + "=" * 50)
    print("Testing complete!") 