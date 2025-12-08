import streamlit as st
from utils.ollama_utils import get_gpu_usage, format_gpu_memory

def render_sidebar():
    """Render the sidebar with tool selection and model selection."""
    with st.sidebar:
        # Tool selection
        st.subheader("Select Tool")
        tool_options = [
            "Homework Helper",
            "Writing Assistant",
            "Research Assistant",
            "Learning Games",
            "Teacher Tools"
        ]
        
        selected_tool = st.radio("Tool Selection", tool_options, index=tool_options.index(st.session_state.current_tool), label_visibility="collapsed")
        
        if selected_tool != st.session_state.current_tool:
            st.session_state.current_tool = selected_tool
            # Reset any tool-specific session state here if needed
        
        # Model selection
        st.subheader("AI Model Settings")
        model_options = {
            "llama3:latest": "Llama3 latest",
            "gpt-oss:120b": "GPT-OSS 120B (Largest, ~62GB VRAM) 🚀"
        }
        
        # Ensure default model is in the list, otherwise use first available
        available_models = list(model_options.keys())
        if st.session_state.selected_model not in available_models:
            st.session_state.selected_model = available_models[0]
        
        selected_model = st.selectbox(
            "Select AI Model",
            options=available_models,
            format_func=lambda x: model_options[x],
            index=available_models.index(st.session_state.selected_model)
        )
        
        if selected_model != st.session_state.selected_model:
            st.session_state.selected_model = selected_model
        
        # Grade level selection for content adaptation
        st.subheader("Grade Level")
        grade_options = [
            "K-2 (Elementary)",
            "3-5 (Elementary)",
            "6-8 (Middle School)",
            "9-12 (High School)"
        ]
        
        if "grade_level" not in st.session_state:
            st.session_state.grade_level = grade_options[1]  # Default to grades 3-5
            
        selected_grade = st.radio("Grade Level", grade_options, index=grade_options.index(st.session_state.grade_level), label_visibility="collapsed")
        
        if selected_grade != st.session_state.grade_level:
            st.session_state.grade_level = selected_grade
        
        # GPU Usage section
        st.markdown("---")
        st.subheader("GPU Status")
        gpu_info = get_gpu_usage()
        if gpu_info:
            for gpu in gpu_info:
                st.text(f"GPU {gpu['index']}: {gpu['name']}")
                
                # Display memory if available
                if gpu['memory_used_mb'] is not None:
                    memory_used = format_gpu_memory(gpu['memory_used_mb'])
                    if gpu['memory_total_mb'] is not None:
                        memory_total = format_gpu_memory(gpu['memory_total_mb'])
                        memory_percent = (gpu['memory_used_mb'] / gpu['memory_total_mb']) * 100
                        st.progress(memory_percent / 100, text=f"Memory: {memory_used} / {memory_total} ({memory_percent:.1f}%)")
                    else:
                        # For unified memory systems (GB10), show total used
                        st.caption(f"Memory Used: {memory_used}")
                        if gpu.get('ollama_memory_mb'):
                            ollama_mem = format_gpu_memory(gpu['ollama_memory_mb'])
                            st.caption(f"Ollama: {ollama_mem}")
                else:
                    st.caption("Memory: N/A")
                
                # Display utilization and temperature
                util_text = f"{gpu['utilization_percent']}%" if gpu['utilization_percent'] is not None else "N/A"
                temp_text = f"{gpu['temperature_c']}°C" if gpu['temperature_c'] is not None else "N/A"
                st.caption(f"Utilization: {util_text} | Temp: {temp_text}")
        else:
            st.info("GPU monitoring unavailable")
        
        # About section
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This application uses local AI models through Ollama to provide educational assistance for K-12 students and teachers.
        
        All processing happens on this computer - no data is sent to external servers.
        """)
