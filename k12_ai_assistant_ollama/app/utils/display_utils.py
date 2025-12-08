"""
Utility functions for consistently displaying AI responses across the application.
"""
import streamlit as st

def display_response(response_text, header=None):
    """
    Display an AI response in a uniform way without any interactive elements.
    
    Args:
        response_text: The response text to display (will be converted to string)
        header: Optional header text to display above the response
    """
    if response_text:
        # Convert to string if needed
        text = str(response_text).strip()
        
        if header:
            st.subheader(header)
        
        # Display as plain markdown without HTML/JavaScript
        # This ensures no interactive widgets are created
        st.markdown(text, unsafe_allow_html=False)
    else:
        st.info("No response received.")

def display_streaming_response(stream_generator, header=None):
    """
    Display a streaming AI response as it's being generated.
    
    Args:
        stream_generator: A generator that yields response chunks
        header: Optional header text to display above the response
    """
    if header:
        st.subheader(header)
    
    # Create a placeholder for the streaming response
    response_placeholder = st.empty()
    full_response = ""
    
    try:
        # Stream the response chunk by chunk
        chunk_count = 0
        for chunk in stream_generator:
            if chunk:
                chunk_str = str(chunk)
                full_response += chunk_str
                chunk_count += 1
                # Update the placeholder with the accumulated response
                response_placeholder.markdown(full_response, unsafe_allow_html=False)
        
        # Check if we got any chunks
        if chunk_count == 0:
            response_placeholder.warning("⚠️ No response received. The stream generator may not be working. Check if Ollama is running and the model is loaded.")
            return None
        
        # Return the full response for storage in session state
        if full_response.strip():
            return full_response.strip()
        else:
            response_placeholder.warning("⚠️ Empty response received. Please try again.")
            return None
    except Exception as e:
        error_msg = str(e)
        response_placeholder.error(f"❌ Error during streaming: {error_msg}")
        import traceback
        with st.expander("Error Details (click to expand)"):
            st.code(traceback.format_exc())
        return None
