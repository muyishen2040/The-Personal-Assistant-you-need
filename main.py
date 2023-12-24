import speech_recognition as sr
import pyttsx3
from typing import Any
import openai
from gtts import gTTS
import os
from pydub import AudioSegment
from pydub.playback import play
import socket
import os
import smbus
import time
import http.server
import threading
from collections import deque
import random

actions = (
    "Happy1",
    "Happy2",
    "Happy3",
    "Angry1",
    "Angry2",
    "Angry3",
    "Sad1",
    "Sad2",
    "Sad3",
)

characters = (
    "Jotaro",
    "Miku"
)

commands = (
    "character:Jotaro",
    "action:Happy1",
    "action:Happy2",
    "action:Happy3",
    "action:Angry1",
    "action:Angry2",
    "action:Angry3",
    "action:Sad1",
    "action:Sad2",
    "action:Sad3",
    "character:Miku",
    "action:Happy1",
    "action:Happy2",
    "action:Happy3",
    "action:Angry1",
    "action:Angry2",
    "action:Angry3",
    "action:Sad1",
    "action:Sad2",
    "action:Sad3",
)
HTTP_PORT = 25002

response = "None"
light = 0

class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global response
        self.send_response(200)
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Headers", "Accept, X-Access-Token, X-Application-Name, X-Request-Sent-Time")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Origin", "*")

        self.end_headers()
        self.wfile.write(response.encode())
        # print(f"Sent response: {response}")
        response = "None"

    def log_message(self, format: str, *args: Any) -> None:
        return ""

def run_http_server():
    with http.server.HTTPServer(("", HTTP_PORT), HTTPRequestHandler) as httpd:
        print("Serving at port", HTTP_PORT)
        httpd.serve_forever()
        httpd.server_close()
        
def check_command(command):
    if command.startswith("action"):
        return command.split(":")[1] in actions
    elif command.startswith("character"):
        return command.split(":")[1] in characters
    else:
        return False



bus = smbus.SMBus(1)
address = 0x04

def writeNumber(value):
    bus.write_byte(address, value)
    return -1

def readNumber():
    number = bus.read_byte(address)
    return number


local_port = 9009
buffer_size = 1024

processed_file = 'processed_file.wav'
EOF_marker = b"<EOF>"

cur_character = "Jotaro"

openai.api_key = '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'


def ask_chatgpt(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        max_tokens=100,
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
    server = threading.Thread(target=run_http_server)
    server.daemon = True
    server.start()

    system_message = {"role": "system", 
            "content": f'You are a home assistant robot, and your character is {cur_character}. Please reply in a python dictionary format, which contains two keys: action, meassage and light. For example: {"{"}"action": Happy, "message": "Hello", "light": 0{"}"}. The available actions are: "Happy", "Angry" and "Sad". Also, you should control the lights in the room when the user asks for it. If the user does not specify you to change the light, please reply 0 for light. If the user wants you to turn on white light, reply 1; 2 for red light; 3 for green light; and 4 for blue Light. If the user wants to turn off the light, please reply 5.'}
    
    messages = deque([], maxlen=15)

    while True:
        prompt = speech_to_text()

        if prompt == "":
            continue

        print('Question:', prompt)


        messages.append({"role": "user", "content": prompt})
        
        query = list(messages)
        query.insert(0, system_message)
        ret = ask_chatgpt(query)
        
        try: 
            ret_cmd = eval(ret)

            action_cmd = "action:" + ret_cmd["action"] + str(random.randint(1, 3))
            assert check_command(action_cmd)
            response = action_cmd

            assert 0 <= int(ret_cmd["light"]) <= 5
            light = int(ret_cmd["light"])

            print('Message:', ret_cmd["message"])
            print('Action:', ret_cmd["action"])
            print('Light:', ret_cmd["light"])
        
        except Exception as e:
            print(e)
            print(query)
            print(ret)

        writeNumber(int(ret_cmd["light"]))

        messages.append({"role": "assistant", "content": ret})

        text_to_speech_client(ret_cmd["message"])
