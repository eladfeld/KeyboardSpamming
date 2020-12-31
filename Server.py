import socket
import threading
import time
import random
from scapy.arch import get_if_addr
from Color import bcolors
from Group import Group
from Player import Player
from statistics import mode

# constants:
MAGIC_COOKIE = [0xfe, 0xed, 0xbe, 0xef]
MESSAGE_TYPE = [0x2]
PORT_NUM = [0x13, 0x8d]
BUFFER_SIZE = 32
NUMBER_OF_SECONDS_TO_WAIT = 10
TCP_PORT = 5005
INITIAL_BROADCAST_PORT = 13117
NUMBER_OF_GROUPS = 2

# global vars:
groups = [Group(), Group()]
init_part_ended = False
game_part_ended = False


# this function works in a special thread that sands offers via udp in order to inform potential players
# that a game is about to get started!
def make_offer():
    global init_part_ended
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    message = bytearray(MAGIC_COOKIE + MESSAGE_TYPE + PORT_NUM)
    for i in range(NUMBER_OF_SECONDS_TO_WAIT):
        server_socket.sendto(message, ('<broadcast>', INITIAL_BROADCAST_PORT))
        print(bcolors.HEADER + 'sending an offer!')
        time.sleep(1)
    init_part_ended = True
    sand_welcome_messages()


# this function works on a thread per client meaning that every client that connect to this server via tcp
# is hendled with by this thread when a player sendes bytes throw that connection
def client_handler(client_conn, addr):
    # first message of some client is it's name
    try:
        player_name = client_conn.recv(BUFFER_SIZE)
    except:
        pass
    # if the message have neen recived correctly we procceed
    if player_name:
        player_name = player_name.decode("utf-8")
        print(bcolors.OKGREEN + 'new player just join with name: ' + player_name)
        group_number = int(NUMBER_OF_GROUPS * random.random())
        # create a new player with the random group number and name recived from the connection
        player = Player(client_conn, addr, player_name)
        groups[group_number].add_player(player)
        # set the socket to be non blocking in order to stop the game when the flag is raised
        client_conn.setblocking(False)
        # main loop of the client looping until game_part_ended is raised
        while not game_part_ended:
            char = None
            try:
                char = client_conn.recv(1)
            except:
                pass
            if char:
                try:
                    char = char.decode('utf-8')
                    player.player_pushed(char)
                    print(char)
                except:
                    pass
        client_conn.close()


# function run by thread in order to receive new players and create a thread that handle their requests
def receive_new_connections():
    print(bcolors.OKBLUE + bcolors.UNDERLINE + 'Server started,\n listening on IP address 172.1.0.4...')
    # getting the local ip address
    tcp_ip = get_if_addr("eth1")
    # open the socket to accept new connections
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((tcp_ip, TCP_PORT))
    server_socket.listen()
    server_socket.settimeout(0.1)
    # runs until the initial state of the server have ended and we stop getting new connections
    while not init_part_ended:
        try:
            conn, addr = server_socket.accept()
            # begin a thread for each client that connects
            client_thread = threading.Thread(target=client_handler, args=(conn, addr))
            client_thread.start()
        except:
            pass
    server_socket.close()
    print('init part is done!!')


def broadcast_all(message):
    for group in groups:
        group.broadcast(message)


def sand_welcome_messages():
    message = 'Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n' + \
              groups[0].print_players() + 'Group 2:\n==\n' + groups[1].print_players() \
              + 'Start pressing keys on your keyboard as fast as you can!!\n'
    broadcast_all(message)


def get_most_typed_char():
    char = ' '
    history = groups[0].get_history() + groups[1].get_history()
    try:
        if len(history) > 0:
            char = mode(history)
    except:
        pass
    return  char, history.count(char)


# this function is called when the game part is over and sends a game-over message to all players in the game
def print_result():
    group1_score = groups[0].get_group_score()
    group2_score = groups[1].get_group_score()
    avarage_char_typed = (group1_score + group2_score) / NUMBER_OF_SECONDS_TO_WAIT
    most_typed_char, number_of_instances = get_most_typed_char()
    winning_group = 1 if (group2_score < group1_score) else 2 if (group2_score > group1_score) else 0
    message = ''
    if winning_group == 0:
        message = 'its a draw guys! everybody wins'
    else:
        message = 'Game over!\nGroup 1 typed in ' + str(group1_score) + ' characters. Group 2 typed in ' + \
                  str(group2_score) + ' characters.\n' + 'group ' + str(winning_group) \
                  + ' wins! Congratulations to the winners:\n==\n' + groups[winning_group - 1].print_players()
        # print some statistics
        message += bcolors.OKBLUE + 'SOME STATISTICS:\nthe average characters per seconds: ' + \
                   str(avarage_char_typed) + '\nthe most typed character is: ' + most_typed_char + '\nit was typed: ' \
                   + str(number_of_instances) + ' times!'
    broadcast_all(message)


if __name__ == '__main__':
    while 1:
        t1 = threading.Thread(target=make_offer, name='offer maker')
        t2 = threading.Thread(target=receive_new_connections)
        t2.start()
        t1.start()
        t1.join()
        t2.join()
        time.sleep(NUMBER_OF_SECONDS_TO_WAIT)
        print_result()
        game_part_ended = True
