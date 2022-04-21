#Look for #IMPLEMENT tags in this file. These tags indicate what has
#to be implemented to complete problem solution.
import random

from cspbase import CSP, Constraint, Variable
'''This file will contain different constraint propagators to be used within 
   bt_search.

   propagator == a function with the following template
      propagator(csp, newly_instantiated_variable=None)
           ==> returns (True/False, [(Variable, Value), (Variable, Value) ...]

      csp is a CSP object---the propagator can use this to get access
      to the variables and constraints of the problem. The assigned variables
      can be accessed via methods, the values assigned can also be accessed.

      newly_instaniated_variable is an optional argument.
      if newly_instantiated_variable is not None:
          then newly_instantiated_variable is the most
           recently assigned variable of the search.
      else:
          progator is called before any assignments are made
          in which case it must decide what processing to do
           prior to any variables being assigned. SEE BELOW

       The propagator returns True/False and a list of (Variable, Value) pairs.
       Return is False if a deadend has been detected by the propagator.
       in this case bt_search will backtrack
       return is true if we can continue.

      The list of variable values pairs are all of the values
      the propagator pruned (using the variable's prune_value method). 
      bt_search NEEDS to know this in order to correctly restore these 
      values when it undoes a variable assignment.

      NOTE propagator SHOULD NOT prune a value that has already been 
      pruned! Nor should it prune a value twice

      PROPAGATOR called with newly_instantiated_variable = None
      PROCESSING REQUIRED:
        for plain backtracking (where we only check fully instantiated 
        constraints) 
        we do nothing...return true, []

        for forward checking (where we only check constraints with one
        remaining variable)
        we look for unary constraints of the csp (constraints whose scope 
        contains only one variable) and we forward_check these constraints.

        for gac we establish initial GAC by initializing the GAC queue
        with all constaints of the csp


      PROPAGATOR called with newly_instantiated_variable = a variable V
      PROCESSING REQUIRED:
         for plain backtracking we check all constraints with V (see csp method
         get_cons_with_var) that are fully assigned.

         for forward checking we forward check all constraints with V
         that have one unassigned variable left

         for gac we initialize the GAC queue with all constraints containing V.
   '''

def prop_BT(csp: CSP, newVar=None):
    '''Do plain backtracking propagation. That is, do no 
    propagation at all. Just check fully instantiated constraints'''
    
    if not newVar:
        return True, []
    for c in csp.get_cons_with_var(newVar):
        if c.get_n_unasgn() == 0:
            vals = []
            vars = c.get_scope()
            for var in vars:
                vals.append(var.get_assigned_value())
            if not c.check(vals):
                return False, []
    return True, []


def prop_FC(csp: CSP, newVar=None):
    '''Do forward checking. That is check constraints with
       only one uninstantiated variable. Remember to keep
       track of all pruned variable,value pairs and return '''
    status, prune = True, []
    if newVar is None:
        # will deal with each variable one by one, using for loop
        for const in csp.get_all_cons():
            if const.get_n_unasgn() == 1:
                newVar = const.get_unasgn_vars()[0]
                status, new_prune = FChelper(newVar, csp)
                prune.extend(new_prune)
        return status, prune
    else:
        return FChelper(newVar, csp)

# we look for unary constraints of the csp (constraints whose scope
# contains only one variable) and we forward_check these constraints.
def FChelper(newVar, csp):
    result_pruned = []

    DWO = False
    for constraint in csp.get_cons_with_var(newVar):
        if constraint.get_n_unasgn() == 1:
            remaining_unassigned = constraint.get_unasgn_vars()[0]
            result, pruned_values = FCcheck(constraint, remaining_unassigned)
            for pruned_value in pruned_values:
                result_pruned.append((remaining_unassigned, pruned_value))
            if result == "DWO":
                DWO = True
                break
    # if not DWO:
    #     success, results_pruned_recurse = prop_FC(csp, newVar=newVar)
    #     result_pruned.extend(results_pruned_recurse)
    return not DWO, result_pruned


def FCcheck(c: Constraint, x: Variable):
    value_pruned = []
    curr_domain = x.curdom
    domain = x.dom
    for d in range(len(curr_domain)):
        if curr_domain[d] is True:
            x.assign(domain[d])
            vals = []
            vars = c.get_scope()
            for var in vars:
                vals.append(var.get_assigned_value())
            if c.check(vals) is False:
                value_pruned.append(domain[d])
                x.prune_value(domain[d])
            x.unassign()
    if True not in curr_domain:
        return "DWO", value_pruned
    else:
        return "OK", value_pruned


def cartesian_product(variable_unassigned):
    # this will return the cartesian product of all variable's possible
    # domain combinations, for a constraint
    all_var_cur_domain = []
    var_dom_size = []
    output_before = [[]]
    output_after = []
    for var in variable_unassigned:
        all_var_cur_domain.append(var.cur_domain())
        var_dom_size.append(len(var.cur_domain()))
    # the idea is, iteratively move forward (just like creating the frontier, and for all
    # existing results, append current variable's value to form new lists)
    for i in range(len(all_var_cur_domain)):
        for j in range(var_dom_size[i]):
            for k in range(len(output_before)):
                a = all_var_cur_domain[i][j]
                b = output_before[k].copy()
                b.append(all_var_cur_domain[i][j])
                output_after.append(b)
        output_before = output_after.copy()
        output_after = []
    return output_before


def prop_GAC(csp: CSP, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    # according to how this function is called, when it's called without newVar,
    # the result is sxactly the pre-processing.
    # otherwise will only deal with constraints relating to given variable. Thus
    # except the gac_queue, everything could all be processed in gac_enforce. One problem is,
    # as one value in domain could be removed, might require multiple iterations of the same value's
    # domain to ensure everything is still in order.
    gac_queue = []
    if newVar is None:
        gac_queue = csp.get_all_cons()
    else:
        gac_queue = csp.get_cons_with_var(newVar)

    return gac_enforce(csp, gac_queue)

#
def gac_enforce(csp: CSP, gac_queue):
    # this function must be able to return the possible choices, or "DWO"
    # if no results could be produced.
    # require an unassigned variable, and give it values all along the way;
    # then should check whether there are other values possible for making remaining variables
    # of current constraint work.
    # will make the queue only pop values, but not giving new, to see whether it works as expected.
    pruned_list = []
    while not len(gac_queue) == 0:
        curr_constraint = gac_queue.pop(0)
        variables_in_constraint = curr_constraint.get_unasgn_vars()

        # now need to iterate through each variable, and each value
        for var in variables_in_constraint:
            current_domain = var.cur_domain()
            for values in current_domain:
                found_assignment = False
                # assign current var with this domain value,
                Variable.assign(var, values)
                # and see whether a satisfying value assignment
                # makes this constraint satisfied;
                remaining_unassigned = Constraint.get_unasgn_vars(curr_constraint)
                all_combinations = cartesian_product(remaining_unassigned)
                # check all possible combinations; first assign value, and then unassign
                for i in range(len(all_combinations)):
                    for vari in range(len(remaining_unassigned)):
                        Variable.assign(remaining_unassigned[vari], all_combinations[i][vari])
                    # now extract all variables' value in this constraint and evaluate
                    vals = []
                    vars = curr_constraint.get_scope()
                    for variabl in vars:
                        vals.append(variabl.get_assigned_value())
                    # now evaluate
                    if Constraint.check(curr_constraint, vals):
                        found_assignment = True

                    for vari in range(len(remaining_unassigned)):
                        Variable.unassign(remaining_unassigned[vari])
                    if found_assignment == True:
                        break
                # if no such one, prune this value from var's domain, record and unassign

                Variable.unassign(var)
                if not found_assignment:
                    Variable.prune_value(var, values)

                    pruned_list.append((var, values))
                    # if no value for curr domain of curr variable, then there's no solution given(possibly)
                    # previous assignment
                    if Variable.cur_domain(var) == []:
                        gac_queue = []
                        return False, pruned_list
                    else:
                        # should push new constraints into the queue
                        extra_constraints = csp.get_cons_with_var(var)
                        for extra in extra_constraints:
                            if extra not in gac_queue:
                                gac_queue.append(extra)

    return True, pruned_list
