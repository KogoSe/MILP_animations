"""Scene 3 — turning the picture into MILP variables.

Three variables carry the whole model: t[i,g] (a cumulative "is row i in
group <= g?" flag that avoids enumerating every cut), q[i,g,p] (which of
the 6 pairs row i uses, if it lands in group g), and M (the worst-case
load we're about to minimize in scene 4). The telescoping trick — that
"row i is in group g" is just t[i,g] - t[i,g-1] and never its own
variable — is the one idea worth slowing down for.
"""
from manim import *
from common import (
    thai, title_card, caption, PAIR_COLORS, PAIRS, OK_COLOR, WARN_COLOR, FAIL_COLOR,
)

N_ROWS = 6
ON_COLOR = "#3DDC84"
OFF_COLOR = "#3A3A3A"
BAND_COLOR = "#FFD866"


def make_row_square(i, size=0.9):
    box = Square(side_length=size, fill_color=OFF_COLOR, fill_opacity=1, stroke_color=WHITE, stroke_width=2)
    lbl = thai(str(i + 1), size=22, color=WHITE)
    lbl.move_to(box.get_center())
    return VGroup(box, lbl)


class Scene3_Variables(Scene):
    def construct(self):
        title = title_card("เข้ารหัสเป็นตัวแปร MILP", "3 ตัวแปรหลักที่ solver จะเล่นด้วย")
        self.play(FadeIn(title))

        rows = VGroup(*[make_row_square(i) for i in range(N_ROWS)])
        rows.arrange(RIGHT, buff=0.3)
        rows.move_to(UP * 1.6)
        self.play(LaggedStart(*[FadeIn(r, shift=UP * 0.2) for r in rows], lag_ratio=0.1))
        self.wait(0.3)

        # ── t[i,g]: cumulative threshold ──
        cap1 = caption("t[i, g] = “แถว i อยู่กลุ่ม ≤ g หรือเปล่า?” (binary)")
        self.play(FadeIn(cap1))

        def threshold_line(after_idx):
            x = (rows[after_idx].get_right()[0] + rows[after_idx + 1].get_left()[0]) / 2
            return DashedLine(
                [x, rows.get_top()[1] + 0.15, 0], [x, rows.get_bottom()[1] - 0.7, 0],
                color=WARN_COLOR, stroke_width=5,
            )

        g_label = thai("g = 1", size=28, color=WARN_COLOR, weight=BOLD)
        g_label.next_to(rows, RIGHT, buff=1.0)
        self.play(FadeIn(g_label))

        line = threshold_line(1)  # boundary after row index 1 (rows 1,2 are "<=1")
        self.play(Create(line))

        def color_left_of(cut_after):
            anims = []
            for idx, r in enumerate(rows):
                color = ON_COLOR if idx <= cut_after else OFF_COLOR
                anims.append(r[0].animate.set_fill(color))
            return anims

        t_labels = VGroup()
        for idx, r in enumerate(rows):
            val = 1 if idx <= 1 else 0
            lbl = thai(f"t={val}", size=16, color=(OK_COLOR if val else GRAY_B))
            lbl.next_to(r, DOWN, buff=0.15)
            t_labels.add(lbl)
        self.play(*color_left_of(1), FadeIn(t_labels))
        self.wait(0.6)

        cap1b = caption("เลื่อน g ไปเรื่อย ๆ ก็ได้ threshold ใหม่ — ไม่ต้อง enumerate จุดตัดทุกแบบ")
        self.play(Transform(cap1, cap1b))

        line2 = threshold_line(3)
        new_g_label = thai("g = 2", size=28, color=WARN_COLOR, weight=BOLD)
        new_g_label.move_to(g_label.get_center())
        self.play(
            Transform(line, line2),
            Transform(g_label, new_g_label),
            *color_left_of(3),
            *self.__t_label_anims(t_labels, cut_after=3),
        )
        self.wait(0.6)
        self.play(FadeOut(cap1), FadeOut(t_labels), FadeOut(line), FadeOut(g_label))
        self.play(*[r[0].animate.set_fill(OFF_COLOR) for r in rows])

        # ── telescoping: y[i,g] = t[i,g] - t[i,g-1] is just a band, not a variable ──
        cap2 = caption("“แถว i อยู่กลุ่ม g พอดี” ไม่ใช่ตัวแปรใหม่ — เป็นแค่ช่องว่างระหว่าง t สองค่า")
        self.play(FadeIn(cap2))

        line_lo = threshold_line(1)
        line_hi = threshold_line(3)
        lbl_lo = thai("t[i,1]", size=20, color=WARN_COLOR).next_to(line_lo, UP, buff=0.15)
        lbl_hi = thai("t[i,2]", size=20, color=WARN_COLOR).next_to(line_hi, UP, buff=0.15)
        self.play(Create(line_lo), Create(line_hi), FadeIn(lbl_lo), FadeIn(lbl_hi))

        band = Rectangle(
            width=(line_hi.get_center()[0] - line_lo.get_center()[0]),
            height=rows.height + 0.6,
            fill_color=BAND_COLOR, fill_opacity=0.35, stroke_width=0,
        )
        band.move_to([(line_lo.get_center()[0] + line_hi.get_center()[0]) / 2, rows.get_center()[1], 0])
        self.play(FadeIn(band))
        y_formula = thai("y[i, 2] = t[i,2] − t[i,1]", size=26, color=BAND_COLOR, weight=BOLD)
        y_formula.next_to(rows, DOWN, buff=1.2)
        self.play(FadeIn(y_formula, shift=UP * 0.2))
        self.wait(0.9)
        self.play(FadeOut(cap2), FadeOut(band), FadeOut(line_lo), FadeOut(line_hi),
                   FadeOut(lbl_lo), FadeOut(lbl_hi), FadeOut(y_formula))

        # ── q[i,g,p]: which pair does a 2-source row use ──
        cap3 = caption("q[i, g, p] = “แถว i อยู่กลุ่ม g และเลือกใช้ pair p” (binary)")
        self.play(FadeIn(cap3))

        target_row = rows[2]
        self.play(Indicate(target_row, color=WARN_COLOR, scale_factor=1.2))

        dials = VGroup()
        for p in PAIRS:
            chip = RoundedRectangle(corner_radius=0.08, width=0.9, height=0.5,
                                     fill_color=PAIR_COLORS[p], fill_opacity=0.4, stroke_color=WHITE, stroke_width=1.5)
            lbl = thai(p, size=18, color=WHITE)
            lbl.move_to(chip.get_center())
            dials.add(VGroup(chip, lbl))
        dials.arrange(RIGHT, buff=0.2)
        dials.next_to(target_row, DOWN, buff=1.0)
        self.play(LaggedStart(*[FadeIn(d, shift=UP * 0.1) for d in dials], lag_ratio=0.08))
        self.wait(0.3)

        chosen = dials[3]  # BC
        self.play(chosen[0].animate.set_fill(opacity=1.0).set_stroke(width=3, color=OK_COLOR))
        self.play(Indicate(chosen, color=OK_COLOR, scale_factor=1.15))
        others_note = thai("เหลืออีก 5 ตัวถูกบังคับให้เป็น 0 โดย constraint sum(q) = y[i,g]", size=20, color=GRAY_B)
        others_note.next_to(dials, DOWN, buff=0.35)
        self.play(FadeIn(others_note))
        self.wait(0.9)
        self.play(FadeOut(cap3), FadeOut(dials), FadeOut(others_note))

        # ── M: the continuous variable we'll minimize next ──
        cap4 = caption("M = ตัวแปรต่อเนื่อง แทน “โหลดสูงสุดที่เป็นไปได้” — ตัวที่เราจะ minimize")
        self.play(FadeIn(cap4))

        m_line = DashedLine(LEFT * 4 + DOWN * 0.5, RIGHT * 4 + DOWN * 0.5, color=FAIL_COLOR, stroke_width=6)
        m_line.move_to(DOWN * 0.5)
        m_label = thai("M", size=30, color=FAIL_COLOR, weight=BOLD)
        m_label.next_to(m_line, RIGHT, buff=0.3)
        self.play(Create(m_line), FadeIn(m_label))
        self.play(m_line.animate.shift(UP * 0.4), m_label.animate.shift(UP * 0.4), run_time=0.6)
        self.play(m_line.animate.shift(DOWN * 0.7), m_label.animate.shift(DOWN * 0.7), run_time=0.6)
        note = thai("(ต่อไป: ทำไมค่านี้ minimize-the-maximum ได้แบบ linear)", size=22, color=GRAY_B)
        note.next_to(m_line, DOWN, buff=0.5)
        self.play(FadeIn(note))
        self.wait(1.0)
        self.play(*[FadeOut(m) for m in self.mobjects])

    @staticmethod
    def __t_label_anims(t_labels, cut_after):
        anims = []
        for idx, lbl in enumerate(t_labels):
            val = 1 if idx <= cut_after else 0
            new_lbl = thai(f"t={val}", size=16, color=(OK_COLOR if val else GRAY_B))
            new_lbl.move_to(lbl.get_center())
            anims.append(Transform(lbl, new_lbl))
        return anims
