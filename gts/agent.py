"""
An AI player for Othello.
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move
state_to_score = {}

def eprint(*args, **kwargs):  # you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)


# Method to compute utility value of terminal state
def compute_utility(board, color):
    # IMPLEMENT
    dark, light = get_score(board)
    if color == 1:  # me is dark
        return dark - light
    else:  # me is light
        return light - dark

# Better heuristic value of board
def compute_heuristic(board, color):  # not implemented, optional
    # IMPLEMENT
    # define the score of each point to be the number of blocks that can be flipped
    corn_bonus = 10
    side_bonus = 5
    num_move_bonus = 1

    if color == 1:
        opponent = 2
    else:
        opponent = 1

    n = len(board)
    dark, light = get_score(board)
    if color == 1:  # me is dark
        score = dark - light
    else:  # me is light
        score = light - dark
    for i in range(n):
        for j in range(n):
            # corner bonus
            if i == (0 or n) and j == (0 or n):
                if board[i][j] == color:
                    score += corn_bonus
                elif board[i][j] == opponent:
                    score -= corn_bonus
            elif i == (0 or n) or j == (0 or n):
                if board[i][j] == color:
                    score += side_bonus
                elif board[i][j] == opponent:
                    score -= side_bonus

    # score plus the number of moves to make
    moves = len(get_possible_moves(board, color))
    oppo_move = len(get_possible_moves(board, opponent))
    score += moves * num_move_bonus
    score -= oppo_move * num_move_bonus

    # different strategies: early to occupy corners and side, later to change as much as possible
    return score  # change this!


############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching=0):
    # IMPLEMENT (and replace the line below)
    # base case, there is no more possible moves
    lst = []
    for i in range(len(board)):
        lst.append(tuple(board[i]))
    tuple_board = tuple(lst)
    if caching:
        if tuple_board in state_to_score:
            return state_to_score[tuple_board]
    if color == 1:
        opponent = 2
    else:
        opponent = 1
    moves = get_possible_moves(board, opponent)
    if len(moves) == 0 or limit == 0:
        # if caching:
        #     state_to_score[tuple_board] = (None, compute_utility(board, color))
        return None, compute_utility(board, color)
    # else, recursive steps.
    # for each possible moves, call max for each one, and return the min of these
    min_utility = float("inf")
    move = (0, 0)
    for i, j in moves:
        next_state = play_move(board, opponent, i, j)
        temp_move, temp_utility = minimax_max_node(next_state, color, limit - 1, caching)
        # if caching:
        #     state_to_score[next_state] = (temp_move, temp_utility)
        if temp_utility < min_utility:
            min_utility = temp_utility
            move = (i, j)
    if caching:
        state_to_score[tuple_board] = (move, min_utility)
    return move, min_utility


def minimax_max_node(board, color, limit, caching=0):  # returns highest possible utility
    # IMPLEMENT (and replace the line below)
    # base case, there are no more possible moves
    lst = []
    for i in range(len(board)):
        lst.append(tuple(board[i]))
    tuple_board = tuple(lst)
    if caching:
        if tuple_board in state_to_score:
            return state_to_score[tuple_board]
    moves = get_possible_moves(board, color)


    if len(moves) == 0 or limit == 0:
        # if caching:
        #     state_to_score[tuple_board] = (None, compute_utility(board, color))
        return None, compute_utility(board, color)
    # else, recursive steps
    # for each possible moves, call min for each possible moves, return the min one
    max_utility = (-1) * float("inf")
    move = (0, 0)
    for i, j in moves:
        next_state = play_move(board, color, i, j)
        temp_move, temp_utility = minimax_min_node(next_state, color, limit - 1, caching)
        # if caching:
        #     state_to_score[next_state] = (temp_move, temp_utility)
        if temp_utility > max_utility:
            max_utility = temp_utility
            move = (i, j)
    if caching:
        state_to_score[tuple_board] = (move, max_utility)
    return move, max_utility



def select_move_minimax(board, color, limit, caching=0):
    """
    Given a board and a player color, decide on a move.
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.
    """
    state_to_score.clear()
    return minimax_max_node(board, color, limit)[0]


def alphabeta_min_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    # IMPLEMENT (and replace the line below)
    lst = []
    for i in range(len(board)):
        lst.append(tuple(board[i]))
    tuple_board = tuple(lst)
    if caching:
        if tuple_board in state_to_score:
            return state_to_score[tuple_board]
    if color == 1:
        opponent = 2
    else:
        opponent = 1
    moves = get_possible_moves(board, opponent)
    if len(moves) == 0 or limit == 0:
        # if caching:
        #     state_to_score[tuple_board] = (None, compute_utility(board, color))
        return None, compute_utility(board, color)
    move = (0, 0)
    min_beta = beta
    # ordering
    if ordering:
        utility_list = [compute_utility(play_move(board, color, k[0], k[1]), color) for k in moves]
        lst = []
        for i in range(len(utility_list)):
            lst.append((utility_list, moves))
        lst.sort(key=take_first, reverse=True)
        moves = [lst[i][1] for i in range(len(lst))]
    for i, j in moves:
        next_state = play_move(board, opponent, i, j)
        temp_move, temp_beta = alphabeta_max_node(next_state, color, alpha, beta, limit-1, caching, ordering)
        if caching:
            state_to_score[next_state] = (temp_move, temp_beta)
        if temp_beta < min_beta:
            min_beta = temp_beta
            move = (i, j)
        if alpha >= min_beta:
            break
        beta = min(beta, min_beta)
    if caching:
        state_to_score[tuple_board] = (move, min_beta)
    return move, min_beta

############ ALPHA-BETA PRUNING #####################
def take_first(element):
    return element[0]


def alphabeta_max_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    # IMPLEMENT (and replace the line below)
    # print(state_to_score)
    # print("caching", caching)
    lst = []
    for i in range(len(board)):
        lst.append(tuple(board[i]))
    tuple_board = tuple(lst)
    if caching and (tuple_board in state_to_score):
        return state_to_score[tuple_board]
    moves = get_possible_moves(board, color)
    if len(moves) == 0 or limit == 0:
        if caching:
            state_to_score[tuple_board] = (None, compute_utility(board, color))
        return None, compute_utility(board, color)
    max_alpha = alpha
    move = (0, 0)
    # ordering
    if ordering:
        utility_list = [compute_utility(play_move(board, color, k[0], k[1]), color) for k in moves]
        lst = []
        for i in range(len(utility_list)):
            lst.append((utility_list, moves))
        lst.sort(key=take_first, reverse=True)
        moves = [lst[i][1] for i in range(len(lst))]
    # if ordering:
    #     moves.sort(key=lambda k: compute_utility(play_move(board, color, k[0], k[1]), color))
    #     moves.reverse()
    for i, j in moves:
        next_state = play_move(board, color, i, j)
        temp_move, temp_alpha = alphabeta_min_node(next_state, color, alpha, beta, limit-1, caching, ordering)
        # if caching:
        #     state_to_score[next_state] = (temp_move, temp_alpha)
        if temp_alpha > max_alpha:
            max_alpha = temp_alpha
            move = (i, j)
        if max_alpha >= beta:
            break
        alpha = max(alpha, max_alpha)
    if caching:
        state_to_score[tuple_board] = (move, max_alpha)
    return move, max_alpha


def select_move_alphabeta(board, color, limit, caching=0, ordering=0):
    """
    Given a board and a player color, decide on a move.
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.
    If ordering is ON (i.e. 1), use node ordering to expedite pruning and reduce the number of state evaluations.
    If ordering is OFF (i.e. 0), do NOT use node ordering to expedite pruning and reduce the number of state evaluations.
    """
    state_to_score.clear()
    return alphabeta_max_node(board, color, alpha=(-1) * float("inf"), beta=float("inf"),
                              limit=limit, caching=caching, ordering=ordering)[0]

    # IMPLEMENT (and replace the line below)
    # return (0, 0)  # change this!


####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("Othello AI")  # First line is the name of this AI
    arguments = input().split(",")

    color = int(arguments[0])  # Player color: 1 for dark (goes first), 2 for light.
    limit = int(arguments[1])  # Depth limit
    minimax = int(arguments[2])  # Minimax or alpha beta
    caching = int(arguments[3])  # Caching
    ordering = int(arguments[4])  # Node-ordering (for alpha-beta only)

    if (minimax == 1):
        eprint("Running MINIMAX")
    else:
        eprint("Running ALPHA-BETA")

    if (caching == 1):
        eprint("State Caching is ON")
    else:
        eprint("State Caching is OFF")

    if (ordering == 1):
        eprint("Node Ordering is ON")
    else:
        eprint("Node Ordering is OFF")

    if (limit == -1):
        eprint("Depth Limit is OFF")
    else:
        eprint("Depth Limit is ", limit)

    if (minimax == 1 and ordering == 1): eprint("Node Ordering should have no impact on Minimax")

    while True:  # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()
        dark_score = int(dark_score_s)
        light_score = int(light_score_s)

        if status == "FINAL":  # Game is over.
            print
        else:
            board = eval(input())  # Read in the input and turn it into a Python
            # object. The format is a list of rows. The
            # squares in each row are represented by
            # 0 : empty square
            # 1 : dark disk (player 1)
            # 2 : light disk (player 2)

            # Select the move and send it to the manager
            if (minimax == 1):  # run this if the minimax flag is given
                movei, movej = select_move_minimax(board, color, limit, caching)
            else:  # else run alphabeta
                movei, movej = select_move_alphabeta(board, color, limit, caching, ordering)

            print("{} {}".format(movei, movej))


if __name__ == "__main__":
    run_ai()