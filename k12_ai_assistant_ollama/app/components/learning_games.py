import streamlit as st
from utils.ollama_utils import get_ai_response
import random

def render_learning_games():
    """Render the Learning Games tool interface."""
    st.header("Learning Games")
    
    st.markdown("""
    Have fun while learning with these educational games and activities!
    Choose a game type from the options below.
    """)
    
    # Game selection
    game_type = st.selectbox(
        "Select a game or activity",
        ["Quiz Game", "Word Scramble", "Math Challenge", "Fact or Fiction", "Story Builder"]
    )
    
    if game_type == "Quiz Game":
        render_quiz_game()
    elif game_type == "Word Scramble":
        render_word_scramble()
    elif game_type == "Math Challenge":
        render_math_challenge()
    elif game_type == "Fact or Fiction":
        render_fact_or_fiction()
    elif game_type == "Story Builder":
        render_story_builder()

def render_quiz_game():
    """Render the Quiz Game interface."""
    st.subheader("Quiz Game")
    
    st.markdown("""
    Test your knowledge with a custom quiz on any subject!
    """)
    
    # Topic selection
    topic = st.text_input(
        "Enter a topic for your quiz",
        placeholder="Example: Solar System, American History, Fractions"
    )
    
    # Number of questions
    num_questions = st.slider("Number of questions", 3, 10, 5)
    
    # Difficulty level
    difficulty = st.select_slider(
        "Difficulty level",
        options=["Easy", "Medium", "Hard"]
    )
    
    # Quiz format
    quiz_format = st.radio(
        "Quiz format",
        ["Multiple Choice", "True/False", "Mixed"]
    )
    
    # Generate quiz button
    if st.button("Generate Quiz"):
        if not topic:
            st.warning("Please enter a topic for your quiz.")
        else:
            with st.spinner("Creating your quiz..."):
                # Prepare prompt with grade level adaptation
                grade_level = st.session_state.grade_level
                prompt = f"""
                Topic: {topic}
                Grade Level: {grade_level}
                Number of Questions: {num_questions}
                Difficulty: {difficulty}
                Format: {quiz_format}
                
                Please create an educational quiz on the topic "{topic}" appropriate for a student in {grade_level}.
                Generate {num_questions} questions at {difficulty} difficulty level.
                Use {quiz_format} format for the questions.
                
                For each question:
                1. Provide the question
                2. For multiple choice, provide 4 options with one correct answer
                3. For true/false, clearly state if the statement is true or false
                4. Include the correct answer
                5. Provide a brief explanation for the correct answer
                
                Format each question as:
                
                Q1: [Question text]
                Options:
                A. [Option A]
                B. [Option B]
                C. [Option C]
                D. [Option D]
                Correct Answer: [Letter]
                Explanation: [Brief explanation]
                
                For true/false questions, use:
                
                Q1: [Statement]
                Options:
                A. True
                B. False
                Correct Answer: [Letter]
                Explanation: [Brief explanation]
                """
                
                try:
                    response = get_ai_response(prompt, st.session_state.selected_model)
                    
                    # Store the quiz in session state
                    if "quiz_questions" not in st.session_state:
                        st.session_state.quiz_questions = response
                        st.session_state.quiz_answers_revealed = False
                    else:
                        st.session_state.quiz_questions = response
                        st.session_state.quiz_answers_revealed = False
                    
                    # Display the quiz
                    #display_quiz()
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.info("Make sure Ollama is running on your computer with the selected model available.")
    
    # Display quiz if it exists in session state
    if "quiz_questions" in st.session_state:
        display_quiz()

def display_quiz():
    """Display the quiz questions and handle answers."""
    st.subheader("Your Quiz")
    
    # Split the quiz into questions
    quiz_text = st.session_state.quiz_questions
    
    # Display the quiz
    st.markdown(quiz_text)

    # Show/hide answers button
    #if st.button("Show Answers" if not st.session_state.quiz_answers_revealed else "Hide Answers", key="toggle_answers_button"):

    import random

    if st.button("Show Answers" if not st.session_state.quiz_answers_revealed else "Hide Answers" , key=f"toggle_answers_button_{random.randint(1, 10000)}"):
        st.session_state.quiz_answers_revealed = not st.session_state.quiz_answers_revealed
    
    # Display answers if revealed
    if st.session_state.quiz_answers_revealed:
        st.subheader("Answers")
        
        # Extract answers from the quiz text
        lines = quiz_text.split('\n')
        answers = []
        for i, line in enumerate(lines):
            if line.startswith("Correct Answer:"):
                answers.append(line)
                # Also add the explanation if available
                if i+1 < len(lines) and lines[i+1].startswith("Explanation:"):
                    answers.append(lines[i+1])
                answers.append("")  # Add a blank line between answers
        
        st.markdown("\n".join(answers))

def render_word_scramble():
    """Render the Word Scramble interface."""
    st.subheader("Word Scramble")
    
    st.markdown("""
    Unscramble words related to a specific topic or subject!
    """)
    
    # Topic selection
    topic = st.text_input(
        "Enter a topic for word scramble",
        placeholder="Example: Animals, Space, Sports"
    )
    
    # Number of words
    num_words = st.slider("Number of words", 5, 15, 8)
    
    # Generate word scramble button
    if st.button("Generate Word Scramble"):
        if not topic:
            st.warning("Please enter a topic for your word scramble.")
        else:
            with st.spinner("Creating word scramble..."):
                # Prepare prompt with grade level adaptation
                grade_level = st.session_state.grade_level
                prompt = f"""
                Topic: {topic}
                Grade Level: {grade_level}
                Number of Words: {num_words}
                
                Please create a word scramble game with {num_words} words related to the topic "{topic}" appropriate for a student in {grade_level}.
                
                For each word:
                1. Provide the scrambled letters (randomly rearranged)
                2. Provide a hint or clue about the word
                3. Include the original unscrambled word (as the answer)
                
                Format each word as:
                
                Word 1:
                Scrambled: [scrambled letters]
                Hint: [hint or clue]
                Answer: [original word]
                
                Make sure the words are appropriate for the grade level and related to the topic.
                """
                
                try:
                    response = get_ai_response(prompt, st.session_state.selected_model)
                    
                    # Store the word scramble in session state
                    if "word_scramble" not in st.session_state:
                        st.session_state.word_scramble = response
                        st.session_state.scramble_answers_revealed = False
                    else:
                        st.session_state.word_scramble = response
                        st.session_state.scramble_answers_revealed = False
                    
                    # Display the word scramble
                    display_word_scramble()
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.info("Make sure Ollama is running on your computer with the selected model available.")
    
    # Display word scramble if it exists in session state
    if "word_scramble" in st.session_state:
        display_word_scramble()

def display_word_scramble():
    """Display the word scramble and handle answers."""
    st.subheader("Word Scramble")
    
    # Get the word scramble text
    scramble_text = st.session_state.word_scramble
    
    # Process the text to hide answers
    if not st.session_state.scramble_answers_revealed:
        lines = scramble_text.split('\n')
        filtered_lines = []
        for line in lines:
            if not line.startswith("Answer:"):
                filtered_lines.append(line)
        scramble_text = '\n'.join(filtered_lines)
    
    # Display the word scramble
    st.markdown(scramble_text)
    
    # Show/hide answers button
    if st.button("Show Answers" if not st.session_state.scramble_answers_revealed else "Hide Answers"):
        st.session_state.scramble_answers_revealed = not st.session_state.scramble_answers_revealed

def render_math_challenge():
    """Render the Math Challenge interface."""
    st.subheader("Math Challenge")
    
    st.markdown("""
    Practice your math skills with custom math challenges!
    """)
    
    # Math topic selection
    math_topic = st.selectbox(
        "Select a math topic",
        ["Addition", "Subtraction", "Multiplication", "Division", "Fractions", "Decimals", 
         "Percentages", "Algebra", "Geometry", "Mixed"]
    )
    
    # Difficulty level
    difficulty = st.select_slider(
        "Difficulty level",
        options=["Easy", "Medium", "Hard"]
    )
    
    # Number of problems
    num_problems = st.slider("Number of problems", 5, 20, 10)
    
    # Generate math challenge button
    if st.button("Generate Math Challenge"):
        with st.spinner("Creating math challenge..."):
            # Prepare prompt with grade level adaptation
            grade_level = st.session_state.grade_level
            prompt = f"""
            Math Topic: {math_topic}
            Grade Level: {grade_level}
            Difficulty: {difficulty}
            Number of Problems: {num_problems}
            
            Please create a math challenge with {num_problems} {math_topic} problems appropriate for a student in {grade_level} at {difficulty} difficulty level.
            
            For each problem:
            1. Provide the problem statement or equation
            2. Include the correct answer
            3. For more complex problems, include a step-by-step solution
            
            Format each problem as:
            
            Problem 1:
            [Problem statement or equation]
            Answer: [correct answer]
            Solution: [step-by-step solution if needed]
            
            Make sure the problems are appropriate for the grade level and difficulty.
            """
            
            try:
                response = get_ai_response(prompt, st.session_state.selected_model)
                
                # Store the math challenge in session state
                if "math_challenge" not in st.session_state:
                    st.session_state.math_challenge = response
                    st.session_state.math_answers_revealed = False
                else:
                    st.session_state.math_challenge = response
                    st.session_state.math_answers_revealed = False
                
                # Display the math challenge
                display_math_challenge()
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Make sure Ollama is running on your computer with the selected model available.")
    
    # Display math challenge if it exists in session state
    if "math_challenge" in st.session_state:
        display_math_challenge()

def display_math_challenge():
    """Display the math challenge and handle answers."""
    st.subheader("Math Challenge")
    
    # Get the math challenge text
    challenge_text = st.session_state.math_challenge
    
    # Process the text to hide answers and solutions
    if not st.session_state.math_answers_revealed:
        lines = challenge_text.split('\n')
        filtered_lines = []
        skip_line = False
        for line in lines:
            if line.startswith("Answer:") or line.startswith("Solution:"):
                skip_line = True
            elif line.strip() == "" or line.startswith("Problem"):
                skip_line = False
                filtered_lines.append(line)
            elif not skip_line:
                filtered_lines.append(line)
        challenge_text = '\n'.join(filtered_lines)
    
    # Display the math challenge
    st.markdown(challenge_text)
    
    # Show/hide answers button
    if st.button("Show Answers" if not st.session_state.math_answers_revealed else "Hide Answers"):
        st.session_state.math_answers_revealed = not st.session_state.math_answers_revealed

def render_fact_or_fiction():
    """Render the Fact or Fiction interface."""
    st.subheader("Fact or Fiction")
    
    st.markdown("""
    Can you tell what's true and what's false? Test your knowledge with these statements!
    """)
    
    # Topic selection
    topic = st.text_input(
        "Enter a topic for fact or fiction",
        placeholder="Example: Ocean Animals, Ancient Civilizations, Human Body"
    )
    
    # Number of statements
    num_statements = st.slider("Number of statements", 5, 15, 10)
    
    # Generate fact or fiction button
    if st.button("Generate Fact or Fiction"):
        if not topic:
            st.warning("Please enter a topic for your fact or fiction game.")
        else:
            with st.spinner("Creating fact or fiction game..."):
                # Prepare prompt with grade level adaptation
                grade_level = st.session_state.grade_level
                prompt = f"""
                Topic: {topic}
                Grade Level: {grade_level}
                Number of Statements: {num_statements}
                
                Please create a "Fact or Fiction" game with {num_statements} statements about the topic "{topic}" appropriate for a student in {grade_level}.
                
                Create a mix of true statements (facts) and false statements (fiction).
                
                For each statement:
                1. Provide the statement
                2. Indicate whether it is a FACT (true) or FICTION (false)
                3. For facts, provide a brief additional interesting detail
                4. For fiction, explain why it's false and provide the correct information
                
                Format each statement as:
                
                Statement 1:
                [Statement text]
                Answer: FACT or FICTION
                Explanation: [Explanation text]
                
                Make sure the statements are appropriate for the grade level and related to the topic.
                """
                
                try:
                    response = get_ai_response(prompt, st.session_state.selected_model)
                    
                    # Store the fact or fiction in session state
                    if "fact_or_fiction" not in st.session_state:
                        st.session_state.fact_or_fiction = response
                        st.session_state.fact_fiction_answers_revealed = False
                    else:
                        st.session_state.fact_or_fiction = response
                        st.session_state.fact_fiction_answers_revealed = False
                    
                    # Display the fact or fiction
                    display_fact_or_fiction()
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.info("Make sure Ollama is running on your computer with the selected model available.")
    
    # Display fact or fiction if it exists in session state
    if "fact_or_fiction" in st.session_state:
        display_fact_or_fiction()

def display_fact_or_fiction():
    """Display the fact or fiction game and handle answers."""
    st.subheader("Fact or Fiction")
    
    # Get the fact or fiction text
    fact_fiction_text = st.session_state.fact_or_fiction
    
    # Process the text to hide answers and explanations
    if not st.session_state.fact_fiction_answers_revealed:
        lines = fact_fiction_text.split('\n')
        filtered_lines = []
        skip_line = False
        for line in lines:
            if line.startswith("Answer:") or line.startswith("Explanation:"):
                skip_line = True
            elif line.strip() == "" or line.startswith("Statement"):
                skip_line = False
                filtered_lines.append(line)
            elif not skip_line:
                filtered_lines.append(line)
        fact_fiction_text = '\n'.join(filtered_lines)
    
    # Display the fact or fiction
    st.markdown(fact_fiction_text)
    
    # Show/hide answers button
    if st.button("Show Answers" if not st.session_state.fact_fiction_answers_revealed else "Hide Answers"):
        st.session_state.fact_fiction_answers_revealed = not st.session_state.fact_fiction_answers_revealed

def render_story_builder():
    """Render the Story Builder interface."""
    st.subheader("Story Builder")
    
    st.markdown("""
    Create your own story with AI assistance! Choose a theme and characters, and the AI will help you build a story.
    """)
    
    # Story theme
    theme = st.text_input(
        "Story theme or setting",
        placeholder="Example: Space adventure, Enchanted forest, Underwater kingdom"
    )
    
    # Main character
    main_character = st.text_input(
        "Main character",
        placeholder="Example: A brave astronaut, A curious wizard, A friendly dolphin"
    )
    
    # Story elements
    col1, col2 = st.columns(2)
    with col1:
        include_challenge = st.checkbox("Include a challenge or problem", value=True)
        include_helper = st.checkbox("Include a helper character", value=True)
    with col2:
        include_magic = st.checkbox("Include magical elements", value=False)
        include_lesson = st.checkbox("Include a moral or lesson", value=True)
    
    # Story length
    story_length = st.select_slider(
        "Story length",
        options=["Short", "Medium", "Long"]
    )
    
    # Generate story button
    if st.button("Generate Story"):
        if not theme or not main_character:
            st.warning("Please enter a theme and main character for your story.")
        else:
            with st.spinner("Creating your story..."):
                # Prepare prompt with grade level adaptation
                grade_level = st.session_state.grade_level
                
                # Build elements list
                elements = []
                if include_challenge:
                    elements.append("a challenge or problem to overcome")
                if include_helper:
                    elements.append("a helper character")
                if include_magic:
                    elements.append("magical elements or powers")
                if include_lesson:
                    elements.append("a moral or lesson")
                
                elements_str = ", ".join(elements)
                
                prompt = f"""
                Theme/Setting: {theme}
                Main Character: {main_character}
                Grade Level: {grade_level}
                Story Length: {story_length}
                Elements to Include: {elements_str}
                
                Please create an engaging {story_length.lower()} story appropriate for a student in {grade_level}.
                The story should be set in {theme} and feature {main_character} as the main character.
                Include the following elements: {elements_str}.
                
                Structure the story with a clear beginning, middle, and end.
                Use language, vocabulary, and complexity appropriate for the student's grade level.
                Make the story engaging, creative, and educational where possible.
                
                Format the story with a title and paragraphs.
                """
                
                try:
                    response = get_ai_response(prompt, st.session_state.selected_model)
                    
                    # Display the story
                    st.subheader("Your Story")
                    st.markdown(response)
                    
                    # Story extension options
                    st.markdown("---")
                    st.subheader("Story Extensions")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Create a sequel"):
                            sequel_prompt = f"""
                            Based on the following story, please create a sequel that continues the adventure.
                            Keep the same characters and setting, but introduce new challenges or situations.
                            Make the sequel appropriate for a student in {grade_level}.
                            
                            Original Story:
                            {response}
                            """
                            sequel_response = get_ai_response(sequel_prompt, st.session_state.selected_model)
                            st.subheader("Sequel")
                            st.markdown(sequel_response)
                    
                    with col2:
                        if st.button("Create discussion questions"):
                            questions_prompt = f"""
                            Based on the following story, please create 5-7 discussion questions that would be appropriate for a student in {grade_level}.
                            Include questions about the characters, plot, themes, and any lessons or morals.
                            Also include questions that encourage critical thinking and personal connections.
                            
                            Story:
                            {response}
                            """
                            questions_response = get_ai_response(questions_prompt, st.session_state.selected_model)
                            st.subheader("Discussion Questions")
                            st.markdown(questions_response)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.info("Make sure Ollama is running on your computer with the selected model available.")
