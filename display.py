""" 
Author: CS76; Scaffolding (Provided Code) 
Date: 11/17/24

displays .sol solutions to sudoku 

"""
from Sudoku import Sudoku
import sys

def display_sudoku_solution(filename):
    test_sudoku = Sudoku()
    test_sudoku.read_solution(filename)
    print(test_sudoku)

if __name__ == "__main__":
    display_sudoku_solution(sys.argv[1])