"""Scene 06 -- "Decisions become switches"

Built strictly from scene06_prompt.md + common_prompt.md.

Starts from: black (Scene 05 ended on "We need a smarter way to search."
then faded to black).

Ends with: fade to black after "Now every decision is a set of 0/1
switches."

Run with:
    manim -pqh scene06_variables.py Scene06Variables
"""
from manim import *

from common.style import (
    BG_COLOR, TEXT_COLOR, SECONDARY_COLOR, UPS_COLORS,
    HL_COLOR, GROUP1_COLOR, GROUP2_COLOR, PAIR_COLOR, FAIL_COLOR,
    ROW_FILL, ROW_STROKE, CUT_COLOR,
)
from common.layout import caption, title, LayoutCheckMixin
from common.data import SCENE06
from common.widgets import row_block, pair_chip, cut_line

ROW_YS_8 = [1.9 - 0.55 * k for k in range(8)]


def mini_row(name, width, height, x, y, font=22):
    rect = Rectangle(width=width, height=height, fill_color=ROW_FILL, fill_opacity=1,
                      stroke_color=ROW_STROKE, stroke_width=1.5)
    rect.move_to([x, y, 0])
    lbl = Tex(name, font_size=font, color=TEXT_COLOR)
    if lbl.width > width - 0.1:
        lbl.scale_to_fit_width(width - 0.1)
    lbl.move_to(rect.get_center())
    grp = VGroup(rect, lbl)
    grp.rect, grp.lbl = rect, lbl
    return grp


def value_box(value, x, y, colour, w=0.5, h=0.4, font=26):
    box = Rectangle(width=w, height=h, stroke_color=TEXT_COLOR, stroke_width=1)
    box.move_to([x, y, 0])
    txt = Tex(str(value), font_size=font, color=colour)
    txt.move_to(box.get_center())
    grp = VGroup(box, txt)
    grp.box, grp.txt = box, txt
    return grp


def switch_box(value, x, y, w=0.6, h=0.5, font=32):
    filled = value == 1
    color = PAIR_COLOR if filled else SECONDARY_COLOR
    box = Rectangle(width=w, height=h, stroke_color=TEXT_COLOR, stroke_width=1.5,
                     fill_color=PAIR_COLOR if filled else BG_COLOR,
                     fill_opacity=0.25 if filled else 0)
    box.move_to([x, y, 0])
    txt = Tex(str(value), font_size=font, color=color)
    txt.move_to(box.get_center())
    grp = VGroup(box, txt)
    grp.box, grp.txt = box, txt
    return grp


class Scene06Variables(LayoutCheckMixin, Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        self.current_caption = None

        self.beat_6_1_pair_switch()
        self.beat_6_2_one_pair()
        self.beat_6_3_staircase()
        self.beat_6_4_t_to_y()
        self.beat_6_5_more_groups()

    # --------------------------------------------------------- helpers ---
    def swap_caption(self, text):
        new_cap = caption(text)
        if self.current_caption is not None:
            self.play(FadeOut(self.current_caption))
        self.play(FadeIn(new_cap))
        self.current_caption = new_cap
        return new_cap

    # ===================================================== Beat 6.1 =====
    def beat_6_1_pair_switch(self):
        t = title("Decisions as switches")
        self.play(FadeIn(t, shift=DOWN * 0.15))
        cap = self.swap_caption("First, we write every decision as numbers.")
        self.wait(1.0)

        row = row_block("Row 1", 500, "2-source", width=4.4, height=0.6, font=26)
        row.move_to([-3.6, 1.6, 0])
        row_tag = Tex("in Group 1", font_size=24, color=GROUP1_COLOR)
        row_tag.move_to([-3.6, 0.95, 0])
        self.play(FadeIn(row), FadeIn(row_tag))

        pairs = SCENE06["pair_order"]
        chip_ys = [2.1, 1.48, 0.86, 0.24, -0.38, -1.0]
        chips = {}
        for pair, y in zip(pairs, chip_ys):
            chip = pair_chip(pair, font=24)
            chip.move_to([1.4, y, 0])
            chips[pair] = chip
        self.play(LaggedStart(*[FadeIn(chips[p]) for p in pairs], lag_ratio=0.15), run_time=1.2)

        boxes = {p: switch_box(0, 2.6, y) for p, y in zip(pairs, chip_ys)}
        self.play(*[FadeIn(b) for b in boxes.values()])

        col_label = Tex("Group 1 switches", font_size=22, color=SECONDARY_COLOR)
        col_label.move_to([2.0, 2.62, 0])
        self.play(FadeIn(col_label))

        new_ab = switch_box(1, 2.6, chip_ys[0])
        self.play(Transform(boxes["AB"], new_ab), run_time=0.5)

        cap2 = self.swap_caption("Each pair becomes a switch: 1 if chosen, 0 if not.")
        self.wait(1.0)

        off_ab = switch_box(0, 2.6, chip_ys[0])
        on_ac = switch_box(1, 2.6, chip_ys[1])
        self.play(Transform(boxes["AB"], off_ab), Transform(boxes["AC"], on_ac), run_time=0.5)
        self.wait(0.6)
        on_ab = switch_box(1, 2.6, chip_ys[0])
        off_ac = switch_box(0, 2.6, chip_ys[1])
        self.play(Transform(boxes["AB"], on_ab), Transform(boxes["AC"], off_ac), run_time=0.5)

        q_eq = MathTex("q_{1,1,AB}", "=1", font_size=36)
        q_eq.set_color_by_tex("q_{1,1,AB}", PAIR_COLOR)
        q_eq.set_color_by_tex("=1", TEXT_COLOR)
        q_eq.move_to([4.9, 2.1, 0])
        self.play(FadeIn(q_eq))

        q_domain = MathTex("q_{i,g,p}", r"\in\{0,1\}", font_size=40)
        q_domain.set_color_by_tex("q_{i,g,p}", PAIR_COLOR)
        q_domain.set_color_by_tex(r"\in\{0,1\}", TEXT_COLOR)
        q_domain.move_to([4.9, 1.2, 0])
        line1 = Tex("row i, in group g,", font_size=22, color=TEXT_COLOR)
        line1.move_to([4.9, 0.55, 0])
        line2 = Tex("uses pair p", font_size=22, color=TEXT_COLOR)
        line2.move_to([4.9, 0.25, 0])
        self.play(FadeIn(q_domain))
        self.play(FadeIn(line1), FadeIn(line2))

        cap3 = self.swap_caption("q says which pair a row uses, inside a given group.")
        self.wait(1.5)

        self.layout_items = [
            t, row, row_tag, *chips.values(), *boxes.values(), col_label,
            q_eq, q_domain, line1, line2, cap3,
        ]
        self.allowed_overlaps = set()
        self.check_layout("6_1")

        self._row = row
        self._row_tag = row_tag
        self._chips = chips
        self._boxes = boxes
        self._col_label = col_label
        self._q_eq = q_eq
        self._q_domain = q_domain
        self._line1 = line1
        self._line2 = line2
        self._title = t
        self._chip_ys = chip_ys

    # ===================================================== Beat 6.2 =====
    def beat_6_2_one_pair(self):
        self.play(FadeOut(self._q_eq), FadeOut(self._line1), FadeOut(self._line2))

        new_domain = self._q_domain.copy()
        new_domain.scale(32 / 40).move_to([4.9, 2.1, 0])
        self.play(Transform(self._q_domain, new_domain), run_time=0.6)

        box_group = VGroup(*self._boxes.values())
        brace = Brace(box_group, direction=RIGHT)
        if brace.get_right()[0] >= 3.4:
            brace.scale_to_fit_width(3.4 - brace.get_left()[0] - 0.05)
        self.play(GrowFromCenter(brace))

        sum_eq = MathTex(r"\sum_p", "q_{i,g,p}", "=", "y_{i,g}", font_size=36)
        sum_eq.set_color_by_tex("q_{i,g,p}", PAIR_COLOR)
        sum_eq.set_color_by_tex("y_{i,g}", GROUP1_COLOR)
        sum_eq.move_to([4.9, 0.55, 0])
        self.play(FadeIn(sum_eq))

        line_a = MathTex("y_{i,g}", r"=1 \Rightarrow \text{one pair}", font_size=28)
        line_a.set_color_by_tex("y_{i,g}", GROUP1_COLOR)
        line_a.set_color_by_tex(r"=1 \Rightarrow \text{one pair}", TEXT_COLOR)
        if line_a.width > 3.0:
            line_a.scale_to_fit_width(3.0)
        line_a.move_to([4.9, -0.3, 0])

        line_b = MathTex("y_{i,g}", r"=0 \Rightarrow \text{no pair}", font_size=28)
        line_b.set_color_by_tex("y_{i,g}", GROUP1_COLOR)
        line_b.set_color_by_tex(r"=0 \Rightarrow \text{no pair}", TEXT_COLOR)
        if line_b.width > 3.0:
            line_b.scale_to_fit_width(3.0)
        line_b.move_to([4.9, -0.9, 0])
        self.play(FadeIn(line_a), FadeIn(line_b))

        cap = self.swap_caption("A row uses exactly one pair --- inside the group it belongs to.")
        self.wait(1.2)

        new_tag = Tex("in Group 2", font_size=24, color=GROUP2_COLOR)
        new_tag.move_to(self._row_tag.get_center())
        off_boxes = {p: switch_box(0, 2.6, y) for p, y in zip(self._boxes.keys(), self._chip_ys)}
        self.play(
            Transform(self._row_tag, new_tag),
            *[Transform(self._boxes[p], off_boxes[p]) for p in self._boxes],
        )
        self.play(Indicate(line_b))

        cap2 = self.swap_caption("In any other group, all of its switches stay off.")
        self.wait(1.2)

        restore_tag = Tex("in Group 1", font_size=24, color=GROUP1_COLOR)
        restore_tag.move_to(self._row_tag.get_center())
        on_ab = switch_box(1, 2.6, self._chip_ys[0])
        self.play(Transform(self._row_tag, restore_tag), Transform(self._boxes["AB"], on_ab))

        note = Tex("4-source rows have no pair switches", font_size=22, color=SECONDARY_COLOR)
        note.move_to([-3.6, -0.4, 0])
        self.play(FadeIn(note))

        cap3 = self.swap_caption("4-source rows use all four UPS, so they need no pair switches.")
        self.wait(1.2)

        self.layout_items = [
            self._title, self._row, self._row_tag, *self._chips.values(),
            *self._boxes.values(), self._col_label, self._q_domain, brace,
            sum_eq, line_a, line_b, note, cap3,
        ]
        idx_brace = self.layout_items.index(brace)
        allowed = set()
        for b in self._boxes.values():
            allowed.add((self.layout_items.index(b), idx_brace))
        self.allowed_overlaps = allowed
        self.check_layout("6_2")

        self.play(
            FadeOut(VGroup(
                self._row, self._row_tag, *self._chips.values(), *self._boxes.values(),
                self._col_label, self._q_domain, brace, sum_eq, line_a, line_b, note,
                cap3,
            )),
        )
        self.current_caption = None

        new_title = title("The cut as switches")
        self.play(Transform(self._title, new_title), run_time=0.6)

    # ===================================================== Beat 6.3 =====
    def beat_6_3_staircase(self):
        names = [f"Row {i+1}" for i in range(8)]
        rows = [mini_row(names[i], 1.6, 0.4, -4.6, ROW_YS_8[i], font=22) for i in range(8)]
        self.play(LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.1), run_time=1.2)

        cut_y = (ROW_YS_8[4] + ROW_YS_8[5]) / 2
        line = cut_line(length=1.9)
        line.move_to([-4.6, cut_y, 0])
        self.play(Create(line))

        header_t1 = MathTex("t_{i,1}", font_size=30, color=GROUP1_COLOR)
        header_t1.move_to([-2.9, 2.45, 0])
        self.play(FadeIn(header_t1))

        t1_vals = SCENE06["t1_two_groups"]
        t_boxes = [value_box(t1_vals[i], -2.9, ROW_YS_8[i], GROUP1_COLOR) for i in range(8)]
        for b in t_boxes:
            self.play(FadeIn(b), run_time=0.15)

        staircase = VMobject(color=GROUP1_COLOR, stroke_width=3)
        staircase.set_points_as_corners([[-2.6, 2.15, 0], [-2.6, cut_y, 0], [-3.2, cut_y, 0]])
        self.play(Create(staircase))

        line1 = MathTex("t_{i,1}", "= 1", font_size=28)
        line1.set_color(TEXT_COLOR)
        line1.set_color_by_tex("t_{i,1}", GROUP1_COLOR)
        line1b = Tex(": row i is in Group 1", font_size=28, color=TEXT_COLOR)
        row_a = VGroup(line1, line1b).arrange(RIGHT, buff=0.15)
        row_a.move_to([-1.2 + row_a.width / 2, 1.6, 0])

        line2 = MathTex("t_{i,1}", "= 0", font_size=28)
        line2.set_color(TEXT_COLOR)
        line2.set_color_by_tex("t_{i,1}", GROUP1_COLOR)
        line2b = Tex(": row i is in a later group", font_size=28, color=TEXT_COLOR)
        row_b = VGroup(line2, line2b).arrange(RIGHT, buff=0.15)
        row_b.move_to([-1.2 + row_b.width / 2, 1.0, 0])

        self.play(FadeIn(row_a), FadeIn(row_b))

        cap = self.swap_caption("The cut becomes switches too: t = 1 means the row is in Group 1.")
        self.wait(1.2)

        rule = MathTex("t_{i,1}", r"\ge", "t_{i+1,1}", font_size=36)
        rule.set_color_by_tex("t_{i,1}", GROUP1_COLOR)
        rule.set_color_by_tex("t_{i+1,1}", GROUP1_COLOR)
        rule.move_to([-1.2 + rule.width / 2, 0.0, 0])
        rule_note = Tex("once we pass the cut, we never go back", font_size=26, color=SECONDARY_COLOR)
        rule_note.move_to([-1.2 + rule_note.width / 2, -0.6, 0])
        self.play(FadeIn(rule))
        self.play(FadeIn(rule_note))

        cap2 = self.swap_caption("t can only step down once, so every group is a continuous run.")
        self.wait(1.2)

        broken_box = value_box(1, -2.9, ROW_YS_8[6], FAIL_COLOR)
        cross = VGroup(
            Line([-2.35 - 0.12, ROW_YS_8[6] + 0.12, 0], [-2.35 + 0.12, ROW_YS_8[6] - 0.12, 0],
                 color=FAIL_COLOR, stroke_width=4),
            Line([-2.35 - 0.12, ROW_YS_8[6] - 0.12, 0], [-2.35 + 0.12, ROW_YS_8[6] + 0.12, 0],
                 color=FAIL_COLOR, stroke_width=4),
        )
        broken_text = Tex("Row 7 would jump back to Group 1", font_size=24, color=FAIL_COLOR)
        broken_text.move_to([-1.2 + broken_text.width / 2, -1.5, 0])
        self.play(Transform(t_boxes[6], broken_box), FadeIn(cross), FadeIn(broken_text))

        cap3 = self.swap_caption("Switching Row 7 back on would break the rule.")
        self.wait(1.5)

        self.layout_items = [
            *rows, header_t1, *t_boxes, row_a, row_b, rule, rule_note, cross, broken_text, cap3,
        ]
        idx_staircase_related = []
        self.background_items = [staircase, line]
        self.allowed_overlaps = set()
        self.check_layout("6_3")

        restore_box = value_box(0, -2.9, ROW_YS_8[6], GROUP1_COLOR)
        self.play(Transform(t_boxes[6], restore_box), FadeOut(cross), FadeOut(broken_text))

        self._mini_rows = rows
        self._cut_line = line
        self._header_t1 = header_t1
        self._t_boxes = t_boxes
        self._staircase = staircase
        self._row_a = row_a
        self._row_b = row_b
        self._rule = rule
        self._rule_note = rule_note

    # ===================================================== Beat 6.4 =====
    def beat_6_4_t_to_y(self):
        self.play(
            FadeOut(self._row_a), FadeOut(self._row_b), FadeOut(self._rule), FadeOut(self._rule_note),
        )
        self.play(FadeOut(self.current_caption))
        self.current_caption = None

        header_y1 = MathTex("y_{i,1}", font_size=30, color=GROUP1_COLOR)
        header_y1.move_to([-1.9, 2.45, 0])
        header_y2 = MathTex("y_{i,2}", font_size=30, color=GROUP2_COLOR)
        header_y2.move_to([-0.9, 2.45, 0])
        self.play(FadeIn(header_y1), FadeIn(header_y2))

        y1_vals = SCENE06["y1_two_groups"]
        y2_vals = SCENE06["y2_two_groups"]
        y1_boxes = []
        y2_boxes = []
        for i in range(8):
            b1 = value_box(y1_vals[i], -1.9, ROW_YS_8[i], GROUP1_COLOR)
            b2 = value_box(y2_vals[i], -0.9, ROW_YS_8[i], GROUP2_COLOR)
            self.play(FadeIn(b1), FadeIn(b2), run_time=0.15)
            y1_boxes.append(b1)
            y2_boxes.append(b2)

        f1 = MathTex("y_{i,1}", "=", "t_{i,1}", font_size=36)
        f1.set_color_by_tex("y_{i,1}", GROUP1_COLOR)
        f1.set_color_by_tex("t_{i,1}", GROUP1_COLOR)
        f1.move_to([2.6, 1.2, 0])
        f2 = MathTex("y_{i,2}", "=1-", "t_{i,1}", font_size=36)
        f2.set_color_by_tex("y_{i,2}", GROUP2_COLOR)
        f2.set_color_by_tex("t_{i,1}", GROUP1_COLOR)
        f2.move_to([2.6, 0.4, 0])
        self.play(FadeIn(f1), FadeIn(f2))

        cap = self.swap_caption("Which group a row is in, y, comes straight from t.")
        self.wait(1.5)

        self.background_items = [self._staircase, self._cut_line]
        self.layout_items = [
            *self._mini_rows, self._header_t1, *self._t_boxes,
            header_y1, header_y2, *y1_boxes, *y2_boxes, f1, f2, cap,
        ]
        self.allowed_overlaps = set()
        self.check_layout("6_4")

        self.play(
            FadeOut(VGroup(
                *self._mini_rows, self._staircase, self._cut_line, self._header_t1, *self._t_boxes,
                header_y1, header_y2, *y1_boxes, *y2_boxes, f1, f2, cap,
            )),
        )
        self.current_caption = None

        new_title = title("With more groups")
        self.play(Transform(self._title, new_title), run_time=0.6)

    # ===================================================== Beat 6.5 =====
    def beat_6_5_more_groups(self):
        names = [f"Row {i+1}" for i in range(8)]
        rows = [mini_row(names[i], 1.4, 0.36, -4.8, ROW_YS_8[i], font=22) for i in range(8)]
        self.play(LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.1), run_time=1.0)

        cut_y1 = (ROW_YS_8[2] + ROW_YS_8[3]) / 2
        cut_y2 = (ROW_YS_8[5] + ROW_YS_8[6]) / 2
        line1 = cut_line(length=1.7)
        line1.move_to([-4.8, cut_y1, 0])
        line2 = cut_line(length=1.7)
        line2.move_to([-4.8, cut_y2, 0])
        self.play(Create(line1), Create(line2))

        header_t1 = MathTex("t_{i,1}", font_size=26, color=GROUP1_COLOR)
        header_t1.move_to([-3.3, 2.45, 0])
        header_t2 = MathTex("t_{i,2}", font_size=26, color=GROUP1_COLOR)
        header_t2.move_to([-2.4, 2.45, 0])
        header_y2 = MathTex("y_{i,2}", font_size=26, color=GROUP2_COLOR)
        header_y2.move_to([-1.3, 2.45, 0])

        t1_vals = SCENE06["t1_three_groups"]
        t2_vals = SCENE06["t2_three_groups"]
        y2_vals = SCENE06["y2_three_groups"]

        self.play(FadeIn(header_t1))
        t1_boxes = [value_box(t1_vals[i], -3.3, ROW_YS_8[i], GROUP1_COLOR, w=0.5, h=0.36, font=24)
                    for i in range(8)]
        for b in t1_boxes:
            self.play(FadeIn(b), run_time=0.12)

        self.play(FadeIn(header_t2))
        t2_boxes = [value_box(t2_vals[i], -2.4, ROW_YS_8[i], GROUP1_COLOR, w=0.5, h=0.36, font=24)
                    for i in range(8)]
        for b in t2_boxes:
            self.play(FadeIn(b), run_time=0.12)

        cap = self.swap_caption("With more groups, each cut adds one column of switches.")
        self.wait(1.0)

        rule = MathTex("t_{i,g}", r"\le", "t_{i,g+1}", font_size=34)
        rule.set_color_by_tex("t_{i,g}", GROUP1_COLOR)
        rule.set_color_by_tex("t_{i,g+1}", GROUP1_COLOR)
        rule.move_to([3.0, 1.6, 0])
        rule_note = Tex("in Groups 1...g $\\Rightarrow$ also in Groups 1...g+1",
                         font_size=22, color=SECONDARY_COLOR)
        if rule_note.width > 4.0:
            rule_note.scale_to_fit_width(4.0)
        rule_note.move_to([3.0, 1.05, 0])
        self.play(FadeIn(rule), FadeIn(rule_note))

        self.play(FadeIn(header_y2))
        y2_boxes = []
        for i in range(8):
            self.play(Indicate(t1_boxes[i]), Indicate(t2_boxes[i]), run_time=0.15)
            b = value_box(y2_vals[i], -1.3, ROW_YS_8[i], GROUP2_COLOR, w=0.5, h=0.36, font=24)
            if y2_vals[i] == 1:
                outline = SurroundingRectangle(b, color=SECONDARY_COLOR, buff=0.02, stroke_width=1.5)
                b = VGroup(b, outline)
            self.play(FadeIn(b), run_time=0.1)
            y2_boxes.append(b)

        f = MathTex("y_{i,g}", "=", "t_{i,g}", "-", "t_{i,g-1}", font_size=36)
        f.set_color_by_tex("y_{i,g}", GROUP2_COLOR)
        f.set_color_by_tex("t_{i,g}", GROUP1_COLOR)
        f.set_color_by_tex("t_{i,g-1}", GROUP1_COLOR)
        f.move_to([3.0, 0.0, 0])
        f_note = MathTex(r"\text{with } t_{i,0} = 0,\ t_{i,G} = 1", font_size=24, color=SECONDARY_COLOR)
        f_note.move_to([3.0, -0.6, 0])
        self.play(FadeIn(f))
        self.play(FadeIn(f_note))

        cap2 = self.swap_caption("Subtracting two columns tells us who is in each group.")
        self.wait(1.5)

        self.background_items = [line1, line2]
        self.layout_items = [
            *rows, header_t1, header_t2, header_y2, *t1_boxes, *t2_boxes, *y2_boxes,
            rule, rule_note, f, f_note, cap2,
        ]
        self.allowed_overlaps = set()
        self.check_layout("6_5")

        cap3 = self.swap_caption("Now every decision is a set of 0/1 switches.")
        self.wait(2.0)

        self.play(
            FadeOut(self._title),
            FadeOut(VGroup(*rows, line1, line2, header_t1, header_t2, header_y2,
                            *t1_boxes, *t2_boxes, *y2_boxes, rule, rule_note, f, f_note, cap3)),
            run_time=1.0,
        )
        self.current_caption = None
