"""Reusable mobjects -- common_prompt.md Section 6."""
from manim import (
    VGroup, Rectangle, RoundedRectangle, Tex, Line, Arrow, DashedLine,
    SurroundingRectangle, Transform, Create, FadeOut, LEFT, RIGHT, DOWN, UP, ORIGIN,
    UL, DR, DL, UR,
)

from .style import (
    BG_COLOR, TEXT_COLOR, SECONDARY_COLOR, UPS_COLORS, UPS_NAMES,
    FAIL_FILL, FAIL_COLOR, ROW_FILL, ROW_STROKE, CUT_COLOR,
)
from .data import fmt_kw


def row_block(name, kw, type_, width=5.0, height=0.46, font=24):
    rect = Rectangle(width=width, height=height, fill_color=ROW_FILL,
                      fill_opacity=1, stroke_color=ROW_STROKE, stroke_width=2)

    name_txt = Tex(name, font_size=font, color=TEXT_COLOR)
    name_txt.move_to(rect.get_center())
    name_txt.align_to(rect, LEFT)
    name_txt.shift(RIGHT * 0.25)

    kw_txt = Tex(fmt_kw(kw), font_size=font, color=TEXT_COLOR)
    kw_txt.move_to(rect.get_center())

    type_txt = Tex(type_, font_size=font, color=SECONDARY_COLOR)
    type_txt.move_to(rect.get_center())
    type_txt.align_to(rect, RIGHT)
    type_txt.shift(LEFT * 0.25)

    grp = VGroup(rect, name_txt, kw_txt, type_txt)
    grp.rect, grp.name, grp.kw, grp.type = rect, name_txt, kw_txt, type_txt
    return grp


def ups_box(letter, w=1.4, h=0.8, font=30, short=False):
    color = UPS_COLORS[letter]
    box = Rectangle(width=w, height=h, stroke_color=color, stroke_width=2,
                     fill_color=color, fill_opacity=0.15)
    label_text = letter if short else f"UPS {letter}"
    label = Tex(label_text, font_size=font, color=TEXT_COLOR)
    if label.width > w - 0.1:
        label.scale_to_fit_width(w - 0.1)
    label.move_to(box.get_center())
    grp = VGroup(box, label)
    grp.box, grp.label, grp.letter = box, label, letter
    return grp


def fail_anims(ups_grp):
    box = ups_grp.box
    new_box = box.copy().set_fill(FAIL_FILL, opacity=1).set_stroke(SECONDARY_COLOR, width=2)
    cross = VGroup(
        Line(box.get_corner(UL), box.get_corner(DR), color=FAIL_COLOR, stroke_width=4),
        Line(box.get_corner(DL), box.get_corner(UR), color=FAIL_COLOR, stroke_width=4),
    )
    ups_grp.cross = cross
    anims = [Transform(box, new_box), ups_grp.label.animate.set_opacity(0.4), Create(cross)]
    return anims


def restore_anims(ups_grp):
    color = UPS_COLORS[ups_grp.letter]
    orig_box = Rectangle(width=ups_grp.box.width, height=ups_grp.box.height,
                          stroke_color=color, stroke_width=2,
                          fill_color=color, fill_opacity=0.15)
    orig_box.move_to(ups_grp.box.get_center())
    anims = [Transform(ups_grp.box, orig_box), ups_grp.label.animate.set_opacity(1)]
    if hasattr(ups_grp, "cross"):
        anims.append(FadeOut(ups_grp.cross))
    return anims


def pair_chip(pair, font=24, pad=0.2):
    # fill_color/fill_opacity are set explicitly (even though the chip is
    # meant to be stroke-only) because Manim's shape default fill_color is
    # its brand red at opacity 0 -- a later .animate.set_opacity() call
    # anywhere up the VGroup chain would otherwise reveal it.
    if pair == "ABCD":
        txt = Tex("ABCD", font_size=font, color=SECONDARY_COLOR)
        box = RoundedRectangle(width=txt.width + 0.3, height=txt.height + pad,
                                corner_radius=0.08, stroke_color=SECONDARY_COLOR, stroke_width=2,
                                fill_color=BG_COLOR, fill_opacity=0)
        box.move_to(txt.get_center())
        grp = VGroup(box, txt)
        grp.box, grp.letters = box, txt
        return grp

    l1, l2 = pair[0], pair[1]
    t1 = Tex(l1, font_size=font, color=UPS_COLORS[l1])
    t2 = Tex(l2, font_size=font, color=UPS_COLORS[l2])
    letters = VGroup(t1, t2).arrange(RIGHT, buff=0.08)
    box = RoundedRectangle(width=letters.width + 0.3, height=letters.height + pad,
                            corner_radius=0.08, stroke_color=TEXT_COLOR, stroke_width=2,
                            fill_color=BG_COLOR, fill_opacity=0)
    box.move_to(letters.get_center())
    grp = VGroup(box, letters)
    grp.box, grp.letters = box, letters
    return grp


def group_frame(mobject, colour, buff=0.1):
    return SurroundingRectangle(mobject, color=colour, buff=buff,
                                 corner_radius=0.08, stroke_width=2.5,
                                 fill_color=BG_COLOR, fill_opacity=0)


def cut_line(length, vertical=False):
    if vertical:
        return DashedLine(DOWN * length / 2, UP * length / 2, color=CUT_COLOR, stroke_width=4)
    return DashedLine(LEFT * length / 2, RIGHT * length / 2, color=CUT_COLOR, stroke_width=4)


def power_train(colour):
    gen_box = Rectangle(width=2.0, height=0.4, stroke_color=colour, stroke_width=2,
                         fill_color=BG_COLOR, fill_opacity=0)
    gen_lbl = Tex("Generator", font_size=22, color=TEXT_COLOR)
    if gen_lbl.width > gen_box.width - 0.2:
        gen_lbl.scale_to_fit_width(gen_box.width - 0.2)
    gen_lbl.move_to(gen_box.get_center())
    gen_grp = VGroup(gen_box, gen_lbl)

    ups_row = VGroup(*[ups_box(l, w=0.5, h=0.4, font=22, short=True) for l in UPS_NAMES])
    ups_row.arrange(RIGHT, buff=0.15)

    arrow = Arrow(UP * 0.15, DOWN * 0.15, stroke_width=3, color=colour, buff=0,
                  max_tip_length_to_length_ratio=0.5)

    stack = VGroup(gen_grp, arrow, ups_row).arrange(DOWN, buff=0.15)

    frame = SurroundingRectangle(stack, color=colour, buff=0.15,
                                  corner_radius=0.08, stroke_width=2)
    card = VGroup(frame, gen_grp, arrow, ups_row)
    card.frame, card.generator, card.arrow, card.ups_row = frame, gen_grp, arrow, ups_row
    return card


def bar_panel(title_text, values: dict, failed, y_max, bar_width=0.6, max_height=1.6, font=22):
    """`values` maps UPS letter -> kW for the surviving UPS (failed excluded)."""
    letters = [l for l in UPS_NAMES if l != failed]
    bars = VGroup()
    val_labels = VGroup()
    letter_labels = VGroup()
    xs = [i * (bar_width + 0.35) for i in range(len(letters))]
    xs = [x - xs[-1] / 2 for x in xs]

    for x, letter in zip(xs, letters):
        v = values.get(letter, 0)
        frac = max(0.0, min(1.0, v / y_max if y_max else 0))
        h = max(max_height * frac, 0.02)
        bar = Rectangle(width=bar_width, height=h, stroke_width=0,
                         fill_color=UPS_COLORS[letter], fill_opacity=1)
        bar.move_to([x, h / 2, 0])
        val_lbl = Tex(fmt_kw(v), font_size=font, color=TEXT_COLOR)
        val_lbl.next_to(bar, UP, buff=0.1)
        letter_lbl = Tex(letter, font_size=font, color=UPS_COLORS[letter])
        letter_lbl.next_to(bar, DOWN, buff=0.1)
        bars.add(bar)
        val_labels.add(val_lbl)
        letter_labels.add(letter_lbl)

    title_lbl = Tex(title_text, font_size=font + 2, color=TEXT_COLOR)
    title_lbl.next_to(VGroup(bars, val_labels), UP, buff=0.25)

    panel = VGroup(title_lbl, bars, val_labels, letter_labels)
    panel.title, panel.bars, panel.val_labels, panel.letter_labels = (
        title_lbl, bars, val_labels, letter_labels,
    )
    return panel


def data_table(cell_matrix, col_gap=0.8, row_gap=0.5):
    """Lay out a 2D list of already-built Mobjects (row 0 is the header) into
    a table with per-column max-width alignment, so a wide cell in one
    column never overlaps its neighbours in any row. Positions every cell
    directly (not via .arrange()), which is the only way to keep columns
    aligned when row heights/widths vary a lot from row to row."""
    n_rows = len(cell_matrix)
    n_cols = len(cell_matrix[0])

    col_widths = [max(cell_matrix[r][c].width for r in range(n_rows)) for c in range(n_cols)]
    col_x = [0.0]
    for w in col_widths[:-1]:
        col_x.append(col_x[-1] + w + col_gap)

    row_heights = [max(cell_matrix[r][c].height for c in range(n_cols)) for r in range(n_rows)]
    row_y = [0.0]
    for h in row_heights[:-1]:
        row_y.append(row_y[-1] - (h + row_gap))

    table = VGroup()
    row_groups = []
    for r in range(n_rows):
        row_vg = VGroup()
        for c in range(n_cols):
            cell = cell_matrix[r][c]
            cell.move_to([col_x[c] + cell.width / 2, row_y[r], 0])
            row_vg.add(cell)
        row_groups.append(row_vg)
        table.add(row_vg)

    table.move_to(ORIGIN)
    table.header = row_groups[0]
    table.rows = VGroup(*row_groups[1:])
    return table
