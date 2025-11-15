import chess
import sys
from engine import ChessEngine
from helpers import forcedCaptureLegalMoves


def print_flush(s):
    print(s, flush=True)

"""
Class to parse xboard messages and return a move 
"""

class XBoardHandler():
  def __init__(self, engine: ChessEngine):
    self.board = chess.Board
    self.engine = engine

  def handle_command(self, cmd):
    parts = cmd.strip().split()

    if cmd == "xboard":
        # Initial handshake
        return
    elif cmd.startswith("protover"):
        # Declare features to XBoard
        print_flush("feature done=1")
    elif cmd == "new":
        self.board.reset()
    elif cmd.startswith("usermove"):
        move_uci = parts[1]
        try:
            move = chess.Move.from_uci(move_uci)
            if move in forcedCaptureLegalMoves(self.board):
                self.board.push(move)
        except:
            pass
    elif cmd == "go":
        # Very simple move selection
        move = self.engine.find_best_move(self.engine)
        self.board.push(move)
        print_flush(f"move {move.uci()}")
    elif cmd in ("quit", "exit"):
        sys.exit(0)
    # You can handle other commands like 'force', 'remove', etc., if needed
