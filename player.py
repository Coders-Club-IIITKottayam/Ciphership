import numpy as np

class Player:
    def __init__(self, board_size = 5, team_name = "", cipher = ""):
        # Board Data
        self.board_size = board_size
        self.my_board = np.zeros((board_size, board_size))
        self.op_board = np.zeros((board_size, board_size))

        # Algorithm Data
        self.algo_dte = {}
        self.algo_etd = {}
        self.alpha = [chr(asc) for asc in range(97, 97 + board_size)]
        self.cipher = cipher
        self.setAlgo(cipher)

        # Game Data
        self.team_name = team_name
        self.attack = None
        self.defend = None
        self.prev_def = None
        self.points = 0
        self.state = 1
        self.game_lost = False

    def setAttack(self,move):
        self.attack = move['x'], move['y']
        self.op_board[move['x']][move['y']] = 4

    def setDefend(self,move):
        if self.prev_def != None:
            # Undo defense 
            x,y,color = self.prev_def
            self.my_board[x][y] = color
        self.defend = move['x'], move['y']
        self.prev_def = move['x'], move['y'],self.my_board[move['x']][move['y']]
        self.my_board[move['x']][move['y']] = 3


    def setAlgo(self, algo_str):
        for idx in range(self.board_size):
            self.algo_dte[self.alpha[idx]] = algo_str[idx]
            self.algo_etd[algo_str[idx]] = self.alpha[idx]

    def setShip(self, ships):
        for ship in ships:
            self.my_board[ship['x']][ship['y']] = 1

    def gch(self,ch):
        return chr(ch + ord('a'))
        
    def decrypt(self, enc_coord):
        enc_x, enc_y = enc_coord
        return self.algo_etd[self.gch(enc_x)] + self.algo_etd[self.gch(enc_y)]

    def encrypt(self, dec_coord):
        dec_x, dec_y = dec_coord
        return self.algo_dte[self.gch(dec_x)] + self.algo_dte[self.gch(dec_y)]



    def updatePlayer(self, opponent):
        # Perform Attack
        (att_x, att_y) = opponent.attack
        if self.my_board[att_x][att_y] == 2:
            return
        if opponent.attack != self.defend and self.my_board[att_x][att_y] == 1:
            # Self Update
            self.my_board[att_x][att_y] = 2
            opponent.op_board[att_x][att_y] = 2
            # Opponent Update
            opponent.points += 1
        else:
            opponent.op_board[att_x][att_y] = 0
        val = 0 
        if self.prev_def != None:
            x,y,color = self.prev_def
            if color == 1:
                val +=1

        print("no of ships by defense : ",val)
        val += (self.my_board.flatten()==1).sum() 
        print("no of ships : ",val)
        
        if val == 0:
            self.game_lost = True

        print(self.points)
