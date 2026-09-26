
import speech_recognition as sr
import webbrowser
import pyttsx3
import time
import musicLibrary
import requests
from groq import Groq
from gtts import gTTS
import pygame


# API KEYS

newsapi = ""
groq_api_key = ""

# TEXT TO SPEECH

def speak_old(text):
    print("JARVIS:", text)

    engine = pyttsx3.init("sapi5")
    engine.setProperty("rate", 150)
    engine.setProperty("volume", 1.0)

    engine.say(text)
    engine.runAndWait()

    engine.stop()
    time.sleep(1)

def speak(text):
    tts =gTTS(text)
    tts.save("temp.mp3")  


    pygame.mixer.init()

    pygame.mixer.music.load("temp.mp3")

    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
     pass

    pygame.mixer.quit()


def aiProcess(command):

    try:

        # Create Groq client
        client = Groq(
            api_key=groq_api_key
        )

        print("Searching the web for current information...")

        response = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are JARVIS, a helpful voice assistant. "
                        "Give short and clear answers suitable for voice. "
                        "When the user asks about current, latest, "
                        "recent, today's, live, or up-to-date information, "
                        "use web search and provide the most current answer."
                    )
                },

                {
                    "role": "user",
                    "content": command
                }
            ],

            tools=[
                {
                    "type": "browser_search"
                }
            ],

            tool_choice="required",

            max_completion_tokens=1024
        )

        answer = response.choices[0].message.content

        print("AI:", answer)

        return answer


    except Exception as e:

        print("===================================")
        print("GROQ ERROR:")
        print(e)
        print("===================================")

        return "Sorry, I could not process your request."

# COMMAND PROCESSING

def processCommand(command):

    command = command.lower().strip()

    # GOOGLE

    if "open google" in command:

        speak("Opening Google")

        webbrowser.open(
            "https://www.google.com"
        )

    # FACEBOOK

    elif "open facebook" in command:

        speak("Opening Facebook")

        webbrowser.open(
            "https://www.facebook.com"
        )

    # YOUTUBE

    elif "open youtube" in command:

        speak("Opening YouTube")

        webbrowser.open(
            "https://www.youtube.com"
        )

    # WHATSAPP

    elif "open whatsapp" in command:

        speak("Opening WhatsApp")

        webbrowser.open(
            "https://web.whatsapp.com"
        )

    # LINKEDIN

    elif "open linkedin" in command:

        speak("Opening LinkedIn")

        webbrowser.open(
            "https://www.linkedin.com"
        )

    # INSTAGRAM

    elif "open instagram" in command:

        speak("Opening Instagram")

        webbrowser.open(
            "https://www.instagram.com"
        )

    # PLAY MUSIC

    elif command.startswith("play"):

        song = command[4:].strip()

        print("Song requested:", song)

        if song in musicLibrary.music:

            link = musicLibrary.music[song]

            speak("Playing " + song)

            webbrowser.open(link)

        else:

            speak(
                "Sorry, I don't have that song in my music library."
            )

            print("Available songs:")

            for song_name in musicLibrary.music:

                print("-", song_name)


    # NEWS

    elif "news" in command:

        speak("Getting the latest news")

        try:

            # Check NewsAPI key
            if not newsapi or newsapi == "YOUR_NEWSAPI_KEY":

                print("ERROR: NewsAPI key is missing.")

                speak("My news API key is missing.")

                return


            params = {
 
                # NewsAPI Top Headlines supports US here
                "country": "us",

                "apiKey": newsapi,

                "pageSize": 5

            }


            r = requests.get(

                "https://newsapi.org/v2/top-headlines",

                params=params,

                timeout=10

            )


            print(
                "News API Status:",
                r.status_code
            )


            data = r.json()


            print(
                "News API Response:",
                data
            )


            if r.status_code == 200:

                articles = data.get(
                    "articles",
                    []
                )


                print(
                    "Number of articles:",
                    len(articles)
                )


                if not articles:

                    speak(
                        "Sorry, I could not find any news."
                    )

                    return


                for article in articles[:5]:

                    title = article.get("title")


                    if title:

                        print(
                            "NEWS:",
                            title
                        )

                        speak(title)


            else:

                error_message = data.get(
                    "message",
                    "Unknown News API error"
                )


                print(
                    "News API Error:",
                    error_message
                )


                speak(
                    "Sorry, I could not get the news right now."
                )


        except requests.exceptions.RequestException as e:

            print(
                "News request error:",
                e
            )


            speak(
                "Sorry, I cannot connect to the news service."
            )


        except Exception as e:

            print(
                "News processing error:",
                e
            )


            speak(
                "Sorry, something went wrong while getting the news."
            )

    # AI

    else:

        print(
            "Sending command to AI:",
            command
        )

        answer = aiProcess(command)

        print(
            "AI:",
            answer
        )

        speak(answer)

# MAIN PROGRAM

if __name__ == "__main__":

    speak("Initializing Jarvis please wait...")


    while True:

        print("\nListening for Jarvis...")


        r = sr.Recognizer()


        try:

            # ----------------------------------
            # WAIT FOR WAKE WORD
            # ----------------------------------

            with sr.Microphone() as source:

                print("Listening...")

                audio = r.listen(
                    source,
                    timeout=3,
                    phrase_time_limit=3
                )


            word = r.recognize_google(audio)


            print(
                "You said:",
                word
            )


            # ----------------------------------
            # JARVIS WAKE WORD
            # ----------------------------------

            if "jarvis" in word.lower():

                speak(
                    "Yes, I am listening.."
                )


                # ----------------------------------
                # LISTEN FOR COMMAND
                # ----------------------------------

                with sr.Microphone() as source:

                    print(
                        "Jarvis is active..."
                    )


                    audio = r.listen(
                        source,
                        timeout=3,
                        phrase_time_limit=4
                    )


                command = r.recognize_google(
                    audio
                )


                print(
                    "Your command:",
                    command
                )


                processCommand(command)


        # --------------------------------------
        # NO SPEECH
        # --------------------------------------

        except sr.WaitTimeoutError:

            print(
                "No speech detected."
            )


        # --------------------------------------
        # SPEECH NOT UNDERSTOOD
        # --------------------------------------

        except sr.UnknownValueError:

            print(
                "Sorry, I could not understand you."
            )


        # --------------------------------------
        # GOOGLE SPEECH SERVICE ERROR
        # --------------------------------------

        except sr.RequestError as e:

            print(
                "Speech recognition service is unavailable."
            )

            print(
                "Error:",
                e
            )

        # OTHER ERRORS

        except Exception as e:

            print(
                "Error:",
                e
            )
