""" 
Author: CS76; Lisa Samoylov
Date: 12/10/24
Contains helper functions for DPLL algorithm 

"""
# MISC 
def GET_ALL_CELL_VALUES(rc): # STR rc -> SET ['rc1',...,'rc9']
                             # returns: all possible cell values 
    cell_values = set()
    for i in range(1,10): 
        cell_values.add(rc + str(i))
    return cell_values 

# GETTING LITERAL'S VALUE 
def VAL_TO_TRUE(literal): 
    if literal > 0: return True 
    else: return False 

# DEGREE STUFF 
def MAKE_DEGREE_DICT(symbols, clauses): 
    score_list = [0]*len(symbols) 

    # tallying symbol appearances 
    for clause in clauses: 
        for symbol in clause: 
            score_list[abs(symbol)-1] += 1
    
    # making dictionary to associate symbol with score
    score_dict = dict()

    for i in range(len(score_list)): 
        score_dict[i+1] = score_list[i]
    
            # degree dict
    return score_dict 

# GETTING LITERALS IN UNIT CLAUSES 
def GET_UNIT_CLAUSE_LITERALS(c_list): 
    unit_clause_literals = set()

     # finding literals in unit clauses  
    for clause in c_list: 
        if len(clause) == 1: 
            unit_clause_literals.add(clause[0])
    return list(unit_clause_literals)
        
 
# CLAUSE SATISFACTION
#=========================================
def EVALUATE(clause, assignment): 
    # INPUT: LIST clauses = [LIST clause1, LIST clause2, LIST clausen]
    #        DICT assignment = {int var: bool 0,1}
    # OUTPUT: BOOL T/F 
    # !!! modified so that it works with dpll but really slow at checking it
    # --------------------------------------------------------
    EXISTS_TRUE = False 
    EXISTS_UNASSIGNED_SYMBOL = False 
    # print("IN CLAUSE_SATISFIED: ", clause, assignment)

    # iterating through all symbols in clause 
    for symbol in clause: 
        # symbol unassigned 
        if abs(symbol) not in list(assignment.keys()): EXISTS_UNASSIGNED_SYMBOL = True 

        # a symbol evaluates to True 
        # so EITHER positive symbol P = TRUE 
        # OR     negative symbol P = FALSE 
        elif ((symbol > 0) and (assignment[abs(symbol)] == True)) or \
         ((symbol < 0) and (assignment[abs(symbol)] == False)): 
            EXISTS_TRUE = True 

    # RETURN 1: CLAUSE SATISFIED 
    if EXISTS_TRUE == True: 
        # print("CLAUSE SATISFIED") 
        return 1

    # RETURN 2: NO TRUE VAR; BUT SOME VAR MISSING ASSIGNMENTS 
    elif EXISTS_UNASSIGNED_SYMBOL == True: 
        # print("UNASSIGNED VAR")
        return 2 

    # RETURN 0: NO TRUE VAR; ALL VAR EVAL TO FALSE 
    else: 
        # print("FALSE")
        return 0