"""Scene 11 -- "Proof"

Built strictly from scene11_prompt.md + common_prompt.md.

Starts from: black (Scene 10 ended on "The best answer found is 990 kW.
But is it truly the best?" then faded to black).

Ends with: fade to black after "So what does this look like in the real
hall?"

Run with:
    manim -pqh scene11_proof.py Scene11Proof
"""
from manim import *

from common.style import (
    BG_COLOR, TEXT_COLOR, SECONDARY_COLOR, HL_COLOR, LB_COLOR, FAIL_COLOR, GROUP1_COLOR,
)
from common.layout import caption, title, LayoutCheckMixin
from common.data import SCENE11


def number_line_x(v):
    return -5.5 + (v - 700) * 11 / 700


class Scene11Proof(LayoutCheckMixin, Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        self.current_caption = None

        self.beat_11_1_floor_rises()
        self.beat_11_2_sandwich()
        self.beat_11_3_app_checks()

    # --------------------------------------------------------- helpers ---
    def swap_caption(self, text):
        new_cap = caption(text)
        if self.current_caption is not None:
            self.play(FadeOut(self.current_caption))
        self.play(FadeIn(new_cap))
        self.current_caption = new_cap
        return new_cap

    def dot_grid(self, n, size, colour=TEXT_COLOR, opacity=0.5, r=0.018):
        spacing = size / (n - 1)
        dots = VGroup()
        for i in range(n):
            for j in range(n):
                x = -size / 2 + i * spacing
                y = -size / 2 + j * spacing
                dots.add(Dot([x, y, 0], radius=r, color=colour, fill_opacity=opacity))
        return dots

    # ===================================================== Beat 11.1 =====
    def beat_11_1_floor_rises(self):
        t = title("Closing the gap")
        self.play(FadeIn(t, shift=DOWN * 0.15))

        num_line = Line([-5.5, 0, 0], [5.5, 0, 0], color=TEXT_COLOR, stroke_width=2)
        ticks = VGroup()
        tick_labels = VGroup()
        for v in range(700, 1401, 100):
            x = number_line_x(v)
            tick = Line([x, -0.1, 0], [x, 0.1, 0], color=TEXT_COLOR, stroke_width=2)
            lbl = Tex(str(v), font_size=22, color=SECONDARY_COLOR)
            lbl.move_to([x, -0.5, 0])
            ticks.add(tick)
            tick_labels.add(lbl)
        self.play(Create(num_line), Create(ticks), FadeIn(tick_labels), run_time=1.0)

        best = SCENE11["best"]
        best_x = number_line_x(best)
        best_marker = Triangle(color=HL_COLOR, fill_color=HL_COLOR, fill_opacity=1)
        best_marker.scale(0.1)
        best_marker.rotate(PI)
        best_marker.move_to([best_x, 0.25, 0])
        best_label = Tex(f"BEST {best}", font_size=26, color=HL_COLOR)
        best_label.move_to([best_x, 0.8, 0])
        self.play(FadeIn(best_marker), FadeIn(best_label))

        cap = self.swap_caption("We have a real answer: BEST = 990 kW.")
        self.wait(1.0)

        lb_tracker = ValueTracker(SCENE11["lb_start"])
        self._lb_show_value = True
        self._lb_show_text = "746.7"

        def make_lb_marker():
            x = number_line_x(lb_tracker.get_value())
            m = Triangle(color=LB_COLOR, fill_color=LB_COLOR, fill_opacity=1)
            m.scale(0.1)
            m.move_to([x, -0.18, 0])
            return m

        def make_lb_label():
            x = number_line_x(lb_tracker.get_value())
            text = f"LB {self._lb_show_text}" if self._lb_show_value else "LB"
            lbl = Tex(text, font_size=26, color=LB_COLOR)
            lbl.move_to([x, -1.0, 0])
            return lbl

        def make_gap_segment():
            x1 = number_line_x(lb_tracker.get_value())
            x2 = best_x
            if x2 <= x1:
                return Line([x1, 0, 0], [x1, 0, 0], stroke_width=8, color=LB_COLOR, stroke_opacity=0)
            return Line([x1, 0, 0], [x2, 0, 0], stroke_width=8, color=LB_COLOR, stroke_opacity=0.5)

        lb_marker = always_redraw(make_lb_marker)
        lb_label = always_redraw(make_lb_label)
        gap_segment = always_redraw(make_gap_segment)

        self.add(gap_segment)
        self.play(FadeIn(lb_marker), FadeIn(lb_label))

        gap_label = Tex(f"gap {SCENE11['gap_start_pct']:.1f}\\%", font_size=26, color=TEXT_COLOR)
        gap_mid_x = (number_line_x(SCENE11["lb_start"]) + best_x) / 2
        gap_label.move_to([gap_mid_x, 1.5, 0])
        self.play(FadeIn(gap_label))

        cap2 = self.swap_caption("But the floor is still 746.7, so something better might exist.")
        self.wait(1.2)

        token_label = Tex("open branches", font_size=22, color=SECONDARY_COLOR)
        token_label.move_to([-5.7 + token_label.width / 2, 2.45, 0])
        tokens = VGroup(*[
            Circle(radius=0.15, stroke_color=SECONDARY_COLOR, stroke_width=2,
                   fill_color=BG_COLOR, fill_opacity=0).move_to([x, 2.0, 0])
            for x in [-5.5 + 0.5 * i for i in range(12)]
        ])
        self.play(FadeIn(token_label))
        self.play(LaggedStart(*[FadeIn(tok) for tok in tokens], lag_ratio=0.08), run_time=1.2)

        rule1 = Tex("LB = lowest floor", font_size=26, color=TEXT_COLOR)
        rule1.move_to([1.0 + rule1.width / 2, 2.0, 0])
        rule2 = Tex("among open branches", font_size=26, color=TEXT_COLOR)
        rule2.move_to([1.0 + rule2.width / 2, 1.55, 0])
        self.play(FadeIn(rule1), FadeIn(rule2))

        cap3 = self.swap_caption("The floor of the whole search...")
        self.wait(0.6)
        cap3b = self.swap_caption("...is the lowest floor still open.")
        self.wait(1.2)

        # -- the closing: tokens vanish while LB rises to meet BEST --
        self.play(FadeOut(gap_label))
        self._lb_show_value = False

        token_anims = []
        for tok in tokens:
            flash = Flash(tok, color=FAIL_COLOR, flash_radius=0.25)
            token_anims.append(Succession(flash, FadeOut(tok)))

        cap4 = self.swap_caption("As open branches are closed, the floor rises.")
        self.play(
            LaggedStart(*token_anims, lag_ratio=0.3),
            lb_tracker.animate.set_value(best),
            run_time=4.2,
            rate_func=smooth,
        )

        self._lb_show_value = True
        self._lb_show_text = str(best)
        self.play(Flash(lb_marker, color=LB_COLOR), Flash(best_marker, color=HL_COLOR))

        gap_label_end = Tex(f"gap {SCENE11['gap_end_pct']}\\%", font_size=26, color=TEXT_COLOR)
        gap_label_end.move_to([best_x, 1.5, 0])
        self.play(FadeIn(gap_label_end))

        cap5 = self.swap_caption("The floor meets the best answer. The gap is zero.")
        self.wait(1.5)

        self.background_items = [num_line, ticks, gap_segment]
        self.layout_items = [
            t, tick_labels, best_marker, best_label, lb_marker, lb_label,
            gap_label_end, rule1, rule2, cap5,
        ]
        self.allowed_overlaps = set()
        self.check_layout("11_1")

        self.play(
            FadeOut(t), FadeOut(num_line), FadeOut(ticks), FadeOut(tick_labels),
            FadeOut(best_marker), FadeOut(best_label), FadeOut(lb_marker), FadeOut(lb_label),
            FadeOut(gap_segment), FadeOut(gap_label_end), FadeOut(token_label),
            FadeOut(rule1), FadeOut(rule2), FadeOut(cap5),
            run_time=1.0,
        )
        self.current_caption = None
        self._title = t

    # ===================================================== Beat 11.2 =====
    def beat_11_2_sandwich(self):
        t = Tex("Proven optimal", font_size=44, color=TEXT_COLOR)
        t.move_to([0, 3.15, 0])
        self.play(FadeIn(t))
        self._title = t

        best = SCENE11["best"]
        sandwich = MathTex(str(best), r"\le M^{*} \le", str(best), font_size=48)
        sandwich.set_color(TEXT_COLOR)
        left_990 = sandwich[0]
        right_990 = sandwich[2]
        left_990.set_color(LB_COLOR)
        right_990.set_color(HL_COLOR)
        sandwich.move_to([0, 1.2, 0])

        under_left = Tex("floor", font_size=22, color=LB_COLOR)
        under_left.next_to(left_990, DOWN, buff=0.15)
        under_right = Tex("best found", font_size=22, color=HL_COLOR)
        under_right.next_to(right_990, DOWN, buff=0.15)

        self.play(Write(sandwich))
        self.play(FadeIn(under_left), FadeIn(under_right))

        arrow_left = Arrow([-5.0, 1.2, 0], left_990.get_left() + LEFT * 0.2, stroke_width=3,
                            color=LB_COLOR, buff=0)
        arrow_right = Arrow([5.0, 1.2, 0], right_990.get_right() + RIGHT * 0.2, stroke_width=3,
                             color=HL_COLOR, buff=0)
        self.play(GrowArrow(arrow_left), GrowArrow(arrow_right), run_time=0.8)

        cap = self.swap_caption("The best answer cannot be below the floor, or above what we already found.")
        self.wait(1.5)

        equals_990 = MathTex(r"M^{*}", "=", str(best), font_size=48)
        equals_990.set_color(TEXT_COLOR)
        equals_990.set_color_by_tex(str(best), HL_COLOR)
        equals_990.move_to([0, 1.2, 0])
        self.play(
            Transform(sandwich, equals_990),
            FadeOut(under_left), FadeOut(under_right),
            FadeOut(arrow_left), FadeOut(arrow_right),
            run_time=1.0,
        )

        optimal_text = Tex("OPTIMAL", font_size=64, color=HL_COLOR)
        optimal_text.move_to([0, -0.1, 0])
        self.play(GrowFromCenter(optimal_text), run_time=0.6)

        cap2 = self.swap_caption("So 990 kW is the best possible --- proven, not guessed.")
        self.wait(1.5)

        status_line = Tex(f"App status: {SCENE11['app_status']}", font_size=26, color=TEXT_COLOR)
        status_line.move_to([0, -1.1, 0])
        note_line = Tex(
            "If the time limit is reached first, the app shows the remaining gap instead.",
            font_size=22, color=SECONDARY_COLOR,
        )
        if note_line.width > 12.0:
            note_line.scale_to_fit_width(12.0)
        note_line.move_to([0, -1.75, 0])
        self.play(FadeIn(status_line))
        self.play(FadeIn(note_line))

        cap3 = self.swap_caption("The app reports this as 'Optimal (proven)'.")
        self.wait(1.2)

        self.layout_items = [self._title, sandwich, optimal_text, status_line, note_line, cap3]
        self.allowed_overlaps = set()
        self.check_layout("11_2")

        self.play(
            FadeOut(self._title), FadeOut(sandwich), FadeOut(optimal_text),
            FadeOut(status_line), FadeOut(note_line), FadeOut(cap3),
            run_time=1.0,
        )
        self.current_caption = None

    # ===================================================== Beat 11.3 =====
    def beat_11_3_app_checks(self):
        t = title("Checked another way")
        self.play(FadeIn(t, shift=DOWN * 0.15))
        self._title = t

        cap = self.swap_caption("The app also checks the answer in other ways.")

        card_xs = [-4.2, 0, 4.2]
        cards = [
            RoundedRectangle(width=3.9, height=4.6, corner_radius=0.1,
                              stroke_color=SECONDARY_COLOR, stroke_width=2).move_to([cx, 0.2, 0])
            for cx in card_xs
        ]

        # ---------------------------------------------------- Card 1 ---
        cx = card_xs[0]
        c1_outline = cards[0]
        c1_header = Tex("Floor for this cut", font_size=28, color=TEXT_COLOR)
        c1_header.move_to([cx, 2.15, 0])
        c1_sub = Tex(r"heavier group $\div$ 3", font_size=22, color=SECONDARY_COLOR)
        c1_sub.move_to([cx, 1.7, 0])
        self.play(Create(c1_outline), FadeIn(c1_header), FadeIn(c1_sub))

        g1 = SCENE11["optimal_cut_group1"]
        bar = Rectangle(width=3.0, height=0.35, fill_color=GROUP1_COLOR, fill_opacity=1,
                         stroke_width=0)
        bar.move_to([cx, 1.1, 0])
        bar_text = Tex(f"{g1:,} kW", font_size=22, color=BG_COLOR)
        bar_text.move_to(bar.get_center())
        self.play(FadeIn(bar), FadeIn(bar_text))

        down_arrow = Arrow([cx, 0.85, 0], [cx, 0.55, 0], stroke_width=3, color=TEXT_COLOR, buff=0)
        self.play(GrowArrow(down_arrow))

        floor_val = SCENE11["floor_this_cut"]
        seg_group = VGroup()
        for i in range(3):
            seg_x = cx - 1.0 + i * 1.0
            seg = Rectangle(width=1.0, height=0.35, fill_color=GROUP1_COLOR, fill_opacity=1,
                             stroke_color=BG_COLOR, stroke_width=2)
            seg.move_to([seg_x, 0.3, 0])
            seg_text = Tex(str(floor_val), font_size=22, color=BG_COLOR)
            seg_text.move_to(seg.get_center())
            seg_group.add(VGroup(seg, seg_text))
        self.play(FadeIn(seg_group), run_time=1.0)

        c1_line1 = Tex(f"{floor_val} $\\le$ {SCENE11['best']}", font_size=26, color=TEXT_COLOR)
        check1 = Tex(r"$\checkmark$", font_size=26, color=HL_COLOR)
        c1_line1_group = VGroup(c1_line1, check1).arrange(RIGHT, buff=0.15)
        c1_line1_group.move_to([cx, -0.6, 0])
        c1_line2 = Tex("a floor for this grouping", font_size=22, color=SECONDARY_COLOR)
        c1_line2.move_to([cx, -1.1, 0])
        self.play(FadeIn(c1_line1_group), FadeIn(c1_line2))

        cap1a = self.swap_caption("With this cut, the heavier group carries 2,430 kW...")
        self.wait(0.6)
        cap1b = self.swap_caption("...so its floor is 810.")
        self.wait(0.6)
        cap1c = self.swap_caption("990 is above that floor, as it must be.")
        self.wait(1.0)

        # ---------------------------------------------------- Card 2 ---
        cx2 = card_xs[1]
        c2_outline = cards[1]
        c2_header = Tex("Floor for any answer", font_size=28, color=TEXT_COLOR)
        if c2_header.width > 3.6:
            c2_header = Tex("Floor for any answer", font_size=26, color=TEXT_COLOR)
        c2_header.move_to([cx2, 2.15, 0])
        c2_sub = Tex(r"total $\div$ (groups $\times$ 3)", font_size=22, color=SECONDARY_COLOR)
        c2_sub.move_to([cx2, 1.7, 0])
        self.play(Create(c2_outline), FadeIn(c2_header), FadeIn(c2_sub))

        fraction = MathTex(r"\dfrac{4480}{2 \times 3}", "=", "746.7", font_size=34)
        fraction.set_color(TEXT_COLOR)
        fraction.set_color_by_tex("746.7", LB_COLOR)
        fraction.move_to([cx2, 0.7, 0])
        self.play(FadeIn(fraction))

        c2_line1 = Tex(r"746.7 $\le$ 990", font_size=26, color=TEXT_COLOR)
        check2 = Tex(r"$\checkmark$", font_size=26, color=HL_COLOR)
        c2_line1_group = VGroup(c2_line1, check2).arrange(RIGHT, buff=0.15)
        c2_line1_group.move_to([cx2, -0.6, 0])
        c2_line2 = Tex("the relaxed floor", font_size=22, color=SECONDARY_COLOR)
        c2_line2.move_to([cx2, -1.1, 0])
        self.play(FadeIn(c2_line1_group), FadeIn(c2_line2))

        cap2a = self.swap_caption("For any answer at all, the floor is 746.7 --- also below 990.")
        self.wait(1.2)

        # ---------------------------------------------------- Card 3 ---
        cx3 = card_xs[2]
        c3_outline = cards[2]
        c3_header = Tex("Try every pairing", font_size=28, color=TEXT_COLOR)
        c3_header.move_to([cx3, 2.15, 0])
        c3_sub = Tex("of the worst group (Group 1)", font_size=22, color=SECONDARY_COLOR)
        if c3_sub.width > 3.6:
            c3_sub.scale_to_fit_width(3.6)
        c3_sub.move_to([cx3, 1.7, 0])
        self.play(Create(c3_outline), FadeIn(c3_header), FadeIn(c3_sub))

        dots = self.dot_grid(36, 2.1)
        dots.move_to([cx3, 0.25, 0])
        self.play(FadeIn(dots), run_time=1.5)

        self.play(LaggedStart(*[
            Flash(d, color=TEXT_COLOR, flash_radius=0.03, line_length=0.02)
            for d in dots[::20]
        ], lag_ratio=0.05), run_time=0.8)

        winner = dots[22 * 36 + 13]
        winner_dot = Dot(winner.get_center(), radius=0.06, color=HL_COLOR, fill_opacity=1)
        self.play(Transform(winner, winner_dot))

        c3_line1 = Tex(f"6$^4$ = {SCENE11['brute_force_combos']:,} pairings", font_size=24, color=TEXT_COLOR)
        c3_line1.move_to([cx3, -1.2, 0])
        c3_line2 = MathTex("\\text{best} = ", "990", "= \\text{MILP}", r"\checkmark", font_size=24)
        c3_line2.set_color(TEXT_COLOR)
        c3_line2.set_color_by_tex("990", HL_COLOR)
        c3_line2.move_to([cx3, -1.65, 0])
        self.play(FadeIn(c3_line1), FadeIn(c3_line2))

        cap3a = self.swap_caption("Finally, it tries all 1,296 pairings of the worst group, one by one.")
        self.wait(1.0)
        cap3b = self.swap_caption("The best of them is 990 --- exactly what the model found.")
        self.wait(1.5)

        self.play(Indicate(check1, color=HL_COLOR), Indicate(check2, color=HL_COLOR),
                   Indicate(c3_line2[3], color=HL_COLOR))

        self.layout_items = [
            t, c1_outline, c1_header, c1_sub, bar, bar_text, seg_group, c1_line1_group, c1_line2,
            c2_outline, c2_header, c2_sub, fraction, c2_line1_group, c2_line2,
            c3_outline, c3_header, c3_sub, c3_line1, c3_line2, cap3b,
        ]
        idx_c1_outline = self.layout_items.index(c1_outline)
        idx_c2_outline = self.layout_items.index(c2_outline)
        idx_c3_outline = self.layout_items.index(c3_outline)
        c1_members = [c1_header, c1_sub, bar, bar_text, seg_group, c1_line1_group, c1_line2]
        c2_members = [c2_header, c2_sub, fraction, c2_line1_group, c2_line2]
        c3_members = [c3_header, c3_sub, c3_line1, c3_line2]
        allowed = set()
        for m in c1_members:
            allowed.add((idx_c1_outline, self.layout_items.index(m)))
        for m in c2_members:
            allowed.add((idx_c2_outline, self.layout_items.index(m)))
        for m in c3_members:
            allowed.add((idx_c3_outline, self.layout_items.index(m)))
        allowed.add((self.layout_items.index(bar), self.layout_items.index(bar_text)))
        self.allowed_overlaps = allowed
        self.background_items = [down_arrow, dots]
        self.check_layout("11_3")

        cap4 = self.swap_caption("990 kW is the best possible answer for this hall.")
        self.wait(1.5)
        cap5 = self.swap_caption("So what does this look like in the real hall?")
        self.wait(1.5)

        self.play(
            FadeOut(t), FadeOut(c1_outline), FadeOut(c1_header), FadeOut(c1_sub),
            FadeOut(bar), FadeOut(bar_text), FadeOut(down_arrow), FadeOut(seg_group),
            FadeOut(c1_line1_group), FadeOut(c1_line2),
            FadeOut(c2_outline), FadeOut(c2_header), FadeOut(c2_sub), FadeOut(fraction),
            FadeOut(c2_line1_group), FadeOut(c2_line2),
            FadeOut(c3_outline), FadeOut(c3_header), FadeOut(c3_sub), FadeOut(dots),
            FadeOut(c3_line1), FadeOut(c3_line2), FadeOut(cap5),
            run_time=1.0,
        )
        self.current_caption = None
