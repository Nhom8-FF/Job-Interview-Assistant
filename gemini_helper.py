import google.generativeai as genai
import streamlit as st

def initialize_gemini(api_key):
    """
    Initialize the Gemini API client
    
    Args:
        api_key (str): API key for Gemini
        
    Returns:
        genai.GenerativeModel: The initialized Gemini model
    """
    try:
        genai.configure(api_key=api_key)
        
        # Initialize the generative model with appropriate settings
        # Using the newer gemini-2.0-flash model for improved performance
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            },
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
            ],
        )
        
        return model
    except Exception as e:
        st.error(f"Error initializing Gemini API: {str(e)}")
        return None

def generate_response(model, messages):
    """
    Generate a response from the Gemini model based on conversation history
    
    Args:
        model (genai.GenerativeModel): The initialized Gemini model
        messages (list): List of message dictionaries with 'role' and 'content'
        
    Returns:
        str: The generated response from the model
    """
    try:
        if not model:
            return "Error: Gemini model not initialized properly. Please check your API key."
        
        # Convert messages to the format expected by Gemini
        gemini_messages = []
        for message in messages:
            if message["role"] == "user":
                gemini_messages.append({"role": "user", "parts": [message["content"]]})
            elif message["role"] == "assistant":
                gemini_messages.append({"role": "model", "parts": [message["content"]]})
            elif message["role"] == "system":
                # For system messages, we add them to the user's first message
                # as Gemini API doesn't directly support system messages
                if gemini_messages and gemini_messages[0]["role"] == "user":
                    gemini_messages[0]["parts"][0] = message["content"] + "\n\n" + gemini_messages[0]["parts"][0]
                else:
                    # If there's no user message yet, create a placeholder
                    gemini_messages.append({"role": "user", "parts": [message["content"]]})
        
        # Generate response
        response = model.generate_content(gemini_messages)
        
        if hasattr(response, 'text'):
            return response.text
        else:
            return "I apologize, but I couldn't generate a response. Please try rephrasing your question."
    
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return f"I apologize, but an error occurred: {str(e)}. Please try again or check your API key."
