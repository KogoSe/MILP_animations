"""Scene 1 — worst-case fault load.

Goal: make the audience *feel* what "max-fail-load" means before any
optimization talk starts. Four UPS units share PTU rows; when one UPS
dies, its rows must instantly reroute onto the others. A 4-source row
splits evenly three ways. A 2-source row depends entirely on which pair
it was wired to — that dependency is the whole reason this problem is hard.
"""
from manim import *
from common import (
    thai, title_card, ups_row, fail_mark, flow_arrow, caption,
    UPS_COLORS, PAIR_COLORS, FAIL_COLOR, OK_COLOR, WARN_COLOR,
)


def row_box(label_str, color, width=2.0, height=0.6):
    box = RoundedRectangle(corner_radius=0.08, width=width, height=height,
                            fill_color=color, fill_opacity=0.9, stroke_color=WHITE, stroke_width=1.5)
    txt = thai(label_str, size=20, color="#1B1B1B")
    txt.move_to(box.get_center())
    return VGroup(box, txt)


class Scene1_Problem(Scene):
    def construct(self):
        title = title_card("โจทย์ตั้งต้น", "ถ้า UPS ตัวหนึ่งพัง โหลดจะไปตกที่ไหน?")
        self.play(FadeIn(title))

        ups = ups_row(spacing=2.6)
        ups.move_to(UP * 1.0)
        self.play(LaggedStart(*[FadeIn(b, shift=DOWN * 0.3) for b in ups], lag_ratio=0.15))
        self.wait(0.3)

        # ── 4-source row wired to all four ──
        row4 = row_box("แถว 4-source\n(600 kW)", "#D8D2FF", width=2.4)
        row4.move_to(DOWN * 2.0 + LEFT * 3.4)
        self.play(FadeIn(row4, shift=UP * 0.2))

        lines4 = VGroup(*[
            Line(row4.get_top(), b.get_bottom(), stroke_color=GRAY_B, stroke_width=2)
            for b in ups
        ])
        self.play(LaggedStart(*[Create(l) for l in lines4], lag_ratio=0.1))
        self.wait(0.3)

        # ── 2-source row wired to pair A-B ──
        row2ab = row_box("แถว 2-source\npair AB (300 kW)", PAIR_COLORS["AB"], width=2.6)
        row2ab.move_to(DOWN * 2.0 + RIGHT * 3.4)
        self.play(FadeIn(row2ab, shift=UP * 0.2))

        line_a = Line(row2ab.get_top(), ups[0].get_bottom(), stroke_color=PAIR_COLORS["AB"], stroke_width=4)
        line_b = Line(row2ab.get_top(), ups[1].get_bottom(), stroke_color=PAIR_COLORS["AB"], stroke_width=4)
        self.play(Create(line_a), Create(line_b))
        self.wait(0.5)

        cap = caption("สมมติ UPS “B” พังกะทันหัน...")
        self.play(FadeIn(cap))

        b_box = ups[1]
        self.play(Indicate(b_box, color=FAIL_COLOR, scale_factor=1.15))
        x_mark = fail_mark(b_box, scale=1.3)
        self.play(Create(x_mark), b_box.animate.set_opacity(0.35))
        self.wait(0.4)

        # ── 4-source row reroutes: 200kW each to A, C, D ──
        self.play(FadeOut(cap))
        cap2 = caption("แถว 4-source: โหลดกระจายเท่า ๆ กันไปอีก 3 ตัว (kW/3)")
        self.play(FadeIn(cap2))

        arrows4 = VGroup()
        for target in (ups[0], ups[2], ups[3]):
            arrows4.add(flow_arrow(row4, target, "200 kW\n(33.3%)", color=OK_COLOR, width=5))
        self.play(FadeOut(lines4))
        self.play(LaggedStart(*[GrowArrow(a[0]) for a in arrows4], lag_ratio=0.15))
        self.play(LaggedStart(*[FadeIn(a[1]) for a in arrows4], lag_ratio=0.15))
        self.wait(0.6)
        self.play(FadeOut(cap2), FadeOut(arrows4))

        # ── 2-source AB row reroutes: since B failed and B is in the pair, ──
        # ── the full load goes to the partner A. C and D get nothing. ──
        cap3 = caption("แถว 2-source pair AB: B พัง (อยู่ใน pair) → A รับเต็ม 100%")
        self.play(FadeIn(cap3))
        self.play(FadeOut(line_a), FadeOut(line_b))
        full_arrow = flow_arrow(row2ab, ups[0], "300 kW\n(100%)", color=WARN_COLOR, width=7)
        self.play(GrowArrow(full_arrow[0]), FadeIn(full_arrow[1]))
        self.wait(0.6)
        self.play(FadeOut(cap3), FadeOut(full_arrow))

        # ── contrast: a 2-source row paired CD instead (B not involved) ──
        cap4 = caption("แต่ถ้าแถวนั้นจับคู่เป็น CD แทน (B ไม่เกี่ยวเลย) → C, D รับคนละ 50%")
        row2cd = row_box("แถว 2-source\npair CD (300 kW)", PAIR_COLORS["CD"], width=2.6)
        row2cd.move_to(row2ab.get_center())
        self.play(FadeIn(cap4), Transform(row2ab, row2cd))
        arrow_c = flow_arrow(row2ab, ups[2], "150 kW (50%)", color=OK_COLOR, width=5)
        arrow_d = flow_arrow(row2ab, ups[3], "150 kW (50%)", color=OK_COLOR, width=5)
        self.play(GrowArrow(arrow_c[0]), GrowArrow(arrow_d[0]))
        self.play(FadeIn(arrow_c[1]), FadeIn(arrow_d[1]))
        self.wait(0.8)
        self.play(FadeOut(cap4), FadeOut(arrow_c), FadeOut(arrow_d))

        # ── the punchline: pairing choice changes who bears the load ──
        punch = thai(
            "เห็นไหม? “จับคู่ไหน” กำหนดว่าโหลดจะตกหนักไปที่ตัวไหนตอน UPS พัง",
            size=28, color=WHITE,
        )
        punch.to_edge(DOWN, buff=0.6)
        self.play(FadeIn(punch))
        self.wait(1.0)
        self.play(FadeOut(punch))

        goal = thai(
            "เป้าหมาย: จัดกลุ่ม + จับคู่ ให้ “โหลดสูงสุดที่ตกหนักที่สุด” ในทุกกรณีพัง ต่ำที่สุด",
            size=30, color=WARN_COLOR, weight=BOLD,
        )
        goal.move_to(DOWN * 3.0)
        self.play(FadeIn(goal, shift=UP * 0.2))
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects])
