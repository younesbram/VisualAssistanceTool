# Visual Assistance Tool

This project provides a visual assistance tool designed for visually impaired users. The tool captures the screen, generates a description of the screen content using the OpenAI GPT-4 API, and reads the description out loud using either local text-to-speech (TTS) or cloud-based TTS services like OpenAI's TTS or ElevenLabs.

## Features

- **Screen Capture**: Captures the current screen content.
- **Image Description**: Uses OpenAI's GPT-4 to generate a description of the captured image.
- **Text-to-Speech (TTS)**: Supports local TTS and cloud-based TTS services (OpenAI, ElevenLabs).
- **Multi-language Support**: Supports a wide range of languages for the TTS output.
- **Hotkey Activation**: Customize and use a hotkey to activate the screen capture and description process.
- **Persistent Settings**: Saves API keys, TTS service preferences, and other settings for future use.
- **System Tray Integration**: Minimize the app to the system tray and use a tray icon for quick access.

## Installation

### Prerequisites

- Python 3.7 or higher
- Pip package manager
- PyInstaller (for creating an executable)

### Clone the Repository

```
git clone https://github.com/yourusername/visual-assistance-tool.git
cd visual-assistance-tool
```

### Install Dependencies

```
pip install -r requirements.txt
```

### Create Executable (Optional)

To create an executable for easy distribution:

```
pyinstaller --onefile --windowed visualizemyscreen.py
```

The executable will be created in the `dist` directory.

## Usage

### Running the Application

```
python visualizemyscreen.py
```

Or, if you created an executable:

```
./dist/visualizemyscreen.exe
```

### Setting Up

1. Enter your OpenAI API key and ElevenLabs API key in the settings tab.
2. Choose your preferred TTS service (Local, OpenAI, ElevenLabs).
3. Set your desired hotkey for activating the screen capture and description.
4. Select the language for the TTS output.
5. Save your settings.

### Activating the Tool

- Use the hotkey you set up to capture the screen and generate a description.
- You can also use the tray icon to activate the tool.

## Contact

For more information or support, visit:
- Twitter: [@didntdrinkwater](https://twitter.com/didntdrinkwater)
- Website: [younes.ca](https://www.younes.ca)

## License

This project is licensed under the MIT License.

---

Feel free to contact me for any questions or support!

---

This tool is designed to be helpful and accessible for visually impaired users. Contributions and suggestions are welcome to make this tool even better.

---

Message me on x.com/didntdrinkwater or https://www.younes.ca
