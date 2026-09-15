"""
MILP BRANCH-AND-BOUND — cinematic visual story (illustrative only)

Everything in this file is hardcoded/illustrative. No solver, no PuLP, no
CBC, no real optimization is performed anywhere — every number below is
invented purely to make the animation's narrative arc land cleanly:

  ROWS -> CUTS -> GROUPS -> ROW DECISION -> TREE -> BRANCH -> BOUND
  -> PRUNE -> NEW BEST -> FINAL PATH -> SOLUTION

The branch-and-bound tree below is not abstract filler: it branches on the
real *kind* of decision this problem has (which pairing a 2-source row
uses), it just explores a small hand-picked slice of it (4 of the 6
pairing options for ROW 3, then 2 of the 6 for ROW 4) so the animation
stays legible. All LB / BEST / search-space numbers are invented to make
the pruning story land cleanly — they do not represent a real run.

Run:
    manim -pql bnb_demo_scene.py BranchAndBoundStory
    manim -pqh bnb_demo_scene.py BranchAndBoundStory
"""
from manim import *

# ── palette: dark, tech, cinematic ──
CYAN = "#4DE8FF"
GOLD = "#FFC857"
NEUTRAL = "#3A3E46"
NEUTRAL_LINE = "#5A5F68"
DIM = "#2A2D33"
PRUNE_RED = "#FF5C5C"
GROUP_A = "#3E6FE0"
GROUP_B = "#8B5CF6"
INK = "#EDEDED"

LABEL_FONT = "Segoe UI"
DATA_FONT = "Consolas"


def label(txt, size=22, color=INK, weight=NORMAL, font=LABEL_FONT):
    return Text(txt, font=font, font_size=size, color=color, weight=weight)


def data_text(txt, size=22, color=INK, weight=NORMAL):
    return Text(txt, font=DATA_FONT, font_size=size, color=color, weight=weight)


def glow(mobject, color=CYAN, layers=3, spread=0.12, opacity=0.35):
    """Cheap glow: stack faint enlarged copies of the same stroke behind it."""
    halo = VGroup()
    for i in range(layers, 0, -1):
        copy = mobject.copy()
        copy.set_stroke(color=color, width=mobject.get_stroke_width() + spread * i * 10, opacity=opacity / i)
        copy.set_fill(opacity=0)
        halo.add(copy)
    return halo


def candidate_cloud(center, n=12, radius=0.42, color=NEUTRAL_LINE):
    """A cluster of tiny dots around `center` — visual shorthand for
    'this node still represents many possible solutions', not one."""
    dots = VGroup()
    golden_angle = 137.5 * DEGREES
    for i in range(n):
        r = radius * np.sqrt((i + 0.5) / n)
        theta = i * golden_angle
        pos = np.array(center) + np.array([r * np.cos(theta), r * np.sin(theta), 0])
        d = Dot(point=pos, radius=0.028, color=color, fill_opacity=0.85)
        dots.add(d)
    return dots


PAIR_OPTIONS = ["AB", "AC", "AD", "BC", "BD", "CD"]

# ══════════════════════════════════════════════════════════════════════
#  hardcoded illustrative data
# ══════════════════════════════════════════════════════════════════════

ROWS = [
    {"name": "ROW 1", "kw": 500, "type": "2-SOURCE"},
    {"name": "ROW 2", "kw": 620, "type": "4-SOURCE"},
    {"name": "ROW 3", "kw": 480, "type": "2-SOURCE"},
    {"name": "ROW 4", "kw": 550, "type": "2-SOURCE"},
]

# candidate cuts: (left_count, worst_left, worst_right)
CUT_CANDIDATES = [
    (1, 82, 91),
    (2, 78, 88),   # winner
    (3, 84, 79),
]
BEST_CUT_INDEX = 1

# ── the branch-and-bound tree: GROUP 2 = {ROW 3, ROW 4}, both 2-source.
# Root branches on ROW 3's pairing (4 of 6 options shown); the surviving
# branches then branch again on ROW 4's pairing. Every LB / prune / new-best
# below was chosen by hand to make a clean, honest-looking DFS story —
# fully invented, not computed. ──
TREE_Y = {0: 2.6, 1: 1.2, 2: -0.35}

TREE = [
    {"id": "root", "parent": None, "depth": 0, "x": 0.0, "lb": None, "kind": "root"},
    {"id": "AB", "parent": "root", "depth": 1, "x": -4.5, "lb": 91, "kind": "open", "pick": "AB"},
    {"id": "AC", "parent": "root", "depth": 1, "x": -1.5, "lb": 99, "kind": "prune_subtree", "pick": "AC"},
    {"id": "BC", "parent": "root", "depth": 1, "x": 1.5, "lb": 91, "kind": "open", "pick": "BC"},
    {"id": "CD", "parent": "root", "depth": 1, "x": 4.5, "lb": 78, "kind": "open", "pick": "CD"},

    {"id": "AB-AB", "parent": "AB", "depth": 2, "x": -5.3, "lb": 97, "kind": "new_best", "pick": "AB"},
    {"id": "AB-CD", "parent": "AB", "depth": 2, "x": -3.7, "lb": 94, "kind": "new_best", "pick": "CD"},

    {"id": "BC-AB", "parent": "BC", "depth": 2, "x": 0.7, "lb": 101, "kind": "prune", "pick": "AB"},
    {"id": "BC-CD", "parent": "BC", "depth": 2, "x": 2.3, "lb": 90, "kind": "new_best", "pick": "CD"},

    {"id": "CD-AB", "parent": "CD", "depth": 2, "x": 3.7, "lb": 85, "kind": "new_best", "pick": "AB"},
    {"id": "CD-AC", "parent": "CD", "depth": 2, "x": 5.3, "lb": 82, "kind": "new_best", "pick": "AC"},
]
BY_ID = {n["id"]: n for n in TREE}
L1_IDS = ["AB", "AC", "BC", "CD"]
FINAL_PATH = ["root", "CD", "CD-AC"]
M_STAR = 82

# illustrative-only, invented, shrinks as branches get eliminated
SEARCH_SPACE_STEPS = [1728, 1296, 864, 432]

FINAL_GROUPS = [
    ("GROUP 1", [("ROW 1", "AB"), ("ROW 2", "4-SOURCE")]),
    ("GROUP 2", [("ROW 3", "CD"), ("ROW 4", "AC")]),
]


def pos_of(node_id):
    n = BY_ID[node_id]
    return np.array([n["x"], TREE_Y[n["depth"]], 0.0])


# ══════════════════════════════════════════════════════════════════════
#  builders
# ══════════════════════════════════════════════════════════════════════

def create_row_card(row, width=2.5, height=1.3):
    box = RoundedRectangle(corner_radius=0.1, width=width, height=height,
                            stroke_color=NEUTRAL_LINE, stroke_width=2, fill_color=DIM, fill_opacity=0.9)
    kw = data_text(f"{row['kw']} kW", size=22, color=CYAN, weight=BOLD)
    kw.move_to(box.get_center() + UP * 0.15)
    typ = label(row["type"], size=13, color=GRAY_B)
    typ.move_to(box.get_center() + DOWN * 0.35)
    name = label(row["name"], size=13, color=GRAY_A)
    name.move_to(box.get_center() + UP * 0.48)
    return VGroup(box, name, kw, typ)


def create_cut(x, y_top, y_bot):
    return DashedLine([x, y_top, 0], [x, y_bot, 0], color=CYAN, stroke_width=2.5, dash_length=0.1)


def create_group_region(x_left, x_right, y, height, color):
    w = x_right - x_left
    rect = Rectangle(width=w, height=height, stroke_width=0, fill_color=color, fill_opacity=0.14)
    rect.move_to([(x_left + x_right) / 2, y, 0])
    return rect


def create_node(pos, radius=0.26, kind="open", pick=None):
    fill = NEUTRAL
    stroke = NEUTRAL_LINE
    if kind in ("prune", "prune_subtree"):
        fill, stroke = DIM, PRUNE_RED
    elif kind == "new_best":
        fill, stroke = NEUTRAL, GOLD
    c = Circle(radius=radius, fill_color=fill, fill_opacity=1, stroke_color=stroke, stroke_width=2.5)
    c.move_to(pos)
    if pick:
        txt = data_text(pick, size=11, color=WHITE)
        txt.move_to(c.get_center())
        return VGroup(c, txt)
    return VGroup(c)


def create_branch(p1, p2, color=NEUTRAL_LINE, width=2):
    return Line(p1, p2, color=color, stroke_width=width)


# ══════════════════════════════════════════════════════════════════════

class BranchAndBoundStory(Scene):
    def construct(self):
        self.camera.background_color = "#050608"

        tag = label("MILP · BRANCH & BOUND  —  ILLUSTRATIVE EXAMPLE", size=16, color=GRAY_C)
        tag.to_corner(UL, buff=0.4)
        self.play(FadeIn(tag, run_time=0.6))

        self.data_stream_entry()
        self.wait(0.2)

        cut_lines, group_rects = self.grouping_search()
        self.wait(0.2)

        node_mobs, branch_mobs, hud, space_hud = self.bridge_to_pairing_tree(group_rects)
        self.wait(0.2)

        self.grow_tree(node_mobs, branch_mobs, hud, space_hud)
        self.wait(0.2)

        self.collapse_to_final_path(node_mobs, branch_mobs)
        self.wait(0.3)

        self.final_solution()
        self.wait(1.5)

    # ────────────────────────────────────────────────────────────────
    def data_stream_entry(self):
        # VO:
        # "We have several load rows that need to be grouped,
        #  and some of them still need a pairing decision."
        spine = Line(LEFT * 6.5, RIGHT * 6.5, color=DIM, stroke_width=1.5)
        spine.move_to(UP * 1.5)
        self.play(Create(spine), run_time=0.6)

        cards = VGroup(*[create_row_card(r) for r in ROWS])
        cards.arrange(RIGHT, buff=0.5)
        cards.move_to(UP * 1.5)
        self.cards = cards
        self.card_positions = [c.get_center().copy() for c in cards]

        entrances = []
        for i, card in enumerate(cards):
            box, name, kw, typ = card
            start = box.get_center() + LEFT * 3.0
            box.move_to(start)
            name.move_to(start + UP * 0.48)
            kw.move_to(start + UP * 0.15)
            typ.move_to(start + DOWN * 0.35)
            target = self.card_positions[i]
            seq = AnimationGroup(
                box.animate.move_to(target),
                run_time=0.5, rate_func=rate_functions.ease_out_cubic,
            )
            entrances.append(seq)

        self.play(LaggedStart(*entrances, lag_ratio=0.35), run_time=2.0)

        settle = []
        for card in cards:
            box, name, kw, typ = card
            name.move_to(box.get_center() + UP * 0.48)
            kw.move_to(box.get_center() + UP * 0.15)
            typ.move_to(box.get_center() + DOWN * 0.35)
            settle.append(AnimationGroup(FadeIn(name, scale=1.2), FadeIn(kw, scale=1.1)))
        self.play(LaggedStart(*settle, lag_ratio=0.25), run_time=1.0)

        settle2 = [FadeIn(card[3], shift=UP * 0.05) for card in cards]
        self.play(LaggedStart(*settle2, lag_ratio=0.2), run_time=0.8)

        pulses = [card[0].animate.scale(0.97) for card in cards]
        self.play(*pulses, rate_func=there_and_back, run_time=0.4)
        self.play(FadeOut(spine), run_time=0.4)

    # ────────────────────────────────────────────────────────────────
    def grouping_search(self):
        cards = self.cards
        y = 1.5
        gaps = []
        for i in range(len(cards) - 1):
            x = (cards[i].get_right()[0] + cards[i + 1].get_left()[0]) / 2
            gaps.append(x)

        intro = label("TESTING WHERE TO CUT THE ROW SEQUENCE", size=16, color=GRAY_B)
        intro.next_to(cards, UP, buff=0.7)
        self.play(FadeIn(intro, shift=UP * 0.1), run_time=0.4)

        cuts = VGroup(*[create_cut(x, y + 1.0, y - 1.0) for x in gaps])
        cuts.set_opacity(0)
        self.play(FadeIn(cuts, run_time=0.4))
        for c in cuts:
            self.play(c.animate.set_opacity(0.8), run_time=0.25)
            self.play(c.animate.set_opacity(0.35), run_time=0.25)
        self.play(FadeOut(intro), run_time=0.3)

        left_edge = cards[0].get_left()[0] - 0.3
        right_edge = cards[-1].get_right()[0] + 0.3
        region_h = 1.7

        left_rect = create_group_region(left_edge, gaps[0], y, region_h, GROUP_A)
        right_rect = create_group_region(gaps[0], right_edge, y, region_h, GROUP_B)
        left_num = data_text("", size=30, color=GROUP_A, weight=BOLD)
        right_num = data_text("", size=30, color=GROUP_B, weight=BOLD)

        self.play(FadeIn(left_rect), FadeIn(right_rect), run_time=0.4)

        for idx, (cut_i, wl, wr) in enumerate(CUT_CANDIDATES):
            split_x = gaps[cut_i - 1]
            new_left = create_group_region(left_edge, split_x, y, region_h, GROUP_A)
            new_right = create_group_region(split_x, right_edge, y, region_h, GROUP_B)
            new_left_num = data_text(str(wl), size=30, color=GROUP_A, weight=BOLD)
            new_left_num.next_to(new_left, UP, buff=0.15)
            new_right_num = data_text(str(wr), size=30, color=GROUP_B, weight=BOLD)
            new_right_num.next_to(new_right, UP, buff=0.15)

            active_cut = cuts[cut_i - 1]
            self.play(
                Transform(left_rect, new_left),
                Transform(right_rect, new_right),
                Transform(left_num, new_left_num),
                Transform(right_num, new_right_num),
                active_cut.animate.set_opacity(1.0).set_stroke(GOLD if idx == BEST_CUT_INDEX else CYAN),
                run_time=0.7, rate_func=smooth,
            )
            self.wait(0.35)
            if idx != BEST_CUT_INDEX:
                self.play(active_cut.animate.set_opacity(0.25).set_stroke(CYAN), run_time=0.3)

        for i, c in enumerate(cuts):
            if i != BEST_CUT_INDEX:
                self.play(c.animate.set_opacity(0.08), run_time=0.3)

        best_tag = label("BEST GROUPING — WORST CASE MINIMIZED", size=18, color=GOLD, weight=BOLD)
        best_tag.next_to(cards, UP, buff=1.25)
        self.play(
            cuts[BEST_CUT_INDEX].animate.set_stroke(width=4),
            FadeIn(best_tag, scale=1.2),
            run_time=0.5,
        )
        self.play(cuts[BEST_CUT_INDEX].animate.scale(1.0), rate_func=there_and_back, run_time=0.4)
        self.wait(0.4)
        self.play(FadeOut(best_tag), run_time=0.3)

        self.group_left_num = left_num
        self.group_right_num = right_num

        bridge = label("GROUPING IS FIXED. NOW: THE PAIRING INSIDE EACH GROUP.", size=17, color=GRAY_A)
        bridge.next_to(cards, UP, buff=0.7)
        self.play(FadeIn(bridge, shift=UP * 0.1), run_time=0.4)
        self.wait(0.6)
        self.play(FadeOut(bridge), run_time=0.3)

        return cuts, (left_rect, right_rect)

    # ────────────────────────────────────────────────────────────────
    def bridge_to_pairing_tree(self, group_rects):
        """Point 8: explicitly transform ONE real row decision into the
        root of the search tree, instead of conjuring the tree from
        nowhere. ROW 3 is the row this tree actually explores."""
        cards = self.cards
        left_rect, right_rect = group_rects
        number_labels = VGroup(self.group_left_num, self.group_right_num)
        row3_card = cards[2]
        other_cards = VGroup(*[c for i, c in enumerate(cards) if i != 2])

        self.play(
            FadeOut(other_cards), FadeOut(number_labels),
            FadeOut(left_rect), FadeOut(right_rect),
            run_time=0.5,
        )
        self.play(row3_card.animate.scale(1.15).move_to(UP * 2.0), run_time=0.6, rate_func=rate_functions.ease_in_out_cubic)

        q = label("ROW 3 NEEDS A PAIRING DECISION", size=18, color=CYAN)
        q.next_to(row3_card, DOWN, buff=0.35)
        self.play(FadeIn(q, shift=UP * 0.1), run_time=0.4)

        chips = VGroup(*[
            RoundedRectangle(corner_radius=0.06, width=0.85, height=0.42,
                              fill_color=DIM, fill_opacity=1, stroke_color=NEUTRAL_LINE, stroke_width=1.5)
            for _ in PAIR_OPTIONS
        ])
        chip_labels = VGroup(*[data_text(p, size=15, color=INK) for p in PAIR_OPTIONS])
        for chip, txt in zip(chips, chip_labels):
            txt.move_to(chip)
        chip_group = VGroup(*[VGroup(c, t) for c, t in zip(chips, chip_labels)])
        chip_group.arrange(RIGHT, buff=0.22)
        chip_group.next_to(q, DOWN, buff=0.4)

        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in chip_group], lag_ratio=0.08), run_time=0.8)
        self.play(LaggedStart(*[Indicate(c, color=CYAN, scale_factor=1.15) for c in chip_group], lag_ratio=0.06), run_time=0.9)
        self.wait(0.2)

        kept_idx = [PAIR_OPTIONS.index(pid) for pid in L1_IDS]
        dropped = VGroup(*[chip_group[i] for i in range(6) if i not in kept_idx])
        kept = [chip_group[i] for i in kept_idx]
        self.play(dropped.animate.set_opacity(0.12), run_time=0.35)

        note = label("(4 of 6 pairings shown here to keep this legible)", size=13, color=GRAY_C)
        note.next_to(chip_group, DOWN, buff=0.25)
        self.play(FadeIn(note), run_time=0.3)

        # collapse ROW 3 card into the root node, kept chips fly down into L1
        root_pos = pos_of("root")
        root_node = create_node(root_pos, radius=0.22, kind="root")
        self.play(
            FadeOut(q), FadeOut(note), FadeOut(dropped),
            ReplacementTransform(row3_card, root_node),
            run_time=0.6,
        )

        cloud = candidate_cloud(root_pos, n=12, color=NEUTRAL_LINE)
        self.play(FadeIn(cloud, scale=0.6), run_time=0.4)

        branch_label = label("ROW 3 PAIRING?", size=16, color=GRAY_A)
        branch_label.next_to(root_node, DOWN, buff=0.35).shift(LEFT * 0.0)
        branch_label.move_to([0, (TREE_Y[0] + TREE_Y[1]) / 2 + 0.15, 0])
        self.play(FadeIn(branch_label), run_time=0.3)

        l1_targets = [pos_of(nid) for nid in L1_IDS]
        branches = VGroup(*[create_branch(root_pos, t) for t in l1_targets])
        self.play(LaggedStart(*[Create(b) for b in branches], lag_ratio=0.15), run_time=0.9)

        # candidate cloud splits: one node = many possibilities -> branching
        # divides that set (point 1 + point 8 combined)
        mini_clouds = self.split_cloud_to_children(cloud, l1_targets, per_child=3)

        self.play(FadeOut(branch_label), run_time=0.3)

        l1_nodes = {}
        l1_labels_grp = VGroup()
        for nid, chip, target in zip(L1_IDS, kept, l1_targets):
            n = BY_ID[nid]
            node = create_node(target, radius=0.26, kind="open", pick=n["pick"])
            self.play(ReplacementTransform(chip, node), run_time=0.35)
            l1_nodes[nid] = node

        # HUD: BEST
        hud_box = RoundedRectangle(corner_radius=0.08, width=2.0, height=0.9,
                                    stroke_color=NEUTRAL_LINE, stroke_width=1.5, fill_color="#101216", fill_opacity=0.9)
        hud_box.to_corner(UR, buff=0.4)
        hud_label = label("BEST", size=14, color=GRAY_B)
        hud_label.move_to(hud_box.get_center() + UP * 0.22)
        hud_value = data_text("M = 100", size=26, color=GOLD, weight=BOLD)
        hud_value.move_to(hud_box.get_center() + DOWN * 0.15)
        hud = VGroup(hud_box, hud_label, hud_value)

        # HUD: SEARCH SPACE
        space_box = RoundedRectangle(corner_radius=0.08, width=2.0, height=0.9,
                                      stroke_color=NEUTRAL_LINE, stroke_width=1.5, fill_color="#101216", fill_opacity=0.9)
        space_box.next_to(hud_box, DOWN, buff=0.25)
        space_label = label("SEARCH SPACE", size=11, color=GRAY_B)
        space_label.move_to(space_box.get_center() + UP * 0.22)
        space_value = data_text(f"{SEARCH_SPACE_STEPS[0]:,}", size=20, color=CYAN, weight=BOLD)
        space_value.move_to(space_box.get_center() + DOWN * 0.15)
        space_hud = VGroup(space_box, space_label, space_value)

        self.play(FadeIn(hud, shift=DOWN * 0.15), FadeIn(space_hud, shift=DOWN * 0.15), run_time=0.5)

        node_mobs = {"root": root_node, **l1_nodes}
        branch_mobs = {f"root-{nid}": br for nid, br in zip(L1_IDS, branches)}
        self.mini_clouds = dict(zip(L1_IDS, mini_clouds))

        return node_mobs, branch_mobs, hud, space_hud

    # ────────────────────────────────────────────────────────────────
    def split_cloud_to_children(self, cloud, child_centers, per_child=3):
        n_children = len(child_centers)
        anims = []
        groups = [VGroup() for _ in range(n_children)]
        for i, dot in enumerate(cloud):
            child_idx = i % n_children
            ring_i = i // n_children
            angle = ring_i * (TAU / max(per_child, 1)) + child_idx * 0.7
            offset = 0.22 * np.array([np.cos(angle), np.sin(angle), 0])
            target = np.array(child_centers[child_idx]) + offset + DOWN * 0.35
            anims.append(dot.animate.move_to(target).scale(0.75))
            groups[child_idx].add(dot)
        self.play(LaggedStart(*anims, lag_ratio=0.03), run_time=0.7)
        return groups

    # ────────────────────────────────────────────────────────────────
    def show_bound_check(self, node, lb, best, will_prune):
        """Point 3: make LB-vs-BEST visually causal instead of implied."""
        cmp_symbol = "≥" if will_prune else "<"
        color = PRUNE_RED if will_prune else CYAN
        txt = data_text(f"LB {lb}  {cmp_symbol}  BEST {best}", size=15, color=color)
        txt.next_to(node, UP, buff=0.16)
        ring = Circle(radius=0.34, stroke_color=color, stroke_width=2, fill_opacity=0)
        ring.move_to(node.get_center())
        self.play(FadeIn(txt, shift=UP * 0.05), FadeIn(ring), run_time=0.22)
        self.wait(0.2)
        self.play(FadeOut(txt), FadeOut(ring), run_time=0.2)

    # ────────────────────────────────────────────────────────────────
    def drop_search_space(self, space_hud, step_idx):
        space_value = space_hud[2]
        new_val = data_text(f"{SEARCH_SPACE_STEPS[step_idx]:,}", size=20, color=CYAN, weight=BOLD)
        new_val.move_to(space_value.get_center())
        self.play(Transform(space_value, new_val), run_time=0.3)
        self.play(space_hud[0].animate.set_stroke(color=PRUNE_RED), run_time=0.15)
        self.play(space_hud[0].animate.set_stroke(color=NEUTRAL_LINE), run_time=0.25)

    # ────────────────────────────────────────────────────────────────
    def grow_tree(self, node_mobs, branch_mobs, hud, space_hud):
        hud_value = hud[2]
        node_labels = {}
        current_best = 100
        space_step = 0

        def make_lb(nid, size=14):
            n = BY_ID[nid]
            t = data_text(f"LB {n['lb']}", size=size, color=GRAY_A)
            t.next_to(node_mobs[nid], DOWN, buff=0.12)
            return t

        for nid in L1_IDS:
            lb_lbl = make_lb(nid)
            node_labels[nid] = lb_lbl
            self.play(FadeIn(lb_lbl), node_mobs[nid].animate.set_stroke(width=3.5), run_time=0.25)
            self.play(node_mobs[nid].animate.set_stroke(width=2.5), run_time=0.15)

        for nid in L1_IDS:
            n = BY_ID[nid]
            node = node_mobs[nid]
            lb_lbl = node_labels[nid]

            will_prune = n["lb"] >= current_best
            self.show_bound_check(node, n["lb"], current_best, will_prune)

            if n["kind"] == "prune_subtree":
                self.prune_with_subtree_reveal(nid, node, branch_mobs[f"root-{nid}"], lb_lbl)
                space_step += 1
                self.drop_search_space(space_hud, space_step)
                if nid in self.mini_clouds:
                    self.play(self.mini_clouds[nid].animate.set_opacity(0.08), run_time=0.3)
                continue

            # open: expand into ROW 4 pairing choices
            self.play(self.mini_clouds[nid].animate.set_opacity(0.15), run_time=0.25)
            children = [c["id"] for c in TREE if c["parent"] == nid]
            branch_label = label("ROW 4 PAIRING?", size=13, color=GRAY_A)
            branch_label.move_to([n["x"], (TREE_Y[1] + TREE_Y[2]) / 2 + 0.1, 0])
            self.play(FadeIn(branch_label), run_time=0.25)

            child_branches = VGroup()
            for cid in children:
                br = create_branch(pos_of(nid), pos_of(cid))
                child_branches.add(br)
                branch_mobs[f"{nid}-{cid}"] = br
            self.play(LaggedStart(*[Create(b) for b in child_branches], lag_ratio=0.2), run_time=0.5)
            self.play(FadeOut(branch_label), run_time=0.2)

            for cid in children:
                cn = BY_ID[cid]
                cnode = create_node(pos_of(cid), radius=0.2, kind="open", pick=cn["pick"])
                node_mobs[cid] = cnode
                self.play(FadeIn(cnode, scale=0.4), run_time=0.22)
                clb = make_lb(cid, size=12)
                node_labels[cid] = clb
                self.play(FadeIn(clb), run_time=0.18)

                child_prune = cn["lb"] >= current_best
                self.show_bound_check(cnode, cn["lb"], current_best, child_prune)

                if child_prune:
                    self.prune_node(cnode, branch_mobs[f"{nid}-{cid}"], clb)
                    space_step += 1
                    self.drop_search_space(space_hud, space_step)
                else:
                    current_best = cn["lb"]
                    self.new_best_flash(cnode, hud_value, current_best)

        self.current_best = current_best
        self.node_mobs = node_mobs
        self.node_labels = node_labels
        self.branch_mobs = branch_mobs
        self.hud = hud
        self.space_hud = space_hud

        # nothing left in the search space can beat 82 — the remaining
        # (unshown) pairing options collapse in one final illustrative step
        final_note = label("REMAINING OPTIONS CANNOT BEAT THE CURRENT BEST", size=14, color=GRAY_C)
        final_note.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(final_note), run_time=0.3)
        space_step += 1
        self.drop_search_space(space_hud, space_step)
        self.wait(0.4)
        self.play(FadeOut(final_note), run_time=0.3)

    # ────────────────────────────────────────────────────────────────
    def new_best_flash(self, node, hud_value, new_value):
        ring = Circle(radius=0.4, stroke_color=GOLD, stroke_width=3, fill_opacity=0)
        ring.move_to(node.get_center())
        self.play(
            node.animate.set_stroke(GOLD, width=3),
            FadeIn(ring),
            run_time=0.2,
        )
        self.play(ring.animate.scale(1.6).set_stroke(opacity=0), run_time=0.35)
        self.remove(ring)

        new_hud = data_text(f"M = {new_value}", size=26, color=GOLD, weight=BOLD)
        new_hud.move_to(hud_value.get_center())
        self.play(Transform(hud_value, new_hud), run_time=0.25)
        self.play(hud_value.animate.scale(1.15), rate_func=there_and_back, run_time=0.3)

    def prune_node(self, node, branch, lb_label):
        self.play(node.animate.shift(RIGHT * 0.04), run_time=0.05)
        self.play(node.animate.shift(LEFT * 0.08), run_time=0.05)
        self.play(node.animate.shift(RIGHT * 0.04), run_time=0.05)

        x = Cross(scale_factor=0.16, stroke_color=PRUNE_RED, stroke_width=4)
        x.move_to(node.get_center())
        self.play(Create(x), run_time=0.25)
        self.play(
            node.animate.set_fill(opacity=0.35).set_stroke(PRUNE_RED, opacity=0.6),
            branch.animate.set_stroke(opacity=0.25),
            lb_label.animate.set_color(PRUNE_RED).set_opacity(0.6),
            run_time=0.3,
        )

    def prune_with_subtree_reveal(self, nid, node, branch, lb_label):
        """Point 4: before pruning an INTERNAL node, briefly reveal the
        descendants it would have had, so eliminating it visibly reads as
        'we just removed a whole subtree', not just one point."""
        n = BY_ID[nid]
        ghost_offsets = [LEFT * 0.7, RIGHT * 0.7]
        ghost_y = TREE_Y[2]
        ghost_nodes = VGroup()
        ghost_branches = VGroup()
        for off in ghost_offsets:
            gpos = np.array([n["x"], ghost_y, 0]) + off
            gnode = Circle(radius=0.15, stroke_color=NEUTRAL_LINE, stroke_width=1.5,
                            fill_color=NEUTRAL, fill_opacity=0.5)
            gnode.move_to(gpos)
            gbranch = create_branch(node.get_center(), gpos, color=NEUTRAL_LINE, width=1.5)
            ghost_nodes.add(gnode)
            ghost_branches.add(gbranch)

        self.play(
            LaggedStart(*[Create(b) for b in ghost_branches], lag_ratio=0.15),
            LaggedStart(*[FadeIn(g, scale=0.5) for g in ghost_nodes], lag_ratio=0.15),
            run_time=0.5,
        )
        whole = VGroup(node, ghost_nodes, ghost_branches)
        self.play(whole.animate.set_opacity(1.0), Flash(node.get_center(), color=PRUNE_RED, line_length=0.15), run_time=0.3)

        self.play(node.animate.shift(RIGHT * 0.05), run_time=0.05)
        self.play(node.animate.shift(LEFT * 0.1), run_time=0.05)
        self.play(node.animate.shift(RIGHT * 0.05), run_time=0.05)

        x = Cross(scale_factor=0.16, stroke_color=PRUNE_RED, stroke_width=4)
        x.move_to(node.get_center())
        self.play(Create(x), run_time=0.25)
        self.play(
            node.animate.set_fill(opacity=0.3).set_stroke(PRUNE_RED, opacity=0.5),
            branch.animate.set_stroke(opacity=0.2),
            lb_label.animate.set_color(PRUNE_RED).set_opacity(0.5),
            ghost_nodes.animate.set_opacity(0.12),
            ghost_branches.animate.set_stroke(opacity=0.1),
            run_time=0.4,
        )

    # ────────────────────────────────────────────────────────────────
    def collapse_to_final_path(self, node_mobs, branch_mobs):
        path_ids = FINAL_PATH
        keep = set(path_ids)

        dim_anims = []
        for nid, mob in node_mobs.items():
            if nid not in keep:
                dim_anims.append(mob.animate.set_opacity(0.15))
        for nid, mob in self.node_labels.items():
            if nid not in keep:
                dim_anims.append(mob.animate.set_opacity(0.1))
        for key, br in branch_mobs.items():
            a, b = key.split("-", 1)
            if not (a in keep and b in keep):
                dim_anims.append(br.animate.set_opacity(0.08))
        for cloud in self.mini_clouds.values():
            dim_anims.append(cloud.animate.set_opacity(0.05))
        self.play(*dim_anims, run_time=0.8)

        path_edges = VGroup()
        for i in range(len(path_ids) - 1):
            e = create_branch(pos_of(path_ids[i]), pos_of(path_ids[i + 1]), color=GOLD, width=4)
            path_edges.add(e)
        self.play(LaggedStart(*[Create(e) for e in path_edges], lag_ratio=0.25), run_time=1.0)

        star = Star(n=5, outer_radius=0.22, color=GOLD, fill_opacity=1, stroke_width=0)
        star.move_to(node_mobs["CD-AC"].get_center())
        halo = glow(star, color=GOLD, layers=3, spread=0.15, opacity=0.5)
        self.play(
            ReplacementTransform(node_mobs["CD-AC"], star),
            FadeIn(halo),
            run_time=0.6,
        )
        self.play(star.animate.scale(1.3), rate_func=there_and_back, run_time=0.4)

    # ────────────────────────────────────────────────────────────────
    def final_solution(self):
        everything = Group(*self.mobjects)
        self.play(everything.animate.scale(0.55).move_to(UP * 3.5), run_time=1.0, rate_func=rate_functions.ease_in_out_cubic)
        self.play(FadeOut(everything), run_time=0.6)

        cards_out = VGroup()
        for gname, rows in FINAL_GROUPS:
            title = label(gname, size=20, color=GOLD, weight=BOLD)
            row_lines = VGroup(*[
                label(f"{rname} → {val}", size=18, color=INK) for rname, val in rows
            ])
            row_lines.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
            block = VGroup(title, row_lines).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
            cards_out.add(block)
        cards_out.arrange(RIGHT, buff=1.6, aligned_edge=UP)
        cards_out.move_to(UP * 1.3)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cards_out], lag_ratio=0.3), run_time=1.0)
        self.wait(0.6)

        m_label = label("M*", size=32, color=GRAY_B)
        m_value = data_text(f"{M_STAR}", size=110, color=GOLD, weight=BOLD)
        m_group = VGroup(m_label, m_value).arrange(DOWN, buff=0.1)
        m_group.move_to(DOWN * 1.3)

        halo = glow(m_value, color=GOLD, layers=4, spread=0.05, opacity=0.25)
        self.play(FadeIn(m_label, shift=UP * 0.1), run_time=0.4)
        self.play(FadeIn(m_value, scale=0.6), FadeIn(halo), run_time=0.6, rate_func=rate_functions.ease_out_back)
        self.play(m_value.animate.scale(1.05), rate_func=there_and_back, run_time=0.6)

        foot = label("ILLUSTRATIVE EXAMPLE · NOT REAL SOLVER OUTPUT", size=14, color=GRAY_C)
        foot.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(foot), run_time=0.5)
