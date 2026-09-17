"""Scene 01 -- "The Problem"

Built strictly from scene01_prompt.md (Beats 1.1-1.8), with the Row 2 load
correction from video_scenes_02_to_12_prompt.md Section 4 (620 -> 600 kW).

All on-screen text is English. All positions/sizes follow the prompt's
layout tables. Every beat ends with check_layout() (see Section 3 of the
prompt) which asserts every top-level object stays inside the safe frame
and that no two registered items overlap (except allowed overlaps).

Run with:
    manim -pqh scene01_problem.py Scene01Problem
"""
import os

from manim import *

# --------------------------------------------------------------- style ---
BG_COLOR = "#0a0e1a"
TEXT_COLOR = "#e6e9ef"
SECONDARY_COLOR = "#8a93a6"
RACK_FILL = "#2a3550"
RACK_STROKE = "#4a5878"
UPS_COLORS = {"A": "#00d4ff", "B": "#ffaa00", "C": "#a66cff", "D": "#3ddc84"}
FAIL_FILL = "#3a3f4b"
FAIL_COLOR = "#ff3b3b"
HL_COLOR = "#ffe600"

UPS_NAMES = ["A", "B", "C", "D"]

# ---------------------------------------------------------------- data ---
ROWS = [
    {"name": "Row 1", "kw": 500, "type": "2-source"},
    {"name": "Row 2", "kw": 600, "type": "4-source"},  # corrected 620 -> 600
    {"name": "Row 3", "kw": 480, "type": "2-source"},
    {"name": "Row 4", "kw": 550, "type": "2-source"},
]

REVIEW = True
REVIEW_DIR = os.path.join(os.path.dirname(__file__), "review")


def fmt_kw(x):
    if float(x).is_integer():
        return f"{int(x)} kW"
    return f"{x:.1f} kW"


# -------------------------------------------------------------- layout ---
def caption(text):
    t = Tex(text, font_size=34, color=TEXT_COLOR)
    if t.width > 12.5:
        t.scale_to_fit_width(12.5)
        if t.font_size < 28:
            raise ValueError(f"Caption too long even at font 28: {text!r}")
    t.move_to([0, -3.25, 0])
    return t


def in_frame(m, margin=0.4):
    return (
        m.get_left()[0] >= -config.frame_width / 2 + margin
        and m.get_right()[0] <= config.frame_width / 2 - margin
        and m.get_bottom()[1] >= -config.frame_height / 2 + margin
        and m.get_top()[1] <= config.frame_height / 2 - margin
    )


def boxes_overlap(a, b, pad=0.05):
    return not (
        a.get_right()[0] + pad <= b.get_left()[0]
        or b.get_right()[0] + pad <= a.get_left()[0]
        or a.get_top()[1] + pad <= b.get_bottom()[1]
        or b.get_top()[1] + pad <= a.get_bottom()[1]
    )


def make_ups_box(letter, w=1.2, h=0.7, font_size=26):
    color = UPS_COLORS[letter]
    box = Rectangle(width=w, height=h, stroke_color=color, stroke_width=2,
                     fill_color=color, fill_opacity=0.15)
    label = Tex(f"UPS {letter}", font_size=font_size, color=TEXT_COLOR)
    if label.width > w - 0.1:
        label.scale_to_fit_width(w - 0.1)
    label.move_to(box.get_center())
    grp = VGroup(box, label)
    grp.box = box
    grp.label = label
    grp.letter = letter
    return grp


def set_failed(ups_grp):
    box = ups_grp.box
    new_box = box.copy().set_fill(FAIL_FILL, opacity=1).set_stroke(SECONDARY_COLOR, width=2)
    cross = VGroup(
        Line(box.get_corner(UL), box.get_corner(DR), color=FAIL_COLOR, stroke_width=4),
        Line(box.get_corner(DL), box.get_corner(UR), color=FAIL_COLOR, stroke_width=4),
    )
    return new_box, cross


def make_cable(start, corner1, corner2, end, color):
    return VMobject(color=color, stroke_width=4).set_points_as_corners(
        [start, corner1, corner2, end]
    )


class Scene01Problem(MovingCameraScene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        if REVIEW:
            os.makedirs(REVIEW_DIR, exist_ok=True)
        self._beat_count = 0
        self.current_caption = None

        self.beat_1_1_floor_plan()
        self.beat_1_2_power_path()
        self.beat_1_3_zoom_into_row()
        self.beat_1_4_two_source_row()
        self.beat_1_5_four_source_row()
        self.beat_1_6_real_data()
        self.beat_1_7_scale_up()
        self.beat_1_8_question()

    # --------------------------------------------------------- helpers ---
    def swap_caption(self, text):
        new_cap = caption(text)
        anims = []
        if self.current_caption is not None:
            anims.append(FadeOut(self.current_caption))
        self.play(*anims) if anims else None
        self.play(FadeIn(new_cap))
        self.current_caption = new_cap
        return new_cap

    def check_layout(self, beat_id):
        background = getattr(self, "background_items", [])
        for m in [*self.layout_items, *background]:
            if not in_frame(m):
                raise ValueError(f"[{beat_id}] object out of frame: {m}")
        n = len(self.layout_items)
        for i in range(n):
            for j in range(i + 1, n):
                a, b = self.layout_items[i], self.layout_items[j]
                if (i, j) in self.allowed_overlaps or (j, i) in self.allowed_overlaps:
                    continue
                if boxes_overlap(a, b):
                    raise ValueError(f"[{beat_id}] overlap between item {i} and item {j}")
        if REVIEW:
            self._beat_count += 1
            path = os.path.join(REVIEW_DIR, f"scene01_beat_{self._beat_count:02d}.png")
            self.camera.frame.save_state()
            self.renderer.camera.save_image_to(path) if hasattr(
                self.renderer.camera, "save_image_to"
            ) else None

    # ===================================================== Beat 1.1 =====
    def beat_1_1_floor_plan(self):
        building = Rectangle(width=10.4, height=5.5, stroke_color=RACK_STROKE, stroke_width=2)
        building.move_to([(-6.4 + 4.0) / 2, (-2.3 + 3.2) / 2, 0])

        inner_wall = Line([0.6, -2.3, 0], [0.6, 3.2, 0], color=RACK_STROKE, stroke_width=2)

        it_hall_lbl = Tex("IT Hall", font_size=26, color=SECONDARY_COLOR)
        it_hall_lbl.move_to([-6.2 + it_hall_lbl.width / 2, 2.85, 0], aligned_edge=LEFT)
        ups_room_lbl = Tex("UPS Room", font_size=26, color=SECONDARY_COLOR)
        ups_room_lbl.move_to([0.8 + ups_room_lbl.width / 2, 2.85, 0], aligned_edge=LEFT)
        outdoor_lbl = Tex("Outdoor", font_size=26, color=SECONDARY_COLOR)
        outdoor_lbl.move_to([4.8 + outdoor_lbl.width / 2, 2.85, 0], aligned_edge=LEFT)

        row_ys = [2.1, 1.2, 0.3, -0.6]
        rack_rows = VGroup()
        row_labels = VGroup()
        first_x = -4.75
        for idx, y in enumerate(row_ys):
            racks = VGroup(*[
                Rectangle(width=0.42, height=0.30, stroke_color=RACK_STROKE, stroke_width=1.5,
                          fill_color=RACK_FILL, fill_opacity=1).move_to([first_x + i * 0.5, y, 0])
                for i in range(10)
            ])
            lbl = Tex(f"Row {idx + 1}", font_size=26, color=TEXT_COLOR)
            lbl.move_to([-5.2 - lbl.width / 2, y, 0], aligned_edge=RIGHT)
            rack_rows.add(racks)
            row_labels.add(lbl)

        ups_boxes = VGroup()
        ups_positions = {"A": (1.5, 1.6), "B": (3.1, 1.6), "C": (1.5, 0.2), "D": (3.1, 0.2)}
        for letter, (x, y) in ups_positions.items():
            box = Rectangle(width=1.2, height=0.7, stroke_color=UPS_COLORS[letter], stroke_width=2,
                             fill_color=UPS_COLORS[letter], fill_opacity=0.15)
            box.move_to([x, y, 0])
            lbl = Tex(f"UPS {letter}", font_size=26, color=TEXT_COLOR)
            if lbl.width > box.width - 0.1:
                lbl.scale_to_fit_width(box.width - 0.1)
            lbl.move_to(box.get_center())
            ups_boxes.add(VGroup(box, lbl))

        transformer_box = Rectangle(width=1.6, height=0.7, stroke_color=RACK_STROKE, stroke_width=2)
        transformer_box.move_to([5.6, 1.6, 0])
        transformer_lbl = Tex("Transformer", font_size=24, color=TEXT_COLOR)
        if transformer_lbl.width > transformer_box.width - 0.15:
            transformer_lbl.scale_to_fit_width(transformer_box.width - 0.15)
        transformer_lbl.move_to(transformer_box.get_center())

        generator_box = Rectangle(width=1.6, height=0.7, stroke_color=RACK_STROKE, stroke_width=2)
        generator_box.move_to([5.6, 0.2, 0])
        generator_lbl = Tex("Generator", font_size=24, color=TEXT_COLOR)
        if generator_lbl.width > generator_box.width - 0.15:
            generator_lbl.scale_to_fit_width(generator_box.width - 0.15)
        generator_lbl.move_to(generator_box.get_center())

        self.play(Create(building), Create(inner_wall), run_time=1.2)
        self.play(FadeIn(it_hall_lbl), FadeIn(ups_room_lbl), FadeIn(outdoor_lbl), run_time=0.5)

        for racks, lbl in zip(rack_rows, row_labels):
            self.play(
                LaggedStart(*[FadeIn(r) for r in racks], lag_ratio=0.08),
                FadeIn(lbl),
                run_time=0.7,
            )

        self.play(*[FadeIn(u) for u in ups_boxes], run_time=0.6)
        self.play(FadeIn(VGroup(transformer_box, transformer_lbl)),
                   FadeIn(VGroup(generator_box, generator_lbl)), run_time=0.6)

        cap = self.swap_caption("A data hall must never lose power --- not even for a second.")

        # building outline and inner wall are structural framing (like cables):
        # everything else is intentionally drawn inside them, so they are
        # checked only for staying in frame, not for pairwise overlap.
        self.background_items = [building, inner_wall]
        self.layout_items = [
            it_hall_lbl, ups_room_lbl, outdoor_lbl,
            *rack_rows, *row_labels, *ups_boxes,
            transformer_box, transformer_lbl, generator_box, generator_lbl, cap,
        ]
        self.allowed_overlaps = set()
        # register text-inside-box pairs as allowed overlaps
        idx_transformer_box = self.layout_items.index(transformer_box)
        idx_transformer_lbl = self.layout_items.index(transformer_lbl)
        idx_generator_box = self.layout_items.index(generator_box)
        idx_generator_lbl = self.layout_items.index(generator_lbl)
        self.allowed_overlaps.add((idx_transformer_box, idx_transformer_lbl))
        self.allowed_overlaps.add((idx_generator_box, idx_generator_lbl))
        self.check_layout("1.1")

        self._floor = dict(
            building=building, inner_wall=inner_wall,
            it_hall_lbl=it_hall_lbl, ups_room_lbl=ups_room_lbl, outdoor_lbl=outdoor_lbl,
            rack_rows=rack_rows, row_labels=row_labels, ups_boxes=ups_boxes,
            transformer_box=transformer_box, transformer_lbl=transformer_lbl,
            generator_box=generator_box, generator_lbl=generator_lbl,
        )

    # ===================================================== Beat 1.2 =====
    def beat_1_2_power_path(self):
        f = self._floor
        arrow1 = Arrow([4.8, 0.9, 0], [3.7, 0.9, 0], stroke_width=4, color=TEXT_COLOR, buff=0)
        arrow2 = Arrow([2.3, -1.6, 0], [-2.5, -1.6, 0], stroke_width=4, color=TEXT_COLOR, buff=0)

        self.play(Create(arrow1), Create(arrow2), run_time=1.0)

        dot1 = Dot(arrow1.get_start(), radius=0.06, color=HL_COLOR)
        dot2 = Dot(arrow2.get_start(), radius=0.06, color=HL_COLOR)
        self.play(FadeIn(dot1), FadeIn(dot2))
        for _ in range(2):
            self.play(
                dot1.animate.move_to(arrow1.get_end()),
                dot2.animate.move_to(arrow2.get_end()),
                run_time=0.8,
            )
            self.play(
                dot1.animate.move_to(arrow1.get_start()),
                dot2.animate.move_to(arrow2.get_start()),
                run_time=0.01,
            )
        self.play(FadeOut(dot1), FadeOut(dot2))

        cap = self.swap_caption("Every rack is powered through the UPS.")

        self.background_items = [f["building"], f["inner_wall"]]
        self.layout_items = [
            f["it_hall_lbl"], f["ups_room_lbl"], f["outdoor_lbl"],
            *f["rack_rows"], *f["row_labels"], *f["ups_boxes"],
            f["transformer_box"], f["transformer_lbl"], f["generator_box"], f["generator_lbl"],
            arrow1, arrow2, cap,
        ]
        idx_transformer_box = self.layout_items.index(f["transformer_box"])
        idx_transformer_lbl = self.layout_items.index(f["transformer_lbl"])
        idx_generator_box = self.layout_items.index(f["generator_box"])
        idx_generator_lbl = self.layout_items.index(f["generator_lbl"])
        self.allowed_overlaps = {
            (idx_transformer_box, idx_transformer_lbl),
            (idx_generator_box, idx_generator_lbl),
        }
        self.check_layout("1.2")

        self._arrows = (arrow1, arrow2)

    # ===================================================== Beat 1.3 =====
    def beat_1_3_zoom_into_row(self):
        f = self._floor
        row1_racks = f["rack_rows"][0]
        row1_label = f["row_labels"][0]

        self.play(row1_racks.animate.set_stroke(TEXT_COLOR, width=2), run_time=0.5)
        self.wait(0.1)

        to_fade = VGroup(
            f["building"], f["inner_wall"], f["it_hall_lbl"], f["ups_room_lbl"], f["outdoor_lbl"],
            *f["rack_rows"][1:], *f["row_labels"][1:],
            f["transformer_box"], f["transformer_lbl"], f["generator_box"], f["generator_lbl"],
            *self._arrows,
        )
        if self.current_caption is not None:
            self.play(FadeOut(self.current_caption))
            self.current_caption = None
        self.play(FadeOut(to_fade))

        schematic_ups = VGroup()
        xs = [-3.3, -1.1, 1.1, 3.3]
        for letter, x in zip(UPS_NAMES, xs):
            grp = make_ups_box(letter, w=1.4, h=0.8, font_size=30)
            grp.move_to([x, 2.6, 0])
            schematic_ups.add(grp)

        row_block = Rectangle(width=3.0, height=0.9, fill_color=RACK_FILL, fill_opacity=1,
                               stroke_color=RACK_STROKE, stroke_width=2)
        row_block.move_to([0, -1.4, 0])
        row_name = Tex("Row 1", font_size=30, color=TEXT_COLOR)
        row_kw = Tex(fmt_kw(ROWS[0]["kw"]), font_size=26, color=TEXT_COLOR)
        row_name.move_to(row_block.get_center() + UP * 0.2)
        row_kw.move_to(row_block.get_center() + DOWN * 0.2)
        row_group = VGroup(row_block, row_name, row_kw)

        self.play(
            ReplacementTransform(VGroup(*f["ups_boxes"]).copy(), schematic_ups),
            FadeOut(VGroup(*f["ups_boxes"])),
            ReplacementTransform(VGroup(row1_racks, row1_label).copy(), row_group),
            FadeOut(VGroup(row1_racks, row1_label)),
            run_time=1.2,
        )

        self.layout_items = [*schematic_ups, row_block, row_name, row_kw]
        idx_block = self.layout_items.index(row_block)
        idx_name = self.layout_items.index(row_name)
        idx_kw = self.layout_items.index(row_kw)
        self.allowed_overlaps = {(idx_block, idx_name), (idx_block, idx_kw)}
        self.check_layout("1.3")

        self._schematic_ups = schematic_ups
        self._row_block = row_block
        self._row_name = row_name
        self._row_kw = row_kw

    # ===================================================== Beat 1.4 =====
    def beat_1_4_two_source_row(self):
        ups = {g.letter: g for g in self._schematic_ups}
        row_block = self._row_block

        tag = Tex("2-source", font_size=26, color=SECONDARY_COLOR)
        tag.move_to([0, -0.6, 0])
        self.play(FadeIn(tag))

        drop_x = 0.6 if tag.width < 1.0 else 0.9
        cable_a = make_cable(
            ups["A"].box.get_bottom(), [ups["A"].box.get_x(), 0.9, 0],
            [-drop_x, 0.9, 0], [-drop_x, row_block.get_top()[1], 0], UPS_COLORS["A"],
        )
        cable_b = make_cable(
            ups["B"].box.get_bottom(), [ups["B"].box.get_x(), 0.9, 0],
            [drop_x, 0.9, 0], [drop_x, row_block.get_top()[1], 0], UPS_COLORS["B"],
        )
        self.play(Create(cable_a), Create(cable_b), run_time=1.0)

        half = ROWS[0]["kw"] / 2
        label_a = Tex(fmt_kw(half), font_size=24, color=UPS_COLORS["A"])
        label_a.move_to([ups["A"].box.get_x() + 0.45, 1.85, 0], aligned_edge=LEFT)
        label_b = Tex(fmt_kw(half), font_size=24, color=UPS_COLORS["B"])
        label_b.move_to([ups["B"].box.get_x() + 0.45, 1.85, 0], aligned_edge=LEFT)
        self.play(FadeIn(label_a), FadeIn(label_b))

        cap = self.swap_caption("Normally, the load is shared equally between two UPS.")
        self.wait(1.5)

        self.background_items = [cable_a, cable_b]
        self.layout_items = [*self._schematic_ups, row_block, self._row_name, self._row_kw,
                              tag, label_a, label_b, cap]
        idx_block = self.layout_items.index(row_block)
        self.allowed_overlaps = {
            (idx_block, self.layout_items.index(self._row_name)),
            (idx_block, self.layout_items.index(self._row_kw)),
        }
        self.check_layout("1.4-normal")

        # failure
        new_box_a, cross_a = set_failed(ups["A"])
        self.play(
            Transform(ups["A"].box, new_box_a),
            ups["A"].label.animate.set_opacity(0.4),
            Create(cross_a),
            cable_a.animate.set_stroke(opacity=0.2),
            FadeOut(label_a),
        )

        counter = DecimalNumber(half, num_decimal_places=0, font_size=24, color=UPS_COLORS["B"])
        counter.add_updater(lambda m: m.next_to(label_b, ORIGIN))
        counter.move_to(label_b.get_center())
        unit_lbl = Tex("kW", font_size=24, color=UPS_COLORS["B"]).next_to(counter, RIGHT, buff=0.1)
        self.play(FadeOut(label_b), FadeIn(counter), FadeIn(unit_lbl))
        self.play(
            counter.animate.set_value(ROWS[0]["kw"]).set_color(HL_COLOR),
            unit_lbl.animate.set_color(HL_COLOR),
            run_time=1.2,
        )
        counter.clear_updaters()

        cap2 = self.swap_caption("If one UPS fails, the other must carry the whole row.")
        self.wait(1.5)

        self.background_items = [cable_a, cable_b]
        self.layout_items = [*self._schematic_ups, row_block, self._row_name, self._row_kw,
                              tag, cross_a, counter, unit_lbl, cap2]
        idx_ups_a = self.layout_items.index(next(u for u in self._schematic_ups if u.letter == "A"))
        idx_cross = self.layout_items.index(cross_a)
        self.allowed_overlaps = {
            (self.layout_items.index(row_block), self.layout_items.index(self._row_name)),
            (self.layout_items.index(row_block), self.layout_items.index(self._row_kw)),
            (idx_ups_a, idx_cross),
        }
        self.check_layout("1.4-fail")

        # reset for next beat
        reset_box = Rectangle(width=1.4, height=0.8, stroke_color=UPS_COLORS["A"], stroke_width=2,
                               fill_color=UPS_COLORS["A"], fill_opacity=0.15).move_to(ups["A"].box)
        self.play(
            FadeOut(cross_a), FadeOut(cable_a), FadeOut(cable_b),
            FadeOut(counter), FadeOut(unit_lbl), FadeOut(tag),
            Transform(ups["A"].box, reset_box),
            ups["A"].label.animate.set_opacity(1),
        )

    # ===================================================== Beat 1.5 =====
    def beat_1_5_four_source_row(self):
        ups = {g.letter: g for g in self._schematic_ups}
        row_block = self._row_block

        new_name = Tex("Row 2", font_size=30, color=TEXT_COLOR).move_to(self._row_name)
        new_kw = Tex(fmt_kw(ROWS[1]["kw"]), font_size=26, color=TEXT_COLOR).move_to(self._row_kw)
        self.play(Transform(self._row_name, new_name), Transform(self._row_kw, new_kw))

        tag = Tex("4-source", font_size=26, color=SECONDARY_COLOR)
        tag.move_to([0, -0.6, 0])

        xs = {"A": -1.2, "B": -0.4, "C": 0.4, "D": 1.2}
        levels = {"A": 1.05, "B": 0.75, "C": 0.75, "D": 1.05}
        cables = {}
        for letter in UPS_NAMES:
            cables[letter] = make_cable(
                ups[letter].box.get_bottom(),
                [ups[letter].box.get_x(), levels[letter], 0],
                [xs[letter], levels[letter], 0],
                [xs[letter], row_block.get_top()[1], 0],
                UPS_COLORS[letter],
            )

        if boxes_overlap(tag, cables["B"]) or boxes_overlap(tag, cables["C"]):
            tag.move_to([0, -2.1, 0])

        self.play(FadeIn(tag))
        self.play(*[Create(c) for c in cables.values()], run_time=1.0)

        quarter = ROWS[1]["kw"] / 4
        labels = {}
        for letter in UPS_NAMES:
            lbl = Tex(fmt_kw(quarter), font_size=24, color=UPS_COLORS[letter])
            lbl.move_to([ups[letter].box.get_x() + 0.45, 1.85, 0], aligned_edge=LEFT)
            labels[letter] = lbl
        self.play(*[FadeIn(l) for l in labels.values()])

        cap = self.swap_caption("A 4-source row is shared by all four UPS.")
        self.wait(1.5)

        self.background_items = list(cables.values())
        self.layout_items = [*self._schematic_ups, row_block, self._row_name, self._row_kw,
                              tag, *labels.values(), cap]
        idx_block = self.layout_items.index(row_block)
        self.allowed_overlaps = {
            (idx_block, self.layout_items.index(self._row_name)),
            (idx_block, self.layout_items.index(self._row_kw)),
        }
        self.check_layout("1.5-normal")

        # failure of A
        new_box_a, cross_a = set_failed(ups["A"])
        self.play(
            Transform(ups["A"].box, new_box_a),
            ups["A"].label.animate.set_opacity(0.4),
            Create(cross_a),
            cables["A"].animate.set_stroke(opacity=0.2),
            FadeOut(labels["A"]),
        )

        third = ROWS[1]["kw"] / 3
        counters = {}
        unit_lbls = {}
        anims = []
        for letter in ("B", "C", "D"):
            c = DecimalNumber(quarter, num_decimal_places=0, font_size=24, color=UPS_COLORS[letter])
            c.move_to(labels[letter].get_center())
            u = Tex("kW", font_size=24, color=UPS_COLORS[letter]).next_to(c, RIGHT, buff=0.1)
            counters[letter] = c
            unit_lbls[letter] = u
            anims += [FadeOut(labels[letter]), FadeIn(c), FadeIn(u)]
        self.play(*anims)
        self.play(
            *[counters[l].animate.set_value(third).set_color(HL_COLOR) for l in ("B", "C", "D")],
            *[unit_lbls[l].animate.set_color(HL_COLOR) for l in ("B", "C", "D")],
            run_time=1.2,
        )

        cap2 = self.swap_caption("If one fails, the remaining three share the load.")
        self.wait(1.5)

        self.background_items = list(cables.values())
        self.layout_items = [*self._schematic_ups, row_block, self._row_name, self._row_kw,
                              tag, cross_a,
                              *counters.values(), *unit_lbls.values(), cap2]
        idx_ups_a = self.layout_items.index(next(u for u in self._schematic_ups if u.letter == "A"))
        idx_cross = self.layout_items.index(cross_a)
        idx_block = self.layout_items.index(row_block)
        self.allowed_overlaps = {
            (idx_block, self.layout_items.index(self._row_name)),
            (idx_block, self.layout_items.index(self._row_kw)),
            (idx_ups_a, idx_cross),
        }
        self.check_layout("1.5-fail")

        self._to_clear_schematic = VGroup(
            *self._schematic_ups, row_block, self._row_name, self._row_kw,
            tag, *cables.values(), cross_a, *counters.values(), *unit_lbls.values(),
        )

    # ===================================================== Beat 1.6 =====
    def beat_1_6_real_data(self):
        if self.current_caption is not None:
            self.play(FadeOut(self.current_caption))
            self.current_caption = None
        self.play(FadeOut(self._to_clear_schematic))

        title = Tex("Electrical Loads", font_size=40, color=TEXT_COLOR)
        title.move_to([0, 3.1, 0])
        self.play(FadeIn(title))

        header = VGroup(
            Tex("Row", font_size=32, color=SECONDARY_COLOR),
            Tex("Load (kW)", font_size=32, color=SECONDARY_COLOR),
            Tex("Type", font_size=32, color=SECONDARY_COLOR),
        )
        header.arrange(RIGHT, buff=1.2)

        data_rows = VGroup()
        for r in ROWS:
            cells = VGroup(
                Tex(r["name"], font_size=32, color=TEXT_COLOR),
                Tex(fmt_kw(r["kw"]), font_size=32, color=TEXT_COLOR),
                Tex(r["type"], font_size=32, color=TEXT_COLOR),
            )
            data_rows.add(cells)

        # align columns using header's x positions
        table = VGroup(header, *data_rows).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        for row in [header, *data_rows]:
            row[1].align_to(header[1], LEFT)
            row[2].align_to(header[2], LEFT)
        table.move_to([0, 0.6, 0])

        underline = Line(
            header.get_corner(DL) + LEFT * 0.1 + DOWN * 0.15,
            header.get_corner(DR) + RIGHT * 0.1 + DOWN * 0.15,
            color=SECONDARY_COLOR, stroke_width=2,
        )

        self.play(FadeIn(header), Create(underline))
        for row in data_rows:
            self.play(FadeIn(row, shift=UP * 0.2), run_time=0.4)

        self.play(*[Indicate(row[1], color=HL_COLOR) for row in data_rows])
        self.play(*[Indicate(row[2], color=HL_COLOR) for row in data_rows])

        cap = self.swap_caption("Each row has its own load and its own source type.")

        self.layout_items = [title, header, underline, *data_rows, cap]
        self.allowed_overlaps = set()
        self.check_layout("1.6")

        self._table_title = title
        self._table_header = header
        self._table_underline = underline
        self._table_rows = data_rows

    # ===================================================== Beat 1.7 =====
    def beat_1_7_scale_up(self):
        table_group = VGroup(self._table_header, self._table_underline, *self._table_rows)
        self.play(table_group.animate.scale(0.7))
        self.play(table_group.animate.next_to(self._table_title, DOWN, buff=0.3))

        ellipsis = Tex(r"$\vdots$", font_size=32 * 0.7, color=TEXT_COLOR)
        ellipsis.move_to(table_group.get_bottom() + DOWN * 0.3)
        row100 = VGroup(
            Tex("Row 100", font_size=32 * 0.7, color=TEXT_COLOR),
            Tex("...", font_size=32 * 0.7, color=TEXT_COLOR),
            Tex("...", font_size=32 * 0.7, color=TEXT_COLOR),
        ).arrange(RIGHT, buff=1.2 * 0.7)
        row100.align_to(table_group, LEFT)
        row100.next_to(ellipsis, DOWN, buff=0.25)

        combo = VGroup(ellipsis, row100)
        if table_group.get_bottom()[1] - 0.3 - row100.height < -2.5:
            scale_needed = (table_group.get_top()[1] - (-2.5)) / (
                table_group.get_top()[1] - row100.get_bottom()[1]
            )
            VGroup(self._table_title, table_group, combo).scale(
                max(scale_needed, 0.5)
            )

        self.play(FadeIn(ellipsis), FadeIn(row100))

        cap = self.swap_caption("A real data hall has hundreds of rows.")

        self.layout_items = [self._table_title, self._table_header, self._table_underline,
                              *self._table_rows, ellipsis, row100, cap]
        self.allowed_overlaps = set()
        self.check_layout("1.7")

        self._full_table_group = VGroup(
            self._table_title, self._table_header, self._table_underline,
            *self._table_rows, ellipsis, row100,
        )

    # ===================================================== Beat 1.8 =====
    def beat_1_8_question(self):
        if self.current_caption is not None:
            self.play(FadeOut(self.current_caption))
            self.current_caption = None
        self.play(FadeOut(self._full_table_group))

        question = Tex("How should we group them?", font_size=54, color=TEXT_COLOR)
        question.move_to(ORIGIN)
        self.play(FadeIn(question))

        self.layout_items = [question]
        self.allowed_overlaps = set()
        self.check_layout("1.8")

        self.wait(2.0)
        self.play(FadeOut(question))
        self.camera.background_color = BLACK
        self.wait(1.0)
