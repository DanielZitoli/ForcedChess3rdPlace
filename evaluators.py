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

# FOR EVALUATORS

WEIGHTS1 = {
    # base piece values (slightly compressed to encourage dynamic play)
    "pawn": 100,
    "knight": 300,
    "bishop": 310,
    "rook": 470,
    "queen": 850,
    "king": 20000,

    # mobility weight (balanced: encourages activity but not reckless)
    "mobility": 4,

    # center control (moderate)
    "center": 12,

    # passed pawn base + per-rank urgency (bigger than default to avoid fortress)
    "passed_base": 70,
    "passed_per_rank": 22,

    # pawn rank (general advancement reward)
    "pawn_rank_weight": 12,

    # king-safety (midgame) — stronger than vanilla but not extreme
    "king_attack_penalty": 140,
    "king_home_penalty_per_rank": 60,
    "king_center_penalty": 45,

    # endgame scaling (favor converting small advantages)
    "endgame_king_dist_weight": 18,
    "endgame_edge_bonus": 12,
    "endgame_mobility_mult": 6,

    # anti-fortress: encourage progress when no captures exist
    "anti_fortress_pawn_progress": 28,   # per-best-rank

    # repetition / draw avoidance (contempt + rep penalty)
    "contempt": 42,
    "repetition_penalty": 280,

    # trade-safety multiplier (how strongly we punish bad trades)
    "trade_penalty_mult": 0.6,

    # check bonus/penalty
    "check_penalty": 140,

    # terminal values
    "mate_score": 999999,
    "stalemate_score": -220,
}

# second weights for comparison

WEIGHTS2 = {
    # base piece values (slightly compressed to encourage dynamic play)
    "pawn": 100,
    "knight": 300,
    "bishop": 310,
    "rook": 470,
    "queen": 850,
    "king": 20000,

    # mobility weight (balanced: encourages activity but not reckless)
    "mobility": 4,

    # center control (moderate)
    "center": 12,

    # passed pawn base + per-rank urgency (bigger than default to avoid fortress)
    "passed_base": 70,
    "passed_per_rank": 22,

    # pawn rank (general advancement reward)
    "pawn_rank_weight": 12,

    # king-safety (midgame) — stronger than vanilla but not extreme
    "king_attack_penalty": 140,
    "king_home_penalty_per_rank": 60,
    "king_center_penalty": 45,

    # endgame scaling (favor converting small advantages)
    "endgame_king_dist_weight": 18,
    "endgame_edge_bonus": 12,
    "endgame_mobility_mult": 6,

    # anti-fortress: encourage progress when no captures exist
    "anti_fortress_pawn_progress": 28,   # per-best-rank

    # repetition / draw avoidance (contempt + rep penalty)
    "contempt": 42,
    "repetition_penalty": 280,

    # trade-safety multiplier (how strongly we punish bad trades)
    "trade_penalty_mult": 0.6,

    # check bonus/penalty
    "check_penalty": 140,

    # terminal values
    "mate_score": 999999,
    "stalemate_score": -220,
}


# =========================================================
# Helpers (self-contained)
# =========================================================
def is_endgame(board: chess.Board) -> bool:
    """Strict endgame: few non-pawn pieces on the board."""
    nonpawn = 0
    for p in board.piece_map().values():
        if p.piece_type not in (chess.KING, chess.PAWN):
            nonpawn += 1
    return nonpawn <= 4


def is_passed_pawn(board: chess.Board, sq: int, color: bool) -> bool:
    """Standard passed pawn definition."""
    file = chess.square_file(sq)
    rank = chess.square_rank(sq)
    direction = 1 if color == chess.WHITE else -1
    opp = not color

    r = rank + direction
    while 0 <= r < 8:
        for f in (file - 1, file, file + 1):
            if 0 <= f < 8:
                t = chess.square(f, r)
                p = board.piece_at(t)
                if p and p.piece_type == chess.PAWN and p.color == opp:
                    return False
        r += direction
    return True


def king_safety_eval(board: chess.Board, color: bool, weights) -> float:
    """King safety: penalize unsafe kings in midgame; allow active kings in endgame."""
    w = weights
    ksq = board.king(color)
    if ksq is None:
        return 0.0

    score = 0.0
    rank = chess.square_rank(ksq)
    file = chess.square_file(ksq)

    if not is_endgame(board):
        # penalty for leaving home rank (discourages premature king walks)
        home_rank = 0 if color == chess.WHITE else 7
        if rank != home_rank:
            score -= w["king_home_penalty_per_rank"] * abs(rank - home_rank)

        # penalty for being in central files (d/e)
        if file in (3, 4):
            score -= w["king_center_penalty"]

        # penalty if attacked at all
        if board.attackers(not color, ksq):
            score -= w["king_attack_penalty"]
    else:
        # endgame: centralization bonus
        center_squares = {chess.D4, chess.D5, chess.E4, chess.E5}
        if ksq in center_squares:
            score += 36  # modest centralization bonus in real endgames

    return score


# =========================================================
# Main evaluator
# =========================================================
def REvaluator(board: chess.Board) -> float:
    w = WEIGHTS1
    score = 0.0

    # ---------------------------
    # 1) Material (compressed values to encourage dynamic play)
    # ---------------------------
    piece_values = {
        chess.PAWN:   w["pawn"],
        chess.KNIGHT: w["knight"],
        chess.BISHOP: w["bishop"],
        chess.ROOK:   w["rook"],
        chess.QUEEN:  w["queen"],
        chess.KING:   w["king"],
    }

    for pt, val in piece_values.items():
        score += val * (len(board.pieces(pt, chess.WHITE)) - len(board.pieces(pt, chess.BLACK)))

    # ---------------------------
    # 2) Trade / capture safety (simple, stable)
    #    We penalize positions where our pieces are attacked proportionally,
    #    but less extremely than before (keeps engine willing to sacrifice tactically).
    # ---------------------------
    for color, sign in [(chess.WHITE, +1), (chess.BLACK, -1)]:
        opponent = not color
        for sq in board.pieces(chess.PAWN, color) | board.pieces(chess.KNIGHT, color) | \
                  board.pieces(chess.BISHOP, color) | board.pieces(chess.ROOK, color) | \
                  board.pieces(chess.QUEEN, color):
            # sq is an int; convert to piece
            piece = board.piece_at(sq)
            if piece is None:
                continue
            base_val = piece_values[piece.piece_type]
            attackers = board.attackers(opponent, sq)
            if attackers:
                worst_trade = -9999
                for a in attackers:
                    a_piece = board.piece_at(a)
                    if a_piece:
                        trade = piece_values[a_piece.piece_type] - base_val
                        if trade > worst_trade:
                            worst_trade = trade
                # smaller multiplier than before: keeps tactical willingness
                score += sign * worst_trade * w["trade_penalty_mult"]

    # ---------------------------
    # 3) Mobility (balanced)
    # ---------------------------
    # compute mobility for both sides cleanly without mutating board.turn
    white_mob = len(list(board.legal_moves_of_color(chess.WHITE))) if hasattr(board, "legal_moves_of_color") else None
    if white_mob is None:
        # fallback if python-chess version is older: simulate
        white_mob = 0
        for move in board.legal_moves:
            if board.turn == chess.WHITE:
                white_mob += 1
        # less precise fallback; but we will compute black_mob using a simple swap
        # For safety below, we'll compute black_mob similarly.

    # compute black mobility by making a shallow turn-swap (non-mutating approach)
    # python-chess doesn't provide a direct API to cheaply count black legal moves without changing the board; we use copy
    board_copy = board.copy()
    board_copy.turn = not board.turn
    black_mob = len(list(board_copy.legal_moves))

    score += w["mobility"] * (white_mob - black_mob)

    # ---------------------------
    # 4) Center control
    # ---------------------------
    for sq in (chess.D4, chess.D5, chess.E4, chess.E5):
        p = board.piece_at(sq)
        if p:
            score += w["center"] if p.color == chess.WHITE else -w["center"]

    # ---------------------------
    # 5) Passed pawns + pawn advancement urgency
    # ---------------------------
    for color, sign in [(chess.WHITE, +1), (chess.BLACK, -1)]:
        for sq in board.pieces(chess.PAWN, color):
            # pawn rank (encourage pushing)
            rank = chess.square_rank(sq) if color == chess.WHITE else 7 - chess.square_rank(sq)
            score += sign * (w["pawn_rank_weight"] * rank)
            if is_passed_pawn(board, sq, color):
                score += sign * (w["passed_base"] + w["passed_per_rank"] * rank)

    # ---------------------------
    # 6) King safety (midgame) but allow activity in endgame
    # ---------------------------
    score += king_safety_eval(board, chess.WHITE, w)
    score -= king_safety_eval(board, chess.BLACK, w)

    # ---------------------------
    # 7) Check penalty (keeps engine from walking into checks)
    # ---------------------------
    if board.is_check():
        # penalty for side to move being in check
        if board.turn == chess.WHITE:
            score -= w["check_penalty"]
        else:
            score += w["check_penalty"]

    # ---------------------------
    # 8) Endgame adjustments (convert advantages, push kings to corner if winning)
    # ---------------------------
    if is_endgame(board):
        # king distance: smaller is better (helps forcing mates)
        wk = board.king(chess.WHITE)
        bk = board.king(chess.BLACK)
        if wk is not None and bk is not None:
            dist = chess.square_distance(wk, bk)
            score += w["endgame_king_dist_weight"] * (14 - dist)

        # edge bonus: penalize your king being too central when defending; reward pushing enemy king to edge
        def edge_bonus(sq):
            f = chess.square_file(sq)
            r = chess.square_rank(sq)
            dist_center = min(f, 7 - f) + min(r, 7 - r)
            return (6 - dist_center) * w["endgame_edge_bonus"]

        score += edge_bonus(board.king(chess.BLACK))  # good to push black king to edge
        score -= edge_bonus(board.king(chess.WHITE))

        # increase mobility weight in endgame
        score += w["endgame_mobility_mult"] * (white_mob - black_mob)

    # ---------------------------
    # 9) Anti-fortress logic (force progress when no captures)
    # ---------------------------
    legal_caps_exist = any(board.is_capture(m) for m in board.legal_moves)
    if not legal_caps_exist:
        for color, sign in [(chess.WHITE, +1), (chess.BLACK, -1)]:
            best_rank = 0
            for sq in board.pieces(chess.PAWN, color):
                rank = chess.square_rank(sq) if color == chess.WHITE else 7 - chess.square_rank(sq)
                if rank > best_rank:
                    best_rank = rank
            score += sign * (best_rank * w["anti_fortress_pawn_progress"])

    # ---------------------------
    # 10) Repetition / contempt (tournament exploit)
    # ---------------------------
    if board.is_repetition():
        score -= w["repetition_penalty"]

    score += w["contempt"] if board.turn == chess.WHITE else -w["contempt"]

    # ---------------------------
    # 11) Terminals
    # ---------------------------
    if board.is_checkmate():
        return w["mate_score"] if board.turn == chess.BLACK else -w["mate_score"]
    if board.is_stalemate():
        return w["stalemate_score"]

    return score


# =========================================================
# Main evaluator
# =========================================================
def REvaluator2(board: chess.Board) -> float:
    w = WEIGHTS2
    score = 0.0

    # ---------------------------
    # 1) Material (compressed values to encourage dynamic play)
    # ---------------------------
    piece_values = {
        chess.PAWN:   w["pawn"],
        chess.KNIGHT: w["knight"],
        chess.BISHOP: w["bishop"],
        chess.ROOK:   w["rook"],
        chess.QUEEN:  w["queen"],
        chess.KING:   w["king"],
    }

    for pt, val in piece_values.items():
        score += val * (len(board.pieces(pt, chess.WHITE)) - len(board.pieces(pt, chess.BLACK)))

    # ---------------------------
    # 2) Trade / capture safety (simple, stable)
    #    We penalize positions where our pieces are attacked proportionally,
    #    but less extremely than before (keeps engine willing to sacrifice tactically).
    # ---------------------------
    for color, sign in [(chess.WHITE, +1), (chess.BLACK, -1)]:
        opponent = not color
        for sq in board.pieces(chess.PAWN, color) | board.pieces(chess.KNIGHT, color) | \
                  board.pieces(chess.BISHOP, color) | board.pieces(chess.ROOK, color) | \
                  board.pieces(chess.QUEEN, color):
            # sq is an int; convert to piece
            piece = board.piece_at(sq)
            if piece is None:
                continue
            base_val = piece_values[piece.piece_type]
            attackers = board.attackers(opponent, sq)
            if attackers:
                worst_trade = -9999
                for a in attackers:
                    a_piece = board.piece_at(a)
                    if a_piece:
                        trade = piece_values[a_piece.piece_type] - base_val
                        if trade > worst_trade:
                            worst_trade = trade
                # smaller multiplier than before: keeps tactical willingness
                score += sign * worst_trade * w["trade_penalty_mult"]

    # ---------------------------
    # 3) Mobility (balanced)
    # ---------------------------
    # compute mobility for both sides cleanly without mutating board.turn
    white_mob = len(list(board.legal_moves_of_color(chess.WHITE))) if hasattr(board, "legal_moves_of_color") else None
    if white_mob is None:
        # fallback if python-chess version is older: simulate
        white_mob = 0
        for move in board.legal_moves:
            if board.turn == chess.WHITE:
                white_mob += 1
        # less precise fallback; but we will compute black_mob using a simple swap
        # For safety below, we'll compute black_mob similarly.

    # compute black mobility by making a shallow turn-swap (non-mutating approach)
    # python-chess doesn't provide a direct API to cheaply count black legal moves without changing the board; we use copy
    board_copy = board.copy()
    board_copy.turn = not board.turn
    black_mob = len(list(board_copy.legal_moves))

    score += w["mobility"] * (white_mob - black_mob)

    # ---------------------------
    # 4) Center control
    # ---------------------------
    for sq in (chess.D4, chess.D5, chess.E4, chess.E5):
        p = board.piece_at(sq)
        if p:
            score += w["center"] if p.color == chess.WHITE else -w["center"]

    # ---------------------------
    # 5) Passed pawns + pawn advancement urgency
    # ---------------------------
    for color, sign in [(chess.WHITE, +1), (chess.BLACK, -1)]:
        for sq in board.pieces(chess.PAWN, color):
            # pawn rank (encourage pushing)
            rank = chess.square_rank(sq) if color == chess.WHITE else 7 - chess.square_rank(sq)
            score += sign * (w["pawn_rank_weight"] * rank)
            if is_passed_pawn(board, sq, color):
                score += sign * (w["passed_base"] + w["passed_per_rank"] * rank)

    # ---------------------------
    # 6) King safety (midgame) but allow activity in endgame
    # ---------------------------
    score += king_safety_eval(board, chess.WHITE, w)
    score -= king_safety_eval(board, chess.BLACK, w)

    # ---------------------------
    # 7) Check penalty (keeps engine from walking into checks)
    # ---------------------------
    if board.is_check():
        # penalty for side to move being in check
        if board.turn == chess.WHITE:
            score -= w["check_penalty"]
        else:
            score += w["check_penalty"]

    # ---------------------------
    # 8) Endgame adjustments (convert advantages, push kings to corner if winning)
    # ---------------------------
    if is_endgame(board):
        # king distance: smaller is better (helps forcing mates)
        wk = board.king(chess.WHITE)
        bk = board.king(chess.BLACK)
        if wk is not None and bk is not None:
            dist = chess.square_distance(wk, bk)
            score += w["endgame_king_dist_weight"] * (14 - dist)

        # edge bonus: penalize your king being too central when defending; reward pushing enemy king to edge
        def edge_bonus(sq):
            f = chess.square_file(sq)
            r = chess.square_rank(sq)
            dist_center = min(f, 7 - f) + min(r, 7 - r)
            return (6 - dist_center) * w["endgame_edge_bonus"]

        score += edge_bonus(board.king(chess.BLACK))  # good to push black king to edge
        score -= edge_bonus(board.king(chess.WHITE))

        # increase mobility weight in endgame
        score += w["endgame_mobility_mult"] * (white_mob - black_mob)

    # ---------------------------
    # 9) Anti-fortress logic (force progress when no captures)
    # ---------------------------
    legal_caps_exist = any(board.is_capture(m) for m in board.legal_moves)
    if not legal_caps_exist:
        for color, sign in [(chess.WHITE, +1), (chess.BLACK, -1)]:
            best_rank = 0
            for sq in board.pieces(chess.PAWN, color):
                rank = chess.square_rank(sq) if color == chess.WHITE else 7 - chess.square_rank(sq)
                if rank > best_rank:
                    best_rank = rank
            score += sign * (best_rank * w["anti_fortress_pawn_progress"])

    # ---------------------------
    # 10) Repetition / contempt (tournament exploit)
    # ---------------------------
    if board.is_repetition():
        score -= w["repetition_penalty"]

    score += w["contempt"] if board.turn == chess.WHITE else -w["contempt"]

    # ---------------------------
    # 11) Terminals
    # ---------------------------
    if board.is_checkmate():
        return w["mate_score"] if board.turn == chess.BLACK else -w["mate_score"]
    if board.is_stalemate():
        return w["stalemate_score"]

    return score