import socket
import threading
import time
import random
import select
from scapy.arch import get_if_addr
from Color import bcolors
from Group import Group
from Player import Player
from statistics import mode 


groups = [Group(), Group()]
MAGIC_COOKIE = [0xfe, 0xed, 0xbe, 0xef]
MESSAGE_TYPE = [0x2]
PORT_NUM = [0x13, 0x8d]
BUFFER_SIZE = 32
NUMBER_OF_SECONDS_TO_WAIT = 10

init_part_ended = False
game_part_ended = False


def make_offer():
    global init_part_ended
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    message = bytearray(MAGIC_COOKIE + MESSAGE_TYPE + PORT_NUM)
    for i in range(NUMBER_OF_SECONDS_TO_WAIT):
        server_socket.sendto(message, ('<broadcast>', 13117))
        print(bcolors.HEADER + 'sending an offer!')
        time.sleep(1)
    init_part_ended = True
    print(bcolors.OKGREEN + 'let the game begin ')
    sand_welcome_messages()


def client_handler(client_conn, addr):
    player_name = client_conn.recv(BUFFER_SIZE)
    if player_name:
        player_name = player_name.decode("utf-8")
        print(bcolors.OKGREEN + 'new player just join with name: ' + player_name)
        group_number = int(2 * random.random())
        player = Player(client_conn, addr, player_name)
        groups[group_number].add_player(player)
        client_conn.setblocking(False)
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


def recive_new_connections():
    print(bcolors.OKBLUE + bcolors.UNDERLINE + 'Server started,\n listening on IP address 172.1.0.4...')
    TCP_IP = get_if_addr("eth1")    #socket.gethostbyname(socket.gethostname())
    TCP_PORT = 5005
    BUFFER_SIZE = 20
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((TCP_IP, TCP_PORT))
    server_socket.listen()
    server_socket.settimeout(0.1)
    while not init_part_ended:
        try:
            conn, addr = server_socket.accept()
            client_thread = threading.Thread(target=client_handler, args=(conn, addr))
            client_thread.start()
        except:
            pass
    print('init part is done!!')


def broadcast_all(message):
    for group in groups:
        group.broadcast(message)


def sand_welcome_messages():
    message = 'Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n' + groups[
        0].print_players() + 'Group 2:\n==\n' + groups[
                  1].print_players() + 'Start pressing keys on your keyboard as fast as you can!!\n'
    broadcast_all(message)

def most_frequent(List): 
    counter = 0
    num = List[0] 
      
    for i in List: 
        curr_frequency = List.count(i) 
        if(curr_frequency> counter): 
            counter = curr_frequency 
            num = i 
  
    return num 

def get_most_typed_char():
    history = groups[0].get_history() + groups[1].get_history()
    char = mode(history)
    return (historycount(char), (char))


def print_result():
    group1_score = str(groups[0].get_group_score())
    group2_score = str(groups[1].get_group_score())

    winning_group = 1 if (group2_score < group1_score) else 2 if (group2_score > group1_score) else 0

    message = ''
    if winning_group == 0:
        message = 'its a draw guys! everybody wins'
    else:
        message = 'Game over!\nGroup 1 typed in ' + str(group1_score) + ' characters. Group 2 typed in ' + str(group2_score) + ' characters.\n' + 'group ' + str(winning_group) + ' wins! Congratulations to the winners:\n==\n' + \
                  groups[winning_group - 1].print_players()

    #print some statistics
    avarage_char_typed = (group1_score + group2_score) / NUMBER_OF_SECONDS_TO_WAIT
    most_typed_char, number_of_instances = get_most_typed_char()

    message += bcolors.OKBLUE + 'SOME STATISTICS:\nthe avarage charachters per seconds: ' + str(avarage_char_typed) + '\nthe most typed character is: ' + most_typed_char + '\nit was typed: ' + str(number_of_instances)
    broadcast_all(message)

    print('group1 scored: ' + group1_score + '\ngroup2 scored: ' + group2_score)


if __name__ == '__main__':
    t1 = threading.Thread(target=make_offer, name='offer maker')
    t2 = threading.Thread(target=recive_new_connections)
    t2.start()
    t1.start()
    t1.join()
    t2.join()
    time.sleep(NUMBER_OF_SECONDS_TO_WAIT)
    print_result()
    game_part_ended = True
