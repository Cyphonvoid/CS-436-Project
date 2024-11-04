import json
import time

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
            'TIME_STAMP':None
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

    def get_request_message(self):
        # Get the message content
        return self._message_headers['PAYLOAD']

    def get_request_body(self):
        # Gets the request body as python dict
        return self._message_headers
    
    def unpack_request_body(self, message_body):
        # Re constructs json data into message body and python dictionary to send data
        body = json.loads(message_body)
        self._message_headers = body

    def pack_request_body(self):
        # Constructs the request body into sendable and compiled json data
        message_string = json.dumps(self._message_headers)
        return message_string