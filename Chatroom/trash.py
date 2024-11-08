import threading
from Utility import *
from Sockets import *
from Message import *
import time

CLOSE_CONNECTION = '--Close Connection--'

class Input():

    def __init__(self, status):
        self.state = Status(status)

    def user_input(self):
        if(self.state.get() == True):
            return input()
        elif(self.state.get() == False):
            return None

    def open(self):
        self.state.set_true()

    def close(self):
        self.state.set_false()


class MultiClientServer():

    def __init__(self):
        self.clients = []
        self.client_listener = Listener()
        self.client_listener.attach_event_handler(self.push_new_client)
        self.client_listener.set_limit(10)
        self.current_client = None
        self.status = Status(False)
        self.input = Input(True)
        self.reciever_thread = threading.Thread(target=self.__thread__, daemon=True)
        self.messenger = Messenger()
        self.send_all_flag = False

        self.chatroom_mode = False

    def push_new_client(self, client):
        self.clients.append(client)
        client.attach_callback(self.server_callback)
        print(client.remote_address(), " Connected...")
    
    def server_callback(self, client):
        address = client.remote_address()
        self.filter_clients(client)
        print(str(address) + " got disconnected....")
        self.current_client = None

    def __thread__(self):
        #This thread needs to be synchronized with the main thread when deleting stuff like current client
        while self.status.get() == True:
            value = self.recieve_message()
            if(value == ERROR.RECIEVER):
                self.filter_clients(self.current_client)
                self.current_client = None
            
            if(self.current_client == None):
                time.sleep(1)
                
    def select_client(self, num):

        try:
            num = int(num)
            if(num > len(self.clients)-1 or num < 0):
                return
            self.current_client = self.clients[num]
        except Exception as error:
            pass

    def close_client(self):
        self.current_client.close()

        counter = 0; 
        for client in self.clients:
            if(client == self.current_client):
                self.clients.pop(counter)
            
            counter+=1

    def display(self):
        print("         MultiClientServer")
        print("____________________________________")
        print("Hosted On:", self.client_listener.local_address())  

        
    def send_message(self, message):
        if(len(self.clients) == 0):
            print("[No Clients Available.....]")
            return None
        
        if(self.current_client == None):
            print("[Current client is None and not selected....]")
            return None
        
        if(message == 'exit'):
            self.input.close()
            self.close()
            return None
        
        try:
            if(self.current_client.state() == True):
                
                #success = self.current_client.send_message(message)
                self.messenger.set_request_message(message)
                msg = self.messenger.pack_request_body()
                success = self.current_client.send_message(msg)
                self.messenger.flush()

                if(success == ERROR.SENDER):
                    print("[Error recieved in send:", ERROR.SENDER)
                    return False
                
                print("Sent to:", self.current_client.remote_address(), message)
                return True
            else:
                return False
        except Exception as error:
            print("[Error recieved in send:", error)
            return False


    def __send_beacon_responses(self, message):
        # If many message is an entire list
        if(isinstance(message, (list, tuple)) == True):

            for msg in message:
                
                for client in self.clients:
                    
                    # Send the text data here
                    packed_msg = self.messenger.pack_request_body(msg)
                    client.send_message(packed_msg)

                    # Send the image data from here

        # If message is just a message
        else:
            username = message['MESSAGE']['USERNAME']
            for client in self.clients:
               
                # Send text data here
                packed_msg = self.messenger.pack_request_body(message)
                client.send_message(packed_msg)

                # Send the image data here

    def __process_requests(self, requests):

        for request in requests:

            # Check if the user wants to be admin

            # Check for the available user names

            # Check to see if user wants to quit

            # Other conditions and rules...
            break
           
    def listen_messages(self):
        new_requests = self.client_listener.access_message_storage().read_new_messages()
        
        # Process each message
        # self.__process_requests(new_requests)

        # Relay messages 
        self.__send_beacon_responses(new_requests)
        

    def recieve_message(self):

        if(len(self.clients) == 0 or self.current_client == None):return None
        
        message = None
        try:
            if(self.current_client.state() == True):
                message = self.current_client.recieve_message()
                if(message == ERROR.RECIEVER):
                    print("[Error recieved]:", ERROR.RECIEVER)
                    return False
                
                self.messenger.unpack_request_body(message)
                print("Recieved from:", self.current_client.remote_address(), self.messenger.get_request_message())
                self.messenger.flush()
                return message
            else:
                return False
            
        except Exception as error:
            print("[Error recieved]:", error)
            return False

    
    def __clients(self):

        #Display clients
        counter = 0; 
        for client in self.clients:
            print("client [" + str(counter) + "]")
            client.print()
            counter += 1
        
        print("Select >>", end="")
        val = input()
        self.select_client(val)

    def __disconnect_client(self, num):

        #Display clients
        counter = 0; 
        for client in self.clients:
            print("client [" + str(counter) + "]")
            client.print()
            counter += 1
        
        print("Select to disconnect >>", end="")
        val = input()
        temp = ""
        for i in range(0, len(self.clients)):
            if(i == int(val)):
                temp = self.clients.pop(i)
                break
        
        print("client dropped", temp.remote_address())


    def run(self, IP, PORT):
        self.status.set_true()
        self.input.open()
        self.client_listener.host_with(IP, PORT)
        self.client_listener.open()
        self.display()
        self.reciever_thread.start()
        
        while True:
            val = input()

            if(val == '-exit'):
                print("_______________Closed__________________")
                self.send_close_header()
                self.close_all_clients()
                self.close()
                break

            if(val == '-select'):
                self.send_all_flag = False
                self.__clients()
                continue
            elif(val == 'close'):
                self.__disconnect_client()
                pass

            if(val == '-select all'):
                self.send_all_flag = True

            if(val == '-chatroom on'):
                self.chatroom_mode = True

            elif(val == '-chatroom off'):
                self.chatroom_mode = False

            success = None
            if(self.send_all_flag == False):success = self.send_message(val)
            else: 
                for client in self.clients:
                    self.current_client = client
                    success = self.send_message(val)
                    #success = client.send_message(val)
                    
            if(success == ERROR.SENDER):
                self.filter_clients(self.current_client)
                self.current_client = None


    def filter_clients(self, _client):
        counter = 0
        for client in self.clients:
            if(client == _client):
                self.clients.pop(counter)
            counter += 1
            
    def send_close_header(self):
        for client in self.clients:
            client.send_message(CLOSE_CONNECTION)

    def close_all_clients(self):
        for client in self.clients:
            client.close()
        
    def close(self):
        self.client_listener.close()
        self.input.close()
    


class ChatroomServer():

    def __init__(self) -> None:
        pass

server = MultiClientServer()
server.run('100.77.41.62', 9999)
server.close()


'''
def send_message(self, message):
        if(len(self.clients) == 0):
            print("[No Clients Available.....]")
            return None
        
        if(self.current_client == None):
            print("[Current client is None and not selected....]")
            return None
        
        if(message == 'exit'):
            self.input.close()
            self.close()
            return None
        
        try:
            if(self.current_client.state() == True):
                
                self.messenger.set_request_message(message)
                msg = self.messenger.pack_request_body()
                success = self.current_client.send_message(msg)
                self.messenger.flush()

                if(success == ERROR.SENDER):
                    print("[Error recieved in send:", ERROR.SENDER)
                    return False
                
                print("Sent to:", self.current_client.remote_address(), message)
                return True
            else:
                return False
            
        except Exception as error:
            print("[Error recieved in send:", error)
            return False

'''

'''
class BaseServerActionSpace():

    def __init__(self):
        self._space_name = None
        self._current_request = None

    def request(self, request):
        self._current_request = request


class ChatroomServerActionSpace(BaseServerActionSpace):

    def __init__(self):
        BaseServerActionSpace.__init__(self)
    
    def _assert_is_join_request(self):
        pass

    def _assert_is_report_request(self):
        pass

    def _assert_is_quit_request(self):
        pass

    def _assert_has_attachment(self):
        pass
    
    def _perform_username_removal(self):
        pass


class ServerActions():

    def __init__(self):
        self._spaces = {}

    def space(self, name):
        return self._spaces[name]
    
    def register_space(self, name, action_space):
        self._spaces[name] = action_space
    
'''