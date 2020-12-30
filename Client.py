import socket
import threading
import time
from Color import bcolors
import msvcrt

list_of_clients = []

MAGIC_COOKIE = [0xfe, 0xed, 0xbe, 0xef]

MESSAGE_TYPE = [0x2]

BUFFER_SIZE = 1024

TEAM_NAME = b'GiveUs100Please\n'

stop = False


def listen_to_offer_and_connect():
    print('Client started, listening for offer requests...')
    # first we listen and looking for server that offer us to play under their host!
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client_socket.bind(("", 13117))
    # here we are waiting for a server to sand us it's special form of offer message
    data, addr = client_socket.recvfrom(8)
    # if we got an OK message we procceed to check it's headers
    if data:
        # Magic cookie (4 bytes): 0xfeedbeef. The message is rejected if it doesn’t start with this cookie
        magic_cookie = data[0:4]
        # Message type (1 byte): 0x2 for offer. No other message types are supported
        message_type = data[4:5]
        # Server port (2 bytes): The port on the server that the client is supposed to connect to over TCP
        port = data[5:7]
        port = int.from_bytes(port, byteorder='big', signed=False)
        ip, _ = addr
        address = (ip, port)

        print('Received offer from ' + ip + ' attempting to connect...')

        if magic_cookie == bytearray(MAGIC_COOKIE) and message_type == bytearray(MESSAGE_TYPE):
            # after getting the message and figuring it's correct headers we procceed
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(address)
            client_socket.send(TEAM_NAME)
            return client_socket


if __name__ == '__main__':
    try:
        stop = False
        client_socket = listen_to_offer_and_connect()
        # we chack if a client socket is correct and procceed
        if client_socket:
            data = client_socket.recv(BUFFER_SIZE)
            print(data.decode('utf-8'))
            # listen_thread = threading.Thread(target=listen_until_end, name='listenthread', args=(client_socket, ))
            # listen_thread.start()
            client_socket.setblocking(False)
            while not stop:
                try:
                    data = client_socket.recv(BUFFER_SIZE)
                    if len(data) == 0:
                        stop = True
                        print('server have been disconnected!')
                    print(data.decode('utf-8'))
                except Exception as e:
                    pass
                # reciveing characters from the user and send it to the server in order to win!
                input_char = msvcrt.getch()
                # input_char = 'c'.encode('utf-8')
                client_socket.send(input_char)
                print(input_char.decode('utf-8'))
    except:
        pass
