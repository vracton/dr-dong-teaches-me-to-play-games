from enum import Enum

import pygame
from Player import Player
from Quoridor.QuoridorMove import QuoridorMoveType

class CurrentSelection(Enum):
    MOVE = 0
    HORIZONTAL_FENCE = 1
    VERTICAL_FENCE = 2

    def increment(current):
        if current == CurrentSelection.VERTICAL_FENCE:
            return CurrentSelection.MOVE
        elif current == CurrentSelection.MOVE:
            return CurrentSelection.HORIZONTAL_FENCE
        elif current == CurrentSelection.HORIZONTAL_FENCE:
            return CurrentSelection.VERTICAL_FENCE

class QuoridorHumanPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def getMove(self, board):
        moves = []
        fences = [[], []] # Horizontal, then vertical

        valid_moves = board.getPossibleMoves()
        
        for move in valid_moves:
            if move.type == QuoridorMoveType.MOVE:
                moves.append(move)
            if move.type == QuoridorMoveType.FENCE:
                if move.is_horizontal:
                    fences[0].append(move)
                else:
                    fences[1].append(move)

        moves.sort(key=lambda move: move.coord.y * 10 + move.coord.x)
        fences[0].sort(key=lambda move: move.coord.y * 10 + move.coord.x)
        fences[1].sort(key=lambda move: move.coord.y * 10 + move.coord.x)

        self.current_move_index = 0
        self.current_fence_index = [0, 0]

        self.current_selection = CurrentSelection.MOVE

        redraw = True
        while True:
            if redraw:
                if self.current_selection == CurrentSelection.MOVE:
                    board.drawBoardInternal(moves, [moves[self.current_move_index]], [], [])
                elif self.current_selection == CurrentSelection.HORIZONTAL_FENCE:
                    board.drawBoardInternal([], [], fences[0], [fences[0][self.current_fence_index[0]]])
                elif self.current_selection == CurrentSelection.VERTICAL_FENCE:
                   board.drawBoardInternal([], [], fences[1], [fences[1][self.current_fence_index[1]]])

                redraw = False

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if self.current_selection == CurrentSelection.MOVE:
                            return moves[self.current_move_index]
                        elif self.current_selection == CurrentSelection.HORIZONTAL_FENCE:
                            return fences[0][self.current_fence_index[0]]
                        elif self.current_selection == CurrentSelection.VERTICAL_FENCE:
                            return fences[1][self.current_fence_index[1]]


                    if event.key == pygame.K_SPACE:
                        if fences[0] or fences[1]:
                            self.current_selection = CurrentSelection.increment(self.current_selection)
                        redraw = True
                    if event.key == pygame.K_RIGHT:
                        self.adjust(self.get_next, moves, fences)
                        redraw = True
                    if event.key == pygame.K_LEFT:
                        self.adjust(self.get_previous, moves, fences)
                        redraw = True
                    if event.key == pygame.K_UP:
                        self.adjust(self.get_previous_row, moves, fences)
                        redraw = True
                    if event.key == pygame.K_DOWN:
                        self.adjust(self.get_next_row, moves, fences)
                        redraw = True

    def adjust(self, action, moves, fences):
        if self.current_selection == CurrentSelection.MOVE:
            self.current_move_index = action(moves, self.current_move_index)
        elif self.current_selection == CurrentSelection.HORIZONTAL_FENCE:
            self.current_fence_index[0] = action(fences[0], self.current_fence_index[0])            
        elif self.current_selection == CurrentSelection.VERTICAL_FENCE:
            self.current_fence_index[1] = action(fences[1], self.current_fence_index[1])   

    def get_next(self, collection, current_index):
        if current_index == len(collection) - 1:
            return 0
        else:
            return current_index + 1

    def get_previous(self, collection, current_index):
        if current_index == 0:
            return len(collection) - 1
        else:
            return current_index - 1

    def get_next_row(self, collection, current_index):
        target_x = collection[current_index].coord.x
        target_y = collection[current_index].coord.y + 1
        while current_index < len(collection) - 1:
            current_index += 1
            if collection[current_index].coord.x >= target_x and collection[current_index].coord.y >= target_y:
                return current_index
        return 0

    def get_previous_row(self, collection, current_index):
        target_x = collection[current_index].coord.x
        target_y = collection[current_index].coord.y - 1
        while current_index > 0:
            current_index -= 1
            if collection[current_index].coord.x <= target_x and collection[current_index].coord.y <= target_y:
                return current_index
        return len(collection) - 1  