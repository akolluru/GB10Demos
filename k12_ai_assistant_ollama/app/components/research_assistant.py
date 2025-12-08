import streamlit as st
from utils.ollama_utils import get_ai_response

def render_research_assistant():
    """Render the Research Assistant tool interface."""
    st.header("Research Assistant")
    
    st.markdown("""
    Explore topics, find information, and get help with research projects.
    The AI will provide age-appropriate information based on your grade level.
    """)
    
    # Research type selection
    research_type = st.selectbox(
        "What type of research help do you need?",
        ["Topic Exploration", "Fact Finding", "Summary Generation", "Study Guide Creation"]
    )
    
    if research_type == "Topic Exploration":
        render_topic_exploration()
    elif research_type == "Fact Finding":
        render_fact_finding()
    elif research_type == "Summary Generation":
        render_summary_generation()
    elif research_type == "Study Guide Creation":
        render_study_guide_creation()

def render_topic_exploration():
    """Render the Topic Exploration interface."""
    st.subheader("Topic Exploration")
    
    st.markdown("""
    Explore a topic to learn more about it. The AI will provide an overview and key information.
    """)
    
    # Topic input
    topic = st.text_input(
        "Enter a topic to explore",
        placeholder="Example: Ancient Egypt, Photosynthesis, World War II"
    )
    
    # Subject area
    subject = st.selectbox(
        "Subject area",
        ["Science", "History", "Geography", "Literature", "Art", "Technology", "Other"]
    )
    
    # Specific aspects
    aspects = st.text_area(
        "Specific aspects you're interested in (optional)",
        placeholder="Example: daily life, major discoveries, important figures"
    )
    
    # Submit button
    if st.button("Explore Topic"):
        if not topic:
            st.warning("Please enter a topic to explore.")
        else:
            with st.spinner("Researching..."):
                # Prepare prompt with grade level adaptation
                grade_level = st.session_state.grade_level
                prompt = f"""
                Topic: {topic}
                Subject: {subject}
                Grade Level: {grade_level}
                Specific Aspects: {aspects}
                
                Please provide an educational exploration of the topic "{topic}" appropriate for a student in {grade_level}.
                Include key information, important concepts, and interesting facts.
                If specific aspects are mentioned, focus on those areas.
                Structure the information in a clear, organized way with headings and subheadings include diagrams and images.
                """
                
                try:
                    response = get_ai_response(prompt, st.session_state.selected_model)
                    
                    # Display response
                    st.markdown(response)
                    
                    # Further exploration
                    st.markdown("---")
                    st.subheader("Further Exploration")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Related Topics"):
                            related_prompt = f"""
                            Based on the topic "{topic}", please suggest 5-7 related topics that a student in {grade_level} might find interesting to explore next.
                            For each related topic, provide a brief 1-2 sentence explanation of how it connects to {topic}.
                            """
                            related_response = get_ai_response(related_prompt, st.session_state.selected_model)
                            st.markdown(related_response)
                    
                    with col2:
                        if st.button("Key Vocabulary"):
                            vocab_prompt = f"""
                            Please create a list of 8-10 key vocabulary terms related to the topic "{topic}" that would be important for a student in {grade_level} to know.
                            For each term, provide:
                            1. A clear, age-appropriate definition
                            2. A simple example or context where applicable
                            """
                            vocab_response = get_ai_response(vocab_prompt, st.session_state.selected_model)
                            st.markdown(vocab_response)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.info("Make sure Ollama is running on your computer with the selected model available.")

def render_fact_finding():
    """Render the Fact Finding interface."""
    st.subheader("Fact Finding")
    
    st.markdown("""
    Find specific facts or answers to questions for your research.
    """)
    
    # Question input
    question = st.text_input(
        "Enter your research question",
        placeholder="Example: What is the tallest mountain in the world?"
    )
    
    # Context
    context = st.text_area(
        "Additional context (optional)",
        placeholder="Add any additional information that might help the AI understand your question better."
    )
    
    # Submit button
    if st.button("Find Facts"):
        if not question:
            st.warning("Please enter a research question.")
        else:
            with st.spinner("Searching for information..."):
                # Prepare prompt with grade level adaptation
                grade_level = st.session_state.grade_level
                prompt = f"""
                Research Question: {question}
                Grade Level: {grade_level}
                Additional Context: {context}
                
                Please provide a factual, educational answer to this research question appropriate for a student in {grade_level}.
                Include relevant facts, figures, and context.
                If there are multiple perspectives or interpretations, present them fairly.
                Cite sources or references where possible.
                """
                
                try:
                    response = get_ai_response(prompt, st.session_state.selected_model)
                    
                    # Display response
                    st.markdown(response)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.info("Make sure Ollama is running on your computer with the selected model available.")

def render_summary_generation():
    """Render the Summary Generation interface."""
    st.subheader("Summary Generation")
    
    st.markdown("""
    Generate summaries of texts or topics for your research.
    """)
    
    # Summary type
    summary_type = st.radio(
        "What would you like to summarize?",
        ["Text Passage", "Topic or Concept"]
    )
    
    if summary_type == "Text Passage":
        # Text input
        text = st.text_area(
            "Enter the text to summarize",
            height=250,
            placeholder="Paste the text you want to summarize here..."
        )
        
        # Length selection
        length = st.select_slider(
            "Summary length",
            options=["Very Short", "Short", "Medium", "Detailed"]
        )
        
        # Submit button
        if st.button("Generate Summary"):
            if not text:
                st.warning("Please enter text to summarize.")
            else:
                with st.spinner("Generating summary..."):
                    # Prepare prompt with grade level adaptation
                    grade_level = st.session_state.grade_level
                    prompt = f"""
                    Text: {text}
                    Grade Level: {grade_level}
                    Summary Length: {length}
                    
                    Please generate a {length.lower()} summary of the provided text that would be appropriate for a student in {grade_level}.
                    Focus on the main ideas and key points.
                    Use language and explanations suitable for the student's grade level.
                    """
                    
                    try:
                        response = get_ai_response(prompt, st.session_state.selected_model)
                        
                        # Display response
                        st.subheader("Summary")
                        st.markdown(response)
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                        st.info("Make sure Ollama is running on your computer with the selected model available.")
    
    elif summary_type == "Topic or Concept":
        # Topic input
        topic = st.text_input(
            "Enter the topic or concept to summarize",
            placeholder="Example: Photosynthesis, The American Revolution"
        )
        
        # Subject area
        subject = st.selectbox(
            "Subject area",
            ["Science", "History", "Geography", "Literature", "Art", "Technology", "Other"]
        )
        
        # Length selection
        length = st.select_slider(
            "Summary length",
            options=["Very Short", "Short", "Medium", "Detailed"]
        )
        
        # Submit button
        if st.button("Generate Summary"):
            if not topic:
                st.warning("Please enter a topic to summarize.")
            else:
                with st.spinner("Generating summary..."):
                    # Prepare prompt with grade level adaptation
                    grade_level = st.session_state.grade_level
                    prompt = f"""
                    Topic: {topic}
                    Subject: {subject}
                    Grade Level: {grade_level}
                    Summary Length: {length}
                    
                    Please generate a {length.lower()} summary of the topic "{topic}" that would be appropriate for a student in {grade_level}.
                    Focus on the main ideas, key concepts, and important information.
                    Use language and explanations suitable for the student's grade level.
                    Structure the summary in a clear, organized way.
                    """
                    
                    try:
                        response = get_ai_response(prompt, st.session_state.selected_model)
                        
                        # Display response
                        st.subheader("Summary")
                        st.markdown(response)
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                        st.info("Make sure Ollama is running on your computer with the selected model available.")

def render_study_guide_creation():
    """Render the Study Guide Creation interface."""
    st.subheader("Study Guide Creation")
    
    st.markdown("""
    Create a study guide for a topic or subject to help with your research and learning.
    """)
    
    # Topic input
    topic = st.text_input(
        "Enter the topic for your study guide",
        placeholder="Example: Cell Biology, American Civil War"
    )
    
    # Subject area
    subject = st.selectbox(
        "Subject area",
        ["Science", "History", "Geography", "Literature", "Math", "Language Arts", "Other"]
    )
    
    # Study guide elements
    st.write("Select elements to include in your study guide:")
    col1, col2 = st.columns(2)
    with col1:
        include_key_concepts = st.checkbox("Key Concepts", value=True)
        include_vocabulary = st.checkbox("Vocabulary List", value=True)
        include_timeline = st.checkbox("Timeline/Sequence", value=False)
    with col2:
        include_examples = st.checkbox("Examples/Illustrations", value=True)
        include_practice = st.checkbox("Practice Questions", value=True)
        include_resources = st.checkbox("Additional Resources", value=False)
    
    # Submit button
    if st.button("Create Study Guide"):
        if not topic:
            st.warning("Please enter a topic for your study guide.")
        else:
            with st.spinner("Creating study guide..."):
                # Prepare prompt with grade level adaptation
                grade_level = st.session_state.grade_level
                
                # Build elements list
                elements = []
                if include_key_concepts:
                    elements.append("Key Concepts")
                if include_vocabulary:
                    elements.append("Vocabulary List")
                if include_timeline:
                    elements.append("Timeline/Sequence")
                if include_examples:
                    elements.append("Examples/Illustrations")
                if include_practice:
                    elements.append("Practice Questions")
                if include_resources:
                    elements.append("Additional Resources")
                
                elements_str = ", ".join(elements)
                
                prompt = f"""
                Topic: {topic}
                Subject: {subject}
                Grade Level: {grade_level}
                Elements to Include: {elements_str}
                
                Please create a comprehensive study guide on the topic "{topic}" appropriate for a student in {grade_level}.
                Include the following elements: {elements_str}.
                Structure the study guide in a clear, organized way with headings and subheadings.
                Use language and explanations suitable for the student's grade level.
                """
                
                try:
                    response = get_ai_response(prompt, st.session_state.selected_model)
                    
                    # Display response
                    st.subheader("Study Guide")
                    st.markdown(response)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.info("Make sure Ollama is running on your computer with the selected model available.")
