#Look for #IMPLEMENT tags in this file. These tags indicate what has
#to be implemented to complete problem solution.
import cspbase

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

def prop_BT(csp, newVar=None):
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


def prop_FC(csp: cspbase.CSP, newVar=None):
    '''Do forward checking. That is check constraints with
       only one uninstantiated variable. Remember to keep
       track of all pruned variable,value pairs and return '''

    # we look for unary constraints of the csp (constraints whose scope
    # contains only one variable) and we forward_check these constraints.
    result_pruned = []
    if newVar is None:
        for constraint in csp.get_all_cons():
            if constraint.get_n_unasgn() == 1:
                newVar = constraint.get_unasgn_vars()[0]
                break
    if newVar is None:
        return True, []

    DWO = False
    for constraint in csp.get_cons_with_var(newVar):
        if constraint.get_n_unasgn() == 1:
            unassigned_var1 = constraint.get_unasgn_vars()[0]
            result, pruned_values = FCcheck(constraint, unassigned_var1)
            for pruned_value in pruned_values:
                result_pruned.append((unassigned_var1, pruned_value))
            if result == "DWO":
                DWO = True
                break

    return not DWO, result_pruned





def FCcheck(C: cspbase.Constraint, x: cspbase.Variable):

    value_pruned = []
    for d in x.cur_domain():
        x.assign(d)
        vals = []
        vars = C.get_scope()
        for var in vars:
            vals.append(var.get_assigned_value())
        if C.check(vals) is False:
            value_pruned.append(d)
            x.prune_value(d)
        x.unassign()
    if True not in x.curdom:
        return "DWO", value_pruned
    else:
        return "OK", value_pruned

def pick_an_unassigned_variable(csp: cspbase.CSP) -> cspbase.Variable:
    return csp.get_all_unasgn_vars()[0]


def prop_GAC(csp: cspbase.CSP, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    if newVar is None:
        newVar = pick_an_unassigned_variable(csp)

    gac_q = []
    prone_pair = []
    for d in newVar.cur_domain():  # first value for var
        newVar.assign(d)
        for val in newVar.cur_domain():  # second value for var
            if val != d:
                newVar.prune_value(val)
            for constraint in csp.get_cons_with_var(newVar):
                gac_q.append(constraint)
            status, new_prone_pair = gac_enforce(csp, gac_q)
            prone_pair.extend(new_prone_pair)
            if status != "DWO":
                return True, prone_pair
        newVar.unassign()
    return False, prone_pair


def gac_enforce(csp: cspbase.CSP, gac_q):
    prone_variable_value = []
    while gac_q != []:
        constraint = gac_q.pop(0)
        for var in constraint.get_scope():
            for val in var.cur_domain():

                var.assign(val)  # V=d
                found_assignment = False
                unassigned_vars = constraint.get_unasgn_vars()
                all_assignments = cartesian_product(unassigned_vars)
                for pair in all_assignments:
                    for i in range(len(unassigned_vars)):
                        unassigned_vars[i].assign(pair[i])
                    vals = []
                    vars = constraint.get_scope()
                    for variabl in vars:
                        vals.append(variabl.get_assigned_value())
                    if constraint.check(vals):
                        found_assignment = True
                    for i in range(len(unassigned_vars)):
                        unassigned_vars[i].unassign()
                if not found_assignment:
                    var.prune_value(val)
                    prone_variable_value.append((var, val))
                    if var.cur_domain() == []:
                        gac_q = []
                        return "DWO", prone_variable_value
                else:
                    for constraint_prim in csp.get_cons_with_var(var):
                        if constraint_prim not in gac_q:
                            gac_q.append(constraint_prim)
    return "OK", prone_variable_value


def find_other_assignment(csp: cspbase.CSP, constraint: cspbase.Constraint, used_vars):
    if len(used_vars) + 1 == len(constraint.get_scope()):
        remaining_var = [x for x in constraint.get_scope() if x not in used_vars][0]
        used_vars.append(remaining_var)
        return remaining_var.cur_domain(), used_vars
    else:
        new_result = []
        for var in constraint.get_scope():
            if var not in used_vars:
                used_vars.append(var)
                existing_result, used_vars = find_other_assignment(csp, constraint, used_vars)

                for value in var.cur_domain():
                    for unfinished_assignment in existing_result:
                        temp = unfinished_assignment.insert(0, value)
                        new_result.append(temp)
        return new_result


def cartesian_product(variable_unassigned):
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



