import streamlit as st
from utils.ollama_utils import get_ai_response

def generate_quiz(subject, topic, grade_level, num_questions=5, difficulty="Medium"):
    """
    Generate a quiz on a specific topic.
    
    Args:
        subject (str): The subject area
        topic (str): The specific topic
        grade_level (str): The grade level
        num_questions (int): Number of questions to generate
        difficulty (str): Difficulty level (Easy, Medium, Hard)
        
    Returns:
        str: The generated quiz
    """
    prompt = f"""
    Create an educational quiz on {topic} in {subject} for students in {grade_level}.
    
    Generate {num_questions} questions at {difficulty} difficulty level.
    Include a mix of question types (multiple choice, true/false, short answer).
    
    For each question:
    1. Provide the question
    2. For multiple choice, provide 4 options with one correct answer
    3. Include the correct answer
    4. Provide a brief explanation for the correct answer
    
    Format each question as:
    
    Q1: [Question text]
    Options:
    A. [Option A]
    B. [Option B]
    C. [Option C]
    D. [Option D]
    Correct Answer: [Letter]
    Explanation: [Brief explanation]
    
    Make the quiz educational, engaging, and appropriate for {grade_level} students.
    """
    
    try:
        response = get_ai_response(prompt, st.session_state.selected_model)
        return response
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return "Unable to generate quiz. Please check if Ollama is running."

def generate_lesson_plan(subject, topic, grade_level, duration="45 minutes"):
    """
    Generate a lesson plan on a specific topic.
    
    Args:
        subject (str): The subject area
        topic (str): The specific topic
        grade_level (str): The grade level
        duration (str): Lesson duration
        
    Returns:
        str: The generated lesson plan
    """
    prompt = f"""
    Create a detailed lesson plan for teaching {topic} in {subject} to students in {grade_level}.
    The lesson should be designed for a {duration} class period.
    
    Include the following components:
    1. Learning Objectives
    2. Materials Needed
    3. Warm-up Activity (5-10 minutes)
    4. Main Instruction (15-20 minutes)
    5. Student Activity (15-20 minutes)
    6. Assessment Method
    7. Closure (5 minutes)
    
    Structure the lesson plan with clear headings and sections.
    Provide specific activities, questions, and examples appropriate for {grade_level}.
    Include timing guidelines for each section of the lesson.
    """
    
    try:
        response = get_ai_response(prompt, st.session_state.selected_model)
        return response
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return "Unable to generate lesson plan. Please check if Ollama is running."

def generate_study_guide(subject, topic, grade_level):
    """
    Generate a study guide on a specific topic.
    
    Args:
        subject (str): The subject area
        topic (str): The specific topic
        grade_level (str): The grade level
        
    Returns:
        str: The generated study guide
    """
    prompt = f"""
    Create a comprehensive study guide on {topic} in {subject} for students in {grade_level}.
    
    Include the following elements:
    1. Key Concepts (main ideas and principles)
    2. Vocabulary List (important terms with definitions)
    3. Examples and Illustrations
    4. Common Misconceptions
    5. Practice Questions (with answers)
    6. Memory Tips and Mnemonics
    
    Structure the study guide in a clear, organized way with headings and subheadings.
    Use language and explanations suitable for {grade_level} students.
    Make the content educational, accurate, and engaging.
    """
    
    try:
        response = get_ai_response(prompt, st.session_state.selected_model)
        return response
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return "Unable to generate study guide. Please check if Ollama is running."

def generate_writing_prompt(writing_type, grade_level, theme=None):
    """
    Generate a writing prompt.
    
    Args:
        writing_type (str): Type of writing (narrative, persuasive, etc.)
        grade_level (str): The grade level
        theme (str, optional): Specific theme or topic
        
    Returns:
        str: The generated writing prompt
    """
    theme_text = f"on the theme of {theme}" if theme else ""
    
    prompt = f"""
    Create an engaging {writing_type} writing prompt {theme_text} for students in {grade_level}.
    
    The prompt should:
    1. Be clear and specific
    2. Be appropriate for {grade_level} students
    3. Encourage creativity and critical thinking
    4. Include any necessary background information
    5. Provide guidance on length or structure if appropriate
    
    Also include:
    - A title for the prompt
    - A brief description of the purpose
    - 2-3 questions to help students brainstorm ideas
    - Success criteria (what makes a good response)
    """
    
    try:
        response = get_ai_response(prompt, st.session_state.selected_model)
        return response
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return "Unable to generate writing prompt. Please check if Ollama is running."

def generate_feedback(assignment_type, grade_level, strengths=None, improvements=None):
    """
    Generate constructive feedback for a student.
    
    Args:
        assignment_type (str): Type of assignment
        grade_level (str): The grade level
        strengths (str, optional): Specific strengths to mention
        improvements (str, optional): Areas for improvement to mention
        
    Returns:
        str: The generated feedback
    """
    strengths_text = f"Specific strengths: {strengths}" if strengths else ""
    improvements_text = f"Areas for improvement: {improvements}" if improvements else ""
    
    prompt = f"""
    Generate constructive feedback for a student in {grade_level} who completed a {assignment_type}.
    
    {strengths_text}
    {improvements_text}
    
    Include the following in your feedback:
    1. Positive comments on strengths
    2. Constructive criticism on areas for improvement
    3. Specific suggestions for how to improve
    4. Encouraging closing remarks
    
    Make the feedback specific, constructive, and appropriate for {grade_level}.
    Use a supportive and encouraging tone throughout.
    """
    
    try:
        response = get_ai_response(prompt, st.session_state.selected_model)
        return response
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return "Unable to generate feedback. Please check if Ollama is running."
