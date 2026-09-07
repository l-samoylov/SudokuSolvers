""" 
Author: CS76; Lisa Samoylov
Date: 11/22/24 
Helper functions for SAT and DPLL Solvers
"""
import random 

# GENERATING RANDOM ASSIGNMENT 
#=========================================
def RANDOM_ASSIGNMENT(variables):  # generates random assignment 
    #INPUT: LIST variables [var]
    #OUTPUT: DICT assignment {int var: bool 0,1} 
    #----------------------------------------------------
    assignment = dict()

    # randomly assiging each varuable T or F 
    for var in variables: 
        assignment[var] = random.choice([0,1]) 

    return assignment 

# CLAUSE SATISFACTION AND CLAUSE RELATED FUNCS 
#=========================================
def CLAUSE_SATISFIED(clause, assignment): # checks if assignment satisfies single clause 
    # INPUT: LIST clauses = [LIST clause1, LIST clause2, LIST clausen]
    #        DICT assignment = {int var: bool 0,1}
    # OUTPUT: BOOL T/F 
    # --------------------------------------------------------

    # iterating through all symbols in clause 
    for symbol in clause: 
        # positive symbol = True 
        if symbol > 0: 
            if assignment[abs(symbol)] == True: return True 
        
        # negtive symbol = False 
        if symbol < 0: 
            if assignment[abs(symbol)] == False: return True 

    return False

def ALL_CLAUSES_SATISFIED(clauses, variables, assignment): # checks if all the clauses are satisfied or not
        # INPUT: DICT assignment = {int var: T/F}; 
        #        LIST clauses = [LIST clause1, ..., LIST clauseN]
        # OUTPUT: BOOL T/F
        # --------------------------------------------------------

        # len assignment = num var 
        if len(assignment) < len(variables): 
            return False 
        
        # iterating through all clauses
        for clause in clauses: 
            # if there's a clause that isn't satisfied; return False 
            if not CLAUSE_SATISFIED(clause, assignment): return False 
        
        return True 

def FALSE_CLAUSES(clauses, assignment): # returns set of false clauses under model 
    # INPUT: DICT assignment = {INT var: T/F}; 
    #        LIST clauses = [LIST clause1, ..., LIST clauseN]
    # OUTPUT: LIST false_clause_list = [LIST clause1, ..., LIST clauseN]
    # --------------------------------------------------------
    false_clause_list = list()

    # iterating through all clauses 
    for clause in clauses: 
        if not CLAUSE_SATISFIED(clause, assignment): 
            false_clause_list.append(list(clause))

    return false_clause_list

def NUM_CLAUSE_SATISFIED(clauses, assignment): # returns number of clauses assignment satisfies 
    # INPUT: DICT assignment = {INT var: T/F}
    #        LIST clauses = [LIST clause1, LIST clause2, LIST clausen]
    # OUTPUT: INT num_clauses_satsfied  
    #------------------------------------------

    num_clause_satisfied = 0 

    # iterating through all clauses 
    for clause in clauses: 
        # add satisfied clause to count 
        if  CLAUSE_SATISFIED(clause, assignment): 
            num_clause_satisfied += 1 

    return num_clause_satisfied

# VARIABLE SELECTION FUNCS
#==============================================
def SET_HIGHEST_SCORERS(scored_var): # returns set of highest scored vars 
    #INPUT: SORTED LIST scored_var = [(INT var, INT score)]
    #OUTPUT: SET highest_scorers = {INT var} 
    #-----------------------------------------
    highest_scorers = set() 
    cur_score = scored_var[-1][1]
    high_score = scored_var[-1][1]

    # idea: pop off the last elements while they have highest score 
    while cur_score == high_score: 
        cur_var = scored_var.pop() # popping off last var
        highest_scorers.add(cur_var[0]) 
        cur_score = scored_var[-1][1] # updating the cur_score 

    return highest_scorers


def GET_HIGHEST_SCORED_VAR(clauses, variables, assignment): # picking P propositional variable to flip 
    #INPUT: DICT assignment = {INT var: T/F} 
    #       LIST variables = [INT var]
    #       LIST clauses = [LIST clause1, LIST clause2, LIST clausen]
    #OUTPUT: INT var
    #-------------------------------------------------
    scored_var = list()

    # getting the base number of clauses assignment satisfied 
    base_num = NUM_CLAUSE_SATISFIED(clauses, assignment) 

    # iterating through and scoring all the variables 
    for var in variables: 
        # flipping variable value
        assignment[var] = not assignment[var]

        # checking to see how many more clauses satisfied 
        score = NUM_CLAUSE_SATISFIED(clauses, assignment) - base_num 

        # adding scored variable to the list 
        scored_var.append((var, score)) 

        # flipping variable value back to original 
        assignment[var] = not assignment[var]
    
    # sorting the var lowest -> highest
    scored_var.sort(key = lambda x : x[1]) 

    # picking a random high scorer to flip
    prop_var = random.choice(list(SET_HIGHEST_SCORERS(scored_var))) 

    return prop_var
 
# MISC FUNCS 
#============================================
# getting symbol from a specific clause 
def SELECT_SYMBOL_FROM(clause): 
    # bc e.g. clause = [-1,2,-5,19]
    return abs(random.choice(clause)) # pick abs of random int in clause 

