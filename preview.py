#!/usr/bin/env python3
"""Preview a 25x25 Glyph Matrix using the official Phone (3) LED allocation."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from led_mask import LED_MASK, SIZE, is_led

GLYPH_W = 3
GLYPH_H = 5
GLYPH_SPACING = 1

LAYER_Y = {
    "top": 5,
    "mid": 11,
    "low": 17,
}

GLYPHS: dict[str, list[str]] = {
    "0": ["111", "101", "101", "101", "111"],
    "1": ["010", "110", "010", "010", "111"],
    "2": ["111", "001", "111", "100", "111"],
    "3": ["111", "001", "111", "001", "111"],
    "4": ["101", "101", "111", "001", "001"],
    "5": ["111", "100", "111", "001", "111"],
    "6": ["111", "100", "111", "101", "111"],
    "7": ["111", "001", "010", "010", "010"],
    "8": ["111", "101", "111", "101", "111"],
    "9": ["111", "101", "111", "001", "111"],
    ".": ["000", "000", "000", "000", "010"],
    "+": ["000", "010", "111", "010", "000"],
    "-": ["000", "000", "111", "000", "000"],
    "%": ["100", "001", "010", "100", "001"],
    "E": ["111", "100", "110", "100", "111"],
    "R": ["110", "101", "110", "101", "101"],
    "T": ["111", "010", "010", "010", "010"],
    "S": ["111", "100", "111", "001", "111"],
    "A": ["010", "101", "111", "101", "101"],
    "B": ["110", "101", "110", "101", "110"],
    "C": ["011", "100", "100", "100", "011"],
    "D": ["110", "101", "101", "101", "110"],
    "N": ["101", "110", "011", "101", "101"],
    "V": ["101", "101", "101", "101", "010"],
    "L": ["100", "100", "100", "100", "111"],
    "Y": ["101", "101", "010", "010", "010"],
    "r": ["000", "101", "110", "101", "101"],
    "e": ["000", "011", "111", "100", "111"],
    "y": ["000", "101", "101", "111", "001"],
    "t": ["010", "111", "010", "010", "001"],
    "k": ["100", "101", "110", "101", "101"],
}


def text_width(text: str) -> int:
    cell = GLYPH_W + GLYPH_SPACING
    return len(text) * cell - GLYPH_SPACING


def center_x(text: str) -> int:
    return max((SIZE - text_width(text)) // 2, 0)


def stamp_text(grid: list[list[bool]], text: str, y: int) -> None:
    x = center_x(text)
    for char in text:
        glyph = GLYPHS.get(char)
        if glyph:
            for row_i, row in enumerate(glyph):
                for col_i, pixel in enumerate(row):
                    if pixel != "1":
                        continue
                    px = x + col_i
                    py = y + row_i
                    if is_led(px, py):
                        grid[py][px] = True
        x += GLYPH_W + GLYPH_SPACING


def build_grid(top: str | None, mid: str | None, low: str | None) -> list[list[bool]]:
    grid = [[False] * SIZE for _ in range(SIZE)]
    if top:
        stamp_text(grid, top, LAYER_Y["top"])
    if mid:
        stamp_text(grid, mid, LAYER_Y["mid"])
    if low:
        stamp_text(grid, low, LAYER_Y["low"])
    return grid


def led_bounds() -> tuple[int, int, int, int]:
    xs = [x for y in range(SIZE) for x in range(SIZE) if LED_MASK[y][x]]
    ys = [y for y in range(SIZE) for x in range(SIZE) if LED_MASK[y][x]]
    return min(xs), min(ys), max(xs) + 1, max(ys) + 1


def render_pearls(
    grid: list[list[bool]],
    scale: int = 20,
    pearl_ratio: float = 0.38,
    padding: int = 8,
    show_all_leds: bool = True,
    crop_to_leds: bool = False,
    dim_led_color: tuple[int, int, int] = (28, 28, 28),
) -> Image.Image:
    canvas = SIZE * scale + padding * 2
    img = Image.new("RGB", (canvas, canvas), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    radius = max(scale * pearl_ratio, 2)
    dim_radius = max(radius * 0.55, 1)

    if show_all_leds:
        for y in range(SIZE):
            for x in range(SIZE):
                if not LED_MASK[y][x]:
                    continue
                cx = padding + x * scale + scale / 2
                cy = padding + y * scale + scale / 2
                draw.ellipse(
                    (cx - dim_radius, cy - dim_radius, cx + dim_radius, cy + dim_radius),
                    fill=dim_led_color,
                )

    for y in range(SIZE):
        for x in range(SIZE):
            if not grid[y][x]:
                continue
            cx = padding + x * scale + scale / 2
            cy = padding + y * scale + scale / 2
            draw.ellipse(
                (cx - radius, cy - radius, cx + radius, cy + radius),
                fill=(255, 255, 255),
            )

    if crop_to_leds:
        x0, y0, x1, y1 = led_bounds()
        left = int(padding + x0 * scale)
        top = int(padding + y0 * scale)
        right = int(padding + x1 * scale)
        bottom = int(padding + y1 * scale)
        margin = max(scale // 2, 4)
        img = img.crop((
            max(0, left - margin),
            max(0, top - margin),
            min(img.width, right + margin),
            min(img.height, bottom + margin),
        ))

    return img


def render(
    top: str | None,
    mid: str | None,
    low: str | None,
    scale: int = 20,
    *,
    show_all_leds: bool = True,
    crop_to_leds: bool = False,
) -> Image.Image:
    return render_pearls(
        build_grid(top, mid, low),
        scale=scale,
        show_all_leds=show_all_leds,
        crop_to_leds=crop_to_leds,
    )


def render_github_strip(output: Path, scale: int = 28) -> Image.Image:
    panels = [
        ("TSLA", "TSLA", "421", "+2%"),
        ("BTC", "BTC", "87k", "-1%"),
        ("NVDA", "NVDA", "140", "+3%"),
    ]
    rendered: list[Image.Image] = []
    for _label, top, mid, low in panels:
        rendered.append(
            render(
                top,
                mid,
                low,
                scale=scale,
                show_all_leds=False,
                crop_to_leds=True,
            ),
        )

    gap = scale
    label_h = scale + 8
    width = sum(img.width for img in rendered) + gap * (len(rendered) - 1)
    height = max(img.height for img in rendered) + label_h
    strip = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(strip)
    x = 0
    y0 = label_h
    for (label, _top, _mid, _low), img in zip(panels, rendered, strict=True):
        strip.paste(img, (x, y0 + (max(img.height for img in rendered) - img.height) // 2))
        draw.text((x + 4, 4), label, fill=(180, 180, 180))
        x += img.width + gap

    strip.save(output)
    return strip


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview Phone (3) Glyph Matrix (official LED map)")
    parser.add_argument("--top", help="Top layer text (e.g. TSLA)")
    parser.add_argument("--mid", help="Middle layer text (e.g. 421)")
    parser.add_argument("--low", help="Bottom layer text (e.g. +2.1%%)")
    parser.add_argument("-o", "--output", default="glyph-preview.png")
    parser.add_argument("--scale", type=int, default=20, help="Pixels per matrix cell")
    parser.add_argument("--crop", action="store_true", help="Crop to LED cluster bounds")
    parser.add_argument("--no-grid", action="store_true", help="Hide unlit LED positions")
    parser.add_argument("--github-strip", action="store_true", help="Export README strip (TSLA/BTC/NVDA)")
    args = parser.parse_args()

    output = Path(args.output)
    if args.github_strip:
        render_github_strip(output, scale=args.scale)
        print(f"Wrote {output.resolve()} (GitHub README strip, scale {args.scale}px/cell)")
    else:
        image = render(
            args.top,
            args.mid,
            args.low,
            scale=args.scale,
            show_all_leds=not args.no_grid,
            crop_to_leds=args.crop,
        )
        image.save(output)
        print(f"Wrote {output.resolve()} (621 LEDs, 25x25 logical, scale {args.scale}px/cell)")


if __name__ == "__main__":
    main()