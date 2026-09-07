""" 
Author: CS76; Scaffolding (Provided Code) 
Date: 11/17/24

Python script to convert to 
- load a sudoku puzzle
- convert it to cnf form (suitable for solvers) as a .cnf file

Run > "python sudoku2cnf.py <filename.sud>" 
argv[1]: sudoku puzzle filename (.sud) 

"""
from Sudoku import Sudoku
import sys

if __name__ == "__main__":
    test_sudoku = Sudoku()

    test_sudoku.load(sys.argv[1])
    print(test_sudoku)

    puzzle_name = sys.argv[1][:-4]
    cnf_filename = puzzle_name + ".cnf"

    test_sudoku.generate_cnf(cnf_filename)
    print("Output file: " + cnf_filename)

