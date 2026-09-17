"""Scene 04 -- "Judging one solution"

Built strictly from scene04_prompt.md + common_prompt.md.

Starts from: black (Scene 03 ended on "Two decisions -- and we must make
them together." then faded to black).

Ends with: fade to black after `min M` has been shown.

Run with:
    manim -pqh scene04_judge_solution.py Scene04JudgeSolution
"""
import numpy as np
from manim import *

from common.style import (
    BG_COLOR, TEXT_COLOR, SECONDARY_COLOR, UPS_COLORS, UPS_NAMES,
    HL_COLOR, GROUP1_COLOR, GROUP2_COLOR, CUT_COLOR,
)
from common.layout import caption, title, LayoutCheckMixin
from common.data import DEMO_ROWS, GROUP_TOTALS, SOLUTION_A, FAULT_TABLE_A_G2, \
    FAULT_TABLE_A_G2_CONTRIBUTIONS_A_FAILS, fmt_kw
from common.widgets import row_block, pair_chip, group_frame, cut_line, ups_box, fail_anims

ROW_X_OVERVIEW = -2.6
ROW_WIDTH_OVERVIEW = 4.4
ROW_HEIGHT_OVERVIEW = 0.46
ROW_FONT_OVERVIEW = 24
ROW_PITCH = 0.58
ROW_TOP_Y = 2.35
GROUP_GAP = 0.40
CUT_AFTER = 4


def row_letter(name):
    return name.split()[-1]


class Scene04JudgeSolution(LayoutCheckMixin, Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        self.current_caption = None

        self.beat_4_1_previous_approach()
        self.beat_4_2_one_failure()
        self.beat_4_3_every_failure()
        self.beat_4_4_define_m()
        self.beat_4_5_goal()

    # --------------------------------------------------------- helpers ---
    def swap_caption(self, text):
        new_cap = caption(text)
        if self.current_caption is not None:
            self.play(FadeOut(self.current_caption))
        self.play(FadeIn(new_cap))
        self.current_caption = new_cap
        return new_cap

    def stack_positions(self, cut=CUT_AFTER):
        positions = []
        for k in range(1, 9):
            y = ROW_TOP_Y - ROW_PITCH * (k - 1)
            if k > cut:
                y -= GROUP_GAP
            positions.append(np.array([ROW_X_OVERVIEW, y, 0]))
        return positions

    def pair_for_row(self, idx):
        """idx is 0-based row index (0 = Row 1)."""
        name, kw, type_ = DEMO_ROWS[idx]
        if type_ == "4-source":
            return "ABCD"
        return SOLUTION_A["pairs"][name]

    def pair_letters(self, pair, font=26):
        if pair == "ABCD":
            return Tex("ABCD", font_size=font, color=SECONDARY_COLOR)
        parts = [Tex(l, font_size=font, color=UPS_COLORS[l]) for l in pair]
        return VGroup(*parts).arrange(RIGHT, buff=0.03)

    def contribution_line(self, prefix, fragments, tag_tex, font=22):
        """fragments: list of (text, color). tag_tex: MathTex source."""
        prefix_txt = Tex(prefix, font_size=font, color=TEXT_COLOR)
        frag_txts = [Tex(txt, font_size=font, color=color) for txt, color in fragments]
        tag = MathTex(tag_tex, font_size=font, color=SECONDARY_COLOR)
        line = VGroup(prefix_txt, *frag_txts, tag).arrange(RIGHT, buff=0.08)
        return line

    # ===================================================== Beat 4.1 =====
    def beat_4_1_previous_approach(self):
        t = Tex("Solution A --- the previous approach", font_size=44, color=TEXT_COLOR)
        if t.width > 12.5:
            t = Tex("Solution A --- the previous approach", font_size=40, color=TEXT_COLOR)
        t.move_to([0, 3.15, 0])
        self.play(FadeIn(t, shift=DOWN * 0.15))

        positions = self.stack_positions(CUT_AFTER)
        self.rows = []
        for i, (name, kw, type_) in enumerate(DEMO_ROWS):
            row = row_block(name, kw, type_, width=ROW_WIDTH_OVERVIEW,
                             height=ROW_HEIGHT_OVERVIEW, font=ROW_FONT_OVERVIEW)
            row.move_to(positions[i])
            self.rows.append(row)

        self.play(LaggedStart(*[FadeIn(r) for r in self.rows], lag_ratio=0.15), run_time=1.6)

        row_c_bottom = positions[CUT_AFTER - 1][1] - ROW_HEIGHT_OVERVIEW / 2
        row_c1_top = positions[CUT_AFTER][1] + ROW_HEIGHT_OVERVIEW / 2
        y_line = (row_c_bottom + row_c1_top) / 2
        line = cut_line(length=4.7)
        line.move_to([ROW_X_OVERVIEW, y_line, 0])

        frame1 = group_frame(VGroup(*self.rows[:4]), GROUP1_COLOR, buff=0.1)
        frame2 = group_frame(VGroup(*self.rows[4:]), GROUP2_COLOR, buff=0.1)
        title1 = Tex("Group 1", font_size=26, color=GROUP1_COLOR)
        title1.move_to([-4.95 - title1.width / 2, frame1.get_center()[1], 0])
        title2 = Tex("Group 2", font_size=26, color=GROUP2_COLOR)
        title2.move_to([-4.95 - title2.width / 2, frame2.get_center()[1], 0])

        self.play(Create(line), Create(frame1), Create(frame2), FadeIn(title1), FadeIn(title2))

        cap = self.swap_caption("Let's score one complete answer: the previous approach.")
        self.wait(1.0)

        g1, g2 = GROUP_TOTALS[CUT_AFTER]
        line1 = Tex("Cut: most balanced", font_size=26, color=TEXT_COLOR)
        line1.move_to([1.6 + line1.width / 2, 1.6, 0])
        line2 = Tex(f"{fmt_kw(g1)} | {fmt_kw(g2)}", font_size=26, color=SECONDARY_COLOR)
        line2.move_to([1.6 + line2.width / 2, 1.1, 0])
        self.play(FadeIn(line1), FadeIn(line2))

        cap2 = self.swap_caption("It cuts where the load is most balanced...")
        self.wait(1.0)

        line3 = Tex("Pairs: fixed rotation", font_size=26, color=TEXT_COLOR)
        line3.move_to([1.6 + line3.width / 2, 0.1, 0])
        rotation_parts = []
        for pair in ["AB", "CD", "AC"]:
            rotation_parts.append(self.pair_letters(pair, font=26))
            rotation_parts.append(Tex(r"$\to$", font_size=26, color=SECONDARY_COLOR))
        rotation_parts.append(Tex(r"$\dots$", font_size=26, color=SECONDARY_COLOR))
        line4 = VGroup(*rotation_parts).arrange(RIGHT, buff=0.12)
        line4.move_to([1.6 + line4.width / 2, -0.4, 0])
        self.play(FadeIn(line3))
        self.play(FadeIn(line4))

        chips = {}
        chip_order = ["Row 1", "Row 3", "Row 4", "Row 5", "Row 7", "Row 8"]
        for name in chip_order:
            idx = int(name.split()[-1]) - 1
            pair = self.pair_for_row(idx)
            chip = pair_chip(pair, font=24)
            chip.move_to([-0.1 + chip.width / 2, self.rows[idx].get_center()[1], 0])
            chips[name] = chip
            self.play(FadeIn(chip), run_time=0.35)

        chip2 = pair_chip("ABCD", font=24)
        chip2.move_to([-0.1 + chip2.width / 2, self.rows[1].get_center()[1], 0])
        chip6 = pair_chip("ABCD", font=24)
        chip6.move_to([-0.1 + chip6.width / 2, self.rows[5].get_center()[1], 0])
        chips["Row 2"] = chip2
        chips["Row 6"] = chip6
        self.play(FadeIn(chip2), FadeIn(chip6))

        cap3 = self.swap_caption("...then gives the 2-source rows pairs in a fixed rotation.")
        self.wait(1.5)

        self.layout_items = [
            t, *self.rows, line, frame1, frame2, title1, title2,
            line1, line2, line3, line4, *chips.values(), cap3,
        ]
        idx_frame1 = self.layout_items.index(frame1)
        idx_frame2 = self.layout_items.index(frame2)
        self.allowed_overlaps = (
            {(self.layout_items.index(self.rows[i]), idx_frame1) for i in range(4)}
            | {(self.layout_items.index(self.rows[i]), idx_frame2) for i in range(4, 8)}
        )
        self.check_layout("4_1")

        self._overview = dict(
            title=t, line=line, frame1=frame1, frame2=frame2,
            title1=title1, title2=title2, line1=line1, line2=line2,
            line3=line3, line4=line4, chips=chips,
        )

    # ===================================================== Beat 4.2 =====
    def beat_4_2_one_failure(self):
        ov = self._overview
        self.play(
            FadeOut(ov["title"]), FadeOut(ov["line1"]), FadeOut(ov["line2"]),
            FadeOut(ov["line3"]), FadeOut(ov["line4"]), FadeOut(ov["line"]),
            FadeOut(VGroup(*self.rows[:4])), FadeOut(ov["frame1"]), FadeOut(ov["title1"]),
            *[FadeOut(ov["chips"][f"Row {i}"]) for i in (1, 2, 3, 4)],
            run_time=0.6,
        )
        self.play(FadeOut(self.current_caption))
        self.current_caption = None

        # -- transform Group 2 rows + chips + frame + title into the detail layout ---
        detail_ys = [1.6, 0.9, 0.2, -0.5]
        detail_rows = []
        for i, y in zip(range(4, 8), detail_ys):
            name, kw, type_ = DEMO_ROWS[i]
            new_row = row_block(name, kw, type_, width=3.8, height=0.5, font=24)
            new_row.move_to([-4.0, y, 0])
            detail_rows.append(new_row)

        detail_chips = {}
        for i, y in zip(range(4, 8), detail_ys):
            name = DEMO_ROWS[i][0]
            pair = self.pair_for_row(i)
            chip = pair_chip(pair, font=24)
            chip.move_to([-1.95 + chip.width / 2, y, 0])
            detail_chips[name] = chip

        self.play(
            *[Transform(self.rows[4 + j], detail_rows[j]) for j in range(4)],
            *[Transform(ov["chips"][f"Row {i}"], detail_chips[f"Row {i}"]) for i in (5, 6, 7, 8)],
            run_time=1.0,
        )

        detail_frame = group_frame(
            VGroup(*self.rows[4:], *[ov["chips"][f"Row {i}"] for i in (5, 6, 7, 8)]),
            GROUP2_COLOR, buff=0.1,
        )
        self.play(Transform(ov["frame2"], detail_frame), run_time=0.6)

        detail_title = Tex("Group 2", font_size=28, color=GROUP2_COLOR)
        detail_title.move_to([-3.9, 2.3, 0])
        self.play(Transform(ov["title2"], detail_title), run_time=0.4)

        # -- header: small failed UPS A + label ---
        header_ups = ups_box("A", w=0.5, h=0.4, font=22, short=True)
        header_ups.move_to([1.7, 2.5, 0])
        header_lbl = Tex("UPS A fails", font_size=30, color=TEXT_COLOR)
        header_lbl.move_to([2.2 + header_lbl.width / 2, 2.5, 0])
        self.play(FadeIn(header_ups), FadeIn(header_lbl))
        self.play(*fail_anims(header_ups), run_time=0.6)

        # -- empty bar chart: baseline + letters ---
        baseline = Line([0.8, -1.9, 0], [6.0, -1.9, 0], color=SECONDARY_COLOR, stroke_width=2)
        bar_xs = {"B": 1.6, "C": 3.4, "D": 5.2}
        letters = VGroup(*[
            Tex(l, font_size=26, color=UPS_COLORS[l]).move_to([bar_xs[l], -2.2, 0])
            for l in ("B", "C", "D")
        ])
        self.play(Create(baseline), FadeIn(letters))

        cap = self.swap_caption("Take Group 2, and let UPS A fail.")
        self.wait(1.0)

        # -- build the stacked bars row by row ---
        SCALE = 3.6 / 1400
        bar_width = 1.0
        segments = {"B": VGroup(), "C": VGroup(), "D": VGroup()}
        heights = {"B": 0.0, "C": 0.0, "D": 0.0}
        totals_lbl = {}
        log_lines = VGroup()

        row_specs = [
            ("Row 5", "Row 5 (AB): ", [("B +300", UPS_COLORS["B"])], r"\times 1"),
            ("Row 6", "Row 6 (4-source): ", [("B", UPS_COLORS["B"]), (", ", SECONDARY_COLOR),
                                              ("C", UPS_COLORS["C"]), (", ", SECONDARY_COLOR),
                                              ("D", UPS_COLORS["D"]), (" +150", TEXT_COLOR)],
             r"\times\tfrac{1}{3}"),
            ("Row 7", "Row 7 (CD): ", [("C +400", UPS_COLORS["C"]), (", ", SECONDARY_COLOR),
                                        ("D +400", UPS_COLORS["D"])], r"\times\tfrac{1}{2}"),
            ("Row 8", "Row 8 (AC): ", [("C +800", UPS_COLORS["C"])], r"\times 1"),
        ]
        log_ys = [-1.25, -1.60, -1.95, -2.30]

        outline = None
        row_index_map = {"Row 5": 4, "Row 6": 5, "Row 7": 6, "Row 8": 7}
        for (row_name, prefix, frags, tag_tex), y in zip(row_specs, log_ys):
            row_idx = row_index_map[row_name]
            new_outline = SurroundingRectangle(self.rows[row_idx], color=TEXT_COLOR, buff=0.04)
            if outline is None:
                outline = new_outline
                self.play(Create(outline))
            else:
                self.play(Transform(outline, new_outline))

            log_line = self.contribution_line(prefix, frags, tag_tex, font=22)
            log_line.move_to([-6.0 + log_line.width / 2, y, 0])
            self.play(FadeIn(log_line))
            log_lines.add(log_line)

            contrib = FAULT_TABLE_A_G2_CONTRIBUTIONS_A_FAILS[row_name]["to"]
            seg_anims = []
            new_segments = []
            for letter, val in contrib.items():
                bottom = heights[letter] * SCALE
                seg_h = val * SCALE
                seg = Rectangle(width=bar_width, height=seg_h, fill_color=UPS_COLORS[letter],
                                 fill_opacity=1, stroke_color=BG_COLOR, stroke_width=2)
                seg.move_to([bar_xs[letter], -1.9 + bottom + seg_h / 2, 0])
                seg_val = Tex(fmt_kw(val), font_size=22, color=BG_COLOR)
                seg_val.move_to(seg.get_center())
                seg_grp = VGroup(seg, seg_val)
                seg_anims.append(GrowFromEdge(seg_grp, DOWN))
                segments[letter].add(seg_grp)
                new_segments.append((letter, seg_grp))
                heights[letter] += val
            self.play(*seg_anims, run_time=0.9)

            total_anims = []
            for letter in ("B", "C", "D"):
                new_total = Tex(fmt_kw(heights[letter]), font_size=26, color=UPS_COLORS[letter])
                bar_top_y = -1.9 + heights[letter] * SCALE
                new_total.move_to([bar_xs[letter], bar_top_y + 0.1 + new_total.height / 2, 0])
                if letter in totals_lbl:
                    total_anims.append(Transform(totals_lbl[letter], new_total))
                else:
                    totals_lbl[letter] = new_total
                    total_anims.append(FadeIn(new_total))
            self.play(*total_anims, run_time=0.5)

        self.play(FadeOut(outline))

        final_c_total = totals_lbl["C"]
        c_bar_segments = segments["C"]
        self.play(
            final_c_total.animate.set_color(HL_COLOR),
            *[seg[0].animate.set_color(HL_COLOR) for seg in c_bar_segments],
        )

        cap2 = self.swap_caption("Each row sends its share to the UPS that are still running.")
        self.wait(0.5)
        cap3 = self.swap_caption("UPS C ends up carrying 1,350 kW.")
        self.wait(2.0)

        all_seg_items = [seg for letter in ("B", "C", "D") for seg in segments[letter]]
        self.layout_items = [
            header_ups, header_ups.cross, header_lbl, baseline, letters,
            *self.rows[4:], *[ov["chips"][f"Row {i}"] for i in (5, 6, 7, 8)],
            ov["frame2"], ov["title2"], *log_lines, *all_seg_items, *totals_lbl.values(), cap3,
        ]
        idx_frame2 = self.layout_items.index(ov["frame2"])
        # rows/chips overlap the frame that surrounds them (bbox artifact)
        allowed = set()
        for r in self.rows[4:]:
            allowed.add((self.layout_items.index(r), idx_frame2))
        for i in (5, 6, 7, 8):
            allowed.add((self.layout_items.index(ov["chips"][f"Row {i}"]), idx_frame2))
        idx_header_ups = self.layout_items.index(header_ups)
        idx_cross = self.layout_items.index(header_ups.cross)
        allowed.add((idx_header_ups, idx_cross))
        idx_baseline = self.layout_items.index(baseline)
        seg_indices = [self.layout_items.index(seg) for seg in all_seg_items]
        for si in seg_indices:
            allowed.add((idx_baseline, si))
        for a in range(len(seg_indices)):
            for b in range(a + 1, len(seg_indices)):
                allowed.add((seg_indices[a], seg_indices[b]))
        self.allowed_overlaps = allowed
        self.check_layout("4_2")

        self._group2_state = dict(
            header_ups=header_ups, header_lbl=header_lbl, baseline=baseline, letters=letters,
            frame2=ov["frame2"], title2=ov["title2"], chips=ov["chips"], log_lines=log_lines,
            segments=segments, totals=totals_lbl, bar_xs=bar_xs, scale=SCALE,
        )

    # ===================================================== Beat 4.3 =====
    def beat_4_3_every_failure(self):
        st = self._group2_state
        left_region = VGroup(
            *self.rows[4:], *[st["chips"][f"Row {i}"] for i in (5, 6, 7, 8)],
            st["frame2"], st["title2"], st["log_lines"],
        )
        all_segments = VGroup(*[seg for letter in ("B", "C", "D") for seg in st["segments"][letter]])
        self.play(
            FadeOut(left_region), FadeOut(st["header_ups"]), FadeOut(st["header_ups"].cross),
            FadeOut(st["header_lbl"]), FadeOut(st["baseline"]), FadeOut(st["letters"]),
            FadeOut(all_segments), FadeOut(VGroup(*st["totals"].values())),
            run_time=0.6,
        )
        self.play(FadeOut(self.current_caption))
        self.current_caption = None

        t = title("Group 2 --- every failure")
        self.play(FadeIn(t))

        centers = {"A": -4.8, "B": -1.6, "C": 1.6, "D": 4.8}
        panel_scale = 3.4 / 1400

        def build_panel(failed, animate_bars=True):
            cx = centers[failed]
            header = Tex(f"{failed} fails", font_size=26, color=TEXT_COLOR)
            header.move_to([cx, 2.3, 0])
            baseline = Line([cx - 1.35, -1.9, 0], [cx + 1.35, -1.9, 0],
                             color=SECONDARY_COLOR, stroke_width=2)
            survivors = [l for l in UPS_NAMES if l != failed]
            xs = [cx - 0.9, cx, cx + 0.9]
            bars = VGroup()
            vals = VGroup()
            letters = VGroup()
            values = FAULT_TABLE_A_G2[failed]
            for x, letter in zip(xs, survivors):
                v = values[letter]
                h = v * panel_scale
                color = HL_COLOR if v == 1350 else UPS_COLORS[letter]
                bar = Rectangle(width=0.7, height=h, fill_color=color, fill_opacity=1,
                                 stroke_width=0)
                bar.move_to([x, -1.9 + h / 2, 0])
                val_lbl = Tex(fmt_kw(v), font_size=22, color=color)
                val_lbl.next_to(bar, UP, buff=0.1)
                letter_lbl = Tex(letter, font_size=24, color=UPS_COLORS[letter])
                letter_lbl.move_to([x, -2.2, 0])
                bars.add(bar)
                vals.add(val_lbl)
                letters.add(letter_lbl)
            return dict(header=header, baseline=baseline, bars=bars, vals=vals, letters=letters)

        panel_a = build_panel("A")
        self.play(
            FadeIn(panel_a["header"]),
            Create(panel_a["baseline"]),
            *[FadeIn(b) for b in panel_a["bars"]],
            *[FadeIn(v) for v in panel_a["vals"]],
            *[FadeIn(l) for l in panel_a["letters"]],
        )

        cap = self.swap_caption("Now check every possible failure.")

        dividers = VGroup(*[
            Line([x, -2.2, 0], [x, 2.1, 0], color=SECONDARY_COLOR, stroke_width=1, stroke_opacity=0.4)
            for x in (-3.2, 0, 3.2)
        ])
        self.play(Create(dividers))

        panels = {"A": panel_a}
        for failed in ("B", "C", "D"):
            p = build_panel(failed)
            self.play(FadeIn(p["header"]), Create(p["baseline"]))
            self.play(
                *[GrowFromEdge(b, DOWN) for b in p["bars"]],
                run_time=0.8,
            )
            self.play(*[FadeIn(v) for v in p["vals"]])
            self.play(*[FadeIn(l) for l in p["letters"]])
            panels[failed] = p

        cap2 = self.swap_caption("The highest load is 1,350 kW --- in two of the four cases.")
        self.wait(1.5)

        self.background_items = [dividers]
        self.layout_items = [t]
        bar_baseline_pairs = []
        for p in panels.values():
            idx_baseline = len(self.layout_items) + 1
            self.layout_items += [p["header"], p["baseline"], *p["bars"], *p["vals"], *p["letters"]]
            for bar in p["bars"]:
                bar_baseline_pairs.append((idx_baseline, self.layout_items.index(bar)))
        self.layout_items.append(cap2)
        self.allowed_overlaps = set(bar_baseline_pairs)
        self.check_layout("4_3")

        self._panels = panels
        self._every_failure_title = t
        self._dividers = dividers

    # ===================================================== Beat 4.4 =====
    def beat_4_4_define_m(self):
        line = DashedLine([-6.3, 2.0, 0], [6.3, 2.0, 0], color=HL_COLOR, stroke_width=3)
        self.play(Create(line))

        target_y = -1.9 + 1350 * (3.4 / 1400)
        self.play(line.animate.move_to([0, target_y, 0]), run_time=1.2)
        self.wait(1.0)

        panels_group = VGroup(
            self._every_failure_title, self._dividers,
            *[obj for p in self._panels.values()
              for obj in (p["header"], p["baseline"], *p["bars"], *p["vals"], *p["letters"])],
        )
        self.play(panels_group.animate.set_opacity(0.25), line.animate.set_opacity(0.25))

        g1_worst, g2_worst = SOLUTION_A["group_max"][0], SOLUTION_A["group_max"][1]
        card_bg = RoundedRectangle(width=8.0, height=3.2, corner_radius=0.1,
                                    fill_color=BG_COLOR, fill_opacity=0.92,
                                    stroke_color=SECONDARY_COLOR, stroke_width=2)
        card_bg.move_to([0, 0.2, 0])

        l1a = Tex("Group 2 worst case:", font_size=30, color=TEXT_COLOR)
        l1b = Tex(fmt_kw(g2_worst), font_size=30, color=HL_COLOR)
        line1 = VGroup(l1a, l1b).arrange(RIGHT, buff=0.2)

        l2a = Tex("Group 1 worst case:", font_size=30, color=TEXT_COLOR)
        l2b = Tex(fmt_kw(g1_worst), font_size=30, color=TEXT_COLOR)
        l2c = Tex("(same check)", font_size=22, color=SECONDARY_COLOR)
        line2 = VGroup(l2a, l2b, l2c).arrange(RIGHT, buff=0.2)

        text_block = VGroup(line1, line2).arrange(DOWN, buff=0.55, aligned_edge=LEFT)
        text_block.move_to([0, 0.85, 0])

        sep = Line(LEFT * 3.4, RIGHT * 3.4, color=SECONDARY_COLOR, stroke_width=1)
        sep.move_to([0, 0.1, 0])

        m_eq = MathTex(r"M = \max(1000,\ 1350) = 1350", font_size=40)
        m_eq.set_color(TEXT_COLOR)
        m_eq[0][0].set_color(HL_COLOR)
        m_eq.move_to([0, -0.6, 0])

        self.play(FadeIn(card_bg))
        self.play(FadeIn(text_block))
        self.play(Create(sep))
        self.play(FadeIn(m_eq))

        cap = self.swap_caption("Group 2's worst case is 1,350 kW.")
        self.wait(1.5)
        cap2 = self.swap_caption("Group 1's worst case is 1,000 kW.")
        self.wait(1.5)
        cap3 = self.swap_caption("M is the worst load anywhere --- every UPS must be rated for it.")
        self.wait(1.5)

        self.layout_items = [card_bg, text_block, sep, m_eq, cap3]
        self.allowed_overlaps = {(0, 1), (0, 2), (0, 3)}
        self.check_layout("4_4")

        self._card = VGroup(card_bg, text_block, sep, m_eq)
        self._panels_group = panels_group
        self._m_line = line

    # ===================================================== Beat 4.5 =====
    def beat_4_5_goal(self):
        self.play(
            FadeOut(self._card), FadeOut(self._panels_group), FadeOut(self._m_line),
            FadeOut(self.current_caption),
            run_time=0.8,
        )
        self.current_caption = None

        min_m = MathTex(r"\min\ M", font_size=72)
        min_m.set_color(TEXT_COLOR)
        min_m[0][-1].set_color(HL_COLOR)
        min_m.move_to([0, 0.4, 0])

        sub_line = Tex("by choosing the cut and the pairs", font_size=30, color=SECONDARY_COLOR)
        sub_line.move_to([0, -0.8, 0])

        self.play(FadeIn(min_m))
        self.play(FadeIn(sub_line))

        cap = self.swap_caption("Our goal: make M as small as possible.")
        self.wait(2.0)

        self.layout_items = [min_m, sub_line, cap]
        self.allowed_overlaps = set()
        self.check_layout("4_5")

        self.play(FadeOut(min_m), FadeOut(sub_line), FadeOut(cap), run_time=1.0)
        self.current_caption = None
