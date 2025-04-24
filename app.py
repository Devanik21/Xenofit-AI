import streamlit as st
import tempfile
import os
import base64
import time
import random
from gtts import gTTS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Page Config ---
st.set_page_config(page_title="Holistic Fitness Hub", layout="wide")
st.title("🧘 Holistic Fitness Hub")

# --- Sidebar ---
st.sidebar.title("⚙️ Settings")
user_name = st.sidebar.text_input("Your Name", value="Fitness Enthusiast")
fitness_level = st.sidebar.select_slider("Fitness Level", options=["Beginner", "Intermediate", "Advanced"])
workout_duration = st.sidebar.slider("Workout Duration (minutes)", min_value=5, max_value=60, value=15, step=5)

# --- Workout Categories ---
categories = {
    "Yoga": {
        "description": "Ancient practice focusing on strength, flexibility and breathing",
        "types": ["Hatha Yoga", "Vinyasa Flow", "Yin Yoga", "Power Yoga", "Restorative Yoga"]
    },
    "Breathing Exercises": {
        "description": "Techniques to improve lung capacity and reduce stress",
        "types": ["Box Breathing", "Diaphragmatic Breathing", "Alternate Nostril Breathing", "4-7-8 Technique", "Wim Hof Method"]
    },
    "Balance Training": {
        "description": "Exercises that improve stability and coordination",
        "types": ["Single Leg Stands", "Bosu Ball Training", "Stability Exercises", "Functional Balance", "Dynamic Balance"]
    },
    "Japanese Practices": {
        "description": "Traditional Japanese movement arts and exercises",
        "types": ["Tai Chi", "Qigong", "Shiatsu Self-Massage", "Makko Ho Stretches", "Aikido Movements"]
    },
    "Indian Ancient Practices": {
        "description": "Traditional Indian methods for physical and mental wellness",
        "types": ["Surya Namaskar (Sun Salutation)", "Pranayama", "Chakra Meditation", "Ayurvedic Movement", "Mudras"]
    },
    "Modern Abs Workout": {
        "description": "Contemporary exercises targeting core strength",
        "types": ["HIIT Core", "Pilates Core", "Traditional Crunches", "Planks Variations", "Standing Abs"]
    },
    "Body Part Focus": {
        "description": "Targeted exercises for specific body areas",
        "types": ["Upper Body", "Lower Body", "Back Strength", "Shoulder Mobility", "Hip Flexibility"]
    },
    "Meditation & Mindfulness": {
        "description": "Practices to improve mental clarity and presence",
        "types": ["Body Scan", "Guided Visualization", "Mantra Meditation", "Walking Meditation", "Mindful Movement"]
    }
}

# --- Workout Database ---
workout_database = {
    "Hatha Yoga": {
        "beginner": [
            {"name": "Mountain Pose", "duration": 30, "description": "Stand tall with feet together, arms at sides, grounding through all four corners of feet"},
            {"name": "Child's Pose", "duration": 60, "description": "Kneel and sit back on heels, extend arms forward, rest forehead on mat"},
            {"name": "Cat-Cow Stretch", "duration": 60, "description": "On hands and knees, alternate between arching and rounding back"},
            {"name": "Downward Facing Dog", "duration": 45, "description": "Form an inverted V with body, hands and feet on floor, hips high"},
            {"name": "Seated Forward Bend", "duration": 45, "description": "Sit with legs extended, fold forward from hips reaching toward feet"}
        ],
        "intermediate": [
            {"name": "Tree Pose", "duration": 45, "description": "Balance on one foot, place other foot on inner thigh, hands in prayer or extended"},
            {"name": "Warrior I", "duration": 60, "description": "Lunge with back foot at 45°, arms extended overhead"},
            {"name": "Bridge Pose", "duration": 45, "description": "Lie on back, bend knees, lift hips, clasp hands under back"},
            {"name": "Extended Side Angle", "duration": 60, "description": "From warrior stance, lower one hand to floor inside foot, extend other arm overhead"},
            {"name": "Half Moon Pose", "duration": 45, "description": "Balance on one leg and hand, other leg extended, top arm reaching up"}
        ],
        "advanced": [
            {"name": "Crow Pose", "duration": 30, "description": "Balance on hands with knees resting on backs of upper arms"},
            {"name": "Headstand", "duration": 60, "description": "Invert body with weight on forearms and crown of head, legs extended upward"},
            {"name": "Side Plank with Leg Lift", "duration": 45, "description": "From side plank, extend top leg upward"},
            {"name": "Wheel Pose", "duration": 45, "description": "From back, press into backbend with hands and feet on floor"},
            {"name": "Bird of Paradise", "duration": 60, "description": "Standing bind with extended leg, balancing on one foot"}
        ]
    },
    "Box Breathing": {
        "beginner": [
            {"name": "Basic Box Breathing", "duration": 120, "description": "Inhale for 4 counts, hold for 4, exhale for 4, hold for 4"},
            {"name": "Seated Box Breathing", "duration": 120, "description": "Sit comfortably and practice box breathing with hand on belly"},
            {"name": "Beginner's Guided Box Breathing", "duration": 180, "description": "Follow guided instructions for proper breathing technique"},
            {"name": "Morning Box Breathing", "duration": 120, "description": "Practice upon waking to set intention for day"},
            {"name": "Pre-Sleep Box Breathing", "duration": 180, "description": "Practice before bed to calm nervous system"}
        ],
        "intermediate": [
            {"name": "Extended Box Breathing", "duration": 180, "description": "Inhale for 5 counts, hold for 5, exhale for 5, hold for 5"},
            {"name": "Box Breathing with Visualization", "duration": 180, "description": "Add mental imagery of a square while breathing"},
            {"name": "Walking Box Breathing", "duration": 180, "description": "Practice while walking, coordinating steps with breath counts"},
            {"name": "Box Breathing with Hand Mudras", "duration": 180, "description": "Add finger positions that change with each phase of breath"},
            {"name": "Nature-Connected Box Breathing", "duration": 180, "description": "Practice outdoors, connecting breath with natural elements"}
        ],
        "advanced": [
            {"name": "Extended Hold Box Breathing", "duration": 240, "description": "Inhale for 4, hold for 8, exhale for 4, hold for 8"},
            {"name": "Box Breathing in Challenging Pose", "duration": 180, "description": "Maintain breathing pattern while holding difficult yoga pose"},
            {"name": "Box Breathing with Alternating Nostril", "duration": 240, "description": "Combine box breathing with nostril alternation"},
            {"name": "Dynamic Box Breathing", "duration": 240, "description": "Vary the counts while maintaining the box pattern"},
            {"name": "Cold Exposure Box Breathing", "duration": 180, "description": "Practice during cold shower or ice bath"}
        ]
    },
    "Upper Body": {
        "beginner": [
            {"name": "Wall Push-Ups", "duration": 45, "description": "Push-ups performed against wall at an angle"},
            {"name": "Seated Shoulder Press", "duration": 45, "description": "Press arms overhead while seated"},
            {"name": "Bicep Curls with Household Items", "duration": 60, "description": "Use water bottles or cans as light weights"},
            {"name": "Tricep Dips on Chair", "duration": 45, "description": "Use sturdy chair to dip body weight"},
            {"name": "Standing Row with Resistance Band", "duration": 60, "description": "Pull band toward torso to work back muscles"}
        ],
        "intermediate": [
            {"name": "Push-Ups", "duration": 45, "description": "Standard push-ups from floor position"},
            {"name": "Plank to Push-Up", "duration": 60, "description": "Alternate between forearm plank and high plank"},
            {"name": "Dolphin Push-Ups", "duration": 45, "description": "Push-ups with forearms on ground, hips elevated"},
            {"name": "Archer Push-Ups", "duration": 60, "description": "Push-ups with alternating arm extension"},
            {"name": "Pike Push-Ups", "duration": 45, "description": "Push-ups with hips elevated in inverted V"}
        ],
        "advanced": [
            {"name": "One-Arm Push-Up Progression", "duration": 45, "description": "Work toward single-arm push-up"},
            {"name": "Handstand Push-Up Progression", "duration": 60, "description": "Vertical push-ups against wall"},
            {"name": "Planche Progression", "duration": 45, "description": "Leaning forward in push-up position"},
            {"name": "Pseudo Planche Push-Ups", "duration": 60, "description": "Push-ups with hands positioned by hips"},
            {"name": "Typewriter Push-Ups", "duration": 45, "description": "Push-ups with horizontal chest movement"}
        ]
    }
}

# Add more workout categories as needed, following the same structure

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

# --- Utility: Generate Workout Plan ---
def generate_workout_plan(workout_type, level, duration_minutes):
    if workout_type not in workout_database:
        return None
    
    available_exercises = workout_database[workout_type][level.lower()]
    
    # Calculate how many exercises we can fit
    total_seconds = duration_minutes * 60
    rest_time = 15  # seconds rest between exercises
    exercises = []
    current_time = 0
    
    while current_time < total_seconds:
        if not available_exercises:
            break
            
        exercise = random.choice(available_exercises)
        exercise_time = exercise["duration"]
        
        if current_time + exercise_time + rest_time <= total_seconds:
            exercises.append(exercise)
            current_time += exercise_time + rest_time
            # Reduce chance of repeating same exercise
            if len(available_exercises) > 1:
                available_exercises.remove(exercise)
        else:
            break
    
    return exercises

# --- Main App UI ---
st.subheader(f"Welcome, {user_name}!")

# Category Selection
st.subheader("Step 1: Choose Workout Category")
workout_category = st.selectbox("Select Category", list(categories.keys()))

# Display category info
st.write(categories[workout_category]["description"])

# Type Selection
st.subheader("Step 2: Select Workout Type")
workout_type = st.selectbox("Select Type", categories[workout_category]["types"])

# Generate Button
if st.button("Generate Workout Plan"):
    with st.spinner("Creating your personalized workout..."):
        # Simulate processing time
        time.sleep(1)
        
        # Check if workout type exists in database
        if workout_type in workout_database:
            workout_plan = generate_workout_plan(workout_type, fitness_level, workout_duration)
            
            if workout_plan:
                st.success("Your workout plan is ready!")
                
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
                st.error("Couldn't generate workout plan. Please try different options.")
        else:
            st.warning(f"Workout type '{workout_type}' not found in database. More content coming soon!")

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
st.markdown("Holistic Fitness Hub - Your all-in-one wellness companion")
