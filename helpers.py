import chess

"""
A function that returns all legal moves in the Forced Capture variant
"""
def forcedCaptureLegalMoves(board: chess.Board): 
  moves = board.legal_moves
  captures = []
  for move in moves:
    if board.is_capture(move):
      captures.append(move)
  return captures if len(captures) > 0 else list(moves)



"""
A function for deciding when a Forced Capture game is finished?
"""
