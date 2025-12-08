import streamlit as st
from utils.ollama_utils import get_ai_response
from utils.educational_prompts import generate_educational_prompt

def generate_adaptive_content(topic, grade_level, content_type):
    """
    Generate grade-level appropriate educational content.
    
    Args:
        topic (str): The educational topic
        grade_level (str): The grade level (e.g., "K-2 (Elementary)")
        content_type (str): The type of content to generate
        
    Returns:
        str: The generated educational content
    """
    # Map content types to prompt types
    content_to_prompt = {
        "explanation": "explain_concept",
        "tutorial": "step_by_step",
        "examples": "examples",
        "quiz": "quiz",
        "facts": "fun_facts",
        "visual": "visual_description",
        "application": "real_world",
        "comparison": "compare_contrast"
    }
    
    # Get the appropriate prompt type
    prompt_type = content_to_prompt.get(content_type, "explain_concept")
    
    # Generate the educational prompt
    prompt = generate_educational_prompt(topic, grade_level, prompt_type)
    
    # Get response from AI
    try:
        response = get_ai_response(prompt, st.session_state.selected_model)
        return response
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Make sure Ollama is running on your computer with the selected model available.")
        return "Unable to generate content. Please check if Ollama is running."

def render_content_preview(topic, grade_level, content_type):
    """Render a preview of the generated content."""
    with st.spinner("Generating content..."):
        content = generate_adaptive_content(topic, grade_level, content_type)
        st.markdown(content)
        
        # Add download button for the content
        st.download_button(
            label="Download Content",
            data=content,
            file_name=f"{topic.replace(' ', '_')}_{content_type}.md",
            mime="text/markdown"
        )

def get_subject_topics(subject):
    """Get a list of common topics for a given subject."""
    topics = {
        "Math": ["Addition and Subtraction", "Multiplication and Division", "Fractions", 
                "Decimals", "Algebra", "Geometry", "Statistics", "Probability"],
        "Science": ["Plants and Animals", "Weather and Climate", "Solar System", 
                   "States of Matter", "Energy", "Human Body", "Ecosystems", "Simple Machines"],
        "English": ["Grammar Rules", "Vocabulary Building", "Story Elements", 
                   "Reading Comprehension", "Writing Process", "Poetry", "Literary Devices"],
        "History": ["Ancient Civilizations", "American History", "World Wars", 
                   "Civil Rights Movement", "Government Systems", "Cultural Studies", "Geography"],
        "Art": ["Color Theory", "Drawing Techniques", "Famous Artists", 
               "Art History", "Sculpture", "Painting Styles", "Digital Art"],
        "Music": ["Musical Instruments", "Reading Music", "Music History", 
                 "Famous Composers", "Music Theory", "Singing Techniques"],
        "Physical Education": ["Team Sports", "Individual Sports", "Fitness", 
                              "Nutrition", "Health and Wellness", "Motor Skills"],
        "Computer Science": ["Coding Basics", "Algorithms", "Internet Safety", 
                            "Digital Citizenship", "Hardware vs Software", "Web Design"]
    }
    
    return topics.get(subject, ["General Topics"])
