"""Scene 02 -- "Grouping"

Built strictly from scene02_prompt.md + common_prompt.md.

Starts from: black (Scene 01 ended on "How should we group them?" -> black).
Ends with (handoff to Scene 03): black background, no title, no caption,
only the Row 1 block (row_block("Row 1", 500, "2-source")) centred at (0, 0).

Run with:
    manim -pqh scene02_grouping.py Scene02Grouping
"""
import numpy as np
from manim import *

from common.style import (
    BG_COLOR, TEXT_COLOR, SECONDARY_COLOR, HL_COLOR, CUT_COLOR,
    GROUP1_COLOR, GROUP2_COLOR, FAIL_COLOR,
)
from common.layout import caption, title, LayoutCheckMixin
from common.data import DEMO_ROWS, TOTAL_KW, GROUP_TOTALS, MOST_BALANCED_CUT, fmt_kw
from common.widgets import row_block, group_frame, cut_line, power_train

ROW_WIDTH = 5.0
ROW_HEIGHT = 0.46
ROW_FONT = 24
ROW_X = -1.8
ROW_PITCH = 0.58
ROW_TOP_Y = 2.35
GROUP_GAP = 0.40


class Scene02Grouping(LayoutCheckMixin, Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        self.current_caption = None
        self.current_title = None

        self.rows = [
            row_block(name, kw, type_, width=ROW_WIDTH, height=ROW_HEIGHT, font=ROW_FONT)
            for name, kw, type_ in DEMO_ROWS
        ]
        for row in self.rows:
            row.move_to([ROW_X, ROW_TOP_Y, 0])  # placeholder, positioned per-beat

        self.beat_2_1_example()
        self.beat_2_2_task()
        self.beat_2_3_what_is_a_group()
        self.beat_2_4_continuous()
        self.beat_2_5_where_to_cut()
        self.beat_2_6_worst_group()

    # --------------------------------------------------------- helpers ---
    def swap_caption(self, text):
        new_cap = caption(text)
        if self.current_caption is not None:
            self.play(FadeOut(self.current_caption))
        self.play(FadeIn(new_cap))
        self.current_caption = new_cap
        return new_cap

    def stack_positions(self, cut=None):
        positions = []
        for k in range(1, 9):
            y = ROW_TOP_Y - ROW_PITCH * (k - 1)
            if cut is not None and k > cut:
                y -= GROUP_GAP
            positions.append(np.array([ROW_X, y, 0]))
        return positions

    def frame_row_overlaps(self, layout_items, frame, row_indices):
        idx_frame = layout_items.index(frame)
        return {(i, idx_frame) for i in row_indices}

    def cut_line_y(self, cut):
        positions = self.stack_positions(cut)
        row_c_bottom = positions[cut - 1][1] - ROW_HEIGHT / 2
        row_c1_top = positions[cut][1] + ROW_HEIGHT / 2
        return (row_c_bottom + row_c1_top) / 2

    def split_extras(self, cut):
        """Build cut line, cut label, group frames, titles, power-train
        cards and feed arrows for the current (already-moved) row positions
        at this cut. Rows must already be at self.stack_positions(cut)."""
        y_line = self.cut_line_y(cut)

        line = cut_line(length=5.3)
        line.move_to([-1.7, y_line, 0])

        label = Tex("cut", font_size=24, color=CUT_COLOR)
        label.move_to([1.15 + label.width / 2, y_line, 0])

        g1_rows = VGroup(*self.rows[:cut])
        g2_rows = VGroup(*self.rows[cut:])
        frame1 = group_frame(g1_rows, GROUP1_COLOR, buff=0.1)
        frame2 = group_frame(g2_rows, GROUP2_COLOR, buff=0.1)

        title1 = Tex("Group 1", font_size=26, color=GROUP1_COLOR)
        title1.move_to([-4.55 - title1.width / 2, frame1.get_center()[1], 0])
        title2 = Tex("Group 2", font_size=26, color=GROUP2_COLOR)
        title2.move_to([-4.55 - title2.width / 2, frame2.get_center()[1], 0])

        card1 = power_train(GROUP1_COLOR)
        card1.move_to([4.1, frame1.get_center()[1], 0])
        card2 = power_train(GROUP2_COLOR)
        card2.move_to([4.1, frame2.get_center()[1], 0])

        arrow1 = Arrow([2.55, frame1.get_center()[1], 0], [0.95, frame1.get_center()[1], 0],
                       stroke_width=3, color=GROUP1_COLOR, buff=0)
        arrow2 = Arrow([2.55, frame2.get_center()[1], 0], [0.95, frame2.get_center()[1], 0],
                       stroke_width=3, color=GROUP2_COLOR, buff=0)

        return dict(line=line, label=label, frame1=frame1, frame2=frame2,
                    title1=title1, title2=title2, card1=card1, card2=card2,
                    arrow1=arrow1, arrow2=arrow2)

    # ===================================================== Beat 2.1 =====
    def beat_2_1_example(self):
        t = title("A small example")
        self.current_title = t
        self.play(FadeIn(t, shift=DOWN * 0.15), run_time=0.6)

        positions = self.stack_positions(None)
        first_four = self.rows[:4]
        for row, pos in zip(first_four, positions[:4]):
            row.move_to(pos)

        self.play(
            LaggedStart(*[FadeIn(r, shift=DOWN * 0.15) for r in first_four], lag_ratio=0.3),
            run_time=1.2,
        )
        cap = self.swap_caption("Here are the four rows from before...")
        self.wait(1.0)

        last_four = self.rows[4:]
        for row, pos in zip(last_four, positions[4:]):
            row.move_to(pos)
        self.play(
            LaggedStart(*[FadeIn(r, shift=DOWN * 0.15) for r in last_four], lag_ratio=0.3),
            run_time=1.2,
        )
        cap2 = self.swap_caption("...plus four more: a small hall with eight rows.")
        self.wait(1.0)

        self.layout_items = [t, *self.rows, cap2]
        self.allowed_overlaps = set()
        self.check_layout("2_1")

    # ===================================================== Beat 2.2 =====
    def beat_2_2_task(self):
        total_lbl = Tex("Total load", font_size=30, color=TEXT_COLOR).move_to([4.1, 1.2, 0])
        kw_lbl = Tex(fmt_kw(TOTAL_KW), font_size=44, color=TEXT_COLOR).move_to([4.1, 0.5, 0])
        into_lbl = Tex("into 2 groups", font_size=30, color=TEXT_COLOR).move_to([4.1, -0.3, 0])

        self.play(FadeIn(total_lbl), run_time=0.4)
        self.play(FadeIn(kw_lbl), run_time=0.4)
        self.play(FadeIn(into_lbl), run_time=0.4)

        cap = self.swap_caption("We need to split them into two groups.")
        self.wait(1.2)

        self.layout_items = [self.current_title, *self.rows, total_lbl, kw_lbl, into_lbl, cap]
        self.allowed_overlaps = set()
        self.check_layout("2_2")

        self._right_panel_2_2 = VGroup(total_lbl, kw_lbl, into_lbl)

    # ===================================================== Beat 2.3 =====
    def beat_2_3_what_is_a_group(self):
        self.play(FadeOut(self._right_panel_2_2))
        self.play(FadeOut(self.current_title))
        self.current_title = None

        cut = 4
        positions = self.stack_positions(cut)
        self.play(*[row.animate.move_to(pos) for row, pos in zip(self.rows, positions)],
                   run_time=1.0)

        extras = self.split_extras(cut)
        self.play(Create(extras["line"]), FadeIn(extras["label"]), run_time=0.8)
        self.play(Create(extras["frame1"]), Create(extras["frame2"]), run_time=0.8)
        self.play(FadeIn(extras["title1"]), FadeIn(extras["title2"]), run_time=0.4)

        cap = self.swap_caption("We split the rows into groups.")
        self.wait(1.0)

        self.play(FadeIn(extras["card1"]), run_time=0.5)
        self.play(FadeIn(extras["card2"]), run_time=0.5)
        self.play(GrowArrow(extras["arrow1"]), run_time=0.6)
        self.play(GrowArrow(extras["arrow2"]), run_time=0.6)

        dot1 = Dot(extras["arrow1"].get_start(), radius=0.05, color=GROUP1_COLOR)
        dot2 = Dot(extras["arrow2"].get_start(), radius=0.05, color=GROUP2_COLOR)
        self.play(FadeIn(dot1), FadeIn(dot2))
        self.play(dot1.animate.move_to(extras["arrow1"].get_end()),
                   dot2.animate.move_to(extras["arrow2"].get_end()), run_time=0.6)
        self.play(FadeOut(dot1), FadeOut(dot2))

        cap2 = self.swap_caption(
            "Each group has its own generator and its own UPS A, B, C, D."
        )
        self.wait(2.0)

        self.layout_items = [
            *self.rows, extras["line"], extras["label"],
            extras["frame1"], extras["frame2"], extras["title1"], extras["title2"],
            extras["card1"], extras["card2"], extras["arrow1"], extras["arrow2"], cap2,
        ]
        self.allowed_overlaps = (
            self.frame_row_overlaps(self.layout_items, extras["frame1"], range(0, 4))
            | self.frame_row_overlaps(self.layout_items, extras["frame2"], range(4, 8))
        )
        self.check_layout("2_3")

        self.play(
            FadeOut(extras["line"]), FadeOut(extras["label"]),
            FadeOut(extras["frame1"]), FadeOut(extras["frame2"]),
            FadeOut(extras["title1"]), FadeOut(extras["title2"]),
            FadeOut(extras["card1"]), FadeOut(extras["card2"]),
            FadeOut(extras["arrow1"]), FadeOut(extras["arrow2"]),
        )
        plain_positions = self.stack_positions(None)
        self.play(*[row.animate.move_to(pos) for row, pos in zip(self.rows, plain_positions)],
                   run_time=0.8)

    # ===================================================== Beat 2.4 =====
    def beat_2_4_continuous(self):
        row1, row2, row3 = self.rows[0], self.rows[1], self.rows[2]

        outline1 = SurroundingRectangle(row1, color=GROUP1_COLOR, buff=0.04, stroke_width=3)
        outline3 = SurroundingRectangle(row3, color=GROUP1_COLOR, buff=0.04, stroke_width=3)
        self.play(Create(outline1), Create(outline3), row2.animate.set_opacity(0.4), run_time=0.6)

        start = np.array([-4.3, row1.get_center()[1], 0])
        end = np.array([-4.3, row3.get_center()[1], 0])
        connector = ArcBetweenPoints(start, end, angle=-TAU / 6, color=GROUP1_COLOR, stroke_width=3)
        if connector.get_left()[0] < -6.0:
            connector = ArcBetweenPoints(start, end, angle=-TAU / 10, color=GROUP1_COLOR, stroke_width=3)
        self.play(Create(connector), run_time=0.7)

        left_pt = connector.get_left()
        cross = VGroup(
            Line(left_pt + UP * 0.15 + LEFT * 0.15, left_pt + DOWN * 0.15 + RIGHT * 0.15,
                 color=FAIL_COLOR, stroke_width=5),
            Line(left_pt + DOWN * 0.15 + LEFT * 0.15, left_pt + UP * 0.15 + RIGHT * 0.15,
                 color=FAIL_COLOR, stroke_width=5),
        )
        self.play(Create(cross), run_time=0.4)

        not_allowed = Tex(r"$\times$ Not allowed", font_size=30, color=FAIL_COLOR)
        not_allowed.move_to([4.1, 1.77, 0])
        skip_lbl = Tex("Row 1 and Row 3 skip Row 2", font_size=24, color=SECONDARY_COLOR)
        skip_lbl.move_to([4.1, 1.30, 0])
        self.play(FadeIn(not_allowed), FadeIn(skip_lbl), run_time=0.5)

        cap = self.swap_caption("A group must be a continuous run of rows --- no skipping.")
        self.wait(1.5)

        self.layout_items = [*self.rows, outline1, outline3, connector, cross,
                              not_allowed, skip_lbl, cap]
        idx_row1 = self.layout_items.index(self.rows[0])
        idx_row2 = self.layout_items.index(self.rows[1])
        idx_row3 = self.layout_items.index(self.rows[2])
        idx_connector = self.layout_items.index(connector)
        self.allowed_overlaps = {
            (self.layout_items.index(outline1), idx_row1),
            (self.layout_items.index(outline3), idx_row3),
            (self.layout_items.index(cross), idx_connector),
            (idx_connector, idx_row1),
            (idx_connector, idx_row2),
            (idx_connector, idx_row3),
            (idx_row2, idx_connector),
        }
        idx_cross = self.layout_items.index(cross)
        idx_outline1 = self.layout_items.index(outline1)
        idx_outline3 = self.layout_items.index(outline3)
        self.allowed_overlaps |= {
            (idx_cross, idx_row1), (idx_cross, idx_row2), (idx_cross, idx_row3),
            (idx_outline1, idx_connector), (idx_outline3, idx_connector),
        }
        self.check_layout("2_4a")

        self.play(
            FadeOut(outline1), FadeOut(outline3), FadeOut(connector), FadeOut(cross),
            FadeOut(not_allowed), FadeOut(skip_lbl),
            row2.animate.set_opacity(1),
        )

        cut = 3
        positions = self.stack_positions(cut)
        self.play(*[row.animate.move_to(pos) for row, pos in zip(self.rows, positions)],
                   run_time=0.8)
        frame = group_frame(VGroup(*self.rows[:cut]), GROUP1_COLOR, buff=0.1)
        self.play(Create(frame), run_time=0.6)

        allowed_lbl = Tex(r"$\checkmark$ Allowed", font_size=30, color=TEXT_COLOR)
        allowed_lbl.move_to([4.1, 1.77, 0])
        sit_lbl = Tex("Rows 1, 2, 3 sit side by side", font_size=24, color=SECONDARY_COLOR)
        if sit_lbl.width > 4.8:
            sit_lbl = Tex("Rows 1, 2, 3 sit side by side", font_size=22, color=SECONDARY_COLOR)
        sit_lbl.move_to([4.1, 1.30, 0])
        self.play(FadeIn(allowed_lbl), FadeIn(sit_lbl), run_time=0.5)

        cap2 = self.swap_caption("That matches how the rows sit in the hall.")
        self.wait(1.2)

        self.layout_items = [*self.rows, frame, allowed_lbl, sit_lbl, cap2]
        self.allowed_overlaps = self.frame_row_overlaps(self.layout_items, frame, range(0, 3))
        self.check_layout("2_4b")

        self.play(FadeOut(frame), FadeOut(allowed_lbl), FadeOut(sit_lbl))
        plain_positions = self.stack_positions(None)
        self.play(*[row.animate.move_to(pos) for row, pos in zip(self.rows, plain_positions)],
                   run_time=0.6)

    # ===================================================== Beat 2.5 =====
    def right_panel_for_cut(self, k):
        g1, g2 = GROUP_TOTALS[k]
        header = Tex(f"Cut after Row {k}", font_size=30, color=TEXT_COLOR)
        header.move_to([4.1, 2.2, 0])

        g1_lbl = Tex("Group 1", font_size=28, color=GROUP1_COLOR)
        g1_lbl.move_to([2.3 + g1_lbl.width / 2, 1.3, 0])
        g1_val = Tex(fmt_kw(g1), font_size=28, color=GROUP1_COLOR)
        g1_val.move_to([5.9 - g1_val.width / 2, 1.3, 0])

        g2_lbl = Tex("Group 2", font_size=28, color=GROUP2_COLOR)
        g2_lbl.move_to([2.3 + g2_lbl.width / 2, 0.6, 0])
        g2_val = Tex(fmt_kw(g2), font_size=28, color=GROUP2_COLOR)
        g2_val.move_to([5.9 - g2_val.width / 2, 0.6, 0])

        bar1_w = g1 * 3.6 / 4000
        bar2_w = g2 * 3.6 / 4000
        bar1 = Rectangle(width=bar1_w, height=0.3, fill_color=GROUP1_COLOR, fill_opacity=0.7,
                          stroke_width=0)
        bar1.move_to([2.3 + bar1_w / 2, -0.3, 0])
        bar2 = Rectangle(width=bar2_w, height=0.3, fill_color=GROUP2_COLOR, fill_opacity=0.7,
                          stroke_width=0)
        bar2.move_to([2.3 + bar2_w / 2, -0.8, 0])

        return dict(header=header, g1_lbl=g1_lbl, g1_val=g1_val,
                    g2_lbl=g2_lbl, g2_val=g2_val, bar1=bar1, bar2=bar2)

    def beat_2_5_where_to_cut(self):
        cut = 1
        positions = self.stack_positions(cut)
        self.play(*[row.animate.move_to(pos) for row, pos in zip(self.rows, positions)],
                   run_time=0.5)

        y_line = self.cut_line_y(cut)
        line = cut_line(length=5.3).move_to([-1.7, y_line, 0])
        label = Tex("cut", font_size=24, color=CUT_COLOR)
        label.move_to([1.15 + label.width / 2, y_line, 0])
        self.play(Create(line), FadeIn(label), run_time=0.4)

        panel = self.right_panel_for_cut(cut)
        panel_group = VGroup(*panel.values())
        self.play(FadeIn(panel_group), run_time=0.4)

        cap = self.swap_caption("There are seven places to cut.")

        for k in range(2, 8):
            new_positions = self.stack_positions(k)
            new_y_line = self.cut_line_y(k)
            new_panel = self.right_panel_for_cut(k)

            anims = [row.animate.move_to(pos) for row, pos in zip(self.rows, new_positions)]
            anims += [
                line.animate.move_to([-1.7, new_y_line, 0]),
                label.animate.move_to([1.15 + label.width / 2, new_y_line, 0]),
                Transform(panel["header"], new_panel["header"]),
                Transform(panel["g1_val"], new_panel["g1_val"]),
                Transform(panel["g2_val"], new_panel["g2_val"]),
                Transform(panel["bar1"], new_panel["bar1"]),
                Transform(panel["bar2"], new_panel["bar2"]),
            ]
            self.play(*anims, run_time=0.7)
            self.wait(0.35)

        final_cut = MOST_BALANCED_CUT
        final_positions = self.stack_positions(final_cut)
        final_y_line = self.cut_line_y(final_cut)
        final_panel = self.right_panel_for_cut(final_cut)
        self.play(
            *[row.animate.move_to(pos) for row, pos in zip(self.rows, final_positions)],
            line.animate.move_to([-1.7, final_y_line, 0]),
            label.animate.move_to([1.15 + label.width / 2, final_y_line, 0]),
            Transform(panel["header"], final_panel["header"]),
            Transform(panel["g1_val"], final_panel["g1_val"]),
            Transform(panel["g2_val"], final_panel["g2_val"]),
            Transform(panel["bar1"], final_panel["bar1"]),
            Transform(panel["bar2"], final_panel["bar2"]),
            run_time=1.0,
        )

        tag = Tex("most balanced", font_size=26, color=TEXT_COLOR)
        tag.move_to([4.1, -1.6, 0])
        self.play(FadeIn(tag), run_time=0.4)
        self.play(Indicate(panel["g1_val"], color=HL_COLOR), Indicate(panel["g2_val"], color=HL_COLOR))

        cap2 = self.swap_caption("Cutting after Row 4 splits the load most evenly.")
        self.wait(1.2)
        cap3 = self.swap_caption("But is it the best cut?")
        self.wait(1.5)

        self.layout_items = [
            *self.rows, line, label, panel["header"], panel["g1_lbl"], panel["g1_val"],
            panel["g2_lbl"], panel["g2_val"], panel["bar1"], panel["bar2"], tag, cap3,
        ]
        self.allowed_overlaps = set()
        self.check_layout("2_5")

        self._panel_2_5 = VGroup(panel["header"], panel["g1_lbl"], panel["g1_val"],
                                  panel["g2_lbl"], panel["g2_val"], panel["bar1"],
                                  panel["bar2"], tag)
        self._line_2_5 = line
        self._label_2_5 = label

    # ===================================================== Beat 2.6 =====
    def beat_2_6_worst_group(self):
        self.play(FadeOut(self._panel_2_5))

        cut = MOST_BALANCED_CUT
        extras = self.split_extras(cut)
        line = self._line_2_5
        label = self._label_2_5

        self.play(
            Create(extras["frame1"]), Create(extras["frame2"]),
            FadeIn(extras["title1"]), FadeIn(extras["title2"]),
            FadeIn(extras["card1"]), FadeIn(extras["card2"]),
            GrowArrow(extras["arrow1"]), GrowArrow(extras["arrow2"]),
            run_time=0.8,
        )

        mid_y = (extras["card1"].get_bottom()[1] + extras["card2"].get_top()[1]) / 2
        same_size = Tex("same UPS size", font_size=26, color=TEXT_COLOR)
        same_size.move_to([4.1, mid_y, 0])
        self.play(FadeIn(same_size), run_time=0.4)

        self.play(
            Indicate(extras["card1"].ups_row, scale_factor=1.1),
            Indicate(extras["card2"].ups_row, scale_factor=1.1),
        )

        cap = self.swap_caption(
            "Every group uses the same UPS size, so the worst group sets it for all."
        )
        self.wait(2.0)

        self.layout_items = [
            *self.rows, line, label, extras["frame1"], extras["frame2"],
            extras["title1"], extras["title2"], extras["card1"], extras["card2"],
            extras["arrow1"], extras["arrow2"], same_size, cap,
        ]
        self.allowed_overlaps = (
            self.frame_row_overlaps(self.layout_items, extras["frame1"], range(0, 4))
            | self.frame_row_overlaps(self.layout_items, extras["frame2"], range(4, 8))
        )
        self.check_layout("2_6")

        cap2 = self.swap_caption("To find the worst group, we look inside one group.")
        self.wait(1.2)

        row1 = self.rows[0]
        others = VGroup(*self.rows[1:])
        self.play(
            FadeOut(others), FadeOut(line), FadeOut(label),
            FadeOut(extras["frame1"]), FadeOut(extras["frame2"]),
            FadeOut(extras["title1"]), FadeOut(extras["title2"]),
            FadeOut(extras["card1"]), FadeOut(extras["card2"]),
            FadeOut(extras["arrow1"]), FadeOut(extras["arrow2"]),
            FadeOut(same_size), FadeOut(cap2),
            run_time=0.8,
        )
        self.current_caption = None

        self.play(row1.animate.move_to([0, 0, 0]), run_time=1.0)
        self.wait(0.5)

        self.layout_items = [row1]
        self.allowed_overlaps = set()
        self.check_layout("2_end")
