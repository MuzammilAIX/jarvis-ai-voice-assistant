# 🤖 JARVIS — AI Voice Assistant

JARVIS is a Python-based AI voice assistant that allows users to interact with an AI system using voice commands.

It combines **speech recognition, text-to-speech, Groq AI, weather information, news, Google search, YouTube search, music playback, and website automation** into one practical Python project.

The project is being developed as a hands-on AI engineering project to learn Python, APIs, AI/LLMs, speech processing, automation, and software development.

---

## ✨ Features

### 🎙️ Voice Recognition

JARVIS listens for the wake word:

```text
Jarvis
```

After detecting the wake word, JARVIS listens for the user's command.

It uses the `SpeechRecognition` library with Google's speech-recognition service to convert speech into text.

---

## 🧠 AI Assistant

JARVIS uses the **Groq API** to answer general questions.

The current Groq model configured in the project is:

```text
openai/gpt-oss-20b
```

JARVIS is designed to provide short, natural responses because its answers are spoken aloud.

Example:

```text
Jarvis what is artificial intelligence
```

```text
Jarvis explain machine learning
```

```text
Jarvis what is Python
```

The AI system also includes error handling for missing API keys and failed Groq requests.

---

## 🔊 Text-to-Speech

JARVIS supports multiple speech systems.

### Primary

**pyttsx3**

This provides local Windows text-to-speech.

### Fallback

**gTTS + Pygame**

If the primary speech system fails, JARVIS attempts to generate speech using Google Text-to-Speech and play the generated audio through Pygame.

This gives the assistant a fallback mechanism when one speech system is unavailable.

---

## 🌤️ Weather

JARVIS can retrieve current weather information using **wttr.in**.

No additional weather API key is required.

The weather response includes:

* Weather condition
* Temperature in Celsius
* Feels-like temperature
* Humidity

Example:

```text
Jarvis what is the weather
```

```text
Jarvis weather today
```

The current implementation uses Lahore as the default weather location.

> Note: The current version's weather command is configured around Lahore. City-specific natural-language weather commands can be expanded in a future update.

---

## 📰 News

JARVIS can retrieve the latest top headlines using **NewsAPI**.

The current configuration requests the top headlines for the configured country and reads up to five headlines aloud.

Example:

```text
Jarvis tell me the news
```

```text
Jarvis latest news
```

```text
Jarvis read the news
```

A valid `NEWS_API_KEY` is required.

---

## 🌐 Web Search

JARVIS can open Google searches for current or live information.

Example:

```text
Jarvis search the web for artificial intelligence news
```

```text
Jarvis search online for Python tutorials
```

The web-search feature opens the search in the user's browser.

JARVIS does not ask the Groq model to perform browser tool calls. Instead, current/live searches are handled separately by the Python application.

---

## 🔎 Google Search

JARVIS can open Google searches.

Examples:

```text
Jarvis search Google for Python courses
```

```text
Jarvis search for AI engineering roadmap
```

---

## ▶️ YouTube Search

JARVIS can search YouTube.

Example:

```text
Jarvis search YouTube for Python tutorials
```

It opens the YouTube search results in the default browser.

---

## 🎵 Music Playback

JARVIS can search for music on YouTube using `pywhatkit`.

Examples:

```text
Jarvis play music
```

```text
Jarvis play Believer
```

```text
Jarvis play Imagine Dragons
```

If `pywhatkit` cannot play the requested song directly, JARVIS falls back to opening YouTube search results.

---

## 🌐 Website Automation

JARVIS can open several commonly used websites.

Currently supported:

* Google
* YouTube
* Facebook
* WhatsApp
* LinkedIn
* Instagram
* GitHub
* Gmail

Examples:

```text
Jarvis open Google
```

```text
Jarvis open YouTube
```

```text
Jarvis open GitHub
```

```text
Jarvis open Gmail
```

---

## 🕐 Time and Date

JARVIS can tell the current local time.

Example:

```text
Jarvis what is the time
```

It can also provide the current date.

Example:

```text
Jarvis what is today's date
```

The time and date are obtained directly from the computer using Python's `datetime` module.

---

## 😂 Joke

JARVIS includes a simple built-in programming joke.

Example:

```text
Jarvis tell me a joke
```

---

## ❓ Help

JARVIS has a built-in help command.

Example:

```text
Jarvis help
```

The available commands are displayed in the terminal and summarized through speech.

---

## 🛑 Shutdown

JARVIS can be stopped using commands such as:

```text
Jarvis stop
```

```text
Jarvis exit
```

```text
Jarvis quit
```

```text
Jarvis shutdown
```

```text
Jarvis goodbye
```

It also handles `Ctrl+C` gracefully.

---

# 🛠️ Technologies Used

| Technology                | Purpose                         |
| ------------------------- | ------------------------------- |
| Python                    | Main programming language       |
| SpeechRecognition         | Voice-to-text                   |
| Google Speech Recognition | Speech recognition service      |
| pyttsx3                   | Local text-to-speech            |
| gTTS                      | Online text-to-speech fallback  |
| Pygame                    | Audio playback                  |
| Groq                      | AI/LLM responses                |
| Requests                  | HTTP/API requests               |
| NewsAPI                   | News headlines                  |
| wttr.in                   | Weather information             |
| pywhatkit                 | YouTube music playback          |
| python-dotenv             | Environment variable management |
| Webbrowser                | Browser automation              |

---

# 📁 Project Structure

```text
Mega Project 01 JARVIS/
│
├── JARVIS.py
├── musicLibrary.py
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
└── env313/              # Local virtual environment
```

The `env313` virtual environment should **not** be uploaded to GitHub.

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Then enter the project directory:

```bash
cd "Mega Project 01 JARVIS"
```

---

## 2. Create a Virtual Environment

On Windows:

```powershell
py -m venv env313
```

Activate it:

```powershell
.\env313\Scripts\Activate.ps1
```

If PowerShell prevents activation, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate the environment again:

```powershell
.\env313\Scripts\Activate.ps1
```

You should see:

```text
(env313)
```

in the terminal.

---

# 📦 Install Dependencies

Install the project dependencies using:

```powershell
pip install -r requirements.txt
```

---

# 🔑 API Configuration

JARVIS requires API keys for some features.

Create a file named:

```text
.env
```

in the project root.

Add:

```env
NEWS_API_KEY=your_newsapi_key_here
GROQ_API_KEY=your_groq_api_key_here
```

### Groq API

The Groq API is used for AI-generated responses.

### NewsAPI

NewsAPI is used to retrieve current headlines.

### Weather

The weather feature currently uses wttr.in and does not require another API key.

---

# 🔐 Security

**Never upload your `.env` file to GitHub.**

Your `.env` file contains private API credentials.

Your `.gitignore` should contain:

```gitignore
.env
```

A safe template can be provided using:

```text
.env.example
```

For example:

```env
NEWS_API_KEY=your_newsapi_key_here
GROQ_API_KEY=your_groq_api_key_here
```

If an API key is accidentally committed to a public GitHub repository, revoke or rotate the key immediately.

---

# ▶️ Run JARVIS

Activate your virtual environment and run:

```powershell
python JARVIS.py
```

JARVIS will:

1. Check the configuration.
2. Check the microphone.
3. Initialize the speech system.
4. Wait for the wake word.
5. Listen for commands.
6. Process the command.
7. Respond through text and speech.

---

# 🎤 Example Commands

## AI

```text
Jarvis explain artificial intelligence
```

```text
Jarvis what is machine learning
```

```text
Jarvis explain Python classes
```

## Weather

```text
Jarvis what is the weather
```

## News

```text
Jarvis latest news
```

## Web

```text
Jarvis search the web for AI engineering
```

## Google

```text
Jarvis search Google for Python tutorials
```

## YouTube

```text
Jarvis search YouTube for Python courses
```

## Music

```text
Jarvis play Believer
```

## Websites

```text
Jarvis open GitHub
```

```text
Jarvis open YouTube
```

```text
Jarvis open Gmail
```

## Time

```text
Jarvis what is the time
```

## Date

```text
Jarvis what is today's date
```

## Help

```text
Jarvis help
```

## Exit

```text
Jarvis goodbye
```

---

# 🧩 Error Handling

JARVIS includes error handling for several common situations:

* Missing Groq API key
* Missing NewsAPI key
* Microphone errors
* Speech-recognition errors
* AI API errors
* Weather request errors
* News API errors
* Website-opening errors
* Music playback errors
* Text-to-speech errors
* Keyboard interruption

The application attempts to continue running when possible rather than immediately shutting down.

---

# 🏗️ Current Architecture

The current application follows a simple command-processing architecture:

```text
                    ┌─────────────────┐
                    │   Microphone    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ SpeechRecognition│
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Wake Word Check │
                    │     "Jarvis"    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Command Handler │
                    └────────┬────────┘
                             │
              ┌──────────────┼───────────────┐
              │              │               │
              ▼              ▼               ▼
         Local Commands   Web/API          Groq AI
              │              │               │
              ├── Time       ├── Weather     └── AI Answers
              ├── Date       ├── News
              ├── Websites  ├── Google
              ├── Music     └── YouTube
              └── Help
                             │
                             ▼
                    ┌─────────────────┐
                    │ Text + Speech   │
                    └─────────────────┘
```

---

# 🚀 Future Improvements

The current version provides the core JARVIS voice-assistant functionality.

Planned improvements include:

### 🧠 Memory

* Conversation history
* Persistent memory
* User preferences
* Context-aware conversations

### 🤖 Better AI Architecture

* Intent classification
* Dedicated tool/function routing
* Better command understanding
* Multi-step AI tasks
* Structured tool calling

### 💻 Computer Automation

* Open desktop applications
* Control files and folders
* Keyboard automation
* Mouse automation
* System controls

### 👁️ Computer Vision

* Camera integration
* Image understanding
* Screen understanding
* Object detection

### 📚 Document Intelligence

* PDF understanding
* Document search
* RAG
* Vector databases
* Personal knowledge base

### 📧 Productivity

* Email integration
* Calendar integration
* Task management
* Reminders

### 🖥️ User Interface

* Graphical user interface
* Animated JARVIS interface
* Conversation history
* System status dashboard

### 🔐 Security

* User authentication
* Permission management
* Secure tool execution
* Protected personal data

---

# 🎯 Learning Objectives

This project is designed to develop practical experience in:

* Python programming
* Object-oriented programming
* APIs
* Environment variables
* Git and GitHub
* Speech recognition
* Text-to-speech
* Large Language Models
* AI application development
* Web APIs
* Browser automation
* Error handling
* Virtual environments
* Software architecture

---

# 📈 Project Development

JARVIS is being developed incrementally.

The development path is:

```text
Python Fundamentals
        ↓
Voice Recognition
        ↓
Text-to-Speech
        ↓
API Integration
        ↓
Groq AI
        ↓
Web Search
        ↓
Weather & News
        ↓
Automation
        ↓
Memory
        ↓
Advanced AI Assistant
```

---

# 👨‍💻 Author

**Enginner Muzammil**

This project is part of my hands-on journey toward becoming an **AI Engineer**.

---

# ⭐ Contributing

Suggestions, improvements, and ideas are welcome.

If you want to contribute:

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Test the changes.
5. Submit a pull request.

---

# 📜 License

This project is licensed under the MIT License.

You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of this software, subject to the conditions of the MIT License.

See the LICENSE file for the full license text.

---

## ⭐ If you find this project useful

Consider giving the repository a ⭐ on GitHub.
