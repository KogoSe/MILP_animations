"""Scene 8 — before/after payoff.

All numbers below are PLACEHOLDERS (clearly marked), not real project
output. Swap PLACEHOLDER_DATA once real numbers are pulled from
solve_pairing_milp() on an actual dataset — nothing else in this scene
needs to change.
"""
from manim import *
from common import thai, title_card, caption, OK_COLOR, WARN_COLOR, FAIL_COLOR

# ── PLACEHOLDER DATA — replace with real solve_pairing_milp() output ──
PLACEHOLDER_DATA = {
    "naive_M": 410,
    "milp_M": 290,
    "theoretical_lower_bound": 275,
    "global_theoretical_lower_bound": 258,
    "gap_pct": 0.8,
    "status": "Optimal (proven)",
    "n_groups": 5,
}
MAX_SCALE = 450


class Scene8_Results(Scene):
    def construct(self):
        title = title_card("สรุปผลลัพธ์")
        self.play(FadeIn(title))
        warn = thai("⚠ ตัวเลขในฉากนี้เป็น placeholder — รอสลับเป็นข้อมูลจริงจากโปรเจกต์", size=22, color=WARN_COLOR)
        warn.next_to(title, DOWN, buff=0.25)
        self.play(FadeIn(warn))
        self.wait(0.8)
        self.play(FadeOut(warn))

        d = PLACEHOLDER_DATA

        def meter(value, color, width=6.5, height=0.7):
            frac = value / MAX_SCALE
            back = Rectangle(width=width, height=height, stroke_color=GRAY_B, fill_color="#2A2A2A", fill_opacity=1)
            fill = Rectangle(width=width * frac, height=height, fill_color=color, fill_opacity=1, stroke_width=0)
            fill.align_to(back, LEFT)
            return VGroup(back, fill)

        naive_label = thai("จัดกลุ่ม/จับคู่แบบสุ่ม (ไม่ optimize)", size=24, color=WHITE)
        naive_meter = meter(d["naive_M"], FAIL_COLOR)
        naive_val = thai(f"M = {d['naive_M']} kW", size=24, color=FAIL_COLOR, weight=BOLD)
        naive_row = VGroup(naive_label, naive_meter, naive_val).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        naive_row.move_to(UP * 1.6)

        milp_label = thai("จัดกลุ่ม/จับคู่ด้วย MILP", size=24, color=WHITE)
        milp_meter = meter(d["milp_M"], OK_COLOR)
        milp_val = thai(f"M* = {d['milp_M']} kW", size=24, color=OK_COLOR, weight=BOLD)
        milp_row = VGroup(milp_label, milp_meter, milp_val).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        milp_row.move_to(DOWN * 0.6)

        self.play(FadeIn(naive_row, shift=RIGHT * 0.2))
        self.wait(0.4)
        self.play(FadeIn(milp_row, shift=RIGHT * 0.2))
        self.wait(0.6)

        reduction_pct = round((1 - d["milp_M"] / d["naive_M"]) * 100)
        reduction = thai(f"ลดโหลดสูงสุดที่ต้องเผื่อไว้ลง ~{reduction_pct}%", size=28, color=WARN_COLOR, weight=BOLD)
        reduction.next_to(milp_row, DOWN, buff=0.6)
        self.play(FadeIn(reduction, scale=1.1))
        self.wait(0.8)

        # ── reference lines: how close to the theoretical floor ──
        cap2 = caption("แล้ว M* ใกล้ “พื้นที่ต่ำสุดในทางทฤษฎี” แค่ไหน?")
        self.play(FadeIn(cap2), FadeOut(reduction))

        floor_x = naive_meter.get_left()[0] + (d["theoretical_lower_bound"] / MAX_SCALE) * naive_meter.width
        global_floor_x = naive_meter.get_left()[0] + (d["global_theoretical_lower_bound"] / MAX_SCALE) * naive_meter.width

        floor_line = DashedLine(
            [floor_x, milp_row.get_top()[1] + 0.3, 0], [floor_x, milp_row.get_bottom()[1] - 0.3, 0],
            color=WHITE, stroke_width=3,
        )
        floor_lbl = thai(f"lower bound (กลุ่มนี้) = {d['theoretical_lower_bound']}", size=16, color=WHITE)
        floor_lbl.next_to(floor_line, UP, buff=0.1)

        gfloor_line = DashedLine(
            [global_floor_x, milp_row.get_top()[1] + 0.3, 0], [global_floor_x, milp_row.get_bottom()[1] - 0.3, 0],
            color=GRAY_B, stroke_width=3,
        )
        gfloor_lbl = thai(f"floor ทฤษฎีล้วน ๆ = {d['global_theoretical_lower_bound']}", size=16, color=GRAY_B)
        gfloor_lbl.next_to(gfloor_line, DOWN, buff=0.5)

        self.play(Create(gfloor_line), FadeIn(gfloor_lbl))
        self.play(Create(floor_line), FadeIn(floor_lbl))
        self.wait(0.8)
        self.play(FadeOut(cap2))

        cap3 = caption(f"gap = {d['gap_pct']}%  |  status = “{d['status']}”  |  จำนวนกลุ่ม = {d['n_groups']}")
        self.play(FadeIn(cap3))
        self.wait(1.2)
        self.play(FadeOut(cap3), FadeOut(floor_line), FadeOut(floor_lbl), FadeOut(gfloor_line), FadeOut(gfloor_lbl))

        final = thai(
            "ความรอบคอบทั้งหมด — MILP + verification —\nแลกมาด้วยคำตอบที่ “ดีที่สุดเท่าที่พิสูจน์ได้” และ “ตรวจสอบซ้ำแล้ว”",
            size=24, color=WHITE,
        )
        final.move_to(DOWN * 2.6)
        self.play(FadeIn(final, shift=UP * 0.2))
        self.wait(1.6)
        self.play(*[FadeOut(m) for m in self.mobjects])
