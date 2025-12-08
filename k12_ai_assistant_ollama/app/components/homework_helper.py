import streamlit as st
from utils.ollama_utils import get_ai_response
from utils.display_utils import display_response, display_streaming_response

def render_homework_helper():
    """Render the Homework Helper tool interface."""
    st.header("Homework Helper")
    
    st.markdown("""
    Need help with your homework? Ask questions about any subject and get step-by-step explanations.
    The AI will adapt explanations to your grade level.
    """)
    
    # Subject selection
    subject = st.selectbox(
        "Select Subject",
        ["Math", "Science", "English", "History", "Geography", "Other"]
    )
    
    # Question input
    question = st.text_area(
        "Enter your homework question",
        height=100,
        placeholder="Example: How do I solve for x in the equation 2x + 5 = 13?"
    )
    
    # Additional context
    context = st.text_area(
        "Additional context (optional)",
        height=75,
        placeholder="Add any additional information that might help the AI understand your question better."
    )
    
    # Initialize session state for responses
    if "homework_response" not in st.session_state:
        st.session_state.homework_response = None
    if "simplified_response" not in st.session_state:
        st.session_state.simplified_response = None
    if "detailed_response" not in st.session_state:
        st.session_state.detailed_response = None
    
    # Submit button
    if st.button("Get Help"):
        if not question:
            st.warning("Please enter a question to get help.")
        else:
            # Clear previous responses
            st.session_state.homework_response = None
            st.session_state.simplified_response = None
            st.session_state.detailed_response = None
            
            # Prepare prompt with grade level adaptation
            grade_level = st.session_state.grade_level
            prompt = f"""
            Subject: {subject}
            Grade Level: {grade_level}
            Question: {question}
            Additional Context: {context}
            
            Please provide a helpful, educational response to this homework question.
            Adapt your explanation to be appropriate for a student in {grade_level}.
            Include step-by-step explanations where applicable.
            """
            
            # Get streaming response from AI
            st.subheader("Answer")
            try:
                # Try streaming first
                stream_generator = get_ai_response(prompt, st.session_state.selected_model, stream=True)
                response = display_streaming_response(stream_generator, header=None)
                
                # If streaming returned None or empty, fall back to non-streaming
                if not response:
                    st.info("Streaming didn't work, trying non-streaming mode...")
                    response = get_ai_response(prompt, st.session_state.selected_model, stream=False)
                    if response:
                        display_response(response, header=None)
                
                # Store the complete response in session state
                if response:
                    st.session_state.homework_response = response
                    st.session_state.current_question = question
                    st.session_state.current_subject = subject
                    st.session_state.current_grade_level = grade_level
                    
                    # Show the buttons for additional actions after streaming
                    st.markdown("---")
                    if st.session_state.simplified_response:
                        display_response(st.session_state.simplified_response, header="Simplified Answer")
                    else:
                        if st.button("Get Simpler Explanation", key="simpler_btn_after"):
                            try:
                                simplified_prompt = f"""
                                The previous explanation was too complex. Please explain the following in much simpler terms, 
                                appropriate for a student in {st.session_state.current_grade_level}:
                                
                                Subject: {st.session_state.current_subject}
                                Question: {st.session_state.current_question}
                                
                                Use very simple language, step-by-step explanations, and relatable examples.
                                """
                                # Use streaming for simpler explanation too
                                st.subheader("Simplified Answer")
                                stream_generator = get_ai_response(simplified_prompt, st.session_state.selected_model, stream=True)
                                simplified_response = display_streaming_response(stream_generator, header=None)
                                
                                if not simplified_response:
                                    # Fallback to non-streaming
                                    simplified_response = get_ai_response(simplified_prompt, st.session_state.selected_model, stream=False)
                                    if simplified_response:
                                        display_response(simplified_response, header=None)
                                
                                if simplified_response:
                                    st.session_state.simplified_response = simplified_response
                                    st.rerun()
                            except Exception as e:
                                st.error(f"An error occurred: {str(e)}")
                else:
                    st.error("❌ No response received. Please check if Ollama is running.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                import traceback
                with st.expander("Error Details"):
                    st.code(traceback.format_exc())
                st.info("""
                **Ollama Backend Error**
                
                Make sure Ollama is running on your computer:
                1. Open a terminal and run: `ollama serve`
                2. Make sure you have downloaded a model: `ollama pull <model-name>`
                3. Refresh this page and try again
                """)
    
    # Display main response if available (stored from previous interaction)
    # Only show if we're not currently in the streaming button click block
    if st.session_state.homework_response and not st.button.__wrapped__ if hasattr(st.button, '__wrapped__') else True:
        # Check if we just finished streaming by looking at session state
        if "just_streamed" not in st.session_state:
            # Display response uniformly without any dropdowns or interactive elements
            display_response(st.session_state.homework_response, header="Answer")
            
            # Option to get a simpler explanation
            st.markdown("---")
            if st.session_state.simplified_response:
                display_response(st.session_state.simplified_response, header="Simplified Answer")
            else:
                if st.button("Get Simpler Explanation", key="simpler_btn"):
                    try:
                        simplified_prompt = f"""
                        The previous explanation was too complex. Please explain the following in much simpler terms, 
                        appropriate for a student in {st.session_state.current_grade_level}:
                        
                        Subject: {st.session_state.current_subject}
                        Question: {st.session_state.current_question}
                        
                        Use very simple language, step-by-step explanations, and relatable examples.
                        """
                        # Use streaming for simpler explanation too
                        stream_generator = get_ai_response(simplified_prompt, st.session_state.selected_model, stream=True)
                        simplified_response = display_streaming_response(stream_generator, header="Simplified Answer")
                        
                        if simplified_response:
                            st.session_state.simplified_response = simplified_response
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
        else:
            # Clear the flag so we show stored response on next render
            del st.session_state.just_streamed
    
    # Tips section
    with st.expander("Tips for getting better answers"):
        st.markdown("""
        - Be specific in your questions
        - Include any relevant formulas or concepts you're working with
        - Specify what part you're struggling with
        - For math problems, include the full problem statement
        """)
