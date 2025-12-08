import ollama
import streamlit as st
import subprocess
import re
import os

def get_ai_response(prompt, model_name, stream=False):
    """
    Get a response from the AI model using Ollama.
    
    Args:
        prompt (str): The prompt to send to the model
        model_name (str): The name of the model to use
        stream (bool): If True, returns a generator that yields response chunks
        
    Returns:
        str or generator: The generated response text (or generator if stream=True)
    """
    try:
        # Optimized configuration for high-performance GPUs
        # Settings are tuned for maximum throughput on powerful hardware
        
        # Create Ollama client with timeout to prevent hanging
        client = ollama.Client(timeout=300.0)  # 5 minute timeout
        
        # Streaming response
        if stream:
            def stream_generator():
                try:
                    stream_response = client.generate(
                        model=model_name,
                        prompt=prompt,
                        stream=True,  # Enable streaming
                        options={
                            "temperature": 0.7,
                            "top_k": 40,
                            "top_p": 0.9,
                            "num_predict": 4096,
                            "num_ctx": 16384,
                            "repeat_penalty": 1.1,
                            "tfs_z": 1.0,
                            "typical_p": 1.0,
                        }
                    )
                    
                    # Ollama streaming returns GenerateResponse objects
                    # Each chunk has a 'response' field that contains the text
                    for chunk in stream_response:
                        # Handle different response formats
                        if hasattr(chunk, 'response'):
                            # GenerateResponse object
                            response_text = chunk.response
                            if response_text:
                                yield str(response_text)
                        elif isinstance(chunk, dict):
                            # Dictionary format
                            response_text = chunk.get('response', '') or chunk.get('content', '')
                            if response_text:
                                yield str(response_text)
                        elif chunk:
                            # Try to convert to string
                            yield str(chunk)
                except Exception as e:
                    error_msg = str(e)
                    if "connection refused" in error_msg.lower() or "connect" in error_msg.lower():
                        st.warning("Could not connect to Ollama. Using fallback mode with pre-defined responses.")
                        fallback = get_fallback_response(prompt, model_name)
                        yield fallback
                    else:
                        st.error(f"Streaming error: {error_msg}")
                        raise Exception(f"Error communicating with Ollama: {error_msg}")
            
            return stream_generator()
        
        # Non-streaming response (backward compatibility)
        response = client.generate(
            model=model_name,
            prompt=prompt,
            options={
                "temperature": 0.7,
                "top_k": 40,
                "top_p": 0.9,
                "num_predict": 4096,  # Can handle very long responses efficiently
                "num_ctx": 16384,  # Large context window
                "repeat_penalty": 1.1,
                "tfs_z": 1.0,  # Tail free sampling for quality
                "typical_p": 1.0,  # Typical sampling
            }
        )
        
        # Extract ONLY the response text - Ollama.generate() returns a dict
        # The actual text is in the 'response' key
        # We want to extract just the text content, ignoring all metadata
        
        response_text = ""
        
        # Ollama always returns a dict with 'response' key containing the text
        if isinstance(response, dict):
            response_text = response.get('response', '')
        else:
            # Fallback: if it's not a dict, try to get the response attribute
            response_text = getattr(response, 'response', '') if hasattr(response, 'response') else ''
        
        # Ensure we have a string
        if not isinstance(response_text, str):
            response_text = str(response_text) if response_text else ''
        
        # Clean and return ONLY the text (no metadata)
        return response_text.strip() if response_text else ""
            
    except Exception as e:
        # Handle connection errors or other issues
        error_msg = str(e)
        if "connection refused" in error_msg.lower():
            # Provide a fallback response when Ollama is not available
            st.warning("Could not connect to Ollama. Using fallback mode with pre-defined responses.")
            return get_fallback_response(prompt, model_name)
        else:
            raise Exception(f"Error communicating with Ollama: {error_msg}")

def get_gpu_usage():
    """
    Get GPU usage information using nvidia-smi.
    
    Returns:
        dict: Dictionary with GPU information including memory usage, utilization, etc.
              Returns None if nvidia-smi is not available or fails.
    """
    try:
        # Run nvidia-smi query for GPU info
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=index,name,memory.used,memory.total,utilization.gpu,temperature.gpu', 
             '--format=csv,noheader,nounits'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return None
        
        # Get process-level memory usage (works better for unified memory systems)
        process_result = subprocess.run(
            ['nvidia-smi', '--query-compute-apps=pid,process_name,used_memory', 
             '--format=csv,noheader,nounits'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Calculate total memory used by all processes
        total_process_memory = 0
        ollama_memory = 0
        if process_result.returncode == 0:
            for line in process_result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 3:
                    try:
                        mem_mb = int(parts[2])
                        total_process_memory += mem_mb
                        if 'ollama' in parts[1].lower():
                            ollama_memory += mem_mb
                    except (ValueError, IndexError):
                        pass
        
        # Parse the GPU output
        lines = result.stdout.strip().split('\n')
        gpu_info = []
        
        for line in lines:
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 6:
                # Handle [N/A] values for memory
                try:
                    memory_used = int(parts[2]) if parts[2] != '[N/A]' else None
                except (ValueError, IndexError):
                    memory_used = None
                    
                try:
                    memory_total = int(parts[3]) if parts[3] != '[N/A]' else None
                except (ValueError, IndexError):
                    memory_total = None
                    
                try:
                    utilization = int(parts[4]) if parts[4] != '[N/A]' else None
                except (ValueError, IndexError):
                    utilization = None
                    
                try:
                    temperature = int(parts[5]) if parts[5] != '[N/A]' else None
                except (ValueError, IndexError):
                    temperature = None
                
                # Use process memory if GPU memory is N/A (for unified memory systems)
                if memory_used is None and total_process_memory > 0:
                    memory_used = total_process_memory
                
                gpu_info.append({
                    'index': parts[0],
                    'name': parts[1],
                    'memory_used_mb': memory_used,
                    'memory_total_mb': memory_total,
                    'utilization_percent': utilization,
                    'temperature_c': temperature,
                    'ollama_memory_mb': ollama_memory if ollama_memory > 0 else None
                })
        
        return gpu_info if gpu_info else None
        
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError, Exception) as e:
        return None

def format_gpu_memory(mb):
    """Format memory in MB to human-readable format."""
    if mb is None:
        return "N/A"
    if mb >= 1024:
        return f"{mb / 1024:.1f} GB"
    return f"{mb} MB"

def get_available_models():
    """
    Get a list of available models from Ollama.
    
    Returns:
        list: A list of available model names
    """
    try:
        models = ollama.list()
        return [model['name'] for model in models['models']]
    except Exception:
        # Return default models if we can't connect to Ollama
        return ["llama3.2:3b", "phi:latest", "mixtral:8x7b", "gemma:7b"]

def format_prompt_for_grade_level(prompt, grade_level):
    """
    Format a prompt with appropriate instructions for the selected grade level.
    
    Args:
        prompt (str): The base prompt
        grade_level (str): The grade level (e.g., "K-2 (Elementary)")
        
    Returns:
        str: The formatted prompt with grade level instructions
    """
    # Extract the grade range from the grade level string
    if "K-2" in grade_level:
        instructions = """
        - Use very simple language appropriate for kindergarten to 2nd grade
        - Explain concepts using familiar examples and concrete terms
        - Keep sentences short and use basic vocabulary
        - Use a friendly, encouraging tone
        - Include visual descriptions where possible
        """
    elif "3-5" in grade_level:
        instructions = """
        - Use language appropriate for 3rd to 5th grade students
        - Explain concepts clearly with some simple examples
        - Use straightforward sentences and grade-appropriate vocabulary
        - Be encouraging and supportive
        - Include some interesting facts to maintain engagement
        """
    elif "6-8" in grade_level:
        instructions = """
        - Use language appropriate for middle school students (6th to 8th grade)
        - Provide more detailed explanations with relevant examples
        - Introduce some subject-specific terminology with explanations
        - Encourage critical thinking and connections between concepts
        - Maintain an engaging and supportive tone
        """
    elif "9-12" in grade_level:
        instructions = """
        - Use language appropriate for high school students (9th to 12th grade)
        - Provide comprehensive explanations with specific examples
        - Use appropriate academic language and subject-specific terminology
        - Encourage deeper analysis and critical thinking
        - Make connections to broader concepts and real-world applications
        """
    else:
        # Default to middle grades if unknown
        instructions = """
        - Use clear, straightforward language
        - Provide helpful examples to illustrate concepts
        - Maintain an encouraging and supportive tone
        """
    
    # Combine the base prompt with the grade-level instructions
    formatted_prompt = f"""
    {prompt}
    
    Please follow these guidelines for a {grade_level} student:
    {instructions}
    """
    
    return formatted_prompt

def get_fallback_response(prompt, model_name):
    """
    Provide a fallback response when Ollama is not available.
    
    Args:
        prompt (str): The prompt that was sent
        model_name (str): The model that was requested
        
    Returns:
        str: A pre-defined fallback response
    """
    # Check for common prompt types and provide appropriate responses
    prompt_lower = prompt.lower()
    
    if "water cycle" in prompt_lower:
        return """
        # The Water Cycle
        
        The water cycle is how water moves around our Earth. It's like a big circle that never stops!
        
        Here's how it works:
        
        1. **Evaporation**: The sun heats up water in oceans, lakes, and rivers, turning it into water vapor (a gas) that rises into the air. It's like when a puddle disappears on a hot day!
        
        2. **Condensation**: As the water vapor goes up high in the sky, it cools down and turns into tiny water droplets that form clouds. It's like when you see foggy stuff on a cold window!
        
        3. **Precipitation**: When the water droplets in clouds get heavy enough, they fall back to Earth as rain, snow, sleet, or hail. That's when we need our umbrellas!
        
        4. **Collection**: The water that falls down goes back into oceans, lakes, and rivers, or soaks into the ground. Then the cycle starts all over again!
        
        The water cycle is super important because it gives us fresh water to drink and helps plants grow. It's been working the same way for millions of years!
        """
    
    elif "math" in prompt_lower or "problem" in prompt_lower:
        return """
        I'd be happy to help with your math problem! Since I can't see the specific problem right now (Ollama connection is unavailable), here are some general steps for solving math problems:
        
        1. Read the problem carefully to understand what's being asked
        2. Identify the important information and what you need to find
        3. Choose the right method or formula to solve it
        4. Work through the steps carefully, showing your work
        5. Check your answer to make sure it makes sense
        
        For specific types of problems:
        
        **Addition/Subtraction**: Line up the numbers carefully by place value
        **Multiplication**: Break it down into steps if needed
        **Division**: Remember to check with multiplication
        **Fractions**: Find common denominators when adding/subtracting
        **Word Problems**: Draw a picture or diagram to help understand
        
        When Ollama is connected, I can help with specific problems!
        """
    
    elif "write" in prompt_lower or "essay" in prompt_lower or "story" in prompt_lower:
        return """
        # Writing Tips
        
        Here are some helpful writing tips:
        
        1. **Start with a plan**: Outline your main ideas before you start writing
        2. **Strong beginning**: Grab your reader's attention with an interesting opening
        3. **Clear structure**: Organize your writing with a beginning, middle, and end
        4. **Use details**: Include specific details to make your writing more interesting
        5. **Show, don't tell**: Use descriptive language to paint a picture for your reader
        6. **Vary your sentences**: Mix short and long sentences to create a good rhythm
        7. **Strong ending**: Finish with a conclusion that wraps up your main points
        8. **Revise and edit**: Always read through your work to catch mistakes and make improvements
        
        When Ollama is connected, I can provide more specific help with your writing!
        """
    
    else:
        return f"""
        # Fallback Response
        
        I notice you're asking about: "{prompt[:100]}..."
        
        I'd love to help you with this question, but I need to connect to Ollama to generate a complete response. 
        
        To use this application with full functionality:
        
        1. Make sure Ollama is installed on your computer
        2. Open a command prompt or terminal
        3. Run the command `ollama serve` to start the Ollama server
        4. Make sure you have the {model_name} model downloaded (or another model from the dropdown)
        5. Refresh this page
        
        While Ollama is disconnected, I can only provide limited pre-defined responses. Thank you for your understanding!
        """

