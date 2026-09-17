"""Scene 09 -- "Relaxation and the lower bound"

Built strictly from scene09_prompt.md + common_prompt.md (corrected
version, "common_prompt แก้.md" -- Section 5.5's LP relaxation values).

Starts from: black (Scene 08 ended on "Next: how a solver finds the best
answer without trying them all." then faded to black).

Ends with: the number line is shown, then fade to black after "To close
this gap, the solver starts to branch."

Run with:
    manim -pqh scene09_relaxation.py Scene09Relaxation
"""
from manim import *

from common.style import (
    BG_COLOR, TEXT_COLOR, SECONDARY_COLOR, UPS_COLORS,
    HL_COLOR, LB_COLOR, GROUP1_COLOR, GROUP2_COLOR,
)
from common.layout import caption, title, LayoutCheckMixin
from common.data import DEMO_ROWS, SCENE09
from common.widgets import pair_chip

ROW_YS_8 = [1.9 - 0.55 * k for k in range(8)]


def number_line_x(v):
    return -5.5 + (v - 700) * 11 / 700


class Scene09Relaxation(LayoutCheckMixin, Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        self.current_caption = None

        self.beat_9_1_relax()
        self.beat_9_2_strange_answer()
        self.beat_9_3_floor()
        self.beat_9_4_trap()

    # --------------------------------------------------------- helpers ---
    def swap_caption(self, text):
        new_cap = caption(text)
        if self.current_caption is not None:
            self.play(FadeOut(self.current_caption))
        self.play(FadeIn(new_cap))
        self.current_caption = new_cap
        return new_cap

    # ===================================================== Beat 9.1 =====
    def beat_9_1_relax(self):
        t = title("Relax the switches")
        self.play(FadeIn(t, shift=DOWN * 0.15))

        zero_one = MathTex(r"\{0,\,1\}", font_size=64, color=TEXT_COLOR)
        zero_one.move_to([-2.8, 1.0, 0])
        self.play(FadeIn(zero_one))

        cap = self.swap_caption("Every switch in the real model must be 0 or 1.")
        self.wait(1.0)

        arrow = Arrow([-1.5, 1.0, 0], [1.5, 1.0, 0], stroke_width=3, color=TEXT_COLOR, buff=0)
        interval = MathTex(r"[0,\,1]", font_size=64, color=TEXT_COLOR)
        interval.move_to([2.8, 1.0, 0])
        self.play(GrowArrow(arrow))
        self.play(FadeIn(interval))

        cap2 = self.swap_caption("So the solver first lets every switch take any value from 0 to 1.")

        slider_line = Line([-3.0, -0.8, 0], [3.0, -0.8, 0], color=SECONDARY_COLOR, stroke_width=3)
        tick0 = Tex("0", font_size=26, color=SECONDARY_COLOR).move_to([-3.0, -1.25, 0])
        tick1 = Tex("1", font_size=26, color=SECONDARY_COLOR).move_to([3.0, -1.25, 0])
        knob = Dot([-3.0, -0.8, 0], radius=0.14, color=GROUP1_COLOR, fill_opacity=1)
        readout = DecimalNumber(0.0, num_decimal_places=3, font_size=28, color=GROUP1_COLOR)
        readout.move_to(knob.get_center() + UP * 0.45)
        readout.add_updater(lambda m: m.move_to(knob.get_center() + UP * 0.45))

        self.play(Create(slider_line), FadeIn(tick0), FadeIn(tick1), FadeIn(knob), FadeIn(readout))

        self.play(knob.animate.move_to([3.0, -0.8, 0]), readout.animate.set_value(1.0), run_time=1.0)
        self.play(knob.animate.move_to([-3.0, -0.8, 0]), readout.animate.set_value(0.0), run_time=0.8)
        final_x = -3.0 + 0.437 * 6.0
        self.play(knob.animate.move_to([final_x, -0.8, 0]), readout.animate.set_value(0.437), run_time=0.8)

        cap3 = self.swap_caption("This easier version is called the LP relaxation.")
        self.wait(1.5)

        readout.clear_updaters()
        self.layout_items = [t, zero_one, interval, tick0, tick1, readout, cap3]
        self.background_items = [arrow, slider_line, knob]
        self.allowed_overlaps = set()
        self.check_layout("9_1")

        self.play(
            FadeOut(VGroup(t, zero_one, arrow, interval, slider_line, tick0, tick1, knob, readout, cap3)),
        )
        self.current_caption = None

    # ===================================================== Beat 9.2 =====
    def beat_9_2_strange_answer(self):
        t = title("What the relaxed answer looks like")
        if t.width > 12.5:
            new_t = Tex("What the relaxed answer looks like", font_size=40, color=TEXT_COLOR)
            new_t.move_to([0, 3.15, 0])
            t = new_t
        self.play(FadeIn(t, shift=DOWN * 0.15))

        legend_sq1 = Square(side_length=0.2, fill_color=GROUP1_COLOR, fill_opacity=1, stroke_width=0)
        legend_txt1 = Tex("Group 1", font_size=22, color=TEXT_COLOR)
        legend1 = VGroup(legend_sq1, legend_txt1).arrange(RIGHT, buff=0.15)
        legend1.move_to([-5.3 + legend1.width / 2, 2.45, 0])

        legend_sq2 = Square(side_length=0.2, fill_color=GROUP2_COLOR, fill_opacity=1, stroke_width=0)
        legend_txt2 = Tex("Group 2", font_size=22, color=TEXT_COLOR)
        legend2 = VGroup(legend_sq2, legend_txt2).arrange(RIGHT, buff=0.15)
        legend2.move_to([-3.4 + legend2.width / 2, 2.45, 0])

        note = Tex("one of many possible relaxed answers", font_size=22, color=SECONDARY_COLOR)
        note.move_to([3.6, 2.45, 0])
        self.play(FadeIn(legend1), FadeIn(legend2), FadeIn(note))

        names = []
        bars_pink = []
        bars_grey = []
        seps = []
        shares = []
        for i in range(8):
            y = ROW_YS_8[i]
            t_val = SCENE09["t_row1"] if i == 0 else SCENE09["t_others"]
            name = Tex(DEMO_ROWS[i][0], font_size=22, color=TEXT_COLOR)
            name.move_to([-6.3 + name.width / 2, y, 0])
            names.append(name)

            pink_w = 3.4 * t_val
            pink = Rectangle(width=max(pink_w, 0.001), height=0.36, fill_color=GROUP1_COLOR,
                              fill_opacity=1, stroke_width=0)
            pink.move_to([-5.3 + pink_w / 2, y, 0])
            grey_w = 3.4 - pink_w
            grey = Rectangle(width=max(grey_w, 0.001), height=0.36, fill_color=GROUP2_COLOR,
                              fill_opacity=1, stroke_width=0)
            grey.move_to([-5.3 + pink_w + grey_w / 2, y, 0])
            sep = Line([-5.3 + pink_w, y - 0.18, 0], [-5.3 + pink_w, y + 0.18, 0],
                       color=BG_COLOR, stroke_width=2)
            bars_pink.append(pink)
            bars_grey.append(grey)
            seps.append(sep)

            pct1 = f"{t_val*100:.0f}\%" if t_val in (1.0, 0.0) else f"{t_val*100:.1f}\%"
            pct2_val = 1 - t_val
            pct2 = f"{pct2_val*100:.0f}\%" if pct2_val in (1.0, 0.0) else f"{pct2_val*100:.1f}\%"
            share = VGroup(
                Tex(pct1, font_size=22, color=GROUP1_COLOR),
                Tex("|", font_size=22, color=SECONDARY_COLOR),
                Tex(pct2, font_size=22, color=GROUP2_COLOR),
            ).arrange(RIGHT, buff=0.1)
            share.move_to([-1.7 + share.width / 2, y, 0])
            shares.append(share)

        self.play(LaggedStart(*[FadeIn(n) for n in names], lag_ratio=0.1), run_time=1.0)
        self.play(
            *[GrowFromEdge(p, LEFT) for p in bars_pink],
            *[FadeIn(g) for g in bars_grey],
            *[FadeIn(s) for s in seps],
            run_time=1.2,
        )
        self.play(*[FadeIn(s) for s in shares])

        cap = self.swap_caption("In the relaxed answer, most rows sit partly in both groups.")
        self.wait(1.0)

        row3_bar = VGroup(bars_pink[2], bars_grey[2])
        outline = SurroundingRectangle(row3_bar, color=TEXT_COLOR, buff=0.03)

        card1_header = Tex("Row 3", font_size=26, color=TEXT_COLOR)
        card1_header.move_to([3.6, 1.55, 0])
        card1_line1 = Tex(r"43.7\% in Group 1, pair", font_size=22, color=TEXT_COLOR)
        chip_bc = pair_chip("BC", font=22, pad=0.08)
        card1_row1 = VGroup(card1_line1, chip_bc).arrange(RIGHT, buff=0.1)
        card1_row1.move_to([3.6, 1.1, 0])
        card1_line2 = Tex(r"56.3\% in Group 2, pair", font_size=22, color=TEXT_COLOR)
        chip_bd = pair_chip("BD", font=22, pad=0.08)
        card1_row2 = VGroup(card1_line2, chip_bd).arrange(RIGHT, buff=0.1)
        card1_row2.move_to([3.6, 0.7, 0])
        card1 = VGroup(card1_header, card1_row1, card1_row2)

        self.play(Create(outline), FadeIn(card1))

        cap2 = self.swap_caption(r"Row 3 is 43.7\% in Group 1 and 56.3\% in Group 2...")
        self.wait(0.6)
        cap2b = self.swap_caption("...with a different pair in each.")
        self.wait(1.2)

        row1_bar = VGroup(bars_pink[0], bars_grey[0])
        new_outline = SurroundingRectangle(row1_bar, color=TEXT_COLOR, buff=0.03)

        card2_header = Tex("Row 1", font_size=26, color=TEXT_COLOR)
        card2_header.move_to([3.6, -0.05, 0])
        card2_line = Tex("all in Group 1, but its pair is split three ways:", font_size=22, color=TEXT_COLOR)
        if card2_line.width > 5.6:
            card2_line.scale_to_fit_width(5.6)
        card2_line.move_to([3.6, -0.45, 0])

        splits = SCENE09["row1_pair_splits"]
        chip_xs = [2.4, 3.6, 4.8]
        chip_mobs = []
        val_mobs = []
        for (pair, val), x in zip(splits.items(), chip_xs):
            c = pair_chip(pair, font=22, pad=0.08)
            c.move_to([x, -1.0, 0])
            v = Tex(f"{val:.3f}", font_size=22, color=TEXT_COLOR)
            v.move_to([x, -1.4, 0])
            chip_mobs.append(c)
            val_mobs.append(v)
        card2 = VGroup(card2_header, card2_line, *chip_mobs, *val_mobs)

        self.play(Transform(outline, new_outline), FadeIn(card2))

        cap3 = self.swap_caption("Row 1 stays in Group 1, but its pair is split three ways.")
        self.wait(1.2)

        g1_total, g2_total = SCENE09["group_totals_relaxed"]
        totals = VGroup(
            Tex(f"Group 1: {g1_total:,} kW", font_size=24, color=GROUP1_COLOR),
            Tex("  |  ", font_size=24, color=SECONDARY_COLOR),
            Tex(f"Group 2: {g2_total:,} kW", font_size=24, color=GROUP2_COLOR),
        ).arrange(RIGHT, buff=0.1)
        totals.move_to([-3.6, -2.45, 0])
        self.play(FadeIn(totals))

        cap4 = self.swap_caption("The load ends up split exactly in half: 2,240 kW each.")
        self.wait(1.2)

        stamp_box = DashedVMobject(
            RoundedRectangle(width=2.6, height=0.6, corner_radius=0.08,
                              stroke_color=SECONDARY_COLOR, stroke_width=2),
            num_dashes=24,
        )
        stamp_box.move_to([3.6, -2.15, 0])
        stamp_text = Tex("Not buildable", font_size=30, color=SECONDARY_COLOR)
        stamp_text.move_to([3.6, -2.15, 0])
        self.play(Create(stamp_box), FadeIn(stamp_text))

        cap5 = self.swap_caption("It cannot be built --- but it is fast to solve...")
        self.wait(0.6)
        cap5b = self.swap_caption("...and it tells us something useful.")
        self.wait(1.5)

        self.layout_items = [
            t, legend1, legend2, note, *names, *shares,
            card1_header, card1_row1, card1_row2,
            card2_header, card2_line, *chip_mobs, *val_mobs,
            totals, stamp_box, stamp_text, outline, cap5b,
        ]
        idx_outline = self.layout_items.index(outline)
        idx_stamp_box = self.layout_items.index(stamp_box)
        idx_stamp_text = self.layout_items.index(stamp_text)
        allowed = {(idx_outline, self.layout_items.index(name)) for name in []}
        allowed.add((idx_stamp_box, idx_stamp_text))
        self.allowed_overlaps = allowed
        self.background_items = [*bars_pink, *bars_grey, *seps]
        self.check_layout("9_2")

        self.play(
            FadeOut(VGroup(
                legend1, legend2, note, *names, *bars_pink, *bars_grey, *seps, *shares,
                card1_header, card1_row1, card1_row2, card2_header, card2_line,
                *chip_mobs, *val_mobs, totals, stamp_box, stamp_text, outline,
            )),
            FadeOut(self.current_caption),
        )
        self.current_caption = None
        self._title = t

    # ===================================================== Beat 9.3 =====
    def beat_9_3_floor(self):
        new_title = Tex("A floor no answer can go below", font_size=44, color=TEXT_COLOR)
        if new_title.width > 12.5:
            new_title = Tex("A floor no answer can go below", font_size=40, color=TEXT_COLOR)
        new_title.move_to([0, 3.15, 0])
        self.play(Transform(self._title, new_title), run_time=0.6)

        line1 = Tex("When a UPS fails, the group's whole load sits on 3 UPS", font_size=28, color=TEXT_COLOR)
        line1.move_to([0, 1.9, 0])
        line2 = Tex(r"$\to$ one of them carries at least a third", font_size=26, color=SECONDARY_COLOR)
        line2.move_to([0, 1.35, 0])
        self.play(FadeIn(line1))
        self.play(FadeIn(line2))

        cap = self.swap_caption("When a UPS fails, its group's load moves onto the other three.")
        self.wait(1.2)

        line3 = Tex("The two groups share 4,480 kW", font_size=28, color=TEXT_COLOR)
        line3.move_to([0, 0.55, 0])
        line4 = Tex(r"$\to$ one group carries at least half", font_size=26, color=SECONDARY_COLOR)
        line4.move_to([0, 0.0, 0])
        self.play(FadeIn(line3))
        self.play(FadeIn(line4))

        cap2 = self.swap_caption("And one of the two groups must carry at least half of the total.")
        self.wait(1.2)

        fraction = MathTex(
            r"\text{LB}", "=", r"\dfrac{4480}{2 \times 3}", "=", "746.7", font_size=48,
        )
        fraction.set_color(TEXT_COLOR)
        fraction.set_color_by_tex(r"\text{LB}", LB_COLOR)
        fraction.set_color_by_tex("746.7", LB_COLOR)
        fraction.move_to([0, -1.1, 0])
        self.play(Write(fraction))

        legend_line = Tex("2 groups $\\times$ 3 surviving UPS", font_size=24, color=SECONDARY_COLOR)
        legend_line.move_to([0, -2.2, 0])
        self.play(FadeIn(legend_line))

        cap3 = self.swap_caption("So no answer --- relaxed or real --- can have M below 746.7 kW.")
        self.wait(1.5)

        cap4 = self.swap_caption("The relaxed answer reaches exactly this floor.")
        self.wait(1.0)
        cap4b = self.swap_caption("We call it the lower bound, LB.")
        self.wait(1.5)

        self.layout_items = [self._title, line1, line2, line3, line4, fraction, legend_line, cap4b]
        self.allowed_overlaps = set()
        self.check_layout("9_3")

        self.play(
            FadeOut(VGroup(line1, line2, line3, line4, fraction, legend_line)),
            FadeOut(self.current_caption),
        )
        self.current_caption = None

    # ===================================================== Beat 9.4 =====
    def beat_9_4_trap(self):
        new_title = title("Where the best answer must be")
        self.play(Transform(self._title, new_title), run_time=0.6)

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

        lb = SCENE09["lb"]
        lb_x = number_line_x(lb)
        lb_marker = Triangle(color=LB_COLOR, fill_color=LB_COLOR, fill_opacity=1)
        lb_marker.scale(0.1)
        lb_marker.move_to([lb_x, -0.18, 0])
        lb_label = Tex(f"LB {lb:.1f}", font_size=26, color=LB_COLOR)
        lb_label.move_to([lb_x, -1.0, 0])
        if lb_label.get_left()[0] < -6.4:
            lb_label.move_to([-6.4 + lb_label.width / 2, -1.0, 0])
        self.play(FadeIn(lb_marker), Flash(lb_marker, color=LB_COLOR), FadeIn(lb_label))

        sol_a = SCENE09["solution_a_m"]
        sol_b = SCENE09["solution_b_m"]
        a_x = number_line_x(sol_a)
        b_x = number_line_x(sol_b)

        a_marker = Triangle(color=HL_COLOR, fill_color=HL_COLOR, fill_opacity=1)
        a_marker.scale(0.1)
        a_marker.rotate(PI)
        a_marker.move_to([a_x, 0.25, 0])
        a_label = Tex(f"Solution A  {sol_a:,}", font_size=26, color=HL_COLOR)
        a_label.move_to([a_x, 0.8, 0])

        b_marker = Triangle(color=HL_COLOR, fill_color=HL_COLOR, fill_opacity=1)
        b_marker.scale(0.1)
        b_marker.rotate(PI)
        b_marker.move_to([b_x, 0.25, 0])
        b_label = Tex(f"Solution B  {sol_b:,}", font_size=26, color=HL_COLOR)
        b_label.move_to([b_x, 0.8, 0])

        self.play(FadeIn(a_marker), FadeIn(a_label))
        self.play(FadeIn(b_marker), FadeIn(b_label))

        cap = self.swap_caption("We already know two real answers: 1,350 and 1,100 kW.")
        self.wait(1.0)

        band = Rectangle(width=(b_x - lb_x), height=0.5, fill_color=LB_COLOR, fill_opacity=0.15,
                          stroke_width=0)
        band.move_to([(lb_x + b_x) / 2, 0, 0])
        band_label = Tex("the best M is in here", font_size=26, color=TEXT_COLOR)
        band_label.move_to([(lb_x + b_x) / 2, 1.6, 0])
        self.play(GrowFromEdge(band, LEFT), run_time=1.0)
        self.play(FadeIn(band_label))

        cap2 = self.swap_caption("So the best M is somewhere between 746.7 and 1,100 kW.")
        self.wait(1.5)

        self.background_items = [num_line, ticks, band]
        self.layout_items = [
            self._title, tick_labels, lb_marker, lb_label,
            a_marker, a_label, b_marker, b_label, band_label, cap2,
        ]
        allowed = {
            (self.layout_items.index(lb_marker), self.layout_items.index(a_marker)),
        }
        self.allowed_overlaps = allowed
        self.check_layout("9_4")

        cap3 = self.swap_caption("To close this gap, the solver starts to branch.")
        self.wait(1.5)

        self.play(
            FadeOut(self._title), FadeOut(num_line), FadeOut(ticks), FadeOut(tick_labels),
            FadeOut(lb_marker), FadeOut(lb_label), FadeOut(a_marker), FadeOut(a_label),
            FadeOut(b_marker), FadeOut(b_label), FadeOut(band), FadeOut(band_label),
            FadeOut(cap3),
            run_time=1.0,
        )
        self.current_caption = None
