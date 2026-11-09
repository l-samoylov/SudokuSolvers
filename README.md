# Sudoku SAT Solver

This project converts 9x9 Sudoku puzzles into CNF formulas and solves them with SAT algorithms. The driver supports CDCL, DPLL, WalkSAT, and GSAT algorithms. 

## Files
--- Algorithm Files 
- `DPLL.py` - DPLL solver with clause propagation, Sudoku constraint propagation, and frozen clue variables.
- `DPLL_HELPER.py` - helper functions from the original DPLL implementation.
- `CDCL.py` - CDCL solver with watched literals, clause learning, non-chronological backtracking, and frozen clue variables.
- `CDCL_HELPER.py` - helper functions used by the CDCL solver.
- `SAT.py` - experimental GSAT and WalkSAT implementations.
- `HELPER.py` - helper functions used by GSAT and WalkSAT.
--- Driver and Other Files 
- `Sudoku.py` - Sudoku grid representation and CNF generation.
- `READFILE.py` - reads CNF files and maps Sudoku literals to internal integers.
- `solve_sudoku.py` - main driver; solves a CNF file, writes a `.sol` file, and displays the completed grid.
- `sudoku2cnf.py` - converts a Sudoku `.sud` file into a `.cnf` file.
- `display.py` - displays a generated `.sol` file as a Sudoku grid.
- `Puzzles/` - sample `.sud` puzzles and generated `.cnf` files.
- `Solutions/` - sample solution files.

## Run the Solver

From the project directory, pass a CNF puzzle to the driver:

```shell
python solve_sudoku.py Puzzles/puzzle2.cnf
```

If the puzzle is satisfiable, the completed grid is printed and a matching solution file, such as `Puzzles/puzzle2.sol`, is created.

## Swap the Solver

The solver used by `solve_sudoku.py` is selected by its import and solver block. Remove or comment out the experimental `SAT Learning` block so that only the selected solver runs. To use DPLL, import the class:

```python
from DPLL import DPLL
```

Then use this block inside `if __name__ == "__main__":`:

```python
dpll = DPLL(sys.argv[1])
result = dpll.run_dpll()
print("RESULT: ", result)
if result:
    dpll.write_solution(sol_filename)
    display_sudoku_solution(sol_filename)
```

To swap to CDCL, replace the DPLL import with:

```python
from CDCL import CDCL
```

Then replace the DPLL block with:

```python
cdcl = CDCL(sys.argv[1])
result = cdcl.run_cdcl()
print("RESULT: ", result)
if result:
    cdcl.write_solution(sol_filename)
    display_sudoku_solution(sol_filename)
```

Only keep the block for the solver you want to run. The command remains the same:

```shell
python solve_sudoku.py Puzzles/puzzle2.cnf
```

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
