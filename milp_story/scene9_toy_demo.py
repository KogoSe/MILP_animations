"""Scene 9 — the real branch-and-bound tree, built from actual solver output.

Everything drawn here is read from toy_solve_log.json (produced by
hac_project/toy_solver.py) via toy_data.py — no fabricated numbers. The
full tree has 229 logged nodes (1 root + 6 row_1 choices + 36 row_2
choices + 186 row_3 leaves); the 216 possible leaves are represented by
a real leaf-count badge under each row_2 node rather than drawn one by
one, so the picture stays legible while every count and every bound
value shown is exactly what the toy solver logged.
"""
from manim import *
from common import thai, title_card, caption, OK_COLOR, WARN_COLOR, FAIL_COLOR
from toy_data import load_toy_log, build_tree, last_pair

NODE_GRAY = "#3A3A3A"


class Scene9_ToyDemo(Scene):
    def construct(self):
        data = load_toy_log()
        nodes, children = build_tree(data)
        pairs = data["pairs"]

        title = title_card("ลองจริง: branch-and-bound บน toy case", "3 แถว 2-source, 1 กลุ่ม, 6³ = 216 ทางเลือก — ข้อมูลจากการรันจริง")
        self.play(FadeIn(title))

        rows_text = ", ".join(f"{r['label']} = {r['kw']:.0f} kW" for r in data["toy_rows"])
        rows_cap = thai(rows_text, size=22, color=GRAY_A)
        rows_cap.next_to(title, DOWN, buff=0.15)
        self.play(FadeIn(rows_cap))
        self.wait(0.5)
        self.play(FadeOut(rows_cap))

        # ── layout ──
        root_y, l1_y, l2_y, badge_y = 2.1, 1.0, -0.1, -0.6
        l1_xs = [-6.25 + i * 2.5 for i in range(6)]
        l2_offsets = [-0.75 + j * 0.3 for j in range(6)]

        root = Circle(radius=0.28, fill_color=NODE_GRAY, fill_opacity=1, stroke_color=WHITE, stroke_width=2)
        root.move_to([0, root_y, 0])
        root_lbl = thai("start", size=16, color=GRAY_A).next_to(root, LEFT, buff=0.35)
        self.play(FadeIn(root, scale=0.6), FadeIn(root_lbl))

        # ── level 1: 6 row_1 choices (always fully explored, never pruned) ──
        l1_group = children[0]  # ids of root's children, in PAIRS order
        l1_nodes = VGroup()
        l1_edges = VGroup()
        l1_labels = VGroup()
        for x, node_id in zip(l1_xs, l1_group):
            n = nodes[node_id]
            c = Circle(radius=0.24, fill_color=NODE_GRAY, fill_opacity=1, stroke_color=WHITE, stroke_width=2)
            c.move_to([x, l1_y, 0])
            lbl = thai(last_pair(n["assignment"]), size=16, color=WHITE)
            lbl.move_to(c)
            edge = Line(root.get_bottom(), c.get_top(), color=GRAY_B, stroke_width=1.5)
            l1_nodes.add(c)
            l1_edges.add(edge)
            l1_labels.add(lbl)

        cap1 = caption("ระดับที่ 1: เลือก pair ให้ row_1 — 6 ทางเลือก ยังไม่มีใครถูกตัดทิ้ง (bound ยังต่ำกว่า best เสมอ)")
        self.play(FadeIn(cap1))
        self.play(LaggedStart(*[Create(e) for e in l1_edges], lag_ratio=0.1))
        self.play(LaggedStart(*[FadeIn(n, scale=0.6) for n in l1_nodes], lag_ratio=0.1))
        self.play(LaggedStart(*[FadeIn(lb) for lb in l1_labels], lag_ratio=0.1))
        self.wait(0.4)
        self.play(FadeOut(cap1))

        # ── level 2: for each level-1 node, up to 6 row_2 choices ──
        cap2 = caption("ระดับที่ 2: เลือก pair ให้ row_2 — ตอนนี้เริ่มมี node ที่ bound >= best แล้ว โดนตัดทิ้งจริง (สีแดง)")
        self.play(FadeIn(cap2))

        l2_nodes = VGroup()
        l2_edges = VGroup()
        l2_labels = VGroup()
        badges = VGroup()
        pruned_examples = []

        for x1, l1_id in zip(l1_xs, l1_group):
            l2_ids = children.get(l1_id, [])
            for off, node_id in zip(l2_offsets, l2_ids):
                n = nodes[node_id]
                pruned = len(children.get(node_id, [])) == 0
                x = x1 + off
                color = FAIL_COLOR if pruned else NODE_GRAY
                stroke = FAIL_COLOR if pruned else WHITE
                c = Circle(radius=0.11, fill_color=color, fill_opacity=(0.9 if pruned else 1), stroke_color=stroke, stroke_width=1.5)
                c.move_to([x, l2_y, 0])
                lbl = thai(last_pair(n["assignment"]), size=8, color=WHITE)
                lbl.move_to(c)
                edge = Line([x1, l1_y, 0], c.get_top(), color=GRAY_B, stroke_width=1)
                leaf_n = len(children.get(node_id, []))
                badge = thai("✗" if pruned else str(leaf_n), size=13, color=(FAIL_COLOR if pruned else OK_COLOR), weight=BOLD)
                badge.move_to([x, badge_y, 0])
                l2_nodes.add(c)
                l2_edges.add(edge)
                l2_labels.add(lbl)
                badges.add(badge)
                if pruned:
                    pruned_examples.append(n)

        self.play(LaggedStart(*[Create(e) for e in l2_edges], lag_ratio=0.02), run_time=1.5)
        self.play(LaggedStart(*[FadeIn(n, scale=0.6) for n in l2_nodes], lag_ratio=0.02), run_time=1.5)
        self.play(LaggedStart(*[FadeIn(b) for b in badges], lag_ratio=0.02), run_time=1.2)
        self.wait(0.3)
        self.play(FadeOut(cap2))

        cap2b = caption("ตัวเลขใต้แต่ละ node = จำนวน row_3 ที่ไปถึงจริง (6 ถ้าไม่ถูกตัด), ✗ = ถูกตัดตั้งแต่ระดับนี้ ไม่ไปต่อเลย")
        self.play(FadeIn(cap2b))
        self.wait(1.0)
        self.play(FadeOut(cap2b))

        # ── zoom on one real prune event, numbers pulled straight from the log ──
        example = pruned_examples[0]
        ex_row1 = list(example["assignment"].values())[0]
        ex_row2 = list(example["assignment"].values())[1]
        cap3 = caption(
            f"ตัวอย่างจริง: row_1={ex_row1}, row_2={ex_row2} → bound = {example['bound']} kW "
            f"≥ best ที่เจอแล้ว ({example['best_value_so_far']} kW) → ตัดทิ้งทันที ไม่ไปต่อที่ row_3",
            size=20,
        )
        self.play(FadeIn(cap3))
        self.wait(1.4)
        self.play(FadeOut(cap3))

        # ── the real best path, traced with the real winning pairs ──
        best_assignment = data["best_assignment"]
        best_value = data["best_value"]
        r1_best = best_assignment["row_1"]
        r2_best = best_assignment["row_2"]
        r3_best = best_assignment["row_3"]

        cap4 = caption(f"เส้นทางที่ดีที่สุดจริง: row_1={r1_best} → row_2={r2_best} → row_3={r3_best}")
        self.play(FadeIn(cap4))

        best_l1_idx = pairs.index(r1_best)
        best_l1_id = l1_group[best_l1_idx]
        best_l1_node = l1_nodes[best_l1_idx]

        best_l2_ids = children.get(best_l1_id, [])
        best_l2_idx_local = None
        for k, nid in enumerate(best_l2_ids):
            if last_pair(nodes[nid]["assignment"]) == r2_best:
                best_l2_idx_local = k
                break
        best_l2_global_idx = sum(len(children.get(lid, [])) for lid in l1_group[:best_l1_idx]) + best_l2_idx_local
        best_l2_node = l2_nodes[best_l2_global_idx]

        path_edge1 = Line(root.get_center(), best_l1_node.get_center(), color=WARN_COLOR, stroke_width=5)
        path_edge2 = Line(best_l1_node.get_center(), best_l2_node.get_center(), color=WARN_COLOR, stroke_width=5)
        self.play(
            root.animate.set_stroke(WARN_COLOR, width=3),
            best_l1_node.animate.set_stroke(WARN_COLOR, width=3),
            best_l2_node.animate.set_stroke(WARN_COLOR, width=3),
            Create(path_edge1), Create(path_edge2),
        )
        result_lbl = thai(f"→ row_3 = {r3_best} → M* = {best_value:.1f} kW", size=24, color=WARN_COLOR, weight=BOLD)
        result_lbl.move_to(DOWN * 1.6)
        self.play(FadeIn(result_lbl, shift=UP * 0.15))
        self.wait(1.2)
        self.play(FadeOut(cap4))

        # ── real summary stats ──
        cap5 = caption(
            f"สรุปจริง: explore {data['nodes_explored']} node, ไปถึง leaf {data['leaves_explored']}/{data['total_leaves_no_pruning']} "
            f"(ประหยัดไป {100*(1 - data['leaves_explored']/data['total_leaves_no_pruning']):.1f}%) — ยืนยันตรงกับ brute-force 100%",
            size=20,
        )
        self.play(FadeIn(cap5))
        self.wait(1.6)
        self.play(*[FadeOut(m) for m in self.mobjects])
