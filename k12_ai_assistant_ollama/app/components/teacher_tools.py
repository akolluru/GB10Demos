import streamlit as st
from utils.ollama_utils import get_ai_response

def render_teacher_tools():
    """Render the Teacher Tools interface."""
    st.header("Teacher Tools")
    
    st.markdown("""
    Tools to help teachers with lesson planning, assignment creation, and grading assistance.
    """)
    
    # Tool selection
    tool_type = st.selectbox(
        "Select a teacher tool",
        ["Lesson Plan Generator", "Assignment Creator", "Rubric Builder", "Discussion Questions", "Feedback Generator"]
    )
    
    if tool_type == "Lesson Plan Generator":
        render_lesson_plan_generator()
    elif tool_type == "Assignment Creator":
        render_assignment_creator()
    elif tool_type == "Rubric Builder":
        render_rubric_builder()
    elif tool_type == "Discussion Questions":
        render_discussion_questions()
    elif tool_type == "Feedback Generator":
        render_feedback_generator()

def render_lesson_plan_generator():
    """Render the Lesson Plan Generator interface."""
    st.subheader("Lesson Plan Generator")
    
    st.markdown("""
    Generate detailed lesson plans for any subject and grade level.
    """)
    
    # Subject
    subject = st.text_input(
        "Subject",
        placeholder="Example: Science, Math, English, History"
    )
    
    # Topic
    topic = st.text_input(
        "Specific topic",
        placeholder="Example: Photosynthesis, Fractions, Shakespeare, Civil War"
    )
    
    # Lesson duration
    duration = st.selectbox(
        "Lesson duration",
        ["30 minutes", "45 minutes", "60 minutes", "90 minutes"]
    )
    
    # Lesson components
    st.write("Select components to include in the lesson plan:")
    col1, col2 = st.columns(2)
    with col1:
        include_objectives = st.checkbox("Learning Objectives", value=True)
        include_materials = st.checkbox("Materials Needed", value=True)
        include_warmup = st.checkbox("Warm-up Activity", value=True)
    with col2:
        include_assessment = st.checkbox("Assessment Methods", value=True)
        include_differentiation = st.checkbox("Differentiation Strategies", value=True)
        include_homework = st.checkbox("Homework/Extension", value=False)
    
    # Generate lesson plan button
    if st.button("Generate Lesson Plan"):
        if not subject or not topic:
            st.warning("Please enter a subject and topic for your lesson plan.")
        else:
            with st.spinner("Creating lesson plan..."):
                # Build components list
                components = []
                if include_objectives:
                    components.append("Learning Objectives")
                if include_materials:
                    components.append("Materials Needed")
                if include_warmup:
                    components.append("Warm-up Activity")
                if include_assessment:
                    components.append("Assessment Methods")
                if include_differentiation:
                    components.append("Differentiation Strategies")
                if include_homework:
                    components.append("Homework/Extension")
                
                components_str = ", ".join(components)
                
                # Prepare prompt with grade level adaptation
                grade_level = st.session_state.grade_level
                prompt = f"""
                Subject: {subject}
                Topic: {topic}
                Grade Level: {grade_level}
                Lesson Duration: {duration}
                Components to Include: {components_str}
                
                Please create a detailed lesson plan for teaching {topic} in {subject} to students in {grade_level}.
                The lesson should be designed for a {duration} class period.
                
                Include the following components: {components_str}.
                
                Structure the lesson plan with clear headings and sections.
                Provide specific activities, questions, and examples appropriate for the grade level.
                Include timing guidelines for each section of the lesson.
                """
                
                try:
                    response = get_ai_response(prompt, st.session_state.selected_model)
                    
                    # Display response
                    st.subheader("Lesson Plan")
                    st.markdown(response)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.info("Make sure Ollama is running on your computer with the selected model available.")

def render_assignment_creator():
    """Render the Assignment Creator interface."""
    st.subheader("Assignment Creator")
    
    st.markdown("""
    Create customized assignments, worksheets, or projects for your students.
    """)
    
    # Assignment type
    assignment_type = st.selectbox(
        "Assignment type",
        ["Worksheet", "Project", "Essay Prompt", "Lab Activity", "Reading Assignment"]
    )
    
    # Subject
    subject = st.text_input(
        "Subject",
        placeholder="Example: Science, Math, English, History"
    )
    
    # Topic
    topic = st.text_input(
        "Specific topic",
        placeholder="Example: Ecosystems, Algebra, Creative Writing, World War II"
    )
    
    # Assignment details
    st.write("Assignment details:")
    
    # Duration/length
    if assignment_type in ["Project", "Essay Prompt"]:
        duration = st.text_input(
            "Expected duration or length",
            placeholder="Example: 1 week, 3-5 pages"
        )
    else:
        duration = st.text_input(
            "Expected completion time",
            placeholder="Example: 30 minutes, 1 hour"
        )
    
    # Difficulty level
    difficulty = st.select_slider(
        "Difficulty level",
        options=["Basic", "Standard", "Advanced", "Challenge"]
    )
    
    # Generate assignment button
    if st.button("Generate Assignment"):
        if not subject or not topic:
            st.warning("Please enter a subject and topic for your assignment.")
        else:
            with st.spinner("Creating assignment..."):
                # Prepare prompt with grade level adaptation
                grade_level = st.session_state.grade_level
                prompt = f"""
                Assignment Type: {assignment_type}
                Subject: {subject}
                Topic: {topic}
                Grade Level: {grade_level}
                Duration/Length: {duration}
                Difficulty Level: {difficulty}
                
                Please create a detailed {assignment_type} on {topic} in {subject} for students in {grade_level}.
                The assignment should be at {difficulty} difficulty level and designed to take approximately {duration} to complete.
                
                Include the following:
                1. Title
                2. Clear instructions
                3. Specific questions, tasks, or requirements
                4. Any necessary background information
                5. Grading criteria or expectations
                
                Make the assignment engaging, educational, and appropriate for the grade level.
                """
                
                try:
                    response = get_ai_response(prompt, st.session_state.selected_model)
                    
                    # Display response
                    st.subheader("Assignment")
                    st.markdown(response)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.info("Make sure Ollama is running on your computer with the selected model available.")

def render_rubric_builder():
    """Render the Rubric Builder interface."""
    st.subheader("Rubric Builder")
    
    st.markdown("""
    Create detailed grading rubrics for assignments and projects.
    """)
    
    # Assignment type
    assignment_type = st.text_input(
        "Assignment type",
        placeholder="Example: Essay, Presentation, Science Project, Art Portfolio"
    )
    
    # Subject
    subject = st.text_input(
        "Subject",
        placeholder="Example: Science, Math, English, History"
    )
    
    # Number of criteria
    num_criteria = st.slider("Number of evaluation criteria", 3, 10, 5)
    
    # Performance levels
    performance_levels = st.slider("Number of performance levels", 3, 5, 4)
    
    # Generate rubric button
    if st.button("Generate Rubric"):
        if not assignment_type or not subject:
            st.warning("Please enter an assignment type and subject for your rubric.")
        else:
            with st.spinner("Creating rubric..."):
                # Prepare prompt with grade level adaptation
                grade_level = st.session_state.grade_level
                prompt = f"""
                Assignment Type: {assignment_type}
                Subject: {subject}
                Grade Level: {grade_level}
                Number of Criteria: {num_criteria}
                Performance Levels: {performance_levels}
                
                Please create a detailed grading rubric for a {assignment_type} in {subject} for students in {grade_level}.
                Include {num_criteria} evaluation criteria and {performance_levels} performance levels.
                
                Structure the rubric as a table with:
                - Rows for each criterion
                - Columns for each performance level
                - Clear descriptions of expectations for each criterion at each performance level
                - Point values or percentages for each level
                
                Make the rubric clear, specific, and appropriate for the grade level.
                Format the rubric in markdown table format.
                """
                
                try:
                    response = get_ai_response(prompt, st.session_state.selected_model)
                    
                    # Display response
                    st.subheader("Grading Rubric")
                    st.markdown(response)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.info("Make sure Ollama is running on your computer with the selected model available.")

def render_discussion_questions():
    """Render the Discussion Questions interface."""
    st.subheader("Discussion Questions Generator")
    
    st.markdown("""
    Generate thought-provoking discussion questions for any topic or reading.
    """)
    
    # Question type
    question_type = st.selectbox(
        "Question type",
        ["Reading Comprehension", "Critical Thinking", "Personal Connection", "Debate/Argument", "Mixed"]
    )
    
    # Topic or reading
    topic = st.text_input(
        "Topic or reading title",
        placeholder="Example: To Kill a Mockingbird, Climate Change, American Revolution"
    )
    
    # Additional context
    context = st.text_area(
        "Additional context (optional)",
        placeholder="Add any specific themes, chapters, or aspects you want to focus on."
    )
    
    # Number of questions
    num_questions = st.slider("Number of questions", 5, 20, 10)
    
    # Generate questions button
    if st.button("Generate Discussion Questions"):
        if not topic:
            st.warning("Please enter a topic or reading title.")
        else:
            with st.spinner("Creating discussion questions..."):
                # Prepare prompt with grade level adaptation
                grade_level = st.session_state.grade_level
                prompt = f"""
                Question Type: {question_type}
                Topic/Reading: {topic}
                Grade Level: {grade_level}
                Additional Context: {context}
                Number of Questions: {num_questions}
                
                Please generate {num_questions} {question_type} discussion questions about {topic} appropriate for students in {grade_level}.
                
                If additional context is provided, focus on those specific aspects.
                
                For each question:
                1. Make it clear and thought-provoking
                2. Appropriate for the grade level
                3. Designed to encourage meaningful discussion
                4. Include a brief teacher note with possible discussion points or answers
                
                Format each question with a number, the question text, and a separate teacher note.
                """
                
                try:
                    response = get_ai_response(prompt, st.session_state.selected_model)
                    
                    # Display response
                    st.subheader("Discussion Questions")
                    st.markdown(response)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.info("Make sure Ollama is running on your computer with the selected model available.")

def render_feedback_generator():
    """Render the Feedback Generator interface."""
    st.subheader("Feedback Generator")
    
    st.markdown("""
    Generate constructive feedback for student work.
    """)
    
    # Assignment type
    assignment_type = st.selectbox(
        "Assignment type",
        ["Essay", "Project", "Presentation", "Homework", "Test/Quiz", "Creative Work"]
    )
    
    # Subject
    subject = st.text_input(
        "Subject",
        placeholder="Example: Science, Math, English, History"
    )
    
    # Performance level
    performance = st.select_slider(
        "Overall performance level",
        options=["Needs Improvement", "Developing", "Proficient", "Excellent"]
    )
    
    # Specific strengths
    strengths = st.text_area(
        "Specific strengths (optional)",
        placeholder="List specific strengths of the student's work."
    )
    
    # Areas for improvement
    improvements = st.text_area(
        "Areas for improvement (optional)",
        placeholder="List specific areas where the student could improve."
    )
    
    # Generate feedback button
    if st.button("Generate Feedback"):
        if not assignment_type or not subject:
            st.warning("Please enter an assignment type and subject.")
        else:
            with st.spinner("Creating feedback..."):
                # Prepare prompt with grade level adaptation
                grade_level = st.session_state.grade_level
                prompt = f"""
                Assignment Type: {assignment_type}
                Subject: {subject}
                Grade Level: {grade_level}
                Performance Level: {performance}
                Specific Strengths: {strengths}
                Areas for Improvement: {improvements}
                
                Please generate constructive feedback for a student in {grade_level} who completed a {assignment_type} in {subject} at a {performance} level.
                
                Include the following in your feedback:
                1. Positive comments on strengths (including those specifically mentioned if any)
                2. Constructive criticism on areas for improvement (including those specifically mentioned if any)
                3. Specific suggestions for how to improve
                4. Encouraging closing remarks
                
                Make the feedback specific, constructive, and appropriate for the grade level.
                Use a supportive and encouraging tone throughout.
                """
                
                try:
                    response = get_ai_response(prompt, st.session_state.selected_model)
                    
                    # Display response
                    st.subheader("Student Feedback")
                    st.markdown(response)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.info("Make sure Ollama is running on your computer with the selected model available.")
