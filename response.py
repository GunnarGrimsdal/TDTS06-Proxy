FILTER_TAGS = [
    b'SpongeBob', b'Britney Spears', b'Paris Hilton', b'Norrk&oumlping'
]


class Response:

    # Return a list of tuples
    # Example [(header_element_name, header_element_value), ...]
    def get_header_list(self):
        header_data = []
        for data in self.get_header().split(b'\r\n'):
            header_data.append(
                (data.split(b" ")[0], b' '.join(data.split(b' ')[1:])))
        return header_data

    # Get header as byte string
    def get_header(self):
        return self.byte_data.split(b'\r\n\r\n')[0]

    # Get payload as a byte string (HTML or file)
    def get_payload(self):
        if len(self.byte_data.split(b'\r\n\r\n')) > 1:
            return self.byte_data.split(b'\r\n\r\n')[1]
        else:
            return None

    # Get value from a specific header element
    def get_header_element(self, header_name):
        for element_name, element in self.get_header_list():
            if element_name == header_name:
                return element
        return None  # If Host: not found

    # Return true if the Content-Type starts with text
    def is_text(self):
        con_typ = self.get_header_element(b'Content-Type:')
        return con_typ .startswith(b'text') if con_typ else False

    # Add data to the internal byte string
    def add(self, msg):
        self.byte_data += msg

    # Set the header element name and value in form of byte strings
    # and add theme to the byte string self.byte_data
    def set_header_element(self, header_name, header_value):
        header = self.get_header_list()
        for index in range(len(header)):
            if header[index][0] == header_name:
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

    # Sets the payload
    def set_payload(self, payload):
        self.byte_data = self.get_header() + b'\r\n\r\n' + payload

    # Checks if the payload contains any forbidden keywords
    def is_acceptable(self):
        for tag in FILTER_TAGS:
            if tag in self.get_payload():
                return False
        return True

    def __init__(self, byte_data=b''):
        self.byte_data = byte_data
