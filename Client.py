import socket
from Color import bcolors
import select
import tty
import sys


MAGIC_COOKIE = [0xfe, 0xed, 0xbe, 0xef]
MESSAGE_TYPE = [0x2]
BUFFER_SIZE = 1024
INITIAL_BROADCAST_PORT = 13117
FORMAT_SIZE = 7
MAGIC_COOKIE_SIZE = 4
MESSAGE_TYPE_SIZE = 1
PORT_SIZE = 2
TEAM_NAME = b'GiveUs100Please\n'
stop = False


def listen_to_offer_and_connect():
    try:
        print(bcolors.HEADER + 'Client started, listening for offer requests...')
        # first we listen and looking for server that offer us to play under their host!
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client_socket.bind(('', INITIAL_BROADCAST_PORT))
        # here we are waiting for a server to sand us it's special form of offer message
        data, addr = client_socket.recvfrom(FORMAT_SIZE)
        # if we got an OK message we procceed to check it's headers
        if data:
            # Magic cookie (4 bytes): 0xfeedbeef. The message is rejected if it doesn’t start with this cookie
            magic_cookie = data[0:MAGIC_COOKIE_SIZE]
            # Message type (1 byte): 0x2 for offer. No other message types are supported
            end_of_message_type = MAGIC_COOKIE_SIZE + MESSAGE_TYPE_SIZE
            message_type = data[MAGIC_COOKIE_SIZE:end_of_message_type]
            # Server port (2 bytes): The port on the server that the client is supposed to connect to over TCP
            port = data[end_of_message_type:FORMAT_SIZE]
            port = int.from_bytes(port, byteorder='big', signed=False)
            ip, _ = addr
            address = (ip, port)
            print(bcolors.HEADER + 'Received offer from ' + ip + ' attempting to connect...')
            if magic_cookie == bytearray(MAGIC_COOKIE) and message_type == bytearray(MESSAGE_TYPE):
                # after getting the message and figuring it's correct headers we procceed
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect(address)
                client_socket.send(TEAM_NAME)
                return client_socket
    except Exception as e:
        pass


if __name__ == '__main__':
    while True:  
        try:
            stop = False
            #turn on state one and wait for a connection when state two is over in this function
            client_socket = listen_to_offer_and_connect()
            # we chack if a client socket is correct and procceed
            if client_socket:
                data = client_socket.recv(BUFFER_SIZE)
                print(bcolors.OKGREEN + data.decode('utf-8'))
                #set the socket to be non blocking in order to be able to read and write simultaneously
                client_socket.setblocking(False)
                #give us the abilty to read user input when a key is pressing rather then when enter is pushed
                tty.setcbreak(sys.stdin)
                #game main loop
                while not stop:
                    try:
                        data = client_socket.recv(BUFFER_SIZE)
                        #if data that the socket recive is of length 0 that means that the connection have been closed
                        if len(data) == 0:
                            stop = True
                            print(bcolors.WARNING + 'server have been disconnected!')
                        else:
                            print(bcolors.OKGREEN + data.decode('utf-8'))
                    except Exception as e:
                        pass
                    # reciveing characters from the user and send it to the server in order to win!
                    input_char = ''
                    #let us know when sys.stdin buffer contain something and read that from the user in oreder to send to server
                    if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                        input_char = sys.stdin.read(1)
                        client_socket.send(input_char.encode('utf-8'))
                        print(bcolors.OKGREEN + input_char.decode('utf-8'))
        except Exception as e:
            pass
