


"""
An AI player for Othello.
"""
import math
import random
import sys
import time
# below is for space cleaning convenience;
# import gc


# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

caching_dict = {}

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)

# Method to compute utility value of terminal state
def compute_utility(board, color):
    #IMPLEMENT
    # print("reached")
    player1_score, player2_score = get_score(board)
    if color == 1:
        return player1_score - player2_score
    else:
        return player2_score - player1_score


# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    #IMPLEMENT
    """
    will write custom heuristic here;
    basic idea:
    by refering to online materials, should consider edge cases and corner cases,
    as these are not that easy to be flipped
    """
    # base_utility = compute_utility(board, color)
    border_heuristic = compute_border_heuristic(board, color)

    return border_heuristic #change this!

def compute_border_heuristic(board, color):
    """
    for any stone at corners: add side_length to player;
    for any stone at border not on corner: add 2 to player; (as the stone is hard to change,
    and may lead to more stones change in color because of this stone)
    """
    side_length = len(board)
    # checking corner
    up_left = board[0][0] # value of either (0, 1, 2) representing (empty, player 1, player 2)
    up_right = board[0][side_length - 1]
    down_left = board[side_length - 1][0]
    down_right = board[side_length - 1][side_length - 1]
    corners = [up_left, up_right, down_right, down_left]
    player_heuristic = [0, 0, 0] # corresponds to None, player1, player2(indicated by color1, color2)
    for corner in corners:
        player_heuristic[corner] += side_length

    # checking edges
    for i in range(1, side_length - 1):
        up_edge = board[0][i]
        down_edge = board[side_length - 1][i]
        left_edge = board[i][0]
        right_edge = board[i][side_length - 1]
        edges = [up_edge, down_edge, left_edge, right_edge]
        for edge in edges:
            player_heuristic[edge] += 2
    # heuristic returned is the difference between color's heuristic and opponent(color)'s heuristic
    return player_heuristic[color] - player_heuristic[find_next_player(color)]


############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    #IMPLEMENT (and replace the line below)
    best_move = None, None
    # terminal state is reached when there are no moves that could be performed
    opponent = find_next_player(color)
    if (caching == 1) and (board in caching_dict):
        return best_move, caching_dict[board][opponent]
    next_possible_moves = get_possible_moves(board, opponent)
    if len(next_possible_moves) == 0 or limit == 0:
        return [(None, None), -compute_utility(board, opponent)] # returned utility is for max's
    score = - math.inf
    for move in next_possible_moves:
        next_board = play_move(board, opponent, move[0], move[1])
        # next move should be made by the different player!!!
        # "limit" requires further modifcation
        next_move = minimax_max_node(next_board, color, limit - 1, caching)
        # taking negative of next_move[1] gives min's utility
        if (- next_move[1]) > score:
            best_move = move
            score = -next_move[1]
        if caching == 1 and not (next_board in caching_dict):
            caching_dict[next_board] = {color: -score, opponent: score}
    return best_move, -score #score returned is for max's

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    #IMPLEMENT (and replace the line below)
    best_move = None, None
    if (caching == 1) and (board in caching_dict):
        return best_move, caching_dict[board][color]
    # terminal state is reached when there are no moves that could be performed
    next_possible_moves = get_possible_moves(board, color)
    if len(next_possible_moves) == 0 or limit == 0:
        return [(None, None), compute_utility(board, color)]
    # as compute_utility only yields positive scores, and higher score
    # means higher outcome for both players (differentiate by color)
    # then the initial score should always set to -infinity
    score = -math.inf
    for move in next_possible_moves:
        next_board = play_move(board, color, move[0], move[1])
        # next move should be made by the different player!!!
        # "limit" requires further modifcation
        next_move = minimax_min_node(next_board, color, limit - 1, caching)
        # taking positive of next_move[1] gives max's utility
        if (next_move[1]) > score:
            best_move = move
            score = next_move[1]
        if caching == 1 and not (next_board in caching_dict):
            opponent = find_next_player(color)
            caching_dict[next_board] = {color: score, opponent: -score}
    return best_move, score

def select_move_minimax(board, color, limit, caching = 0):
    """
    Given a board and a player color, decide on a move.
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enforce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.
    """
    '''
    to recursively call the function, should recursively set limit to be reduced by 1 every time 
    a deeper level is reached.  
    also be aware that board can be mutable... however in play_move, the function returns a completely new 
    board... guess that's what they believe should handle. 
    '''
    #IMPLEMENT (and replace the line below)
    move = minimax_max_node(board, color, limit, caching)[0]
    if caching == 1:
        caching_dict = {}
    return move


def find_next_player(color):
    """
    helper function for finding the next player to do recursive propagation of game tree

    """
    if color == 2:
        return 1
    elif color == 1:
        return 2
    else:
        print("invalid player!")
        return None

############ ALPHA-BETA PRUNING #####################
def find_successors(moves, board, color, ordering = 0):
    """
    return a list of new boards as successors
    """
    all_possible_actions = moves
    final_boards = []
    for actions in all_possible_actions:
        new_board = play_move(board, color, actions[0], actions[1])
        new_board_utility = compute_utility(new_board, color) # the utility will always be the color-player's utility
        # the higher the utility, the position should be more advanced in list
        final_boards.append([actions, new_board, new_board_utility])
    # now will conduct sort;
    if ordering == 1:
        final_boards.sort(key=successors_sort_key, reverse=True)
    # print(final_boards)
    return final_boards

def successors_sort_key(element):
    return element[2] # the utility of the board

def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    best_move = None, None
    if caching == 1 and board in caching_dict:
        return best_move, caching_dict[board]
    # need code for terminal checking here
    next_player = find_next_player(color)
    # all_moves = get_possible_moves(board, color)
    all_moves = get_possible_moves(board, next_player)
    if len(all_moves) == 0 or limit == 0:
        # return (None, None), -compute_utility(board, color) # the returned utility will be max's
        final_utility = -compute_utility(board, next_player) # this will be max's utility!!!
        # if caching == 1:
        #     caching_dict[board] = final_utility
        return (None, None), final_utility
    # successor_states = find_successors(all_moves, board, color)
    successor_states = find_successors(all_moves, board, next_player, ordering)
    value = math.inf

    for successor in successor_states:
        new_board = successor[1]
        # if (caching == 1) and (new_board in caching_dict):
        #     next_score = caching_dict[new_board]
        # else:
        next_status = alphabeta_max_node(new_board, color, alpha, beta, limit - 1, caching, ordering)
        next_score = next_status[1] # this should be alpha; consider beta is initialized as +infinity
        if caching == 1:
            caching_dict[new_board] = next_score
        if value > next_score:
            best_move, value = successor[0], next_score
        if value <= alpha:
            return best_move, value
        beta = min(beta, value)
    return best_move, value #change this!


def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    best_move = None, None
    if caching == 1 and board in caching_dict:
        return best_move, caching_dict[board]

    all_moves = get_possible_moves(board, color)
    if len(all_moves) == 0 or limit == 0:
        final_utility = compute_utility(board, color)
        # if caching == 1:
        #     caching_dict[board] = final_utility
        return best_move, final_utility
    successor_states = find_successors(all_moves, board, color, ordering)
    value = -math.inf
    for successor in successor_states:
        # next_player = find_next_player(color)
        new_board = successor[1]
        # caching: for each for-loop iterations, check whether new board state can be found in dictionary;
        # if that is: the recorded utility in dict is always max's outcome;
        # if (caching == 1) and (new_board in caching_dict):
        #     next_score = caching_dict[new_board]
        # else: # not in caching;
        next_status = alphabeta_min_node(new_board, color, alpha, beta, limit - 1, caching, ordering)
        next_score = next_status[1]
        # caching: append new board into dict
        if caching == 1:
            caching_dict[new_board] = next_score
        if value < next_score:
            best_move, value = successor[0], next_score
        if value >= beta:
            return best_move, value
        alpha = max(alpha, value)
    return best_move, value

def select_move_alphabeta(board, color, limit, caching = 0, ordering = 0):
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
    #IMPLEMENT (and replace the line below)
    # need to initialize alpha and beta to corresponding values. suggesting settings follow same idea from class,
    # thus when considering min node, should invert returned value from child, while for max, there's no need to
    # change returned value.
    alpha = -math.inf
    beta = math.inf
    # if color == 2:
    #     best_move = alphabeta_min_node(board, color, alpha, beta, limit)
    # else:
    #     best_move = alphabeta_max_node(board, color, alpha, beta, limit)
    best_move = alphabeta_max_node(board, color, alpha, beta, limit, caching, ordering)
    # according to handout, black player makes the first move. Thus can be set to max.

    # caching: by testing in python console, as long as the final board is tuple, even if a new board created with
    # a different address, dictionary access still works.
    # idea: when facing returnings, append states to dictionary; INCLUDING terminal and FOR-LOOP RETURNS!!!
    # adopted from friends' advice, should check the board at beginning of each call. (reason is simple: if
    # instead checking inside for-loop, get_all_possible_moves would be called for more times)
    if caching == 1:
        caching_dict = {}
    # ordering: see comments in find_successors()
    return best_move[0]

####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("Othello AI") # First line is the name of this AI
    arguments = input().split(",")

    color = int(arguments[0]) #Player color: 1 for dark (goes first), 2 for light.
    limit = int(arguments[1]) #Depth limit
    minimax = int(arguments[2]) #Minimax or alpha beta
    caching = int(arguments[3]) #Caching
    ordering = int(arguments[4]) #Node-ordering (for alpha-beta only)

    if (minimax == 1): eprint("Running MINIMAX")
    else: eprint("Running ALPHA-BETA")

    if (caching == 1): eprint("State Caching is ON")
    else: eprint("State Caching is OFF")

    if (ordering == 1): eprint("Node Ordering is ON")
    else: eprint("Node Ordering is OFF")

    if (limit == -1): eprint("Depth Limit is OFF")
    else: eprint("Depth Limit is ", limit)

    if (minimax == 1 and ordering == 1): eprint("Node Ordering should have no impact on Minimax")

    while True: # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()
        dark_score = int(dark_score_s)
        light_score = int(light_score_s)

        if status == "FINAL": # Game is over.
            print("game is over")
        else:
            board = eval(input()) # Read in the input and turn it into a Python
            # object. The format is a list of rows. The
            # squares in each row are represented by
            # 0 : empty square
            # 1 : dark disk (player 1)
            # 2 : light disk (player 2)

            # Select the move and send it to the manager
            if (minimax == 1): #run this if the minimax flag is given
                movei, movej = select_move_minimax(board, color, limit, caching)
            else: #else run alphabeta
                movei, movej = select_move_alphabeta(board, color, limit, caching, ordering)

            print("{} {}".format(movei, movej))

if __name__ == "__main__":
    run_ai()
