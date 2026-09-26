# JARVIS AI Voice Assistant

A Python-based voice assistant inspired by JARVIS. It listens for the wake word **"Jarvis"**, understands voice commands, opens websites, plays music links, fetches news, and uses Groq AI for general questions.

## Features

- Voice recognition with SpeechRecognition
- Text-to-speech with gTTS and Pygame
- AI responses using Groq
- Web search through Groq browser search
- Latest news using NewsAPI
- Music library support
- Opens Google, YouTube, Facebook, WhatsApp, LinkedIn, and Instagram
- Wake-word interaction using "Jarvis"
- API keys stored outside the source code

## Project Structure

```text
jarvis-ai-voice-assistant/
├── main.py
├── musicLibrary.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Requirements

- Windows 10/11
- Python 3.13 or a compatible Python version
- Working microphone
- Internet connection
- Groq API key
- NewsAPI key

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/itzmuzammilaidev-lab/jarvis-ai-voice-assistant.git
cd jarvis-ai-voice-assistant
```

### 2. Create a virtual environment

```powershell
py -m venv env313
```

Activate it:

```powershell
.\env313\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again:

```powershell
.\env313\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

> If PyAudio fails to install on your Python version, use a compatible PyAudio installation for your environment. Your existing project already has microphone support working.

### 4. Create your environment file

Copy `.env.example` and rename the copy to `.env`.

Put your own keys inside:

```env
NEWS_API_KEY=your_real_newsapi_key
GROQ_API_KEY=your_real_groq_api_key
```

**Never commit `.env` to GitHub.**

### 5. Run JARVIS

```powershell
python main.py
```

Say:

```text
Jarvis
```

Then try commands such as:

```text
Open Google
Open YouTube
Give me the latest news
```

or ask a general question for the AI.

## Example Commands

| Command | Action |
|---|---|
| `Jarvis` | Activates the assistant |
| `Open Google` | Opens Google |
| `Open YouTube` | Opens YouTube |
| `Open Facebook` | Opens Facebook |
| `Open WhatsApp` | Opens WhatsApp Web |
| `Open LinkedIn` | Opens LinkedIn |
| `Open Instagram` | Opens Instagram |
| `Play stealth` | Opens the matching music-library link |
| `Give me the latest news` | Fetches top headlines |
| General question | Sends the question to Groq AI |

## API Keys

This project uses Groq for AI responses and NewsAPI for news headlines.

Keep API keys private. Do not put real keys directly into `main.py`, GitHub, screenshots, or README files.

## Security

The repository should contain `.env.example` but should **not** contain `.env`.

If a secret is accidentally pushed to GitHub, revoke/rotate the key immediately.

## Future Improvements

- Local MP3 music playback
- Desktop application controls
- Better wake-word detection
- Conversation memory
- GUI interface
- Weather commands
- System controls
- Modular command architecture
- More natural voice responses

## Author

**Muzammil**

GitHub: https://github.com/itzmuzammilaidev-lab

## License

This project is intended for learning, experimentation, and portfolio development.
