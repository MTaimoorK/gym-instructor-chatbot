import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def get_gym_instruction_response(user_message, user_profile):
    """
    Generates a response and image using OpenAI GPT-3 based on the user's profile and message.
    """
    conversation = [
        {"role": "system", "content": "You are a fitness expert with vast knowledge of gym workouts, nutrition, and health advice. Respond to the user's queries in a personalized and detailed manner, keeping in mind their fitness goals, age, and gender."},
        {"role": "user", "content": f"User goal: {user_profile.get('goal', 'General fitness')}\nUser age: {user_profile.get('age', 'Not specified')}\nUser gender: {user_profile.get('gender', 'Not specified')}\nUser query: {user_message}"}
    ]
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversation,
        max_tokens=1000,
        temperature=0.7
    )
    
    # Generate a relevant gym-related image
    image_response = openai.images.generate(
        prompt=f"Gym fitness image related to: {user_message}",
        n=1,
        size="1024x1024",
        model="dall-e-3"
    )
    
    return {
        'text': response.choices[0].message.content.strip(),
        'image_url': image_response.data[0].url
    }