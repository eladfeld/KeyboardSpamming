class Player:
    def __init__(self, conn, address, name):
        self.conn = conn
        self.addr = address
        self.name = name
        self.score = 0
        self.history = []

    def player_pushed(self, char):
        print('oh yeah')
        self.history.append(char)
        self.score += 1

    def get_score(self):
        return self.score

    def get_name(self):
        return self.name

    def send(self, message):
        try:
            self.conn.send(message.encode('utf8'))
        except:
            pass
