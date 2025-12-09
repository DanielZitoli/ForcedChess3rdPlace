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
        chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
        chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 200
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
    def attackers_of_color(square, color):
      return board.attackers(color, square)

    for color, sign in [(chess.WHITE, +1), (chess.BLACK, -1)]:
      opp = not color

      for piece_type, my_val in val.items():
        for sq in board.pieces(piece_type, color):

            # All opponent attackers on this piece
            opp_attackers = list(attackers_of_color(sq, opp))

            if not opp_attackers:
                continue  # no trade possible

            # Value of MY piece being captured
            victim_value = my_val

            # For each attacker, compute trade delta
            # attacker_value - victim_value
            best_trade = None

            for attacker_sq in opp_attackers:
                attacker_piece = board.piece_at(attacker_sq)
                attacker_value = val[attacker_piece.piece_type]

                trade_delta = attacker_value - victim_value

                if best_trade is None or trade_delta > best_trade:
                    best_trade = trade_delta

            # If best_trade > 0, this is a favorable trade for "color"
            # Example: They capture your knight (3) with a rook (5): +2
            score += sign * best_trade * 1.5

    # -----------------------------------------
    # 4. WINNING / LOSING THE GAME
    # -----------------------------------------

    # If the game is over, assign terminal values
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            # white is checkmated → black wins
            return -99999
        else:
            # black is checkmated → white wins
            return +99999

    if board.is_stalemate():
        return 0  # or small bonus/penalty if desired

    # -----------------------------------------
    # Incentivize approaching checkmate
    # -----------------------------------------
    # Give a bonus for checking the opponent
    if board.is_check():
        if board.turn == chess.WHITE:
            score += 50
        else:
            score -= 50

    # -----------------------------------------
    # Improve King Safety (simple but effective)
    # -----------------------------------------
    # Penalize your king being attacked
    white_king_sq = board.king(chess.WHITE)
    black_king_sq = board.king(chess.BLACK)

    if board.attackers(chess.BLACK, white_king_sq):
        score -= 40
    if board.attackers(chess.WHITE, black_king_sq):
        score += 40

    return score