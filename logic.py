from uuid import uuid4


class Player:
    def __init__(self) -> None:
        self.id = uuid4()
        self.marker = None
        self.game = None

    def __eq__(self, __o: object) -> bool:
        if type(__o) == type(self) and __o.id == self.id:
            return True
        return False
    
    def place_by_player(self,index):
        self.game : Game
        self.game.place(index,self)

   

class Tile:
    def __init__(self) -> None:
        self.value = 0
    
    def update_value(self, newvalue):
        self.value = newvalue
    
    def __repr__(self) -> str:
        return f"Tile({self.value})"



    def __eq__(self, __o: object) -> bool:
        if type(__o) == type(self) and __o.value == self.value:
            return True
        elif __o is int:
            if __o == self.value: return True
        return False

    def __ne__(self, __o: object) -> bool:
        if type(__o) == type(self):
            if __o.value == self.value: return False
            
        elif __o is int:
            if __o == self.value: return False
        return True



class Board:
    def __init__(self) -> None:
        print("new Board")
        self.board = [
            [Tile(),Tile(),Tile()],
            [Tile(),Tile(),Tile()],
            [Tile(),Tile(),Tile()]
        ]
        print(self)
    
    def place(self,index,marker):
        xindex,yindex = index
        
        if self.board[yindex][xindex] != Tile(): return False


        self.board[yindex][xindex].update_value(marker)
        print(self)
        return True

    def check_winner(self):
        board = self.board
        for x in range(3):
            if board[x][0] == board[x][1] == board[x][2] != Tile():
                return board[x][0]
            elif board[0][x] == board[1][x] == board[2][x] != Tile():
                return board[0][x]
        if board[0][0] == board[1][1] == board[2][2] != Tile():
            return board[0][0]
        elif board[0][2] == board[1][1] == board[2][0] != Tile():
            return board[0][2]
        return False


    def __repr__(self) -> str:
        return f"\n{self.board[0] }\n{self.board[1]}\n{self.board[2]}\n"



class Game:  
    def __init__(self, player1:Player, player2:Player) -> None:
        print("new Game")
        self.player1 = player1
        self.player2 = player2

        self.currentplayer = player1
        self.winner = None

        self.player1.marker = "X"
        self.player2.marker = "O"

        self.player1.game = self
        self.player2.game = self
        
        self.board = Board()

    def place(self,index, player:Player):
        if self.winner is not None: return self.winner
        print("placing")
        if player != self.currentplayer: print("is not currentplayer");return False

        if self.board.place(index,player.marker) is False: print("is taken.");return False
        print("placing")

        rt = self.board.check_winner()
        if rt is not False: print("winner",rt);self.winner = self.currentplayer;return self.winner

        if self.currentplayer == self.player1:
            self.currentplayer = self.player2
        elif self.currentplayer == self.player2:
            self.currentplayer = self.player1
        print(f"new currentplayer:{self.currentplayer.marker}")

    def mainloop(self):

        while True:
            inp = input(f"xmove for {self.currentplayer.marker}:")
            inp = int(inp)

            inp2 = input(f"ymove for {self.currentplayer.marker}")
            inp2 = int(inp2)

            t = (inp,inp2)
            if g.place(t,self.currentplayer) is not (False or None): print("exiting mainloop");return True

if __name__ == "__main__":
    p1 = Player()
    p2 = Player()

    g = Game(p1,p2)
    g.mainloop()


