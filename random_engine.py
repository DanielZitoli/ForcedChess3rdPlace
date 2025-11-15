import random
import chess
from engine import ChessEngine
from helpers import forcedCaptureLegalMoves

class RandomEngine(ChessEngine):
    """A trivial engine that picks a random legal move."""

    def __init__(self):
        super().__init__(name="RandomEngine")

    def find_best_move(self, board: chess.Board, max_depth=1, time_limit=None) -> chess.Move:
        return random.choice(forcedCaptureLegalMoves(board))