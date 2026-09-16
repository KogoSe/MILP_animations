"""LP Relaxation & Simplex — a purely visual explainer.

The point of this file is a picture, not a solver:

  1. A MILP's feasible solutions are isolated dots (0/1, integers only) —
     that discreteness is why the problem is NP-hard.
  2. "Relaxing" the integrality constraint lets those dots blur into a
     continuous range. Geometrically, the set of feasible points becomes
     the convex hull of the original dots: a convex polytope.
  3. Because the objective is linear and the region is convex, the optimum
     always sits on a vertex of that polytope. The Simplex method exploits
     this by hopping from vertex to adjacent vertex along the edges,
     always improving, until no neighboring vertex is better.

No real data, no real LP is solved — the numbers don't matter, only the
shape of the idea. Run with e.g.:

    uv run manim -pql src/manimations/lp_relaxation_simplex.py LPRelaxationSimplex
"""
from manim import *

THAI_FONT = "Leelawadee UI"

BG_DOT = "#7F8C8D"
HULL_STROKE = "#5DADE2"
HULL_FILL = "#2E86C1"
VERTEX_COLOR = "#F5D76E"
PATH_COLOR = "#F39C12"
OPTIMAL_COLOR = "#2ECC71"
COLD_COLOR = "#5DADE2"
HOT_COLOR = "#E74C3C"
FORBID_COLOR = "#E74C3C"


def thai(s, size=32, color=WHITE, weight=NORMAL, **kwargs):
    return Text(s, font=THAI_FONT, font_size=size, color=color, weight=weight, **kwargs)


def caption(text_str, size=26, color=GRAY_A):
    cap = thai(text_str, size=size, color=color)
    cap.to_edge(DOWN, buff=0.5)
    return cap


def convex_hull(points):
    """Andrew's monotone chain. Returns hull vertices in CCW order."""
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


# A hand-placed scatter of "integer-feasible" points. Irregular on purpose,
# so the hull that comes out of them isn't a trivial square.
ALL_POINTS = [
    (-3.0, -1.2), (-2.6, 0.4), (-2.9, 1.3), (-1.9, 2.0), (-0.6, 2.3),
    (0.9, 2.1), (2.1, 1.5), (2.9, 0.5), (3.1, -0.8), (2.2, -1.9),
    (0.6, -2.3), (-0.9, -2.1), (-2.1, -2.0),
    (-1.6, -0.6), (-0.8, 0.3), (0.2, -0.4), (0.9, 0.6),
    (-1.2, 1.0), (1.4, -0.9), (-0.2, 1.1),
]


def scene_positions(points):
    return [np.array([x, y, 0.0]) for x, y in points]


class LPRelaxationSimplex(Scene):
    def construct(self):
        self.show_title()
        dots, hull_idx_by_point = self.show_discrete_points()
        hull_group, hull_polygon, hull_vertices, interior_dots = self.relax_to_polytope(dots)
        self.sweep_objective(hull_polygon, hull_vertices)
        self.run_simplex_walk(hull_polygon, hull_vertices)
        self.closing_message()

    # ------------------------------------------------------------------
    def show_title(self):
        title = thai("จาก MILP สู่ LP Relaxation", size=44, weight=BOLD)
        sub = thai("ทำไม “ปล่อยให้เบลอ” ถึงทำให้แก้ปัญหาไวขึ้นมหาศาล", size=24, color=GRAY_B)
        sub.next_to(title, DOWN, buff=0.3)
        grp = VGroup(title, sub)
        self.play(FadeIn(grp, shift=UP * 0.2))
        self.wait(1.0)
        self.play(FadeOut(grp))

    # ------------------------------------------------------------------
    def show_discrete_points(self):
        cap = caption("คำตอบของ MILP: จุดโดดๆ ที่ยอมรับได้เท่านั้น (0/1 หรือจำนวนเต็ม) — จุดอื่นระหว่างกลางห้ามแตะ")
        self.play(FadeIn(cap))

        positions = scene_positions(ALL_POINTS)
        dots = VGroup(*[Dot(p, radius=0.09, color=BG_DOT) for p in positions])
        self.play(LaggedStartMap(FadeIn, dots, scale=0.3, lag_ratio=0.05), run_time=1.6)
        self.wait(0.3)

        # emphasize forbidden in-between space with a couple of red X's
        forbidden_spots = [
            (positions[0] + positions[1]) / 2 + UP * 0.15,
            (positions[5] + positions[6]) / 2 + DOWN * 0.1,
        ]
        crosses = VGroup()
        for spot in forbidden_spots:
            x1 = Line(UL, DR, color=FORBID_COLOR, stroke_width=6).scale(0.12).move_to(spot)
            x2 = Line(UR, DL, color=FORBID_COLOR, stroke_width=6).scale(0.12).move_to(spot)
            crosses.add(VGroup(x1, x2))
        note = thai("ค่ากลาง ๆ ระหว่างจุด = ไม่ใช่คำตอบที่ยอมรับ", size=20, color=FORBID_COLOR)
        note.next_to(dots, RIGHT, buff=0.8).shift(UP * 1.6)
        self.play(*[GrowFromCenter(c) for c in crosses], FadeIn(note))
        self.wait(0.8)
        self.play(FadeOut(crosses), FadeOut(note), FadeOut(cap))
        return dots, None

    # ------------------------------------------------------------------
    def relax_to_polytope(self, dots):
        cap = caption("Relax: อนุญาตให้เป็นค่าต่อเนื่องในช่วง [0,1] แทนที่จะเป็น 0 หรือ 1 เป๊ะ ๆ")
        self.play(FadeIn(cap))

        hull_points = convex_hull(ALL_POINTS)
        hull_positions = scene_positions(hull_points)
        interior_points = [p for p in ALL_POINTS if p not in hull_points]

        point_to_dot = dict(zip(ALL_POINTS, dots))
        hull_dots = VGroup(*[point_to_dot[p] for p in hull_points])
        interior_dots = VGroup(*[point_to_dot[p] for p in interior_points])

        polygon = Polygon(*hull_positions, stroke_color=HULL_STROKE, stroke_width=5,
                           fill_color=HULL_FILL, fill_opacity=0.0)

        self.play(
            interior_dots.animate.set_opacity(0.15),
            *[d.animate.set_color(VERTEX_COLOR).scale(1.6) for d in hull_dots],
            run_time=0.8,
        )
        self.play(Create(polygon), run_time=1.4)
        self.play(polygon.animate.set_fill(opacity=0.35), run_time=1.0)
        self.wait(0.3)

        label = thai("Convex Polytope — พื้นที่คำตอบต่อเนื่องและ “นูน”", size=24, color=HULL_STROKE, weight=BOLD)
        label.to_edge(UP, buff=1.0)
        self.play(FadeIn(label, shift=UP * 0.15))
        self.wait(0.6)

        vertex_label = thai("จุดยอด (Vertex)", size=18, color=VERTEX_COLOR)
        vertex_label.next_to(hull_dots[0], UL, buff=0.15)
        pointer = Arrow(vertex_label.get_bottom(), hull_dots[0].get_center(), buff=0.1,
                         color=VERTEX_COLOR, stroke_width=3, max_tip_length_to_length_ratio=0.25)
        self.play(FadeIn(vertex_label), GrowArrow(pointer))
        self.wait(0.8)
        self.play(FadeOut(vertex_label), FadeOut(pointer), FadeOut(cap), FadeOut(label))

        hull_group = VGroup(polygon, hull_dots)
        return hull_group, polygon, list(zip(hull_points, hull_dots)), interior_dots

    # ------------------------------------------------------------------
    def sweep_objective(self, polygon, hull_vertices):
        cap = caption("เป้าหมาย (objective) เป็นเส้นตรง — ยิ่งไปทางหัวลูกศรยิ่งได้ค่ามากขึ้น")
        self.play(FadeIn(cap))

        direction = np.array([1.0, 0.55, 0.0])
        direction = direction / np.linalg.norm(direction)
        perp = np.array([-direction[1], direction[0], 0.0])

        arrow = Arrow(ORIGIN, direction * 2.2, color=HOT_COLOR, stroke_width=6)
        arrow.move_to(polygon.get_center() + direction * 3.4)
        arrow_label = thai("ทิศทางค่าดีขึ้น", size=18, color=HOT_COLOR)
        arrow_label.next_to(arrow, direction, buff=0.15)
        self.play(GrowArrow(arrow), FadeIn(arrow_label))

        # level-set bands, clipped to the polytope so it reads as a heatmap
        bands = VGroup()
        n_bands = 9
        span = 9.0
        for i in range(n_bands):
            t = i / (n_bands - 1)
            offset = (-span / 2) + t * span
            band = Rectangle(width=0.55, height=8.0, stroke_width=0,
                              fill_color=interpolate_color(ManimColor(COLD_COLOR), ManimColor(HOT_COLOR), t), fill_opacity=0.55)
            band.rotate(angle_of_vector(perp))
            band.move_to(polygon.get_center() + direction * offset)
            clipped = Intersection(band, polygon, fill_color=band.fill_color,
                                    fill_opacity=0.55, stroke_width=0)
            bands.add(clipped)

        self.play(FadeOut(polygon.copy().set_fill(opacity=0)), LaggedStartMap(FadeIn, bands, lag_ratio=0.06), run_time=1.6)
        self.wait(0.6)
        self.play(FadeOut(bands), FadeOut(arrow), FadeOut(arrow_label), FadeOut(cap))

        self._direction = direction

    # ------------------------------------------------------------------
    def run_simplex_walk(self, polygon, hull_vertices):
        cap = caption("Simplex: เริ่มที่จุดยอดหนึ่ง แล้วเดินไปตามขอบสู่จุดยอดข้าง ๆ ที่ดีกว่าเสมอ")
        self.play(FadeIn(cap))

        points = [p for p, _ in hull_vertices]
        dots = [d for _, d in hull_vertices]
        n = len(points)
        direction = self._direction
        values = [float(np.dot(np.array([px, py, 0.0]), direction)) for px, py in points]

        start_idx = int(np.argmin(values))
        path = [start_idx]
        current = start_idx
        visited = {start_idx}
        while True:
            left = (current - 1) % n
            right = (current + 1) % n
            candidates = [i for i in (left, right) if i not in visited and values[i] > values[current]]
            if not candidates:
                break
            nxt = max(candidates, key=lambda i: values[i])
            path.append(nxt)
            visited.add(nxt)
            current = nxt

        marker = Dot(dots[path[0]].get_center(), radius=0.22, color=PATH_COLOR)
        ring = Circle(radius=0.32, color=PATH_COLOR, stroke_width=4).move_to(marker.get_center())
        self.play(FadeIn(marker, scale=0.4), Create(ring))
        self.play(Flash(marker, color=PATH_COLOR, line_length=0.25))
        self.wait(0.2)

        edges_drawn = VGroup()
        for a, b in zip(path[:-1], path[1:]):
            edge = Line(dots[a].get_center(), dots[b].get_center(), color=PATH_COLOR, stroke_width=6)
            self.play(
                Create(edge),
                marker.animate.move_to(dots[b].get_center()),
                ring.animate.move_to(dots[b].get_center()),
                run_time=0.9,
            )
            self.play(Flash(marker, color=PATH_COLOR, line_length=0.22), run_time=0.4)
            edges_drawn.add(edge)
            self.wait(0.15)

        self.wait(0.3)
        self.play(FadeOut(cap))

        final_dot = dots[path[-1]]
        halo = Circle(radius=0.55, color=OPTIMAL_COLOR, stroke_width=5).move_to(final_dot.get_center())
        star = Star(color=OPTIMAL_COLOR, fill_color=OPTIMAL_COLOR, fill_opacity=1, outer_radius=0.28)
        star.move_to(final_dot.get_center())
        optimal_label = thai("Optimal — ไม่มีจุดยอดข้าง ๆ ที่ดีกว่านี้แล้ว", size=24, color=OPTIMAL_COLOR, weight=BOLD)
        optimal_label.next_to(final_dot, UR, buff=0.4)

        self.play(final_dot.animate.set_color(OPTIMAL_COLOR).scale(1.2), FadeOut(ring))
        self.play(Create(halo), FadeIn(star, scale=0.3), FadeIn(optimal_label))
        self.play(Flash(final_dot, color=OPTIMAL_COLOR, line_length=0.4, flash_radius=0.7))
        self.wait(1.2)

        self._final_group = VGroup(marker, edges_drawn, halo, star, optimal_label)

    # ------------------------------------------------------------------
    def closing_message(self):
        msg1 = thai("MILP (0/1 จริง ๆ) = NP-hard, ค้นหาแบบละเอียดยิบยาก", size=26, color=BG_DOT)
        msg2 = thai("LP Relaxation = นูน (Convex) → คำตอบดีที่สุดอยู่ที่จุดยอดเสมอ", size=26, color=HULL_STROKE, weight=BOLD)
        msg3 = thai("Simplex ไล่ตามขอบจากจุดยอดสู่จุดยอด → ได้คำตอบไวในทางปฏิบัติ", size=26, color=OPTIMAL_COLOR, weight=BOLD)
        group = VGroup(msg1, msg2, msg3).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        group.to_edge(DOWN, buff=1.0)

        self.play(*[FadeOut(m) for m in self.mobjects if m not in group])
        self.play(FadeIn(msg1, shift=UP * 0.1))
        self.wait(0.6)
        self.play(FadeIn(msg2, shift=UP * 0.1))
        self.wait(0.6)
        self.play(FadeIn(msg3, shift=UP * 0.1))
        self.wait(1.8)
        self.play(FadeOut(group))
