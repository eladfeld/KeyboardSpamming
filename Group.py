from functools import reduce


class Group:
    def __init__(self):
        self.list_of_players = []

    def add_player(self, player):
        self.list_of_players.append(player)

    def get_group_score(self):
        score = 0
        for player in self.list_of_players:
            score += player.get_score()
        return score
        # return reduce((lambda p1, p2: p1.get_score + p2.get_score ))

    def print_players(self):
        string = ''
        for player in self.list_of_players:
            string += player.get_name() + '\n'
        return string

    def broadcast(self, message):
        for player in self.list_of_players:
            player.send(message)

    def get_history(self):
        history = []
        for player in self.list_of_players:
            history += player.get_history()
        return history

