FILTER_URL_TAGS = [
    b'SpongeBob', b'Britney Spears', b'Paris Hilton', b'Norrk??ping'
]


class Request:
    # Return a list of tuples
    # Example [(header_element_name, header_element_value), ...]
    def get_header_data(self):
        header_data = []
        for data in self.get_header().split(b'\r\n'):
            header_data.append(
                (data.split(b" ")[0], b' '.join(data.split(b' ')[1:])))
        return header_data

    # Get header as byte string
    def get_header(self):
        return self.byte_data.split(b'\r\n\r\n')[0]

    # Get payload as byte string. Used if post method
    def get_payload(self):
        if len(self.byte_data.split(b'\r\n\r\n')) > 1:
            return self.byte_data.split(b'\r\n\r\n')[1]
        else:
            return b''

    # Get value from a specific header element
    def get_header_element(self, header_name):
        for element_name, element in self.get_header_data():
            if element_name == header_name:
                return element
        return None

    # Add data to the internal byte string
    def add(self, msg):
        self.byte_data += msg

    # Get HOST as a tuple of (address, port),
    # where any can be None due to HTTP version or lack of port number
    def get_host(self):
        value = self.get_header_element(b'Host:')
        #Check if it's empty, if so return None, None
        if not value:
            return None, None

        # Return the UTF-8 string if it exists else None
        if b':' in value:
            value = value.split(b':')
            return value[0].decode('utf-8'), int(value[1])
        return value.decode('utf-8'), None

    def get_URL(self):
        return self.get_header_data()[0][1].split(b' ')[0]
    # Return True if the request is a GET request
    def is_get(self):
        return self.get_header_element(b'GET') is None

    # Return True if the request is a GET request
    def is_post(self):
        return self.get_header_element(b'POST') is None

    # Set the payload in the internal byte string
    def set_payload(self, payload):
        self.byte_data = self.get_header() + b'\r\n\r\n' + payload

    # Set the header element name and value in form of byte strings
    # and add them to the byte string self.byte_data
    def set_header_element(self, header_name, header_value):
        header = self.get_header_data()
        # Loop over all the element and see if the header_name already exists
        for index in range(len(header)):
            if header[index][0] == header_name:
                # The header exists change the value and save to byte_data
                header[index] = (header_name, header_value)
                self.__set_header(header)
                return
        # If the element is not yet in the header add it now
        header.append((header_name, header_value))
        self.__set_header(header)

    # Get a list with the data and write it to the
    # byte string self.byte_data
    def __set_header(self, data_dict):
        local_header = b''
        for key, value in data_dict:
            local_header += key + b' ' + value + b'\r\n'
        self.byte_data = local_header + b'\r\n' + self.get_payload()

    #  Check if not accepted are in the payload
    def is_acceptable(self):
        # Return the first element of the header and it's value
        # This should always be the url
        for tag in FILTER_URL_TAGS:
            # If a tag is found the content is not safe
            if tag in self.get_URL():
                return False
        return True # No tags were found

    def __init__(self, byte_data):
        self.byte_data = byte_data
