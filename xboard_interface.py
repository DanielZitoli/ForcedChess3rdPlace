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
        self.board = chess.Board()
        self.engine = engine

    def handle_command(self, cmd):
        cmd = cmd.strip()
        parts = cmd.strip().split()

        if parts[0] == "usermove":
            move_uci = parts[1]
        elif len(parts) == 1 and len(parts[0]) in (4, 5):  # e.g., "e2e4" or "a7a8q"
                move_uci = parts[0]
        else:
            move_uci = None

        if cmd == "xboard":
            # Initial handshake
            return
        elif cmd.startswith("protover"):
            # Declare features to XBoard
            print_flush("feature done=1")
        elif cmd == "new":
            self.board.reset()
        elif move_uci:
            try:
                move = chess.Move.from_uci(move_uci)
                legal = forcedCaptureLegalMoves(self.board)
                if move in legal:
                    self.board.push(move)
                    # respond if not in force mode
                    if not getattr(self, "force_mode", False):
                        move_reply = self.engine.find_best_move(board=self.board)
                        self.board.push(move_reply)
                        print_flush(f"move {move_reply.uci()}")
            except Exception as e:
                print_flush(f"# Invalid move: {e}")
        elif cmd == "go":
            self.force_mode = False
            move = self.engine.find_best_move(board=self.board)
            self.board.push(move)
            print_flush(f"move {move.uci()}")
        elif cmd in ("quit", "exit"):
            sys.exit(0)
    # You can handle other commands like 'force', 'remove', etc., if needed
