import customtkinter
from client import *
import threading
import time
import copy

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")
    
class MyFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # add widgets onto the frame...
        self.frame = customtkinter.CTkFrame(self,width=200, height=200, corner_radius=5, bg_color="grey")
        self.frame.grid(row=0, column=0, padx=20)



class App(customtkinter.CTk):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.title(self.name)
        self.geometry("1280x720")
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._reciever_thread = threading.Thread(target=self.__reciever, daemon=True)
        self._sender_thread = threading.Thread(target=self.__sender, daemon=True)

        self._choice = ""

        self._join_chatroom_thread = None

        self._input_box_data = ""

        #Textbox
        self.textbox = customtkinter.CTkTextbox(master=self, width=1000, height=500, font = ("Arial", 20), text_color="white",wrap = "word", state = "disabled")
        self.textbox.place(relx = 0.1, rely = 0.1, anchor = "nw")
        
        #Send Button
        self.message_frame = customtkinter.CTkFrame(self,width=1280, height=70, corner_radius=1, bg_color="grey")
        self.message_frame.pack(side = "bottom", padx=20, pady=10)
        self.button = customtkinter.CTkButton(master=self.message_frame, text="Send", command=self.button_callback, width = 200, height = 50, font = ("Arial", 20), text_color="white", fg_color="grey")
        self.button.place(relx = 0.825, rely = 0.89, anchor = "sw")

        #Exit Button
        self.button = customtkinter.CTkButton(master=self, text="EXIT", command=self.exit_button, width = 100, height = 50, font = ("Arial", 20), text_color="white", fg_color="grey")
        self.button.place(relx = 0.975, rely = 0.025, anchor = "ne")

        #User Input
        self.text_entry = customtkinter.CTkEntry(master=self.message_frame, placeholder_text= "Input Message Here", width = 1000, height = 50, font = ("Arial", 20), text_color="white", fg_color="grey")
        self.text_entry_frame = customtkinter.CTkFrame(self)
        self.text_entry.place(relx = 0.01, rely = 0.89, anchor = "sw")
    
    def __reciever(self):
        self.server_listen()
    
    def __sender(self):
        self.start_options()


    def button_callback(self):
        data = self.text_entry.get()
        self.text_entry.delete(0, len(data))
        self._input_box_data = data


    def read_input_data(self):
        data = ""
        while(data == ""):
            data = self._input_box_data
            time.sleep(0.1)
        
        self._input_box_data = ""
        return data
    
    def start_options(self):
        #send message to server here
        data = self.read_input_data()

        if(data == "1" or self._choice == "1"):
            self._choice = data
            message = {"REPORT_REQUEST_FLAG": 1}
            self._socket.send(json.dumps(message).encode())
            response = json.loads(self._socket.recv(1024).decode())

            if("REPORT_RESPONSE_FLAG" not in response):
                    self.display_text("Error, REPORT_RESPONSE_FLAG not in message.")
                    exit()
            
            try:
                number = response["NUMBER"]
                payload = response["PAYLOAD"]

                self.display_text(f"There are {number} active users in the chatroom.")
                iterator = 0

                while(iterator <= number - 1):
                        self.display_text(f"{iterator + 1}. {payload[iterator]['username']} at IP: {payload[iterator]['ip']} and port: {payload[iterator]['port']}")
                        iterator+=1
            
            except Exception as e:
                self.display_text(e)
          
        elif(data == "2" or self._choice == "2"):
            self._choice = data
            self.display_text("\nWhat is your username: {}".format(self.name))
            username = self.name

            output_payload = {"JOIN_REQUEST_FLAG": 1, "USERNAME": username}    
            self._socket.send(json.dumps(output_payload).encode())
            response = json.loads(self._socket.recv(1024).decode())

            # Error handling
            if("JOIN_REJECT_FLAG" in response):
                    self.display_text(f"Error, JOIN_REJECT_FLAG, {response['PAYLOAD']}.")
                    exit()
            if("JOIN_ACCEPT_FLAG" not in response):
                    self.display_text("Error, JOIN_ACCEPT_FLAG not in response")
                    exit()
                
                # Successful join of chatroom
            if(self._join_chatroom_thread == None):
                self._join_chatroom_thread = Thread(target=self.join_chatroom, args=(username, response['PAYLOAD'], self._socket))
                self._join_chatroom_thread.start()

            #self.join_chatroom(username=username, history=response['PAYLOAD'], server_socket=self._socket)
            pass
        
        elif(data == "3" or self._choice == "3"):
            self._choice = data
            pass
    



    def server_listen(self, server_socket):
        while True:
            # Constantly listens for incoming message from a client
            data = server_socket.recv(1024).decode()

            # If the socket connection was closed by the client, stop the thread
            if not data:
                self.display_text("\nServer disconnected!")
                return
            
            msg = json.loads(data)

            # If the server has send a quit response
            if("QUIT_RESPONSE_FLAG" in msg):
                server_socket.close()
                os._exit(0)
            
            if("USER_QUIT_FLAG" in msg):
                username = msg["PAYLOAD"]["username"]
                self.display_text(f"\n[SERVER]: User {username} has left the chatroom.")
                continue
            
            if("USER_JOINED_FLAG" in msg):
                username = msg["PAYLOAD"]["username"]
                time = msg["PAYLOAD"]["time"]
                self.display_text(f"\n[{time}] Server: {username} has joined the chatroom.")
                continue

            # If the server has send an attachment
            if("ATTACHMENT_FLAG" in msg):
                username = msg["PAYLOAD"]["username"]
                filename = msg["FILENAME"]
                content = msg["PAYLOAD"]["content"]
                time = msg["PAYLOAD"]["time"]

                # Download the file into the downloads folder
                with open(f"C:\\Users\\yasha\\Downloads\\{filename}", 'w') as f:
                    f.write(content)

                # self.display_text the content of the downloaded file
                with open(f"C:\\Users\\yasha\\Downloads\\{filename}", 'r') as f:
                    self.display_text(f"[{time}] {username}: {f.read()}")
                continue
            
            username = msg["PAYLOAD"]["username"]
            content = msg["PAYLOAD"]["content"]
            time = msg["PAYLOAD"]["time"]
            self.display_text(f"\n[{time}] {username}: {content}")
    
    def join_chatroom(self, username, history, server_socket):
        self.display_text("\tThe server welcomes you to the chatroom.")
        self.display_text("\tType lowercase 'q' and press enter at any time to quit the chatroom.")
        self.display_text("\tType lowercase 'a' and press enter at any time to upload an attachment to the chatroom.\n\n")

        self.display_text("----------Chat History----------")   
        for message in history:
            self.display_text(f"[{message['time']}] {message['username']}: {message['content']}")
        self.display_text("------Chat History Finished------")   


        # Create a thread that listens for the server's messages
        t = Thread(target=self.server_listen, args=(server_socket,))
        # Make a daemon so thread ends when main thread ends
        t.daemon = True
        t.start()

       
        while True:
                user_input = self.read_input_data()
                # If the client is attempting to quit
                if(user_input == 'q'):
                    output_payload = {"QUIT_REQUEST_FLAG": 1, "USERNAME": username}
                    server_socket.send(json.dumps(output_payload).encode())
                    continue

                # If the client wants to send an attachment
                if(user_input == 'a'):
                    filename = input("Please enter the file path and name: ")
                    try:
                        ext = filename.split(".")[1]
                        
                        # check if the file is image or text
                        if(ext == "png"):
                            with open(f"attachments/{filename}", 'wb') as f:
                                pass
                            
                            pass
                        
                        elif(ext == "txt"):
                            with open(f"attachments/{filename}", 'r') as f:
                                attachment = f.read()
                                output_payload = {"ATTACHMENT_FLAG": 1, "FILENAME": filename, "USERNAME": username, "PAYLOAD": attachment}
                                server_socket.send(json.dumps(output_payload).encode())

                    except Exception as e:
                        self.display_text("Error, that file does not exist.")
                        self.display_text(e)
                    continue

                # Otherwise, just simply send a message with the default payload format
                message = {"USERNAME": username, "PAYLOAD": user_input}
                server_socket.send(json.dumps(message).encode())
                pass
    
    def display_text(self,message):
        self.textbox.configure(state="normal")
        self.textbox.insert('end',message)
        self.textbox.configure(state="disabled")

    def exit_button(self):
        self.destroy()
        exit()

    def setup(self):
        # Write basic to screen
        self.display_text("Please select one of the following options:\n")
        self.display_text("1. Get a report of the chatroom from the server.\n")
        self.display_text("2. Request to join the chatroom.\n")
        self.display_text("3. Quit the program.")

        host_name = socket.gethostbyname(socket.gethostname())
        self.display_text("Connecting to" + host_name + str(18000) +  "...")
        self._socket.connect((host_name, 18000))
        self.display_text("Connected.")

        self._sender_thread.start()

    def run(self):
        self.setup()
        self.mainloop()    

app = App("JOSHUA")

#USE IN CODE
#USE INSTEAD OF self.display_text

#USE IN MAIN TO START GUI
#app.update_idletasks()
#app.update()

app.run()
