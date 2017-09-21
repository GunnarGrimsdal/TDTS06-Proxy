import socket
import sys
from request import Request
from response import Response
import _thread as thread

BUFFER_SIZE = 1024
REQ_RED_URL = b'http://www.ida.liu.se/~TDTS04/labs/2011/ass2/error1.html'
RESP_RED_URL = b'http://www.ida.liu.se/~TDTS04/labs/2011/ass2/error2.html'


# Returns a tuple with the header as first element and eventually a part
# of the body (if it reads too much) as the second element
def read_header(sock):
    data = b''
    fragment = b''
    end_sequence = -1
    while True:
        fragment = sock.recv(BUFFER_SIZE)
        if not fragment:
            break
        data += fragment
        end_sequence = data.find(b'\r\n\r\n')
        if end_sequence != -1:
            end_sequence += 4
            break
    return data[:end_sequence], data[end_sequence:]


# Read the HTTP payload from a request or an response
def read_body(sock, length):
    data_size = 0
    data = b''
    fragment = b''
    while data_size < length:
        fragment = sock.recv(length - data_size)
        if fragment == b'':
            break
        data += fragment
        data_size += len(fragment)
    return data


# Read the HTTP payload in request or response that uses chunked data
def read_chunked_body(sock, msg_part=b''):
    END = b'\r\n'
    current_index = 0
    next_data_size = 0
    next_chunk_size_byte = b''
    data = msg_part

    while True:
        if len(data) == 0:
            data += sock.recv(BUFFER_SIZE)
        if END in data[current_index:]:
            end_index = current_index+data[current_index:].find(END)
            next_chunk_size_byte = data[current_index:end_index]
            next_data_size = int(next_chunk_size_byte, 16)
            if next_data_size == 0:
                break
            current_index += next_data_size + len(next_chunk_size_byte) + 4
        data += sock.recv(BUFFER_SIZE)
    return data


# Send data to a server and return a response
def send_and_receive(msg):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Send client message to server..
    print("Sending to {}".format(msg.get_host()))

    # Connecting to webserver
    address, port = msg.get_host()
    #If no port or address exists there will be a None value returned
    port = port if port else 80
    address = address if address else msg.get_URL()
    server_socket.connect((address, port)) # TODO Don't assume port 80?

    # Forward the request to the server
    server_socket.sendall(msg.byte_data)

    # Read response from server
    header, payload = read_header(server_socket)
    server_msg = Response(header)
    con_leng = server_msg.get_header_element(b'Content-Length:')
    # If the package contains a payload read it
    if con_leng:
        con_leng = int(con_leng) - len(payload)
        server_msg.add(payload + read_body(server_socket, int(con_leng)))
    # If the response is chunked
    elif server_msg.get_header_element(b'Transfer-Encoding:') == b'chunked':
        server_msg.add(read_chunked_body(server_socket, payload))

    server_socket.close() # Done with socket
    # This is where the content is checked for unaccable keywords
    # If not acceptable request redirect to error page
    if server_msg.is_text() and not server_msg.is_acceptable():
        server_msg = Response(b'HTTP/1.1 301 Moved Permanently\r\n\r\n')
        server_msg.set_header_element(b'Location:', RESP_RED_URL)

    return server_msg


# Read the request from the client
def read_client(sock):
    header, payload = read_header(sock)
    client = Request(header)
    # Get Content-Length to know how how many bites to read from socket
    con_leng = client.get_header_element(b'Content-Length:')
    # If there is a Content-Length read so many bytes
    if con_leng:
        con_leng = int(con_leng) - len(payload)
        client.add(payload + read_body(sock, int(con_leng)))
    # If the request is chunked
    elif client.get_header_element(b'Transfer-Encoding:') == b'chunked':
        client.add(read_chunked_body(sock, payload))
    return client


# Run for every new connection
def connection_handler(client):
    client_msg = read_client(client)
    if len(client_msg.byte_data) < 4: # this is a bad request
        return
    # Check if the words that should be filterd are not in the url
    if client_msg.is_acceptable():
        client_msg.set_header_element(b'Connection:', b'close')
        server_msg = send_and_receive(client_msg)
    # This is where the URL is checked for unaccable keywords
    else:  # If not acceptable request redirect to error page
        server_msg = Response(b'HTTP/1.1 301 Moved Permanently\r\n\r\n')
        server_msg.set_header_element(b'Location:', REQ_RED_URL)
    client.sendall(server_msg.byte_data)
    client.close()


# The main functions starts a socket
def main():
    # If port number is not in de exec use port 13337
    port = 13337 if len(sys.argv) < 2 else int(sys.argv[1])

    ip_addr = '127.0.0.1' # Ip addess to listen to
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Close socket on thread close
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((ip_addr, port))
    sock.listen(1)
    print("Server started at {}:{}".format(ip_addr, str(port)))
    while True:
        client, address = sock.accept() # Client connected
        # Start a thread for the new client
        thread.start_new_thread(connection_handler, (client, ))


if __name__ == '__main__':
    main()
