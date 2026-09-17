"""Display data -- common_prompt.md Section 5. Nothing here is recalculated;
every value is transcribed from the prompt. If a scene needs a value that
is not here, stop and ask instead of inventing one."""

DEMO_ROWS = [
    ("Row 1", 500, "2-source"),
    ("Row 2", 600, "4-source"),
    ("Row 3", 480, "2-source"),
    ("Row 4", 550, "2-source"),
    ("Row 5", 300, "2-source"),
    ("Row 6", 450, "4-source"),
    ("Row 7", 800, "2-source"),
    ("Row 8", 800, "2-source"),
]
N_GROUPS = 2
TOTAL_KW = 4480

# Scene 03 -- Section 2 of scene03_prompt.md
SCENE03 = {
    "row1_kw": 500,
    "row1_type": "2-source",
    "row1_half_share": 250,
    "row1_partner_full_share": 500,
    "row2_kw": 600,
    "row2_type": "4-source",
    "row2_quarter_share": 150,
    "row2_third_share": 200,
    "pairs": ["AB", "AC", "AD", "BC", "BD", "CD"],
}

# cut_after k -> (Group 1 kW, Group 2 kW)
GROUP_TOTALS = {
    1: (500, 3980),
    2: (1100, 3380),
    3: (1580, 2900),
    4: (2130, 2350),
    5: (2430, 2050),
    6: (2880, 1600),
    7: (3680, 800),
}
BEST_M_PER_CUT = {1: 1540, 2: 1340, 3: 1225, 4: 1100, 5: 990, 6: 1140, 7: 1425}
MOST_BALANCED_CUT = 4

SOLUTION_A = {
    "cut_after": 4,
    "pairs": {
        "Row 1": "AB", "Row 3": "CD", "Row 4": "AC",
        "Row 5": "AB", "Row 7": "CD", "Row 8": "AC",
    },
    "group_max": [1000, 1350],
    "M": 1350,
}
SOLUTION_B = {
    "cut_after": 4,
    "pairs": {
        "Row 1": "AB", "Row 3": "AC", "Row 4": "CD",
        "Row 5": "AB", "Row 7": "AC", "Row 8": "BD",
    },
    "group_max": [990, 1100],
    "M": 1100,
}
SOLUTION_OPT = {
    "cut_after": 5,
    "pairs": {
        "Row 1": "AB", "Row 3": "AC", "Row 4": "CD", "Row 5": "BD",
        "Row 7": "AB", "Row 8": "CD",
    },
    "group_max": [990, 950],
    "M": 990,
}

FAULT_TABLE_A_G2 = {
    "A": {"B": 450, "C": 1350, "D": 550},
    "B": {"A": 850, "C": 950, "D": 550},
    "C": {"A": 1100, "B": 300, "D": 950},
    "D": {"A": 700, "B": 300, "C": 1350},
}
FAULT_TABLE_A_G2_CONTRIBUTIONS_A_FAILS = {
    "Row 5": {"pair": "AB", "share": "0", "to": {}},
    "Row 6": {"pair": "ABCD", "share": "1/3", "to": {"B": 150, "C": 150, "D": 150}},
    "Row 7": {"pair": "CD", "share": "1/2", "to": {"C": 400, "D": 400}},
    "Row 8": {"pair": "AC", "share": "1", "to": {"C": 800}},
}

FAULT_TABLE_OPT_G1 = {
    "A": {"B": 850, "C": 955, "D": 625},
    "B": {"A": 940, "C": 715, "D": 775},
    "C": {"A": 930, "B": 600, "D": 900},
    "D": {"A": 690, "B": 750, "C": 990},
}
FAULT_TABLE_OPT_G2 = {
    "A": {"B": 950, "C": 550, "D": 550},
    "B": {"A": 950, "C": 550, "D": 550},
    "C": {"A": 550, "B": 550, "D": 950},
    "D": {"A": 550, "B": 550, "C": 950},
}

SEARCH_SPACE_DEMO = 326592
SEARCH_SPACE_REAL = 1.4e42
N_LOAD_EQUATIONS = 24

ROOT_LB = 746.7
ROOT_T = 0.437
ROOT_Q_EXAMPLE = 0.594
BRANCH_ROW4_LB_1 = 1037.5
BRANCH_ROW4_LB_0 = 746.7
BEST_SEQUENCE = [1375, 1350, 1225, 1000, 990]
LPS_SOLVED = 2269
LPS_PRUNED = 1130

MILP_OBJECTIVE = 990
SOLVER_LB = 990
GAP_PCT = 0.0

THEORETICAL_LB_GROUP = 810
GLOBAL_LB = 746.7
BRUTE_FORCE_COMBOS = 1296

IMPROVEMENT_PCT = 26.7


def fmt_kw(x):
    if float(x).is_integer():
        return f"{int(x):,} kW"
    return f"{x:,.1f} kW"
