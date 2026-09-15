"""Scene 2 — why a simple greedy / sort rule cannot work here.

Two independent choices stack on top of each other: where to cut the row
sequence into groups, and which of 6 pairs each 2-source row uses. The
audience should *see* the option count explode, then watch a "sensible"
greedy guess get beaten by a smarter arrangement on the same data.
"""
from manim import *
from common import (
    thai, title_card, caption, PAIR_COLORS, PAIRS, OK_COLOR, FAIL_COLOR, WARN_COLOR,
)

ROW_KW = [400, 250, 600, 300, 250, 500]
ROW_TYPE = ["2s", "4s", "2s", "2s", "4s", "2s"]  # 2-source / 4-source


def make_row_icon(kw, kind, width=1.1, height=1.0):
    color = "#D8D2FF" if kind == "4s" else PAIR_COLORS["AB"]
    box = RoundedRectangle(corner_radius=0.08, width=width, height=height,
                            fill_color=color, fill_opacity=0.9, stroke_color=WHITE, stroke_width=1.5)
    label = thai(f"{kw}", size=20, color="#1B1B1B")
    label.move_to(box.get_center() + UP * 0.15)
    tag = thai("4-src" if kind == "4s" else "2-src", size=14, color="#1B1B1B")
    tag.move_to(box.get_center() + DOWN * 0.28)
    return VGroup(box, label, tag)


class Scene2_Combinatorial(Scene):
    def construct(self):
        title = title_card("ทำไมเดา/เรียงลำดับธรรมดาไม่พอ", "โจทย์นี้มี 2 ทางเลือกซ้อนกัน")
        self.play(FadeIn(title))

        rows = VGroup(*[make_row_icon(kw, kind) for kw, kind in zip(ROW_KW, ROW_TYPE)])
        rows.arrange(RIGHT, buff=0.35)
        rows.move_to(UP * 1.5)
        self.play(LaggedStart(*[FadeIn(r, shift=UP * 0.2) for r in rows], lag_ratio=0.1))
        self.wait(0.3)

        # ── choice 1: where to cut into groups ──
        cap1 = caption("ทางเลือกที่ 1: จะตัดแถวเหล่านี้เป็นกลุ่มตรงไหนบ้าง?")
        self.play(FadeIn(cap1))

        def cut_line_at(i):
            x = (rows[i].get_right()[0] + rows[i + 1].get_left()[0]) / 2
            line = DashedLine(
                [x, rows.get_top()[1] + 0.3, 0], [x, rows.get_bottom()[1] - 0.3, 0],
                color=WARN_COLOR, stroke_width=5,
            )
            return line

        cut_options = [[1], [2, 4], [0, 3]]
        counter_label = thai("จำนวนวิธีแบ่งกลุ่ม: 1", size=26, color=WARN_COLOR)
        counter_label.next_to(rows, DOWN, buff=1.0).align_to(rows, LEFT)
        self.play(FadeIn(counter_label))

        current_cuts = VGroup()
        counts = [3, 5, 8]
        for cuts, n in zip(cut_options, counts):
            new_cuts = VGroup(*[cut_line_at(i) for i in cuts])
            new_counter = thai(f"จำนวนวิธีแบ่งกลุ่ม: {n}", size=26, color=WARN_COLOR)
            new_counter.move_to(counter_label, aligned_edge=LEFT)
            self.play(
                Transform(current_cuts, new_cuts) if len(current_cuts) else Create(new_cuts),
                Transform(counter_label, new_counter),
            )
            if len(current_cuts) == 0:
                current_cuts = new_cuts
            self.wait(0.3)
        self.play(FadeOut(current_cuts), FadeOut(cap1))

        # ── choice 2: which of 6 pairs each 2-source row uses ──
        cap2 = caption("ทางเลือกที่ 2: แต่ละแถว 2-source เลือก pair ไหนใน 6 แบบ?")
        self.play(FadeIn(cap2), FadeOut(counter_label))

        two_source_rows = [r for r, k in zip(rows, ROW_TYPE) if k == "2s"]
        dial_labels = VGroup()
        for r in two_source_rows:
            lbl = thai(PAIRS[0], size=16, color=WHITE, weight=BOLD)
            lbl.move_to(r.get_top() + UP * 0.35)
            dial_labels.add(lbl)
        self.play(LaggedStart(*[FadeIn(l) for l in dial_labels], lag_ratio=0.1))

        for _ in range(3):
            anims = []
            new_labels = []
            for lbl in dial_labels:
                nxt = PAIRS[(PAIRS.index(lbl.text) + 2) % len(PAIRS)]
                new_lbl = thai(nxt, size=16, color=WHITE, weight=BOLD)
                new_lbl.move_to(lbl.get_center())
                new_labels.append(new_lbl)
            for old, new in zip(dial_labels, new_labels):
                anims.append(Transform(old, new))
            self.play(*anims, run_time=0.4)
        self.wait(0.3)
        self.play(FadeOut(dial_labels), FadeOut(cap2))

        # ── combine: explosion of total combinations ──
        cap3 = caption("สองทางเลือกนี้คูณกัน → จำนวนความเป็นไปได้ทั้งหมดโตแบบก้าวกระโดด")
        self.play(FadeIn(cap3))

        big_number = thai("รวม ~8 กลุ่ม × 6⁴ pairing = 10,368 แบบ", size=32, color=FAIL_COLOR, weight=BOLD)
        big_number.move_to(DOWN * 1.6)
        self.play(FadeIn(big_number, scale=1.3))
        self.wait(0.6)
        grow_note = thai("(และยิ่งมีแถวเยอะขึ้น ตัวเลขนี้ยิ่งบวมเร็วกว่านี้อีกมาก)", size=22, color=GRAY_B)
        grow_note.next_to(big_number, DOWN, buff=0.3)
        self.play(FadeIn(grow_note))
        self.wait(0.8)
        self.play(FadeOut(cap3), FadeOut(big_number), FadeOut(grow_note))

        # ── greedy guess vs smarter arrangement, same data ──
        cap4 = caption("ลองเรียงจากหนักไปเบาแล้ววางแบบ “ดูดี ๆ” (greedy) ดูสิ...")
        self.play(FadeIn(cap4))
        self.wait(0.5)

        greedy_label = thai("Greedy: max-fail-load สูง", size=24, color=WHITE)
        greedy_meter_bg = Rectangle(width=4.0, height=0.5, stroke_color=GRAY_B, fill_color="#333333", fill_opacity=1)
        greedy_meter_fill = Rectangle(width=3.4, height=0.5, fill_color=FAIL_COLOR, fill_opacity=1, stroke_width=0)
        greedy_meter_fill.align_to(greedy_meter_bg, LEFT)
        greedy_group = VGroup(greedy_meter_bg, greedy_meter_fill)
        greedy_row = VGroup(greedy_label, greedy_group).arrange(DOWN, buff=0.2)
        greedy_row.move_to(UP * 0.2)

        best_label = thai("จัดอย่างฉลาด: max-fail-load ต่ำกว่า", size=24, color=WHITE)
        best_meter_bg = Rectangle(width=4.0, height=0.5, stroke_color=GRAY_B, fill_color="#333333", fill_opacity=1)
        best_meter_fill = Rectangle(width=2.3, height=0.5, fill_color=OK_COLOR, fill_opacity=1, stroke_width=0)
        best_meter_fill.align_to(best_meter_bg, LEFT)
        best_group = VGroup(best_meter_bg, best_meter_fill)
        best_row = VGroup(best_label, best_group).arrange(DOWN, buff=0.2)
        best_row.move_to(DOWN * 1.1)

        self.play(FadeIn(greedy_row, shift=RIGHT * 0.2))
        self.wait(0.3)
        self.play(FadeIn(best_row, shift=RIGHT * 0.2))
        self.wait(0.6)

        conclusion = thai(
            "greedy ไม่ได้ผิดเสมอไป แต่ “ไม่มีอะไร garantee” ว่ามันคือคำตอบที่ดีที่สุด",
            size=26, color=WARN_COLOR,
        )
        conclusion.to_edge(DOWN, buff=0.5)
        self.play(FadeOut(cap4))
        self.play(FadeIn(conclusion))
        self.wait(1.0)

        final = thai("ต้องใช้วิธีค้นหาที่ครอบคลุมทุกความเป็นไปได้อย่างเป็นระบบ", size=28, color=WHITE, weight=BOLD)
        final.move_to(DOWN * 2.6)
        self.play(FadeIn(final))
        self.wait(1.0)
        self.play(*[FadeOut(m) for m in self.mobjects])
