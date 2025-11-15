from engine import ChessEngine
import chess

"""
Functions for simulating engine vs engine tournaments

Maybe also a way to visualize the game by printing to terminal?
"""

def simulateGame(engine1: ChessEngine, engine2: ChessEngine):
  board = chess.Board()
  numMoves = 0
  while not board.is_game_over() and numMoves <= 50:
    move = engine1.find_best_move(board)
    board.push(move)
    if board.is_game_over():
      break
    move = engine2.find_best_move(board)
    board.push(move)
    numMoves += 1
    if numMoves % 10 == 0: print(numMoves)
  print(board, "\n") 

  pass

def simulateTournament(engine1: ChessEngine, engine2: ChessEngine, n: int = 10):
  """
  Simulates n matches between the engines and prints results
  """
  pass