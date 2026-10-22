"""
Configuration for the Minimax Alpha-Beta Reversi engine.

SEARCH_DEPTH controls the number of half-moves (plies) the engine looks ahead.
Higher depth produces stronger play at the cost of computation time.

Typical depth vs. compute time on a standard desktop (8x8 board):
  depth=3  -- < 0.05 s  (very fast, beginner strength)
  depth=4  -- 0.05-0.2 s  (fast, decent play)
  depth=5  -- 0.2-0.8 s  (good balance)
  depth=6  -- 0.5-3 s    (strong; noticeable pause on first few moves)
  depth=7+ -- several seconds; use only for endgame analysis

Evaluation weights:
  CORNER_WEIGHT   -- score awarded per net corner advantage (corners are the
                     most stable cells on a Reversi board and cannot be flipped)
  X_SQUARE_PENALTY -- penalty for occupying a cell diagonally adjacent to an
                      empty corner (X-squares give the opponent easy corner access)
  MOBILITY_WEIGHT -- multiplier for the net mobility advantage
                     (having more legal moves restricts the opponent)
  PARITY_WEIGHT   -- multiplier for disc-count parity
                     (disc parity matters more in the endgame than the opening)

KILLER_MOVE_ENABLED: try corner and blocking moves first during search to
improve alpha-beta cutoffs (move ordering heuristic).
"""

SEARCH_DEPTH = 5

CORNER_WEIGHT    = 25   # score per net corner captured
X_SQUARE_PENALTY = 8    # deducted per X-square adjacent to an empty corner
MOBILITY_WEIGHT  = 2    # multiplier for net mobility score
PARITY_WEIGHT    = 1    # multiplier for disc-parity score

KILLER_MOVE_ENABLED = True
