import streamlit as st
import uuid
import json
from chatbot import get_gym_instruction_response
from user_profiles import load_user_profiles, create_or_update_user_profile, get_user_profile
import openai

# Load user profiles from file
user_profiles = load_user_profiles()

# Session management
def start_session():
    """Initialize a new session ID."""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.chat_history = []

def log_chat(user_input, bot_response, image_url=None):
    """Log chat history for the current session."""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Extract text from response if it's a dictionary
    if isinstance(bot_response, dict) and 'text' in bot_response:
        response_text = bot_response['text']
        # Use image URL from response if available
        image_url = bot_response.get('image_url', image_url)
    else:
        response_text = bot_response
        
    st.session_state.chat_history.append({"user": user_input, "bot": response_text, "image": image_url})

def generate_image(prompt):
    """Generate image using DALL-E."""
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        return response['data'][0]['url']
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None

def app(environ, start_response):
    # Custom CSS for chat interface
    st.markdown("""
        <style>
        .user-message {
            background-color: #4A90E2;
            color: white;
            padding: 12px 18px;
            border-radius: 25px;
            margin: 8px 0;
            max-width: 75%;
            float: right;
            clear: both;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            font-family: 'Inter', sans-serif;
        }
        .bot-message {
            background-color: #2ECC71;
            color: white;
            padding: 12px 18px;
            border-radius: 25px;
            margin: 8px 0;
            max-width: 75%;
            float: left;
            clear: both;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            font-family: 'Inter', sans-serif;
        }
        .chat-container {
            padding: 25px;
            border-radius: 15px;
            background-color: #1E1E1E;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            margin: 15px 0;
            border: 1px solid #333;
        }
        .message-input {
            border-radius: 25px;
            border: 2px solid #4A90E2;
            padding: 12px;
            background-color: #2D2D2D;
            color: white;
            transition: all 0.3s ease;
        }
        .message-input:focus {
            border-color: #2ECC71;
            box-shadow: 0 0 10px rgba(46, 204, 113, 0.2);
        }
        .stButton>button {
            border-radius: 25px;
            background-color: #4A90E2;
            color: white;
            border: none;
            padding: 10px 25px;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #357ABD;
            transform: translateY(-2px);
        }
        .profile-section {
            background-color: #2D2D2D;
            padding: 20px;
            border-radius: 15px;
            margin: 15px 0;
            border: 1px solid #333;
        }
        .stTextInput>div>div>input {
            border-radius: 10px;
            background-color: #2D2D2D;
            color: white;
            border: 1px solid #4A90E2;
        }
        .stSelectbox>div>div>div {
            border-radius: 10px;
            background-color: #2D2D2D;
            color: white;
        }
        .chat-image {
            margin: 8px 0;
            clear: both;
            max-width: 75%;
            float: left;
        }
        </style>
        """, unsafe_allow_html=True)

    # Streamlit app layout
    st.title("🏋️‍♂️ Gym Instruction Chatbot")

    # Initialize session
    start_session()

    # Profile creation form
    with st.expander("💪 Create or Update Profile"):
        st.markdown('<div class="profile-section">', unsafe_allow_html=True)
        user_id = st.text_input("🆔 User ID")
        goal = st.text_input("🎯 Goal (e.g., Muscle Gain, Fat Loss)")
        age = st.number_input("📅 Age", min_value=10, max_value=100, step=1)
        gender = st.selectbox("⚧ Gender", ["Male", "Female", "Other"])
        height = st.number_input("📏 Height (cm)", min_value=100, max_value=250, step=1)
        weight = st.number_input("⚖️ Weight (kg)", min_value=30, max_value=200, step=1)
        body_type = st.selectbox("🧬 Body Type", ["Ectomorph", "Mesomorph", "Endomorph"])
        activity_level = st.selectbox("📊 Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])
        fitness_preferences = st.text_area("🎨 Fitness Preferences (e.g., Cardio, Strength Training)")

        if st.button("Save Profile ✅"):
            create_or_update_user_profile(
                user_id=user_id,
                goal=goal,
                age=age,
                gender=gender,
                height=height,
                weight=weight,
                body_type=body_type,
                activity_level=activity_level,
                fitness_preferences=fitness_preferences,
                user_profiles=user_profiles
            )
            st.session_state.user_id = user_id
            st.success("✨ Profile created successfully!")
        st.markdown('</div>', unsafe_allow_html=True)

    # Check if user profile is set up
    if "user_id" in st.session_state:
        user_profile = get_user_profile(st.session_state.user_id, user_profiles)
        if user_profile:
            st.write(f"👤 **Profile for User ID**: {st.session_state.user_id}")
        else:
            st.warning("⚠️ User profile not found, please create one above.")
    else:
        st.warning("⚠️ Please create a profile first.")

    # Chat interface
    st.subheader("💬 Chat with the Gym Instruction Bot")

    # Display chat history
    if "chat_history" in st.session_state:
        chat_container = st.container()
        with chat_container:
            for chat in st.session_state.chat_history:
                st.markdown(f'<div class="user-message">{chat["user"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="bot-message">{chat["bot"]}</div>', unsafe_allow_html=True)
                if chat.get("image"):
                    st.markdown(f'<div class="chat-image"><img src="{chat["image"]}" style="max-width: 100%; border-radius: 10px;"></div>', unsafe_allow_html=True)

    # Input container at the bottom
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    input_container = st.container()
    with input_container:
        user_input = st.text_input("💭 Type your message...", key="user_input", placeholder="Send a message...")
        generate_image_checkbox = st.checkbox("Generate image for this message")
        col1, col2 = st.columns([6,1])
        with col2:
            send_button = st.button("Send 📤")
        
        if send_button or (user_input and user_input != st.session_state.get('prev_input', '')):
            if "user_id" in st.session_state:
                user_profile = get_user_profile(st.session_state.user_id, user_profiles)
                if user_profile and user_input:
                    if generate_image_checkbox:
                        response = get_gym_instruction_response(user_input, user_profile)
                    else:
                        response = {'text': get_gym_instruction_response(user_input, user_profile)['text']}
                    log_chat(user_input, response)
                    st.session_state.prev_input = user_input
                    st.rerun()
                elif not user_profile:
                    st.warning("⚠️ Profile not found, please create a profile first.")
            else:
                st.warning("⚠️ Please create a profile first.")
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    app(None, None)