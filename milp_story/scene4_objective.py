"""Scene 4 — linearizing "minimize the maximum".

The trick that trips people up: how do you turn "minimize the worst
outcome across many scenarios" into something a linear solver can chew?
Answer: give every scenario its own bar, force M to sit above every bar
(M >= load), then push M down until it just touches the tallest one.
Objective is really M + tiny*sum(all loads) — the epsilon term only
breaks ties, so it gets a short, separate beat instead of being folded
into the main idea.
"""
from manim import *
from common import thai, title_card, caption, OK_COLOR, WARN_COLOR, FAIL_COLOR

BAR_VALUES = [1.2, 2.6, 1.8, 3.4, 2.1, 2.9, 1.5, 2.4, 3.0, 1.9]
MAX_VAL = 3.4


class Scene4_Objective(Scene):
    def construct(self):
        title = title_card("Objective: linearize the minimax", "M ต้องมากกว่าหรือเท่ากับทุกโหลดที่เป็นไปได้")
        self.play(FadeIn(title))

        cap1 = caption("ทุกจุด (กลุ่ม × ใครพัง × ใครรับ) คือแท่งโหลดหนึ่งแท่ง")
        self.play(FadeIn(cap1))

        bars = VGroup()
        for v in BAR_VALUES:
            bar = Rectangle(width=0.5, height=v, fill_color=OK_COLOR, fill_opacity=0.85, stroke_width=0)
            bars.add(bar)
        bars.arrange(RIGHT, buff=0.25, aligned_edge=DOWN)
        bars.move_to(DOWN * 1.1)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.08))
        self.wait(0.4)
        self.play(FadeOut(cap1))

        cap2 = caption("บังคับ M ≥ ทุกแท่ง (constraint ธรรมดา ไม่ใช่ non-linear)")
        self.play(FadeIn(cap2))

        top_y = bars.get_top()[1] + 1.2
        m_line = DashedLine(
            [bars.get_left()[0] - 0.4, top_y, 0], [bars.get_right()[0] + 0.4, top_y, 0],
            color=FAIL_COLOR, stroke_width=6,
        )
        m_label = thai("M", size=30, color=FAIL_COLOR, weight=BOLD)
        m_label.next_to(m_line, RIGHT, buff=0.3)
        self.play(Create(m_line), FadeIn(m_label))
        self.wait(0.3)

        ge_arrows = VGroup()
        for bar in bars:
            top = bar.get_top()
            arrow = Arrow(top, [top[0], top_y - 0.1, 0], buff=0.05, color=WHITE, stroke_width=2, max_tip_length_to_length_ratio=0.15)
            ge_arrows.add(arrow)
        self.play(LaggedStart(*[GrowArrow(a) for a in ge_arrows], lag_ratio=0.05))
        self.wait(0.6)
        self.play(FadeOut(ge_arrows), FadeOut(cap2))

        # ── push M down until it just touches the tallest bar = minimize M ──
        cap3 = caption("minimize M = ดันเส้นนี้ลงให้ต่ำที่สุดเท่าที่จะทำได้ โดยห้ามต่ำกว่าแท่งไหนเลย")
        self.play(FadeIn(cap3))

        target_y = bars.get_top()[1] + 0.05
        self.play(
            m_line.animate.move_to([m_line.get_center()[0], target_y, 0]),
            m_label.animate.shift(UP * (target_y - top_y)),
            run_time=1.8,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.play(Indicate(bars[3], color=FAIL_COLOR, scale_factor=1.05))
        touch_note = thai("แตะแท่งที่สูงที่สุดพอดี → M* = max-fail-load ที่ต่ำที่สุดที่เป็นไปได้", size=22, color=FAIL_COLOR)
        touch_note.next_to(m_line, UP, buff=0.25)
        self.play(FadeIn(touch_note))
        self.wait(1.0)
        self.play(FadeOut(cap3), FadeOut(touch_note))

        # ── epsilon tie-break, kept short and clearly secondary ──
        cap4 = caption("รายละเอียดเสริม: บวก epsilon×(โหลดรวม) เล็กมาก ๆ กัน M เท่ากันแต่จัดเบี้ยว")
        self.play(FadeIn(cap4))

        eps_formula = thai("objective จริง = M + ε × Σ(โหลดทุกจุด),  ε = 0.00001", size=24, color=GRAY_B)
        eps_formula.next_to(m_line, DOWN, buff=2.0)
        self.play(FadeIn(eps_formula))
        eps_note = thai("ε เล็กจนไม่แย่งความสำคัญจาก M เลย — แค่เลือกคำตอบที่ “เนียนกว่า” เวลา M เท่ากัน", size=20, color=GRAY_B)
        eps_note.next_to(eps_formula, DOWN, buff=0.25)
        self.play(FadeIn(eps_note))
        self.wait(1.1)
        self.play(*[FadeOut(m) for m in self.mobjects])
