"""
MILP BRANCH-AND-BOUND — cinematic visual story (illustrative only)

Everything in this file is hardcoded/illustrative. No solver, no PuLP, no
CBC, no real optimization is performed anywhere — every number below is
invented purely to make the animation's narrative arc land cleanly:

  ROWS -> CUTS -> GROUPS -> TREE -> BRANCH -> BOUND -> PRUNE -> NEW BEST
  -> FINAL PATH -> SOLUTION

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

# hardcoded branch-and-bound tree (see module docstring — fully invented)
# each node: id, parent, depth, x, lb, kind: "prune" | "new_best" | "open"
TREE = [
    {"id": "root", "parent": None, "depth": 0, "x": 0.0, "lb": None, "kind": "open"},
    {"id": "A", "parent": "root", "depth": 1, "x": -3.0, "lb": 78, "kind": "open"},
    {"id": "B", "parent": "root", "depth": 1, "x": 3.0, "lb": 88, "kind": "prune"},
    {"id": "A0", "parent": "A", "depth": 2, "x": -4.6, "lb": 97, "kind": "new_best"},
    {"id": "A1", "parent": "A", "depth": 2, "x": -3.6, "lb": 94, "kind": "new_best"},
    {"id": "A2", "parent": "A", "depth": 2, "x": -2.6, "lb": 91, "kind": "open"},
    {"id": "A3", "parent": "A", "depth": 2, "x": -1.6, "lb": 99, "kind": "prune"},
    {"id": "A2a", "parent": "A2", "depth": 3, "x": -3.0, "lb": 101, "kind": "prune"},
    {"id": "A2b", "parent": "A2", "depth": 3, "x": -2.2, "lb": 82, "kind": "new_best"},
]
FINAL_PATH = ["root", "A", "A2", "A2b"]
M_STAR = 82

FINAL_GROUPS = [
    ("GROUP 1", [("ROW 1", "AB"), ("ROW 2", "4-SOURCE")]),
    ("GROUP 2", [("ROW 3", "CD"), ("ROW 4", "AC")]),
]

TREE_Y = {0: 2.7, 1: 1.35, 2: 0.0, 3: -1.35}


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


def create_node(pos, radius=0.26, kind="open"):
    fill = NEUTRAL
    stroke = NEUTRAL_LINE
    if kind == "prune":
        fill, stroke = DIM, PRUNE_RED
    elif kind == "new_best":
        fill, stroke = NEUTRAL, GOLD
    c = Circle(radius=radius, fill_color=fill, fill_opacity=1, stroke_color=stroke, stroke_width=2.5)
    c.move_to(pos)
    return c


def create_branch(p1, p2, color=NEUTRAL_LINE, width=2):
    return Line(p1, p2, color=color, stroke_width=width)


# ══════════════════════════════════════════════════════════════════════

class BranchAndBoundStory(Scene):
    def construct(self):
        self.camera.background_color = "#050608"

        tag = label("MILP · BRANCH & BOUND  —  ILLUSTRATIVE EXAMPLE", size=16, color=GRAY_C)
        tag.to_corner(UL, buff=0.4)
        self.play(FadeIn(tag, run_time=0.6))

        # ── VO: "we have several load rows that need grouping, and some
        # of them need a pairing decision" ──
        self.data_stream_entry()
        self.wait(0.2)

        cut_lines, group_rects, best_group_rects = self.grouping_search()
        self.wait(0.2)

        node_mobs, branch_mobs, hud = self.transform_to_tree(group_rects)
        self.wait(0.2)

        self.grow_tree(node_mobs, branch_mobs, hud)
        self.wait(0.2)

        self.collapse_to_final_path(node_mobs, branch_mobs, hud)
        self.wait(0.3)

        self.final_solution()
        self.wait(1.5)

    # ────────────────────────────────────────────────────────────────
    def data_stream_entry(self):
        # VO:
        # "เรามีหลายแถวโหลดที่ต้องจัดกลุ่ม
        #  และบางแถวต้องตัดสินใจเลือก pairing"
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

        cuts = VGroup(*[create_cut(x, y + 1.0, y - 1.0) for x in gaps])
        cuts.set_opacity(0)
        self.play(FadeIn(cuts, run_time=0.4))
        for c in cuts:
            self.play(c.animate.set_opacity(0.8), run_time=0.25)
            self.play(c.animate.set_opacity(0.35), run_time=0.25)

        left_edge = cards[0].get_left()[0] - 0.3
        right_edge = cards[-1].get_right()[0] + 0.3
        region_h = 1.7

        left_rect = create_group_region(left_edge, gaps[0], y, region_h, GROUP_A)
        right_rect = create_group_region(gaps[0], right_edge, y, region_h, GROUP_B)
        left_num = data_text("", size=30, color=GROUP_A, weight=BOLD)
        right_num = data_text("", size=30, color=GROUP_B, weight=BOLD)

        self.play(FadeIn(left_rect), FadeIn(right_rect), run_time=0.4)

        winner_left_rect = winner_right_rect = None
        winner_left_num = winner_right_num = None

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
            else:
                winner_left_rect, winner_right_rect = new_left, new_right
                winner_left_num, winner_right_num = new_left_num, new_right_num

        for i, c in enumerate(cuts):
            if i != BEST_CUT_INDEX:
                self.play(c.animate.set_opacity(0.08), run_time=0.3)

        best_tag = label("BEST GROUPING", size=18, color=GOLD, weight=BOLD)
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
        return cuts, (left_rect, right_rect), (winner_left_rect, winner_right_rect)

    # ────────────────────────────────────────────────────────────────
    def transform_to_tree(self, group_rects):
        left_rect, right_rect = group_rects
        cards = self.cards
        cuts_and_labels = VGroup(self.group_left_num, self.group_right_num)

        root_pos = np.array([0.0, TREE_Y[0], 0.0])
        a_pos = np.array([TREE[1]["x"], TREE_Y[1], 0.0])
        b_pos = np.array([TREE[2]["x"], TREE_Y[1], 0.0])

        self.play(
            FadeOut(cards), FadeOut(cuts_and_labels),
            run_time=0.6,
        )

        root_node = create_node(root_pos, radius=0.22, kind="open")
        a_node = create_node(a_pos, radius=0.26, kind="open")
        b_node = create_node(b_pos, radius=0.26, kind="open")  # bound (88) < current best (100): stays open for now

        self.play(
            ReplacementTransform(left_rect, a_node),
            ReplacementTransform(right_rect, b_node),
            run_time=0.8, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.play(FadeIn(root_node, scale=0.5), run_time=0.4)

        branch_a = create_branch(root_pos, a_pos)
        branch_b = create_branch(root_pos, b_pos)
        self.play(Create(branch_a), Create(branch_b), run_time=0.6)

        lb_a = data_text(f"LB {TREE[1]['lb']}", size=16, color=GRAY_A).next_to(a_node, DOWN, buff=0.15)
        lb_b = data_text(f"LB {TREE[2]['lb']}", size=16, color=GRAY_A).next_to(b_node, DOWN, buff=0.15)
        self.play(FadeIn(lb_a), FadeIn(lb_b), run_time=0.4)

        # HUD
        hud_box = RoundedRectangle(corner_radius=0.08, width=2.0, height=0.9,
                                    stroke_color=NEUTRAL_LINE, stroke_width=1.5, fill_color="#101216", fill_opacity=0.9)
        hud_box.to_corner(UR, buff=0.4)
        hud_label = label("BEST", size=14, color=GRAY_B)
        hud_label.move_to(hud_box.get_center() + UP * 0.22)
        hud_value = data_text("M = 100", size=26, color=GOLD, weight=BOLD)
        hud_value.move_to(hud_box.get_center() + DOWN * 0.15)
        hud = VGroup(hud_box, hud_label, hud_value)
        self.play(FadeIn(hud, shift=DOWN * 0.15), run_time=0.5)

        node_mobs = {"root": root_node, "A": a_node, "B": b_node}
        node_labels = {"A": lb_a, "B": lb_b}
        branch_mobs = {"root-A": branch_a, "root-B": branch_b}

        # B's bound (88) is still below the starting BEST (100) here, so it
        # stays open — DFS visits A's whole subtree first (dropping BEST all
        # the way to 82) before B ever gets its bound re-checked in grow_tree().
        return (node_mobs, node_labels), branch_mobs, hud

    # ────────────────────────────────────────────────────────────────
    def grow_tree(self, node_bundle, branch_mobs, hud):
        node_mobs, node_labels = node_bundle
        hud_value = hud[2]
        current_best = 100

        by_id = {n["id"]: n for n in TREE}

        def pos_of(node_id):
            n = by_id[node_id]
            return np.array([n["x"], TREE_Y[n["depth"]], 0.0])

        # expand A's children: A0, A1, A2, A3
        a_children = ["A0", "A1", "A2", "A3"]
        self.play(node_mobs["A"].animate.set_stroke(width=4), rate_func=there_and_back, run_time=0.3)

        branches = VGroup()
        for cid in a_children:
            br = create_branch(pos_of("A"), pos_of(cid))
            branches.add(br)
        self.play(LaggedStart(*[Create(b) for b in branches], lag_ratio=0.15), run_time=0.9)

        for cid, br in zip(a_children, branches):
            n = by_id[cid]
            node = create_node(pos_of(cid), radius=0.22, kind="open")
            self.play(FadeIn(node, scale=0.4), run_time=0.25)
            self.play(node.animate.scale(1.15), rate_func=there_and_back, run_time=0.25)

            lb_lbl = data_text(f"LB {n['lb']}", size=14, color=GRAY_A)
            lb_lbl.next_to(node, DOWN, buff=0.12)
            self.play(FadeIn(lb_lbl), run_time=0.2)

            node_mobs[cid] = node
            node_labels[cid] = lb_lbl
            branch_mobs[f"A-{cid}"] = br

            if n["kind"] == "new_best":
                current_best = n["lb"]
                self.new_best_flash(node, hud_value, current_best)
                if cid == "A2":
                    pass
            elif n["kind"] == "prune":
                self.prune_node(node, br, lb_lbl, compare_best=current_best)
            else:
                # "A2": open, will expand further below
                pass

        # expand A2's children: A2a, A2b
        a2_children = ["A2a", "A2b"]
        self.play(node_mobs["A2"].animate.set_stroke(width=4), rate_func=there_and_back, run_time=0.3)
        branches2 = VGroup()
        for cid in a2_children:
            br = create_branch(pos_of("A2"), pos_of(cid))
            branches2.add(br)
        self.play(LaggedStart(*[Create(b) for b in branches2], lag_ratio=0.2), run_time=0.7)

        for cid, br in zip(a2_children, branches2):
            n = by_id[cid]
            node = create_node(pos_of(cid), radius=0.2, kind="open")
            self.play(FadeIn(node, scale=0.4), run_time=0.25)
            lb_lbl = data_text(f"LB {n['lb']}", size=13, color=GRAY_A)
            lb_lbl.next_to(node, DOWN, buff=0.1)
            self.play(FadeIn(lb_lbl), run_time=0.2)

            node_mobs[cid] = node
            node_labels[cid] = lb_lbl
            branch_mobs[f"A2-{cid}"] = br

            if n["kind"] == "prune":
                self.prune_node(node, br, lb_lbl, compare_best=current_best)
            elif n["kind"] == "new_best":
                current_best = n["lb"]
                self.new_best_flash(node, hud_value, current_best)

        # A's whole subtree is done (BEST is now as low as it will get from
        # this branch) — DFS backtracks to sibling B and re-checks its bound
        # against the now-much-lower BEST. 88 >= 82: the entire B subtree
        # never needed to be opened at all.
        self.play(node_mobs["B"].animate.set_stroke(width=4), rate_func=there_and_back, run_time=0.3)
        self.prune_node(node_mobs["B"], branch_mobs["root-B"], node_labels["B"], compare_best=current_best)

        self.current_best = current_best
        self.node_mobs = node_mobs
        self.node_labels = node_labels
        self.branch_mobs = branch_mobs
        self.hud = hud

    # ────────────────────────────────────────────────────────────────
    def new_best_flash(self, node, hud_value, new_value):
        ring = Circle(radius=node.radius * 1.8, stroke_color=GOLD, stroke_width=3, fill_opacity=0)
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

    def prune_node(self, node, branch, lb_label, compare_best=None):
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

    # ────────────────────────────────────────────────────────────────
    def collapse_to_final_path(self, node_bundle, branch_mobs, hud):
        node_mobs, node_labels = node_bundle
        path_ids = FINAL_PATH
        keep = set(path_ids)

        dim_anims = []
        for nid, mob in node_mobs.items():
            if nid not in keep:
                dim_anims.append(mob.animate.set_opacity(0.15))
        for nid, mob in node_labels.items():
            if nid not in keep:
                dim_anims.append(mob.animate.set_opacity(0.1))
        for key, br in branch_mobs.items():
            a, b = key.split("-")[-2:] if "-" in key else (key, key)
            if not (a in keep and b in keep):
                dim_anims.append(br.animate.set_opacity(0.08))
        self.play(*dim_anims, run_time=0.8)

        by_id = {n["id"]: n for n in TREE}

        def pos_of(node_id):
            n = by_id[node_id]
            return np.array([n["x"], TREE_Y[n["depth"]], 0.0])

        path_edges = VGroup()
        for i in range(len(path_ids) - 1):
            e = create_branch(pos_of(path_ids[i]), pos_of(path_ids[i + 1]), color=GOLD, width=4)
            path_edges.add(e)
        self.play(LaggedStart(*[Create(e) for e in path_edges], lag_ratio=0.25), run_time=1.0)

        star = Star(n=5, outer_radius=0.22, color=GOLD, fill_opacity=1, stroke_width=0)
        star.move_to(node_mobs["A2b"].get_center())
        halo = glow(star, color=GOLD, layers=3, spread=0.15, opacity=0.5)
        self.play(
            ReplacementTransform(node_mobs["A2b"], star),
            FadeIn(halo),
            run_time=0.6,
        )
        self.play(star.animate.scale(1.3), rate_func=there_and_back, run_time=0.4)

        self.final_star = star
        self.final_halo = halo
        self.path_group = VGroup(*[node_mobs[n] for n in path_ids[:-1]], path_edges, star, halo)

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
