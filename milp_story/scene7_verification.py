"""Scene 7 — brute-force verification of the pairing.

Accuracy note (checked against engine/optimization.py build_proof_context):
brute_force_pairing_check actually runs on EVERY group, not just the
bottleneck one — it just also flags which group is the bottleneck
(its max-fail equals the overall M*). The animation says that correctly,
then zooms into the bottleneck group as the one worth walking through,
since that's the group whose number *is* the reported M*.
"""
from manim import *
from common import thai, title_card, caption, PAIRS, OK_COLOR, WARN_COLOR, FAIL_COLOR

N_GROUPS = 3
GROUP_SIZES = [2, 3, 2]


def make_row(idx, size=0.7):
    box = Square(side_length=size, fill_color="#3A3A3A", fill_opacity=1, stroke_color=WHITE, stroke_width=1.5)
    lbl = thai(str(idx + 1), size=16, color=WHITE)
    lbl.move_to(box)
    return VGroup(box, lbl)


class Scene7_Verification(Scene):
    def construct(self):
        title = title_card("Verification: brute-force cross-check", "ตรวจ MILP ด้วยวิธีที่ไม่มี logic ร่วมกันเลย")
        self.play(FadeIn(title))

        # ── build the frozen grouping ──
        all_rows = VGroup()
        group_boxes = []
        idx = 0
        for gsize in GROUP_SIZES:
            grp = VGroup(*[make_row(idx + j) for j in range(gsize)])
            grp.arrange(RIGHT, buff=0.2)
            group_boxes.append(grp)
            all_rows.add(grp)
            idx += gsize
        all_rows.arrange(RIGHT, buff=0.6)
        all_rows.move_to(UP * 1.7)
        self.play(LaggedStart(*[FadeIn(g) for g in all_rows], lag_ratio=0.15))

        frames = VGroup()
        for grp in group_boxes:
            frame = SurroundingRectangle(grp, color=GRAY_B, buff=0.15)
            frames.add(frame)
        self.play(*[Create(f) for f in frames])
        self.wait(0.3)

        cap1 = caption("ตรึง grouping ตามที่ MILP หาได้ไว้ก่อน — ห้ามแก้")
        self.play(FadeIn(cap1))
        lock_body = RoundedRectangle(corner_radius=0.08, width=0.55, height=0.45, fill_color=WARN_COLOR, fill_opacity=1, stroke_width=0)
        lock_shackle = Arc(radius=0.2, start_angle=0, angle=PI, stroke_color=WARN_COLOR, stroke_width=6)
        lock_shackle.next_to(lock_body, UP, buff=-0.05)
        lock = VGroup(lock_shackle, lock_body)
        lock.next_to(all_rows, RIGHT, buff=0.5)
        lock_note = thai("locked", size=18, color=WARN_COLOR)
        lock_note.next_to(lock, RIGHT, buff=0.15)
        lock = VGroup(lock, lock_note)
        self.play(FadeIn(lock, scale=1.3))
        self.wait(0.6)
        self.play(FadeOut(cap1))

        # ── brute-force check every group independently ──
        cap2 = caption("brute-force เช็คทุกกลุ่มจริง ๆ (ลองทุก pairing ที่เป็นไปได้ในกลุ่มนั้น แล้วหาค่าที่แย่สุดจริง)")
        self.play(FadeIn(cap2))

        checks = VGroup()
        for frame in frames:
            check = thai("✓", size=28, color=OK_COLOR, weight=BOLD)
            check.next_to(frame, DOWN, buff=0.15)
            checks.add(check)
        self.play(LaggedStart(*[FadeIn(c, scale=1.4) for c in checks], lag_ratio=0.3))
        self.wait(0.5)
        self.play(FadeOut(cap2))

        # ── identify the bottleneck group ──
        cap3 = caption("กลุ่มที่ค่าแย่สุด = M* พอดี คือ “กลุ่มที่ชี้ขาด” ทั้งระบบ — zoom เข้าไปดูกลุ่มนี้")
        self.play(FadeIn(cap3))

        bottleneck = frames[1]
        star = thai("★ bottleneck group", size=20, color=WARN_COLOR, weight=BOLD)
        star.next_to(checks[1], DOWN, buff=0.2)
        self.play(bottleneck.animate.set_color(WARN_COLOR), FadeIn(star))
        self.wait(0.5)

        other_frames = VGroup(*[f for f in frames if f is not bottleneck])
        other_groups = VGroup(*[g for g in group_boxes if g is not group_boxes[1]])
        self.play(
            FadeOut(other_frames), FadeOut(other_groups), FadeOut(checks),
            FadeOut(lock), FadeOut(star), FadeOut(cap3),
        )
        self.play(
            group_boxes[1].animate.scale(1.8).move_to(UP * 1.5),
            bottleneck.animate.scale(1.8).move_to(UP * 1.5),
        )
        self.wait(0.3)

        # ── enumerate all 6^k pairings for this group (k = 3 two-source rows here) ──
        cap4 = caption("ลองทุก pairing ที่เป็นไปได้ในกลุ่มนี้ (6^k แบบ) แล้วจับตัวที่แย่สุดของแต่ละชุด")
        self.play(FadeIn(cap4))

        slot = thai(f"{PAIRS[0]}-{PAIRS[1]}-{PAIRS[2]}", size=26, color=WHITE)
        slot.move_to(DOWN * 0.3)
        self.play(FadeIn(slot))

        best_tracker = thai("best so far: 2.9", size=22, color=GRAY_B)
        best_tracker.next_to(slot, DOWN, buff=0.6)
        self.play(FadeIn(best_tracker))

        sample_sequence = [
            ("AB-CD-AC", 2.7), ("AD-BC-AB", 2.5), ("CD-AB-BD", 2.5),
            ("AC-BD-AD", 2.3), ("BC-AD-CD", 2.3), ("AB-AC-BD", 2.3),
        ]
        current_best = 2.9
        for combo, val in sample_sequence:
            new_slot = thai(combo, size=26, color=WHITE)
            new_slot.move_to(slot.get_center())
            improved = val < current_best
            if improved:
                current_best = val
            new_tracker = thai(f"best so far: {current_best}", size=22, color=(OK_COLOR if improved else GRAY_B))
            new_tracker.move_to(best_tracker.get_center())
            self.play(Transform(slot, new_slot), Transform(best_tracker, new_tracker), run_time=0.35)
        self.wait(0.4)
        self.play(FadeOut(cap4))

        cap5 = caption("ผลลัพธ์ brute-force ตรงกับที่ MILP เจอเป๊ะ — ยืนยันว่า MILP ไม่ได้ทำพลาด")
        self.play(FadeIn(cap5))
        match = thai("brute-force best = 2.3 = MILP's answer  ✓", size=26, color=OK_COLOR, weight=BOLD)
        match.next_to(best_tracker, DOWN, buff=0.5)
        self.play(FadeIn(match, scale=1.1))
        self.wait(1.0)
        self.play(FadeOut(cap5))

        cap6 = caption(
            "ข้อจำกัด: จำกัดไว้ที่ 2-source ≤ 8 แถวต่อกลุ่ม (6⁸ ≈ 1.68 ล้าน) — และยัง verify เฉพาะ pairing ไม่ใช่ grouping เอง",
            size=22,
        )
        self.play(FadeIn(cap6))
        self.wait(1.4)
        self.play(*[FadeOut(m) for m in self.mobjects])
