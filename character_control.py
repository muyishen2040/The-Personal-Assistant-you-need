import http.server
import threading
import time

actions = [
    "Happy1",
    "Happy2",
    "Happy3",
    "Angry1",
    "Angry2",
    "Angry3",
    "Sad1",
    "Sad2",
    "Sad3",
]

characters = [
    "Jotaro",
    "Miku"
]

commands = [
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
]

PORT = 25002

response = "None"

class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global response
        self.send_response(200)
        # self.send_header('Content-type', 'text/plain')
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Headers", "Accept, X-Access-Token, X-Application-Name, X-Request-Sent-Time")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Origin", "*")

        self.end_headers()
        self.wfile.write(response.encode())
        print(f"Sent response: {response}")
        response = "None"

def run_http_server():
    with http.server.HTTPServer(("", PORT), HTTPRequestHandler) as httpd:
        print("Serving at port", PORT)
        httpd.serve_forever()
        httpd.server_close()
        
def check_command(command):
    if command.startswith("action"):
        return command.split(":")[1] in actions
    elif command.startswith("character"):
        return command.split(":")[1] in characters
    else:
        return False


if __name__ == "__main__":
    # Start the server
    server = threading.Thread(target=run_http_server)
    server.daemon = True
    server.start()


    idx = 0
    while True:

        command = commands[idx]
        idx = (idx + 1) % len(commands)
        while not check_command(command):
            print("Invalid command")
            command = commands[idx]

        response = command
        time.sleep(8)
