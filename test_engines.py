from random_engine import RandomEngine
from minimax_engine import MinimaxEngine
from evaluators import materialEvaluator
from simulator import simulateGame, simulateTournament

randomEngine = RandomEngine()
simpleMinimax = MinimaxEngine(name="Simple minimax", use_alphabeta=False, evaluator=materialEvaluator)
alphaBetaMinimax = MinimaxEngine(name="Minimax with alpha-beta pruning", use_alphabeta=True, evaluator=materialEvaluator)

simulateGame(randomEngine, alphaBetaMinimax)
simulateGame(randomEngine, simpleMinimax)
