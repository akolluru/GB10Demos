import streamlit as st
from utils.ollama_utils import get_ai_response

def generate_concept_map(subject, topic, grade_level):
    """
    Generate a concept map for a specific topic.
    
    Args:
        subject (str): The subject area
        topic (str): The specific topic
        grade_level (str): The grade level
        
    Returns:
        str: The generated concept map description
    """
    prompt = f"""
    Create a concept map for {topic} in {subject} appropriate for students in {grade_level}.
    
    The concept map should:
    1. Identify the main concept ({topic}) at the center
    2. Include 5-8 key related concepts or subtopics
    3. Show connections between concepts with brief descriptions of relationships
    4. Be organized in a logical hierarchy or structure
    5. Include brief explanations of each concept
    
    Format the concept map as a text description that could be used to create a visual concept map.
    Use markdown formatting with headers, bullet points, and emphasis where appropriate.
    Make the content educational, accurate, and appropriate for {grade_level} students.
    """
    
    try:
        response = get_ai_response(prompt, st.session_state.selected_model)
        return response
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return "Unable to generate concept map. Please check if Ollama is running."

def generate_vocabulary_list(subject, topic, grade_level, num_terms=10):
    """
    Generate a vocabulary list for a specific topic.
    
    Args:
        subject (str): The subject area
        topic (str): The specific topic
        grade_level (str): The grade level
        num_terms (int): Number of vocabulary terms to generate
        
    Returns:
        str: The generated vocabulary list
    """
    prompt = f"""
    Create a vocabulary list of {num_terms} important terms related to {topic} in {subject} for students in {grade_level}.
    
    For each term, provide:
    1. The word or phrase
    2. A clear, grade-appropriate definition
    3. An example sentence using the term
    4. A memory tip or mnemonic device (where helpful)
    
    Format the vocabulary list with clear headings and numbered entries.
    Make sure the terms and definitions are accurate and appropriate for {grade_level} students.
    """
    
    try:
        response = get_ai_response(prompt, st.session_state.selected_model)
        return response
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return "Unable to generate vocabulary list. Please check if Ollama is running."

def generate_discussion_questions(subject, topic, grade_level, num_questions=5):
    """
    Generate discussion questions for a specific topic.
    
    Args:
        subject (str): The subject area
        topic (str): The specific topic
        grade_level (str): The grade level
        num_questions (int): Number of questions to generate
        
    Returns:
        str: The generated discussion questions
    """
    prompt = f"""
    Create {num_questions} thought-provoking discussion questions about {topic} in {subject} for students in {grade_level}.
    
    Include a mix of question types:
    - Factual recall questions
    - Comprehension questions
    - Application questions
    - Analysis questions
    - Evaluation questions
    - Creative thinking questions
    
    For each question:
    1. Provide the question
    2. Include a brief teacher note with possible discussion points or answers
    
    Format each question with a number and clear structure.
    Make the questions engaging, educational, and appropriate for {grade_level} students.
    """
    
    try:
        response = get_ai_response(prompt, st.session_state.selected_model)
        return response
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return "Unable to generate discussion questions. Please check if Ollama is running."

def generate_experiment_activity(subject, topic, grade_level):
    """
    Generate a hands-on experiment or activity for a specific topic.
    
    Args:
        subject (str): The subject area
        topic (str): The specific topic
        grade_level (str): The grade level
        
    Returns:
        str: The generated experiment or activity
    """
    prompt = f"""
    Create a hands-on experiment or activity about {topic} in {subject} for students in {grade_level}.
    
    Include the following:
    1. Title of the experiment/activity
    2. Learning objectives
    3. Materials needed (common, easily available items)
    4. Step-by-step instructions
    5. Expected results or outcomes
    6. Discussion questions
    7. Extensions or variations
    8. Safety considerations (if applicable)
    
    The activity should be:
    - Engaging and interactive
    - Appropriate for {grade_level} students
    - Doable in a classroom or home setting
    - Illustrative of key concepts related to {topic}
    - Requiring minimal specialized equipment
    
    Format with clear headings and numbered steps.
    """
    
    try:
        response = get_ai_response(prompt, st.session_state.selected_model)
        return response
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return "Unable to generate experiment/activity. Please check if Ollama is running."

def generate_differentiated_content(subject, topic, grade_level, learning_level):
    """
    Generate differentiated content for different learning levels.
    
    Args:
        subject (str): The subject area
        topic (str): The specific topic
        grade_level (str): The grade level
        learning_level (str): Learning level (Basic, Standard, Advanced)
        
    Returns:
        str: The generated differentiated content
    """
    prompt = f"""
    Create differentiated educational content about {topic} in {subject} for {grade_level} students at a {learning_level} learning level.
    
    The content should include:
    1. A brief introduction to the topic
    2. Key concepts explained at the appropriate level
    3. Examples and illustrations
    4. Practice activities or questions
    5. Extension resources (for advanced) or support resources (for basic)
    
    For {learning_level} level:
    """
    
    if learning_level == "Basic":
        prompt += """
        - Use simpler vocabulary and shorter sentences
        - Focus on foundational concepts
        - Provide more scaffolding and support
        - Include more visual explanations
        - Break down complex ideas into smaller steps
        """
    elif learning_level == "Advanced":
        prompt += """
        - Use more sophisticated vocabulary and complex sentence structures
        - Include more in-depth content and nuanced explanations
        - Incorporate higher-order thinking questions
        - Make connections to broader concepts and other subjects
        - Include challenging extension activities
        """
    else:  # Standard
        prompt += """
        - Use grade-appropriate vocabulary and sentence structures
        - Cover the core curriculum concepts
        - Balance concrete examples with abstract ideas
        - Include a mix of question types
        - Provide moderate scaffolding
        """
    
    prompt += f"\nFormat the content with clear headings and sections, making it engaging and educational for {grade_level} students at a {learning_level} level."
    
    try:
        response = get_ai_response(prompt, st.session_state.selected_model)
        return response
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return "Unable to generate differentiated content. Please check if Ollama is running."
