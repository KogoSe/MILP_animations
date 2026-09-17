"""Scene 05 -- "Too many answers"

Built strictly from scene05_prompt.md + common_prompt.md.

Starts from: black (Scene 04 ended on "Our goal: make M as small as
possible." then faded to black).

Ends with: fade to black after "We need a smarter way to search."

Run with:
    manim -pqh scene05_search_space.py Scene05SearchSpace
"""
import numpy as np
from manim import *

from common.style import (
    BG_COLOR, TEXT_COLOR, SECONDARY_COLOR, UPS_COLORS,
    HL_COLOR, GROUP1_COLOR, GROUP2_COLOR, ROW_FILL, ROW_STROKE,
)
from common.layout import caption, title, LayoutCheckMixin
from common.data import DEMO_ROWS, SOLUTION_A, SOLUTION_B, SEARCH_SPACE_DEMO, fmt_kw
from common.widgets import pair_chip, group_frame

MINI_ROW_YS = [1.8, 1.4, 1.0, 0.6, -0.1, -0.5, -0.9, -1.3]


def row_type(idx):
    return DEMO_ROWS[idx][2]


class Scene05SearchSpace(LayoutCheckMixin, Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        self.current_caption = None

        self.beat_5_1_better_answer()
        self.beat_5_2_is_it_best()
        self.beat_5_3_count_small()
        self.beat_5_4_real_hall()

    # --------------------------------------------------------- helpers ---
    def swap_caption(self, text):
        new_cap = caption(text)
        if self.current_caption is not None:
            self.play(FadeOut(self.current_caption))
        self.play(FadeIn(new_cap))
        self.current_caption = new_cap
        return new_cap

    def pair_for(self, solution, idx):
        name, kw, type_ = DEMO_ROWS[idx]
        if type_ == "4-source":
            return "ABCD"
        return solution["pairs"][name]

    def solution_card(self, label, solution, cx):
        header = Tex(label, font_size=32, color=TEXT_COLOR)
        header.move_to([cx, 2.35, 0])

        mini_rows = []
        for i, y in enumerate(MINI_ROW_YS):
            name, kw, type_ = DEMO_ROWS[i]
            rect = Rectangle(width=1.4, height=0.34, fill_color=ROW_FILL, fill_opacity=1,
                              stroke_color=ROW_STROKE, stroke_width=1.5)
            rect.move_to([cx - 0.6, y, 0])
            lbl = Tex(name, font_size=22, color=TEXT_COLOR)
            if lbl.width > rect.width - 0.1:
                lbl.scale_to_fit_width(rect.width - 0.1)
            lbl.move_to(rect.get_center())
            mini_rows.append(VGroup(rect, lbl))

        chips = {}
        for i, y in enumerate(MINI_ROW_YS):
            name = DEMO_ROWS[i][0]
            pair = self.pair_for(solution, i)
            chip = pair_chip(pair, font=20, pad=0.06)
            chip.move_to([cx + 0.25 + chip.width / 2, y, 0])
            chips[name] = chip

        frame1 = group_frame(VGroup(*[mr[0] for mr in mini_rows[:4]]), GROUP1_COLOR, buff=0.05)
        frame2 = group_frame(VGroup(*[mr[0] for mr in mini_rows[4:]]), GROUP2_COLOR, buff=0.05)

        g1, g2 = solution["group_max"]
        w1 = Tex(f"worst {fmt_kw(g1)}", font_size=22, color=SECONDARY_COLOR)
        w1.move_to([cx + 1.2 + w1.width / 2, frame1.get_center()[1], 0])
        w2 = Tex(f"worst {fmt_kw(g2)}", font_size=22, color=SECONDARY_COLOR)
        w2.move_to([cx + 1.2 + w2.width / 2, frame2.get_center()[1], 0])

        m_val = solution["M"]
        result = MathTex("M", "=", f"{m_val:,}", font_size=34)
        result.set_color_by_tex("M", HL_COLOR)
        result.set_color_by_tex("=", TEXT_COLOR)
        result.set_color_by_tex(f"{m_val:,}", HL_COLOR)
        result.move_to([cx, -2.05, 0])

        card = VGroup(header, *mini_rows, frame1, frame2, *chips.values(), w1, w2, result)
        card.header, card.mini_rows, card.chips = header, mini_rows, chips
        card.frame1, card.frame2, card.w1, card.w2, card.result = frame1, frame2, w1, w2, result
        return card

    def dots_grid(self, spacing=0.5, offset=(0.0, 0.0), opacity=0.25, radius=0.03):
        dots = VGroup()
        xs = np.arange(-6.6 + offset[0], 6.6, spacing)
        ys = np.arange(-3.6 + offset[1], 3.6, spacing)
        for x in xs:
            for y in ys:
                if -6.6 <= x <= 6.6 and -3.6 <= y <= 3.6:
                    dots.add(Dot([x, y, 0], radius=radius, color=TEXT_COLOR, fill_opacity=opacity))
        return dots

    # ===================================================== Beat 5.1 =====
    def beat_5_1_better_answer(self):
        t = title("Can we do better?")
        self.play(FadeIn(t, shift=DOWN * 0.15))

        card_a = self.solution_card("Solution A", SOLUTION_A, -3.4)
        self.play(FadeIn(card_a.header))
        self.play(LaggedStart(*[FadeIn(mr) for mr in card_a.mini_rows], lag_ratio=0.1), run_time=1.0)
        self.play(Create(card_a.frame1), Create(card_a.frame2))
        self.play(*[FadeIn(c) for c in card_a.chips.values()])
        self.play(FadeIn(card_a.w1), FadeIn(card_a.w2))
        self.play(FadeIn(card_a.result))

        cap = self.swap_caption("This is the previous approach, with M = 1,350 kW.")
        self.wait(1.0)

        divider = Line([0, 2.5, 0], [0, -2.3, 0], color=SECONDARY_COLOR, stroke_width=1)
        self.play(Create(divider))

        # Solution B starts as a copy of Solution A's pairs/result, then updates
        card_b_start = SOLUTION_A.copy()
        card_b_start["group_max"] = SOLUTION_A["group_max"]
        card_b_start["M"] = SOLUTION_A["M"]
        card_b_start["pairs"] = SOLUTION_A["pairs"]
        card_b = self.solution_card("Solution B", card_b_start, 3.4)

        self.play(FadeIn(card_b.header))
        self.play(LaggedStart(*[FadeIn(mr) for mr in card_b.mini_rows], lag_ratio=0.1), run_time=1.0)
        self.play(Create(card_b.frame1), Create(card_b.frame2))
        self.play(*[FadeIn(c) for c in card_b.chips.values()])
        self.play(FadeIn(card_b.w1), FadeIn(card_b.w2))
        self.play(FadeIn(card_b.result))

        cap2 = self.swap_caption("Keep the same cut, but choose the pairs more carefully.")

        changes = [("Row 3", "AC"), ("Row 4", "CD"), ("Row 7", "AC"), ("Row 8", "BD")]
        for name, new_pair in changes:
            old_chip = card_b.chips[name]
            new_chip = pair_chip(new_pair, font=20, pad=0.06)
            new_chip.move_to([3.4 + 0.25 + new_chip.width / 2, old_chip.get_center()[1], 0])
            self.play(Transform(old_chip, new_chip), run_time=0.5)
            self.play(Indicate(old_chip), run_time=0.3)

        g1b, g2b = SOLUTION_B["group_max"]
        new_w1 = Tex(f"worst {fmt_kw(g1b)}", font_size=22, color=SECONDARY_COLOR)
        new_w1.move_to([3.4 + 1.2 + new_w1.width / 2, card_b.frame1.get_center()[1], 0])
        new_w2 = Tex(f"worst {fmt_kw(g2b)}", font_size=22, color=SECONDARY_COLOR)
        new_w2.move_to([3.4 + 1.2 + new_w2.width / 2, card_b.frame2.get_center()[1], 0])
        self.play(Transform(card_b.w1, new_w1), Transform(card_b.w2, new_w2))

        counter = DecimalNumber(1350, num_decimal_places=0, font_size=34, color=HL_COLOR)
        counter.move_to(card_b.result.get_center() + RIGHT * 0.3)
        m_prefix = MathTex("M = ", font_size=34, color=TEXT_COLOR)
        m_prefix.next_to(counter, LEFT, buff=0.1)
        self.play(FadeOut(card_b.result), FadeIn(m_prefix), FadeIn(counter))
        self.play(counter.animate.set_value(1100), run_time=1.2)

        cap3 = self.swap_caption("The worst case drops from 1,350 to 1,100 kW.")
        self.wait(1.5)

        self.layout_items = [
            t, card_a.header, *card_a.mini_rows, card_a.frame1, card_a.frame2,
            *card_a.chips.values(), card_a.w1, card_a.w2, card_a.result,
            divider,
            card_b.header, *card_b.mini_rows, card_b.frame1, card_b.frame2,
            *card_b.chips.values(), card_b.w1, card_b.w2, m_prefix, counter, cap3,
        ]
        allowed = set()
        idx_a_f1 = self.layout_items.index(card_a.frame1)
        idx_a_f2 = self.layout_items.index(card_a.frame2)
        idx_b_f1 = self.layout_items.index(card_b.frame1)
        idx_b_f2 = self.layout_items.index(card_b.frame2)
        for mr in card_a.mini_rows[:4]:
            allowed.add((self.layout_items.index(mr), idx_a_f1))
        for mr in card_a.mini_rows[4:]:
            allowed.add((self.layout_items.index(mr), idx_a_f2))
        for mr in card_b.mini_rows[:4]:
            allowed.add((self.layout_items.index(mr), idx_b_f1))
        for mr in card_b.mini_rows[4:]:
            allowed.add((self.layout_items.index(mr), idx_b_f2))
        self.allowed_overlaps = allowed
        self.check_layout("5_1")

        self._card_a = card_a
        self._card_b = card_b
        self._divider = divider
        self._title = t
        self._b_result = VGroup(m_prefix, counter)

    # ===================================================== Beat 5.2 =====
    def beat_5_2_is_it_best(self):
        card_a = self._card_a
        card_b = self._card_b
        background = VGroup(
            self._title, card_a, self._divider,
            card_b.header, *card_b.mini_rows, card_b.frame1, card_b.frame2,
            *card_b.chips.values(), card_b.w1, card_b.w2,
        )
        self.play(background.animate.set_opacity(0.2))

        self.play(self._b_result.animate.move_to([0, 1.2, 0]).scale(44 / 34))

        question = Tex("Is this the best we can do?", font_size=40, color=TEXT_COLOR)
        question.move_to([0, 0.0, 0])
        question_bg = BackgroundRectangle(question, fill_color=BG_COLOR, fill_opacity=0.9, buff=0.1)
        self.play(FadeIn(question_bg), FadeIn(question))

        cap = self.swap_caption("Better --- but is it the best possible?")
        self.wait(1.2)
        cap2 = self.swap_caption("We only changed the pairs. The cut can change too.")
        self.wait(1.5)

        self.background_items = [background]
        self.layout_items = [self._b_result, question_bg, question, cap2]
        self.allowed_overlaps = {(1, 2)}
        self.check_layout("5_2")

        self.play(
            FadeOut(background), FadeOut(self._b_result),
            FadeOut(question_bg), FadeOut(question), FadeOut(cap2),
        )
        self.current_caption = None

        new_title = title("How many answers?")
        self.play(Transform(self._title, new_title), run_time=0.6)

    # ===================================================== Beat 5.3 =====
    def beat_5_3_count_small(self):
        dots1 = self.dots_grid(spacing=0.6, offset=(0, 0), opacity=0.0)
        self.play(dots1.animate.set_opacity(0.25), run_time=2.0)
        self._dots = [dots1]

        seven = MathTex("7", font_size=60, color=TEXT_COLOR)
        seven_bg = BackgroundRectangle(seven, fill_color=BG_COLOR, fill_opacity=0.9, buff=0.1)
        seven.move_to([0, 0.8, 0])
        seven_bg.move_to(seven.get_center())
        seven_label = Tex("places to cut", font_size=24, color=SECONDARY_COLOR)
        seven_label_bg = BackgroundRectangle(seven_label, fill_color=BG_COLOR, fill_opacity=0.9, buff=0.1)
        seven_label.move_to([0, -0.4, 0])
        seven_label_bg.move_to(seven_label.get_center())

        self.play(FadeIn(seven_bg), FadeIn(seven), FadeIn(seven_label_bg), FadeIn(seven_label))

        cap = self.swap_caption("There are seven places to cut.")
        self.wait(1.0)

        top_line = MathTex("6", r"\times", "6", r"\times", "6", r"\times", "6", r"\times", "6",
                            r"\times", "6", font_size=36, color=TEXT_COLOR)
        top_line.move_to([0, 2.2, 0])
        top_bg = BackgroundRectangle(top_line, fill_color=BG_COLOR, fill_opacity=0.9, buff=0.1)
        six_parts = [top_line[i] for i in range(0, 11, 2)]
        self.play(FadeIn(top_bg))
        for part in six_parts:
            self.play(FadeIn(part), run_time=0.2)
        for i in range(1, 11, 2):
            self.play(FadeIn(top_line[i]), run_time=0.05)

        cap2 = self.swap_caption("Each of the six 2-source rows can take one of six pairs.")
        self.wait(1.0)

        six_to_six = MathTex(r"\times\ 6^{6}", font_size=60, color=TEXT_COLOR)
        six_to_six.next_to(seven, RIGHT, buff=0.3)
        pair_label = Tex("pair choices", font_size=24, color=SECONDARY_COLOR)
        pair_label2 = Tex("(six 2-source rows)", font_size=22, color=SECONDARY_COLOR)
        pair_label_grp = VGroup(pair_label, pair_label2).arrange(DOWN, buff=0.05)
        pair_label_grp.next_to(seven_label, RIGHT, buff=0.4)
        pair_label_bg = BackgroundRectangle(pair_label_grp, fill_color=BG_COLOR, fill_opacity=0.9, buff=0.1)

        self.play(Transform(top_line, six_to_six), FadeOut(top_bg), run_time=1.0)
        self.play(FadeIn(pair_label_bg), FadeIn(pair_label_grp))

        equals = MathTex("=", font_size=60, color=TEXT_COLOR)
        equals.next_to(six_to_six, RIGHT, buff=0.3)
        counter = DecimalNumber(0, num_decimal_places=0, font_size=60, color=TEXT_COLOR,
                                 group_with_commas=True)
        counter.next_to(equals, RIGHT, buff=0.3)
        counter_label = Tex("possible answers", font_size=24, color=SECONDARY_COLOR)
        counter_label.next_to(pair_label_grp, RIGHT, buff=0.4)
        counter_label_bg = BackgroundRectangle(counter_label, fill_color=BG_COLOR, fill_opacity=0.9, buff=0.1)

        main_group = VGroup(seven, top_line, equals, counter).arrange(RIGHT, buff=0.3)
        main_group.move_to([0, 0.8, 0])
        seven_bg.move_to(seven.get_center())

        self.play(FadeIn(equals))
        self.play(FadeIn(counter_label_bg), FadeIn(counter_label))
        self.play(counter.animate.set_value(SEARCH_SPACE_DEMO), run_time=1.5)

        dots2 = self.dots_grid(spacing=0.6, offset=(0.3, 0.3), opacity=0.0)
        self.play(dots2.animate.set_opacity(0.25), run_time=0.8)
        self._dots.append(dots2)

        cap3 = self.swap_caption(f"Even this small hall has {SEARCH_SPACE_DEMO:,} possible answers.")
        self.wait(2.0)

        self.background_items = [*self._dots]
        self.layout_items = [
            seven_bg, seven, seven_label_bg, seven_label,
            top_line, pair_label_bg, pair_label_grp,
            equals, counter, counter_label_bg, counter_label, cap3,
        ]
        self.allowed_overlaps = {(0, 1), (2, 3), (5, 6), (9, 10)}
        self.check_layout("5_3")

        self._count_state = dict(
            seven=seven, seven_bg=seven_bg, seven_label=seven_label, seven_label_bg=seven_label_bg,
            top_line=top_line, pair_label_grp=pair_label_grp, pair_label_bg=pair_label_bg,
            equals=equals, counter=counter, counter_label=counter_label, counter_label_bg=counter_label_bg,
        )

    # ===================================================== Beat 5.4 =====
    def beat_5_4_real_hall(self):
        st = self._count_state

        top_line2 = Tex("A real hall: 60 rows, 3 groups, 50 of them 2-source", font_size=30,
                         color=TEXT_COLOR)
        if top_line2.width > 12.0:
            top_line2 = Tex("A real hall: 60 rows, 3 groups, 50 of them 2-source", font_size=28,
                             color=TEXT_COLOR)
        top_line2.move_to([0, 2.2, 0])
        top_line2_bg = BackgroundRectangle(top_line2, fill_color=BG_COLOR, fill_opacity=0.9, buff=0.1)
        self.play(FadeIn(top_line2_bg), FadeIn(top_line2))

        new_main = MathTex(r"\binom{59}{2} \times 6^{50} \approx 1.4 \times 10^{42}", font_size=48)
        new_main.set_color(TEXT_COLOR)
        new_main.move_to([0, 0.8, 0])
        new_main_bg = BackgroundRectangle(new_main, fill_color=BG_COLOR, fill_opacity=0.9, buff=0.1)

        old_group = VGroup(st["seven"], st["top_line"], st["equals"], st["counter"])
        self.play(
            FadeOut(st["seven_bg"]), FadeOut(st["pair_label_bg"]), FadeOut(st["counter_label_bg"]),
            FadeOut(old_group), FadeIn(new_main_bg), FadeIn(new_main),
            run_time=1.0,
        )
        old_group = new_main

        new_label1 = Tex("places for 2 cuts", font_size=24, color=SECONDARY_COLOR)
        new_label1.next_to(new_main, DOWN, buff=0.5).shift(LEFT * 2.5)
        new_label1_bg = BackgroundRectangle(new_label1, fill_color=BG_COLOR, fill_opacity=0.9, buff=0.1)
        new_label2 = Tex("pair choices", font_size=24, color=SECONDARY_COLOR)
        new_label2.next_to(new_main, DOWN, buff=0.5)
        new_label2_bg = BackgroundRectangle(new_label2, fill_color=BG_COLOR, fill_opacity=0.9, buff=0.1)
        new_label3 = Tex("possible answers", font_size=24, color=SECONDARY_COLOR)
        new_label3.next_to(new_main, DOWN, buff=0.5).shift(RIGHT * 2.5)
        new_label3_bg = BackgroundRectangle(new_label3, fill_color=BG_COLOR, fill_opacity=0.9, buff=0.1)

        self.play(
            FadeOut(st["seven_label"]), FadeOut(st["seven_label_bg"]), FadeIn(new_label1_bg), FadeIn(new_label1),
            FadeOut(st["pair_label_grp"]), FadeIn(new_label2_bg), FadeIn(new_label2),
            FadeOut(st["counter_label"]), FadeOut(st["counter_label_bg"]), FadeIn(new_label3_bg), FadeIn(new_label3),
            run_time=1.0,
        )
        st["seven_label"] = new_label1
        st["pair_label_grp"] = new_label2
        st["counter_label"] = new_label3

        dots3 = self.dots_grid(spacing=0.6, offset=(0.15, 0.45), opacity=0.0)
        self.play(
            *[d.animate.scale(1.5).set_opacity(0.25) for d in self._dots],
            dots3.animate.set_opacity(0.25),
            run_time=1.0,
        )
        self._dots.append(dots3)

        cap = self.swap_caption("A real hall is far bigger.")
        self.wait(1.2)

        self.background_items = [*self._dots]
        self.layout_items = [
            top_line2_bg, top_line2, new_main_bg, old_group,
            new_label1_bg, st["seven_label"], new_label2_bg, st["pair_label_grp"],
            new_label3_bg, st["counter_label"], cap,
        ]
        self.allowed_overlaps = {(0, 1), (2, 3), (4, 5), (6, 7), (8, 9)}
        self.check_layout("5_4")

        cap2 = self.swap_caption("Trying every answer one by one is impossible.")
        self.wait(1.5)
        cap3 = self.swap_caption("We need a smarter way to search.")
        self.wait(2.0)

        self.play(
            FadeOut(self._title), FadeOut(top_line2_bg), FadeOut(top_line2),
            FadeOut(new_main_bg), FadeOut(old_group),
            FadeOut(new_label1_bg), FadeOut(st["seven_label"]),
            FadeOut(new_label2_bg), FadeOut(st["pair_label_grp"]),
            FadeOut(new_label3_bg), FadeOut(st["counter_label"]),
            FadeOut(cap3), *[FadeOut(d) for d in self._dots],
            run_time=1.0,
        )
        self.current_caption = None
