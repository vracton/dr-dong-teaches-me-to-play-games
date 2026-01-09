from Player import Player
from Quoridor.QuoridorMove import QuoridorMove
from random import Random

class QuoridorYOURNAMEPlayer(Player):
    def __init__(self):
        super().__init__("Your names here") 

    def getMove(self, board):
        
        # Here is where your code goes


                
        old_coord = board.players[index].coord
        old_coord.y += 1
        return QuoridorMove.move_pawn(old_coord, self)