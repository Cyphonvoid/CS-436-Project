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


class BaseServerActionSpace():

    def __init__(self):
        self._space_name = None
        self._current_request = None

    def request(self, request):
        self._current_request = request
        return self


class ChatroomServerActionSpace(BaseServerActionSpace):

    def __init__(self, server_reference):
        BaseServerActionSpace.__init__(self)
        self._server_reference = server_reference
    
    def _assert_is_join_request(self):
        request = self._current_request['MESSAGE']
        join_flag = request['JOIN_REQUEST_FLAG']
        
        if(join_flag == 0 or join_flag == False):
            return False
        
        elif(join_flag == 1 or join_flag == True):
            username = self._current_request['MESSAGE']['USERNAME']
            index = 0

            # If client with same username exists then close that client
            for client in self._server_reference.clients:
                if(username == client.get_identity_card()['NAME']):
                        
                        # Construct a response to tell that join was declined.
                        self._server_reference.messenger.flush()
                        self._server_reference.messenger.set_request_message("Join request declined username isn't unique")
                        packed_body = self._server_reference.messenger.pack_request_body()
                        client.send_message(packed_body)

                        # Close the connection after telling them that.
                        client.close()
                        print("[server action] {} client closed...".format(username))
                        self._server_reference.clients.pop(index)
                        index += 1

            return True
        
    def _assert_is_report_request(self):
        pass
    
    def _assert_is_quit_request(self):
        index = 0
        quit_msg = self._current_request['MESSAGE']['PAYLOAD']
        if(quit_msg == '--QUIT--'):
            for client in self._server_reference.clients:
                client.close()
                self._server_reference.clients.pop(index)
                index += 0

    
    def _assert_has_attachment(self):
        pass
    

    def _assert_remove_identical_clients(self):
        username = self._current_request['MESSAGE']['USERNAME']
        index = 0
        for client in self._server_reference.clients:
            if(username == client.get_identity_card()['NAME']):
                    client.close()
                    print("[server action] {} client closed...".format(username))
                    self._server_reference.clients.pop(index)
                    index += 1

    def _assert_close_client(self):
        pass
    
class MultiClientServer():
    AUTO = 'auto'

    def __init__(self):
        self.clients = []
        self.clients_dict = {}
        self.name = 'Server'
        self.client_listener = Listener()
        self.client_listener.attach_event_handler(self.push_new_client)
        self.client_listener.set_limit(10)
        self.current_client = None
        self.status = Status(False)
        self.input = Input(True)
        self.processing_thread = threading.Thread(target=self.__request_processing_thread__, daemon=True)
        self.messenger = Messenger()

        self.chatroom_server_action = ChatroomServerActionSpace(self)
        self.send_all_flag = False

    def __request_processing_thread__(self):
        #This thread needs to be synchronized with the main thread when deleting stuff like current client
        while self.status.get() == True:
            value = self.__process_requests()
            if(value == ERROR.RECIEVER):
                self.filter_clients(self.current_client)
                self.current_client = None
            

    def __send_beacon_responses(self, message):
        if(len(message) == 0):
            return 
        
        # If many message is an entire list
        if(isinstance(message, (list, tuple)) == True):

            for msg in message:
                username = msg['MESSAGE']['USERNAME']

                for client in self.clients:
                    card = client.get_identity_card()

                    if(card['NAME'] != username):
                        # Send the text data here
                        self.messenger.set_request_body(msg['MESSAGE'])
                        packed_msg = self.messenger.pack_request_body()
                        client.send_message(packed_msg)

                    # Send the image data from here

        # If message is just a message
        else:
            username = message['USERNAME']
            for client in self.clients:
                card = client.get_identity_card()
                if(card['NAME'] != username):
                    # Send text data here
                    self.messenger.set_request_body(msg['MESSAGE'])
                    packed_msg = self.messenger.pack_request_body(message)
                    client.send_message(packed_msg)

                # Send the image data here
    

    def __arrange_requests(self, requests):
        _dict = {}
        for req in requests: 
            _dict[req['MESSAGE']['CONVERTED_TIME']] = req
        sorted_order = sorted([key for key in _dict.keys()], reverse=False)
        ascending_order_reqs = [_dict[timestamp] for timestamp in _dict.keys()]

        return ascending_order_reqs
    

    def __perform_server_actions(self, requests):

        for request in requests:
            
            # Check for the available user names
            #self.chatroom_server_action.request(request)._assert_remove_identical_clients()

            # Check to see if there's a join request 
            self.chatroom_server_action.request(request)._assert_is_join_request()

            # Check to see if there's report request 
            #self.chatroom_server_action.request(request)._assert_is_report_request()
            
            # Check to see if user wants to quit
            #self.chatroom_server_action.request(request)._assert_is_quit_request()

            # Check to see if user wants to upload image

            # Other conditions and rules.....
            pass
        
    def __process_requests(self):
        new_requests = self.client_listener.access_message_storage().read_new_messages()

        # Make the request in ascending order of their time when they were sent
        new_requests = self.__arrange_requests(new_requests)

        # Process each message
        self.__perform_server_actions(new_requests)

        # Relay messages 
        self.__send_beacon_responses(new_requests)
        
    
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


    def push_new_client(self, client):
        self.clients.append(client)
        client.attach_callback(self.server_callback)
        print(client.remote_address(), " Connected...")
    

    def server_callback(self, client):
        address = client.remote_address()
        self.filter_clients(client)
        print(str(address) + " got disconnected....")
        self.current_client = None

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
        
    def run(self, IP, PORT):
        if(IP == MultiClientServer.AUTO):
            IP = socket.gethostbyname(socket.gethostname())

        self.status.set_true()
        self.input.open()
        self.client_listener.host_with(IP, PORT)
        self.client_listener.open()
        self.display()
        self.processing_thread.start()
        #self.recieving_thread.start()
        
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
server.run(IP=MultiClientServer.AUTO, PORT=9999)
server.close()
