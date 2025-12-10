import chess
import sys
from engine import ChessEngine
from helpers import forcedCaptureLegalMoves


def print_flush(s):
    print(s, flush=True)


class XBoardHandler:
    def __init__(self, engine: ChessEngine):
        self.board = chess.Board()
        self.engine = engine
        self.force_mode = False

    # -----------------------------------------
    # Extract move from noisy XBoard input
    # -----------------------------------------
    def extract_move(self, cmd):
        cmd = cmd.strip()

        # Typical formats:
        #   "usermove e2e4"
        #   "e2e4"
        #   "123 >first: e2e4"
        #   "time 100"
        parts = cmd.replace(":", " ").split()

        # Case 1: usermove command
        if len(parts) >= 2 and parts[0] == "usermove":
            mv = parts[1]
            if self.is_valid_uci(mv):
                return mv

        # Case 2: Find a UCI move anywhere in the string
        for p in parts:
            if self.is_valid_uci(p):
                return p

        return None

    def is_valid_uci(self, move_str):
        if len(move_str) not in (4, 5):
            return False
        try:
            chess.Move.from_uci(move_str)
            return True
        except ValueError:
            return False

    # -----------------------------------------
    # MAIN COMMAND HANDLER
    # -----------------------------------------
    def handle_command(self, cmd):
        cmd = cmd.strip()

        # Extract potential move
        move_uci = self.extract_move(cmd)

        # ---------------------------
        # XBoard handshake
        # ---------------------------
        if cmd == "xboard":
            return

        elif cmd.startswith("protover"):
            print_flush("feature usermove=1 sigint=0 sigterm=0 done=1")
            return

        # ---------------------------
        # Game control
        # ---------------------------
        elif cmd == "new":
            self.board.reset()
            self.force_mode = False
            return

        elif cmd == "force":
            self.force_mode = True
            return

        elif cmd == "go":
            self.force_mode = False
            return self.make_engine_move()

        elif cmd in ("quit", "exit"):
            sys.exit(0)

        # ---------------------------
        # TIME COMMANDS IGNORED (safe)
        # ---------------------------
        elif cmd.startswith("time") or cmd.startswith("otim"):
            return

        # ---------------------------
        # MOVE HANDLING
        # ---------------------------
        elif move_uci:
            return self.handle_user_move(move_uci)

        # If nothing else matches → ignore silently (XBoard standard)
        return

    # -----------------------------------------
    # Make engine move safely
    # -----------------------------------------
    def make_engine_move(self):
        best = self.engine.find_best_move(self.board)

        if not best:
            print_flush("resign")
            return

        self.board.push(best)
        print_flush(f"move {best.uci()}")

    # -----------------------------------------
    # Handle user move safely
    # -----------------------------------------
    def handle_user_move(self, move_uci):
        try:
            move = chess.Move.from_uci(move_uci)
        except Exception:
            return

        legal = forcedCaptureLegalMoves(self.board)
        if move not in legal:
            # illegal move → ignore
            return

        # push user's move
        self.board.push(move)

        # if in force mode → DO NOT MOVE
        if self.force_mode:
            return

        # otherwise respond
        return self.make_engine_move()