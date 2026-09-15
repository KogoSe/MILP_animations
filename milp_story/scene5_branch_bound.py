"""Scene 5 — what the solver (CBC) is actually doing.

Kept deliberately shallow: relax binaries into fuzzy 0..1 values to get a
fast lower bound, then branch (force a variable to 0 or force it to 1),
and prune any branch whose own lower bound already can't beat the best
integer solution found so far. A small growing tree with a few grayed-out
"pruned" leaves tells the whole story — no LP duality, no theory.
"""
from manim import *
from common import thai, title_card, caption, OK_COLOR, WARN_COLOR, FAIL_COLOR


def fuzzy_box(value, size=0.9):
    """value in [0,1]; 0.5 = fully fuzzy (half-filled look), 0/1 = solid."""
    box = Square(side_length=size, stroke_color=WHITE, stroke_width=2, fill_color=WARN_COLOR, fill_opacity=0.15 + 0.55 * abs(value - 0.5) * 2)
    lbl = thai(f"{value:.1f}", size=18, color=WHITE)
    lbl.move_to(box.get_center())
    return VGroup(box, lbl)


class Scene5_BranchBound(Scene):
    def construct(self):
        title = title_card("LP relaxation กับ Branch-and-Bound", "ภาพรวมว่า CBC solver คิดยังไง")
        self.play(FadeIn(title))

        cap1 = caption("Binary (0 หรือ 1 เท่านั้น) แก้ตรง ๆ ยาก → ปล่อยให้เป็นเลข “เบลอ ๆ” ระหว่าง 0-1 ก่อน")
        self.play(FadeIn(cap1))

        fuzzy = fuzzy_box(0.5, size=1.3)
        fuzzy.move_to(UP * 1.2)
        crisp_label = thai("ตัวแปร binary จริง: 0 หรือ 1", size=20, color=GRAY_B)
        crisp_label.next_to(fuzzy, DOWN, buff=0.3)
        self.play(FadeIn(fuzzy), FadeIn(crisp_label))
        self.wait(0.4)

        relax_note = thai("LP relaxation: อนุญาตให้เป็นค่ากลางชั่วคราว → หาคำตอบเร็ว ๆ ได้ “เพดานล่าง” (lower bound)", size=20, color=WARN_COLOR)
        relax_note.next_to(crisp_label, DOWN, buff=0.3)
        self.play(FadeIn(relax_note))
        self.wait(0.8)
        self.play(FadeOut(cap1), FadeOut(fuzzy), FadeOut(crisp_label), FadeOut(relax_note))

        # ── branch and bound tree ──
        cap2 = caption("Branch: บังคับตัวแปรเบลอ ๆ ให้เป็น 0 หรือ 1 ทีละตัว แล้วแตกเป็นสองกิ่ง")
        self.play(FadeIn(cap2))

        root = Circle(radius=0.35, color=WHITE, fill_color="#444444", fill_opacity=1)
        root_lbl = thai("LB=1.0", size=16, color=WHITE).move_to(root)
        root_grp = VGroup(root, root_lbl).move_to(UP * 1.6)
        self.play(FadeIn(root_grp, scale=0.7))

        def node(lbl_text, color="#444444"):
            c = Circle(radius=0.32, color=WHITE, fill_color=color, fill_opacity=1)
            t = thai(lbl_text, size=14, color=WHITE).move_to(c)
            return VGroup(c, t)

        left1 = node("LB=1.4")
        right1 = node("LB=2.1")
        left1.move_to(UP * 0.2 + LEFT * 2.2)
        right1.move_to(UP * 0.2 + RIGHT * 2.2)

        edge_l1 = Line(root_grp.get_bottom(), left1.get_top(), color=GRAY_B)
        edge_r1 = Line(root_grp.get_bottom(), right1.get_top(), color=GRAY_B)
        lbl_l1 = thai("x=0", size=14, color=GRAY_B).next_to(edge_l1.get_center(), LEFT, buff=0.1)
        lbl_r1 = thai("x=1", size=14, color=GRAY_B).next_to(edge_r1.get_center(), RIGHT, buff=0.1)

        self.play(Create(edge_l1), Create(edge_r1), FadeIn(lbl_l1), FadeIn(lbl_r1))
        self.play(FadeIn(left1, scale=0.7), FadeIn(right1, scale=0.7))
        self.wait(0.5)
        self.play(FadeOut(cap2))

        # incumbent (best integer solution found so far)
        cap3 = caption("สมมติเจอคำตอบเต็มจำนวนที่ M = 2.6 แล้ว (incumbent) — เก็บไว้เป็นสถิติ")
        self.play(FadeIn(cap3))
        incumbent = thai("Best found so far: M = 2.6", size=22, color=OK_COLOR, weight=BOLD)
        incumbent.to_edge(RIGHT, buff=0.6).shift(UP * 1.6)
        self.play(FadeIn(incumbent))
        self.wait(0.6)
        self.play(FadeOut(cap3))

        # branch further from right1, one side gets pruned because its LB already exceeds incumbent
        cap4 = caption("ถ้ากิ่งไหน lower bound มันแย่กว่า incumbent ที่เจอแล้ว → ตัดทิ้งได้เลยโดยไม่ต้องขุดต่อ")
        self.play(FadeIn(cap4))

        left2 = node("LB=2.4")
        right2 = node("LB=3.1", color="#3A3A3A")
        left2.move_to(DOWN * 1.4 + RIGHT * 1.2)
        right2.move_to(DOWN * 1.4 + RIGHT * 3.4)
        edge_l2 = Line(right1.get_bottom(), left2.get_top(), color=GRAY_B)
        edge_r2 = Line(right1.get_bottom(), right2.get_top(), color=GRAY_B)
        self.play(Create(edge_l2), Create(edge_r2))
        self.play(FadeIn(left2, scale=0.7), FadeIn(right2, scale=0.7))
        self.wait(0.3)

        pruned_stamp = thai("PRUNED", size=16, color=FAIL_COLOR, weight=BOLD)
        pruned_stamp.move_to(right2.get_center())
        self.play(right2.animate.set_opacity(0.3), FadeIn(pruned_stamp))
        prune_reason = thai("3.1 > 2.6 อยู่แล้ว → กิ่งนี้แตกต่อไปก็ไม่มีทางดีกว่า incumbent", size=18, color=FAIL_COLOR)
        prune_reason.next_to(right2, DOWN, buff=0.3)
        self.play(FadeIn(prune_reason))
        self.wait(1.0)
        self.play(FadeOut(cap4), FadeOut(prune_reason))

        cap5 = caption("ทำซ้ำจนกิ่งที่เหลือหมด → คำตอบสุดท้ายคือ optimal ที่ “พิสูจน์แล้ว” ว่าดีที่สุดจริง")
        self.play(FadeIn(cap5))
        self.wait(1.2)
        self.play(*[FadeOut(m) for m in self.mobjects])
