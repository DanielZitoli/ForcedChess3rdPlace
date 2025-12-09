from engine import ChessEngine
import chess

"""
Functions for simulating engine vs engine tournaments
"""

def simulateGame(engineA: ChessEngine, engineB: ChessEngine, debug = False):
  board = chess.Board()
  numMoves = 0
  while not board.is_game_over():
    move = engineA.find_best_move(board)
    board.push(move)
    if board.is_game_over():
      break
    move = engineB.find_best_move(board)
    board.push(move)
    numMoves += 1

  print(board, "\n") 
  
  return board.result()

def simulateTournament(engineA: ChessEngine, engineB: ChessEngine, n: int = 10):
  """
  Simulates n matches between the engines and prints results
  """

  score = {"AWins": 0, "Tie": 0, "BWins": 0}
  for game in range(n):
    if game % 2 == 0:
      result = simulateGame(engineA, engineB)
    else:
      result = simulateGame(engineB, engineA)
    
    if result == "1-0":
      if game % 2 == 0:
        score["AWins"] += 1
      else:
        score["BWins"] += 1
    elif result == "0-1":
      if game % 2 == 0:
        score["BWins"] += 1
      else:
        score["AWins"] += 1
    else:
      score["Tie"] += 1
    print(f"Game {game}")
  
  displayResult(score, n)

  return

def displayResult(score, n):
  print(f"{n} games played: (Engine A Wins, Ties, Engine B Wins) = ({score["AWins"]}, {score["Tie"]}, {score["BWins"]})")