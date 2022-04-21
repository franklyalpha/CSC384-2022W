#Look for #IMPLEMENT tags in this file.
'''
All models need to return a CSP object, and a list of lists of Variable objects
representing the board. The returned list of lists is used to access the
solution.

For example, after these three lines of code

    csp, var_array = caged_csp_model(board)
    solver = BT(csp)
    solver.bt_search(prop_FC, var_ord)

var_array[0][0].get_assigned_value() should be the correct value in the top left
cell of the FunPuzz puzzle.

The grid-only models do not need to encode the cage constraints.

1. binary_ne_grid (worth 10/100 marks)
    - A model of a FunPuzz grid (without cage constraints) built using only
      binary not-equal constraints for both the row and column constraints.

2. nary_ad_grid (worth 10/100 marks)
    - A model of a FunPuzz grid (without cage constraints) built using only n-ary
      all-different constraints for both the row and column constraints.

3. caged_csp_model (worth 25/100 marks)
    - A model built using your choice of (1) binary binary not-equal, or (2)
      n-ary all-different constraints for the grid.
    - Together with FunPuzz cage constraints.

'''
import copy

from cspbase import *
import itertools


def init_zero_matrix(n):
    lst = [0] * n
    matrix = []
    for i in range(n):
        matrix.append(lst.copy())
    return matrix


def check_row_binary(matrix, row_num, num):
    """
    return true if num not in matrix[row]
    """
    for existing_number in matrix[row_num]:
        if num == existing_number:
            return False
    return True


def check_column_binary(matrix, col_num, num):
    """
    return true if num not in matrix[col]
    """
    for row in matrix:
        if num == row[col_num]:
            return False
    return True


def binary_ne_grid(fpuzz_grid):
    n = fpuzz_grid[0][0]
    matrix = init_zero_matrix(n)
    result = binary_ne_grid_helper(matrix, 0, n)

    # a list of variable objects
    vars = []
    for i in range(n*n):
        new_var = Variable(f"{i+1}", list(range(1, n+1)))
        vars.append(new_var)

    # create new csp object
    new_csp = CSP("binary not equal constraint", vars)
    # create new constraint object
    constraint = Constraint(f"constraint", vars)
    # a list of list of constrains for [var1, 2, 3 ... 9]
    constraints = []
    for matrix in result:
        constraint_lst = []
        for row in range(n):
            for col in range(n):
                constraint_lst.append(matrix[row][col])
        constraints.append(constraint_lst)
        # print(matrix)

    constraint.add_satisfying_tuples(constraints)
    new_csp.add_constraint(c=constraint)
    return new_csp, vars


def binary_ne_grid_helper(matrix, cell_num, n):
    if cell_num == n*n:
        return [matrix]
    else:
        row_num = cell_num // n
        col_num = cell_num % n
        results = []
        for cand_num in range(1, n+1):
            if check_row_binary(matrix, row_num, cand_num) and check_column_binary(matrix, col_num, cand_num):
                matrix_cpy = copy.deepcopy(matrix)
                matrix_cpy[row_num][col_num] = cand_num
                results.extend(binary_ne_grid_helper(matrix_cpy, cell_num+1, n))
        return results


def nary_ad_grid(fpuzz_grid):
    n = fpuzz_grid[0][0]
    matrix = init_zero_matrix(n)
    result = nary_ad_grid_helper(matrix, 0, n)
    print(len(result))

    # a list of variable objects
    vars = []
    for i in range(n*n):
        new_var = Variable(f"{i+1}", list(range(1, n+1)))
        vars.append(new_var)

    # create new csp object
    new_csp = CSP("n-ary not equal constraint", vars)
    # create new constraint object
    constraint = Constraint(f"constraint", vars)
    # a list of list of constrains for [var1, 2, 3 ... 9]
    constraints = []
    for matrix in result:
        constraint_lst = []
        for row in range(n):
            for col in range(n):
                constraint_lst.append(matrix[row][col])
        constraints.append(constraint_lst)

    constraint.add_satisfying_tuples(constraints)
    new_csp.add_constraint(c=constraint)
    return new_csp, vars


def nary_ad_grid_helper(matrix, cell_num, n):
    if cell_num == n*n:
        return [matrix]
    else:
        row_num = cell_num // n
        col_num = cell_num % n
        results = []
        for cand_num in range(1, n+1):
            if check_row(matrix, row_num, cand_num) and check_column(matrix, col_num, cand_num):
                matrix_cpy = copy.deepcopy(matrix)
                matrix_cpy[row_num][col_num] = cand_num
                results.extend(binary_ne_grid_helper(matrix_cpy, cell_num+1, n))
        return results


def check_row(matrix, row_num, num):
    """
    return true if num not in matrix[row]
    """
    return num not in matrix[row_num]


def check_column(matrix, col_num, num):
    """
    return true if num not in matrix[col]
    """
    numbers_in_col = []
    for row in matrix:
        numbers_in_col.append(row[col_num])
    return num not in numbers_in_col


def caged_csp_model(fpuzz_grid):
    n = fpuzz_grid[0][0]
    matrix = init_zero_matrix(n)
    result = caged_csp_model_helper(matrix, 0, n, fpuzz_grid)

    # create new csp object
    new_csp = CSP("binary not equal constraint", vars)
    # create new constraint object
    constraint = Constraint(f"constraint", vars)
    # a list of list of constrains for [var1, 2, 3 ... 9]
    constraints = []
    for matrix in result:
        constraint_lst = []
        for row in range(n):
            for col in range(n):
                constraint_lst.append(matrix[row][col])
        constraints.append(constraint_lst)
        # print(matrix)

    constraint.add_satisfying_tuples(constraints)
    new_csp.add_constraint(c=constraint)
    return new_csp, vars


def caged_csp_model_helper(matrix, cell_num, n, fpuzz_grid):
    if cell_num == n*n:
        return [matrix]
    else:
        row_num = cell_num // n
        col_num = cell_num % n
        results = []
        for cand_num in range(1, n+1):
            if check_row(matrix, row_num, cand_num) and \
               check_column(matrix, col_num, cand_num) and \
               check_fun_puzz(matrix, row_num, col_num, cand_num, fpuzz_grid, n):
                matrix_cpy = copy.deepcopy(matrix)
                matrix_cpy[row_num][col_num] = cand_num
                results.extend(caged_csp_model_helper(matrix_cpy, cell_num+1, n, fpuzz_grid))
        return results


def check_fun_puzz(matrix, row_num, col_num, cand_num, fpuzz_grid, n):
    """
    check if fun puzz constrains violation
    """
    cell_num = (row_num + 1) * 10 + (col_num + 1)
    list_index = num_in_lst(fpuzz_grid, cell_num)
    if list_index is False:
        raise IndexError("list index not found in game grid")
    primary_list = fpuzz_grid[list_index].copy()  # original list of [xy result op]
    operations = {0: "+", 1: "-", 2: "/", 3: "*"}
    curr_op = operations[primary_list[-1]]
    curr_result = primary_list[-2]
    primary_list = fill_primary_list(primary_list[:-2], matrix, cand_num, cell_num)  # now primary list is a list of potential numbers
    empty_cells = primary_list.count(0)
    if empty_cells != 0:  # there is more than 1 cell need filling, not calculable
        return True
    eval_result = evaluate(primary_list, curr_op, curr_result)
    return eval_result


def num_in_lst(nested_lst, num):
    """
    return the index of list where the number is located
    """
    for i in range(1, len(nested_lst)):
        if num in nested_lst[i]:
            return i
    return False


def fill_primary_list(primary_list, matrix, cand_num, cell_num):
    """
    return a new list where primary list contains actual number, replace 0 with candidate number
    """
    result = []
    for i in range(len(primary_list)):
        curr_cell_num = str(primary_list[i])
        row_num = int(curr_cell_num[0]) - 1
        col_num = int(curr_cell_num[1]) - 1
        if str(cell_num) == curr_cell_num:
            result.append(cand_num)
        else:
            result.append(matrix[row_num][col_num])
    return result


def evaluate(nums, op, result):
    """
    Evaluate if all permutations of nums with operation op can produce result
    """

    all_combo = itertools.permutations(nums)
    for combo in all_combo:
        eval_str = ""
        for i in range(len(combo)):
            eval_str += str(combo[i])
            if i != len(combo) - 1:
                eval_str += str(op)
        temp_result = eval(eval_str)
        if temp_result == result:
            return True
    return False





# TODO REMOVE for testing purposes
if __name__ == "__main__":
    # binary_ne_grid([[3],[11,21,3,0],[12,22,2,1],[13,23,33,6,3],[31,32,5,0]])
    nary_ad_grid([[4],[11,21,6,3],[12,13,3,0],[14,24,3,1],[22,23,7,0],[31,32,2,2],[33,43,3,1],[34,44,6,3],[41,42,7,0]])
    caged_csp_model([[6],[11,21,11,0],[12,13,2,2],[14,24,20,3],[15,16,26,36,6,3],[22,23,3,1],[25,35,3,2],[31,32,41,42,240,3],[33,34,6,3],[43,53,6,3],
                     [44,54,55,7,0],[45,46,30,3],[51,52,6,3],[56,66,9,0],[61,62,63,8,0],[64,65,2,2]])



