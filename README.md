> Repositorio migrado desde `github.com/literato1987`, cuenta anterior del mismo autor,
> sin acceso desde agosto de 2026. El historial de commits se conserva íntegro.

# Glyph Matrix Simulator

CLI preview tool for **Nothing Phone (3)** Glyph Matrix layouts.

Unlike generic grid editors, this simulator uses the **official 621-LED allocation** from [GlyphMatrix-Developer-Kit](https://github.com/Nothing-Developer-Programme/GlyphMatrix-Developer-Kit) (`image/23111_25111_LED_allocation.svg`). Pixels outside real LED positions are clipped — what you see is much closer to the physical matrix.

Built to develop and document [Glyph Stock Ticker](https://github.com/literato1987/glyph-stock-ticker), but useful for any Phone (3) toy that renders text on `addTop` / `addMid` / `addLow`.

**Device:** Nothing Phone (3) · 25×25 logical grid · 621 physical LEDs

## Why this exists

| Tool | What it does |
|---|---|
| [GlyphMatrixEditor](https://github.com/pauwma/GlyphMatrixEditor) | Full web editor — drawing, animation, export |
| [glyph-matrix-lab](https://github.com/alex-1121/glyph-matrix-lab) | Android toy builder for Phone (4a) Pro (13×13) |
| **This repo** | Lightweight CLI: official LED mask + toy pixel font → PNG previews for READMEs and dev |

No other public repo we found combines the **official Phone (3) LED SVG mask** with a **matching 3×5 pixel font** for quick `--top/--mid/--low` renders.

## Install

```bash
git clone https://github.com/literato1987/glyph-matrix-simulator.git
cd glyph-matrix-simulator
pip install -r requirements.txt
```

Requires Python 3.10+ and Pillow.

## Usage

```bash
python preview.py --top TSLA --mid 421 --low +2% -o preview.png
```

Dim dots (optional) = real LED positions. Bright dots = lit pixels.

### Common flags

| Flag | Example | Purpose |
|---|---|---|
| `--top` | `NVDA` | Top layer (symbol) |
| `--mid` | `140` | Middle layer (price) |
| `--low` | `+3%` | Bottom layer (change) |
| `--scale` | `24` | Pixels per matrix cell |
| `--crop` | | Crop to LED cluster bounds |
| `--no-grid` | | Hide unlit LED positions (cleaner README images) |
| `--github-strip` | | Export TSLA/BTC/NVDA strip for README |
| `-o` | `out.png` | Output file |

### README strip

```bash
python preview.py --github-strip -o preview-github.png --scale 28
```

## Pixel font

Glyphs live in `preview.py` (`GLYPHS`). Keep them in sync with `MatrixPixelFont.kt` in your toy if you share the same font.

Supported letters used by stock ticker: `A B C D E L N R S T V Y` plus digits and `. + - %`.

**Tip:** letters like `N` need a visible diagonal — a filled centre (`###`) reads as `M` on the matrix.

## LED mask

`led_mask.py` is generated from `23111_25111_LED_allocation.svg` (included). Regenerate if Nothing updates the SVG:

```bash
# led_mask.py was hand-parsed from the official SVG coordinates
```

## Related

- [glyph-stock-ticker](https://github.com/literato1987/glyph-stock-ticker) — live stock/crypto Glyph Toy
- [GlyphMatrix Developer Kit](https://github.com/Nothing-Developer-Programme/GlyphMatrix-Developer-Kit)

## License

MIT — see [LICENSE](LICENSE). LED allocation diagram © Nothing Technology.