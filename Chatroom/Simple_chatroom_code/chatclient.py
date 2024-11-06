import socket
from threading import Thread
from datetime import datetime



class Message():

    def __init__(self):
        self.REPORT_REQUEST_FLAG = 0
        self.REPORT_RESPONSE_FLAG = 0
        self.JOIN_ACCEPT_FLAG = 0
        self.NEW_USER_FLAG = 0
        self.QUIT_REQUEST_FLAG = 0
        self.QUIT_ACCEPT_FLAG = 0
        self.ATTACHMENT_FLAG = 0
        self.NUMBER = 0
        self.USERNAME = 0
        self.FILENAME = 0
        self.PAYLOAD_LENGTH = 0
        self.PAYLOAD = 0

user = Message()

# Sets the preselected IP and port for the chat server
# Eneter your machine's IP address for the host_name. Alternatively, you can enter "localhost"
host_name = "192.168.1.54"
port = 18000

# Creates the TCP socket
new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Connecting to", host_name, port, "...")
new_socket.connect((host_name, port))
print("Connected.")

choice = "0"

while choice != "3":
    choice = input("Please select one of the following options:\n1. Get a report of the chatroom from the server.\n2. Request to join the chatroom.\n3. Quit the program.\n")

    if choice == "1":
        user.REPORT_REQUEST_FLAG = 1
        flag = "REPORT_REQUEST_FLAG"
        new_socket.send(flag.encode())
        #print("Flag sent\n")
        flagReply = new_socket.recv(1024).decode()
        print(flagReply)
        


    elif choice == "2":
        # Prompts the client for a username
        print("Type lowercase 'q' at anytime to quit!")
        name = input("Enter your a username: ")
        user.USERNAME = name
        user.JOIN_ACCEPT_FLAG = 1

        joinreq = "JOIN_REQUEST_FLAG " + str(user.USERNAME)
        new_socket.send(joinreq.encode())
        user.PAYLOAD = new_socket.recv(1024).decode()
        if user.PAYLOAD == "The server rejects the join request. The chatroom has reached its maximum capacity.":
            user.JOIN_REJECT_FLAG = 1
            print(user.PAYLOAD)
        elif user.PAYLOAD == " “The server rejects the join request. Another user is using this username.":
            user.JOIN_REJECT_FLAG = 1
            print(user.PAYLOAD)
        else:
            print(user.PAYLOAD)

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
            if(3 > user.NUMBER):
                #print(user.NUMBER)
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
    
exit()
