import tkinter as tk
from tkinter import ttk, StringVar, messagebox
import pyttsx3
import requests
from PIL import ImageGrab
import base64
import io
import json
from pydub import AudioSegment
from pydub.playback import play
import logging
import os
import keyboard
import threading
from tkinter import simpledialog
from pystray import Icon as icon, Menu as menu, MenuItem as item
from PIL import Image, ImageDraw

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize local TTS engine
tts_engine = pyttsx3.init()

# Load settings from a file
def load_settings():
    settings = {
        "openai_api_key": "",
        "elevenlabs_api_key": "",
        "tts_service": "Local",
        "openai_voice": "alloy",
        "elevenlabs_voice_id": "",
        "language": "English",
        "hotkey": "ctrl+9"
    }
    try:
        with open("settings.json", "r") as f:
            settings.update(json.load(f))
    except FileNotFoundError:
        pass
    return settings

# Save settings to a file
def save_settings(settings):
    with open("settings.json", "w") as f:
        json.dump(settings, f)
    messagebox.showinfo("Settings", "Settings saved successfully!")

def speak(text, tts_service, keys, voice, language):
    """ Speak text using selected TTS service. """
    if tts_service == 'Local':
        tts_engine.say(text)
        tts_engine.runAndWait()
    else:
        get_tts_audio(text, tts_service, keys, voice, language)

def send_request(url, headers, data):
    """ Helper function to send HTTP requests. """
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.content
        else:
            logging.error(f"Failed to communicate with service. Status code {response.status_code}. Response: {response.text}")
            return None
    except Exception as e:
        logging.error(f"Exception occurred: {str(e)}")
        return None

def get_tts_audio(text, tts_service, keys, voice, language):
    """ Generate speech from text using selected TTS service. """
    headers = {"Content-Type": "application/json"}
    if tts_service == 'OpenAI':
        url = "https://api.openai.com/v1/audio/speech"
        headers["Authorization"] = f"Bearer {keys['openai_api_key']}"
        data = {"model": "tts-1", "input": text, "voice": voice, "language": language}
    elif tts_service == 'ElevenLabs':
        url = "https://api.elevenlabs.io/v1/text-to-speech"
        headers["Authorization"] = f"Bearer {keys['elevenlabs_api_key']}"
        data = {"text": text, "voice_id": keys['elevenlabs_voice_id'], "language": language}
    else:
        speak(text, "Local", keys, voice, language)
        return

    audio_content = send_request(url, headers, data)
    if audio_content:
        audio_data = io.BytesIO(audio_content)
        sound = AudioSegment.from_file(audio_data, format="mp3")
        play(sound)

def capture_and_describe(tts_service, keys, voice, language, elevenlabs_voice_id):
    """ Capture the screen, generate description using GPT-4, and speak it. """
    screenshot = ImageGrab.grab()
    buffer = io.BytesIO()
    screenshot.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {keys['openai_api_key']}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "Please describe this image. Respond ONLY in this language: {language}"},
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}]}
        ]
    }

    description_content = send_request(url, headers, data)
    if description_content:
        description = json.loads(description_content).get('choices')[0].get('message').get('content')
        get_tts_audio(description, tts_service, keys, voice, language)

def setup_gui():
    """ Setup the GUI with controls for API keys, TTS service selection, and activation. """
    settings = load_settings()
    window = tk.Tk()
    window.title("Visual Assistance Tool")
    window.geometry("800x600")

    tab_control = ttk.Notebook(window)

    # Settings tab
    settings_tab = ttk.Frame(tab_control)
    tab_control.add(settings_tab, text="Settings")

    # Voice settings tab
    voice_settings_tab = ttk.Frame(tab_control)
    tab_control.add(voice_settings_tab, text="Voice Settings")

    # Language settings tab
    language_settings_tab = ttk.Frame(tab_control)
    tab_control.add(language_settings_tab, text="Language Settings")

    tab_control.pack(expand=1, fill='both')

    # Settings tab content
    tk.Label(settings_tab, text="Enter OpenAI API Key:", font=("Helvetica", 14)).grid(row=0, column=0, padx=10, pady=10, sticky='W')
    openai_key_entry = tk.Entry(settings_tab, width=50, font=("Helvetica", 14))
    openai_key_entry.grid(row=0, column=1, padx=10, pady=10)
    openai_key_entry.insert(0, settings["openai_api_key"])

    tk.Label(settings_tab, text="Enter ElevenLabs API Key:", font=("Helvetica", 14)).grid(row=1, column=0, padx=10, pady=10, sticky='W')
    elevenlabs_key_entry = tk.Entry(settings_tab, width=50, font=("Helvetica", 14))
    elevenlabs_key_entry.grid(row=1, column=1, padx=10, pady=10)
    elevenlabs_key_entry.insert(0, settings["elevenlabs_api_key"])

    tk.Label(settings_tab, text="Select TTS Service:", font=("Helvetica", 14)).grid(row=2, column=0, padx=10, pady=10, sticky='W')
    tts_service = StringVar(value=settings["tts_service"])
    tk.Radiobutton(settings_tab, text="Local", variable=tts_service, value="Local", font=("Helvetica", 14)).grid(row=3, column=0, padx=10, pady=10, sticky='W')
    tk.Radiobutton(settings_tab, text="OpenAI", variable=tts_service, value="OpenAI", font=("Helvetica", 14)).grid(row=3, column=1, padx=10, pady=10, sticky='W')
    tk.Radiobutton(settings_tab, text="ElevenLabs", variable=tts_service, value="ElevenLabs", font=("Helvetica", 14)).grid(row=3, column=2, padx=10, pady=10, sticky='W')

    tk.Label(settings_tab, text="Hotkey:", font=("Helvetica", 14)).grid(row=4, column=0, padx=10, pady=10, sticky='W')
    hotkey_entry = tk.Entry(settings_tab, width=50, font=("Helvetica", 14))
    hotkey_entry.grid(row=4, column=1, padx=10, pady=10)
    hotkey_entry.insert(0, settings["hotkey"])

    tk.Button(settings_tab, text="Activate Script", command=lambda: capture_and_describe(tts_service.get(), {'openai_api_key': openai_key_entry.get(), 'elevenlabs_api_key': elevenlabs_key_entry.get(), 'elevenlabs_voice_id': elevenlabs_voice_id_entry.get()}, openai_voice.get(), language.get(), elevenlabs_voice_id_entry.get()), font=("Helvetica", 14)).grid(row=5, column=1, padx=10, pady=20)

    # Voice settings tab content
    tk.Label(voice_settings_tab, text="Select OpenAI Voice:", font=("Helvetica", 14)).grid(row=0, column=0, padx=10, pady=10, sticky='W')
    openai_voice = StringVar(value=settings["openai_voice"])
    openai_voice_menu = ttk.Combobox(voice_settings_tab, textvariable=openai_voice, values=["alloy", "echo", "fable", "onyx", "nova", "shimmer"], font=("Helvetica", 14))
    openai_voice_menu.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(voice_settings_tab, text="Enter ElevenLabs Voice ID:", font=("Helvetica", 14)).grid(row=1, column=0, padx=10, pady=10, sticky='W')
    elevenlabs_voice_id_entry = tk.Entry(voice_settings_tab, width=50, font=("Helvetica", 14))
    elevenlabs_voice_id_entry.grid(row=1, column=1, padx=10, pady=10)
    elevenlabs_voice_id_entry.insert(0, settings["elevenlabs_voice_id"])

    # Language settings tab content
    tk.Label(language_settings_tab, text="Select Language:", font=("Helvetica", 14)).grid(row=0, column=0, padx=10, pady=10, sticky='W')
    language = StringVar(value=settings["language"])
    language_menu = ttk.Combobox(language_settings_tab, textvariable=language, values=["Afrikaans", "Arabic", "Armenian", "Azerbaijani", "Belarusian", "Bosnian", "Bulgarian", "Catalan", "Chinese", "Croatian", "Czech", "Danish", "Dutch", "English", "Estonian", "Finnish", "French", "Galician", "German", "Greek", "Hebrew", "Hindi", "Hungarian", "Icelandic", "Indonesian", "Italian", "Japanese", "Kannada", "Kazakh", "Korean", "Latvian", "Lithuanian", "Macedonian", "Malay", "Marathi", "Maori", "Nepali", "Norwegian", "Persian", "Polish", "Portuguese", "Romanian", "Russian", "Serbian", "Slovak", "Slovenian", "Spanish", "Swahili", "Swedish", "Tagalog", "Tamil", "Thai", "Turkish", "Ukrainian", "Urdu", "Vietnamese", "Welsh"], font=("Helvetica", 14))
    language_menu.grid(row=0, column=1, padx=10, pady=10)

    # Save button
    def save_settings_command():
        settings = {
            "openai_api_key": openai_key_entry.get(),
            "elevenlabs_api_key": elevenlabs_key_entry.get(),
            "tts_service": tts_service.get(),
            "openai_voice": openai_voice.get(),
            "elevenlabs_voice_id": elevenlabs_voice_id_entry.get(),
            "language": language.get(),
            "hotkey": hotkey_entry.get()
        }
        save_settings(settings)
        messagebox.showinfo("Settings", "Settings saved successfully!")

    tk.Button(settings_tab, text="Save Settings", command=save_settings_command, font=("Helvetica", 14)).grid(row=6, column=1, padx=10, pady=20)

    # Tooltip with contact information
    def show_contact_info(event):
        messagebox.showinfo("Contact Info", "For more information or support, visit:\nTwitter: @didntdrinkwater\nWebsite: https://www.younes.ca")

    contact_button = tk.Label(settings_tab, text="?", font=("Helvetica", 18), fg="blue", cursor="hand2")
    contact_button.grid(row=7, column=2, padx=10, pady=10, sticky='E')
    contact_button.bind("<Button-1>", show_contact_info)

    # Run the main loop
    window.mainloop()

# Function to initialize and run the system tray icon
def create_tray_icon():
    def on_activate(icon, item):
        settings = load_settings()
        capture_and_describe(settings["tts_service"], settings, settings["openai_voice"], settings["language"], settings["elevenlabs_voice_id"])

    image = Image.new('RGB', (64, 64), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 64, 64), fill=(255, 255, 255), outline=(0, 0, 0))
    draw.text((10, 10), "V", fill="black")

    menu_items = (item('Activate', on_activate), item('Exit', lambda icon, item: icon.stop()))
    tray_icon = icon("Visual Assistance Tool", image, "Visual Assistance Tool", menu_items)
    tray_icon.run()

if __name__ == "__main__":
    settings = load_settings()
    hotkey = settings.get("hotkey", "ctrl+9")

    # Set up hotkey
    def on_hotkey():
        settings = load_settings()
        capture_and_describe(settings["tts_service"], settings, settings["openai_voice"], settings["language"], settings["elevenlabs_voice_id"])

    keyboard.add_hotkey(hotkey, on_hotkey)

    # Create tray icon in a separate thread
    tray_thread = threading.Thread(target=create_tray_icon, daemon=True)
    tray_thread.start()

    # Run the main GUI setup
    setup_gui()
