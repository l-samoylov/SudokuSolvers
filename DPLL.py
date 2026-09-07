""" 
Author: CS76; Lisa Samoylov
Date: 01/13/25
Clean DPLL utilizing unit-clause propogation 

"""
import random
from DPLL_HELPER import * 
from READFILE import READFILE 

class DPLL(): 
    # CONSTRUCTOR 
    #=================================
    # INPUT: STR puzzlename = FILENAME 
    #----------------------------------
    def __init__(self, puzzlename): 
        self.puzzlename = puzzlename # puzzlefile with the cnfs 
        
        # READING THE FILE 
        self.clauses, self.IntToVar_dict, self.VarToInt_dict = READFILE(puzzlename) 
        print("IntToVar: ", self.IntToVar_dict.keys())
        print("VarToInt: ", self.VarToInt_dict.keys())
        # setting variables
        self.variables = list(self.IntToVar_dict.keys())

        # PREPOPULATING CELLS + FREEZING VARIABLES
        self.assignment, self.frozen_var = self.PREPOPULATE()

        self.solution = dict()
        self.degree_dict = MAKE_DEGREE_DICT(self.variables, self.clauses)
       
    # DPLL ALGORITHM with UNIT PROPOGATION
    #==================================
    # DPLL SHELL
    #---------------------------
    def run_dpll(self): # looks for assignment T/F that satisfies all vars 
        clauses = self.clauses 
        assignment  = dict()
        degree_dict = self.degree_dict

        return self.dpll(c_list = clauses, a_dict = assignment, d_dict = degree_dict, depth = 0, var = None)

    # DPLL RECURSIVE HELPER 
    #---------------------------
    # INPUT: INT var, LIST clause_list, DICT asgn_dict, INT depth
    # OUTPUT: BOOL T/F (if solution was found or not)
    #---------------------------
    def dpll(self, c_list, a_dict, d_dict, depth, var = None): 
        # 0. PRINT DEBUGGING 
        print("===========================")
        print("INSIDE DPLL", depth ) 
        # print("ASSIGNMENT: ", asgn_dict)
        # print("#ASSIGNED_VAR: ", len(asgn_dict))
        # print("CLAUSES: ", clause_list)

        # 1. PROPOGATION 
        new_clist, new_adict, new_ddict, failure = self.PROPOGATE(c_list, a_dict, d_dict, var)
        
        # update the assignment and clauses to use 
        a_dict = new_adict
        c_list = new_clist 
        d_dict = new_ddict 
    
        # checking for failure 
        if failure: return False  

        # checking for solution 
        elif len(new_clist) == 0: 
            self.solution = a_dict
            return True 

        # 2. CONTINUE DPLL 
        else:
            # 3. PICK UNASSIGNED SYMBOL
            P = self.GET_MAX_DEGREE_VAR(a_dict, d_dict)
            # CASE I: P = True 
            a_dict[P] = True 
            result = self.dpll(c_list, a_dict, d_dict, depth + 1, P)
            if result == True: return result 

            # CASE II: P = False 
            else: 
                a_dict[P] = False 
                return self.dpll(c_list, a_dict, d_dict, depth + 1, P)

    # DPLL Methods 
    #=====================================

    # WRITE SOLUTION 
    #-----------------------
    def write_solution(self, solfilename):
        # print("SOLUTION: ", self.solution)
        with open(solfilename, "w") as file: 
            # iterating through the assignment
            for var in self.solution.keys(): 

                # if cell assigned certain value  
                if self.solution[var]: 
                    cell_value = self.IntToVar_dict[var]
                    
                    # writing the assigned value to the file 
                    file.write(str(cell_value) + "\n")

    # GET_MAX_DEGREE_VAR 
    #-----------------------
    # INPUT: DICT assignment, DICT degree_dict 
    # OUTPUT: POSITIVE INT max_var 
    #-----------------------
    def GET_MAX_DEGREE_VAR(self, assignment, degree_dict): 
        unassigned_var = set(self.variables) - set(assignment.keys()) - set(self.frozen_var)
        # print("vars: ", self.variables)
        # print("frozen: ", self.frozen_var)
        # print("assigned: ", assignment.keys())
        # no more variables to pick 
        if len(unassigned_var) == 0: 
            return None 
        
        # search for max var 
        max_var = random.choice(list(unassigned_var))

        # finding max-degree variable 
        for var in unassigned_var: 
            if degree_dict[var] > degree_dict[max_var]: 
                max_var = var

        return max_var
    
    # PROPOGATE 
    #-----------------------
    # INPUT: INT var/NONE, LIST clauses, DICT assignment, DICT degree_dict 
    # OUTPUT: LIST clauses, DICT assignment, DICT degree_dict, BOOL T/F if failed or not
    #-----------------------
    # !!! if var passed in, assumes a_dict[var] exists !!!
    
    def PROPOGATE(self, c_list, a_dict, d_dict, var = None): 
        # print("IN PROPOGATE: ")
        # print("---------------")
        # 1. VAR ASSIGNMENT 
        if var == None: 
            ucl_list = GET_UNIT_CLAUSE_LITERALS(c_list)

            # can't propogate any further? 
            # print("UNIT CLAUSES: ", ucl_list)
            if len(ucl_list) == 0:
                return c_list, a_dict, d_dict, False 
            
            # otherwise get a unit clause 
            var = random.choice(ucl_list)
            a_dict[abs(var)] = VAL_TO_TRUE(var)

        # print("VAR: ", var)
        # print("CLAUSES: ",c_list)
        
        # 3. UPDATE C_LIST AND D_DICT 
        dp_dict = d_dict.copy()
        cp_list = c_list.copy()

        for clause in cp_list: 
            # remove clauses that evaluate to true 
            if EVALUATE(clause, a_dict) == 1: 
                # print("TRUE Clause ", clause, EVALUATE(clause, a_dict))
                cp_list.remove(clause)
            
            # found a failure 
            elif EVALUATE(clause, a_dict) == 0: 
                # removing current value from assignment 
                del a_dict[abs(var)]
                return cp_list, a_dict, dp_dict, True 
            
        # 2. CHECK FOR SOLUTION 
        if len(cp_list) == 0: 
            return cp_list, a_dict, d_dict, False 
        
        # removing visited var from clauses 
        for clause in cp_list: 
                pos_var = var 
                neg_var = 0-var

                if pos_var in clause: clause.remove(var) 
                elif neg_var in clause: clause.remove(neg_var)

                # removing empty clauses
                if len(clause) == 0: cp_list.remove(clause)

        # print("CP CLUASES: ", cp_list)
        # 4. REPEAT 
        return self.PROPOGATE(cp_list, a_dict, dp_dict)

    def PREPOPULATE(self): 
        # GIVEN: 
        clauses = self.clauses
        int_to_var = self.IntToVar_dict
        var_to_int = self.VarToInt_dict

        # RETURN THIS: 
        assignment = dict()
        frozen_var = set()

        # STEPS: 
        # 1. FIND AND SET UNIT CLAUSES (presetting cell values)
        # vars = int_var 
        for clause in clauses:
            # if unit clause  
            if len(clause) == 1: 
                # ensure evaluates to True 
                var = clause[0]
                assignment[abs(var)] = VAL_TO_TRUE(var) 
                
                # freeze var 
                frozen_var.add(abs(var))
        
        # 2. UPDATE ASSIGNMENT (so dpll doesn't consider other values for preset cells) 
        # if preset cell values 
        if len(assignment.keys()) > 0: 
            # go through each cell 
            for int_var in frozen_var: 
                # convert it back to rcv
                rcv_var = int_to_var[int_var] 

                # grab the rc 
                str_rc = rcv_var[0] + rcv_var[1] 

                # get all the potential cell values 
                cell_values  = GET_ALL_CELL_VALUES(str_rc) # return set [rc1, rc9]

                remaining_values = cell_values - {rcv_var} 

                for value in remaining_values: 
                    # convert value to an int 
                    int_val = var_to_int[value] 

                    # assign it to False 
                    assignment[int_val] = False 

            # freeze all the variables we added 
            for int_var in assignment.keys(): 
                frozen_var.add(int_var)

        return assignment, frozen_var
if __name__ == "__main__": 
    my_dpll = DPLL("test.cnf")
    result = my_dpll.run_dpll()
    print(result)
