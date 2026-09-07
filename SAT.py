""" 
Author: CS76; Lisa Samoylov 
Date: 11/17/24

SAT class for the solve_sudoku.py
Contains WalkSAT and GSAT algorithms 

"""
import random
import Sudoku 
from HELPER import *
from READFILE import READFILE 

class SAT(): 
    # CONSTRUCTOR 
    #=================================
    # INPUT: STR puzzlename = CNF FILENAME 
    #----------------------------------
    def __init__(self, puzzlename): 
        self.puzzlename = puzzlename # puzzlefile with the cnfs 
        self.clauses, self.var_dict = READFILE(puzzlename) 
        self.variables = list(self.var_dict.keys())
        self.assignment = None

    # GSAT SOlVER 
    #============================
    # pseudocode from https://www.researchgate.net/publication/2634047_A_New_Method_for_Solving_Hard_Satisfiability_Problems
    # specific implementation of finding p from PA5 instructions 
    #============================
    def gsat(self): # looks for assignment T/F that satisfies all vars 
    # INPUT: n/a
    # OUTPUT: None OR DICT assignment = {INT var: BOOL T/F} 

        THRESHHOLD = 0.7
        MAX_TRIES = 1000
        MAX_FLIPS = 1000

        for i in range(MAX_TRIES): 
            print("TRY iteration: ", i)
            print("---------------")
            assignment = RANDOM_ASSIGNMENT(self.variables) # pick a random assignment 
            #print("ASSIGNMENT: ", assignment)
            for j in range(MAX_FLIPS): 
                 
                 # if rndm assignment satisfies all clauses, return the assignment 
                if ALL_CLAUSES_SATISFIED(self.clauses, self.variables, assignment): 
                    self.assignment = assignment 
                    return assignment 
                
                coin_flip = random.random() 

                # picking a var to flip 
                if coin_flip > THRESHHOLD:  # pick var randomly 
                    # print("MAX: ", max(self.variables))
                    flip_var = random.choice(list(self.variables))
            
                else: # pick var that maximizes increase in # clauses satisfied 
                    flip_var = GET_HIGHEST_SCORED_VAR(self.clauses, self.variables, assignment) 
                
                # making the flip 
                assignment[flip_var] = not assignment[flip_var]

                print("FLIP: ", j) 
                print("num_clauses unsatisfied: ", len(FALSE_CLAUSES(self.clauses, assignment)))

        # GSAT didn't find a solution
        return False
    
    # WALKSAT SOLVER 
    #============================
    # pseudocode from AIMA CHP 7 
    #============================
    def walksat(self): # looks for assignment T/F that satisfies all vars 
    # INPUT: n/a
    # OUTPUT: False OR DICT assignment = {INT var: BOOL T/F}
    #--------------------------------

        THRESHHOLD = 0.3
        MAX_FLIPS = 200000

        assignment = RANDOM_ASSIGNMENT(self.variables) # pick a random assignment

        for i in range(MAX_FLIPS):
            # found a good assignment! 
            if ALL_CLAUSES_SATISFIED(self.clauses, self.variables, assignment): 
                self.assignment = assignment
                return assignment

            bad_clauses = FALSE_CLAUSES(self.clauses, assignment)
            # print("BAD_CLAUSES: ", bad_clauses)
            # picking a variable to flip 
            if random.random() > THRESHHOLD: 
                # pick var that maximizes increase in # clauses satisfied 
                flip_var = GET_HIGHEST_SCORED_VAR(self.clauses, self.variables, assignment)
            
            else: 
                # pick a random clause that's false
                clause = random.choice(bad_clauses)

                # pick a random variable = symbol from that clause
                flip_var = abs(SELECT_SYMBOL_FROM(clause))
            
            # flip the variable
            assignment[flip_var] = not assignment[flip_var]

            # viewing progress in terminal
            print("iteration: ", i)
            print("num_unsatisfied clauses: ", len(bad_clauses))

        return False 

    # MODIFIED WALKSAT SOLVER 1
    #============================
    # idea: gsat with the walksat logic
    #       try running walksat until hit max_tries 
    #       if walksat gets stuck, then will try a different random assignment 
    #       !!! if walksat gets stuck, it will be stuck until it does all the flips
    #       !!! how many flips is good enough? 
    #       !!! NOT COMPLETED 
    #----------------------------
    def mod_walksat(self):
        MAX_TRIES = 10000

        for i in range(MAX_TRIES): 
            print("TRY ", i)
            result  = self.walksat()

            # found a good assignment!
            if result != False: 
                return result 

        return False 

    # WRITE SOLUTION 
    #=========================
    def write_solution(self, solfilename): # outputting correct display for Sudoku class 

        print(ALL_CLAUSES_SATISFIED(self.clauses, self.variables, self.assignment))
        with open(solfilename, "w") as file: 
            # iterating through the assignment vars
            for var in self.assignment.keys(): 
                # if var = True
                if self.assignment[var]: 
                    # fetching original symbol (not int)
                    ori_symb = self.var_dict[var]
                    
                    # writing it to the file 
                    # print("SYMBOL: ", ori_symb, var)
                    file.write(str(ori_symb) + "\n")
        
    
    def __str__(self): 
        print(self.puzzlename)

if __name__ == "__main__": 
    my_sat = SAT("one_cell.cnf")
    result = my_sat.walksat()