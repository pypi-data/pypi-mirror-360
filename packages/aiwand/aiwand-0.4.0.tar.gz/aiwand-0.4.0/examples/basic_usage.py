#!/usr/bin/env python3
"""
Basic usage examples for AIWand package
"""

import aiwand

def main():
    """Run basic examples."""
    
    print("🪄 AIWand Basic Usage Examples")
    print("=" * 40)
    
    # Show current configuration
    print("\n📋 Current Configuration:")
    try:
        aiwand.show_current_config()
    except Exception as e:
        print(f"Error showing config: {e}")
        print("\n💡 Run 'aiwand setup' first to configure your preferences!")
        print("   Or set environment variables: OPENAI_API_KEY, GEMINI_API_KEY")
    
    print("\n" + "=" * 40)
    
    # Example text to work with
    sample_text = """
    Machine learning is a method of data analysis that automates analytical 
    model building. It is a branch of artificial intelligence (AI) based on 
    the idea that systems can learn from data, identify patterns and make 
    decisions with minimal human intervention. Machine learning algorithms 
    build a mathematical model based on training data, in order to make 
    predictions or decisions without being explicitly programmed to do so.
    The process of machine learning involves training algorithms on large 
    datasets to recognize patterns and relationships. These algorithms can 
    then be applied to new data to make predictions or classifications. 
    Common applications include image recognition, natural language processing, 
    recommendation systems, and autonomous vehicles.
    """
    
    print("\n🚀 Running Examples with Smart AI Provider Selection")
    print("AIWand will use your configured preferences or environment variables.\n")
    
    try:
        # Example 1: Basic summarization
        print("1. Basic Summarization:")
        print("-" * 30)
        summary = aiwand.summarize(sample_text)
        print(f"Summary: {summary}\n")
        
        # Example 2: Bullet-point summary
        print("2. Bullet-point Summary:")
        print("-" * 30)
        bullet_summary = aiwand.summarize(sample_text, style="bullet-points")
        print(f"Bullet Summary:\n{bullet_summary}\n")
        
        # Example 3: Chat with AI
        print("3. Chat Example:")
        print("-" * 30)
        response = aiwand.chat("What is the main benefit of machine learning?")
        print(f"AI Response: {response}\n")
        
        # Example 4: Text generation
        print("4. Text Generation:")
        print("-" * 30)
        generated = aiwand.generate_text(
            "Write a short poem about artificial intelligence",
            max_tokens=100,
            temperature=0.8
        )
        print(f"Generated Text:\n{generated}\n")
        
        # Example 5: Conversation with context
        print("5. Conversation with Context:")
        print("-" * 30)
        conversation = []
        
        # First message
        msg1 = "Hello! Can you help me understand neural networks?"
        response1 = aiwand.chat(msg1, conversation_history=conversation)
        conversation.append({"role": "user", "content": msg1})
        conversation.append({"role": "assistant", "content": response1})
        print(f"User: {msg1}")
        print(f"AI: {response1}\n")
        
        # Follow-up message with context
        msg2 = "Can you give me a simple example?"
        response2 = aiwand.chat(msg2, conversation_history=conversation)
        print(f"User: {msg2}")
        print(f"AI: {response2}")
        
    except aiwand.AIError as e:
        print(f"AIWand Error: {e}")
        print("\n💡 To fix this:")
        print("1. Run 'aiwand setup' to configure your preferences")
        print("2. Or set environment variables: OPENAI_API_KEY, GEMINI_API_KEY")
        print("3. Make sure you have an active internet connection")
    except ValueError as e:
        print(f"Input Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
        print("\nMake sure you have:")
        print("1. Configured AIWand with 'aiwand setup'")
        print("2. Installed the required dependencies")
        print("3. Have an active internet connection")


if __name__ == "__main__":
    main() 