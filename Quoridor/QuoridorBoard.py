from copy import deepcopy
from GameState import GameState
from Quoridor.Fence import Fence
from Quoridor.QuoridorMove import QuoridorMove, QuoridorMoveType
from Quoridor.Coordinate import Coordinate

import pygame

from TiePlayer import TiePlayer
pygame.init()

BLACK = 0,0,0
PLAYER1 = 255,0,0
PLAYER2 = 0,0,255
PLAYER3 = 0,150,50
PLAYER4 = 200, 200, 0
WHITE = 50, 50, 50
FENCE_COLOR = 150, 150, 150
FENCE_WIDTH = 4
POTENTIAL_HIGHLIGHT = 0, 100, 100
HIGHLIGHT = 200, 200, 200

COLORS = [PLAYER1, PLAYER2, PLAYER3, PLAYER4]

ROWS = 9

WIDTH = 640
HEIGHT = 480

pygame.font.init()

class QuoridorBoard(GameState):
    
    def __init__(self, players):
        super().__init__(players)
        "Set up initial board configuration."

        self.horizontal_fences = []
        self.vertical_fences = []
       # self.forbidden_moves = {}
        self.check_possible = True

        if len(players) == 2:
            self.pawns = [Coordinate(4, 0), Coordinate(4, 8)]
            self.fences = [10, 10]
        elif len(players) == 4:
            self.pawns = [Coordinate(4, 0), Coordinate(0, 4), Coordinate(4, 8), Coordinate(8, 4)]
            self.fences = [5, 5, 5, 5]
        else:
            raise Exception("Illegal number of players")

        self.current_player = self.players[0]
        
        self.game_closed = False
        
        
    def clone(self):
        newBoard = QuoridorBoard(self.players)
        newBoard.pawns = deepcopy(self.pawns)
        for fence in self.horizontal_fences:
            newBoard.horizontal_fences.append(deepcopy(fence))
        for fence in self.vertical_fences:
            newBoard.vertical_fences.append(deepcopy(fence))
        newBoard.current_player = self.current_player
        return newBoard
    
    def getPossibleMoves(self):       
        return self.get_legal_moves_for_player(self.current_player) + self.get_legal_fences(self.current_player)

        # Find the index of your player
    def findIndex(self, player):
        for i in range(len(self.players)):
            if self.players[i] == player:
                return i
        raise "Player not found"

# Move the pawn
    def move_pawn(self, player, new_coord):
        if self.is_legal_move(player, new_coord):
            self.pawns[self.findIndex(player)] = new_coord
        else:
            raise Exception("Illegal move!")

    # Add a fence
    def add_fence(self, player, coord1, is_horizontal):
        if self.fences[self.findIndex(player)] == 0:
            raise Exception("No fences remain!")
        new_fence = Fence(coord1, is_horizontal)
        for fence in self.all_fences():
            if fence.check_conflict(new_fence):
                raise Exception("Fence in illegal location!")
        if new_fence.is_horizontal:
            self.horizontal_fences.append(new_fence)
        else:
            self.vertical_fences.append(new_fence)

        #for coord_pair in new_fence.forbidden_moves():
        #    if coord_pair[0] not in self.forbidden_moves:
        #        self.forbidden_moves[coord_pair[0]] = []
        #    self.forbidden_moves[coord_pair[0]].append(coord_pair[1])

        self.fences[self.findIndex(player)] -= 1

    # Check if this move is allowed
    def is_legal_move(self, player, new_coord):
        return new_coord in self.get_legal_move_positions_for_player(player)

    # Check if you can move from current to new_coord without going through any fence in the fences collection
    def test_fences(self, fences, current, new_coord):
        for fence in fences:
            if not fence.test_move(current, new_coord):
                return False
        return True

    # Check if you can move from current to new_coord without going through any fences
    def check_fences(self, current, new_coord):
        return (current.x == new_coord.x and self.test_fences(self.horizontal_fences, current, new_coord)) or (current.y == new_coord.y and self.test_fences(self.vertical_fences, current, new_coord))
        #if current not in self.forbidden_moves:
        #    return True
        #else:
        #    return new_coord not in self.forbidden_moves[current]

    # Get all possible positions you can jump to if you are on current and another pawn is on move
    def possible_jumps(self, current, move):
        if not self.is_occupied(move):
            return []
        # Choose target jump
        if current.x == move.x:
            if current.y > move.y:
                target = Coordinate(current.x, current.y - 2)
            else:
                target = Coordinate(current.x, current.y + 2)
        else:
            if current.x > move.x:
                target = Coordinate(current.x - 2, current.y)
            else:
                target = Coordinate(current.x + 2, current.y)

        if not target.is_legal():
            return []

        if self.check_fences(move, target) and not self.is_occupied(target):
            return [target]
        else:
            # Get new targets
            if current.x == move.x:
                new_targets = [Coordinate(current.x - 1, move.y), Coordinate(current.x + 1, move.y)]
            else:
                new_targets = [Coordinate(move.x, current.y - 1), Coordinate(move.x, current.y + 1)]

            final_moves = []
            for new_target in new_targets:
                if self.check_fences(move, new_target) and not self.is_occupied(new_target):
                    final_moves.append(new_target)
            return final_moves


    # Gets all legal moves for a given player's pawn - pawn moves only
    def get_legal_move_positions_for_player(self, player):
        return self.get_legal_move_positions(self.pawns[self.findIndex(player)])

    # These are moves for the pawn moves only
    def get_legal_move_positions(self, current):
        moves = []
        potential_moves = [Coordinate(current.x - 1, current.y), Coordinate(current.x, current.y - 1), Coordinate(current.x + 1, current.y), Coordinate(current.x, current.y + 1)]
        for move in potential_moves:
            # Make sure it's legal
            if not move.is_legal():
                continue
            # Check for fences
            if self.check_fences(current, move):
                # Check for occupied spaces
                if self.is_occupied(move):
                    for jump in self.possible_jumps(current, move):
                        moves.append(jump)
                else:
                    moves.append(move)

        return moves

    def all_fences(self):
        return self.horizontal_fences + self.vertical_fences

    # These are possible fences
    def get_legal_fences(self, player):
        if (self.fences[self.findIndex(player)] == 0):
            return []
        fences = []
        # Horizontal 
        for ix in range(0, 8):
            for iy in range(1, 9):
                potential_fence = Fence(Coordinate(ix, iy), True)
                found_conflict = False
                for fence in self.all_fences():
                    if fence.check_conflict(potential_fence):
                        found_conflict = True
                        break
                if found_conflict:
                    continue
                if self.check_possible:
                    if not self.check_if_possible(potential_fence):
                        continue
                fences.append(QuoridorMove.add_fence(potential_fence, self.current_player))
        # Vertical
        for ix in range(1, 9):
            for iy in range(0, 8):
                potential_fence = Fence(Coordinate(ix, iy), False)
                found_conflict = False
                for fence in self.all_fences():
                    if fence.check_conflict(potential_fence):
                        found_conflict = True
                        break
                if found_conflict:
                    continue
                if self.check_possible:
                    if not self.check_if_possible(potential_fence):
                        continue
                fences.append(QuoridorMove.add_fence(potential_fence, self.current_player))
        return fences

    # Check to make sure it is still possible to get across the board
    def check_if_possible(self, new_fence):
        for i_player in range(len(self.pawns)):
            if not self.check_if_possible_single_player(i_player, new_fence):
                return False
        return True

    # Check to make sure it is still possible to get across the board for a single player
    def check_if_possible_single_player(self, player, new_fence):
        win_condition = self.get_target(player)

        # Provisionally add the new fence
        if new_fence.is_horizontal:
            self.horizontal_fences.append(new_fence)
        else:
            self.vertical_fences.append(new_fence)

        # Dijkstra's algorithm, modified
        already_tested = {}
        # Start with current pawn location
        to_be_tested = [self.pawns[player]]
        while to_be_tested:
            new_to_be_tested = []
            for point in to_be_tested:
                for new_point in self.get_legal_move_positions(point):
                    if win_condition(new_point):
                        # Remove the added fence
                        if new_fence.is_horizontal:
                            self.horizontal_fences.pop(len(self.horizontal_fences) - 1)
                        else:
                            self.vertical_fences.pop(len(self.vertical_fences) - 1)
                        return True
                    if not new_point in already_tested:
                        already_tested[new_point] = 0
                        new_to_be_tested.append(new_point)
            to_be_tested = new_to_be_tested

        # This means no win condition was found
        # So remove the added fence
        if new_fence.is_horizontal:
            self.horizontal_fences.pop(len(self.horizontal_fences) - 1)
        else:
            self.vertical_fences.pop(len(self.vertical_fences) - 1)
        return False

    # Return a lambda function which determines if a coordinate satisfied the win condition for a particular player
    def get_target(self, player):
        if player == 0:
            return lambda a : a.y == 8
        if player == 1:
            if len(self.pawns) == 2:
                return lambda a : a.y == 0
            elif len(self.pawns) == 4:
                return lambda a : a.x == 8
        if player == 2:
            return lambda a : a.y == 0
        if player == 3:
            return lambda a : a.x == 0

        raise Exception("Illegal player number entered")

    # Check if a square is occupied by another pawn
    def is_occupied(self, coord):
        for player in self.pawns:
            if coord == player:
                return True
        return False

    def get_legal_moves_for_player(self, player):
        legal_moves = []
        for move in self.get_legal_move_positions_for_player(player):
            legal_moves.append(QuoridorMove.move_pawn(move, player))
        return legal_moves




    
    def checkIsValid(self, move):
        if move.type == QuoridorMoveType.MOVE:
            return self.is_legal_move(move.player, move.coord)
        elif move.type == QuoridorMoveType.FENCE:
            return move in self.get_legal_fences(move.player)
        else:
            raise "Illegal move type"

    def doMove(self, move):
        if move.type == QuoridorMoveType.MOVE:
            self.move_pawn(move.player, move.coord)
        elif move.type == QuoridorMoveType.FENCE:
            self.add_fence(move.player, move.coord, move.is_horizontal)
        else:
            raise "Illegal move type"
        self.current_player = self.nextPlayer()
        return self
    
    def currentPlayer(self):
        return self.current_player
    
    def nextPlayer(self):
        playerIndex = self.findIndex(self.current_player)

        if (len(self.pawns) == 2 and self.current_player == self.players[1]) or (len(self.pawns) == 4 and self.current_player == self.players[3]):
            return self.players[0]
        else:
            return self.players[playerIndex + 1]
        
    def getGameEnded(self):
        if len(self.pawns) == 2:
            if self.pawns[0].y == 8:
                return self.players[0]
            elif self.pawns[1].y == 0:
                return self.players[1]
        if len(self.pawns) == 4:
            if self.pawns[0].y == 8:
                return self.players[0]
            elif self.pawns[1].x == 8:
                return self.players[1]
            elif self.pawns[2].y == 0:
                return self.players[2]
            elif self.pawns[3].x == 0:
                return self.players[3]
        return False
    
    def scoreBoard(self):
        if len(self.pawns) == 2:
            if self.pawns[0].y == 8:
                return {self.players[0] : 1, self.players[1] : -1}
            elif self.pawns[1].y == 0:
                return {self.players[0] : -1, self.players[1] : 1}
            else:
                return {self.players[0] : 0, self.players[1] : 0}
        if len(self.pawns) == 4:
            if self.pawns[0].y == 8:
                return {self.players[0] : 1, self.players[1] : -1, self.players[2] : -1, self.players[3] : -1}
            elif self.pawns[1].x == 8:
                return {self.players[0] : -1, self.players[1] : 1, self.players[2] : -1, self.players[3] : -1}
            elif self.pawns[2].y == 0:
                return {self.players[0] : -1, self.players[1] : -1, self.players[2] : 1, self.players[3] : -1}
            elif self.pawns[3].x == 0:
                return {self.players[0] : -1, self.players[1] : -1, self.players[2] : -1, self.players[3] : 1}
            else:
                return {self.players[0] : 0, self.players[1] : 0, self.players[2] : 0, self.players[3] : 0}
        
    def initializeDrawing(self):
        # These all have to be class variables to avoid resetting them
        QuoridorBoard.screen = pygame.display.set_mode((WIDTH, HEIGHT))

        QuoridorBoard.width = WIDTH
        QuoridorBoard.height = HEIGHT
        QuoridorBoard.box_size = HEIGHT / (ROWS + 2)
        QuoridorBoard.radius = QuoridorBoard.box_size / 2
        QuoridorBoard.left_disp_offset = QuoridorBoard.box_size * 2
        QuoridorBoard.top_disp_offset = QuoridorBoard.box_size

        QuoridorBoard.game_closed = False
        
    def drawBoard(self):
        self.drawBoardInternal()

    def drawBoardInternal(self, potential_moves = [], current_space = [], potential_fences = [], current_fence = []):
        if not QuoridorBoard.game_closed:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    QuoridorBoard.game_closed = True
                    pygame.quit()

            # Reset screen
            QuoridorBoard.screen.fill(BLACK)

            # Drawing the grid
            for row_num in range(0, 10):
                row_start = (QuoridorBoard.left_disp_offset, QuoridorBoard.top_disp_offset + (QuoridorBoard.box_size * row_num))
                row_end = (QuoridorBoard.left_disp_offset + (QuoridorBoard.box_size * 9), QuoridorBoard.top_disp_offset + (QuoridorBoard.box_size * row_num))
                pygame.draw.line(QuoridorBoard.screen, WHITE, row_start, row_end)
            for col_num in range(0, 10):
                col_start = (QuoridorBoard.left_disp_offset + (QuoridorBoard.box_size * col_num), QuoridorBoard.top_disp_offset)
                col_end = (QuoridorBoard.left_disp_offset + (QuoridorBoard.box_size * col_num), QuoridorBoard.top_disp_offset + (QuoridorBoard.box_size * 9))
                #if col_num > 0:
                #    col_label = my_font.render(str(col_num), 1, WHITE)
                #    QuoridorBoard.screen.blit(col_label, (QuoridorBoard.left_disp_offset + (QuoridorBoard.box_size * col_num) - QuoridorBoard.box_size / 2, QuoridorBoard.height - 40))
                pygame.draw.line(QuoridorBoard.screen, WHITE, col_start, col_end)

            color = COLORS[self.findIndex(self.current_player)]
            highlight_color = color[0] / 2, color[1] / 2, color[2] / 2

            # Drawing potential squares
            for position in potential_moves:
                pygame.draw.rect(QuoridorBoard.screen, highlight_color, pygame.Rect(int(QuoridorBoard.box_size * position.coord.x) + QuoridorBoard.left_disp_offset + 1, int(QuoridorBoard.box_size * position.coord.y) + QuoridorBoard.top_disp_offset + 1, QuoridorBoard.box_size - 1, QuoridorBoard.box_size - 1))

            # Drawing current cursor position for move
            for position in current_space:
                pygame.draw.rect(QuoridorBoard.screen, HIGHLIGHT, pygame.Rect(int(QuoridorBoard.box_size * position.coord.x) + QuoridorBoard.left_disp_offset + 1, int(QuoridorBoard.box_size * position.coord.y) + QuoridorBoard.top_disp_offset + 1, QuoridorBoard.box_size - 1, QuoridorBoard.box_size - 1))

            # Drawing pieces
            for i in range(len(self.pawns)):
                pawn = self.pawns[i]
                pos = (int(QuoridorBoard.box_size * (pawn.x + 0.5)) + QuoridorBoard.left_disp_offset + 1,
                        int(QuoridorBoard.box_size * (pawn.y + 0.5)) + QuoridorBoard.top_disp_offset + 1)
                pygame.draw.circle(QuoridorBoard.screen, COLORS[i], pos, QuoridorBoard.radius - 1)

            # Draw potential fences
            for fence in potential_fences:
                self.draw_fence(fence.coord, fence.is_horizontal, highlight_color)
    
            # Drawing fences
            for fence in self.horizontal_fences:
                self.draw_fence(fence.first, fence.is_horizontal, FENCE_COLOR)
            for fence in self.vertical_fences:
                self.draw_fence(fence.first, fence.is_horizontal, FENCE_COLOR)

            # Draw current potential fence
            for fence in current_fence:
                self.draw_fence(fence.coord, fence.is_horizontal, HIGHLIGHT)

            # Display information on the side:

    
            string = "Current player: %i" % (self.findIndex(self.current_player) + 1)
            position = Coordinate(self.left_disp_offset + (self.box_size * (ROWS + .5)), self.height * .2)
            self.draw_string(string, color, position)
            for i_player, n_fences in enumerate(self.fences):
                string = "Player %i: %i fences left" % (i_player + 1, n_fences)
                position.y += QuoridorBoard.height * .05
                self.draw_string(string, COLORS[i_player], position)


            pygame.display.flip()

    def draw_string(self, string, color, position):
        my_font = pygame.font.SysFont("Calibri", 12)
        text = my_font.render(string, 1, color)
        QuoridorBoard.screen.blit(text, (position.x, position.y))

    def draw_fence(self, coord, is_horizontal, color):
        second_x = coord.x
        second_y = coord.y
        if is_horizontal:
            second_x += 2
        else:
            second_y += 2
        pos1 = (int(QuoridorBoard.box_size * coord.x) + QuoridorBoard.left_disp_offset,
                int(QuoridorBoard.box_size * coord.y) + QuoridorBoard.top_disp_offset)
        pos2 = (int(QuoridorBoard.box_size * second_x) + QuoridorBoard.left_disp_offset,
                int(QuoridorBoard.box_size * second_y) + QuoridorBoard.top_disp_offset)
        pygame.draw.line(QuoridorBoard.screen, color, pos1, pos2, FENCE_WIDTH)
        

