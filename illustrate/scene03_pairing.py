"""Scene 03 -- "Pairing and failure rules"

Built strictly from scene03_prompt.md + common_prompt.md.

Starts from: black, only Row 1 block (row_block("Row 1", 500, "2-source"))
centred at (0, 0) -- exactly Scene 02's handoff frame.

Ends with: fade to black. Nothing on screen.

Run with:
    manim -pqh scene03_pairing.py Scene03Pairing
"""
import numpy as np
from manim import *

from common.style import (
    BG_COLOR, TEXT_COLOR, SECONDARY_COLOR, UPS_COLORS, UPS_NAMES,
    HL_COLOR, GROUP1_COLOR, PAIR_COLOR,
)
from common.layout import caption, title, LayoutCheckMixin
from common.data import SCENE03, fmt_kw
from common.widgets import (
    row_block, ups_box, fail_anims, restore_anims, pair_chip, cut_line, data_table,
)

# ------------------------------------------------------------- geometry ---
UPS_X = {"A": -3.3, "B": -1.1, "C": 1.1, "D": 3.3}
UPS_Y = 2.4
UPS_BOTTOM_Y = 2.0
ROW_TOP_Y = -0.95
ROW_CENTER = np.array([0, -1.3, 0])
CABLE_LEVEL = {"A": 1.1, "B": 0.7, "C": 0.7, "D": 1.1}
CABLE_X = {"A": -1.2, "B": -0.4, "C": 0.4, "D": 1.2}
LOAD_LABEL_Y = 1.65


class Scene03Pairing(LayoutCheckMixin, Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        self.current_caption = None

        self.ups = {letter: ups_box(letter, w=1.4, h=0.8, font=30) for letter in UPS_NAMES}
        for letter, grp in self.ups.items():
            grp.move_to([UPS_X[letter], UPS_Y, 0])

        self.beat_3_1_six_pairs()
        self.beat_3_2_normal()
        self.beat_3_3_fail_in_pair()
        self.beat_3_4_fail_outside_pair()
        self.beat_3_5_pair_moves_load()
        self.beat_3_6_four_source()
        self.beat_3_7_rule_card()
        self.beat_3_8_two_decisions()

    # --------------------------------------------------------- helpers ---
    def swap_caption(self, text):
        new_cap = caption(text)
        if self.current_caption is not None:
            self.play(FadeOut(self.current_caption))
        self.play(FadeIn(new_cap))
        self.current_caption = new_cap
        return new_cap

    def cable(self, letter):
        x = UPS_X[letter]
        y_level = CABLE_LEVEL[letter]
        x_target = CABLE_X[letter]
        return VMobject(color=UPS_COLORS[letter], stroke_width=4).set_points_as_corners([
            [x, UPS_BOTTOM_Y, 0], [x, y_level, 0], [x_target, y_level, 0], [x_target, ROW_TOP_Y, 0],
        ])

    def load_label(self, letter, value):
        lbl = Tex(fmt_kw(value), font_size=26, color=UPS_COLORS[letter])
        lbl.move_to([UPS_X[letter] + 0.45, LOAD_LABEL_Y, 0])
        return lbl

    def share_tag(self, letter, tex, ref_label):
        tag = MathTex(tex, font_size=24, color=SECONDARY_COLOR)
        tag.move_to(ref_label.get_center())
        tag.next_to(ref_label, RIGHT, buff=0.1)
        return tag

    # ===================================================== Beat 3.1 =====
    def beat_3_1_six_pairs(self):
        t = title("Inside one group")
        row1 = row_block("Row 1", SCENE03["row1_kw"], SCENE03["row1_type"],
                          width=5.0, height=0.46, font=24)
        row1.move_to([0, 0, 0])
        self.row1 = row1

        self.play(FadeIn(t, shift=DOWN * 0.15), row1.animate.move_to([-2.6, 0.6, 0]), run_time=1.0)

        possible_pairs_lbl = Tex("Possible pairs", font_size=26, color=SECONDARY_COLOR)
        possible_pairs_lbl.move_to([3.6, 1.9, 0])
        self.play(FadeIn(possible_pairs_lbl))

        pairs = SCENE03["pairs"]
        xs = [2.2, 3.6, 5.0]
        chips = {}
        for i, pair in enumerate(pairs):
            row_i, col_i = divmod(i, 3)
            y = 1.1 if row_i == 0 else 0.1
            chip = pair_chip(pair, font=28)
            chip.move_to([xs[col_i], y, 0])
            chips[pair] = chip
            self.play(FadeIn(chip), run_time=0.35)
        self.chips = chips

        cap = self.swap_caption("Each group has UPS A, B, C and D.")
        self.wait(1.0)

        cap2 = self.swap_caption(
            "A 2-source row connects to two of them --- six possible pairs."
        )
        for pair in pairs:
            self.play(Indicate(chips[pair], color=HL_COLOR), run_time=0.3)
        self.wait(1.0)

        self.layout_items = [t, row1, possible_pairs_lbl, *chips.values(), cap2]
        self.allowed_overlaps = set()
        self.check_layout("3_1")

        self._title = t
        self._possible_pairs_lbl = possible_pairs_lbl

    # ===================================================== Beat 3.2 =====
    def beat_3_2_normal(self):
        chips_to_remove = [c for p, c in self.chips.items() if p != "AB"]
        self.play(
            FadeOut(self._title), FadeOut(self._possible_pairs_lbl),
            *[FadeOut(c) for c in chips_to_remove],
        )

        ab_chip = self.chips["AB"]
        schematic_row = row_block("Row 1", SCENE03["row1_kw"], SCENE03["row1_type"],
                                   width=4.4, height=0.7, font=28)
        schematic_row.move_to(ROW_CENTER)

        group_tag = Tex("Inside Group 1", font_size=24, color=GROUP1_COLOR)
        group_tag.move_to([-5.4, 2.4, 0])

        self.play(
            Transform(self.row1, schematic_row),
            ab_chip.animate.move_to([3.0, -1.3, 0]),
            *[FadeIn(u) for u in self.ups.values()],
            FadeIn(group_tag),
            run_time=1.2,
        )
        self.row_block_mobj = self.row1
        self.group_tag = group_tag
        self.ab_chip = ab_chip

        cable_a = self.cable("A")
        cable_b = self.cable("B")
        self.play(Create(cable_a), Create(cable_b), run_time=0.8)

        label_a = self.load_label("A", SCENE03["row1_half_share"])
        label_b = self.load_label("B", SCENE03["row1_half_share"])
        self.play(FadeIn(label_a), FadeIn(label_b))

        cap = self.swap_caption("With pair AB, UPS A and UPS B share Row 1 half and half.")
        self.wait(1.5)

        self.background_items = [cable_a, cable_b]
        self.layout_items = [
            group_tag, *self.ups.values(), self.row_block_mobj, ab_chip, label_a, label_b, cap,
        ]
        self.allowed_overlaps = set()
        self.check_layout("3_2")

        self._cable_a, self._cable_b = cable_a, cable_b
        self._label_a, self._label_b = label_a, label_b

    # ===================================================== Beat 3.3 =====
    def beat_3_3_fail_in_pair(self):
        self.play(*fail_anims(self.ups["A"]), run_time=0.6)
        self.play(
            self._cable_a.animate.set_stroke(opacity=0.2),
            FadeOut(self._label_a),
        )

        counter_b = DecimalNumber(SCENE03["row1_half_share"], num_decimal_places=0,
                                   font_size=26, color=UPS_COLORS["B"])
        counter_b.move_to(self._label_b.get_center())
        unit_b = Tex("kW", font_size=26, color=UPS_COLORS["B"]).next_to(counter_b, RIGHT, buff=0.1)
        self.play(FadeOut(self._label_b), FadeIn(counter_b), FadeIn(unit_b))
        self.play(
            counter_b.animate.set_value(SCENE03["row1_partner_full_share"]).set_color(HL_COLOR),
            unit_b.animate.set_color(HL_COLOR),
            run_time=1.2,
        )
        tag_b = MathTex(r"\times 1", font_size=24, color=SECONDARY_COLOR)
        tag_b.next_to(VGroup(counter_b, unit_b), RIGHT, buff=0.1)
        self.play(FadeIn(tag_b))

        cap = self.swap_caption("If UPS A fails, its partner B carries the whole row.")
        self.wait(2.0)

        self.background_items = [self._cable_a, self._cable_b]
        self.layout_items = [
            self.group_tag, *self.ups.values(), self.row_block_mobj, self.ab_chip,
            self.ups["A"].cross, counter_b, unit_b, tag_b, cap,
        ]
        idx_ups_a_box = self.layout_items.index(self.ups["A"])
        idx_cross_a = self.layout_items.index(self.ups["A"].cross)
        self.allowed_overlaps = {(idx_ups_a_box, idx_cross_a)}
        self.check_layout("3_3")

        self.play(*restore_anims(self.ups["A"]), run_time=0.8)
        new_label_a = self.load_label("A", SCENE03["row1_half_share"])
        new_label_b = self.load_label("B", SCENE03["row1_half_share"])
        self.play(
            self._cable_a.animate.set_stroke(opacity=1),
            FadeOut(counter_b), FadeOut(unit_b), FadeOut(tag_b),
            FadeIn(new_label_a), FadeIn(new_label_b),
            run_time=0.8,
        )
        self._label_a, self._label_b = new_label_a, new_label_b

    # ===================================================== Beat 3.4 =====
    def beat_3_4_fail_outside_pair(self):
        self.play(*fail_anims(self.ups["C"]), run_time=0.6)
        tag_a = MathTex(r"\times\tfrac{1}{2}", font_size=24, color=SECONDARY_COLOR)
        tag_a.next_to(self._label_a, RIGHT, buff=0.1)
        tag_b = MathTex(r"\times\tfrac{1}{2}", font_size=24, color=SECONDARY_COLOR)
        tag_b.next_to(self._label_b, RIGHT, buff=0.1)
        self.play(FadeIn(tag_a), FadeIn(tag_b))

        cap = self.swap_caption("If UPS C fails, Row 1 is not affected --- A and B still share it.")
        self.wait(1.5)

        self.background_items = [self._cable_a, self._cable_b]
        self.layout_items = [
            self.group_tag, *self.ups.values(), self.row_block_mobj, self.ab_chip,
            self.ups["C"].cross, self._label_a, self._label_b, tag_a, tag_b, cap,
        ]
        idx_ups_c_box = self.layout_items.index(self.ups["C"])
        idx_cross_c = self.layout_items.index(self.ups["C"].cross)
        self.allowed_overlaps = {(idx_ups_c_box, idx_cross_c)}
        self.check_layout("3_4a")

        self.play(*restore_anims(self.ups["C"]), run_time=0.6)
        self.play(*fail_anims(self.ups["D"]), run_time=0.6)
        self.play(Indicate(tag_a), Indicate(tag_b))

        cap2 = self.swap_caption("The same is true if D fails.")
        self.wait(1.0)

        self.layout_items = [
            self.group_tag, *self.ups.values(), self.row_block_mobj, self.ab_chip,
            self.ups["D"].cross, self._label_a, self._label_b, tag_a, tag_b, cap2,
        ]
        idx_ups_d_box = self.layout_items.index(self.ups["D"])
        idx_cross_d = self.layout_items.index(self.ups["D"].cross)
        self.allowed_overlaps = {(idx_ups_d_box, idx_cross_d)}
        self.check_layout("3_4b")

        self.play(*restore_anims(self.ups["D"]), run_time=0.6)
        self.play(FadeOut(tag_a), FadeOut(tag_b))

    # ===================================================== Beat 3.5 =====
    def beat_3_5_pair_moves_load(self):
        ac_chip = pair_chip("AC", font=28)
        ac_chip.move_to(self.ab_chip.get_center())
        self.play(Transform(self.ab_chip, ac_chip), run_time=0.6)

        cable_c = self.cable("C")
        label_c = self.load_label("C", SCENE03["row1_half_share"])
        self.play(
            Uncreate(self._cable_b), FadeOut(self._label_b),
            Create(cable_c), FadeIn(label_c),
            run_time=0.8,
        )

        cap = self.swap_caption("Choose another pair, and the load lands on different UPS.")
        self.wait(1.5)

        self.background_items = [self._cable_a, cable_c]
        self.layout_items = [
            self.group_tag, *self.ups.values(), self.row_block_mobj, self.ab_chip,
            self._label_a, label_c, cap,
        ]
        self.allowed_overlaps = set()
        self.check_layout("3_5")

        self.play(
            FadeOut(self._cable_a), FadeOut(cable_c),
            FadeOut(self._label_a), FadeOut(label_c),
            FadeOut(self.ab_chip),
        )

    # ===================================================== Beat 3.6 =====
    def beat_3_6_four_source(self):
        row2_block = row_block("Row 2", SCENE03["row2_kw"], SCENE03["row2_type"],
                                width=4.4, height=0.7, font=28)
        row2_block.move_to(ROW_CENTER)
        self.play(Transform(self.row_block_mobj, row2_block), run_time=0.6)

        abcd_chip = pair_chip("ABCD", font=28)
        abcd_chip.move_to([3.0, -1.3, 0])
        no_choice = Tex("no choice", font_size=24, color=SECONDARY_COLOR)
        no_choice.move_to([3.0, -1.95, 0])
        self.play(FadeIn(abcd_chip), FadeIn(no_choice))

        cables = {letter: self.cable(letter) for letter in UPS_NAMES}
        self.play(*[Create(c) for c in cables.values()], run_time=1.0)

        labels = {letter: self.load_label(letter, SCENE03["row2_quarter_share"])
                  for letter in UPS_NAMES}
        self.play(*[FadeIn(l) for l in labels.values()])

        cap = self.swap_caption("Row 2 is 4-source: it always uses all four UPS.")
        self.wait(1.2)

        self.background_items = list(cables.values())
        self.layout_items = [
            self.group_tag, *self.ups.values(), self.row_block_mobj, abcd_chip, no_choice,
            *labels.values(), cap,
        ]
        self.allowed_overlaps = set()
        self.check_layout("3_6a")

        self.play(*fail_anims(self.ups["D"]), run_time=0.6)
        self.play(cables["D"].animate.set_stroke(opacity=0.2), FadeOut(labels["D"]))

        counters = {}
        units = {}
        anims = []
        for letter in ("A", "B", "C"):
            c = DecimalNumber(SCENE03["row2_quarter_share"], num_decimal_places=0,
                               font_size=26, color=UPS_COLORS[letter])
            c.move_to(labels[letter].get_center())
            u = Tex("kW", font_size=26, color=UPS_COLORS[letter]).next_to(c, RIGHT, buff=0.1)
            counters[letter] = c
            units[letter] = u
            anims += [FadeOut(labels[letter]), FadeIn(c), FadeIn(u)]
        self.play(*anims)
        self.play(
            *[counters[l].animate.set_value(SCENE03["row2_third_share"]).set_color(HL_COLOR)
              for l in ("A", "B", "C")],
            *[units[l].animate.set_color(HL_COLOR) for l in ("A", "B", "C")],
            run_time=1.2,
        )
        tags = {}
        for letter in ("A", "B", "C"):
            tag = MathTex(r"\times\tfrac{1}{3}", font_size=24, color=SECONDARY_COLOR)
            tag.next_to(VGroup(counters[letter], units[letter]), RIGHT, buff=0.1)
            tags[letter] = tag
        self.play(*[FadeIn(t) for t in tags.values()])

        cap2 = self.swap_caption("If one fails, the other three share it equally.")
        self.wait(2.0)

        self.layout_items = [
            self.group_tag, *self.ups.values(), self.row_block_mobj, abcd_chip, no_choice,
            self.ups["D"].cross, *counters.values(), *units.values(), *tags.values(), cap2,
        ]
        idx_ups_d_box = self.layout_items.index(self.ups["D"])
        idx_cross_d = self.layout_items.index(self.ups["D"].cross)
        self.allowed_overlaps = {(idx_ups_d_box, idx_cross_d)}
        self.check_layout("3_6b")

        self.play(
            FadeOut(VGroup(*self.ups.values())),
            FadeOut(self.ups["D"].cross),
            *[FadeOut(c) for c in cables.values()],
            *[FadeOut(t) for t in tags.values()],
            *[FadeOut(c) for c in counters.values()],
            *[FadeOut(u) for u in units.values()],
            FadeOut(self.row_block_mobj), FadeOut(abcd_chip), FadeOut(no_choice),
            FadeOut(self.group_tag),
        )
        self.current_caption = cap2

    # ===================================================== Beat 3.7 =====
    def beat_3_7_rule_card(self):
        self.play(FadeOut(self.current_caption))
        self.current_caption = None

        t = title("What one failure does")
        self.play(FadeIn(t))

        rows_data = [
            ("2-source", "partner of the failed UPS", r"\times 1"),
            ("2-source", "in the pair, failure elsewhere", r"\times\tfrac{1}{2}"),
            ("2-source", "not in the pair", "0"),
            ("4-source", "any surviving UPS", r"\times\tfrac{1}{3}"),
        ]
        font = 28
        cell_matrix = [
            [Tex("Row type", font_size=font, color=SECONDARY_COLOR),
             Tex("UPS", font_size=font, color=SECONDARY_COLOR),
             Tex("Share of the row's kW", font_size=font, color=SECONDARY_COLOR)],
        ]
        for row_type, ups_desc, share in rows_data:
            cell_matrix.append([
                Tex(row_type, font_size=font, color=TEXT_COLOR),
                Tex(ups_desc, font_size=font, color=TEXT_COLOR),
                MathTex(share, font_size=font, color=TEXT_COLOR),
            ])

        table = data_table(cell_matrix, col_gap=0.8, row_gap=0.45)
        if table.width > 12:
            font = 26
            cell_matrix = [[c.copy() for c in row] for row in cell_matrix]
            for row in cell_matrix:
                for c in row:
                    c.scale_to_fit_height(c.height * font / 28)
            table = data_table(cell_matrix, col_gap=0.8, row_gap=0.45)
        if table.width > 12:
            raise ValueError("Rule-card table too wide even at font 26")
        table.move_to([0, 0.3, 0])

        header = table.header
        data_rows = table.rows

        underline = Line(
            header.get_corner(DL) + LEFT * 0.1 + DOWN * 0.15,
            header.get_corner(DR) + RIGHT * 0.1 + DOWN * 0.15,
            color=SECONDARY_COLOR, stroke_width=2,
        )

        self.play(FadeIn(header), Create(underline))
        for row in data_rows:
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.4)

        cap = self.swap_caption("These rules give the load on every UPS, for every failure.")
        self.wait(2.0)

        self.layout_items = [t, header, underline, *data_rows, cap]
        self.allowed_overlaps = set()
        self.check_layout("3_7")

        self.play(FadeOut(t), FadeOut(header), FadeOut(underline), FadeOut(data_rows))

    # ===================================================== Beat 3.8 =====
    def beat_3_8_two_decisions(self):
        left_box = RoundedRectangle(width=3.8, height=1.1, corner_radius=0.1,
                                     stroke_color=GROUP1_COLOR, stroke_width=3)
        left_box.move_to([-2.7, 0.4, 0])
        left_txt = Tex("Where to cut?", font_size=34, color=TEXT_COLOR)
        left_txt.move_to(left_box.get_center())
        left_grp = VGroup(left_box, left_txt)

        right_box = RoundedRectangle(width=3.8, height=1.1, corner_radius=0.1,
                                      stroke_color=PAIR_COLOR, stroke_width=3)
        right_box.move_to([2.7, 0.4, 0])
        right_txt = Tex("Which pair?", font_size=34, color=TEXT_COLOR)
        right_txt.move_to(right_box.get_center())
        right_grp = VGroup(right_box, right_txt)

        plus = Tex("+", font_size=44, color=TEXT_COLOR)
        plus.move_to([0, 0.4, 0])

        self.play(FadeIn(left_grp), FadeIn(right_grp))
        self.play(FadeIn(plus))

        small_cut = cut_line(length=2.0)
        small_cut.move_to([-2.7, -0.6, 0])
        small_chip = pair_chip("AB", font=24)
        small_chip.move_to([2.7, -0.6, 0])
        self.play(Create(small_cut), FadeIn(small_chip))

        cap = self.swap_caption("Two decisions --- and we must make them together.")
        self.wait(2.0)

        self.layout_items = [left_grp, right_grp, plus, small_cut, small_chip, cap]
        self.allowed_overlaps = set()
        self.check_layout("3_8")

        self.play(
            FadeOut(left_grp), FadeOut(right_grp), FadeOut(plus),
            FadeOut(small_cut), FadeOut(small_chip), FadeOut(cap),
            run_time=1.0,
        )
        self.current_caption = None
