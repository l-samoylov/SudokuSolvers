# Sudoku SAT Solver

This project converts 9x9 Sudoku puzzles into CNF formulas and solves them with SAT algorithms. The driver currently uses the DPLL solver.

## Files

- `solve_sudoku.py` - main driver; solves a CNF file, writes a `.sol` file, and displays the completed grid.
- `sudoku2cnf.py` - converts a Sudoku `.sud` file into a `.cnf` file.
- `DPLL.py` - DPLL solver with clause propagation, Sudoku constraint propagation, and frozen clue variables.
- `SAT.py` - experimental GSAT and WalkSAT implementations.
- `Sudoku.py` - Sudoku grid representation and CNF generation.
- `READFILE.py` - reads CNF files and maps Sudoku literals to internal integers.
- `DPLL_HELPER.py` - helper functions from the original DPLL implementation.
- `HELPER.py` - helper functions used by GSAT and WalkSAT.
- `display.py` - displays a generated `.sol` file as a Sudoku grid.
- `Puzzles/` - sample `.sud` puzzles and generated `.cnf` files.
- `Solutions/` - sample solution files.

## Run the Solver

From the project directory, pass a CNF puzzle to the driver:

```shell
python solve_sudoku.py Puzzles/puzzle2.cnf
```

If the puzzle is satisfiable, the completed grid is printed and a matching solution file, such as `Puzzles/puzzle2.sol`, is created.

## Add Your Own Sudoku

Create a text file ending in `.sud` with nine space-separated numbers on each of nine lines. Use `0` for an empty cell:

```text
0 0 3 0 0 0 0 0 0
0 0 0 1 0 0 0 0 0
0 0 0 0 0 9 0 0 0
0 0 0 0 0 0 0 0 8
0 0 0 0 5 0 0 0 0
0 7 0 0 0 0 0 0 0
0 0 0 0 0 0 9 0 0
0 0 0 0 0 0 0 6 0
0 0 0 0 0 0 0 0 0
```

Place the file in `Puzzles/`, convert it to CNF, and run the solver:

```shell
python sudoku2cnf.py Puzzles/my_puzzle.sud
python solve_sudoku.py Puzzles/my_puzzle.cnf
```

The converter creates `Puzzles/my_puzzle.cnf`; the solver then creates `Puzzles/my_puzzle.sol`.
