import json

# File to store user profiles
PROFILE_FILE = 'user_profiles.json'

def create_or_update_user_profile(user_id, goal, age, gender, height, weight, body_type, activity_level, fitness_preferences, user_profiles):
    # Update or create the user profile
    user_profiles[user_id] = {
        "goal": goal,
        "age": age,
        "gender": gender,
        "height": height,
        "weight": weight,
        "body_type": body_type,
        "activity_level": activity_level,
        "fitness_preferences": fitness_preferences
    }
    save_user_profiles(user_profiles)

def save_user_profiles(user_profiles):
    with open('user_profiles.json', 'w') as f:
        json.dump(user_profiles, f)

def load_user_profiles():
    try:
        with open('user_profiles.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def get_user_profile(user_id, user_profiles):
    """Retrieve the user profile for a given user_id."""
    return user_profiles.get(user_id, None)
