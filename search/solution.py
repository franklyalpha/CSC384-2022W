#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports---i.e., ones that are automatically
#   available on TEACH.CS
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math  # for infinity
import heapq
import time

from search import *  # for search engines
from sokoban import SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems

def sokoban_goal_state(state: SokobanState):
    '''
    @return: Whether all boxes are stored.
    '''
    for box in state.boxes:
        if box not in state.storage:
            return False
    return True

def heur_manhattan_distance(state: SokobanState):
    # IMPLEMENT
    '''admissible sokoban puzzle heuristic: manhattan distance'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # We want an admissible heuristic, which is an optimistic heuristic.
    # It must never overestimate the cost to get from the current state to the goal.
    # The sum of the Manhattan distances between each box that has yet to be stored and the storage
    # point nearest to it is such a heuristic.
    # When calculating distances, assume there are no obstacles on the grid.
    # You should implement this heuristic function exactly, even if it is tempting to improve it.
    # Your function should return a numeric value; this is the estimate of the distance to the goal.

    # first extract out boxes and storages;
    box_list = state.boxes
    storage_list = state.storage
    total_heur = 0
    # then for each box, figure out the storage position closest to it (using Manhattan distance)
    for box_pos in box_list:
        minimal_distance = math.inf
        for store_pos in storage_list:
            manhattan = abs(store_pos[0] - box_pos[0]) + abs(store_pos[1] - box_pos[1])
            minimal_distance = min(minimal_distance, manhattan)
        # finally add up to heuristics
        total_heur += minimal_distance
    return total_heur  # CHANGE THIS

# SOKOBAN HEURISTICS
def trivial_heuristic(state: SokobanState):
    '''trivial admissible sokoban heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance 
    of the state (# of moves required to get) to the goal.'''
    return 0  # CHANGE THIS

def heur_alternate(state: SokobanState):
    # IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''

    """
    Updated based on Manhattan distance, by also considering the distance between robots and boxes. 
    Based on this, added corner-checking: if a corner is not a storage position, heuristic becomes math.inf
    Also to avoid cases putting a box into a wall without storage, the heuristic will be increased
    once a box is attempting to hit any walls.
    
    see below comments among code on specific procedures; 
    """
    # first extract all robots, boxes and storage positions;

    robot_list = state.robots
    box_list = []
    storage_list = []
    # then eliminate boxes and storage positions being placed /filled; to avoid error caused by mutability,
    # will do a copy of box sets and lists of storages first;
    for box in state.boxes:
        box_list.append(box)
    for storage in state.storage:
        storage_list.append(storage)
    # find intersection of boxes and storage positions -> boxes being placed
    placed_boxes = list(set(box_list) & set(storage_list))
    box_list = [ele for ele in box_list if ele not in placed_boxes]
    storage_list = [ele for ele in storage_list if ele not in placed_boxes]
    board_size = [state.width, state.height]

    # below checks whether a box is at a corner
    stucked_box = check_stuck(box_list, placed_boxes, state.obstacles, robot_list, board_size)
    if stucked_box:
        return math.inf

    # distribute remaining boxes to robots
    # calculate each box's position to each robot;
    robot_assign = [] # has length same as number of boxes
    for box in box_list:
        minimal_distance = [0, math.inf]
        for i in range(len(robot_list)):
            robot = robot_list[i]
            manhattan = abs(robot[0] - box[0]) + abs(robot[1] - box[1])
            if manhattan < minimal_distance[1]:
                minimal_distance = [i, manhattan]
        # a robot is assigned with a box, if the robot is the closest to current box
        robot_assign.append(minimal_distance)

    # calculate unstored boxes' manhattan distance to its closest storage
    storage_assign = [] # has length same as number of boxes
    for box in box_list:
        minimal_distance = [0, math.inf]
        for i in range(len(storage_list)):
            storage= storage_list[i]
            manhattan = abs(storage[0] - box[0]) + abs(storage[1] - box[1])
            if manhattan < minimal_distance[1]:
                minimal_distance = [i, manhattan]
        # storage is assigned if it's the closest storage to the box
        storage_assign.append(minimal_distance)
    # now the robot will move one box to assigned location, and then return to "original point"
    # and move another box, continue until all boxes are stored.
    total_heuristic = 0
    for box_index in range(len(box_list)):
        # the steps all robots take to move one box to storage and then return to origin
        # takes exactly doubled cost of moving one box to storage,
        # which involves moving to the box, and pushing the box to the storage.

        # below checks whether a box is put beside a wall, and a penalty heuristic will be returned
        boundary_penalty = avoid_boundary(board_size, box_list[box_index])
        total_heuristic += 2 * (robot_assign[box_index][1] + storage_assign[box_index][1]) + boundary_penalty
    return total_heuristic  # CHANGE THIS

def avoid_boundary(gameboard_size, box):
    # this function checks whether a box is hitting the wall; if is, will return a positive heuristic penalty
    if (box[0] == gameboard_size[0] - 1) or (box[0] == 0):
        return gameboard_size[0] / 3
    elif (box[1] == gameboard_size[1] - 1) or (box[1] == 0):
        return gameboard_size[1] / 3
    else:
        return 0

def check_stuck(box_list, placed_boxes, obstacles, robot_list, board_size) -> bool:
    # case 1: box is at a corner which isn't a storage;
    # case 2: robot cannot move the box any further(requires moving back several steps)
        # case 2 is: the robot is stuck on a up-down tunnel, while what's in front of the box is
        # either a box in storage location, boundary or an obstacle.
    for box in box_list:
        adjacents = [(box[0], box[1] + 1), (box[0] + 1, box[1]), (box[0], box[1] - 1), (box[0] - 1, box[1])]
        for index in range(4):

            # check if adjacent is an obstacle
            if (adjacents[index] in obstacles) or (adjacents[index] in placed_boxes) \
                    or (adjacents[index] in box_list):
                adjacents[index] = 1
            # check if is a horizontal boundary
            elif (adjacents[index][0] == -1) or (adjacents[index][0] == board_size[0]):
                adjacents[index] = 1
            # check if is a vertical boundary
            elif (adjacents[index][1] == -1) or (adjacents[index][1] == board_size[1]):
                adjacents[index] = 1
            # a white space/robot space
            else:
                adjacents[index] = 0
        # check if box is at a corner
        if ((adjacents[0] == 1) and (adjacents[1] == 1)) or (adjacents[1] == 1) and (adjacents[2] == 1) or \
            (adjacents[2] == 1) and (adjacents[3] == 1) or (adjacents[3] == 1) and (adjacents[0] == 1):
            return True
    return False

def heur_zero(state: SokobanState):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0

def fval_function(sN: sNode, weight: float) -> float:
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return sN.gval + weight * sN.hval

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a warehouse state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    se = SearchEngine('custom', 'default')
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn,
                   fval_function=wrapped_fval_function)
    final, stats = se.search(timebound)
    return final, stats  # CHANGE THIS

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a warehouse state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of realtime astar algorithm'''

    start_time = os.times()[0]
    remain_time = timebound
    i = 0
    g_val = math.inf
    h_val = math.inf
    f_val = g_val + weight * h_val
    costbound = (g_val, h_val, f_val)
    best_final = None
    best_stats = None
    while remain_time > 0:
        # same as weighted a* #
        se = SearchEngine('custom', 'default')
        wrapped_fval_function = (lambda sN: fval_function(sN, weight))
        se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn,
                       fval_function=wrapped_fval_function)
        # end same as weighted a* #
        final, stats = se.search(timebound, costbound)

        if final:
            costbound = (final.gval, 0, final.gval)
            best_final = final
            best_stats = stats
        elif final is None or final is False:
            return best_final, best_stats
        remain_time = timebound - (os.times()[0] - start_time)
        i += 1
        weight = weight / 1.5
    return best_final, best_stats


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of anytime gbf algorithm'''
    start_time = os.times()[0]
    remain_time = timebound
    i = 0
    g_val = math.inf
    h_val = math.inf
    f_val = g_val + h_val
    costbound = (g_val, h_val, f_val)
    best_final = None
    best_stats = None
    while remain_time > 0:

        se = SearchEngine('best_first', 'default')
        se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn)

        final, stats = se.search(timebound, costbound)

        if final:
            costbound = (final.gval, 0, final.gval)
            best_final = final
            best_stats = stats
        elif final is None or final is False:
            return best_final, best_stats
        remain_time = timebound - (os.times()[0] - start_time)
        i += 1

    return best_final, best_stats



