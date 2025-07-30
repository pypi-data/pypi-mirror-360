import json
import os
import tempfile
from .utils import get_user_data_dir

def get_preferences_file_path():
    """Returns the full path to the user preferences file."""
    data_dir = get_user_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "user_preferences.json"

def load_user_preferences():
    """Loads user preferences from a JSON file in the user's data directory."""
    prefs_file = get_preferences_file_path()
    try:
        if os.path.exists(prefs_file):
            with open(prefs_file, "r") as f:
                return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load user preferences from {prefs_file}: {e}. Starting with empty preferences.")
    return {}

def save_user_preferences(preferences):
    """Saves user preferences to a JSON file in the user's data directory."""
    prefs_file = get_preferences_file_path()
    try:
        with tempfile.NamedTemporaryFile("w", delete=False, dir=prefs_file.parent) as tf:
            json.dump(preferences, tf, indent=2)
            tempname = tf.name
        os.replace(tempname, prefs_file)
    except IOError as e:
        print(f"Error saving preferences: {e}")