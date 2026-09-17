"""Scene 12 -- "Back to the data hall"

Built strictly from scene12_prompt.md + common_prompt.md.

Starts from: black (Scene 11 ended on "So what does this look like in the
real hall?" then faded to black).

Ends with: fade to black. END OF THE VIDEO.

Run with:
    manim -pqh scene12_back_to_reality.py Scene12BackToReality
"""
from manim import *

from common.style import (
    BG_COLOR, TEXT_COLOR, SECONDARY_COLOR, UPS_COLORS,
    HL_COLOR, GROUP1_COLOR, GROUP2_COLOR, ROW_FILL, ROW_STROKE,
)
from common.layout import caption, title, LayoutCheckMixin
from common.data import (
    DEMO_ROWS, SOLUTION_OPT, GROUP_TOTALS, MOST_BALANCED_CUT, IMPROVEMENT_PCT,
)
from common.widgets import ups_box, pair_chip, fail_anims

ROW_YS_8 = [2.4 - 0.56 * k for k in range(8)]
RACK_XS = [-4.75 + 0.5 * i for i in range(8)]
OPT_CUT = SOLUTION_OPT["cut_after"]


def pair_for(idx):
    name, kw, type_ = DEMO_ROWS[idx]
    if type_ == "4-source":
        return "ABCD"
    return SOLUTION_OPT["pairs"][name]


class Scene12BackToReality(LayoutCheckMixin, Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        self.current_caption = None

        self.beat_12_1_hall()
        self.beat_12_2_design()
        self.beat_12_3_compare()
        self.beat_12_4_lesson()
        self.beat_12_5_journey()

    # --------------------------------------------------------- helpers ---
    def swap_caption(self, text):
        new_cap = caption(text)
        if self.current_caption is not None:
            self.play(FadeOut(self.current_caption))
        self.play(FadeIn(new_cap))
        self.current_caption = new_cap
        return new_cap

    # ===================================================== Beat 12.1 =====
    def beat_12_1_hall(self):
        building = Rectangle(width=10.4, height=5.5, stroke_color=ROW_STROKE, stroke_width=2)
        building.move_to([(-6.4 + 4.0) / 2, (-2.3 + 3.2) / 2, 0])
        inner_wall = Line([0.6, -2.3, 0], [0.6, 3.2, 0], color=ROW_STROKE, stroke_width=2)

        it_hall_lbl = Tex("IT Hall", font_size=26, color=SECONDARY_COLOR)
        it_hall_lbl.move_to([-6.2 + it_hall_lbl.width / 2, 2.85, 0], aligned_edge=LEFT)
        ups_room_lbl = Tex("UPS Room", font_size=26, color=SECONDARY_COLOR)
        ups_room_lbl.move_to([0.8 + ups_room_lbl.width / 2, 2.85, 0], aligned_edge=LEFT)
        outdoor_lbl = Tex("Outdoor", font_size=26, color=SECONDARY_COLOR)
        outdoor_lbl.move_to([4.8 + outdoor_lbl.width / 2, 2.85, 0], aligned_edge=LEFT)

        self.play(Create(building), Create(inner_wall), run_time=1.2)
        self.play(FadeIn(it_hall_lbl), FadeIn(ups_room_lbl), FadeIn(outdoor_lbl), run_time=0.5)

        rows = []
        row_labels = []
        for i in range(8):
            y = ROW_YS_8[i]
            racks = VGroup(*[
                Rectangle(width=0.42, height=0.26, stroke_color=ROW_STROKE, stroke_width=1.5,
                          fill_color=ROW_FILL, fill_opacity=1).move_to([x, y, 0])
                for x in RACK_XS
            ])
            lbl = Tex(DEMO_ROWS[i][0], font_size=22, color=TEXT_COLOR)
            lbl.move_to([-5.2 - lbl.width / 2, y, 0], aligned_edge=RIGHT)
            rows.append(racks)
            row_labels.append(lbl)
            self.play(
                LaggedStart(*[FadeIn(r) for r in racks], lag_ratio=0.08),
                FadeIn(lbl),
                run_time=0.3,
            )

        cap = self.swap_caption("Back to the data hall --- now with all eight rows.")
        self.wait(1.2)

        self.background_items = [building, inner_wall]
        self.layout_items = [it_hall_lbl, ups_room_lbl, outdoor_lbl, *rows, *row_labels, cap]
        self.allowed_overlaps = set()
        self.check_layout("12_1")

        self._building = building
        self._inner_wall = inner_wall
        self._it_hall_lbl = it_hall_lbl
        self._ups_room_lbl = ups_room_lbl
        self._outdoor_lbl = outdoor_lbl
        self._rows = rows
        self._row_labels = row_labels

    # ===================================================== Beat 12.2 =====
    def beat_12_2_design(self):
        g1_rows = VGroup(*self._rows[:5])
        g2_rows = VGroup(*self._rows[5:])
        self.play(
            g1_rows.animate.set_stroke(GROUP1_COLOR).set_fill(GROUP1_COLOR, opacity=0.35),
            g2_rows.animate.set_stroke(GROUP2_COLOR).set_fill(GROUP2_COLOR, opacity=0.35),
            run_time=0.8,
        )

        cut_y = (ROW_YS_8[4] + ROW_YS_8[5]) / 2
        cut_line = DashedLine([-6.1, cut_y, 0], [0.3, cut_y, 0], color=TEXT_COLOR, stroke_width=4)
        self.play(Create(cut_line))

        cap = self.swap_caption("The best design cuts after Row 5.")
        self.wait(1.0)

        chips = []
        for i in range(8):
            pair = pair_for(i)
            chip = pair_chip(pair, font=22)
            chip.move_to([-0.95 + chip.width / 2, ROW_YS_8[i], 0])
            chips.append(chip)
            self.play(FadeIn(chip), run_time=0.35)

        cap2 = self.swap_caption("Each 2-source row gets the pair the model chose.")
        self.wait(1.0)

        def ups_set(cx, y, colour):
            boxes = VGroup(*[
                ups_box(letter, w=0.62, h=0.5, font=22, short=True)
                for letter in ["A", "B", "C", "D"]
            ])
            xs = [1.1, 1.85, 2.6, 3.35]
            for box, x in zip(boxes, xs):
                box.move_to([x, y, 0])
            outline = SurroundingRectangle(boxes, color=colour, buff=0.06,
                                            fill_color=BG_COLOR, fill_opacity=0)
            return boxes, outline

        g1_label = Tex("Group 1", font_size=22, color=GROUP1_COLOR)
        g1_label.move_to([2.3, 2.35, 0])
        g1_boxes, g1_outline = ups_set(2.3, 1.85, GROUP1_COLOR)
        self.play(FadeIn(g1_label), FadeIn(g1_boxes), Create(g1_outline))

        g2_label = Tex("Group 2", font_size=22, color=GROUP2_COLOR)
        g2_label.move_to([2.3, 0.85, 0])
        g2_boxes, g2_outline = ups_set(2.3, 0.35, GROUP2_COLOR)
        self.play(FadeIn(g2_label), FadeIn(g2_boxes), Create(g2_outline))

        gen1 = Rectangle(width=1.6, height=0.6, stroke_color=GROUP1_COLOR, stroke_width=2,
                         fill_color=BG_COLOR, fill_opacity=0)
        gen1.move_to([5.6, 1.85, 0])
        gen1_lbl = Tex("Gen 1", font_size=22, color=TEXT_COLOR)
        gen1_lbl.move_to(gen1.get_center())
        gen2 = Rectangle(width=1.6, height=0.6, stroke_color=GROUP2_COLOR, stroke_width=2,
                         fill_color=BG_COLOR, fill_opacity=0)
        gen2.move_to([5.6, 0.35, 0])
        gen2_lbl = Tex("Gen 2", font_size=22, color=TEXT_COLOR)
        gen2_lbl.move_to(gen2.get_center())
        self.play(FadeIn(VGroup(gen1, gen1_lbl)), FadeIn(VGroup(gen2, gen2_lbl)))

        arrow1 = Arrow([4.75, 1.85, 0], [3.85, 1.85, 0], stroke_width=3, color=GROUP1_COLOR, buff=0)
        arrow2 = Arrow([4.75, 0.35, 0], [3.85, 0.35, 0], stroke_width=3, color=GROUP2_COLOR, buff=0)
        self.play(GrowArrow(arrow1), GrowArrow(arrow2))

        dot1 = Dot(arrow1.get_start(), radius=0.05, color=GROUP1_COLOR)
        dot2 = Dot(arrow2.get_start(), radius=0.05, color=GROUP2_COLOR)
        self.play(FadeIn(dot1), FadeIn(dot2))
        self.play(dot1.animate.move_to(arrow1.get_end()), dot2.animate.move_to(arrow2.get_end()),
                   run_time=0.6)
        self.play(FadeOut(dot1), FadeOut(dot2))

        cap3 = self.swap_caption("Each group has its own generator and its own UPS A to D.")
        self.wait(1.0)

        note = Tex("sized for 990 kW each", font_size=22, color=SECONDARY_COLOR)
        note.move_to([2.3, -0.45, 0])
        self.play(FadeIn(note))
        self.play(Indicate(g1_boxes), Indicate(g2_boxes))

        cap4 = self.swap_caption("Every UPS only needs to handle 990 kW in the worst case.")
        self.wait(1.5)

        self.background_items = [self._building, self._inner_wall, cut_line, arrow1, arrow2]
        self.layout_items = [
            self._it_hall_lbl, self._ups_room_lbl, self._outdoor_lbl,
            *self._rows, *self._row_labels, *chips,
            g1_label, g1_boxes, g1_outline, g2_label, g2_boxes, g2_outline,
            gen1, gen1_lbl, gen2, gen2_lbl, note, cap4,
        ]
        idx_g1_outline = self.layout_items.index(g1_outline)
        idx_g1_boxes = self.layout_items.index(g1_boxes)
        idx_g2_outline = self.layout_items.index(g2_outline)
        idx_g2_boxes = self.layout_items.index(g2_boxes)
        idx_gen1 = self.layout_items.index(gen1)
        idx_gen1_lbl = self.layout_items.index(gen1_lbl)
        idx_gen2 = self.layout_items.index(gen2)
        idx_gen2_lbl = self.layout_items.index(gen2_lbl)
        self.allowed_overlaps = {
            (idx_g1_outline, idx_g1_boxes), (idx_g2_outline, idx_g2_boxes),
            (idx_gen1, idx_gen1_lbl), (idx_gen2, idx_gen2_lbl),
        }
        self.check_layout("12_2")

        self._chips = chips
        self._g1_label, self._g1_boxes, self._g1_outline = g1_label, g1_boxes, g1_outline
        self._g2_label, self._g2_boxes, self._g2_outline = g2_label, g2_boxes, g2_outline
        self._gen1, self._gen1_lbl, self._gen2, self._gen2_lbl = gen1, gen1_lbl, gen2, gen2_lbl
        self._arrow1, self._arrow2, self._cut_line, self._note = arrow1, arrow2, cut_line, note

    # ===================================================== Beat 12.3 =====
    def beat_12_3_compare(self):
        plan = VGroup(
            self._building, self._inner_wall, self._it_hall_lbl, self._ups_room_lbl,
            self._outdoor_lbl, *self._rows, *self._row_labels, *self._chips,
            self._g1_label, self._g1_boxes, self._g1_outline,
            self._g2_label, self._g2_boxes, self._g2_outline,
            self._gen1, self._gen1_lbl, self._gen2, self._gen2_lbl,
            self._cut_line, self._arrow1, self._arrow2, self._note,
        )
        self.play(plan.animate.set_opacity(0.2))
        self.play(FadeOut(self.current_caption))
        self.current_caption = None

        baseline = Line([-3.6, -1.8, 0], [3.6, -1.8, 0], color=TEXT_COLOR, stroke_width=2)
        self.play(Create(baseline))

        scale = 3.6 / 1400
        left_kw, right_kw = 1350, 990

        left_h = left_kw * scale
        left_bar = Rectangle(width=1.4, height=left_h, fill_color=SECONDARY_COLOR,
                              fill_opacity=1, stroke_width=0)
        left_bar.move_to([-2.0, -1.8 + left_h / 2, 0])
        left_val = Tex(f"{left_kw:,} kW", font_size=30, color=TEXT_COLOR)
        left_val.next_to(left_bar, UP, buff=0.15)
        left_label = Tex("Previous approach", font_size=26, color=TEXT_COLOR)
        left_label.move_to([-2.0, -2.2, 0])

        right_h = right_kw * scale
        right_bar = Rectangle(width=1.4, height=right_h, fill_color=HL_COLOR,
                               fill_opacity=1, stroke_width=0)
        right_bar.move_to([2.0, -1.8 + right_h / 2, 0])
        right_val = Tex(f"{right_kw:,} kW", font_size=30, color=HL_COLOR)
        right_val.next_to(right_bar, UP, buff=0.15)
        right_label = Tex("Best design", font_size=26, color=TEXT_COLOR)
        right_label.move_to([2.0, -2.2, 0])

        self.play(GrowFromEdge(left_bar, DOWN), FadeIn(left_val), FadeIn(left_label))
        self.play(GrowFromEdge(right_bar, DOWN), FadeIn(right_val), FadeIn(right_label))

        cap = self.swap_caption("The worst-case load drops from 1,350 to 990 kW.")
        self.wait(1.0)

        arrow = CurvedArrow(left_bar.get_top() + UP * 0.2, right_bar.get_top() + UP * 0.2,
                             color=HL_COLOR, angle=-TAU / 6, stroke_width=3)
        self.play(Create(arrow))

        pct_label = Tex(f"$-${IMPROVEMENT_PCT}\\%", font_size=40, color=HL_COLOR)
        pct_label.move_to([0, 2.4, 0])
        self.play(GrowFromCenter(pct_label))

        note2 = Tex("load basis, before sizing margins", font_size=22, color=SECONDARY_COLOR)
        note2.move_to([6.3 - note2.width / 2, 2.4, 0])
        self.play(FadeIn(note2))

        cap2 = self.swap_caption("That is 26.7\\% less load for every UPS to be sized for.")
        self.wait(1.5)

        self.background_items = [plan, baseline]
        self.layout_items = [
            left_bar, left_val, left_label, right_bar, right_val, right_label,
            arrow, pct_label, note2, cap2,
        ]
        idx_left_bar = self.layout_items.index(left_bar)
        idx_right_bar = self.layout_items.index(right_bar)
        idx_arrow = self.layout_items.index(arrow)
        idx_left_val = self.layout_items.index(left_val)
        idx_right_val = self.layout_items.index(right_val)
        self.allowed_overlaps = {
            (idx_left_bar, idx_arrow), (idx_right_bar, idx_arrow),
            (idx_left_val, idx_arrow), (idx_right_val, idx_arrow),
        }
        self.check_layout("12_3")

        self.play(
            FadeOut(plan), FadeOut(baseline), FadeOut(left_bar), FadeOut(left_val),
            FadeOut(left_label), FadeOut(right_bar), FadeOut(right_val), FadeOut(right_label),
            FadeOut(arrow), FadeOut(pct_label), FadeOut(note2), FadeOut(cap2),
            run_time=1.0,
        )
        self.current_caption = None

    # ===================================================== Beat 12.4 =====
    def beat_12_4_lesson(self):
        t = title("The lesson")
        self.play(FadeIn(t, shift=DOWN * 0.15))

        def mini_stack(cx, cut):
            bars = VGroup()
            for i in range(8):
                y = 1.9 - 0.26 * i
                if i >= cut:
                    y -= 0.15
                name, kw, type_ = DEMO_ROWS[i]
                colour = GROUP1_COLOR if i < cut else GROUP2_COLOR
                bar = Rectangle(width=2.4, height=0.18, fill_color=colour, fill_opacity=0.6,
                                 stroke_color=ROW_STROKE, stroke_width=1)
                bar.move_to([cx, y, 0])
                bars.add(bar)
            cut_y = (bars[cut - 1].get_center()[1] + bars[cut].get_center()[1]) / 2
            line = Line([cx - 1.3, cut_y, 0], [cx + 1.3, cut_y, 0], color=TEXT_COLOR, stroke_width=2)
            return bars, line

        left_bars, left_cut_line = mini_stack(-3.3, MOST_BALANCED_CUT)
        right_bars, right_cut_line = mini_stack(3.3, OPT_CUT)

        left_header = Tex("Most even split", font_size=28, color=TEXT_COLOR)
        left_header.move_to([-3.3, 2.45, 0])
        right_header = Tex("Best split", font_size=28, color=TEXT_COLOR)
        right_header.move_to([3.3, 2.45, 0])

        self.play(
            FadeIn(left_header), FadeIn(left_bars), Create(left_cut_line),
        )
        self.play(
            FadeIn(right_header), FadeIn(right_bars), Create(right_cut_line),
        )

        g1_left, g2_left = GROUP_TOTALS[MOST_BALANCED_CUT]
        g1_right, g2_right = GROUP_TOTALS[OPT_CUT]

        left_totals = Tex(f"{g1_left:,} | {g2_left:,} kW", font_size=24, color=TEXT_COLOR)
        left_totals.move_to([-3.3, -0.6, 0])
        right_totals = Tex(f"{g1_right:,} | {g2_right:,} kW", font_size=24, color=TEXT_COLOR)
        right_totals.move_to([3.3, -0.6, 0])

        left_m = Tex("best M = 1{,}100", font_size=24, color=TEXT_COLOR)
        left_m.move_to([-3.3, -1.1, 0])
        right_m = MathTex("M", "=", "990", font_size=24)
        right_m.set_color(TEXT_COLOR)
        right_m.set_color_by_tex("990", HL_COLOR)
        right_m.move_to([3.3, -1.1, 0])

        self.play(FadeIn(left_totals), FadeIn(right_totals))
        self.play(FadeIn(left_m), FadeIn(right_m))

        cap = self.swap_caption("The most even split was not the best one.")
        self.wait(1.2)

        self.play(Indicate(left_m, color=HL_COLOR), Indicate(right_m, color=HL_COLOR))

        cap2 = self.swap_caption("Where to cut and which pairs to use must be decided together.")
        self.wait(2.0)

        self.layout_items = [
            t, left_header, left_bars, right_header, right_bars,
            left_totals, right_totals, left_m, right_m, cap2,
        ]
        self.background_items = [left_cut_line, right_cut_line]
        self.allowed_overlaps = set()
        self.check_layout("12_4")

        self.play(
            FadeOut(t), FadeOut(left_header), FadeOut(left_bars), FadeOut(left_cut_line),
            FadeOut(right_header), FadeOut(right_bars), FadeOut(right_cut_line),
            FadeOut(left_totals), FadeOut(right_totals), FadeOut(left_m), FadeOut(right_m),
            FadeOut(cap2),
            run_time=1.0,
        )
        self.current_caption = None

    # ===================================================== Beat 12.5 =====
    def beat_12_5_journey(self):
        t = title("The whole journey")
        self.play(FadeIn(t, shift=DOWN * 0.15))

        def chain(labels, y, font=24, arrow_len=0.5):
            boxes = VGroup()
            for lbl_text in labels:
                lbl = Tex(lbl_text, font_size=font, color=TEXT_COLOR)
                box = RoundedRectangle(width=lbl.width + 0.3, height=lbl.height + 0.25,
                                        corner_radius=0.08, stroke_color=SECONDARY_COLOR,
                                        stroke_width=2, fill_color=BG_COLOR, fill_opacity=0)
                lbl.move_to(box.get_center())
                boxes.add(VGroup(box, lbl))
            boxes.arrange(RIGHT, buff=arrow_len)
            boxes.move_to([0, y, 0])
            arrows = VGroup(*[
                Arrow(boxes[i].get_right(), boxes[i + 1].get_left(), buff=0.02,
                      stroke_width=2, color=SECONDARY_COLOR)
                for i in range(len(boxes) - 1)
            ])
            return boxes, arrows

        labels1 = ["Data hall", "Two decisions", "Score: M", "0/1 switches",
                   "Load equations", "One model"]
        labels2 = ["Relax", "Branch \\& Bound", "Proof", "Best design"]

        boxes1, arrows1 = chain(labels1, 1.6)
        if boxes1.width > 12.6:
            boxes1, arrows1 = chain(labels1, 1.6, font=22, arrow_len=0.35)

        boxes2, arrows2 = chain(labels2, 0.5)
        if boxes2.width > 12.6:
            boxes2, arrows2 = chain(labels2, 0.5, font=22, arrow_len=0.35)

        self.play(LaggedStart(*[FadeIn(b) for b in boxes1], lag_ratio=0.15), run_time=1.2)
        self.play(*[Create(a) for a in arrows1], run_time=0.6)

        cap = self.swap_caption("From a data hall to a proven best design.")
        self.wait(1.0)

        self.play(LaggedStart(*[FadeIn(b) for b in boxes2], lag_ratio=0.15), run_time=1.2)
        self.play(*[Create(a) for a in arrows2], run_time=0.6)

        link_arrow = CurvedArrow(boxes1[-1].get_bottom() + DOWN * 0.05,
                                  boxes2[0].get_top() + UP * 0.05,
                                  color=TEXT_COLOR, angle=-TAU / 8, stroke_width=2)
        self.play(Create(link_arrow))

        opt_line = MathTex(
            r"\text{Best found} = \text{Lower bound}", r"\;\Rightarrow\;", r"\text{Optimal}",
            font_size=40,
        )
        opt_line.set_color(TEXT_COLOR)
        opt_line.move_to([0, -0.9, 0])
        self.play(Write(opt_line))

        final_990 = Tex("990 kW", font_size=40, color=HL_COLOR)
        final_990.move_to([0, -1.8, 0])
        self.play(FadeIn(final_990))

        cap2 = self.swap_caption("When the best answer found meets the lower bound,")
        self.wait(0.8)
        cap2b = self.swap_caption("the answer is proven optimal.")
        self.wait(1.2)

        self.layout_items = [
            t, *boxes1, *boxes2, opt_line, final_990, cap2b,
        ]
        self.background_items = [*arrows1, *arrows2, link_arrow]
        self.allowed_overlaps = set()
        self.check_layout("12_5")

        self.play(
            FadeOut(t), FadeOut(boxes1), FadeOut(arrows1), FadeOut(boxes2), FadeOut(arrows2),
            FadeOut(link_arrow), FadeOut(opt_line), FadeOut(final_990), FadeOut(cap2b),
            run_time=1.0,
        )
        self.current_caption = None

        closing_title = Tex("HAC Load Designer", font_size=48, color=TEXT_COLOR)
        closing_title.move_to([0, 0.3, 0])
        closing_sub = Tex("grouping + pairing, solved and proven", font_size=26, color=SECONDARY_COLOR)
        closing_sub.move_to([0, -0.4, 0])
        self.play(FadeIn(closing_title), FadeIn(closing_sub))

        self.layout_items = [closing_title, closing_sub]
        self.allowed_overlaps = set()
        self.check_layout("12_end")

        self.wait(2.5)
        self.play(FadeOut(closing_title), FadeOut(closing_sub), run_time=1.5)
