import chess

"""
Position evaluators

All evaulators should be simply be a function that takes as input a chess.Board
  - all evaluators should return a float value where positive indicated white is winning, negative indicates black is winnig
  - this is because minimax will maximize white's moves, and minimize blacks moves

If we come across more complex evaluators, we can turn this into a class design later
"""

def materialEvaluator(board: chess.Board) -> float:
  """Counts number of pieces of each color and return (weighted) difference"""
  values = {
      chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
      chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0
  }
  score = 0
  for piece_type, val in values.items():
      score += len(board.pieces(piece_type, chess.WHITE)) * val
      score -= len(board.pieces(piece_type, chess.BLACK)) * val
  return score