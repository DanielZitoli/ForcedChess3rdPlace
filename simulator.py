from engine import ChessEngine
import chess

"""
Functions for simulating engine vs engine tournaments
"""

def simulateGame(engineA: ChessEngine, engineB: ChessEngine, debug=False):
    import time
    board = chess.Board()
    numMoves = 0

    # Each engine gets 60 seconds total
    timeA = 0.0
    timeB = 0.0
    time_budget = 60.0

    # Optional: per-move timeout to prevent freezing
    per_move_time_limit = 2.0

    while not board.is_game_over():
        # ----- ENGINE A MOVE -----
        start = time.time()
        move = engineA.find_best_move(board, time_limit=per_move_time_limit)
        timeA += time.time() - start

        if timeA > time_budget:
            if debug:
                print("Engine A flagged for time.")
            return "0-1"   # Engine A loses on time → Black wins

        board.push(move)
        if board.is_game_over():
            break

        # ----- ENGINE B MOVE -----
        start = time.time()
        move = engineB.find_best_move(board, time_limit=per_move_time_limit)
        timeB += time.time() - start

        if timeB > time_budget:
            if debug:
                print("Engine B flagged for time.")
            return "1-0"   # Engine B loses on time → White wins

        board.push(move)
        numMoves += 1

    if debug:
        print(board, "\n")
        print(f"Final time: A={timeA:.2f}s, B={timeB:.2f}s")

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