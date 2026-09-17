"""Scene 1 -- "From a real data hall to the problem we must solve."

Storyboard source: the Thai beat sheet the user supplied (Beats 1.1-1.10,
Parts A-D). All on-screen text is English per the user's instruction; the
Thai beat sheet was only the blueprint. Every number shown is computed in
code from ROWS / UPS_PAIRS below -- nothing is hardcoded twice.

Run with:
    uv run manim -pqh src/manimations/illustrate/scene1_problem.py DataHallProblem
"""
from manim import *

# ------------------------------------------------------------------ palette
BG_COLOR = "#0a0e1a"
UPS_COLORS = {"A": "#00d4ff", "B": "#ffaa00", "C": "#a66cff", "D": "#3ddc84"}
FAIL_COLOR = "#ff3b3b"
HL_COLOR = "#ffe600"
RACK_COLOR = "#25334d"
RACK_LIT = "#3c78c9"
CAP_COLOR = "#cfd8e3"
LINE_COLOR = "#5b6b8c"

NUM_FONT = "Consolas"

# ------------------------------------------------------------------- data
ROWS = [
    {"name": "Row 1", "load": 500, "pair": ("A", "B")},
    {"name": "Row 2", "load": 620, "pair": ("C", "D")},
    {"name": "Row 3", "load": 480, "pair": ("A", "C")},
    {"name": "Row 4", "load": 550, "pair": ("B", "D")},
]
UPS_LIST = ["A", "B", "C", "D"]


def normal_loads(rows):
    loads = {u: 0.0 for u in UPS_LIST}
    for r in rows:
        for u in r["pair"]:
            loads[u] += r["load"] / 2
    return loads


def loads_after_fail(rows, failed):
    loads = {u: 0.0 for u in UPS_LIST if u != failed}
    for r in rows:
        pair = r["pair"]
        if failed in pair:
            partner = pair[0] if pair[1] == failed else pair[1]
            loads[partner] += r["load"]
        else:
            for u in pair:
                loads[u] += r["load"] / 2
    return loads


# --------------------------------------------------------------- helpers
MAX_TEXT_WIDTH = 12.8  # frame is ~14.2 wide; keep a safe margin on both sides


def fit_width(mobj, max_width=MAX_TEXT_WIDTH):
    """Shrink a mobject so it never runs past the frame edges."""
    if mobj.width > max_width:
        mobj.scale_to_fit_width(max_width)
    return mobj


def caption(text_str, size=28, color=CAP_COLOR):
    cap = Text(text_str, font_size=size, color=color)
    fit_width(cap)
    cap.to_edge(DOWN, buff=0.55)
    return cap


def num_text(value, size=28, color=WHITE, weight=BOLD, unit=""):
    text_str = value if isinstance(value, str) else f"{value:g}{unit}"
    return Text(text_str, font=NUM_FONT, font_size=size, color=color, weight=weight)


def iso_box(width=1.5, height=1.1, depth=0.8, color="#3c78c9", label=None):
    """A cheap 3-face fake-isometric block: front + top + side."""
    depth_vec = np.array([0.5, 0.3, 0.0]) * depth
    A, B, C, D = (
        np.array([0, 0, 0]),
        np.array([width, 0, 0]),
        np.array([width, height, 0]),
        np.array([0, height, 0]),
    )
    base = ManimColor(color)
    front = Polygon(A, B, C, D, stroke_width=1.5, stroke_color=BLACK,
                     fill_color=base, fill_opacity=1)
    top = Polygon(D, C, C + depth_vec, D + depth_vec, stroke_width=1.5, stroke_color=BLACK,
                  fill_color=interpolate_color(base, WHITE, 0.35), fill_opacity=1)
    side = Polygon(B, C, C + depth_vec, B + depth_vec, stroke_width=1.5, stroke_color=BLACK,
                   fill_color=interpolate_color(base, BLACK, 0.35), fill_opacity=1)
    box = VGroup(front, top, side)
    box.front_face = front
    if label:
        lbl = Text(label, font_size=18, color=WHITE, weight=BOLD)
        lbl.move_to(front.get_center())
        box.add(lbl)
    return box


def warning_icon(size=0.35, color=FAIL_COLOR):
    tri = Triangle(color=color, fill_color=color, fill_opacity=1).scale(size)
    mark = Text("!", font_size=int(size * 60), color=BLACK, weight=BOLD)
    mark.move_to(tri.get_center() + DOWN * size * 0.12)
    return VGroup(tri, mark)


def meter_bar(width=0.7, max_height=2.6, color="#00d4ff"):
    back = Rectangle(width=width, height=max_height, stroke_color=LINE_COLOR,
                      fill_color="#141b2e", fill_opacity=1)
    fill = Rectangle(width=width, height=0.001, stroke_width=0, fill_color=color, fill_opacity=1)
    fill.align_to(back, DOWN)
    grp = VGroup(back, fill)
    grp.back = back
    grp.fill = fill
    grp.max_height = max_height
    return grp


def set_bar(bar, value, max_value):
    frac = max(0.0, min(1.0, value / max_value if max_value else 0))
    new_fill = Rectangle(width=bar.back.width, height=max(bar.max_height * frac, 0.001),
                          stroke_width=0, fill_color=bar.fill.fill_color, fill_opacity=1)
    new_fill.align_to(bar.back, DOWN)
    return new_fill


# ============================================================= the scene
class DataHallProblem(MovingCameraScene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        self.part_a_establishing_shot()
        self.part_a_power_path()
        self.part_a_dual_feed()
        self.part_c_four_source_pairs()
        self.part_c_fail_sweep()
        self.part_d_scale_hook()
        self.part_d_closing_questions()

    # ---------------------------------------------------------- Beat 1.1
    def part_a_establishing_shot(self):
        cap = caption("A data hall is a place where power can never go down -- not even for a second.")

        # -- a plain top-view floor plan so the setting reads instantly --
        strips = VGroup()
        for i in range(4):
            strip = Rectangle(width=1.3, height=3.2, stroke_color=LINE_COLOR, stroke_width=1.5,
                               fill_color=RACK_COLOR, fill_opacity=1)
            ticks = VGroup(*[
                Line(strip.get_left() + RIGHT * 0.02 + UP * (y),
                     strip.get_right() + LEFT * 0.02 + UP * (y),
                     stroke_color=LINE_COLOR, stroke_width=1, stroke_opacity=0.6)
                for y in np.linspace(-1.35, 1.35, 8)
            ])
            lbl = Text(f"Row {i+1}", font_size=16, color=WHITE, weight=BOLD)
            lbl.next_to(strip, DOWN, buff=0.15)
            strips.add(VGroup(strip, ticks, lbl))
        strips.arrange(RIGHT, buff=0.55).move_to(ORIGIN)

        building = RoundedRectangle(width=strips.width + 1.2, height=strips.height + 1.0,
                                     corner_radius=0.2, stroke_color=LINE_COLOR, stroke_width=2.5,
                                     fill_opacity=0)
        building.move_to(strips.get_center() + UP * 0.15)
        title = Text("DATA HALL -- TOP VIEW", font_size=24, color=CAP_COLOR, weight=BOLD)
        title.next_to(building, UP, buff=0.25)

        self.play(FadeIn(title, shift=DOWN * 0.15), Create(building), run_time=1.0)
        self.play(LaggedStartMap(FadeIn, strips, shift=UP * 0.2, lag_ratio=0.15), FadeIn(cap), run_time=1.2)
        self.play(self.camera.frame.animate.scale(0.85).move_to(strips.get_center()), run_time=1.1)

        for s in strips:
            self.play(s[0].animate.set_fill(RACK_LIT), run_time=0.3)
        self.wait(0.3)

        # -- smoothly lift the flat plan into the 3-D row blocks used later --
        boxes = VGroup()
        for i in range(4):
            b = iso_box(color=RACK_LIT, label=f"Row {i+1}")
            b.move_to(strips[i].get_center())
            boxes.add(b)

        self.play(
            self.camera.frame.animate.scale(1 / 0.85).move_to(ORIGIN),
            FadeOut(title, shift=UP * 0.15),
            FadeOut(building),
            *[ReplacementTransform(strips[i], boxes[i]) for i in range(4)],
            run_time=1.4,
        )
        self.wait(0.5)
        self.play(FadeOut(boxes), FadeOut(cap, shift=DOWN * 0.15))

    # ---------------------------------------------------------- Beat 1.2
    def part_a_power_path(self):
        cap = caption("Power to every row always passes through a UPS first, so it keeps flowing even if the main feed fails.")
        labels = ["Transformer / Generator", "UPS", "Busway", "Rack"]
        nodes = VGroup()
        for i, txt in enumerate(labels):
            box = RoundedRectangle(width=4.2, height=0.8, corner_radius=0.12,
                                    stroke_color=LINE_COLOR, fill_color="#141b2e", fill_opacity=1)
            t = Text(txt, font_size=24, color=WHITE)
            fit_width(t, box.width - 0.3)
            t.move_to(box.get_center())
            grp = VGroup(box, t)
            grp.shift(UP * (2.1 - i * 1.4))
            nodes.add(grp)

        arrows = VGroup(*[
            Arrow(nodes[i].get_bottom(), nodes[i + 1].get_top(), buff=0.08,
                  color=LINE_COLOR, stroke_width=4)
            for i in range(len(nodes) - 1)
        ])

        self.play(FadeIn(cap), LaggedStartMap(FadeIn, nodes, lag_ratio=0.2), run_time=1.0)
        self.play(*[Create(a) for a in arrows], run_time=0.8)

        dot = Dot(nodes[0].get_bottom(), radius=0.09, color=HL_COLOR)
        self.play(FadeIn(dot, scale=0.3))
        for i in range(len(nodes) - 1):
            self.play(dot.animate.move_to(nodes[i + 1].get_top()), run_time=0.35)
            self.play(Flash(dot, color=HL_COLOR, line_length=0.15), run_time=0.25)
        self.wait(0.4)
        self.play(FadeOut(nodes), FadeOut(arrows), FadeOut(dot), FadeOut(cap))

    # ---------------------------------------------------------- Beat 1.3
    def part_a_dual_feed(self):
        cap = caption("Each row draws power from two UPS units at once -- normally splitting the load evenly.")
        self.play(FadeIn(cap))

        row_box = RoundedRectangle(width=2.6, height=1.0, corner_radius=0.12,
                                    stroke_color=LINE_COLOR, fill_color="#141b2e", fill_opacity=1)
        row_lbl = Text("Row 1", font_size=24, color=WHITE).move_to(row_box)
        row_grp = VGroup(row_box, row_lbl).move_to(DOWN * 1.2)

        ups_a = Circle(radius=0.5, color=UPS_COLORS["A"], fill_color=UPS_COLORS["A"], fill_opacity=1)
        ups_a_lbl = Text("UPS A", font_size=20, color=BLACK, weight=BOLD).move_to(ups_a)
        ups_a_grp = VGroup(ups_a, ups_a_lbl).move_to(UP * 1.6 + LEFT * 2.2)

        ups_b = Circle(radius=0.5, color=UPS_COLORS["B"], fill_color=UPS_COLORS["B"], fill_opacity=1)
        ups_b_lbl = Text("UPS B", font_size=20, color=BLACK, weight=BOLD).move_to(ups_b)
        ups_b_grp = VGroup(ups_b, ups_b_lbl).move_to(UP * 1.6 + RIGHT * 2.2)

        line_a = Line(ups_a_grp.get_bottom(), row_grp.get_top(), color=UPS_COLORS["A"], stroke_width=5)
        line_b = Line(ups_b_grp.get_bottom(), row_grp.get_top(), color=UPS_COLORS["B"], stroke_width=5)

        load_total = ROWS[0]["load"]
        total_lbl = num_text(f"{load_total} kW", size=30).next_to(row_grp, DOWN, buff=0.3)

        self.play(FadeIn(ups_a_grp), FadeIn(ups_b_grp), FadeIn(row_grp))
        self.play(Create(line_a), Create(line_b))
        self.play(FadeIn(total_lbl))
        self.wait(0.4)

        half_a = num_text(f"A: {load_total//2} kW", size=24, color=UPS_COLORS["A"]).next_to(line_a.get_center(), LEFT, buff=0.15)
        half_b = num_text(f"B: {load_total//2} kW", size=24, color=UPS_COLORS["B"]).next_to(line_b.get_center(), RIGHT, buff=0.15)
        self.play(FadeOut(total_lbl), FadeIn(half_a), FadeIn(half_b))
        self.wait(0.8)
        self.play(*[FadeOut(m) for m in (ups_a_grp, ups_b_grp, row_grp, line_a, line_b, half_a, half_b, cap)])

    def _ups_node(self, letter, radius=0.5):
        c = Circle(radius=radius, color=UPS_COLORS[letter], fill_color=UPS_COLORS[letter], fill_opacity=1)
        t = Text(f"UPS {letter}", font_size=18, color=BLACK, weight=BOLD).move_to(c)
        return VGroup(c, t)

    # ---------------------------------------------------------- Beat 1.7
    def part_c_four_source_pairs(self):
        cap = caption("With four UPS units, each row can choose which pair supports it.")
        self.play(FadeIn(cap))

        ups_nodes = VGroup(*[self._ups_node(u) for u in UPS_LIST])
        ups_nodes.arrange(RIGHT, buff=1.0).move_to(UP * 1.5)

        row_boxes = VGroup()
        for r in ROWS:
            rb = RoundedRectangle(width=1.7, height=0.75, corner_radius=0.1,
                                   stroke_color=LINE_COLOR, fill_color="#141b2e", fill_opacity=1)
            lbl = Text(f"{r['name']}: {r['load']} kW", font_size=15, color=WHITE)
            fit_width(lbl, rb.width - 0.15)
            lbl.move_to(rb)
            row_boxes.add(VGroup(rb, lbl))
        row_boxes.arrange(RIGHT, buff=0.4).move_to(DOWN * 1.9)

        self.play(FadeIn(ups_nodes), FadeIn(row_boxes))

        ups_pos = {u: ups_nodes[UPS_LIST.index(u)] for u in UPS_LIST}
        pair_lines = VGroup()
        for rb, r in zip(row_boxes, ROWS):
            for u in r["pair"]:
                line = Line(ups_pos[u].get_bottom(), rb.get_top(), color=UPS_COLORS[u], stroke_width=3)
                pair_lines.add(line)
        self.play(LaggedStartMap(Create, pair_lines, lag_ratio=0.08), run_time=1.4)
        self.wait(0.4)

        loads = normal_loads(ROWS)
        bars = VGroup()
        vals = VGroup()
        max_load = max(loads.values())
        for u in UPS_LIST:
            bar = meter_bar(width=0.6, max_height=1.0, color=UPS_COLORS[u])
            bar.next_to(ups_pos[u], UP, buff=0.15)
            val = num_text(f"{loads[u]:.0f} kW", size=16).next_to(bar, UP, buff=0.1)
            bars.add(bar)
            vals.add(val)
        self.play(FadeIn(bars), FadeIn(vals))
        self.play(*[bar.fill.animate.become(set_bar(bar, loads[u], max_load)) for bar, u in zip(bars, UPS_LIST)],
                   run_time=1.0)
        self.wait(0.8)

        self._part_c_common = VGroup(ups_nodes, row_boxes, pair_lines)
        self._part_c_bars = bars
        self._part_c_vals = vals
        self._part_c_ups_pos = ups_pos
        self.play(FadeOut(bars), FadeOut(vals), FadeOut(cap))

    # ---------------------------------------------------------- Beat 1.8
    def part_c_fail_sweep(self):
        cap = caption("Now fail each UPS one at a time -- the highest value across all cases is the worst case.")
        self.play(FadeIn(cap))

        ups_nodes, row_boxes, pair_lines = self._part_c_common
        ups_pos = self._part_c_ups_pos
        max_scale_load = max(
            max(loads_after_fail(ROWS, f).values()) for f in UPS_LIST
        )

        results = []
        bars = VGroup()
        vals = VGroup()
        for u in UPS_LIST:
            bar = meter_bar(width=0.6, max_height=1.0, color=UPS_COLORS[u])
            bar.next_to(ups_pos[u], UP, buff=0.15)
            bars.add(bar)
            val = num_text("0 kW", size=16).next_to(bar, UP, buff=0.1)
            vals.add(val)
        self.play(FadeIn(bars), FadeIn(vals))

        # a dedicated, empty band at the bottom (above the caption) collects
        # each round's worst-case chip, so nothing ever competes with the
        # diagram above it
        chip_slots = [LEFT * 4.5 + RIGHT * i * 3.0 + DOWN * 2.55 for i in range(len(UPS_LIST))]

        collected = VGroup()
        for failed in UPS_LIST:
            title = Text(f"UPS {failed} fails", font_size=24, color=FAIL_COLOR, weight=BOLD)
            title.to_corner(UL, buff=0.35)
            fail_node = ups_pos[failed]
            x_mark = warning_icon().move_to(fail_node.get_top() + UP * 0.25).scale(0.7)

            self.play(FadeIn(title), fail_node.animate.set_opacity(0.25), FadeIn(x_mark, scale=0.4))

            loads = loads_after_fail(ROWS, failed)
            others = [u for u in UPS_LIST if u != failed]
            anims = []
            for bar, val, u in zip(bars, vals, UPS_LIST):
                if u == failed:
                    anims.append(bar.fill.animate.become(set_bar(bar, 0, max_scale_load)))
                    anims.append(val.animate.become(num_text("--", size=16).move_to(val)))
                else:
                    new_fill = set_bar(bar, loads[u], max_scale_load)
                    new_val = num_text(f"{loads[u]:.0f} kW", size=16).next_to(bar, UP, buff=0.1)
                    anims.append(bar.fill.animate.become(new_fill))
                    anims.append(val.animate.become(new_val))
            self.play(*anims, run_time=1.0)

            worst_u = max(others, key=lambda u: loads[u])
            worst_v = loads[worst_u]
            results.append(worst_v)
            highlight = SurroundingRectangle(vals[UPS_LIST.index(worst_u)], color=HL_COLOR, buff=0.08)
            self.play(Create(highlight))
            self.wait(0.4)

            chip = Text(f"{worst_v:.0f} kW", font=NUM_FONT, font_size=20, color=HL_COLOR, weight=BOLD)
            chip.move_to(vals[UPS_LIST.index(worst_u)])
            self.play(chip.animate.move_to(chip_slots[len(collected)]))
            collected.add(chip)

            self.play(FadeOut(highlight), FadeOut(title), FadeOut(x_mark), fail_node.animate.set_opacity(1))

        # clear the working diagram completely before the clean recap, so
        # the final line + label never has to share space with anything
        self.play(FadeOut(VGroup(ups_nodes, row_boxes, pair_lines, bars, vals)))

        worst_all = max(results)
        self.play(collected.animate.move_to(DOWN * 0.6).arrange(RIGHT, buff=1.3).scale(1.3))

        line = DashedLine(LEFT * 5, RIGHT * 5, color=HL_COLOR, stroke_width=3)
        line.move_to(UP * 1.0)
        rating_lbl = Text(f"UPS rating >= {worst_all:.0f} kW", font_size=28, color=HL_COLOR, weight=BOLD)
        rating_lbl.next_to(line, UP, buff=0.3)
        self.play(Create(line), FadeIn(rating_lbl, shift=DOWN * 0.1))
        self.wait(1.2)

        self.play(FadeOut(VGroup(collected, line, rating_lbl, cap)))

    # ---------------------------------------------------------- Beat 1.9
    def part_d_scale_hook(self):
        counter = Text("4 rows", font_size=40, color=WHITE, weight=BOLD)
        self.play(FadeIn(counter))

        mesh = VGroup()
        for n_txt, n_lines in [("20 rows", 15), ("50 rows", 35), ("100 rows", 70)]:
            new_counter = Text(n_txt, font_size=40, color=WHITE, weight=BOLD)
            new_lines = VGroup(*[
                Line(
                    np.array([np.random.uniform(-5, 5), np.random.uniform(-2.5, 2.5), 0]),
                    np.array([np.random.uniform(-5, 5), np.random.uniform(-2.5, 2.5), 0]),
                    stroke_width=1, stroke_color=LINE_COLOR, stroke_opacity=0.5,
                )
                for _ in range(n_lines)
            ])
            self.play(Transform(counter, new_counter), FadeIn(new_lines), run_time=0.7)
            mesh.add(new_lines)
        self.wait(0.6)
        self.play(FadeOut(counter), FadeOut(mesh))

    # ---------------------------------------------------------- Beat 1.10
    def part_d_closing_questions(self):
        intro = Text("Our problem is:", font_size=34, color=WHITE, weight=BOLD)
        q1 = fit_width(Text("1. How should we group rows to minimize equipment size?", font_size=28, color=CAP_COLOR))
        q2 = fit_width(Text("2. How should we pair UPS units to minimize the worst case?", font_size=28, color=CAP_COLOR))
        group = VGroup(intro, q1, q2).arrange(DOWN, buff=0.5, aligned_edge=LEFT)

        self.play(FadeIn(intro, shift=UP * 0.1))
        self.wait(0.5)
        self.play(FadeIn(q1, shift=UP * 0.1))
        self.wait(0.5)
        self.play(FadeIn(q2, shift=UP * 0.1))
        self.wait(2.0)
        self.play(FadeOut(group))
        self.wait(1.0)
