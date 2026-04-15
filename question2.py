from copy import deepcopy
import os
from collections import deque

# --------------------------
# GLOBAL COUNTERS
# --------------------------
BACKTRACK_CALLS = 0
FAILURES = 0

# --------------------------
# READ BOARD
# --------------------------
def read_board(filename):
    if not os.path.exists(filename):
        print("ERROR: File not found ->", filename)
        return None

    board = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if len(line) == 9:
                board.append([int(x) for x in line])
    return board

# --------------------------
# PRINT BOARD
# --------------------------
def print_board(board):
    for row in board:
        print(" ".join(str(x) for x in row))
    print()

# --------------------------
# NEIGHBORS
# --------------------------
def get_neighbors(r, c):
    neighbors = set()

    for i in range(9):
        neighbors.add((r, i))
        neighbors.add((i, c))

    br = (r // 3) * 3
    bc = (c // 3) * 3

    for i in range(br, br + 3):
        for j in range(bc, bc + 3):
            neighbors.add((i, j))

    neighbors.discard((r, c))
    return neighbors

# --------------------------
# DOMAINS
# --------------------------
def initialize_domains(board):
    domains = {}
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                domains[(r, c)] = set(range(1, 10))
            else:
                domains[(r, c)] = {board[r][c]}
    return domains

# --------------------------
# AC-3 (CORRECT)
# --------------------------
def ac3(domains):
    queue = deque([(xi, xj) for xi in domains for xj in get_neighbors(*xi)])

    while queue:
        xi, xj = queue.popleft()

        if revise(domains, xi, xj):
            if len(domains[xi]) == 0:
                return False

            for xk in get_neighbors(*xi):
                if xk != xj:
                    queue.append((xk, xi))

    return True

def revise(domains, xi, xj):
    revised = False
    remove_vals = set()

    for x in domains[xi]:
        # valid if at least one different value exists in neighbor
        if all(x == y for y in domains[xj]):
            remove_vals.add(x)
            revised = True

    for x in remove_vals:
        domains[xi].remove(x)

    return revised

# --------------------------
# MRV (SELECT VARIABLE)
# --------------------------
def select_unassigned(domains):
    vars_ = [v for v in domains if len(domains[v]) > 1]
    if not vars_:
        return None
    return min(vars_, key=lambda v: len(domains[v]))

# --------------------------
# FORWARD CHECKING
# --------------------------
def forward_check(domains, var, value):
    new_domains = deepcopy(domains)
    new_domains[var] = {value}

    for nb in get_neighbors(*var):
        if value in new_domains[nb] and len(new_domains[nb]) > 1:
            new_domains[nb].discard(value)

            if len(new_domains[nb]) == 0:
                return None

    return new_domains

# --------------------------
# CHECK COMPLETE
# --------------------------
def is_complete(domains):
    return all(len(domains[v]) == 1 for v in domains)

# --------------------------
# CONSISTENCY CHECK
# --------------------------
def is_consistent(domains, var):
    r, c = var
    val = list(domains[var])[0]

    for nr, nc in get_neighbors(r, c):
        if len(domains[(nr, nc)]) == 1:
            if list(domains[(nr, nc)])[0] == val:
                return False
    return True

# --------------------------
# BACKTRACKING (CORRECT)
# --------------------------
def backtrack(domains):
    global BACKTRACK_CALLS, FAILURES
    BACKTRACK_CALLS += 1

    if is_complete(domains):
        return domains

    var = select_unassigned(domains)
    if var is None:
        return domains

    for value in list(domains[var]):
        new_domains = forward_check(domains, var, value)

        if new_domains:
            new_domains[var] = {value}

            if is_consistent(new_domains, var):
                result = backtrack(new_domains)
                if result:
                    return result

    FAILURES += 1
    return None

# --------------------------
# CONVERT TO BOARD
# --------------------------
def domains_to_board(domains):
    board = [[0]*9 for _ in range(9)]
    for (r, c), v in domains.items():
        board[r][c] = list(v)[0]
    return board

# --------------------------
# SOLVE
# --------------------------
def solve(filename):
    global BACKTRACK_CALLS, FAILURES
    BACKTRACK_CALLS = 0
    FAILURES = 0

    print("Solving:", filename)

    board = read_board(filename)
    if not board:
        return

    domains = initialize_domains(board)

    # AC-3 preprocessing only
    if not ac3(domains):
        print("No solution (AC-3 failed)")
        return

    result = backtrack(domains)

    if result:
        print_board(domains_to_board(result))
    else:
        print("No solution found!")

    print("Backtracks:", BACKTRACK_CALLS)
    print("Failures:", FAILURES)
    print("-"*40)

# --------------------------
# MAIN
# --------------------------
if __name__ == "__main__":
    solve("easy.txt")
    solve("medium.txt")
    solve("hard.txt")
    solve("veryhard.txt")

