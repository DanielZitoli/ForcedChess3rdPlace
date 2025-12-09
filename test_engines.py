from random_engine import RandomEngine
from minimax_engine import MinimaxEngine
from evaluators import materialEvaluator, chatEvaluator
from simulator import simulateGame, simulateTournament

randomEngine = RandomEngine()
chatEngine = MinimaxEngine(name="Chat evaluator engine", use_alphabeta=True, evaluator=chatEvaluator)
simpleMinimax = MinimaxEngine(name="Simple minimax", use_alphabeta=False, evaluator=materialEvaluator)
alphaBetaMinimax = MinimaxEngine(name="Minimax with alpha-beta pruning", use_alphabeta=True, evaluator=materialEvaluator)

simulateGame(randomEngine, alphaBetaMinimax)
simulateGame(randomEngine, simpleMinimax)
simulateTournament(chatEngine, alphaBetaMinimax, n=5)