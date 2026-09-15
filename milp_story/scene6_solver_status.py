"""Scene 6 — proven optimal vs time-limited, and what "gap" means.

PuLP's own LpStatus calls both outcomes "Optimal", which is why this
project parses the raw CBC log text instead. The visual: one log feeds
into two different real-world outcomes that look identical from the
outside, then a number-line showing what "gap" physically means (the
distance between the best answer found and the best lower bound CBC can
prove).
"""
from manim import *
from common import thai, title_card, caption, OK_COLOR, WARN_COLOR, FAIL_COLOR


class Scene6_SolverStatus(Scene):
    def construct(self):
        title = title_card("Solver status: proven optimal vs time-limited", "PuLP บอกแค่ “Optimal” เหมือนกันทั้งคู่ — ต้องอ่าน log CBC เอง")
        self.play(FadeIn(title))

        cap1 = caption("PuLP's LpStatus มองไม่เห็นความต่าง...")
        self.play(FadeIn(cap1))

        pulp_box = RoundedRectangle(corner_radius=0.1, width=4.2, height=1.0, fill_color="#2A2A2A", fill_opacity=1, stroke_color=GRAY_B)
        pulp_txt = thai("LpStatus[prob.status] = “Optimal”", size=22, color=WHITE)
        pulp_txt.move_to(pulp_box)
        pulp_grp = VGroup(pulp_box, pulp_txt).move_to(UP * 1.8)
        self.play(FadeIn(pulp_grp))
        self.wait(0.5)
        self.play(FadeOut(cap1))

        cap2 = caption("...แต่จริง ๆ อาจเป็นได้ 2 แบบที่ต่างกันโดยสิ้นเชิง — ต้องแกะ log CBC เอง")
        self.play(FadeIn(cap2))

        arrow_l = Arrow(pulp_grp.get_bottom(), pulp_grp.get_bottom() + DOWN * 1.2 + LEFT * 2.6, color=GRAY_B, buff=0.1)
        arrow_r = Arrow(pulp_grp.get_bottom(), pulp_grp.get_bottom() + DOWN * 1.2 + RIGHT * 2.6, color=GRAY_B, buff=0.1)
        self.play(GrowArrow(arrow_l), GrowArrow(arrow_r))

        left_box = RoundedRectangle(corner_radius=0.1, width=3.6, height=1.5, fill_color="#123822", fill_opacity=1, stroke_color=OK_COLOR, stroke_width=2)
        left_txt = thai('"Result - Optimal\nsolution found"', size=18, color=OK_COLOR)
        left_txt.move_to(left_box)
        left_grp = VGroup(left_box, left_txt)
        left_grp.next_to(arrow_l, DOWN, buff=0.1).align_to(pulp_grp, LEFT).shift(LEFT * 1.6)

        right_box = RoundedRectangle(corner_radius=0.1, width=3.6, height=1.5, fill_color="#3A2A10", fill_opacity=1, stroke_color=WARN_COLOR, stroke_width=2)
        right_txt = thai('"Stopped on\ntime limit"', size=18, color=WARN_COLOR)
        right_txt.move_to(right_box)
        right_grp = VGroup(right_box, right_txt)
        right_grp.next_to(arrow_r, DOWN, buff=0.1).align_to(pulp_grp, RIGHT).shift(RIGHT * 1.6)

        self.play(FadeIn(left_grp, shift=DOWN * 0.2), FadeIn(right_grp, shift=DOWN * 0.2))
        self.wait(0.4)

        left_label = thai("proven_optimal = True", size=18, color=OK_COLOR)
        left_label.next_to(left_grp, DOWN, buff=0.2)
        right_label = thai("time_limited = True", size=18, color=WARN_COLOR)
        right_label.next_to(right_grp, DOWN, buff=0.2)
        self.play(FadeIn(left_label), FadeIn(right_label))
        self.wait(1.0)
        self.play(FadeOut(cap2))

        cap3 = caption("ความต่างสำคัญคือ “gap” — ระยะห่างระหว่างคำตอบที่ได้กับ lower bound ที่พิสูจน์ได้")
        self.play(
            FadeOut(pulp_grp), FadeOut(arrow_l), FadeOut(arrow_r),
            FadeOut(left_grp), FadeOut(right_grp), FadeOut(left_label), FadeOut(right_label),
            FadeIn(cap3),
        )

        # ── number line: proven optimal (gap = 0) ──
        line1 = NumberLine(x_range=[0, 10, 1], length=6, color=GRAY_B)
        line1.move_to(UP * 0.9)
        lbl1 = thai("proven optimal", size=20, color=OK_COLOR)
        lbl1.next_to(line1, LEFT, buff=0.3)
        best1 = Dot(line1.n2p(6.2), color=OK_COLOR, radius=0.1)
        lb1 = Dot(line1.n2p(6.2), color=WHITE, radius=0.06)
        best1_lbl = thai("M* = 6.2", size=16, color=OK_COLOR).next_to(best1, UP, buff=0.25)
        gap1_lbl = thai("gap = 0%", size=18, color=OK_COLOR, weight=BOLD).next_to(line1, RIGHT, buff=0.4)

        self.play(Create(line1), FadeIn(lbl1))
        self.play(FadeIn(best1), FadeIn(best1_lbl), FadeIn(lb1))
        self.play(FadeIn(gap1_lbl))
        self.wait(0.5)

        # ── number line: time-limited (gap > 0) ──
        line2 = NumberLine(x_range=[0, 10, 1], length=6, color=GRAY_B)
        line2.move_to(DOWN * 1.3)
        lbl2 = thai("time-limited", size=20, color=WARN_COLOR)
        lbl2.next_to(line2, LEFT, buff=0.3)
        best2 = Dot(line2.n2p(6.8), color=WARN_COLOR, radius=0.1)
        lb2 = Dot(line2.n2p(5.9), color=WHITE, radius=0.08)
        best2_lbl = thai("best found = 6.8", size=16, color=WARN_COLOR).next_to(best2, UP, buff=0.25)
        lb2_lbl = thai("lower bound = 5.9", size=16, color=WHITE).next_to(lb2, DOWN, buff=0.25)
        gap_arrow = DoubleArrow(lb2.get_center(), best2.get_center(), color=FAIL_COLOR, buff=0.1, stroke_width=3)
        gap2_lbl = thai("gap ≈ 14%", size=18, color=FAIL_COLOR, weight=BOLD).next_to(line2, RIGHT, buff=0.4)

        self.play(Create(line2), FadeIn(lbl2))
        self.play(FadeIn(lb2), FadeIn(lb2_lbl), FadeIn(best2), FadeIn(best2_lbl))
        self.play(GrowArrow(gap_arrow), FadeIn(gap2_lbl))
        self.wait(1.0)
        self.play(FadeOut(cap3))

        note = thai(
            "gap = ระยะที่บอกว่า “คำตอบนี้อาจแย่กว่าคำตอบจริงได้แค่ไหน” ถ้า solver หยุดก่อนพิสูจน์เสร็จ",
            size=22, color=WHITE,
        )
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note))
        self.wait(1.2)
        self.play(*[FadeOut(m) for m in self.mobjects])
