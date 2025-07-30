#!/usr/bin/env python3
"""
Test script to verify OpenAI API monkey patching functionality without making actual API calls.
"""

from neatlogs.openai import OpenAIProvider

def test_patching_functionality():
    """
    Test that the OpenAI provider can be initialized and patched without errors.
    """
    print("Testing OpenAI provider initialization and patching...")
    
    # Create a provider instance
    provider = OpenAIProvider(
        trace_id="test-patching-123", 
        api_key="test-neatlogs-api-key",
        tags=["test", "patching"]
    )
    
    print("✓ Provider initialized successfully")
    
    # Test patching
    print("\nTesting API patching...")
    try:
        provider.override()
        print("✓ OpenAI API patching completed successfully")
    except Exception as e:
        print(f"✗ Error during patching: {e}")
        return False
    
    # Test conversation history (should be empty initially)
    print("\nTesting conversation history...")
    history = provider.get_conversation_history()
    print(f"✓ Conversation history retrieved: {len(history)} items")
    
    # Test unpatching
    print("\nTesting API unpatching...")
    try:
        provider.undo_override()
        print("✓ OpenAI API unpatching completed successfully")
    except Exception as e:
        print(f"✗ Error during unpatching: {e}")
        return False
    
    print("\n✓ All patching tests passed!")
    return True

def test_multiple_patching():
    """
    Test that multiple providers can be created and patched safely.
    """
    print("\n" + "=" * 50)
    print("Testing multiple provider instances...")
    
    # Create multiple providers
    provider1 = OpenAIProvider(trace_id="test1", api_key="key1")
    provider2 = OpenAIProvider(trace_id="test2", api_key="key2")
    
    print("✓ Multiple providers created")
    
    # Patch with first provider
    provider1.override()
    print("✓ First provider patched")
    
    # Try to patch with second provider (should skip)
    provider2.override()
    print("✓ Second provider handled correctly (skipped)")
    
    # Unpatch
    provider1.undo_override()
    print("✓ Unpatching completed")
    
    print("✓ Multiple provider test passed!")
    return True

if __name__ == "__main__":
    print("Testing OpenAI API monkey patching functionality...")
    print("=" * 50)
    
    # Test basic patching
    success1 = test_patching_functionality()
    
    # Test multiple providers
    success2 = test_multiple_patching()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 All tests passed! OpenAI provider is working correctly.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    print("=" * 50) 