"""Shared layout-safety system -- common_prompt.md Section 4."""
import os

from manim import Tex, config

from .style import TEXT_COLOR, FONT_CAPTION, FONT_TITLE

REVIEW = True
REVIEW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "review")


def title(text):
    t = Tex(text, font_size=FONT_TITLE, color=TEXT_COLOR)
    t.move_to([0, 3.15, 0])
    return t


def caption(text):
    t = Tex(text, font_size=FONT_CAPTION, color=TEXT_COLOR)
    if t.width > 12.5:
        scale_factor = 12.5 / t.width
        new_font = FONT_CAPTION * scale_factor
        if new_font < 28:
            raise ValueError(
                f"Caption too long even at font 28 ({new_font:.1f}): {text!r}"
            )
        t.scale_to_fit_width(12.5)
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


class LayoutCheckMixin:
    """Mix into a Scene. Set self.layout_items / self.allowed_overlaps
    (and optionally self.background_items) before calling check_layout()."""

    _review_beat_count = 0

    def check_layout(self, beat_id):
        background = getattr(self, "background_items", [])
        for m in [*self.layout_items, *background]:
            if not in_frame(m):
                raise ValueError(f"[{beat_id}] object out of frame: {m}")

        allowed = getattr(self, "allowed_overlaps", set())
        n = len(self.layout_items)
        for i in range(n):
            for j in range(i + 1, n):
                if (i, j) in allowed or (j, i) in allowed:
                    continue
                a, b = self.layout_items[i], self.layout_items[j]
                if boxes_overlap(a, b):
                    raise ValueError(
                        f"[{beat_id}] overlap between item {i} ({a}) and item {j} ({b})"
                    )

        if REVIEW:
            os.makedirs(REVIEW_DIR, exist_ok=True)
            self._review_beat_count += 1
            scene_name = type(self).__name__
            path = os.path.join(
                REVIEW_DIR, f"{scene_name}_{beat_id}.png"
            )
            try:
                image = self.renderer.camera.get_image()
                image.save(path)
            except Exception:
                pass
