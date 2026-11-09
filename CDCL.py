"""
Author: CS76; Lisa Samoylov
Date: 11/08/26
CDCL utilizing unit-clause propogation and clause learning

"""

from CDCL_HELPER import (
    GET_BACKTRACK_LEVEL,
    LITERAL_VALUE,
    NORMALIZE_CLAUSE,
    RESOLVE,
)
from READFILE import READFILE


class CDCL:
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
        self._frozen_assignment = dict(self.assignment)
        self.solution = {}
        self.degree_dict = self._degree_dict(self.clauses)

        # CDCL SEARCH INFORMATION
        self.learned_clauses = []
        self.num_conflicts = 0
        self._reset_search()
        self.assignment = dict(self._frozen_assignment)

    # CDCL ALGORITHM with UNIT-CLAUSE PROPOGATION
    # ==================================
    # CDCL SHELL
    # ---------------------------
    def run_cdcl(self):
        # 1. CLEAR RESULTS FROM ANY EARLIER RUN
        self.solution = {}
        self.learned_clauses = []
        self.num_conflicts = 0
        self._reset_search()

        # contradictory frozen clues make the formula unsatisfiable
        if self._initial_conflict:
            return False

        # 2. CLEAN + LOAD ORIGINAL CLAUSES
        # copying them keeps learned clauses separate from the original CNF
        for clause in self.clauses:
            cleaned_clause = NORMALIZE_CLAUSE(clause)
            if cleaned_clause is None:
                continue
            if not cleaned_clause:
                return False
            self._ADD_CLAUSE(cleaned_clause)

        # 3. LOAD FROZEN ASSIGNMENTS
        # frozen variables are permanent decision-level-zero assignments
        for variable in sorted(self.frozen_var):
            value = self._frozen_assignment[variable]
            literal = variable if value else -variable
            reason = self._FIND_UNIT_REASON(literal)
            if not self._ENQUEUE(literal, reason):
                return False

        # 4. PROPOGATE ROOT ASSIGNMENTS + BEGIN SEARCH
        # a root conflict cannot be repaired because no decision was made
        conflict = self.PROPOGATE()
        if conflict is not None:
            return False

        return self.cdcl()

    # CDCL ITERATIVE HELPER
    # ---------------------------
    # INPUT: n/a
    # OUTPUT: BOOL T/F (if solution was found or not)
    # ---------------------------
    def cdcl(self):
        while True:
            # every pass begins by exhausting queued unit clauses
            conflict = self.PROPOGATE()

            # 1. CONFLICT ANALYSIS + CLAUSE LEARNING
            if conflict is not None:
                self.num_conflicts += 1
                if self.decision_level == 0:
                    return False

                # resolution leaves one literal from the current level
                learned_clause, asserting_literal = self._RESOLVE_CONFLICT(
                    conflict
                )

                # jump to the highest level used by all remaining literals
                backtrack_level = GET_BACKTRACK_LEVEL(
                    learned_clause,
                    self.level_dict,
                    asserting_literal,
                )

                # save the clause so the same failed choices cannot repeat
                self.BACKTRACK(backtrack_level)
                learned_index = self._ADD_CLAUSE(learned_clause)
                self.learned_clauses.append(list(learned_clause))

                # the learned clause becomes unit after backtracking
                if not self._ENQUEUE(asserting_literal, learned_index):
                    return False
                continue

            # 2. CHECKING FOR SOLUTION
            variable, first_value = self._GET_BRANCH_CHOICE()
            if variable is None:
                # unused variables may be False once all clauses are True
                self.solution = {
                    item: self.assignment.get(item, False)
                    for item in self.variables
                }
                return True

            # 3. PICK UNASSIGNED SYMBOL + VALUE
            # decisions have no reason clause, unlike propogated assignments
            self.decision_level += 1
            self.trail_limits.append(len(self.trail))
            decision_literal = variable if first_value else -variable
            self._ENQUEUE(decision_literal, None)

    # CDCL METHODS
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
    def _GET_BRANCH_CHOICE(self):
        active_clauses = []
        degree_dict = {variable: 0 for variable in self.variables}

        # 1. BUILD CLAUSES THAT ARE NOT ALREADY SATISFIED
        # assigned False literals are left out of each active clause
        for clause in self._clauses:
            if any(
                LITERAL_VALUE(literal, self.assignment) is True
                for literal in clause
            ):
                continue

            active_clause = [
                literal
                for literal in clause
                if LITERAL_VALUE(literal, self.assignment) is None
            ]
            if not active_clause:
                continue

            active_clauses.append(active_clause)
            for literal in active_clause:
                variable = abs(literal)
                degree_dict[variable] = degree_dict.get(variable, 0) + 1

        # no active clauses means the partial assignment is already a model
        if not active_clauses:
            return None, None

        # 2. PREFER A POSITIVE SUDOKU CONSTRAINT
        # setting one variable True quickly eliminates its constrained peers
        positive_clauses = [
            clause
            for clause in active_clauses
            if len(clause) > 1 and all(literal > 0 for literal in clause)
        ]

        if positive_clauses:
            shortest_clause = min(positive_clauses, key=len)
            variable = max(
                (abs(literal) for literal in shortest_clause),
                key=lambda item: (degree_dict.get(item, 0), -item),
            )
            return variable, True

        # 3. OTHERWISE CHOOSE THE MOST CONSTRAINED VARIABLE
        variable = self.GET_MAX_DEGREE_VAR(
            self.assignment,
            degree_dict,
        )
        if variable is None:
            return None, None

        # 4. TRY THE POLARITY THAT OCCURS MOST OFTEN FIRST
        positive_count = 0
        negative_count = 0
        for clause in active_clauses:
            for literal in clause:
                if abs(literal) == variable:
                    if literal > 0:
                        positive_count += 1
                    else:
                        negative_count += 1

        return variable, positive_count >= negative_count

    # PROPOGATE
    # -----------------------
    # INPUT: n/a
    # OUTPUT: INT conflict clause index OR None
    # -----------------------
    def PROPOGATE(self):
        while self._propogation_head < len(self.trail):
            # 1. TAKE THE NEXT NEW ASSIGNMENT FROM THE TRAIL
            true_literal = self.trail[self._propogation_head]
            self._propogation_head += 1
            false_literal = -true_literal

            # 2. CHECK CLAUSES WATCHING THE NOW-FALSE LITERAL
            # clauses with other watches cannot have just become unit
            watching = list(self._watchers.get(false_literal, set()))
            for clause_index in watching:
                clause = self._clauses[clause_index]
                first_watch, second_watch = self._watch_positions[clause_index]

                # identify which watch failed and preserve the other watch
                if clause[first_watch] == false_literal:
                    false_watch = 0
                    other_watch = second_watch
                elif clause[second_watch] == false_literal:
                    false_watch = 1
                    other_watch = first_watch
                else:
                    continue

                # 3. A TRUE SECOND WATCH ALREADY SATISFIES THE CLAUSE
                other_literal = clause[other_watch]
                if LITERAL_VALUE(other_literal, self.assignment) is True:
                    continue

                # 4. LOOK FOR AN UNASSIGNED OR TRUE REPLACEMENT WATCH
                replacement = None
                for position, literal in enumerate(clause):
                    if position == first_watch or position == second_watch:
                        continue
                    if LITERAL_VALUE(literal, self.assignment) is not False:
                        replacement = position
                        break

                # moving the watch avoids scanning this clause until needed
                if replacement is not None:
                    if false_watch == 0:
                        self._watch_positions[clause_index][0] = replacement
                    else:
                        self._watch_positions[clause_index][1] = replacement

                    # update the reverse lookup used by future assignments
                    self._watchers[false_literal].discard(clause_index)
                    new_literal = clause[replacement]
                    self._watchers.setdefault(new_literal, set()).add(
                        clause_index
                    )
                    continue

                # 5. NO REPLACEMENT MEANS THE CLAUSE IS UNIT OR CONFLICTING
                other_value = LITERAL_VALUE(other_literal, self.assignment)
                if other_value is False:
                    return clause_index
                if other_value is None:
                    # the remaining watched literal is forced by this clause
                    if not self._ENQUEUE(other_literal, clause_index):
                        return clause_index

        return None

    # RESOLVE CONFLICT
    # -----------------------
    # resolves backward through reasons until one current-level literal remains
    def _RESOLVE_CONFLICT(self, conflict_index):
        # 1. START WITH THE CLAUSE THAT JUST BECAME FALSE
        learned_clause = list(self._clauses[conflict_index])

        # 2. REMOVE CURRENT-LEVEL IMPLICATIONS ONE AT A TIME
        while self._COUNT_CURRENT_LEVEL(learned_clause) > 1:
            resolution_variable = None

            # latest assigned literals are closest to the conflict
            # decisions are skipped because they do not have reason clauses
            for true_literal in reversed(self.trail):
                variable = abs(true_literal)
                if self.level_dict.get(variable) != self.decision_level:
                    continue
                if not any(abs(literal) == variable for literal in learned_clause):
                    continue
                if self.reason_dict.get(variable) is None:
                    continue

                resolution_variable = variable
                break

            if resolution_variable is None:
                break

            # 3. RESOLVE WITH THE CLAUSE THAT FORCED THIS VARIABLE
            # the variable disappears and its earlier causes take its place
            reason_index = self.reason_dict[resolution_variable]
            resolvent = RESOLVE(
                learned_clause,
                self._clauses[reason_index],
                resolution_variable,
            )
            if resolvent is None:
                break
            learned_clause = resolvent

        # 4. FIND THE LITERAL THAT WILL ASSERT AFTER BACKTRACKING
        current_literals = [
            literal
            for literal in learned_clause
            if self.level_dict.get(abs(literal), 0) == self.decision_level
        ]
        asserting_literal = current_literals[0]

        # 5. PUT THE ASSERTING LITERAL IN THE FIRST WATCHED POSITION
        learned_clause.remove(asserting_literal)
        learned_clause.insert(0, asserting_literal)
        return learned_clause, asserting_literal

    # BACKTRACK
    # -----------------------
    # INPUT: INT level
    # OUTPUT: n/a
    # -----------------------
    def BACKTRACK(self, level):
        # assignments at or below this level stay on the trail
        if level >= self.decision_level:
            return

        # 1. REMOVE ASSIGNMENTS MADE ABOVE THE BACKTRACK LEVEL
        first_removed = self.trail_limits[level]
        for true_literal in self.trail[first_removed:]:
            variable = abs(true_literal)
            self.assignment.pop(variable, None)
            self.level_dict.pop(variable, None)
            self.reason_dict.pop(variable, None)

        # 2. SHORTEN THE TRAIL + RESET ITS PROPOGATION BOUNDARY
        del self.trail[first_removed:]
        del self.trail_limits[level:]
        self._propogation_head = min(self._propogation_head, len(self.trail))
        self.decision_level = level

    # SEARCH SETUP
    # -----------------------
    def _reset_search(self):
        # assignment information changes whenever the solver backtracks
        self.assignment = {}
        self.level_dict = {}
        self.reason_dict = {}

        # the trail stores assignments in the order they were made
        self.trail = []
        self.trail_limits = []
        self.decision_level = 0
        self._propogation_head = 0

        # watched-clause information is rebuilt for each independent run
        self._clauses = []
        self._watch_positions = []
        self._watchers = {}

    # ADD CLAUSE
    # -----------------------
    # stores an original or learned clause and initializes its watches
    def _ADD_CLAUSE(self, clause):
        # 1. GIVE THE CLAUSE A STABLE INDEX FOR REASON REFERENCES
        clause_index = len(self._clauses)
        self._clauses.append(list(clause))

        # 2. WATCH TWO LITERALS, OR THE ONLY UNIT LITERAL TWICE
        first_watch = 0
        second_watch = 0 if len(clause) == 1 else 1
        self._watch_positions.append([first_watch, second_watch])
        self._watchers.setdefault(clause[first_watch], set()).add(clause_index)
        self._watchers.setdefault(clause[second_watch], set()).add(clause_index)
        return clause_index

    # ENQUEUE LITERAL
    # -----------------------
    # records an assignment with its decision level and reason clause
    def _ENQUEUE(self, literal, reason):
        variable = abs(literal)
        value = literal > 0

        # an existing opposite value reports a conflict to the caller
        if variable in self.assignment:
            return self.assignment[variable] == value

        # new assignments wait on the trail until PROPOGATE processes them
        self.assignment[variable] = value
        self.level_dict[variable] = self.decision_level
        self.reason_dict[variable] = reason
        self.trail.append(literal)
        return True

    # FIND UNIT REASON
    # -----------------------
    # returns the original unit clause that froze a root literal
    def _FIND_UNIT_REASON(self, literal):
        for clause_index, clause in enumerate(self._clauses):
            if len(clause) == 1 and clause[0] == literal:
                return clause_index
        return None

    # COUNT CURRENT LEVEL
    # -----------------------
    # used to stop resolution when the clause becomes asserting
    def _COUNT_CURRENT_LEVEL(self, clause):
        return sum(
            1
            for literal in clause
            if self.level_dict.get(abs(literal), 0) == self.decision_level
        )

    # UPDATE DEGREE DICTIONARY
    # -----------------------
    def _degree_dict(self, clauses):
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
            cleaned_clause = NORMALIZE_CLAUSE(clause)
            if cleaned_clause is None or len(cleaned_clause) != 1:
                continue

            literal = cleaned_clause[0]
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

        # 1. MAP THREE-DIGIT NAMES TO THEIR INTERNAL VARIABLES
        for variable, name in self.IntToVar_dict.items():
            name = str(name)
            if self._is_sudoku_variable(name):
                sudoku_vars[(int(name[0]), int(name[1]), int(name[2]))] = variable

        if not sudoku_vars:
            return peers

        # 2. INDEX THE CLAUSE SHAPES NEEDED TO VERIFY CONSTRAINTS
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

        # 3. VERIFY EXACTLY-ONE CONSTRAINTS FOR EACH CELL
        valid_cells = set()
        for row in range(1, 10):
            for column in range(1, 10):
                cell_vars = [
                    sudoku_vars.get((row, column, value))
                    for value in range(1, 10)
                ]

                # incomplete cells cannot safely use the Sudoku shortcut
                if any(variable is None for variable in cell_vars):
                    continue
                if frozenset(cell_vars) not in positive_clauses:
                    continue

                # all 36 negative pairs are needed before peers are inferred
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

        # 4. VERIFY + ADD ROW CONSTRAINTS
        for row in range(1, 10):
            cells = [(row, column) for column in range(1, 10)]
            if not all(cell in valid_cells for cell in cells):
                continue

            # one group collects all nine positions for a single value
            groups = [
                [sudoku_vars[(row, column, value)] for column in range(1, 10)]
                for value in range(1, 10)
            ]
            if all(frozenset(group) in positive_clauses for group in groups):
                for group in groups:
                    self._ADD_PEER_GROUP(peers, group)

        # 5. VERIFY + ADD COLUMN CONSTRAINTS
        for column in range(1, 10):
            cells = [(row, column) for row in range(1, 10)]
            if not all(cell in valid_cells for cell in cells):
                continue

            # one group collects all nine positions for a single value
            groups = [
                [sudoku_vars[(row, column, value)] for row in range(1, 10)]
                for value in range(1, 10)
            ]
            if all(frozenset(group) in positive_clauses for group in groups):
                for group in groups:
                    self._ADD_PEER_GROUP(peers, group)

        # 6. VERIFY + ADD 3x3 BLOCK CONSTRAINTS
        for start_row in range(1, 10, 3):
            for start_column in range(1, 10, 3):
                cells = [
                    (row, column)
                    for row in range(start_row, start_row + 3)
                    for column in range(start_column, start_column + 3)
                ]
                if not all(cell in valid_cells for cell in cells):
                    continue

                # make one nine-cell block group for each possible value
                groups = [
                    [sudoku_vars[(row, column, value)] for row, column in cells]
                    for value in range(1, 10)
                ]

                # only a positive block clause proves the group constraint
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