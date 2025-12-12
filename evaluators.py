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


import chess

# =========================================================
#   HELPER: strict endgame detection
# =========================================================
def is_endgame(board: chess.Board) -> bool:
    """
    Very strict endgame definition:
    Only a few non-pawn pieces left on the board.
    """
    material = 0
    for p in board.piece_map().values():
        if p.piece_type not in (chess.KING, chess.PAWN):
            material += 1
    return material <= 4


# =========================================================
#   HELPER: passed pawn detection
# =========================================================
def is_passed_pawn(board: chess.Board, sq: int, color: bool) -> bool:
    file = chess.square_file(sq)
    rank = chess.square_rank(sq)

    direction = 1 if color == chess.WHITE else -1
    opp = not color

    r = rank + direction
    while 0 <= r < 8:
        for f in (file - 1, file, file + 1):
            if 0 <= f < 8:
                target = chess.square(f, r)
                p = board.piece_at(target)
                if p and p.color == opp and p.piece_type == chess.PAWN:
                    return False
        r += direction

    return True


# =========================================================
#   HELPER: king safety evaluation
# =========================================================
def king_safety(board: chess.Board, color: bool) -> float:
    ksq = board.king(color)
    if ksq is None:
        return 0

    score = 0
    rank = chess.square_rank(ksq)
    file = chess.square_file(ksq)

    # Early and mid-game: STAY SAFE
    if not is_endgame(board):
        home_rank = 0 if color == chess.WHITE else 7

        # Penalty for leaving home rank
        if rank != home_rank:
            score -= 80 * abs(rank - home_rank)

        # Penalty for entering center (files d/e)
        if file in (3, 4):
            score -= 60

        # Penalty if king is attacked at all
        if board.attackers(not color, ksq):
            score -= 120

    # Endgame: king SHOULD be active
    else:
        # Bonus for centralization
        center = {chess.D4, chess.D5, chess.E4, chess.E5}
        if ksq in center:
            score += 40

    return score


# =========================================================
#   MAIN EVALUATOR
# =========================================================
def chatEvaluator(board: chess.Board) -> float:

    # Material values
    val = {
        chess.PAWN:   100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK:   500,
        chess.QUEEN:  900,
        chess.KING:   20000
    }

    opp = not board.turn
    score = 0.0

    # =====================================================
    # 1. MATERIAL
    # =====================================================
    for pt, v in val.items():
        score += len(board.pieces(pt, chess.WHITE)) * v
        score -= len(board.pieces(pt, chess.BLACK)) * v

    # =====================================================
    # 2. CAPTURE SAFETY / TRADE QUALITY
    # =====================================================
    for color, sign in [(chess.WHITE, +1), (chess.BLACK, -1)]:
        other = not color
        for sq, piece in board.piece_map().items():
            if piece.color != color:
                continue

            pt_value = val[piece.piece_type]

            attackers = board.attackers(other, sq)
            if attackers:
                # Best trade outcome
                best = -9999
                for a_sq in attackers:
                    a_piece = board.piece_at(a_sq)
                    if a_piece:
                        trade = val[a_piece.piece_type] - pt_value
                        if trade > best:
                            best = trade
                score += sign * best * 0.5

    # =====================================================
    # 3. MOBILITY (REVERSED BONUS FOR FORCED CAPTURE CHESS)
    #    - having MORE legal moves is GOOD (not always true
    #      in standard chess, but extremely important here)
    # =====================================================
    legal = list(board.legal_moves)
    mobility = len(legal)

    if board.turn == chess.WHITE:
        score += mobility * 3
    else:
        score -= mobility * 3

    # =====================================================
    # 4. CENTER CONTROL
    # =====================================================
    for sq in (chess.D4, chess.D5, chess.E4, chess.E5):
        p = board.piece_at(sq)
        if p:
            bonus = 20
            if p.color == chess.WHITE:
                score += bonus
            else:
                score -= bonus

    # =====================================================
    # 5. PASSED PAWNS
    # =====================================================
    for color, sign in [(chess.WHITE, +1), (chess.BLACK, -1)]:
        for sq in board.pieces(chess.PAWN, color):
            if is_passed_pawn(board, sq, color):
                rank = chess.square_rank(sq)
                advance = rank if color == chess.WHITE else (7 - rank)
                score += sign * (40 + advance * 10)

    # =====================================================
    # 6. KING SAFETY
    # =====================================================
    score += king_safety(board, chess.WHITE)
    score -= king_safety(board, chess.BLACK)

    # =====================================================
    # 7. CHECK BONUS
    # =====================================================
    if board.is_check():
        if board.turn == chess.WHITE:  # white is being checked
            score -= 150
        else:
            score += 150

    # =====================================================
    # 8. AVOID 3-MOVE REPETITION (stops king shuffling)
    # =====================================================
    if board.is_repetition():
        score -= 300  # VERY strong anti-draw term

    # =====================================================
    # 9. TERMINALS
    # =====================================================
    if board.is_checkmate():
        return +999999 if board.turn == chess.BLACK else -999999
    if board.is_stalemate():
        return -200  # forced draws are bad

    # =====================================================
    # 10. CONTEMPT: prefer winning over drawing
    # =====================================================
    score += 25 if board.turn == chess.WHITE else -25

    return score
