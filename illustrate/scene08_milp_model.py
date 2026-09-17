"""Scene 08 -- "The whole model"

Built strictly from scene08_prompt.md + common_prompt.md.

Starts from: black (Scene 07 ended on "Next: write 'worst case' in the
same language." then faded to black).

Ends with: fade to black after "Next: how a solver finds the best answer
without trying them all."

Run with:
    manim -pqh scene08_milp_model.py Scene08MilpModel
"""
from manim import *

from common.style import (
    BG_COLOR, TEXT_COLOR, SECONDARY_COLOR, UPS_COLORS,
    HL_COLOR, PAIR_COLOR, GROUP1_COLOR, FAIL_COLOR,
)
from common.layout import caption, title, LayoutCheckMixin
from common.data import SCENE08, fmt_kw

BAR_XS = [-5.6, -4.6, -3.6, -2.6, -1.6, -0.6]
BASELINE_Y = -1.9
SCALE = 3.4 / 1400
BAR_WIDTH = 0.6


def m_line_y(value):
    return BASELINE_Y + value * SCALE


class Scene08MilpModel(LayoutCheckMixin, Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        self.current_caption = None

        self.beat_8_1_max_not_linear()
        self.beat_8_2_push_down()
        self.beat_8_3_whole_model()
        self.beat_8_4_name()

    # --------------------------------------------------------- helpers ---
    def swap_caption(self, text):
        new_cap = caption(text)
        if self.current_caption is not None:
            self.play(FadeOut(self.current_caption))
        self.play(FadeIn(new_cap))
        self.current_caption = new_cap
        return new_cap

    def build_bars(self):
        loads = SCENE08["loads"]
        baseline = Line([-6.1, BASELINE_Y, 0], [-0.1, BASELINE_Y, 0], color=SECONDARY_COLOR, stroke_width=2)
        bars = []
        values = []
        labels = []
        for x, load in zip(BAR_XS, loads):
            h = load["kw"] * SCALE
            bar = Rectangle(width=BAR_WIDTH, height=h, fill_color=UPS_COLORS[load["survivor"]],
                             fill_opacity=1, stroke_width=0)
            bar.move_to([x, BASELINE_Y + h / 2, 0])
            val = Tex(f"{load['kw']:,}", font_size=22, color=UPS_COLORS[load["survivor"]])
            val.move_to([x, BASELINE_Y + h + 0.08 + val.height / 2, 0])
            lbl = MathTex(load["label"], font_size=26, color=TEXT_COLOR)
            lbl.move_to([x, -2.2, 0])
            bars.append(bar)
            values.append(val)
            labels.append(lbl)
        return dict(baseline=baseline, bars=bars, values=values, labels=labels)

    # ===================================================== Beat 8.1 =====
    def beat_8_1_max_not_linear(self):
        t = Tex("Worst case, in the same language", font_size=44, color=TEXT_COLOR)
        if t.width > 12.5:
            t = Tex("Worst case, in the same language", font_size=40, color=TEXT_COLOR)
        t.move_to([0, 3.15, 0])
        self.play(FadeIn(t, shift=DOWN * 0.15))

        b = self.build_bars()
        self.play(Create(b["baseline"]), *[FadeIn(l) for l in b["labels"]])
        self.play(LaggedStart(*[GrowFromEdge(bar, DOWN) for bar in b["bars"]], lag_ratio=0.25), run_time=1.5)
        self.play(*[FadeIn(v) for v in b["values"]])

        cap = self.swap_caption("Here are six loads from Group 2.")
        self.wait(1.0)

        max_eq = MathTex(r"M", r"= \max(L_1, \dots, L_6)", font_size=40)
        max_eq.set_color(TEXT_COLOR)
        max_eq.set_color_by_tex("M", HL_COLOR)
        max_eq.move_to([3.4, 1.4, 0])
        self.play(FadeIn(max_eq))

        cap2 = self.swap_caption("M is the largest of all the loads.")
        self.wait(1.0)

        note = Tex('"largest of" is not a linear rule', font_size=26, color=SECONDARY_COLOR)
        note.move_to([3.4, 0.6, 0])
        self.play(FadeIn(note))

        cap3 = self.swap_caption("But 'largest of' is not a linear rule.")
        self.wait(1.5)

        self.background_items = [b["baseline"]]
        self.layout_items = [t, *b["labels"], *b["values"], max_eq, note, cap3]
        self.allowed_overlaps = set()
        self.check_layout("8_1")

        self._title = t
        self._bars = b
        self._max_eq = max_eq
        self._note = note

    # ===================================================== Beat 8.2 =====
    def beat_8_2_push_down(self):
        loads = SCENE08["loads"]
        rules = []
        rule_xs = [1.9, 1.9, 1.9, 4.7, 4.7, 4.7]
        rule_ys = [1.9, 1.2, 0.5, 1.9, 1.2, 0.5]
        for load, x, y in zip(loads, rule_xs, rule_ys):
            r = MathTex("M", r"\ge", load["label"], font_size=34)
            r.set_color(TEXT_COLOR)
            r.set_color_by_tex("M", HL_COLOR)
            r.move_to([x, y, 0])
            rules.append(r)
        rules_grp = VGroup(*rules)

        self.play(
            Transform(self._max_eq, rules_grp[0]),
            FadeOut(self._note),
            *[FadeIn(rules[i]) for i in range(1, 6)],
            run_time=1.0,
        )
        rules[0] = self._max_eq

        cap = self.swap_caption("Instead, we ask M to be at least every load...")
        self.wait(1.0)

        tracker = ValueTracker(SCENE08["m_start"])

        def make_line():
            y = m_line_y(tracker.get_value())
            color = FAIL_COLOR if tracker.get_value() < SCENE08["m_final"] - 0.5 else HL_COLOR
            return DashedLine([-6.1, y, 0], [-0.3, y, 0], color=color, stroke_width=3)

        m_line = always_redraw(make_line)

        def make_label():
            y = m_line_y(tracker.get_value())
            color = FAIL_COLOR if tracker.get_value() < SCENE08["m_final"] - 0.5 else HL_COLOR
            lbl = Tex("M", font_size=30, color=color)
            lbl.move_to([-0.15 + lbl.width / 2, y, 0])
            return lbl

        m_label = always_redraw(make_label)

        readout_prefix = Tex("M = ", font_size=36, color=TEXT_COLOR)
        readout_num = DecimalNumber(tracker.get_value(), num_decimal_places=0, font_size=36,
                                     color=HL_COLOR, group_with_commas=True)
        readout_group = VGroup(readout_prefix, readout_num).arrange(RIGHT, buff=0.1)
        readout_group.move_to([3.4, -1.0, 0])
        readout_prefix.add_updater(lambda m: m.next_to(readout_num, LEFT, buff=0.1))

        def update_readout(m):
            m.set_value(tracker.get_value())
            m.set_color(FAIL_COLOR if tracker.get_value() < SCENE08["m_final"] - 0.5 else HL_COLOR)
            m.move_to([3.4 + readout_prefix.width / 2 + 0.05, -1.0, 0])

        readout_num.add_updater(update_readout)

        def outline_updater(idx):
            bar = self._bars["bars"][idx]
            def _update(m):
                kw = loads[idx]["kw"]
                visible = tracker.get_value() < kw - 0.5
                new = SurroundingRectangle(bar, color=FAIL_COLOR, buff=0.03, stroke_width=3)
                new.set_stroke(opacity=1 if visible else 0)
                m.become(new)
            return _update

        outline2 = VMobject()
        outline2.add_updater(outline_updater(1))
        outline6 = VMobject()
        outline6.add_updater(outline_updater(5))

        def rule_color_updater(idx):
            def _update(m):
                kw = loads[idx]["kw"]
                if tracker.get_value() < kw - 0.5:
                    m.set_color(FAIL_COLOR)
                else:
                    m.set_color(TEXT_COLOR)
                    m.set_color_by_tex("M", HL_COLOR)
            return _update

        rules[1].add_updater(rule_color_updater(1))
        rules[5].add_updater(rule_color_updater(5))

        self.add(m_line, m_label, outline2, outline6)
        self.play(FadeIn(readout_group))

        cap2 = self.swap_caption("...and then push M down as far as it can go.")
        self.play(tracker.animate.set_value(SCENE08["m_final"]), run_time=2.0)

        self.play(
            Indicate(self._bars["bars"][1]), Indicate(self._bars["bars"][5]),
            Indicate(rules[1]), Indicate(rules[5]),
        )

        cap3 = self.swap_caption("It stops at the tallest load --- exactly the worst case.")
        self.wait(0.4)

        self.play(tracker.animate.set_value(SCENE08["m_test_low"]), run_time=0.6)
        self.wait(0.8)
        self.play(tracker.animate.set_value(SCENE08["m_final"]), run_time=0.6)
        self.wait(0.4)

        note2 = Tex("as low as possible, but never below any load", font_size=24, color=SECONDARY_COLOR)
        note2.move_to([3.4, -1.7, 0])
        self.play(FadeIn(note2))
        self.wait(1.2)

        rules[1].clear_updaters()
        rules[5].clear_updaters()
        rules[1].set_color(TEXT_COLOR)
        rules[1].set_color_by_tex("M", HL_COLOR)
        rules[5].set_color(TEXT_COLOR)
        rules[5].set_color_by_tex("M", HL_COLOR)
        readout_num.clear_updaters()
        readout_num.set_value(SCENE08["m_final"])
        readout_num.set_color(HL_COLOR)
        readout_prefix.clear_updaters()
        readout_prefix.next_to(readout_num, LEFT, buff=0.1)
        outline2.clear_updaters()
        outline2.become(VMobject())
        outline6.clear_updaters()
        outline6.become(VMobject())

        self.background_items = [self._bars["baseline"], m_line]
        self.layout_items = [
            self._title, *self._bars["labels"], *self._bars["values"], *rules,
            m_label, readout_prefix, readout_num, note2,
        ]
        self.allowed_overlaps = set()
        self.check_layout("8_2")

        self._rules = rules
        self._m_line = m_line
        self._m_label = m_label
        self._readout_prefix = readout_prefix
        self._readout_num = readout_num
        self._note2 = note2
        self._outline2 = outline2
        self._outline6 = outline6
        self._tracker = tracker

    # ===================================================== Beat 8.3 =====
    def beat_8_3_whole_model(self):
        self.play(
            FadeOut(VGroup(
                *self._bars["bars"], *self._bars["labels"], *self._bars["values"],
                self._bars["baseline"], *self._rules, self._m_line, self._m_label,
                self._readout_prefix, self._readout_num, self._note2,
                self._outline2, self._outline6,
            )),
            FadeOut(self.current_caption),
        )
        self.current_caption = None

        new_title = title("The whole model")
        self.play(Transform(self._title, new_title), run_time=0.6)

        model_lines = SCENE08["model_lines"]
        eq_ys = [2.20, 1.52, 0.84, 0.16, -0.52, -1.20, -1.88]
        eq_mobjs = []
        label_mobjs = []
        font = 32
        for entry in model_lines:
            eq = MathTex(entry["tex"], font_size=font)
            eq.set_color(TEXT_COLOR)
            eq.set_color_by_tex("M", HL_COLOR)
            eq.set_color_by_tex("q", PAIR_COLOR)
            eq.set_color_by_tex("t_{i", GROUP1_COLOR)
            eq.set_color_by_tex("y_{i", GROUP1_COLOR)
            eq_mobjs.append(eq)
        max_right = max(-5.8 + e.width for e in eq_mobjs)
        if max_right > 1.3:
            font = 30
            eq_mobjs = []
            for entry in model_lines:
                eq = MathTex(entry["tex"], font_size=font)
                eq.set_color(TEXT_COLOR)
                eq.set_color_by_tex("M", HL_COLOR)
                eq.set_color_by_tex("q", PAIR_COLOR)
                eq.set_color_by_tex("t_{i", GROUP1_COLOR)
                eq.set_color_by_tex("y_{i", GROUP1_COLOR)
                eq_mobjs.append(eq)

        captions_for_lines = [
            "Goal: make M as small as possible.",
            "M must be at least every load.",
            "Each load follows the recipe from before.",
            "Each 2-source row takes one pair, inside its group.",
            "Groups stay continuous.",
            "The cut switches tell us each row's group.",
            "And every decision is a 0/1 switch.",
        ]

        for i, (entry, y, eq) in enumerate(zip(model_lines, eq_ys, eq_mobjs)):
            eq.move_to([-5.8 + eq.width / 2, y, 0])
            lbl = Tex(entry["label"], font_size=24, color=SECONDARY_COLOR)
            lbl.move_to([1.6 + lbl.width / 2, y, 0])
            label_mobjs.append(lbl)
            self.play(Write(eq), FadeIn(lbl), run_time=1.0)
            self.swap_caption(captions_for_lines[i])

        footnote = Tex(
            r"The app minimises M + 0.00001 $\times$ (sum of all loads): a tiny "
            r"tie-break, far too small to change the worst case.",
            font_size=22, color=SECONDARY_COLOR,
        )
        if footnote.width > 12.5:
            footnote = Tex(
                "The app adds a tiny tie-break term to M; it does not change the worst case.",
                font_size=22, color=SECONDARY_COLOR,
            )
        footnote.move_to([0, -2.45, 0])
        self.play(FadeIn(footnote))

        cap = self.swap_caption("Grouping and pairing are decided together, in one model.")
        self.wait(2.0)

        self.layout_items = [self._title, *eq_mobjs, *label_mobjs, footnote, cap]
        self.allowed_overlaps = set()
        self.check_layout("8_3")

        self._eq_mobjs = eq_mobjs
        self._label_mobjs = label_mobjs
        self._footnote = footnote
        self._model_card = VGroup(*eq_mobjs, *label_mobjs, footnote)

    # ===================================================== Beat 8.4 =====
    def beat_8_4_name(self):
        self.play(self._model_card.animate.set_opacity(0.2))

        name_title = Tex("Mixed-Integer Linear Program", font_size=48, color=TEXT_COLOR)
        name_title.move_to([0, 0.9, 0])
        name_bg = BackgroundRectangle(name_title, fill_color=BG_COLOR, fill_opacity=0.92, buff=0.3)
        self.play(FadeIn(name_bg), Write(name_title))

        cap = self.swap_caption("This kind of model is called a Mixed-Integer Linear Program.")
        self.wait(1.0)

        mixed_line = Tex("Mixed: M is any number; t and q are 0 or 1", font_size=26, color=TEXT_COLOR)
        mixed_line.move_to([0, -0.1, 0])
        mixed_bg = BackgroundRectangle(mixed_line, fill_color=BG_COLOR, fill_opacity=0.92, buff=0.15)
        self.play(FadeIn(mixed_bg), FadeIn(mixed_line))
        self.play(Indicate(self._eq_mobjs[6], color=HL_COLOR))

        linear_line = Tex("Linear: every rule is a sum of number $\\times$ variable",
                           font_size=26, color=TEXT_COLOR)
        linear_line.move_to([0, -0.7, 0])
        linear_bg = BackgroundRectangle(linear_line, fill_color=BG_COLOR, fill_opacity=0.92, buff=0.15)
        self.play(FadeIn(linear_bg), FadeIn(linear_line))
        self.play(Indicate(self._eq_mobjs[2], color=PAIR_COLOR))

        solved_line = Tex("Solved in the app with PuLP + CBC", font_size=24, color=SECONDARY_COLOR)
        solved_line.move_to([0, -1.5, 0])
        solved_bg = BackgroundRectangle(solved_line, fill_color=BG_COLOR, fill_opacity=0.92, buff=0.15)
        self.play(FadeIn(solved_bg), FadeIn(solved_line))

        new_name = Tex("Mixed-Integer Linear Program (MILP)", font_size=40, color=TEXT_COLOR)
        if new_name.width > 12.5:
            new_name = Tex("Mixed-Integer Linear Program (MILP)", font_size=36, color=TEXT_COLOR)
        new_name.move_to(name_title.get_center())
        new_name_bg = BackgroundRectangle(new_name, fill_color=BG_COLOR, fill_opacity=0.92, buff=0.3)
        self.play(
            Transform(name_title, new_name), Transform(name_bg, new_name_bg), run_time=0.8,
        )

        self.background_items = [self._model_card]
        self.layout_items = [
            name_bg, name_title, mixed_bg, mixed_line, linear_bg, linear_line,
            solved_bg, solved_line,
        ]
        self.allowed_overlaps = {(0, 1), (2, 3), (4, 5), (6, 7)}
        self.check_layout("8_4")

        cap2 = self.swap_caption(
            "Next: how a solver finds the best answer without trying them all."
        )
        self.wait(2.0)

        self.play(
            FadeOut(self._model_card), FadeOut(name_bg), FadeOut(name_title),
            FadeOut(mixed_bg), FadeOut(mixed_line), FadeOut(linear_bg), FadeOut(linear_line),
            FadeOut(solved_bg), FadeOut(solved_line), FadeOut(self._title), FadeOut(cap2),
            run_time=1.0,
        )
        self.current_caption = None
