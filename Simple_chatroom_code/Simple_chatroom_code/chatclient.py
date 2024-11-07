import socket
from threading import Thread
from datetime import datetime
import json



class Message():

    def __init__(self):
        self._message_headers = {
            'REPORT_REQUEST_FLAG':None,
            'REPORT_RESPONSE_FLAG':None,
            'JOIN_ACCEPT_FLAG':None,
            'NEW_USER_FLAG':None,
            'QUIT_REQUEST_FLAG':None,
            'QUIT_ACCEPT_FLAG':None,
            'ATTACHMENT_FLAG':None,
            'NUMBER':None,
            'USERNAME':None,
            'FILENAME':None,
            'PAYLOAD_LENGTH':None,
            'PAYLOAD':None
        }
    
    def set_field(self, header, value):
        self._message_headers[header] = value

    def message(self, message):
        self._message_headers['PAYLOAD'] = message

    def compile_message(self):
        # Compile the whole message string here
        message_string = json.dumps(self._message_headers)
        return message_string
        


# Sets the preselected IP and port for the chat server
# Eneter your machine's IP address for the host_name. Alternatively, you can enter "localhost"
host_name = "100.77.26.140"
port = 18000

# Creates the TCP socket
new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Connecting to", host_name, port, "...")
new_socket.connect((host_name, port))
print("Connected.")

# Prompts the client for a username
print("Type lowercase 'q' at anytime to quit!")
name = input("Enter your a username: ")


# Thread to listen for messages from the server
def listen_for_messages():
    while True:
        message = new_socket.recv(1024).decode()
        print("\n" + message)


t = Thread(target=listen_for_messages)

t.daemon = True

t.start()

# if user is an admin send the admin name before appending time and username
if name == "admin":
    print("Welcome Administrator")
    new_socket.send(name.encode())

while True:
    # Recieves input from the user for a message
    to_send = input()

    # Allows the user to exit the chat room
    if to_send.lower() == "q":
        new_socket.send(to_send.encode())
        exit()
    # Appends the username and time to the clients message
    to_send = name + ": " + to_send
    date_now = datetime.now().strftime("[%H:%M] ")
    to_send = date_now + to_send

    # Sends the message to the server
    new_socket.send(to_send.encode())

# close the socket
new_socket.close()
