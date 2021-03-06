from classify import *
import math

##
## CSP portion of lab 4.
##
from csp import BinaryConstraint, CSP, CSPState, Variable,\
    basic_constraint_checker, solve_csp_problem

# Implement basic forward checking on the CSPState see csp.py
def forward_checking(state, verbose=False):
    # Before running Forward checking we must ensure
    # that constraints are okay for this state.
    basic = basic_constraint_checker(state, verbose)
    if not basic:
        return False
    # forward checking logic
    X = state.get_current_variable()
    if not X: return True
    x = X.get_assigned_value() 
    constraints = state.get_constraints_by_name(X.get_name())
    for con in constraints:
        Y = state.get_variable_by_name(con.get_variable_i_name() if con.get_variable_i_name() != X.get_name() else con.get_variable_j_name())
        for y in Y.get_domain():
            if con.check(state, x, y) is False:
                Y.reduce_domain(y)
                if Y.domain_size() is 0:
                    return False
            
  
    return True

# Now Implement forward checking + (constraint) propagation through
# singleton domains.
def forward_checking_prop_singleton(state, verbose=False):
    # Run forward checking first.
    fc_checker = forward_checking(state, verbose)
    if not fc_checker:
        return False

    # Add your propagate singleton logic here.
    domains = state.get_all_variables()
    singletons = [x for x in domains if x.domain_size == 1]
    for X in singletons:
        x = X.domain[0]
        for con in state.get_constraints_by_name(X.get_name()):
            Y = state.get_variable_by_name(con.get_variable_i_name() if con.get_variable_i_name() != X.get_name() else con.get_variable_j_name())
            for y in Y.get_domain():
                if con.check(state, x, y) is False:
                    Y.reduce_domain(y)
                    if len(Y.get_domain()) is 0: 
                        return False
    return True
        

## The code here are for the tester
## Do not change.
from moose_csp import moose_csp_problem
from map_coloring_csp import map_coloring_csp_problem

def csp_solver_tree(problem, checker):
    problem_func = globals()[problem]
    checker_func = globals()[checker]
    answer, search_tree = problem_func().solve(checker_func)
    return search_tree.tree_to_string(search_tree)

##
## CODE for the learning portion of lab 4.
##

### Data sets for the lab
## You will be classifying data from these sets.
senate_people = read_congress_data('S110.ord')
senate_votes = read_vote_data('S110desc.csv')

house_people = read_congress_data('H110.ord')
house_votes = read_vote_data('H110desc.csv')

last_senate_people = read_congress_data('S109.ord')
last_senate_votes = read_vote_data('S109desc.csv')


### Part 1: Nearest Neighbors
## An example of evaluating a nearest-neighbors classifier.
senate_group1, senate_group2 = crosscheck_groups(senate_people)
#evaluate(nearest_neighbors(hamming_distance, 1), senate_group1, senate_group2, verbose=1)

## Write the euclidean_distance function.
## This function should take two lists of integers and
## find the Euclidean distance between them.
## See 'hamming_distance()' in classify.py for an example that
## computes Hamming distances.

def euclidean_distance(list1, list2):
    assert isinstance(list1, list)
    assert isinstance(list2, list)
    dist = 0
    for item1, item2 in zip(list1, list2):
        if item1 != item2:
            dist += abs((item1-item2)^2)

    return math.sqrt(dist)

#Once you have implemented euclidean_distance, you can check the results:
evaluate(nearest_neighbors(euclidean_distance, 1), senate_group1, senate_group2)

## By changing the parameters you used, you can get a classifier factory that
## deals better with independents. Make a classifier that makes at most 3
## errors on the Senate.

my_classifier = nearest_neighbors(euclidean_distance, 5)
evaluate(my_classifier, senate_group1, senate_group2, verbose=1)

### Part 2: ID Trees
#print CongressIDTree(senate_people, senate_votes, homogeneous_disorder)

## Now write an information_disorder function to replace homogeneous_disorder,
## which should lead to simpler trees.

def information_disorder(yes, no):
    yestotal = len(yes) + 1.
    nototal = len(no) + 1.
    republicanyes = 1.
    republicanno = 1.
    democratyes = 1.
    democratno = 1.
    independentyes = 1.
    independentno = 1.
    for y in yes:
        if y == "Republican":
            republicanyes += 1.
        elif y == "Democrat":
            democratyes += 1.
        elif y == "Independent":
            independentyes += 1.
            
    for n in no:
        if n == "Republican":
            republicanno += 1.
        elif n == "Democrat":
            democratno += 1.
        elif n == "Independent":
            independentno += 1.
            
    repubyesfrac = republicanyes/yestotal
    repubnofrac = republicanno/nototal
    demoyesfrac = democratyes/yestotal
    demonofrac = democratno/nototal
    indeyesfrac = independentyes/yestotal
    indenofrac = independentno/nototal
    yesdisorder = -math.log(repubyesfrac,2)*repubyesfrac-math.log(demoyesfrac,2)*demoyesfrac-math.log(indeyesfrac,2)*indeyesfrac
    nodisorder = -math.log(repubnofrac,2)*repubnofrac-math.log(demonofrac,2)*demonofrac-math.log(indenofrac,2)*indenofrac      
    disorder = yesdisorder + nodisorder
    
    return disorder
    

#print CongressIDTree(senate_people, senate_votes, information_disorder)
evaluate(idtree_maker(senate_votes, information_disorder), senate_group1, senate_group2)

## Now try it on the House of Representatives. However, do it over a data set
## that only includes the most recent n votes, to show that it is possible to
## classify politicians without ludicrous amounts of information.

def limited_house_classifier(house_people, house_votes, n, verbose = False):
    house_limited, house_limited_votes = limit_votes(house_people,
    house_votes, n)
    house_limited_group1, house_limited_group2 = crosscheck_groups(house_limited)

    if verbose:
        print "ID tree for first group:"
        print CongressIDTree(house_limited_group1, house_limited_votes,
                             information_disorder)
        print
        print "ID tree for second group:"
        print CongressIDTree(house_limited_group2, house_limited_votes,
                             information_disorder)
        print
        
    return evaluate(idtree_maker(house_limited_votes, information_disorder),
                    house_limited_group1, house_limited_group2)

                                   
## Find a value of n that classifies at least 430 representatives correctly.
## Hint: It's not 10.
N_1 = 60
rep_classified = limited_house_classifier(house_people, house_votes, N_1)

## Find a value of n that classifies at least 90 senators correctly.
N_2 = 90
senator_classified = limited_house_classifier(senate_people, senate_votes, N_2)

## Now, find a value of n that classifies at least 95 of last year's senators correctly.
N_3 = 50
old_senator_classified = limited_house_classifier(last_senate_people, last_senate_votes, N_3)


## The standard survey questions.
HOW_MANY_HOURS_THIS_PSET_TOOK = "5"
WHAT_I_FOUND_INTERESTING = "asdf"
WHAT_I_FOUND_BORING = "asdf"


## This function is used by the tester, please don't modify it!
def eval_test(eval_fn, group1, group2, verbose = 0):
    """ Find eval_fn in globals(), then execute evaluate() on it """
    # Only allow known-safe eval_fn's
    if eval_fn in [ 'my_classifier' ]:
        return evaluate(globals()[eval_fn], group1, group2, verbose)
    else:
        raise Exception, "Error: Tester tried to use an invalid evaluation function: '%s'" % eval_fn

