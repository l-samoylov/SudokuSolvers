""" 
Author: CS76; Lisa Samoylov + Scaffolding 
Date: 11/17/24
Driver file to test DPLL, WalkSAT, and GSAT Sudoku Solvers 

"""

from display import display_sudoku_solution
import random, sys
from DPLL import DPLL
from SAT import SAT

if __name__ == "__main__":
    # for testing, always initialize the pseudorandom number generator to output the same sequence
    #  of values:
    random.seed(1)

    puzzle_name = str(sys.argv[1][:-4])
    sol_filename = puzzle_name + ".sol"

    # SAT Learning
    #---------------
    satInstance = SAT(sys.argv[1])
    gsatOUT = SAT.gsat()
    wsatOUT = SAT.walksat()

    print("WalkSAT: ", wsatOUT) 
    print("GSAT: ", gsatOUT)

    # DPLL
    #---------------
    # dpll = DPLL(sys.argv[1])
    # result = dpll.run_dpll()
    # print("RESULT: ", result)
    # if result:
    #     dpll.write_solution(sol_filename)
    #     display_sudoku_solution(sol_filename)