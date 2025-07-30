import sys
import pyttsx3


def main():
    text = sys.argv[1]
    speed = int(sys.argv[2])
    voice = int(sys.argv[3])

    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[voice].id)
    engine.setProperty("rate", speed)
    engine.say(text)
    engine.runAndWait()


if __name__ == "__main__":
    main()
