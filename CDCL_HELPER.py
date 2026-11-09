"""
Author: CS76; Lisa Samoylov
Date: 11/08/26
Contains helper functions for CDCL algorithm

"""


# GETTING LITERAL'S VALUE
# =========================================
def LITERAL_VALUE(literal, assignment):
    # INPUT: INT literal, DICT assignment
    # OUTPUT: BOOL T/F OR None if the variable is unassigned
    # --------------------------------------------------------
    variable = abs(literal)
    if variable not in assignment:
        return None

    return assignment[variable] == (literal > 0)


# CLEANING CLAUSES
# =========================================
def NORMALIZE_CLAUSE(clause):
    # INPUT: LIST clause
    # OUTPUT: LIST clause OR None if clause is always True
    # --------------------------------------------------------
    cleaned_clause = []
    seen = set()

    for literal in clause:
        if -literal in seen:
            return None
        if literal not in seen:
            seen.add(literal)
            cleaned_clause.append(literal)

    return cleaned_clause


# CLAUSE RESOLUTION
# =========================================
def RESOLVE(first_clause, second_clause, variable):
    # INPUT: LIST first_clause, LIST second_clause, INT variable
    # OUTPUT: LIST resolvent OR None if resolvent is always True
    # --------------------------------------------------------
    resolvent = []

    # removing the conflicting variable and joining what remains
    for literal in list(first_clause) + list(second_clause):
        if abs(literal) != variable:
            resolvent.append(literal)

    return NORMALIZE_CLAUSE(resolvent)


# GET BACKTRACK LEVEL
# =========================================
def GET_BACKTRACK_LEVEL(clause, level_dict, asserting_literal):
    # INPUT: LIST clause, DICT level_dict, INT asserting_literal
    # OUTPUT: INT highest level below the asserting literal
    # --------------------------------------------------------
    other_levels = [
        level_dict.get(abs(literal), 0)
        for literal in clause
        if literal != asserting_literal
    ]

    if not other_levels:
        return 0
    return max(other_levels)
