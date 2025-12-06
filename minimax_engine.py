import chess
from engine import ChessEngine
import math
from helpers import forcedCaptureLegalMoves

# Next Steps:
# - develop good evaluators
# - tune the engine for depth and time constraints

class MinimaxEngine(ChessEngine):
    """A simple minimax search engine with optional alpha-beta pruning."""

    def __init__(self, name="MinimaxEngine", evaluator=None, use_alphabeta=True, max_depth=4):
        super().__init__(name=name)
        self.use_alphabeta = use_alphabeta
        self.max_depth = max_depth
        self.evaluator = evaluator

    def find_best_move(self, board: chess.Board, max_depth=None, time_limit=None) -> chess.Move:
        depth = max_depth or self.max_depth
        best_move = None
        best_value = -math.inf if board.turn == chess.WHITE else math.inf

        moves = forcedCaptureLegalMoves(board)
        if not moves:
            moves = list(board.legal_moves)

        for move in moves:
            board.push(move)
            if self.use_alphabeta:
                value = self._alphabeta(board, depth - 1, -math.inf, math.inf, not board.turn)
            else:
                value = self._minimax(board, depth - 1, not board.turn)
            board.pop()

            if board.turn == chess.WHITE and value > best_value:
                best_value, best_move = value, move
            elif board.turn == chess.BLACK and value < best_value:
                best_value, best_move = value, move

        return best_move

    def _minimax(self, board, depth, maximizing):
        if depth == 0 or board.is_game_over():
            return self.evaluate(board)

        moves = forcedCaptureLegalMoves(board)
        if not moves:
            moves = list(board.legal_moves)

        if maximizing:
            value = -math.inf
            for move in moves:
                board.push(move)
                value = max(value, self._minimax(board, depth - 1, False))
                board.pop()
            return value
        else:
            value = math.inf
            for move in moves:
                board.push(move)
                value = min(value, self._minimax(board, depth - 1, True))
                board.pop()
            return value

    def _alphabeta(self, board, depth, alpha, beta, maximizing):
        if depth == 0 or board.is_game_over():
            return self.evaluate(board)
        
        moves = forcedCaptureLegalMoves(board)
        if not moves:
            moves = list(board.legal_moves)

        if maximizing:
            value = -math.inf
            for move in moves:
                board.push(move)
                value = max(value, self._alphabeta(board, depth - 1, alpha, beta, False))
                board.pop()
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = math.inf
            for move in moves:
                board.push(move)
                value = min(value, self._alphabeta(board, depth - 1, alpha, beta, True))
                board.pop()
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value
    
    def evaluate(self, board):
        return self.evaluator(board)
