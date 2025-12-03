import chess
import sys
from engine import ChessEngine
from helpers import forcedCaptureLegalMoves


def print_flush(s):
    print(s, flush=True)


class XBoardHandler():
    def __init__(self, engine: ChessEngine):
        self.board = chess.Board()
        self.engine = engine
        self.force_mode = False

    def extract_move(self, cmd):
        """Extract UCI move from a messy command like:
           'usermove e2e4'
           'e2e4'
           '25170 >first : e2e4'
        """
        parts = cmd.replace(":", " ").split()

        # Case 1: usermove e2e4
        if len(parts) >= 2 and parts[0] == "usermove":
            return parts[1]

        # Case 2: Find something that looks like UCI anywhere
        for p in parts:
            if len(p) in (4, 5):
                try:
                    chess.Move.from_uci(p)
                    return p
                except:
                    pass
        return None

    def handle_command(self, cmd):
        cmd = cmd.strip()

        # Try to detect move anywhere
        move_uci = self.extract_move(cmd)

        if cmd == "xboard":
            return

        elif cmd.startswith("protover"):
            print_flush("feature usermove=1 sigint=0 sigterm=0 done=1")

        elif cmd == "new":
            self.board.reset()
            self.force_mode = False

        elif cmd == "force":
            self.force_mode = True

        elif cmd == "go":
            self.force_mode = False
            move = self.engine.find_best_move(self.board)
            self.board.push(move)
            print_flush(f"move {move.uci()}")

        elif move_uci:
            try:
                move = chess.Move.from_uci(move_uci)
            except:
                return

            ###legal = forcedCaptureLegalMoves(self.board)
            ###if move not in legal:
            ###    return

            self.board.push(move)

            if not self.force_mode:
                reply = self.engine.find_best_move(self.board)
                self.board.push(reply)
                print_flush(f"move {reply.uci()}")

        elif cmd in ("quit", "exit"):
            sys.exit(0)
