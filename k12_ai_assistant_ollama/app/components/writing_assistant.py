import streamlit as st
from utils.ollama_utils import get_ai_response

def render_writing_assistant():
    """Render the Writing Assistant tool interface."""
    st.header("Writing Assistant")
    
    st.markdown("""
    Get help with your writing assignments! Generate ideas, improve your essays, 
    or get feedback on your writing.
    """)
    
    # Writing task selection
    writing_task = st.selectbox(
        "What would you like help with?",
        ["Essay Feedback", "Creative Writing", "Grammar Check", "Writing Prompts", "Vocabulary Enhancement"]
    )
    
    if writing_task == "Essay Feedback":
        render_essay_feedback()
    elif writing_task == "Creative Writing":
        render_creative_writing()
    elif writing_task == "Grammar Check":
        render_grammar_check()
    elif writing_task == "Writing Prompts":
        render_writing_prompts()
    elif writing_task == "Vocabulary Enhancement":
        render_vocabulary_enhancement()

def render_essay_feedback():
    """Render the Essay Feedback interface."""
    st.subheader("Essay Feedback")
    
    st.markdown("""
    Paste your essay below to get feedback on structure, clarity, and content.
    """)
    
    # Essay input
    essay = st.text_area(
        "Your essay",
        height=300,
        placeholder="Paste your essay here..."
    )
    
    # Essay type
    essay_type = st.selectbox(
        "Essay type",
        ["Argumentative", "Narrative", "Expository", "Descriptive", "Persuasive", "Compare and Contrast"]
    )
    
    # Submit button
    if st.button("Get Feedback"):
        if not essay:
            st.warning("Please enter your essay to get feedback.")
        else:
            with st.spinner("Analyzing your essay..."):
                # Prepare prompt with grade level adaptation
                grade_level = st.session_state.grade_level
                prompt = f"""
                Essay Type: {essay_type}
                Grade Level: {grade_level}
                Essay: {essay}
                
                Please provide constructive feedback on this {essay_type} essay written by a student in {grade_level}.
                Include comments on:
                1. Structure and organization
                2. Clarity and coherence
                3. Grammar and spelling
                4. Content and ideas
                5. Specific suggestions for improvement
                
                Be encouraging and supportive while providing actionable feedback appropriate for the student's grade level.
                """
                
                try:
                    response = get_ai_response(prompt, st.session_state.selected_model)
                    
                    # Display response
                    st.subheader("Feedback")
                    st.markdown(response)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.info("Make sure Ollama is running on your computer with the selected model available.")

def render_creative_writing():
    """Render the Creative Writing interface."""
    st.subheader("Creative Writing Assistant")
    
    st.markdown("""
    Get help with creative writing projects, story ideas, or character development.
    """)
    
    # Writing type
    writing_type = st.selectbox(
        "What type of creative writing?",
        ["Short Story", "Poem", "Character Development", "Setting Description", "Dialogue Writing"]
    )
    
    # Topic or theme
    topic = st.text_input(
        "Topic or theme (optional)",
        placeholder="E.g., adventure, friendship, mystery, etc."
    )
    
    # Additional instructions
    instructions = st.text_area(
        "Additional instructions or context",
        height=100,
        placeholder="Any specific elements you want to include or focus on..."
    )
    
    # Submit button
    if st.button("Generate Ideas"):
        with st.spinner("Creating ideas..."):
            # Prepare prompt with grade level adaptation
            grade_level = st.session_state.grade_level
            prompt = f"""
            Writing Type: {writing_type}
            Grade Level: {grade_level}
            Topic/Theme: {topic}
            Additional Instructions: {instructions}
            
            Please provide creative writing assistance for a student in {grade_level} working on a {writing_type}.
            Generate ideas, suggestions, or examples appropriate for their grade level.
            If the topic is specified, incorporate it into your response.
            """
            
            try:
                response = get_ai_response(prompt, st.session_state.selected_model)
                
                # Display response
                st.subheader("Creative Writing Ideas")
                st.markdown(response)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Make sure Ollama is running on your computer with the selected model available.")

def render_grammar_check():
    """Render the Grammar Check interface."""
    st.subheader("Grammar Check")
    
    st.markdown("""
    Check your writing for grammar, spelling, and punctuation errors.
    """)
    
    # Text input
    text = st.text_area(
        "Your text",
        height=200,
        placeholder="Enter the text you want to check..."
    )
    
    # Submit button
    if st.button("Check Grammar"):
        if not text:
            st.warning("Please enter some text to check.")
        else:
            with st.spinner("Checking grammar..."):
                prompt = f"""
                Please check the following text for grammar, spelling, and punctuation errors.
                Provide corrections and explanations for each error found.
                
                Text: {text}
                """
                
                try:
                    response = get_ai_response(prompt, st.session_state.selected_model)
                    
                    # Display response
                    st.subheader("Grammar Check Results")
                    st.markdown(response)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.info("Make sure Ollama is running on your computer with the selected model available.")

def render_writing_prompts():
    """Render the Writing Prompts interface."""
    st.subheader("Writing Prompts")
    
    st.markdown("""
    Get creative writing prompts tailored to your grade level and interests.
    """)
    
    # Genre selection
    genre = st.selectbox(
        "Select genre",
        ["Fantasy", "Science Fiction", "Mystery", "Historical", "Realistic Fiction", "Adventure", "Any"]
    )
    
    # Number of prompts
    num_prompts = st.slider("Number of prompts", 1, 10, 5)
    
    # Submit button
    if st.button("Generate Prompts"):
        with st.spinner("Generating prompts..."):
            # Prepare prompt with grade level adaptation
            grade_level = st.session_state.grade_level
            prompt = f"""
            Genre: {genre}
            Grade Level: {grade_level}
            Number of Prompts: {num_prompts}
            
            Please generate {num_prompts} creative writing prompts in the {genre} genre appropriate for a student in {grade_level}.
            Each prompt should be engaging, age-appropriate, and spark creativity.
            Format each prompt as a numbered list item with a title and brief description.
            """
            
            try:
                response = get_ai_response(prompt, st.session_state.selected_model)
                
                # Display response
                st.subheader("Writing Prompts")
                st.markdown(response)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Make sure Ollama is running on your computer with the selected model available.")

def render_vocabulary_enhancement():
    """Render the Vocabulary Enhancement interface."""
    st.subheader("Vocabulary Enhancement")
    
    st.markdown("""
    Improve your vocabulary or find better words for your writing.
    """)
    
    # Enhancement type
    enhancement_type = st.radio(
        "What would you like to do?",
        ["Find synonyms", "Learn new words", "Simplify complex text", "Enhance simple text"]
    )
    
    if enhancement_type == "Find synonyms":
        word = st.text_input("Enter a word to find synonyms")
        context = st.text_input("Context (optional)", placeholder="How the word is being used")
        
        if st.button("Find Synonyms"):
            if not word:
                st.warning("Please enter a word.")
            else:
                with st.spinner("Finding synonyms..."):
                    grade_level = st.session_state.grade_level
                    prompt = f"""
                    Word: {word}
                    Context: {context}
                    Grade Level: {grade_level}
                    
                    Please provide a list of synonyms for the word "{word}" that would be appropriate for a student in {grade_level}.
                    If context is provided, ensure the synonyms would work in that context.
                    For each synonym, provide a brief example of how it could be used in a sentence.
                    """
                    
                    try:
                        response = get_ai_response(prompt, st.session_state.selected_model)
                        st.markdown(response)
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
    
    elif enhancement_type == "Learn new words":
        subject = st.text_input("Subject or topic area")
        num_words = st.slider("Number of words", 5, 20, 10)
        
        if st.button("Generate Vocabulary List"):
            if not subject:
                st.warning("Please enter a subject or topic.")
            else:
                with st.spinner("Creating vocabulary list..."):
                    grade_level = st.session_state.grade_level
                    prompt = f"""
                    Subject: {subject}
                    Grade Level: {grade_level}
                    Number of Words: {num_words}
                    
                    Please create a vocabulary list of {num_words} words related to {subject} that would be appropriate for a student in {grade_level}.
                    For each word, provide:
                    1. The word
                    2. Its definition in simple terms
                    3. An example sentence using the word
                    4. A memory tip to help remember the word (if applicable)
                    """
                    
                    try:
                        response = get_ai_response(prompt, st.session_state.selected_model)
                        st.markdown(response)
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
    
    elif enhancement_type == "Simplify complex text":
        text = st.text_area("Enter complex text to simplify", height=150)
        
        if st.button("Simplify Text"):
            if not text:
                st.warning("Please enter some text to simplify.")
            else:
                with st.spinner("Simplifying text..."):
                    grade_level = st.session_state.grade_level
                    prompt = f"""
                    Text: {text}
                    Grade Level: {grade_level}
                    
                    Please simplify the following text to make it more accessible for a student in {grade_level}.
                    Maintain the key information while using simpler vocabulary and sentence structures.
                    """
                    
                    try:
                        response = get_ai_response(prompt, st.session_state.selected_model)
                        st.subheader("Simplified Text")
                        st.markdown(response)
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
    
    elif enhancement_type == "Enhance simple text":
        text = st.text_area("Enter text to enhance", height=150)
        
        if st.button("Enhance Text"):
            if not text:
                st.warning("Please enter some text to enhance.")
            else:
                with st.spinner("Enhancing text..."):
                    grade_level = st.session_state.grade_level
                    prompt = f"""
                    Text: {text}
                    Grade Level: {grade_level}
                    
                    Please enhance the following text by improving vocabulary and sentence structure while keeping it appropriate for a student in {grade_level}.
                    Suggest more descriptive words, varied sentence structures, and improved phrasing.
                    Provide both the enhanced version and explanations of the changes made.
                    """
                    
                    try:
                        response = get_ai_response(prompt, st.session_state.selected_model)
                        st.subheader("Enhanced Text")
                        st.markdown(response)
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
