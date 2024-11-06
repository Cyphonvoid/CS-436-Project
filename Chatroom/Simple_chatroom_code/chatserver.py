import socket
from threading import Thread
#from chatclient import user
number_clients = 0





# Create and Bind a TCP Server Socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_name = socket.gethostname() 
#socket.gethostname() "localhost"
s_ip = socket.gethostbyname(host_name)
port = 18000
serverSocket.bind((host_name, port))

# Outputs Bound Contents
print("Socket Bound")
print("Server IP: ", s_ip, " Server Port:", port)

# Listens for 3 Users
serverSocket.listen(3)

# Creates a set of clients
client_List = set()
usernames = set()
msgList = []

# Function to constantly listen for an client's incoming messages and sends them to the other clients
def clientWatch(cs):
    adminFlag = 0
    while True:
        try:
            # Constantly listens for incoming message from a client

            msg = cs.recv(1024).decode()

            if msg == "admin":
                adminFlag = 1
                print("Admin Connected")
                adminMsg = "Type 'viewall' to view all recorded messages"
                cs.send(adminMsg.encode())

                continue
            
            # if q is entered remove the client from the client list and close connection
            if msg == "q":
                print("Client Disconnected")
                client_List.remove(cs)
                number_clients = number_clients - 1
                socket.REPORT_REQUEST_FLAG
                cs.close()
            
                continue

            if str(msg[0:17]) == "JOIN_REQUEST_FLAG":
                check = 0
                newName = str(msg[18:])
                if 1 < 3:
                    for us in usernames:
                        if newName == us:
                            check = 1
                            cs.send(us.encode())
                    if check == 0:
                        user = msg[18:]
                        usernames.add(user)
                        cs.send(("Welcome to the chat room.").encode())
                    else:
                        cs.send(("The server rejects the join request. The chatroom has reached its maximum capacity.").encode())
                else:
                    cs.send("The server rejects the join request. Another user is using this username.".encode())
            
                break
        
        except Exception as e:
            print("Error")
            client_List.remove(cs)

        # splits of last word of message (due to username and time being sent)
        newMsg = msg.split()
        # print(newMsg[-1])
        # checks if user is an admin and has entered 'viewall', sends messageList to the admin client
        
        if adminFlag and newMsg[-1] == "viewall":
            print("Admin Accessed Chat Log")
            cs.send(("----------Chatlog----------").encode())
            for x in msgList:
                # print(x)
                cs.send((x + "\n").encode())

            cs.send(("\n----------EndLog----------").encode())
            continue

        # Iterates through clients and sends the message to all connected clients
        msgList.append(msg)
        for client_socket in client_List:
            client_socket.send(msg.encode())

# if flag == "REPORT_REQUEST_FLAG":
#     #if number_clients > 0:
#     strnum = str(number_clients)
#     reportMsg = " There are " + strnum + " active users in the chatroom.\n"
#     counter = 1
#     for client_socket in client_List:
#         reportMsg = reportMsg + str(counter) + ". " + str(client_socket.host_name) + " at IP: " + str(client_socket.s_ip) + " and port: " + str(client_socket.port) + ".\n"
#         counter = counter + 1
#     #else:
#     #reportMsg = " There are no active users in the chatroom.\n"
#     client_socket.send(reportMsg.encode())





while True:
    # Continues to listen / accept new clients
    client_socket, client_address = serverSocket.accept()
    print(client_address, "Connected!")

    #Adds the client's socket to the client set
    
    client_List.add(client_socket)
    number_clients = number_clients + 1
    
    
    # Create a thread that listens for each client's messages
    t = Thread(target=clientWatch, args=(client_socket,))

    # Make a daemon so thread ends when main thread ends
    t.daemon = True

    t.start()

# Close out clients
for cs in client_List:
    cs.close()
# Close socket
s.close()

