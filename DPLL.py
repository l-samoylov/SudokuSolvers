"""
Author: CS76; Lisa Samoylov
Date: 01/13/25
Clean DPLL utilizing unit-clause propogation

"""

from READFILE import READFILE


class DPLL:
    # CONSTRUCTOR
    # =================================
    # INPUT: STR puzzlename = FILENAME
    # ----------------------------------
    def __init__(self, puzzlename):
        self.puzzlename = puzzlename  # puzzlefile with the cnfs

        # READING THE FILE
        (
            self.clauses,
            self.IntToVar_dict,
            self.VarToInt_dict,
        ) = READFILE(puzzlename)
        # SETTING VARIABLES
        self.variables = list(self.IntToVar_dict.keys())

        # PREPOPULATING CELLS + FREEZING VARIABLES
        self._initial_conflict = False
        self._constraint_peers = self._MAKE_CONSTRAINT_PEERS()
        self.assignment, self.frozen_var = self.PREPOPULATE()
        self.solution = {}
        self.degree_dict = self._degree_dict(self.clauses)

    # DPLL ALGORITHM with UNIT-CLAUSE PROPOGATION
    # ==================================
    # DPLL SHELL
    # ---------------------------
    def run_dpll(self):
        self.solution = {}
        if self._initial_conflict:
            return False

        # frozen assignments must be included in every search branch
        return self.dpll(
            c_list=[list(clause) for clause in self.clauses],
            a_dict=dict(self.assignment),
            d_dict=dict(self.degree_dict),
            depth=0,
        )

    # DPLL RECURSIVE HELPER
    # ---------------------------
    # INPUT: INT var, LIST clause_list, DICT asgn_dict, INT depth
    # OUTPUT: BOOL T/F (if solution was found or not)
    # ---------------------------
    def dpll(self, c_list, a_dict, d_dict, depth, var=None):
        # 1. PROPOGATION
        c_list, a_dict, d_dict, failure = self.PROPOGATE(
            c_list, a_dict, d_dict, var
        )

        # checking for failure
        if failure:
            return False

        # checking for solution
        if not c_list:
            # remaining variables can be set to False because every clause is
            # already satisfied by the partial assignment
            self.solution = {
                variable: a_dict.get(variable, False)
                for variable in self.variables
            }
            return True

        # 2. PICK UNASSIGNED SYMBOL + VALUE
        variable, first_value = self._GET_BRANCH_CHOICE(
            c_list, a_dict, d_dict
        )
        if variable is None:
            return False

        # 3. CASE I: P = preferred value
        # each branch needs its own assignment dictionary
        first_assignment = dict(a_dict)
        first_assignment[variable] = first_value
        if self.dpll(
            c_list,
            first_assignment,
            d_dict,
            depth + 1,
            variable,
        ):
            return True

        # 4. CASE II: P = opposite value
        second_assignment = dict(a_dict)
        second_assignment[variable] = not first_value
        return self.dpll(
            c_list,
            second_assignment,
            d_dict,
            depth + 1,
            variable,
        )

    # DPLL METHODS
    # =====================================

    # WRITE SOLUTION
    # -----------------------
    def write_solution(self, solfilename):
        with open(solfilename, "w") as file:
            for variable in sorted(self.solution):
                if self.solution[variable]:
                    file.write(str(self.IntToVar_dict[variable]) + "\n")

    # GET_MAX_DEGREE_VAR
    # -----------------------
    # INPUT: DICT assignment, DICT degree_dict
    # OUTPUT: POSITIVE INT max_var
    # -----------------------
    def GET_MAX_DEGREE_VAR(self, assignment, degree_dict):
        unassigned = [
            variable
            for variable in self.variables
            if variable not in assignment and variable not in self.frozen_var
        ]
        if not unassigned:
            return None

        # deterministic tie break so solver behavior can be reproduced
        return max(
            unassigned,
            key=lambda variable: (degree_dict.get(variable, 0), -variable),
        )

    # GET BRANCH CHOICE
    # -----------------------
    # chooses a constrained positive clause first for Sudoku CNFs
    # otherwise uses max degree + the most common literal polarity
    def _GET_BRANCH_CHOICE(self, clauses, assignment, degree_dict):
        positive_clauses = [
            clause
            for clause in clauses
            if len(clause) > 1 and all(literal > 0 for literal in clause)
        ]

        if positive_clauses:
            shortest_clause = min(positive_clauses, key=len)
            variable = max(
                (abs(literal) for literal in shortest_clause),
                key=lambda item: (degree_dict.get(item, 0), -item),
            )
            return variable, True

        variable = self.GET_MAX_DEGREE_VAR(assignment, degree_dict)
        if variable is None:
            return None, None

        positive_count = 0
        negative_count = 0
        for clause in clauses:
            for literal in clause:
                if abs(literal) == variable:
                    if literal > 0:
                        positive_count += 1
                    else:
                        negative_count += 1

        return variable, positive_count >= negative_count

    # PROPOGATE
    # -----------------------
    # INPUT: INT var/NONE, LIST clauses, DICT assignment, DICT degree_dict
    # OUTPUT: LIST clauses, DICT assignment, DICT degree_dict,
    #         BOOL T/F if failed or not
    # -----------------------
    def PROPOGATE(self, c_list, a_dict, d_dict, var=None):
        # var is kept in the function signature for compatibility
        # all assigned variables are propogated, not just the newest variable
        del var

        # copy assignment so recursive branches don't edit each other
        assignment = dict(a_dict)

        # 1. ENFORCE FROZEN VARIABLES
        for variable in self.frozen_var:
            frozen_value = self.assignment[variable]
            if variable in assignment and assignment[variable] != frozen_value:
                return (
                    [list(clause) for clause in c_list],
                    assignment,
                    dict(d_dict),
                    True,
                )
            assignment[variable] = frozen_value

        # copy each clause so the original formula is never changed
        clauses = [list(clause) for clause in c_list]

        # 2. REPEAT UNTIL NO MORE PROPOGATION IS POSSIBLE
        while True:
            # setting a Sudoku value True makes all constrained peers False
            if not self._PROPOGATE_CONSTRAINTS(assignment):
                return clauses, assignment, self._degree_dict(clauses), True

            clauses, units, failure = self._simplify_clauses(
                clauses, assignment
            )
            if failure:
                return clauses, assignment, self._degree_dict(clauses), True

            if units:
                # setting every unit literal to the value that makes it True
                if not self._apply_literals(units, assignment):
                    return clauses, assignment, self._degree_dict(clauses), True
                continue

            # a pure literal can safely be set to the value that makes it True
            pure_literals = self._pure_literals(clauses, assignment)
            if pure_literals:
                if not self._apply_literals(pure_literals, assignment):
                    return clauses, assignment, self._degree_dict(clauses), True
                continue

            return clauses, assignment, self._degree_dict(clauses), False

    def _PROPOGATE_CONSTRAINTS(self, assignment):
        # PROPOGATE SUDOKU CONSTRAINTS
        # -----------------------
        # these constraints were verified from the clauses during setup
        for variable, value in list(assignment.items()):
            if not value:
                continue

            for peer in self._constraint_peers.get(variable, set()):
                if assignment.get(peer) is True:
                    return False
                assignment[peer] = False

        return True

    @staticmethod
    def _simplify_clauses(clauses, assignment):
        # APPLY ASSIGNMENT + COLLECT NEW UNIT CLAUSES
        # -----------------------
        simplified = []
        unit_literals = []

        for clause in clauses:
            reduced = []
            seen = set()
            satisfied = False

            for literal in clause:
                variable = abs(literal)
                if variable in assignment:
                    if assignment[variable] == (literal > 0):
                        satisfied = True
                        break
                    # remove a False literal from the clause
                    continue

                # remove duplicate literals
                # opposite literals make the clause always True
                if -literal in seen:
                    satisfied = True
                    break
                if literal not in seen:
                    seen.add(literal)
                    reduced.append(literal)

            if satisfied:
                continue
            if not reduced:
                # an empty clause is a failure, not a solved clause
                return simplified + [[]], unit_literals, True

            simplified.append(reduced)
            if len(reduced) == 1:
                unit_literals.append(reduced[0])

        return simplified, unit_literals, False

    @staticmethod
    def _apply_literals(literals, assignment):
        # APPLY PROPOGATED LITERALS
        # -----------------------
        pending = {}
        for literal in literals:
            variable = abs(literal)
            value = literal > 0

            if variable in assignment and assignment[variable] != value:
                return False
            if variable in pending and pending[variable] != value:
                return False
            pending[variable] = value

        assignment.update(pending)
        return True

    @staticmethod
    def _pure_literals(clauses, assignment):
        # GET PURE LITERALS
        # -----------------------
        polarities = {}
        for clause in clauses:
            for literal in clause:
                variable = abs(literal)
                if variable not in assignment:
                    polarities.setdefault(variable, set()).add(literal > 0)

        return [
            variable if next(iter(signs)) else -variable
            for variable, signs in polarities.items()
            if len(signs) == 1
        ]

    def _degree_dict(self, clauses):
        # UPDATE DEGREE DICTIONARY
        # -----------------------
        degrees = {variable: 0 for variable in self.variables}
        for clause in clauses:
            for literal in clause:
                variable = abs(literal)
                degrees[variable] = degrees.get(variable, 0) + 1
        return degrees

    # PREPOPULATE
    # -----------------------
    def PREPOPULATE(self):
        # GIVEN:
        # self.clauses, self.IntToVar_dict, self.VarToInt_dict

        # RETURN THIS:
        assignment = {}
        frozen = set()
        positive_units = []

        # 1. FIND + FREEZE UNIT CLAUSES
        for clause in self.clauses:
            if len(clause) != 1:
                continue

            literal = clause[0]
            variable = abs(literal)
            value = literal > 0
            if variable in assignment and assignment[variable] != value:
                self._initial_conflict = True
            else:
                assignment[variable] = value
            frozen.add(variable)
            if value:
                positive_units.append(variable)

        # 2. PROPOGATE + FREEZE PRESET CELL VALUES
        for clue_variable in positive_units:
            for peer in self._constraint_peers.get(clue_variable, set()):
                if assignment.get(peer) is True:
                    self._initial_conflict = True
                else:
                    assignment[peer] = False
                frozen.add(peer)

        return assignment, frozen

    # MAKE CONSTRAINT PEERS
    # -----------------------
    # identifies Sudoku constraints that are completely represented in CNF
    def _MAKE_CONSTRAINT_PEERS(self):
        peers = {variable: set() for variable in self.variables}
        sudoku_vars = {}

        for variable, name in self.IntToVar_dict.items():
            name = str(name)
            if self._is_sudoku_variable(name):
                sudoku_vars[(int(name[0]), int(name[1]), int(name[2]))] = variable

        if not sudoku_vars:
            return peers

        positive_clauses = {
            frozenset(clause)
            for clause in self.clauses
            if clause and all(literal > 0 for literal in clause)
        }
        binary_clauses = {
            frozenset(clause)
            for clause in self.clauses
            if len(clause) == 2
        }

        # 1. VERIFY EXACTLY-ONE CONSTRAINTS FOR EACH CELL
        valid_cells = set()
        for row in range(1, 10):
            for column in range(1, 10):
                cell_vars = [
                    sudoku_vars.get((row, column, value))
                    for value in range(1, 10)
                ]
                if any(variable is None for variable in cell_vars):
                    continue
                if frozenset(cell_vars) not in positive_clauses:
                    continue

                has_all_exclusions = all(
                    frozenset((-cell_vars[first], -cell_vars[second]))
                    in binary_clauses
                    for first in range(9)
                    for second in range(first + 1, 9)
                )
                if not has_all_exclusions:
                    continue

                valid_cells.add((row, column))
                self._ADD_PEER_GROUP(peers, cell_vars)

        # 2. VERIFY + ADD ROW CONSTRAINTS
        for row in range(1, 10):
            cells = [(row, column) for column in range(1, 10)]
            if not all(cell in valid_cells for cell in cells):
                continue
            groups = [
                [sudoku_vars[(row, column, value)] for column in range(1, 10)]
                for value in range(1, 10)
            ]
            if all(frozenset(group) in positive_clauses for group in groups):
                for group in groups:
                    self._ADD_PEER_GROUP(peers, group)

        # 3. VERIFY + ADD COLUMN CONSTRAINTS
        for column in range(1, 10):
            cells = [(row, column) for row in range(1, 10)]
            if not all(cell in valid_cells for cell in cells):
                continue
            groups = [
                [sudoku_vars[(row, column, value)] for row in range(1, 10)]
                for value in range(1, 10)
            ]
            if all(frozenset(group) in positive_clauses for group in groups):
                for group in groups:
                    self._ADD_PEER_GROUP(peers, group)

        # 4. VERIFY + ADD 3x3 BLOCK CONSTRAINTS
        for start_row in range(1, 10, 3):
            for start_column in range(1, 10, 3):
                cells = [
                    (row, column)
                    for row in range(start_row, start_row + 3)
                    for column in range(start_column, start_column + 3)
                ]
                if not all(cell in valid_cells for cell in cells):
                    continue
                groups = [
                    [sudoku_vars[(row, column, value)] for row, column in cells]
                    for value in range(1, 10)
                ]
                if all(frozenset(group) in positive_clauses for group in groups):
                    for group in groups:
                        self._ADD_PEER_GROUP(peers, group)

        return peers

    @staticmethod
    def _ADD_PEER_GROUP(peers, variables):
        for variable in variables:
            peers[variable].update(set(variables) - {variable})

    @staticmethod
    def _is_sudoku_variable(name):
        return (
            len(name) == 3
            and name.isdigit()
            and all("1" <= character <= "9" for character in name)
        )


if __name__ == "__main__":
    my_dpll = DPLL("Puzzles/test.cnf")
    result = my_dpll.run_dpll()
    print(result)
