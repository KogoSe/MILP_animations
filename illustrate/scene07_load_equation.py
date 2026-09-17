"""Scene 07 -- "The load equation"

Built strictly from scene07_prompt.md + common_prompt.md.

Starts from: black (Scene 06 ended on "Now every decision is a set of 0/1
switches." then faded to black).

Ends with: fade to black after "Next: write 'worst case' in the same
language."

Run with:
    manim -pqh scene07_load_equation.py Scene07LoadEquation
"""
from manim import *

from common.style import (
    BG_COLOR, TEXT_COLOR, SECONDARY_COLOR, UPS_COLORS,
    HL_COLOR, PAIR_COLOR, GROUP1_COLOR, FAIL_COLOR,
)
from common.layout import caption, title, LayoutCheckMixin
from common.data import SCENE07, fmt_kw
from common.widgets import ups_box, fail_anims, pair_chip

PAIR_ORDER = ["AB", "AC", "AD", "BC", "BD", "CD"]
BAR_X = -4.5
BASELINE_Y = -2.0
SCALE = 3.6 / 1400


class Scene07LoadEquation(LayoutCheckMixin, Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        self.current_caption = None

        self.beat_7_1_recall_bar()
        self.beat_7_2_pieces()
        self.beat_7_3_every_pair()
        self.beat_7_4_general_equation()
        self.beat_7_5_why_linear()

    # --------------------------------------------------------- helpers ---
    def swap_caption(self, text):
        new_cap = caption(text)
        if self.current_caption is not None:
            self.play(FadeOut(self.current_caption))
        self.play(FadeIn(new_cap))
        self.current_caption = new_cap
        return new_cap

    def switch_badge(self, target_mobj, colour):
        outline = SurroundingRectangle(target_mobj, color=colour, buff=0.06,
                                        corner_radius=0.06, stroke_width=1.5)
        one = Tex("1", font_size=16, color=colour)
        one.move_to(outline.get_corner(UR) + UP * 0.06 + RIGHT * 0.06)
        return VGroup(outline, one)

    # ===================================================== Beat 7.1 =====
    def beat_7_1_recall_bar(self):
        t = title("One load, written as a sum")
        self.play(FadeIn(t, shift=DOWN * 0.15))

        header_ups = ups_box("A", w=0.5, h=0.4, font=22, short=True)
        header_ups.move_to([-5.9, 2.4, 0])
        header_lbl = Tex("A fails $\\cdot$ Group 2 $\\cdot$ Solution A", font_size=24, color=TEXT_COLOR)
        header_lbl.move_to([-5.5 + header_lbl.width / 2, 2.4, 0])
        self.play(FadeIn(header_ups), FadeIn(header_lbl))
        self.play(*fail_anims(header_ups), run_time=0.5)

        baseline = Line([-5.3, BASELINE_Y, 0], [-3.7, BASELINE_Y, 0], color=SECONDARY_COLOR, stroke_width=2)
        letter_c = Tex("C", font_size=26, color=UPS_COLORS["C"])
        letter_c.move_to([BAR_X, -2.3, 0])
        self.play(Create(baseline), FadeIn(letter_c))

        pieces = SCENE07["pieces"][1:]  # Row 6, 7, 8 (Row 5 contributes 0, not drawn)
        segments = []
        seg_names = []
        heights = 0.0
        anims_all = []
        for p in pieces:
            bottom = BASELINE_Y + heights * SCALE
            seg_h = p["piece"] * SCALE
            seg = Rectangle(width=1.0, height=seg_h, fill_color=UPS_COLORS["C"], fill_opacity=1,
                             stroke_color=BG_COLOR, stroke_width=2)
            seg.move_to([BAR_X, bottom + seg_h / 2, 0])
            seg_val = Tex(fmt_kw(p["piece"]), font_size=22, color=BG_COLOR)
            seg_val.move_to(seg.get_center())
            seg_grp = VGroup(seg, seg_val)
            name_lbl = Tex(p["name"], font_size=22, color=SECONDARY_COLOR)
            name_lbl.move_to([-3.85 + name_lbl.width / 2, bottom + seg_h / 2, 0])
            segments.append(seg_grp)
            seg_names.append(name_lbl)
            self.play(GrowFromEdge(seg_grp, DOWN), FadeIn(name_lbl), run_time=0.5)
            heights += p["piece"]

        total = Tex(fmt_kw(SCENE07["total"]), font_size=28, color=HL_COLOR)
        bar_top = BASELINE_Y + heights * SCALE
        total.move_to([BAR_X, bar_top + 0.1 + total.height / 2, 0])
        self.play(FadeIn(total))

        cap = self.swap_caption("Remember UPS C when A fails, in Group 2.")
        self.wait(1.5)

        self.background_items = [baseline]
        self.layout_items = [
            header_ups, header_ups.cross, header_lbl, letter_c,
            *segments, *seg_names, total, cap,
        ]
        idx_ups = self.layout_items.index(header_ups)
        idx_cross = self.layout_items.index(header_ups.cross)
        allowed = {(idx_ups, idx_cross)}
        for a in range(len(segments)):
            for b in range(a + 1, len(segments)):
                allowed.add((self.layout_items.index(segments[a]), self.layout_items.index(segments[b])))
        self.allowed_overlaps = allowed
        self.check_layout("7_1")

        self._title = t
        self._header_ups = header_ups
        self._header_lbl = header_lbl
        self._baseline = baseline
        self._letter_c = letter_c
        self._segments = segments  # [row6, row7, row8]
        self._seg_names = seg_names
        self._total = total

    # ===================================================== Beat 7.2 =====
    def beat_7_2_pieces(self):
        pieces = SCENE07["pieces"]
        line_ys = [1.4, 0.6, -0.2, -1.0]
        lines = []
        badges = []

        # Row 5 (secondary, no badge)
        r5 = pieces[0]
        line1 = MathTex(r"\text{Row 5:}\ ", "0", r"\times 300 \times ", "q_{5,2,AB}", "=0",
                         font_size=30, color=SECONDARY_COLOR)
        line1.move_to([-1.4 + line1.width / 2, line_ys[0], 0])
        self.play(FadeIn(line1))
        lines.append(line1)

        cap = self.swap_caption("Row 5 adds nothing to C: its pair AB does not include C.")
        self.wait(1.2)

        cap2 = self.swap_caption("Each piece is: share x row kW x switch.")

        # Row 6
        r6 = pieces[1]
        line2 = MathTex(r"\text{Row 6:}\ ", r"\tfrac{1}{3}", r"\times 450 \times ", "y_{6,2}", "=150",
                         font_size=30, color=TEXT_COLOR)
        line2.set_color_by_tex("y_{6,2}", GROUP1_COLOR)
        line2.set_color_by_tex("=150", HL_COLOR)
        line2.move_to([-1.4 + line2.width / 2, line_ys[1], 0])
        outline6 = SurroundingRectangle(self._segments[0], color=TEXT_COLOR, buff=0.03)
        badge6 = self.switch_badge(line2[3], GROUP1_COLOR)
        self.play(FadeIn(line2), Create(outline6))
        self.play(FadeIn(badge6))
        lines.append(line2)
        badges.append(badge6)
        self.play(FadeOut(outline6))

        # Row 7
        r7 = pieces[2]
        line3 = MathTex(r"\text{Row 7:}\ ", r"\tfrac{1}{2}", r"\times 800 \times ", "q_{7,2,CD}", "=400",
                         font_size=30, color=TEXT_COLOR)
        line3.set_color_by_tex("q_{7,2,CD}", PAIR_COLOR)
        line3.set_color_by_tex("=400", HL_COLOR)
        line3.move_to([-1.4 + line3.width / 2, line_ys[2], 0])
        outline7 = SurroundingRectangle(self._segments[1], color=TEXT_COLOR, buff=0.03)
        badge7 = self.switch_badge(line3[3], PAIR_COLOR)
        self.play(FadeIn(line3), Create(outline7))
        self.play(FadeIn(badge7))
        lines.append(line3)
        badges.append(badge7)
        self.play(FadeOut(outline7))

        # Row 8
        r8 = pieces[3]
        line4 = MathTex(r"\text{Row 8:}\ ", "1", r"\times 800 \times ", "q_{8,2,AC}", "=800",
                         font_size=30, color=TEXT_COLOR)
        line4.set_color_by_tex("q_{8,2,AC}", PAIR_COLOR)
        line4.set_color_by_tex("=800", HL_COLOR)
        line4.move_to([-1.4 + line4.width / 2, line_ys[3], 0])
        outline8 = SurroundingRectangle(self._segments[2], color=TEXT_COLOR, buff=0.03)
        badge8 = self.switch_badge(line4[3], PAIR_COLOR)
        self.play(FadeIn(line4), Create(outline8))
        self.play(FadeIn(badge8))
        lines.append(line4)
        badges.append(badge8)
        self.play(FadeOut(outline8))

        sum_line = MathTex("=150+400+800=1350", font_size=30)
        sum_line.set_color(TEXT_COLOR)
        sum_line.set_color_by_tex("1350", HL_COLOR)
        sum_line.move_to([-1.4 + sum_line.width / 2, -1.9, 0])
        self.play(FadeIn(sum_line))
        self.play(Indicate(self._total, color=HL_COLOR))

        cap3 = self.swap_caption("For a 4-source row, the switch is y: is the row in this group?")
        self.wait(1.5)

        self.layout_items = [
            self._header_ups, self._header_ups.cross, self._header_lbl, self._letter_c,
            *self._segments, *self._seg_names, self._total,
            line1, line2, line3, line4, *badges, sum_line, cap3,
        ]
        idx_ups = self.layout_items.index(self._header_ups)
        idx_cross = self.layout_items.index(self._header_ups.cross)
        allowed = {(idx_ups, idx_cross)}
        for a in range(len(self._segments)):
            for b in range(a + 1, len(self._segments)):
                allowed.add((self.layout_items.index(self._segments[a]),
                             self.layout_items.index(self._segments[b])))
        idx_line2 = self.layout_items.index(line2)
        idx_line3 = self.layout_items.index(line3)
        idx_line4 = self.layout_items.index(line4)
        allowed.add((idx_line2, self.layout_items.index(badge6)))
        allowed.add((idx_line3, self.layout_items.index(badge7)))
        allowed.add((idx_line4, self.layout_items.index(badge8)))
        self.allowed_overlaps = allowed
        self.check_layout("7_2")

        self._lines = lines
        self._badges = badges
        self._sum_line = sum_line

    # ===================================================== Beat 7.3 =====
    def beat_7_3_every_pair(self):
        self.play(
            FadeOut(VGroup(
                *self._segments, self._header_ups, self._header_ups.cross, self._header_lbl,
                *self._seg_names, self._total, self._letter_c, self._baseline,
                self._lines[0], self._lines[1], self._lines[3], *self._badges, self._sum_line,
            )),
        )
        self.play(FadeOut(self.current_caption))
        self.current_caption = None

        row7 = SCENE07["pieces"][2]
        row7_line = MathTex(r"\text{Row 7:}\ ", r"\tfrac{1}{2}", r"\times 800 \times ", "q_{7,2,CD}", "=400",
                             font_size=30, color=TEXT_COLOR)
        row7_line.set_color_by_tex("q_{7,2,CD}", PAIR_COLOR)
        row7_line.set_color_by_tex("=400", HL_COLOR)
        row7_line.move_to([0, 2.3, 0])
        self.play(Transform(self._lines[2], row7_line), run_time=0.6)
        row7_line = self._lines[2]

        col_xs = {p: x for p, x in zip(PAIR_ORDER, [-1.0, 0.2, 1.4, 2.6, 3.8, 5.0])}

        row_labels = {
            "reason": Tex("reason", font_size=26, color=SECONDARY_COLOR),
            "pair": Tex("pair", font_size=26, color=SECONDARY_COLOR),
            "share": Tex("share c", font_size=26, color=SECONDARY_COLOR),
            "switch": Tex("switch q", font_size=26, color=SECONDARY_COLOR),
            "product": Tex(r"c $\times$ 800 $\times$ q", font_size=26, color=SECONDARY_COLOR),
        }
        row_ys = {"reason": 1.8, "pair": 1.2, "share": 0.4, "switch": -0.4, "product": -1.2}
        for key, lbl in row_labels.items():
            lbl.move_to([-1.8 - lbl.width / 2, row_ys[key], 0])
        self.play(*[FadeIn(l) for l in row_labels.values()])

        chips = {}
        for pair in PAIR_ORDER:
            chip = pair_chip(pair, font=24)
            chip.move_to([col_xs[pair], row_ys["pair"], 0])
            chips[pair] = chip
        self.play(LaggedStart(*[FadeIn(chips[p]) for p in PAIR_ORDER], lag_ratio=0.15), run_time=1.0)

        cap = self.swap_caption("Row 7 really has a term for every pair.")
        self.wait(1.0)

        reason_tags = {}
        share_cells = {}
        data = SCENE07["row7_pairs"]
        for pair in PAIR_ORDER:
            info = data[pair]
            tag = Tex(info["reason"], font_size=22, color=SECONDARY_COLOR)
            tag.move_to([col_xs[pair], row_ys["reason"], 0])
            reason_tags[pair] = tag
            share = MathTex(info["share_tex"], font_size=30, color=TEXT_COLOR)
            share.move_to([col_xs[pair], row_ys["share"], 0])
            share_cells[pair] = share
            self.play(FadeIn(tag), FadeIn(share), run_time=0.2)

        cap2 = self.swap_caption("The share comes from the rule card.")
        self.wait(1.0)
        cap3 = self.swap_caption(r"Partner: 1 $\cdot$ pair without A: 1/2 $\cdot$ no C: 0.")
        self.wait(1.2)

        switch_cells = {}
        for pair in PAIR_ORDER:
            info = data[pair]
            colour = PAIR_COLOR if info["switch"] == 1 else SECONDARY_COLOR
            sw = MathTex(str(info["switch"]), font_size=30, color=colour)
            sw.move_to([col_xs[pair], row_ys["switch"], 0])
            switch_cells[pair] = sw
            self.play(FadeIn(sw), run_time=0.12)

        product_cells = {}
        for pair in PAIR_ORDER:
            info = data[pair]
            colour = HL_COLOR if info["product"] > 0 else SECONDARY_COLOR
            pr = MathTex(str(info["product"]), font_size=30, color=colour)
            pr.move_to([col_xs[pair], row_ys["product"], 0])
            product_cells[pair] = pr
            self.play(FadeIn(pr), run_time=0.12)

        cd_group = VGroup(
            reason_tags["CD"], chips["CD"], share_cells["CD"], switch_cells["CD"], product_cells["CD"],
        )
        cd_outline = SurroundingRectangle(cd_group, color=PAIR_COLOR, buff=0.1, stroke_width=2)
        self.play(Create(cd_outline))

        cap4 = self.swap_caption("Only the switch that is on counts: 1/2 x 800 = 400.")
        self.wait(1.5)

        self.layout_items = [
            row7_line, *row_labels.values(), *chips.values(), *reason_tags.values(),
            *share_cells.values(), *switch_cells.values(), *product_cells.values(),
            cd_outline, cap4,
        ]
        idx_cd_outline = self.layout_items.index(cd_outline)
        allowed = set()
        for m in cd_group:
            allowed.add((self.layout_items.index(m), idx_cd_outline))
        self.allowed_overlaps = allowed
        self.check_layout("7_3")

        self.play(
            FadeOut(VGroup(
                row7_line, *row_labels.values(), *chips.values(), *reason_tags.values(),
                *share_cells.values(), *switch_cells.values(), *product_cells.values(),
                cd_outline,
            )),
            FadeOut(self.current_caption),
        )
        self.current_caption = None

    # ===================================================== Beat 7.4 =====
    def beat_7_4_general_equation(self):
        new_title = title("The load on any UPS")
        self.play(Transform(self._title, new_title), run_time=0.6)

        eq = MathTex(
            r"L_{g,f,u}", "=",
            r"\sum_{i \in \text{2-src}} \sum_p c_{p,f,u}\, kW_i\, ", "q_{i,g,p}",
            "+",
            r"\sum_{i \in \text{4-src}} \tfrac{kW_i}{3}\, ", "y_{i,g}",
            font_size=40,
        )
        eq.set_color(TEXT_COLOR)
        eq.set_color_by_tex("q_{i,g,p}", PAIR_COLOR)
        eq.set_color_by_tex("y_{i,g}", GROUP1_COLOR)

        if eq.width > 12.5:
            line1 = VGroup(eq[0], eq[1], eq[2], eq[3])
            line2 = VGroup(eq[4], eq[5], eq[6])
            line1.arrange(RIGHT, buff=0.15)
            line2.arrange(RIGHT, buff=0.15)
            line1.move_to([0, 1.5, 0])
            line1.align_to(ORIGIN, LEFT).shift(LEFT * line1.width / 2)
            line2.move_to([0, 0.5, 0])
            line2.align_to(line1, LEFT)
            eq = VGroup(line1, line2)
        else:
            eq.move_to([0, 1.2, 0])

        self.play(Write(eq), run_time=2.0)

        if isinstance(eq, VGroup) and len(eq.submobjects) == 2 and isinstance(eq[0], VGroup):
            two_src_part = VGroup(eq[0][2], eq[0][3])
            four_src_part = VGroup(eq[1][1], eq[1][2])
        else:
            two_src_part = VGroup(eq[2], eq[3])
            four_src_part = VGroup(eq[5], eq[6])

        box1 = SurroundingRectangle(two_src_part, color=PAIR_COLOR, buff=0.08,
                                     stroke_width=1.5, stroke_opacity=0.6)
        box2 = SurroundingRectangle(four_src_part, color=GROUP1_COLOR, buff=0.08,
                                     stroke_width=1.5, stroke_opacity=0.6)
        self.play(Create(box1), Create(box2))

        cap = self.swap_caption("Add this up over every row, and we have the load on any UPS.")
        self.wait(1.0)

        legend1 = Tex("g = group $\\cdot$ f = failed UPS $\\cdot$ u = UPS we look at",
                       font_size=26, color=TEXT_COLOR)
        legend1.move_to([0, -0.6, 0])
        legend2 = Tex(r"c = share from the rule card: 1, $\tfrac{1}{2}$ or 0",
                       font_size=26, color=TEXT_COLOR)
        legend2.move_to([0, -1.25, 0])
        self.play(FadeIn(legend1))
        self.play(FadeIn(legend2))

        cap2 = self.swap_caption("The same recipe works for any group, any failure, any UPS.")
        self.wait(1.2)

        example = MathTex(r"g = 2,\ f = A,\ u = C \;\Rightarrow\; L = ", "1350", font_size=30)
        example.set_color(TEXT_COLOR)
        example.set_color_by_tex("1350", HL_COLOR)
        example.move_to([0, -2.1, 0])
        self.play(FadeIn(example))
        l_part = eq[0][0] if isinstance(eq, VGroup) and isinstance(eq[0], VGroup) else eq[0]
        self.play(Indicate(l_part, color=HL_COLOR))

        cap3 = self.swap_caption("Put in our case, and it gives back 1,350 kW.")
        self.wait(1.5)

        self.layout_items = [self._title, eq, box1, box2, legend1, legend2, example, cap3]
        self.allowed_overlaps = {
            (self.layout_items.index(eq), self.layout_items.index(box1)),
            (self.layout_items.index(eq), self.layout_items.index(box2)),
        }
        self.check_layout("7_4")

        self._eq_group = VGroup(eq, box1, box2, legend1, legend2, example)

    # ===================================================== Beat 7.5 =====
    def beat_7_5_why_linear(self):
        self.play(FadeOut(self._eq_group), FadeOut(self.current_caption))
        self.current_caption = None

        new_title = title("Why this helps")
        self.play(Transform(self._title, new_title), run_time=0.6)

        formula = MathTex(r"\text{fixed number} \times \text{0/1 switch}", font_size=40, color=TEXT_COLOR)
        formula.move_to([0, 1.3, 0])
        arrow = Arrow([0, 0.85, 0], [0, 0.35, 0], stroke_width=3, color=TEXT_COLOR, buff=0)
        linear = Tex("linear", font_size=48, color=HL_COLOR)
        linear.move_to([0, -0.15, 0])

        self.play(FadeIn(formula))
        self.play(GrowArrow(arrow))
        self.play(FadeIn(linear))

        cap = self.swap_caption("Every piece is a fixed number times a switch, so every load is linear.")
        self.wait(1.5)

        count_line = MathTex(
            "2", r"\text{ groups} \times ", "4", r"\text{ failures} \times ", "3",
            r"\text{ surviving UPS} = ", "24", r"\text{ load equations}",
            font_size=30, color=TEXT_COLOR,
        )
        count_line.move_to([0, -1.4, 0])
        for part in count_line:
            self.play(FadeIn(part), run_time=0.3)

        cap2 = self.swap_caption("Our small hall needs 24 of these load equations.")
        self.wait(1.2)

        self.layout_items = [self._title, formula, linear, count_line, cap2]
        self.background_items = [arrow]
        self.allowed_overlaps = set()
        self.check_layout("7_5")

        cap3 = self.swap_caption("Next: write 'worst case' in the same language.")
        self.wait(1.5)

        self.play(
            FadeOut(self._title), FadeOut(formula), FadeOut(arrow), FadeOut(linear),
            FadeOut(count_line), FadeOut(cap3),
            run_time=1.0,
        )
        self.current_caption = None
