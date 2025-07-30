from user_preferences import save_user_preferences, load_user_preferences
import os

def test_save_and_load_user_preferences(tmp_path):
    test_file = tmp_path / "prefs.json"
    prefs = {"always_allowed_commands": ["ls", "echo"]}
    # Temporarily override the preferences file location
    import user_preferences
    old_file = user_preferences.PREFERENCES_FILE
    user_preferences.PREFERENCES_FILE = str(test_file)
    save_user_preferences(prefs)
    loaded = load_user_preferences()
    assert loaded == prefs
    user_preferences.PREFERENCES_FILE = old_file