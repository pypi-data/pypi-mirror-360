"""
Core AI functionality for AIWand
"""

from typing import Optional, List, Dict, Any
from .config import get_ai_client, get_model_name, AIError


def summarize(
    text: str,
    max_length: Optional[int] = None,
    style: str = "concise",
    model: Optional[str] = None
) -> str:
    """
    Summarize the given text using AI API (OpenAI or Gemini).
    
    Args:
        text (str): The text to summarize
        max_length (Optional[int]): Maximum length of the summary in words
        style (str): Style of summary ('concise', 'detailed', 'bullet-points')
        model (Optional[str]): Specific model to use (auto-selected if not provided)
        
    Returns:
        str: The summarized text
        
    Raises:
        ValueError: If the text is empty
        Exception: If the API call fails
    """
    if not text.strip():
        raise ValueError("Text cannot be empty")
    
    # Prepare the prompt based on style
    style_prompts = {
        "concise": "Provide a concise summary of the following text:",
        "detailed": "Provide a detailed summary of the following text:",
        "bullet-points": "Summarize the following text in bullet points:"
    }
    
    prompt = style_prompts.get(style, style_prompts["concise"])
    
    if max_length:
        prompt += f" Keep the summary under {max_length} words."
    
    try:
        client = get_ai_client()
        
        # Use provided model or get from user preferences
        if model is None:
            model = get_model_name()
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    
    except AIError as e:
        raise AIError(str(e))
    except Exception as e:
        raise Exception(f"Failed to summarize text: {str(e)}")


def chat(
    message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    model: Optional[str] = None,
    temperature: float = 0.7
) -> str:
    """
    Have a conversation with the AI (OpenAI or Gemini).
    
    Args:
        message (str): The user's message
        conversation_history (Optional[List[Dict[str, str]]]): Previous conversation messages
        model (Optional[str]): Specific model to use (auto-selected if not provided)
        temperature (float): Response creativity (0.0 to 1.0)
        
    Returns:
        str: The AI's response
        
    Raises:
        ValueError: If the message is empty
        Exception: If the API call fails
    """
    if not message.strip():
        raise ValueError("Message cannot be empty")
    
    try:
        client = get_ai_client()
        
        # Use provided model or get from user preferences
        if model is None:
            model = get_model_name()
        
        messages = conversation_history or []
        messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=1000
        )
        
        return response.choices[0].message.content.strip()
    
    except AIError as e:
        raise AIError(str(e))
    except Exception as e:
        raise Exception(f"Failed to get chat response: {str(e)}")


def generate_text(
    prompt: str,
    max_tokens: int = 500,
    temperature: float = 0.7,
    model: Optional[str] = None
) -> str:
    """
    Generate text based on a prompt using AI (OpenAI or Gemini).
    
    Args:
        prompt (str): The prompt to generate text from
        max_tokens (int): Maximum number of tokens to generate
        temperature (float): Response creativity (0.0 to 1.0)
        model (Optional[str]): Specific model to use (auto-selected if not provided)
        
    Returns:
        str: The generated text
        
    Raises:
        ValueError: If the prompt is empty
        Exception: If the API call fails
    """
    if not prompt.strip():
        raise ValueError("Prompt cannot be empty")
    
    try:
        client = get_ai_client()
        
        # Use provided model or get from user preferences
        if model is None:
            model = get_model_name()
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content.strip()
    
    except AIError as e:
        raise AIError(str(e))
    except Exception as e:
        raise Exception(f"Failed to generate text: {str(e)}") 