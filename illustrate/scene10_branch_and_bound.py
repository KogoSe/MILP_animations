"""Scene 10 -- "Branch and Bound"

Built strictly from scene10_prompt.md + common_prompt.md.

Starts from: black (Scene 09 ended on "To close this gap, the solver
starts to branch." then faded to black).

Ends with: fade to black after "The best answer found is 990 kW. But is
it truly the best?"

Run with:
    manim -pqh scene10_branch_and_bound.py Scene10BranchAndBound
"""
import random

from manim import *

from common.style import (
    BG_COLOR, TEXT_COLOR, SECONDARY_COLOR, HL_COLOR, LB_COLOR, FAIL_COLOR,
)
from common.layout import caption, LayoutCheckMixin
from common.data import (
    ROOT_LB, BRANCH_ROW4_LB_1, BRANCH_ROW4_LB_0, BEST_SEQUENCE,
    LPS_SOLVED, SEARCH_SPACE_DEMO,
)

LOOP_STEPS = ["Branch", "Solve", "Bound", "Prune"]
LOOP_YS = [-0.6, -1.0, -1.4, -1.8]


def fmt_lb(x):
    if float(x).is_integer():
        return f"{int(x):,}"
    return f"{x:,.1f}"


class Scene10BranchAndBound(LayoutCheckMixin, Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        self.current_caption = None

        self.beat_10_1_root()
        self.beat_10_2_branch()
        self.beat_10_3_real_answers()
        self.beat_10_4_bound_prune()
        self.beat_10_5_repeat()
        self.beat_10_6_work_saved()

    # --------------------------------------------------------- helpers ---
    def swap_caption(self, text):
        new_cap = caption(text)
        if self.current_caption is not None:
            self.play(FadeOut(self.current_caption))
        self.play(FadeIn(new_cap))
        self.current_caption = new_cap
        return new_cap

    def open_node(self, lb_value=None, w=1.5, h=0.6):
        # fill_color is set explicitly (matching the background) because
        # Manim's shape default fill_color is its brand red at opacity 0 --
        # any later .animate.set_opacity() call would otherwise reveal it.
        rect = RoundedRectangle(width=w, height=h, corner_radius=0.08,
                                 stroke_color=SECONDARY_COLOR, stroke_width=2,
                                 fill_color=BG_COLOR, fill_opacity=0)
        text = f"LB {fmt_lb(lb_value)}" if lb_value is not None else ""
        label = Tex(text, font_size=24, color=LB_COLOR) if text else Tex("", font_size=24)
        label.move_to(rect.get_center())
        grp = VGroup(rect, label)
        grp.rect, grp.label = rect, label
        return grp

    def set_node_lb(self, node, lb_value):
        new_label = Tex(f"LB {fmt_lb(lb_value)}", font_size=24, color=LB_COLOR)
        new_label.move_to(node.rect.get_center())
        return Transform(node.label, new_label)

    def generic_node(self, r=0.18):
        return Circle(radius=r, stroke_color=SECONDARY_COLOR, stroke_width=2,
                       fill_color=BG_COLOR, fill_opacity=0)

    def leaf(self):
        return Square(side_length=0.36, fill_color=HL_COLOR, fill_opacity=1, stroke_width=0)

    def edge(self, a, b, label=None, label_side=LEFT, label_shift=0.35):
        line = Line(a, b, stroke_color=SECONDARY_COLOR, stroke_width=2)
        if label is None:
            return line
        mid = (a + b) / 2
        offset = LEFT * label_shift if label_side is LEFT else RIGHT * label_shift
        lbl = Tex(label, font_size=22, color=TEXT_COLOR)
        lbl.move_to(mid + offset)
        return VGroup(line, lbl)

    def build_scoreboard(self):
        tag = Tex("Simplified picture --- real solvers also add cuts and heuristics",
                   font_size=22, color=SECONDARY_COLOR)
        tag.move_to([-6.4 + tag.width / 2, 3.3, 0])

        divider = Line([3.4, 2.8, 0], [3.4, -2.5, 0], color=SECONDARY_COLOR,
                        stroke_width=1, stroke_opacity=0.4)

        best_label = Tex("BEST", font_size=26, color=SECONDARY_COLOR)
        best_label.move_to([5.0, 2.4, 0])
        best_value = Tex("---", font_size=40, color=HL_COLOR)
        best_value.move_to([5.0, 1.85, 0])

        info_box = RoundedRectangle(width=2.7, height=1.3, corner_radius=0.08,
                                     stroke_color=SECONDARY_COLOR, stroke_width=2)
        info_box.move_to([5.0, 0.55, 0])
        info_text = Tex("", font_size=22, color=TEXT_COLOR)
        info_text.move_to(info_box.get_center())
        info_card = VGroup(info_box, info_text)
        info_card.box, info_card.text = info_box, info_text

        loop_items = {}
        for name, y in zip(LOOP_STEPS, LOOP_YS):
            t = Tex(name, font_size=24, color=SECONDARY_COLOR)
            t.move_to([4.0 + t.width / 2, y, 0])
            loop_items[name] = t
        loop_group = VGroup(*loop_items.values())

        return dict(tag=tag, divider=divider, best_label=best_label, best_value=best_value,
                    info_card=info_card, loop_items=loop_items, loop_group=loop_group)

    def set_info(self, info_card, lines, font=22):
        new_text = Tex("\\\\".join(lines), font_size=font, color=TEXT_COLOR)
        if new_text.width > 2.4:
            new_text.scale_to_fit_width(2.4)
        new_text.move_to(info_card.box.get_center())
        return Transform(info_card.text, new_text)

    def set_active_step(self, loop_items, name):
        anims = []
        for step_name, mobj in loop_items.items():
            if step_name == name:
                anims.append(mobj.animate.set_color(TEXT_COLOR))
            else:
                anims.append(mobj.animate.set_color(SECONDARY_COLOR))
        return anims

    # ===================================================== Beat 10.1 =====
    def beat_10_1_root(self):
        sb = self.build_scoreboard()
        self.play(FadeIn(sb["tag"]))
        self.play(
            Create(sb["divider"]), FadeIn(sb["best_label"]), FadeIn(sb["best_value"]),
            FadeIn(sb["info_card"]), FadeIn(sb["loop_group"]),
        )

        root = self.open_node()
        root.move_to([-2.0, 2.3, 0])
        self.play(FadeIn(root))

        root_with_lb = self.set_node_lb(root, ROOT_LB)
        self.play(root_with_lb)
        self.play(Flash(root.label, color=LB_COLOR))

        self.play(self.set_info(sb["info_card"], ["Relaxed answer", "some switches are", "not yet 0 or 1"]))

        cap = self.swap_caption("We start from the relaxed answer: the floor is 746.7.")
        self.wait(1.2)

        self.layout_items = [
            sb["tag"], sb["best_label"], sb["best_value"], sb["info_card"],
            *sb["loop_group"], root, cap,
        ]
        self.background_items = [sb["divider"]]
        self.allowed_overlaps = set()
        self.check_layout("10_1")

        self._sb = sb
        self._root = root

    # ===================================================== Beat 10.2 =====
    def beat_10_2_branch(self):
        sb = self._sb
        self.play(*self.set_active_step(sb["loop_items"], "Branch"))
        self.play(self.set_info(sb["info_card"], ["Undecided switch:", r"Row 4 $\to$ Group 2,", "pair AD?"]))

        cap = self.swap_caption("Branch: pick one undecided switch, and try both ways.")
        self.wait(1.0)

        left_child = self.open_node()
        left_child.move_to([-4.2, 0.9, 0])
        right_child = self.open_node()
        right_child.move_to([0.2, 0.9, 0])

        edge_left = self.edge(self._root.get_bottom(), left_child.get_top(), "= 1", LEFT)
        edge_right = self.edge(self._root.get_bottom(), right_child.get_top(), "= 0", RIGHT)

        self.play(Create(edge_left), Create(edge_right), run_time=0.8)
        self.play(FadeIn(edge_left[1]) if isinstance(edge_left, VGroup) else FadeIn(edge_left),
                   FadeIn(edge_right[1]) if isinstance(edge_right, VGroup) else FadeIn(edge_right))
        self.play(FadeIn(left_child), FadeIn(right_child))

        self.play(*self.set_active_step(sb["loop_items"], "Solve"))
        cap2 = self.swap_caption("Solve the relaxed problem on each side.")

        self.play(self.set_node_lb(right_child, BRANCH_ROW4_LB_0), run_time=0.6)
        self.play(self.set_info(sb["info_card"], ["Undecided switch:", r"off $\to$ 746.7"]))

        self.play(self.set_node_lb(left_child, BRANCH_ROW4_LB_1), run_time=0.6)
        up_arrow = Tex("$\\blacktriangle$", font_size=22, color=LB_COLOR)
        up_arrow.next_to(left_child, RIGHT, buff=0.1)
        self.play(FadeIn(up_arrow))
        self.play(self.set_info(sb["info_card"], [r"on $\to$ 1,037.5"]))

        cap3 = self.swap_caption("Forcing this choice pushes that side's floor up to 1,037.5.")
        self.wait(1.2)
        cap4 = self.swap_caption("The other side keeps the floor at 746.7, so we look there first.")
        self.wait(1.2)

        self.layout_items = [
            sb["tag"], sb["best_label"], sb["best_value"], sb["info_card"],
            *sb["loop_group"], self._root, left_child, right_child, up_arrow, cap4,
        ]
        self.background_items = [sb["divider"], edge_left, edge_right]
        self.allowed_overlaps = set()
        self.check_layout("10_2")

        self._left_child = left_child
        self._right_child = right_child
        self._edge_left = edge_left
        self._edge_right = edge_right
        self._up_arrow = up_arrow

    # ===================================================== Beat 10.3 =====
    def beat_10_3_real_answers(self):
        sb = self._sb
        for _ in range(2):
            self.play(*self.set_active_step(sb["loop_items"], "Branch"), run_time=0.4)
            self.play(*self.set_active_step(sb["loop_items"], "Solve"), run_time=0.4)

        gen_a = self.generic_node()
        gen_a.move_to([-0.9, -0.4, 0])
        gen_b = self.generic_node()
        gen_b.move_to([1.3, -0.4, 0])
        edge_a = self.edge(self._right_child.get_bottom(), gen_a.get_top())
        edge_b = self.edge(self._right_child.get_bottom(), gen_b.get_top())
        self.play(Create(edge_a), Create(edge_b), FadeIn(gen_a), FadeIn(gen_b))

        self.play(self.set_info(sb["info_card"], ["Every switch is 0 or 1:", "a real answer.", "Keep the best one."]))

        leaf_xs_a = [-1.8, -0.8, 0.2]
        leaf_xs_b = [1.2, 2.2]
        leaf_positions = [(x, gen_a) for x in leaf_xs_a] + [(x, gen_b) for x in leaf_xs_b]

        leaves = []
        leaf_edges = []
        cap = self.swap_caption("Go deeper until every switch is 0 or 1 --- that is a real answer.")
        self.wait(0.6)
        cap2 = self.swap_caption("Each time we find a better one, BEST goes down.")

        for (x, parent), value in zip(leaf_positions, BEST_SEQUENCE):
            lf = self.leaf()
            lf.move_to([x, -1.8, 0])
            e = self.edge(parent.get_bottom(), lf.get_top())
            self.play(Create(e), run_time=0.3)
            self.play(FadeIn(lf), run_time=0.3)
            leaves.append(lf)
            leaf_edges.append(e)

            new_val = Tex(f"{value:,}", font_size=40, color=HL_COLOR)
            new_val.move_to(sb["best_value"].get_center())
            self.play(Transform(sb["best_value"], new_val), Flash(sb["best_value"], color=HL_COLOR),
                       run_time=0.8)

        self.wait(0.3)
        self.play(Indicate(sb["best_value"], color=HL_COLOR))

        self.layout_items = [
            sb["tag"], sb["best_label"], sb["best_value"], sb["info_card"], *sb["loop_group"],
            self._root, self._left_child, self._right_child, self._up_arrow,
            gen_a, gen_b, *leaves, cap2,
        ]
        self.background_items = [
            sb["divider"], self._edge_left, self._edge_right, edge_a, edge_b, *leaf_edges,
        ]
        self.allowed_overlaps = set()
        self.check_layout("10_3")

        self._gen_a = gen_a
        self._gen_b = gen_b
        self._edge_a = edge_a
        self._edge_b = edge_b
        self._leaves = leaves
        self._leaf_edges = leaf_edges

    # ===================================================== Beat 10.4 =====
    def beat_10_4_bound_prune(self):
        sb = self._sb
        right_subtree = VGroup(
            self._right_child, self._gen_a, self._gen_b, *self._leaves,
        )
        right_edges = VGroup(self._edge_right, self._edge_a, self._edge_b, *self._leaf_edges)
        self.play(right_subtree.animate.set_opacity(0.5), right_edges.animate.set_opacity(0.5))

        outline = SurroundingRectangle(self._left_child, color=TEXT_COLOR, buff=0.05)
        self.play(Create(outline), self._left_child.animate.scale(1.15))

        self.play(*self.set_active_step(sb["loop_items"], "Bound"))

        info_lines_1 = MathTex(r"\text{This side: LB }", "1037.5", font_size=22)
        info_lines_1.set_color(TEXT_COLOR)
        info_lines_1.set_color_by_tex("1037.5", LB_COLOR)
        info_lines_2 = MathTex(r"\text{BEST: }", "990", font_size=22)
        info_lines_2.set_color(TEXT_COLOR)
        info_lines_2.set_color_by_tex("990", HL_COLOR)
        info_lines_3 = MathTex("1037.5", r"\ge", "990", font_size=22)
        info_lines_3.set_color(TEXT_COLOR)
        info_block = VGroup(info_lines_1, info_lines_2, info_lines_3).arrange(DOWN, buff=0.12)
        if info_block.width > 2.4:
            info_block.scale_to_fit_width(2.4)
        info_block.move_to(sb["info_card"].box.get_center())
        self.play(Transform(sb["info_card"].text, info_block))

        cap = self.swap_caption("Bound: the floor tells us the best this side could ever do.")
        self.wait(1.5)

        ghost_a = self.generic_node()
        ghost_a.move_to([-5.2, -0.4, 0])
        ghost_b = self.generic_node()
        ghost_b.move_to([-3.2, -0.4, 0])
        ghost_leaves = VGroup(*[
            self.generic_node(r=0.15).move_to([x, -1.8, 0])
            for x in [-5.7, -4.7, -3.7, -2.7]
        ])
        ghost_edge_a = self.edge(self._left_child.get_bottom(), ghost_a.get_top())
        ghost_edge_b = self.edge(self._left_child.get_bottom(), ghost_b.get_top())
        ghost_leaf_edges = VGroup(
            self.edge(ghost_a.get_bottom(), ghost_leaves[0].get_top()),
            self.edge(ghost_a.get_bottom(), ghost_leaves[1].get_top()),
            self.edge(ghost_b.get_bottom(), ghost_leaves[2].get_top()),
            self.edge(ghost_b.get_bottom(), ghost_leaves[3].get_top()),
        )
        ghost_group = VGroup(ghost_a, ghost_b, ghost_leaves, ghost_edge_a, ghost_edge_b, ghost_leaf_edges)
        ghost_group.set_opacity(0.2)
        self.play(FadeIn(ghost_group))

        cap2 = self.swap_caption("Its best possible answer is 1,037.5...")
        self.wait(0.6)
        cap3 = self.swap_caption("...already worse than 990.")
        self.wait(1.0)

        self.play(*self.set_active_step(sb["loop_items"], "Prune"))

        cross = VGroup(
            Line(self._left_child.get_corner(UL), self._left_child.get_corner(DR),
                 color=FAIL_COLOR, stroke_width=4),
            Line(self._left_child.get_corner(DL), self._left_child.get_corner(UR),
                 color=FAIL_COLOR, stroke_width=4),
        )
        pruned_label = Tex("pruned", font_size=24, color=FAIL_COLOR)
        pruned_label.move_to([-5.35 - pruned_label.width / 2, 0.9, 0])

        self.play(
            Create(cross),
            self._edge_left.animate.set_color(FAIL_COLOR),
            self._left_child.animate.set_color(FAIL_COLOR),
            ghost_group.animate.set_color(FAIL_COLOR),
            FadeIn(pruned_label),
        )

        skip_line = Tex(r"$\to$ skip this whole side", font_size=22, color=TEXT_COLOR)
        if skip_line.width > 2.4:
            skip_line.scale_to_fit_width(2.4)
        skip_line.move_to(sb["info_card"].box.get_center())
        self.play(Transform(sb["info_card"].text, skip_line))

        cap4 = self.swap_caption("So we skip this whole side without looking inside. That is pruning.")
        self.wait(2.0)

        self.play(right_subtree.animate.set_opacity(1.0), right_edges.animate.set_opacity(1.0))
        self.play(FadeOut(outline))

        self.layout_items = [
            sb["tag"], sb["best_label"], sb["best_value"], sb["info_card"], *sb["loop_group"],
            self._root, self._left_child, self._right_child, self._up_arrow,
            self._gen_a, self._gen_b, *self._leaves, pruned_label, cross, cap4,
        ]
        self.background_items = [
            sb["divider"], self._edge_left, self._edge_right, self._edge_a, self._edge_b,
            *self._leaf_edges, ghost_group,
        ]
        idx_left_child = self.layout_items.index(self._left_child)
        idx_cross = self.layout_items.index(cross)
        idx_up_arrow = self.layout_items.index(self._up_arrow)
        self.allowed_overlaps = {
            (idx_left_child, idx_cross), (idx_left_child, idx_up_arrow), (idx_up_arrow, idx_cross),
        }
        self.check_layout("10_4")

        self._pruned_label = pruned_label
        self._cross = cross
        self._ghost_group = ghost_group

    # ===================================================== Beat 10.5 =====
    def beat_10_5_repeat(self):
        sb = self._sb
        old_tree = VGroup(
            self._root, self._left_child, self._right_child, self._up_arrow,
            self._gen_a, self._gen_b, *self._leaves, self._pruned_label, self._cross,
            self._edge_left, self._edge_right, self._edge_a, self._edge_b,
            *self._leaf_edges, self._ghost_group,
        )
        self.play(FadeOut(old_tree))
        self.play(FadeOut(self.current_caption))
        self.current_caption = None

        self.play(self.set_info(sb["info_card"], ["Repeat:", "branch, solve,", "bound, prune"]))

        random.seed(42)
        depth = 6
        root_pos = [-1.6, 2.5, 0]
        leaf_y = -2.3
        n_leaves = 2 ** (depth - 1)
        leaf_xs = [(-6.2 + i * (9.2 / (n_leaves - 1))) for i in range(n_leaves)]

        levels = [[root_pos]]
        for d in range(1, depth):
            y = 2.5 - d * (2.5 - leaf_y) / (depth - 1)
            n = 2 ** d
            prev = levels[-1]
            new_level = []
            for i in range(n):
                if n == n_leaves:
                    x = leaf_xs[i]
                else:
                    x = -6.2 + i * (9.2 / (n - 1)) if n > 1 else -1.6
                new_level.append([x, y, 0])
            levels.append(new_level)

        all_circles = VGroup()
        all_edges = VGroup()
        level_groups = []
        for d, level in enumerate(levels):
            circ_group = VGroup(*[
                Circle(radius=0.05, stroke_color=SECONDARY_COLOR, stroke_width=1,
                       stroke_opacity=0.6).move_to(pos)
                for pos in level
            ])
            level_groups.append(circ_group)
            all_circles.add(circ_group)

        edge_groups = []
        for d in range(1, depth):
            parents = levels[d - 1]
            children = levels[d]
            eg = VGroup()
            for pi, parent in enumerate(parents):
                for ci in (2 * pi, 2 * pi + 1):
                    if ci < len(children):
                        eg.add(Line(parent, children[ci], stroke_color=SECONDARY_COLOR,
                                     stroke_width=1, stroke_opacity=0.6))
            edge_groups.append(eg)
            all_edges.add(eg)

        self.play(FadeIn(level_groups[0]))
        for d in range(1, depth):
            self.play(Create(edge_groups[d - 1]), FadeIn(level_groups[d]), run_time=0.25)

        for name in (LOOP_STEPS * 3):
            self.play(*self.set_active_step(sb["loop_items"], name), run_time=0.2)

        cap = self.swap_caption("The solver repeats these four steps again and again.")

        winning_path_idx = 0
        for d in range(1, depth):
            winning_path_idx = winning_path_idx * 2

        for wave in range(3):
            fade_targets = VGroup()
            for d, circ_group in enumerate(level_groups):
                for i, c in enumerate(circ_group):
                    keep = (i == 0)
                    if not keep:
                        fade_targets.add(c)
            for eg in edge_groups:
                for i, e in enumerate(eg):
                    if i != 0:
                        fade_targets.add(e)
            self.play(fade_targets.animate.set_color(FAIL_COLOR).set_opacity(0.1), run_time=0.6)

        winning_leaf = level_groups[-1][0]
        final_leaf = self.leaf()
        final_leaf.move_to(winning_leaf.get_center())
        final_label = Tex("990", font_size=22, color=HL_COLOR)
        final_label.next_to(final_leaf, RIGHT, buff=0.15)
        self.play(FadeIn(final_leaf), FadeIn(final_label))

        cap2 = self.swap_caption("Most of the tree is never explored --- it is pruned away.")
        self.wait(1.5)

        self.background_items = [all_circles, all_edges]
        self.layout_items = [
            sb["tag"], sb["best_label"], sb["best_value"], sb["info_card"],
            final_leaf, final_label, cap2,
        ]
        self.allowed_overlaps = set()
        self.check_layout("10_5")

        self.play(
            FadeOut(all_circles), FadeOut(all_edges), FadeOut(sb["loop_group"]),
            FadeOut(final_leaf), FadeOut(final_label),
        )
        self._all_circles = all_circles
        self._all_edges = all_edges

    # ===================================================== Beat 10.6 =====
    def beat_10_6_work_saved(self):
        sb = self._sb
        self.play(FadeOut(self.current_caption))
        self.current_caption = None

        label1 = Tex("Trying every answer", font_size=26, color=TEXT_COLOR)
        label1.move_to([-5.8 + label1.width / 2, 1.3, 0])
        bar1 = Rectangle(width=7.0, height=0.3, fill_color=SECONDARY_COLOR, fill_opacity=1,
                          stroke_width=0)
        bar1.move_to([-5.8 + 7.0 / 2, 0.8, 0])
        val1 = Tex(f"{SEARCH_SPACE_DEMO:,}", font_size=26, color=TEXT_COLOR)
        val1.move_to([1.4 + val1.width / 2, 0.8, 0])

        label2 = Tex("Our simple search", font_size=26, color=TEXT_COLOR)
        label2.move_to([-5.8 + label2.width / 2, -0.3, 0])
        bar2_len = max(7.0 * LPS_SOLVED / SEARCH_SPACE_DEMO, 0.08)
        bar2 = Rectangle(width=bar2_len, height=0.3, fill_color=HL_COLOR, fill_opacity=1,
                          stroke_width=0)
        bar2.move_to([-5.8 + bar2_len / 2, -0.8, 0])
        val2 = Tex(f"{LPS_SOLVED:,} small problems", font_size=26, color=TEXT_COLOR)
        val2.move_to([-5.8 + bar2_len + 0.2 + val2.width / 2, -0.8, 0])

        self.play(FadeIn(label1), FadeIn(bar1), FadeIn(val1))
        self.play(FadeIn(label2), FadeIn(bar2), FadeIn(val2))

        cap = self.swap_caption("Our simple search solved 2,269 small problems...")
        self.wait(0.6)
        cap2 = self.swap_caption("...instead of checking 326,592 answers.")
        self.wait(1.0)

        self.layout_items = [
            sb["tag"], sb["best_label"], sb["best_value"], sb["info_card"],
            label1, val1, label2, val2, cap2,
        ]
        self.background_items = [bar1, bar2]
        self.allowed_overlaps = set()
        self.check_layout("10_6")

        cap3 = self.swap_caption("The best answer found is 990 kW. But is it truly the best?")
        self.wait(2.0)

        self.play(
            FadeOut(sb["tag"]), FadeOut(sb["best_label"]), FadeOut(sb["best_value"]),
            FadeOut(sb["info_card"]), FadeOut(sb["divider"]),
            FadeOut(label1), FadeOut(bar1), FadeOut(val1),
            FadeOut(label2), FadeOut(bar2), FadeOut(val2),
            FadeOut(cap3),
            run_time=1.0,
        )
        self.current_caption = None
