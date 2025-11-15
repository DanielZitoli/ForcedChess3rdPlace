from abc import ABC, abstractmethod
import chess

class ChessEngine(ABC):
    """
    Abstract base class for all chess engines.
    Defines the common interface and optional configuration hooks.
    """

    def __init__(self, name="AbstractEngine"):
        self.name = name

    @abstractmethod
    def find_best_move(self, board: chess.Board, max_depth=1, time_limit=None) -> chess.Move:
        """
        Given a board position, return the best move according to this engine.
        """
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"
