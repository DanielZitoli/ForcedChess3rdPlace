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


def chatEvaluator(board: chess.Board) -> float:
    """
    Evaluation function optimized for forced-capture chess variants.
    Prioritizes piece safety over raw material.
    """

    # Material values (down-weighted; safety matters more)
    val = {
        chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
        chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000
    }

    score = 0.0

    # -----------------------------------------
    # 1. MATERIAL (light)
    # -----------------------------------------
    for piece_type, v in val.items():
        score += len(board.pieces(piece_type, chess.WHITE)) * v
        score -= len(board.pieces(piece_type, chess.BLACK)) * v

    # -----------------------------------------
    # 2. PIECE SAFETY / CAPTURE AVOIDANCE
    # -----------------------------------------
    def attackers(color, sq):
        return board.attackers(color, sq)

    for color, sign in [(chess.WHITE, +1), (chess.BLACK, -1)]:
        opp = not color

        for pt, v in val.items():
            for sq in board.pieces(pt, color):
                opp_attackers = attackers(opp, sq)
                if not opp_attackers:
                    continue

                my_value = v
                best_trade = -9999

                for attacker_sq in opp_attackers:
                    attacker_piece = board.piece_at(attacker_sq)
                    attacker_value = val[attacker_piece.piece_type]
                    trade_delta = attacker_value - my_value
                    best_trade = max(best_trade, trade_delta)

                score += sign * best_trade * 0.5  # toned down

    # -----------------------------------------
    # 3. MOBILITY (huge for breaking draws)
    # -----------------------------------------
    score += 5 * (len(list(board.legal_moves)) if board.turn == chess.WHITE else -len(list(board.legal_moves)))

    # -----------------------------------------
    # 4. CENTER CONTROL
    # -----------------------------------------
    center = [chess.D4, chess.D5, chess.E4, chess.E5]
    for sq in center:
        if board.piece_at(sq):
            piece = board.piece_at(sq)
            bonus = 15
            score += bonus if piece.color == chess.WHITE else -bonus
    # -----------------------------------------
    # 5. PASSED PAWNS
    # -----------------------------------------
    def is_passed(board, sq, color):
        rank_dir = 1 if color == chess.WHITE else -1
        file = chess.square_file(sq)
        sq_rank = chess.square_rank(sq)
        for r in range(sq_rank + rank_dir, 8 if color == chess.WHITE else -1, rank_dir):
            for f in [file-1, file, file+1]:
                if 0 <= f < 8:
                    if board.piece_at(chess.square(f, r)) and \
                       board.piece_at(chess.square(f, r)).piece_type == chess.PAWN and \
                       board.piece_at(chess.square(f, r)).color != color:
                        return False
        return True

    for color, sign in [(chess.WHITE, +1), (chess.BLACK, -1)]:
        for sq in board.pieces(chess.PAWN, color):
            if is_passed(board, sq, color):
                rank = chess.square_rank(sq) if color == chess.WHITE else (7 - chess.square_rank(sq))
                score += sign * (30 + 10 * rank)

    # -----------------------------------------
    # 6. KING SAFETY
    # -----------------------------------------
    wk = board.king(chess.WHITE)
    bk = board.king(chess.BLACK)

    if board.attackers(chess.BLACK, wk):
        score -= 60
    if board.attackers(chess.WHITE, bk):
        score += 60

    # -----------------------------------------
    # 7. CHECK BONUS (fixed)
    # -----------------------------------------
    if board.is_check():
        # reward giving check, not being in check
        if board.turn == chess.WHITE:     # white to move → white is checked
            score -= 150
        else:
            score += 150


    # -----------------------------------------
    # 8. TERMINALS
    # -----------------------------------------
    if board.is_checkmate():
        return +999999 if board.turn == chess.BLACK else -999999
    if board.is_stalemate():
        return -50  # avoid draws
    
    # -----------------------------------------
    # 9. CONTEMPT FACTOR (AVOID EQUAL DRAWISH LINES)
    # -----------------------------------------
    contempt = 30
    score += contempt if board.turn == chess.WHITE else -contempt

    return score