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
    



