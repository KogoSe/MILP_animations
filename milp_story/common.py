"""Shared visual building blocks for the MILP explainer story.

Everything here is deliberately visual-first: boxes, bars, arrows, colors.
Keep heavy math (formulas) out of this file — it belongs to individual
scenes only where it earns its place, and even there stays secondary to
the picture.
"""
from manim import *

THAI_FONT = "Leelawadee UI"

UPS_UNITS = ["A", "B", "C", "D"]

UPS_COLORS = {
    "A": "#5B9BD5",
    "B": "#70AD47",
    "C": "#FFC000",
    "D": "#ED7D31",
}

PAIR_COLORS = {
    "AB": "#B5D4F4", "AC": "#9FE1CB", "AD": "#C0DD97",
    "BC": "#FAC775", "BD": "#F4C0D1", "CD": "#F5C4B3",
}

FAIL_COLOR = "#E74C3C"
OK_COLOR = "#2ECC71"
WARN_COLOR = "#F39C12"
INK = "#2B2B2B"
PAPER = "#F7F5F0"

PAIRS = ["AB", "AC", "AD", "BC", "BD", "CD"]


def thai(s, size=32, color=WHITE, weight=NORMAL, **kwargs):
    return Text(s, font=THAI_FONT, font_size=size, color=color, weight=weight, **kwargs)


def title_card(text_str, sub=None):
    """A simple top-left title + optional subtitle, meant to persist through a scene."""
    title = thai(text_str, size=40, weight=BOLD)
    title.to_edge(UP, buff=0.5)
    group = VGroup(title)
    if sub:
        subtitle = thai(sub, size=24, color=GRAY_B)
        subtitle.next_to(title, DOWN, buff=0.2)
        group.add(subtitle)
    return group


def ups_box(label, size=1.1, show_label=True):
    box = Square(
        side_length=size,
        fill_color=UPS_COLORS[label],
        fill_opacity=0.85,
        stroke_color=WHITE,
        stroke_width=2,
    )
    grp = VGroup(box)
    if show_label:
        txt = thai(label, size=32, color=WHITE, weight=BOLD)
        txt.move_to(box.get_center())
        grp.add(txt)
    grp.ups_label = label
    return grp


def ups_row(spacing=2.4, size=1.1):
    boxes = VGroup(*[ups_box(u, size=size) for u in UPS_UNITS])
    boxes.arrange(RIGHT, buff=spacing - size)
    return boxes


def fail_mark(mobj, scale=1.0):
    """A red X placed over an existing mobject to mark it as failed."""
    x1 = Line(UL, DR, color=FAIL_COLOR, stroke_width=8)
    x2 = Line(UR, DL, color=FAIL_COLOR, stroke_width=8)
    cross = VGroup(x1, x2).scale(0.5 * scale)
    cross.move_to(mobj.get_center())
    return cross


def flow_arrow(start_mobj, end_mobj, label_str=None, color=WHITE, width=6):
    arrow = Arrow(
        start_mobj.get_bottom() + DOWN * 0.05,
        end_mobj.get_top() + UP * 0.05,
        buff=0.15,
        color=color,
        stroke_width=width,
    )
    grp = VGroup(arrow)
    if label_str:
        lbl = thai(label_str, size=22, color=color)
        lbl.next_to(arrow, direction=arrow.get_unit_vector(), buff=0.1)
        lbl.shift(RIGHT * 0.3)
        grp.add(lbl)
    return grp


def load_meter(value, max_value, width=4.0, height=0.4, color=OK_COLOR, label_str=None):
    """Horizontal bar meter representing a load value out of some max."""
    frac = max(0.0, min(1.0, value / max_value if max_value else 0))
    back = Rectangle(width=width, height=height, stroke_color=GRAY_B, fill_color="#333333", fill_opacity=1)
    fill = Rectangle(width=max(width * frac, 0.001), height=height, fill_color=color, fill_opacity=1, stroke_width=0)
    fill.align_to(back, LEFT)
    grp = VGroup(back, fill)
    if label_str:
        lbl = thai(label_str, size=22, color=WHITE)
        lbl.next_to(grp, LEFT, buff=0.25)
        grp.add(lbl)
    grp.bar_back = back
    grp.bar_fill = fill
    grp.max_value = max_value
    grp.width_full = width
    return grp


def set_meter_value(meter, value):
    frac = max(0.0, min(1.0, value / meter.max_value if meter.max_value else 0))
    new_fill = Rectangle(
        width=max(meter.width_full * frac, 0.001),
        height=meter.bar_fill.height,
        fill_color=meter.bar_fill.fill_color,
        fill_opacity=1,
        stroke_width=0,
    )
    new_fill.align_to(meter.bar_back, LEFT)
    return new_fill


def caption(text_str, size=26, color=GRAY_A):
    cap = thai(text_str, size=size, color=color)
    cap.to_edge(DOWN, buff=0.5)
    return cap
