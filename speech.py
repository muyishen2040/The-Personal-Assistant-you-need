import speech_recognition as sr
import pyttsx3
import openai
from gtts import gTTS
import os
from pydub import AudioSegment
from pydub.playback import play
import socket
import os
import smbus
import time


bus = smbus.SMBus(1)
address = 0x04

def writeNumber(value):
    bus.write_byte(address, value)
    return -1

def readNumber():
    number = bus.read_byte(address)
    return number


local_port = 9009
remote_port = 9009
buffer_size = 1024

message_to_send = 'Running a Bash command from Python can be done using the subprocess module, which allows you to spawn new processes, connect to their input/output/error pipes, and obtain their return codes. Here'

processed_file = 'processed_file.wav'
EOF_marker = b"<EOF>"


openai.api_key = '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'


def ask_chatgpt(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        max_tokens=20,
        temperature=0.9,
        messages=messages
    )
    
    return response.choices[0].message.content


def speech_to_text(language='zh-CN'):
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Say something...")
        recognizer.adjust_for_ambient_noise(source)
        
        try:
            audio = recognizer.listen(source, timeout=1)
        except:
            print("No voice input")
            return ""

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)#, language=language)# 
        return text
    except:
        print("Could not understand audio")
        return ""
    

# def text_to_speech(text, lang="zh-TW"):
#     try:
#         tts = gTTS(text=text, lang=lang)
#         tts.save("output.mp3")
#         os.system("play " + "output.mp3" + " tempo 1.6")
#         # os.system("mpg321 output.mp3")  # You may need to install mpg321 or use another player
#         os.remove("output.mp3")
#     except Exception as e:
#         print(f"Error: {e}")


def text_to_speech_client(text):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('127.0.0.1', local_port))

        print(text)
        message_to_send = text
        # Send the WAV file to the server
        s.sendall(message_to_send.encode())

        # Wait for the server to process and send the file back
        with open(processed_file, 'wb') as f:
            file_data = bytearray()
            while True:
                data = s.recv(buffer_size)
                if EOF_marker in data:
                    file_data.extend(data.replace(EOF_marker, b""))
                    break
                file_data.extend(data)
            f.write(file_data)
        
        print("WAV file sent and processed WAV file received.")
        
        try:
            
            os.system("play " + processed_file + " tempo 1")
            os.remove(processed_file)
        except Exception as e:
            print(f"Error: {e}")
        


if __name__ == "__main__":
    
    messages=[
            {"role": "system", "content": "If I want you to turn on green light reply A ,Blue light reply B ,Red Light, reply C ,If turn off reply Okay. If change mode reply Z ,Else just reply the question"},
     {"role": "user", "content": None}
    ]

    while True:

        prompt = speech_to_text()

        if prompt == "":
            continue

        print('Question:', prompt)

        writeNumber(1)

        # messages.append({"role": "user", "content": prompt})
        messages[1]["content"] = prompt
        

        ret = ask_chatgpt(messages)

        print('Answer:', ret)

        if ret == "A":
            # time.sleep(0.5)
            writeNumber(3)
            text_to_speech_client("The green light is on")
            continue
        elif ret == "B":
            # time.sleep(0.5)
            writeNumber(4)
            text_to_speech_client("The blue light is on")
            continue
        elif ret == "C":
            # time.sleep(0.5)
            writeNumber(5)
            text_to_speech_client("The red light is on")
            continue
        elif ret == "Z":
            # time.sleep(0.5)
            writeNumber(9)
            text_to_speech_client("The mode has changed")
            continue

        # messages.append({"role": "assistant", "content": ret})

        # text_to_speech(ret)

        text_to_speech_client(ret)

        writeNumber(2)


    




