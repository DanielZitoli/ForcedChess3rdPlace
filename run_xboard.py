#!/usr/bin/env python3
import sys
from xboard_interface import XBoardHandler
from minimax_engine import MinimaxEngine
from evaluators import materialEvaluator

"""
if xboard is downloaded we should be able to run a game against our engine with the command `xboard -fcp [this_file]` 
"""

if __name__ == "__main__":
  bestEngine = MinimaxEngine(evaluator=materialEvaluator, use_alphabeta=True)
  handler = XBoardHandler(bestEngine)
  for line in sys.stdin:
    handler.handle_command(line)