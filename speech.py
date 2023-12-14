import speech_recognition as sr
import pyttsx3
import openai


openai.api_key = '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'


def ask_chatgpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        max_tokens=20,
        temperature=0.5,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


def speech_to_text(language='zh-CN'):
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Say something...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout=2)

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)# , language=language
        return text
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Error with the service; {e}")


def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()



if __name__ == "__main__":
    
    prompt = speech_to_text()

    print('Question:', prompt)

    ret = ask_chatgpt(prompt)

    print('Answer:', ret)

    text_to_speech(ret)




