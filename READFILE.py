""" 
Author: CS76; Lisa Samoylov
Date: 11/20/24 
Reader for .cnf files 
"""

# INPUT: STR filename; must be .cnf 
# OUTPUT: 
#  DICT var_dict {int i: var_i} ; associates integer with var from cnf file 
#                                e.g. {1:"111"}
#  LIST(LIST(INT)) clause_list [[-i,j,k],[-x,-y,-z]]; 
#                  clauses read from cnf file, with symbols being integers 

def READFILE(filename): # reads the .cnf file and returns a list of clauses and var_dict for use 
        # 1st Take!
        #-----------------
        # initialization 
        var_set = set() # to grab all symbols (no negs) from file
        clause_list = [] # to grab all lines in file 

        # reading the file
        with open(filename, "r") as file: 
            for line in file: 
                # cleaning the line
                line = line.strip('\n')

                # dealing with empty lines 
                if line == "": 
                     continue 
                
                line = line.split(' ')
                while "" in line: 
                    line.remove("")

                # getting the clauses
                clause_list.append(line)

                # getting the variables 
                for stuff in line: 
                    #print("prestuff:",stuff)
                    stuff = stuff.strip('-')
                    #print("stuff:",stuff)
                    var_set.add(stuff)

        # 2nd Take! 
        #----------------------------
        # initialization 
        var_set = list(var_set) 

        var_dict = dict()        # var_dict to be returned 
        clause_var_dict = dict() # used to internally clean up clauses 

        # making the dicts 
        for i in range(1, len(var_set)+1):
            var_dict[i] = var_set[i-1]          # var_dict = {i: var}
            clause_var_dict[var_set[i-1]] = i   # clause_var_dict = {var: i}

        #-----------------------
        # Courtesy of ChatGPT
        # swapping the values in clause_list for integer values 
        # where each list represents an OR clause 
        #-----------------------

        # cleaning up the clauses
        # iterating through all clauses
        for i in range(len(clause_list)): 
              clause = clause_list[i]

              # iterating through each symbol in clause 
              for j in range(len(clause)): 
                   symbol = clause[j] 
                   
                   # swapping .cnf symbol for associated int symbol 
                   if "-" in symbol: 
                        symbol = symbol.replace("-", "")
                        clause_list[i][j] = 0-clause_var_dict[symbol]
                   else: 
                        clause_list[i][j] = clause_var_dict[symbol]
    
        return clause_list, var_dict 

# TESTING / DEBUGGING 
if __name__ == "__main__": 
    READFILE("rows.cnf")