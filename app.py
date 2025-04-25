import streamlit as st
import tempfile
import os
import base64
import time
import google.generativeai as genai
from gtts import gTTS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Gemini API Configuration ---
# API key will be entered via sidebar

# Initialize Gemini model
model = genai.GenerativeModel('gemini-2.0-flash')

# --- Page Config ---
st.set_page_config(page_title="Holistic Fitness Hub", layout="wide")
st.title("🧘 Holistic Fitness Hub")

# --- Sidebar ---
st.sidebar.title("⚙️ Settings")
user_name = st.sidebar.text_input("Your Name", value="Fitness Enthusiast")
fitness_level = st.sidebar.select_slider("Fitness Level", options=["Beginner", "Intermediate", "Advanced"])
workout_duration = st.sidebar.slider("Workout Duration (minutes)", min_value=5, max_value=60, value=15, step=5)

# API Key input
st.sidebar.title("🔑 API Settings")
api_key = st.sidebar.text_input("Gemini API Key", type="password")
if api_key:
    genai.configure(api_key=api_key)

# --- Workout Categories ---
categories = {
    "Yoga": "Ancient practice focusing on strength, flexibility and breathing",
    "Breathing Exercises": "Techniques to improve lung capacity and reduce stress",
    "Balance Training": "Exercises that improve stability and coordination",
    "Japanese Practices": "Traditional Japanese movement arts and exercises",
    "Indian Ancient Practices": "Traditional Indian methods for physical and mental wellness",
    "Modern Abs Workout": "Contemporary exercises targeting core strength",
    "Body Part Focus": "Targeted exercises for specific body areas",
    "Meditation & Mindfulness": "Practices to improve mental clarity and presence"
}

# --- Utility: Generate workout with Gemini LLM ---
def generate_workout_with_llm(category, workout_type, level, duration_minutes):
    prompt = f"""
    Create a detailed {duration_minutes}-minute {workout_type} workout plan for a {level.lower()} level fitness enthusiast.
    The workout belongs to the {category} category: {categories[category]}
    
    Format the response as a JSON array with the following structure:
    [
        {{
            "name": "Exercise Name",
            "duration": duration_in_seconds (integer),
            "description": "Detailed exercise description"
        }},
        ...
    ]
    
    Include appropriate exercises for the {level.lower()} level, with proper durations that total approximately {duration_minutes} minutes.
    Include brief 15-second rests between exercises in your planning but don't include them in the JSON.
    Each exercise should have a duration between 30-120 seconds depending on difficulty.
    Provide clear, concise descriptions that explain proper form and execution.
    """
    
    try:
        response = model.generate_content(prompt)
        # Parse the response to extract the JSON workout plan
        # This is simplified and would need proper JSON parsing in a real app
        workout_text = response.text
        
        # Extract JSON part from the response (this is simplified)
        import json
        import re
        
        # Find content between square brackets with optional code block markers
        json_match = re.search(r'```json\s*(\[.*?\])\s*```|(\[.*?\])', workout_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1) if json_match.group(1) else json_match.group(2)
            workout_plan = json.loads(json_str)
            return workout_plan
        else:
            st.error("Could not parse the workout plan from the LLM response")
            return None
            
    except Exception as e:
        logger.error(f"Error generating workout with LLM: {str(e)}")
        st.error(f"Error generating workout: {str(e)}")
        return None

# --- Utility: Text to Audio ---
def text_to_audio(text, filename="workout_audio.mp3"):
    try:
        # Limit text length for TTS
        text_for_tts = text[:3000]  # Limit to prevent issues with very long texts
        tts = gTTS(text=text_for_tts, lang='en')
        tts.save(filename)
        return filename
    except Exception as e:
        logger.error(f"Error in text_to_audio: {str(e)}")
        st.error(f"Error generating audio: {str(e)}")
        return None

# --- Utility: Get Audio Button ---
def get_audio_button(text, button_text="Listen to Instructions"):
    audio_file = text_to_audio(text)
    if audio_file:
        with open(audio_file, "rb") as f:
            audio_bytes = f.read()
        st.audio(audio_bytes, format="audio/mp3")
        st.download_button(
            label="Download Audio",
            data=audio_bytes,
            file_name="workout_instructions.mp3",
            mime="audio/mp3"
        )

# --- Main App UI ---
st.subheader(f"Welcome, {user_name}!")

# Category Selection
st.subheader("Step 1: Choose Workout Category")
workout_category = st.selectbox("Select Category", list(categories.keys()))

# Display category info
st.write(categories[workout_category])

# Type Selection
st.subheader("Step 2: Specify Workout Type")
if workout_category == "Yoga":
    workout_types = ["Hatha Yoga", "Vinyasa Flow", "Yin Yoga", "Power Yoga", "Restorative Yoga"]
elif workout_category == "Breathing Exercises":
    workout_types = ["Box Breathing", "Diaphragmatic Breathing", "Alternate Nostril Breathing", "4-7-8 Technique", "Wim Hof Method"]
elif workout_category == "Body Part Focus":
    workout_types = ["Upper Body", "Lower Body", "Back Strength", "Shoulder Mobility", "Hip Flexibility"]
else:
    workout_types = [f"{workout_category} Flow", f"Dynamic {workout_category}", f"Gentle {workout_category}", 
                    f"Intensive {workout_category}", f"Traditional {workout_category}"]

workout_type = st.selectbox("Select Type", workout_types)

# Generate Button
if st.button("Generate Workout Plan"):
    if not api_key:
        st.error("Please enter your Gemini API key in the sidebar")
    else:
        with st.spinner("Creating your personalized workout with AI..."):
            # Generate workout using LLM
            workout_plan = generate_workout_with_llm(workout_category, workout_type, fitness_level, workout_duration)
            
            if workout_plan:
                st.success("Your AI-generated workout plan is ready!")
                
                # Display workout plan
                st.subheader("Your Personalized Workout Plan")
                
                # Tabs for different views
                tab1, tab2, tab3 = st.tabs(["Exercise List", "Guided Workout", "Audio Instructions"])
                
                with tab1:
                    for i, exercise in enumerate(workout_plan, 1):
                        with st.expander(f"{i}. {exercise['name']} ({exercise['duration']} seconds)"):
                            st.write(exercise["description"])
                
                with tab2:
                    st.write("Follow along with the timer:")
                    
                    # Create workout instructions
                    workout_instructions = f"Welcome to your {workout_duration} minute {workout_type} workout. "
                    workout_instructions += f"This {fitness_level.lower()} level workout includes {len(workout_plan)} exercises. Let's begin!\n\n"
                    
                    for i, exercise in enumerate(workout_plan, 1):
                        workout_instructions += f"Exercise {i}: {exercise['name']} for {exercise['duration']} seconds. {exercise['description']}.\n"
                        if i < len(workout_plan):
                            workout_instructions += "Then rest for 15 seconds.\n\n"
                    
                    workout_instructions += f"\nCongratulations on completing your {workout_type} workout!"
                    
                    st.write(workout_instructions)
                    
                    # Interactive timer option
                    if st.button("Start Guided Workout"):
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        total_duration = sum(ex["duration"] for ex in workout_plan) + (len(workout_plan) - 1) * 15
                        time_elapsed = 0
                        
                        current_exercise = 0
                        in_rest = False
                        rest_time = 0
                        
                        # This would normally be a loop with actual timing
                        # For this example, we'll just update the progress bar quickly
                        while current_exercise < len(workout_plan):
                            if not in_rest:
                                # Exercise period
                                exercise = workout_plan[current_exercise]
                                status_text.write(f"Now: {exercise['name']} - {exercise['description']}")
                                
                                # Simulate exercise time passing
                                for _ in range(exercise["duration"]):
                                    time.sleep(0.01)  # Speed up for demo
                                    time_elapsed += 1
                                    progress_bar.progress(time_elapsed / total_duration)
                                
                                if current_exercise < len(workout_plan) - 1:
                                    in_rest = True
                                else:
                                    current_exercise += 1
                            else:
                                # Rest period
                                status_text.write("REST")
                                
                                # Simulate rest time passing
                                for _ in range(15):
                                    time.sleep(0.01)  # Speed up for demo
                                    time_elapsed += 1
                                    progress_bar.progress(time_elapsed / total_duration)
                                
                                in_rest = False
                                current_exercise += 1
                        
                        status_text.write("Workout complete! Great job!")
                        progress_bar.progress(1.0)
                
                with tab3:
                    st.write("Audio Instructions for your workout:")
                    get_audio_button(workout_instructions)
            else:
                st.error("Couldn't generate workout plan. Please try different options or check your API key.")

# --- Additional Features ---
st.subheader("Additional Tools")

# BMI Calculator
with st.expander("BMI Calculator"):
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.1)
    with col2:
        height = st.number_input("Height (cm)", min_value=120.0, max_value=220.0, value=170.0, step=0.1)
    
    if st.button("Calculate BMI"):
        bmi = weight / ((height/100) ** 2)
        st.write(f"Your BMI: {bmi:.1f}")
        
        # BMI category
        if bmi < 18.5:
            st.write("Category: Underweight")
        elif bmi < 25:
            st.write("Category: Normal weight")
        elif bmi < 30:
            st.write("Category: Overweight")
        else:
            st.write("Category: Obesity")

# AI Fitness Advisor
with st.expander("AI Fitness Advisor"):
    st.write("Ask any fitness or wellness question:")
    user_question = st.text_input("Your Question")
    
    if st.button("Get AI Advice") and user_question:
        if not api_key:
            st.error("Please enter your Gemini API key in the sidebar")
        else:
            with st.spinner("Generating advice..."):
                try:
                    fitness_prompt = f"As a fitness expert, please answer this question: {user_question}"
                    advice_response = model.generate_content(fitness_prompt)
                    st.write(advice_response.text)
                except Exception as e:
                    st.error(f"Error generating advice: {str(e)}")

# Progress Tracker
with st.expander("Progress Tracker"):
    st.write("Track your fitness journey:")
    workout_date = st.date_input("Workout Date")
    workout_completed = st.selectbox("Workout Completed", ["Yes", "Partially", "No"])
    energy_level = st.slider("Energy Level", 1, 10, 5)
    notes = st.text_area("Notes")
    
    if st.button("Save Progress"):
        st.success("Progress saved! (Note: In a real app, this would save to a database)")

# --- Footer ---
st.markdown("---")
st.markdown("Holistic Fitness Hub - Your AI-powered wellness companion")
