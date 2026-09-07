# PROPOGATED DPLL 

# MISSING: 
# freezing vars and prepopulating them 
# constraint propogation 


# Version to with edits to fix propogation logic errors from Take2
# Errors: DPLL doesn't search deep enough into tree; restarts too early.
# Errors: DPLL still doesn't search deep enough (or fast enough)
                DPLL can't solve rows.cnf  -- has same problem 

IMPORTANT FILES: 
--------------------------
solve_sudoku.py = edit file/run in terminal to run DPLL, WalkSAT, and GSAT 
RUN> python solve_sudoku.py sample_puzzle.cnf 

SAT.py = class file for SAT object; has WalkSAT and GSAT algorithm implementations
DPLL.py = class file for DPLL object; has DPLL algorithm implementation 

LESS IMPORTANT FILES:
--------------------------
HELPER.py = has helper functions for SAT and DPLL 
DPLL_HELPER.py = has DPLL helper functions 
READFILE.py = has helper func to read .cnf file and return clauses and variables 

        
