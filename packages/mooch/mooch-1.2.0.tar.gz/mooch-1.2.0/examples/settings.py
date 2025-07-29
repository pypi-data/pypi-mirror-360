from mooch.settings import Settings

defaults = {}
defaults["settings.mood"] = "happy"
defaults["settings.volume"] = 50

settings = Settings("mooch", defaults)  # Change 'mooch' to your project's name

print("Current Settings:")
print(f"Mood: {settings.get('settings.mood')}")
print(f"Volume: {settings.get('settings.volume')}")

settings["settings.volume"] = 75

print("Updated Settings:")
print(f"Mood: {settings.get('settings.mood')}")
print(f"Volume: {settings.get('settings.volume')}")
