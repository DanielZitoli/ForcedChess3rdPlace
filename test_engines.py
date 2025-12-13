from random_engine import RandomEngine
from minimax_engine import MinimaxEngine
from evaluators import materialEvaluator, REvaluator, REvaluator2
from simulator import simulateGame, simulateTournament

randomEngine = RandomEngine()
REngine = MinimaxEngine(name="Chat evaluator engine", use_alphabeta=True, evaluator=REvaluator)
REngine2 = MinimaxEngine(name="Chat evaluator engine", use_alphabeta=True, evaluator=REvaluator2)
simpleMinimax = MinimaxEngine(name="Simple minimax", use_alphabeta=False, evaluator=materialEvaluator)
alphaBetaMinimax = MinimaxEngine(name="Minimax with alpha-beta pruning", use_alphabeta=True, evaluator=materialEvaluator)

#simulateGame(randomEngine, alphaBetaMinimax)
#simulateGame(randomEngine, simpleMinimax)
simulateTournament(REngine2, REngine, n=1)
simulateTournament(REngine, REngine2, n=1)