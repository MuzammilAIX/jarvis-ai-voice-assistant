import os
import base64
import time
import tempfile
import webbrowser
import subprocess
from html.parser import HTMLParser
from datetime import datetime
from urllib.parse import quote_plus

import requests
import speech_recognition as sr
import pyttsx3
import pygame

from dotenv import load_dotenv
from gtts import gTTS
from groq import Groq


# ============================================================
# JARVIS AI VOICE ASSISTANT
# Complete updated version
#
# Main features:
# - Wake word: "Jarvis"
# - Voice recognition
# - Windows SAPI voice + fallbacks
# - Groq AI for general questions
# - Live weather with city detection
# - Text-only web search
# - News
# - Google / YouTube search
# - Music
# - Time / date
# - Common website opening
# ============================================================


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# ============================================================
# CONFIGURATION
# ============================================================

ASSISTANT_NAME = "Jarvis"

GROQ_MODEL = "openai/gpt-oss-20b"
GROQ_REASONING_EFFORT = "low"

NEWS_COUNTRY = "us"

# Default weather city.
# If no city is mentioned, JARVIS uses this city.
DEFAULT_WEATHER_CITY = "Lahore"

WAKE_WORD_TIMEOUT = 5
WAKE_WORD_PHRASE_TIME = 8

COMMAND_TIMEOUT = 8
COMMAND_PHRASE_TIME = 12


# ============================================================
# SPEECH RECOGNIZER
# ============================================================

recognizer = sr.Recognizer()

# Helps speech recognition detect normal speech.
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True

# Silence duration before the phrase is considered finished.
recognizer.pause_threshold = 0.8


# ============================================================
# PYTTSX3 FALLBACK ENGINE
# ============================================================

try:

    pyttsx_engine = pyttsx3.init()

    pyttsx_engine.setProperty(
        "rate",
        175
    )

    pyttsx_engine.setProperty(
        "volume",
        1.0
    )

    PYTTSX_AVAILABLE = True

except Exception as error:

    pyttsx_engine = None
    PYTTSX_AVAILABLE = False

    print(
        "pyttsx3 initialization failed:"
    )

    print(error)


# ============================================================
# PYGAME INITIALIZATION
# ============================================================

pygame_initialized = False


def initialize_pygame():
    """
    Initialize pygame mixer only when needed.
    """

    global pygame_initialized

    try:

        if not pygame_initialized:

            pygame.mixer.init()

            pygame_initialized = True

        return True

    except Exception as error:

        print(
            "Pygame audio initialization error:"
        )

        print(error)

        pygame_initialized = False

        return False


# ============================================================
# SPEECH OUTPUT
# ============================================================

def windows_speak(text):
    """
    Primary Windows voice engine.

    Uses Windows SAPI through PowerShell.

    Base64 encoding prevents apostrophes, quotes, dollar signs,
    brackets, etc. in AI responses from breaking PowerShell.
    """

    if os.name != "nt":
        return False

    if not text:
        return False

    # Encode response text safely.
    text_b64 = base64.b64encode(
        str(text).encode("utf-8")
    ).decode("ascii")

    ps_script = (
        "Add-Type -AssemblyName System.Speech; "
        "$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$voice.Volume = 100; "
        "$voice.Rate = 0; "
        f"$text = [Text.Encoding]::UTF8.GetString("
        f"[Convert]::FromBase64String('{text_b64}')); "
        "$voice.Speak($text); "
        "$voice.Dispose();"
    )

    encoded_command = base64.b64encode(
        ps_script.encode("utf-16le")
    ).decode("ascii")

    try:

        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-EncodedCommand",
                encoded_command,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            return True

        print(
            "Windows SAPI speech error:"
        )

        if result.stderr:
            print(
                result.stderr.strip()
            )

    except Exception as error:

        print(
            "Windows SAPI speech error:"
        )

        print(error)

    return False


def speak_pyttsx3(text):
    """
    Offline pyttsx3 fallback.
    """

    if not PYTTSX_AVAILABLE or not text:
        return False

    try:

        pyttsx_engine.say(
            str(text)
        )

        pyttsx_engine.runAndWait()

        return True

    except Exception as error:

        print(
            "pyttsx3 speech error:"
        )

        print(error)

        return False


def speak_gtts(text):
    """
    Online gTTS + pygame fallback.
    """

    if not text:
        return False

    temp_file = None

    try:

        fd, temp_file = tempfile.mkstemp(
            prefix="jarvis_",
            suffix=".mp3"
        )

        os.close(fd)

        tts = gTTS(
            text=str(text),
            lang="en",
            slow=False
        )

        tts.save(
            temp_file
        )

        if not initialize_pygame():

            raise RuntimeError(
                "Pygame mixer could not initialize."
            )

        try:

            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()

        except Exception:
            pass

        pygame.mixer.music.load(
            temp_file
        )

        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.05)

        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

        try:
            pygame.mixer.music.unload()
        except Exception:
            pass

        return True

    except Exception as error:

        print(
            "gTTS/Pygame speech error:"
        )

        print(error)

        return False

    finally:

        if temp_file:

            for attempt in range(10):

                try:

                    if os.path.exists(
                        temp_file
                    ):

                        os.remove(
                            temp_file
                        )

                    break

                except PermissionError:

                    if attempt < 9:
                        time.sleep(0.2)

                except Exception:

                    break


def speak(text):
    """
    Main JARVIS speech function.

    Normal JARVIS responses are:
    1. Printed in terminal.
    2. Spoken aloud.

    Web-search results deliberately do NOT use this function
    because web search is text-only.
    """

    if text is None:
        return False

    text = str(text).strip()

    if not text:
        return False

    print(
        f"JARVIS: {text}"
    )

    # 1. Windows SAPI
    if windows_speak(text):
        return True

    # 2. pyttsx3
    if speak_pyttsx3(text):
        return True

    # 3. gTTS + pygame
    if speak_gtts(text):
        return True

    print(
        "JARVIS: All speech engines failed."
    )

    return False


# ============================================================
# GROQ CLIENT
# ============================================================

groq_client = None

if GROQ_API_KEY:

    try:

        groq_client = Groq(
            api_key=GROQ_API_KEY
        )

    except Exception as error:

        print(
            "Groq initialization failed:"
        )

        print(error)

        groq_client = None

else:

    print(
        "WARNING: GROQ_API_KEY was not found."
    )


# ============================================================
# AI PROCESSING
# ============================================================

def aiProcess(command):
    """
    Send a general question to Groq AI.

    Live information such as weather, current news, and
    explicit web searches is handled separately by JARVIS.
    """

    if not command:
        return (
            "I didn't receive a question."
        )

    if not groq_client:

        return (
            "My AI service is not configured. "
            "Please check your GROQ_API_KEY in the .env file."
        )

    system_message = """
You are JARVIS, a helpful AI voice assistant.

Rules:
- Give concise, natural answers because your answer will be spoken aloud.
- Do not use markdown tables, long lists, or unnecessary formatting.
- Keep normal answers under about 100 words unless the user asks for detail.
- Never pretend you have live information.
- Live/current information is handled separately by JARVIS.
"""

    try:

        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": command.strip()
                }
            ],
            temperature=0.6,
            max_completion_tokens=2048,
            reasoning_effort=GROQ_REASONING_EFFORT,
        )

        answer = (
            response.choices[0].message.content
        )

        # Retry once if the model returns empty content.
        if not answer:

            response = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": command.strip()
                    }
                ],
                temperature=0.6,
                max_completion_tokens=4096,
                reasoning_effort=GROQ_REASONING_EFFORT,
            )

            answer = (
                response.choices[0].message.content
            )

        if answer:
            return answer.strip()

        return (
            "I couldn't generate an answer."
        )

    except Exception as error:

        print()
        print(
            "Groq AI error:"
        )

        print(error)

        print()

        return (
            "Sorry, I couldn't connect to my AI service right now. "
            "Please check your internet connection and Groq API key."
        )


# ============================================================
# LIVE WEB SEARCH - TEXT ONLY
# ============================================================

class DuckDuckGoParser(HTMLParser):
    """
    Parser for DuckDuckGo HTML results.

    Results are stored explicitly so web_search() can display them.
    """

    def __init__(self):

        super().__init__()

        self.results = []

        self.current = None

        self.in_title = False
        self.in_snippet = False

    def handle_starttag(
        self,
        tag,
        attrs
    ):

        attrs = dict(attrs)

        classes = attrs.get(
            "class",
            ""
        )

        # Search-result title.
        if (
            tag == "a"
            and "result__a" in classes
        ):

            # Save an unfinished previous result.
            if self.current:

                self.results.append(
                    self.current
                )

            self.current = {
                "title": "",
                "url": attrs.get(
                    "href",
                    ""
                ),
                "snippet": ""
            }

            self.in_title = True

            return

        # Search-result snippet.
        if (
            self.current
            and "result__snippet" in classes
        ):

            self.in_snippet = True

    def handle_data(self, data):

        if not self.current:
            return

        data = data.strip()

        if not data:
            return

        if self.in_title:

            self.current["title"] += (
                data + " "
            )

        elif self.in_snippet:

            self.current["snippet"] += (
                data + " "
            )

    def handle_endtag(self, tag):

        if tag == "a":

            self.in_title = False

        if tag in (
            "div",
            "span"
        ):

            self.in_snippet = False

    def close(self):

        # Save final result.
        if self.current:

            self.results.append(
                self.current
            )

            self.current = None

        super().close()


def web_search(query):
    """
    Search the web and DISPLAY INFORMATION AS TEXT ONLY.

    This function deliberately does not call speak().
    """

    query = str(query).strip()

    if not query:

        print(
            "WEB SEARCH: No search query was provided."
        )

        return

    print()
    print("=" * 70)
    print(
        f"WEB SEARCH: {query}"
    )
    print("=" * 70)

    url = (
        "https://html.duckduckgo.com/html/?q="
        + quote_plus(query)
    )

    try:

        response = requests.get(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/140 Safari/537.36"
                )
            },
            timeout=12,
        )

        response.raise_for_status()

        parser = DuckDuckGoParser()

        parser.feed(
            response.text
        )

        parser.close()

        results = []

        for item in parser.results:

            title = " ".join(
                item["title"].split()
            )

            snippet = " ".join(
                item["snippet"].split()
            )

            result_url = item["url"]

            if (
                title
                and title not in [
                    r["title"]
                    for r in results
                ]
            ):

                results.append(
                    {
                        "title": title,
                        "snippet": snippet,
                        "url": result_url,
                    }
                )

        if not results:

            print(
                "No readable text results were found for this search."
            )

            print(
                "Try saying: search the web for <your question> again."
            )

            print("=" * 70)

            return

        for index, result in enumerate(
            results[:5],
            start=1
        ):

            print(
                f"\n{index}. {result['title']}"
            )

            if result["snippet"]:

                print(
                    f"   {result['snippet']}"
                )

            if result["url"]:

                print(
                    f"   {result['url']}"
                )

        print()
        print(
            "Web search completed. Results above are text-only."
        )

        print("=" * 70)

    except requests.exceptions.RequestException as error:

        print(
            "Web search connection error:"
        )

        print(error)

        print(
            "Opening the search page in your browser."
        )

        try:

            webbrowser.open_new_tab(
                url
            )

        except Exception:
            pass

    except Exception as error:

        print(
            "Web search error:"
        )

        print(error)


# ============================================================
# WEATHER
# ============================================================

def get_weather(city=DEFAULT_WEATHER_CITY):
    """
    Get current weather from wttr.in.

    No separate weather API key is required.
    """

    city = str(city).strip()

    if not city:
        city = DEFAULT_WEATHER_CITY

    try:

        url = (
            f"https://wttr.in/"
            f"{quote_plus(city)}"
            f"?format=j1"
        )

        response = requests.get(
            url,
            headers={
                "User-Agent": "JARVIS/1.0"
            },
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        current = data[
            "current_condition"
        ][0]

        temperature = current.get(
            "temp_C",
            "unknown"
        )

        feels_like = current.get(
            "FeelsLikeC",
            "unknown"
        )

        humidity = current.get(
            "humidity",
            "unknown"
        )

        wind_speed = current.get(
            "windspeedKmph",
            "unknown"
        )

        description_list = current.get(
            "weatherDesc",
            []
        )

        if description_list:

            description = (
                description_list[0].get(
                    "value",
                    "unknown"
                )
            )

        else:

            description = "unknown"

        return (
            f"The current weather in {city.title()} is "
            f"{description}. "
            f"The temperature is {temperature} degrees Celsius, "
            f"feels like {feels_like} degrees. "
            f"Humidity is {humidity} percent, "
            f"with wind speed of {wind_speed} kilometers per hour."
        )

    except requests.exceptions.RequestException as error:

        print(
            "Weather connection error:"
        )

        print(error)

        return (
            "I couldn't connect to the weather service right now."
        )

    except (
        KeyError,
        IndexError,
        ValueError,
        TypeError
    ) as error:

        print(
            "Weather data error:"
        )

        print(error)

        return (
            "I received the weather information, "
            "but I couldn't understand it."
        )

    except Exception as error:

        print(
            "Weather error:"
        )

        print(error)

        return (
            "I couldn't get the weather right now."
        )


def extract_weather_city(command):
    """
    Extract a city from natural weather commands.

    Examples:
        weather
        what is weather
        weather in Lahore
        tell me the Lahore weather
        temperature in Islamabad
        how hot is Karachi
    """

    text = command.lower().strip()

    # Common cities.
    known_cities = [
        "lahore",
        "karachi",
        "islamabad",
        "rawalpindi",
        "peshawar",
        "quetta",
        "multan",
        "faisalabad",
        "sialkot",
        "gujranwala",
        "hyderabad",
        "bahawalpur",
        "sargodha",
        "abbottabad",
        "murree",
        "mardan",
        "swat",
        "gilgit",
        "skardu",
        "jhelum",
        "kasur",
        "sheikhupura"
    ]

    # First check known cities anywhere in the sentence.
    # This handles:
    # "tell me the Lahore weather"
    # "how hot is Karachi"
    # "weather in Islamabad"
    for city in known_cities:

        if city in text:
            return city

    # Handle:
    # weather in Dubai
    # weather of Dubai
    # temperature in London
    # forecast for New York
    markers = [
        "weather in ",
        "weather of ",
        "temperature in ",
        "temperature of ",
        "forecast in ",
        "forecast for "
    ]

    for marker in markers:

        if marker in text:

            city = text.split(
                marker,
                1
            )[1].strip()

            # Remove common trailing words.
            endings = [
                " today",
                " right now",
                " now",
                " please",
                " today please"
            ]

            for ending in endings:

                if city.endswith(
                    ending
                ):

                    city = city[
                        :-len(ending)
                    ].strip()

            if city:
                return city

    # Handle:
    # what is the weather of Lahore
    # how is the weather of Karachi
    if (
        "weather" in text
        and " of " in text
    ):

        city = text.split(
            " of ",
            1
        )[1].strip()

        if city:
            return city

    # No city detected.
    return DEFAULT_WEATHER_CITY


def is_weather_command(command):
    """
    Detect weather-related commands before they reach Groq.
    """

    text = command.lower().strip()

    weather_phrases = [
        "weather",
        "temperature",
        "forecast",
        "how hot",
        "how cold",
        "will it rain",
        "is it raining",
        "rain today",
        "weather like"
    ]

    return any(
        phrase in text
        for phrase in weather_phrases
    )


# ============================================================
# NEWS
# ============================================================

def get_news():
    """
    Get top news headlines from NewsAPI.

    On success, headlines are spoken individually.
    On failure, an error message is returned.
    """

    if not NEWS_API_KEY:

        return (
            "News service is not configured. "
            "Please add NEWS_API_KEY to your .env file."
        )

    url = (
        "https://newsapi.org/v2/top-headlines"
    )

    params = {
        "country": NEWS_COUNTRY,
        "pageSize": 5,
        "apiKey": NEWS_API_KEY
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        if data.get("status") != "ok":

            return (
                "I couldn't get the latest news."
            )

        articles = data.get(
            "articles",
            []
        )

        if not articles:

            return (
                "I couldn't find any news right now."
            )

        headlines = []

        for index, article in enumerate(
            articles[:5],
            start=1
        ):

            title = article.get(
                "title"
            )

            if title:

                headlines.append(
                    f"{index}. {title}"
                )

        if not headlines:

            return (
                "No news headlines were found."
            )

        # Speak headlines one by one.
        for headline in headlines:

            speak(headline)

        return None

    except requests.exceptions.RequestException as error:

        print(
            "News API connection error:"
        )

        print(error)

        return (
            "I couldn't connect to the news service."
        )

    except Exception as error:

        print(
            "News error:"
        )

        print(error)

        return (
            "Something went wrong while getting the news."
        )


# ============================================================
# WEBSITE OPENING
# ============================================================

def open_website(url, name):
    """
    Open a website safely.
    """

    try:

        opened = webbrowser.open(
            url
        )

        if opened:

            speak(
                f"Opening {name}."
            )

        else:

            speak(
                f"I couldn't open {name}."
            )

    except Exception as error:

        print(
            "Website opening error:"
        )

        print(error)

        speak(
            f"I couldn't open {name}."
        )


# ============================================================
# GOOGLE SEARCH
# ============================================================

def google_search(query):
    """
    Search Google.
    """

    if not query:

        speak(
            "What should I search for?"
        )

        return

    url = (
        "https://www.google.com/search?q="
        + quote_plus(query)
    )

    open_website(
        url,
        "Google"
    )


# ============================================================
# YOUTUBE SEARCH
# ============================================================

def youtube_search(query):
    """
    Search YouTube.
    """

    if not query:

        speak(
            "What should I search on YouTube?"
        )

        return

    url = (
        "https://www.youtube.com/results?search_query="
        + quote_plus(query)
    )

    open_website(
        url,
        "YouTube"
    )


# ============================================================
# MUSIC
# ============================================================

def play_music(command):
    """
    Open the first YouTube result for the requested song.

    If pywhatkit is unavailable or fails, JARVIS opens
    a normal YouTube search instead.
    """

    music_name = command.lower().strip()

    prefixes = [
        "play music",
        "play song",
        "play",
        "put on",
        "listen to"
    ]

    for prefix in prefixes:

        if music_name.startswith(
            prefix
        ):

            music_name = music_name[
                len(prefix):
            ].strip()

            break

    # Remove natural-language endings.
    for ending in [
        " on youtube",
        " on youtube music"
    ]:

        if music_name.endswith(
            ending
        ):

            music_name = music_name[
                :-len(ending)
            ].strip()

    if not music_name:

        speak(
            "Which song should I play?"
        )

        return

    speak(
        f"Playing {music_name}."
    )

    try:

        import pywhatkit

        pywhatkit.playonyt(
            music_name
        )

    except ImportError:

        print(
            "pywhatkit is not installed."
        )

        print(
            "Install it with: pip install pywhatkit"
        )

        url = (
            "https://www.youtube.com/results?search_query="
            + quote_plus(music_name)
        )

        try:

            webbrowser.open_new_tab(
                url
            )

        except Exception as error:

            print(
                "Music error:"
            )

            print(error)

            speak(
                "I couldn't open YouTube."
            )

    except Exception as error:

        print(
            "Music playback error:"
        )

        print(error)

        url = (
            "https://www.youtube.com/results?search_query="
            + quote_plus(music_name)
        )

        try:

            webbrowser.open_new_tab(
                url
            )

            speak(
                "I opened the YouTube results for that song."
            )

        except Exception as second_error:

            print(
                "YouTube fallback error:"
            )

            print(second_error)

            speak(
                "I couldn't open YouTube."
            )


# ============================================================
# TIME
# ============================================================

def tell_time():

    current_time = datetime.now().strftime(
        "%I:%M %p"
    )

    speak(
        f"The current time is {current_time}."
    )


# ============================================================
# DATE
# ============================================================

def tell_date():

    current_date = datetime.now().strftime(
        "%A, %B %d, %Y"
    )

    speak(
        f"Today is {current_date}."
    )


# ============================================================
# HELP
# ============================================================

def show_help():

    help_text = """
You can ask me to:

Open Google
Open YouTube
Open Facebook
Open WhatsApp
Open LinkedIn
Open Instagram
Open GitHub
Open Gmail

Search Google for something
Search YouTube for something
Search the web for something
Play a song

Tell me the time
Tell me today's date
Tell me the weather
Tell me the weather in another city
Read the news

Ask me any general question

Say stop, exit, quit, or goodbye to close me.
"""

    print(
        help_text
    )

    speak(
        "I can open websites, search Google and YouTube, "
        "search the web, play music, tell you the time, "
        "date and weather, read news, and answer general "
        "questions using AI. Web searches are shown as "
        "text in the terminal."
    )


# ============================================================
# PROCESS COMMAND
# ============================================================

def process_command(command):
    """
    Process a recognized voice command.

    Returns:
        True  -> keep JARVIS running
        False -> exit JARVIS
    """

    if not command:
        return True

    command = command.lower().strip()

    print()
    print(
        f"COMMAND: {command}"
    )
    print()

    # ========================================================
    # EXIT
    # ========================================================

    exit_commands = [
        "exit",
        "quit",
        "stop",
        "shutdown",
        "goodbye",
        "bye",
        "go to sleep",
        "sleep"
    ]

    if any(
        command == item
        or command.startswith(
            item + " "
        )
        for item in exit_commands
    ):

        speak(
            "Goodbye. Shutting down JARVIS."
        )

        return False

    # ========================================================
    # HELP
    # ========================================================

    if command in [
        "help",
        "what can you do",
        "commands",
        "show commands"
    ]:

        show_help()

        return True

    # ========================================================
    # TIME
    # ========================================================

    if (
        "what time" in command
        or "what's the time" in command
        or "what is the time" in command
        or "current time" in command
        or "tell me the time" in command
        or command == "time"
    ):

        tell_time()

        return True

    # ========================================================
    # DATE
    # ========================================================

    if (
        "what is the date" in command
        or "what's the date" in command
        or "today's date" in command
        or "tell me the date" in command
        or command == "date"
        or "what day is it" in command
        or "what is today" in command
    ):

        tell_date()

        return True

    # ========================================================
    # WEATHER
    #
    # IMPORTANT:
    # This MUST be before current/latest and before Groq.
    #
    # Examples:
    #   what is weather
    #   what's the weather
    #   weather in Lahore
    #   tell me the Lahore weather
    #   temperature in Karachi
    #   how hot is Islamabad
    # ========================================================

    if is_weather_command(
        command
    ):

        city = extract_weather_city(
            command
        )

        print(
            f"WEATHER CITY: {city.title()}"
        )

        weather = get_weather(
            city
        )

        speak(
            weather
        )

        return True

    # ========================================================
    # LIVE WEB SEARCH
    # ========================================================

    if (
        command.startswith(
            "search the web for"
        )
        or command.startswith(
            "search web for"
        )
        or command.startswith(
            "web search for"
        )
        or command.startswith(
            "search online for"
        )
    ):

        prefixes = [
            "search the web for",
            "search web for",
            "web search for",
            "search online for"
        ]

        query = command

        for prefix in prefixes:

            if query.startswith(
                prefix
            ):

                query = query[
                    len(prefix):
                ].strip()

                break

        web_search(
            query
        )

        return True

    # ========================================================
    # CURRENT / LATEST INFORMATION
    # ========================================================

    if (
        "latest" in command
        or "current" in command
        or "today" in command
        or "right now" in command
        or "what happened" in command
        or "who is the prime minister" in command
        or "who is the president" in command
        or "who is the chief minister" in command
        or "who is the governor" in command
    ) and not (
        "what time" in command
        or "what's the time" in command
        or "what is the time" in command
        or is_weather_command(
            command
        )
    ):

        web_search(
            command
        )

        return True

    # ========================================================
    # GOOGLE
    # ========================================================

    if command in [
        "open google",
        "google"
    ]:

        open_website(
            "https://www.google.com",
            "Google"
        )

        return True

    # ========================================================
    # YOUTUBE
    # ========================================================

    if command in [
        "open youtube",
        "youtube"
    ]:

        open_website(
            "https://www.youtube.com",
            "YouTube"
        )

        return True

    # ========================================================
    # FACEBOOK
    # ========================================================

    if command in [
        "open facebook",
        "facebook"
    ]:

        open_website(
            "https://www.facebook.com",
            "Facebook"
        )

        return True

    # ========================================================
    # WHATSAPP
    # ========================================================

    if command in [
        "open whatsapp",
        "whatsapp"
    ]:

        open_website(
            "https://web.whatsapp.com",
            "WhatsApp"
        )

        return True

    # ========================================================
    # LINKEDIN
    # ========================================================

    if command in [
        "open linkedin",
        "linkedin"
    ]:

        open_website(
            "https://www.linkedin.com",
            "LinkedIn"
        )

        return True

    # ========================================================
    # INSTAGRAM
    # ========================================================

    if command in [
        "open instagram",
        "instagram"
    ]:

        open_website(
            "https://www.instagram.com",
            "Instagram"
        )

        return True

    # ========================================================
    # GITHUB
    # ========================================================

    if command in [
        "open github",
        "github"
    ]:

        open_website(
            "https://github.com",
            "GitHub"
        )

        return True

    # ========================================================
    # GMAIL
    # ========================================================

    if command in [
        "open gmail",
        "gmail"
    ]:

        open_website(
            "https://mail.google.com",
            "Gmail"
        )

        return True

    # ========================================================
    # GOOGLE SEARCH
    # ========================================================

    if command.startswith(
        "search google for"
    ):

        query = command.replace(
            "search google for",
            "",
            1
        ).strip()

        google_search(
            query
        )

        return True

    if command.startswith(
        "google search for"
    ):

        query = command.replace(
            "google search for",
            "",
            1
        ).strip()

        google_search(
            query
        )

        return True

    if command.startswith(
        "search for"
    ):

        query = command.replace(
            "search for",
            "",
            1
        ).strip()

        google_search(
            query
        )

        return True

    # ========================================================
    # YOUTUBE SEARCH
    # ========================================================

    if command.startswith(
        "search youtube for"
    ):

        query = command.replace(
            "search youtube for",
            "",
            1
        ).strip()

        youtube_search(
            query
        )

        return True

    # ========================================================
    # PLAY MUSIC
    # ========================================================

    if (
        command.startswith(
            "play music"
        )
        or command.startswith(
            "play song"
        )
        or command.startswith(
            "play "
        )
    ):

        play_music(
            command
        )

        return True

    # ========================================================
    # NEWS
    # ========================================================

    if (
        command == "news"
        or "latest news" in command
        or "read the news" in command
        or "tell me the news" in command
        or "what is the news" in command
    ):

        speak(
            "Here are the latest headlines."
        )

        news_result = get_news()

        # get_news() returns None on success because it speaks
        # each headline. On failure it returns an error message.
        if news_result:

            speak(
                news_result
            )

        return True

    # ========================================================
    # JOKE
    # ========================================================

    if (
        "tell me a joke" in command
        or command == "joke"
    ):

        speak(
            "Why do programmers prefer dark mode? "
            "Because light attracts bugs."
        )

        return True

    # ========================================================
    # CALCULATOR
    # ========================================================

    if command.startswith(
        "calculate"
    ):

        answer = aiProcess(
            command
        )

        speak(
            answer
        )

        return True

    # ========================================================
    # DEFAULT -> GROQ AI
    # ========================================================

    speak(
        "Let me think."
    )

    answer = aiProcess(
        command
    )

    speak(
        answer
    )

    return True


# ============================================================
# MICROPHONE CHECK
# ============================================================

def check_microphone():

    try:

        microphones = (
            sr.Microphone.list_microphone_names()
        )

        if not microphones:

            print(
                "No microphone was detected."
            )

            return False

        print()
        print(
            "Available microphones:"
        )

        for index, name in enumerate(
            microphones
        ):

            print(
                f"  {index}: {name}"
            )

        print()

        return True

    except Exception as error:

        print(
            "Microphone check failed:"
        )

        print(error)

        return False


# ============================================================
# LISTEN FOR WAKE WORD
# ============================================================

def listen_for_wake_word():
    """
    Listen for the word 'Jarvis'.
    """

    try:

        with sr.Microphone() as source:

            print(
                "\nListening for Jarvis..."
            )

            try:

                audio = recognizer.listen(
                    source,
                    timeout=WAKE_WORD_TIMEOUT,
                    phrase_time_limit=WAKE_WORD_PHRASE_TIME
                )

            except sr.WaitTimeoutError:

                return None

        try:

            text = recognizer.recognize_google(
                audio
            )

            text = text.lower().strip()

            print(
                f"Heard: {text}"
            )

            return text

        except sr.UnknownValueError:

            print(
                "Could not understand speech."
            )

            return None

        except sr.RequestError as error:

            print(
                "Google speech recognition error:"
            )

            print(error)

            return None

    except Exception as error:

        print(
            "Microphone/wake-word error:"
        )

        print(error)

        return None


# ============================================================
# LISTEN FOR COMMAND
# ============================================================

def listen_for_command():
    """
    Listen for a command after the user says only "Jarvis".
    """

    try:

        with sr.Microphone() as source:

            print()
            print(
                "Jarvis is active..."
            )

            print(
                "Listening for your command..."
            )

            time.sleep(
                0.3
            )

            try:

                audio = recognizer.listen(
                    source,
                    timeout=COMMAND_TIMEOUT,
                    phrase_time_limit=COMMAND_PHRASE_TIME
                )

            except sr.WaitTimeoutError:

                print(
                    "No command detected."
                )

                speak(
                    "I didn't hear a command."
                )

                return None

        try:

            command = recognizer.recognize_google(
                audio
            )

            command = command.lower().strip()

            print(
                f"You said: {command}"
            )

            return command

        except sr.UnknownValueError:

            print(
                "Could not understand command."
            )

            speak(
                "Sorry, I couldn't understand that."
            )

            return None

        except sr.RequestError as error:

            print(
                "Speech recognition service error:"
            )

            print(error)

            speak(
                "The speech recognition service is unavailable."
            )

            return None

    except Exception as error:

        print(
            "Command microphone error:"
        )

        print(error)

        return None


# ============================================================
# STARTUP
# ============================================================

def startup():

    print()
    print("=" * 60)
    print(
        "              JARVIS AI VOICE ASSISTANT"
    )
    print("=" * 60)
    print()

    print(
        "Checking configuration..."
    )

    if GROQ_API_KEY:

        print(
            "✓ Groq API key loaded."
        )

    else:

        print(
            "⚠ Groq API key not found."
        )

    if NEWS_API_KEY:

        print(
            "✓ NewsAPI key loaded."
        )

    else:

        print(
            "⚠ NewsAPI key not found."
        )

    print(
        "✓ Pygame speech system ready."
    )

    print(
        "✓ Default weather city: "
        f"{DEFAULT_WEATHER_CITY}"
    )

    if not check_microphone():

        print(
            "WARNING: Microphone may not be available."
        )

    # Calibrate microphone for current room noise.
    try:

        print(
            "Calibrating microphone for 1 second..."
        )

        with sr.Microphone() as source:

            recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

        print(
            "Microphone calibrated. "
            "Energy threshold: "
            f"{recognizer.energy_threshold:.0f}"
        )

    except Exception as error:

        print(
            "Microphone calibration warning:"
        )

        print(error)

    print()

    speak(
        "Jarvis is initializing."
    )

    time.sleep(
        0.5
    )

    speak(
        "Systems are ready."
    )

    print()

    print(
        "Say 'Jarvis' to activate me."
    )

    print(
        "Say 'exit' or 'shutdown' to close me."
    )

    print()


# ============================================================
# CLEANUP
# ============================================================

def cleanup():

    print()
    print(
        "Cleaning up JARVIS..."
    )

    # Stop pygame.
    try:

        if pygame_initialized:

            pygame.mixer.music.stop()

            try:

                pygame.mixer.music.unload()

            except Exception:
                pass

            pygame.mixer.quit()

    except Exception:
        pass

    # Stop pyttsx3.
    try:

        if (
            PYTTSX_AVAILABLE
            and pyttsx_engine
        ):

            pyttsx_engine.stop()

    except Exception:
        pass

    print(
        "JARVIS stopped successfully."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    startup()

    running = True

    while running:

        try:

            # Wait for wake word.
            heard_text = (
                listen_for_wake_word()
            )

            if not heard_text:
                continue

            # Check for "Jarvis".
            if (
                ASSISTANT_NAME.lower()
                in heard_text
            ):

                print()
                print(
                    "Wake word detected!"
                )

                wake_word = (
                    ASSISTANT_NAME.lower()
                )

                # Everything after "Jarvis" is the command.
                command = heard_text.split(
                    wake_word,
                    1
                )[1].strip(
                    " ,.!?"
                )

                if command:

                    print(
                        "Command after wake word: "
                        f"{command}"
                    )

                    running = process_command(
                        command
                    )

                else:

                    # User said only "Jarvis".
                    speak(
                        "Yes, I am listening."
                    )

                    command = (
                        listen_for_command()
                    )

                    if command:

                        running = process_command(
                            command
                        )

        except KeyboardInterrupt:

            print()
            print(
                "Ctrl+C detected."
            )

            speak(
                "Goodbye."
            )

            running = False

        except Exception as error:

            print()
            print(
                "Unexpected error:"
            )

            print(error)

            print()

            time.sleep(
                1
            )

    cleanup()


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
