import streamlit as st
import sys
from pathlib import Path

# Add the parent directory to sys.path
app_path = Path(__file__).parent
sys.path.append(str(app_path))

# Import utils
from utils.ollama_utils import get_ai_response, format_prompt_for_grade_level

def generate_educational_prompt(topic, grade_level, prompt_type):
    """Generate an educational prompt based on topic, grade level, and prompt type."""
    
    base_prompts = {
        "explain_concept": f"Explain the concept of {topic} in a way that's easy to understand.",
        "step_by_step": f"Provide a step-by-step explanation of how to solve problems related to {topic}.",
        "examples": f"Give examples of {topic} with explanations appropriate for this grade level.",
        "quiz": f"Create a short quiz about {topic} with answers.",
        "fun_facts": f"Share interesting and engaging facts about {topic}.",
        "visual_description": f"Describe {topic} using visual analogies and examples that are easy to picture.",
        "real_world": f"Explain how {topic} applies to real-world situations and everyday life.",
        "compare_contrast": f"Compare and contrast {topic} with related concepts to highlight similarities and differences."
    }
    
    if prompt_type in base_prompts:
        base_prompt = base_prompts[prompt_type]
    else:
        base_prompt = base_prompts["explain_concept"]
    
    # Format the prompt for the appropriate grade level
    return format_prompt_for_grade_level(base_prompt, grade_level)

def test_educational_prompts():
    """Test the educational prompt generation functionality."""
    st.title("Educational AI Prompt Generator")
    
    st.write("This tool demonstrates the educational AI prompt generation capabilities.")
    
    # Topic input
    topic = st.text_input(
        "Enter an educational topic",
        "photosynthesis"
    )
    
    # Grade level selection
    grade_level = st.selectbox(
        "Select grade level",
        ["K-2 (Elementary)", "3-5 (Elementary)", "6-8 (Middle School)", "9-12 (High School)"]
    )
    
    # Prompt type selection
    prompt_type = st.selectbox(
        "Select prompt type",
        ["explain_concept", "step_by_step", "examples", "quiz", "fun_facts", 
         "visual_description", "real_world", "compare_contrast"]
    )
    
    if st.button("Generate Educational Prompt"):
        if not topic:
            st.warning("Please enter a topic.")
        else:
            # Generate the educational prompt
            prompt = generate_educational_prompt(topic, grade_level, prompt_type)
            
            # Display the generated prompt
            st.subheader("Generated Prompt")
            st.text_area("Prompt", prompt, height=300)
            
            # Option to test with Ollama
            st.subheader("Test with Ollama")
            st.write("Click below to test this prompt with Ollama (if available).")
            
            model = st.selectbox(
                "Select model to test",
                ["llama3:3b", "phi:latest", "mistral:7b", "gemma:7b"]
            )
            
            if st.button("Generate Response"):
                with st.spinner("Generating response..."):
                    try:
                        response = get_ai_response(prompt, model)
                        st.subheader("AI Response")
                        st.markdown(response)
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                        st.info("Make sure Ollama is running on your computer with the selected model available.")

if __name__ == "__main__":
    test_educational_prompts()
