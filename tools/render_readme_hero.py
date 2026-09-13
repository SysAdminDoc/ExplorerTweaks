#!/usr/bin/env python3
"""Render the evergreen README hero from approved product artwork."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SIZE = (1280, 640)
DEFAULT_OUTPUT = ROOT / "assets/marketing/readme-hero.png"
VISIBLE_COPY = (
    "WINDOWS DESKTOP APP",
    "ExplorerTweaks",
    "See the setting.",
    "Know the effect.",
    "Configure File Explorer with illustrated previews.",
    "Save profiles or build deployment scripts.",
    "41 settings",
    "Illustrated previews",
    "Dry-run CLI",
    "Portable ZIP",
    "github.com/SysAdminDoc/ExplorerTweaks",
)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = Path("C:/Windows/Fonts") / name
    if not path.is_file():
        raise FileNotFoundError(f"Required Windows font is missing: {path}")
    return ImageFont.truetype(path, size)


def gradient_background() -> Image.Image:
    image = Image.new("RGB", SIZE)
    draw = ImageDraw.Draw(image)
    top = (5, 14, 27)
    bottom = (7, 20, 36)
    for y in range(SIZE[1]):
        amount = y / (SIZE[1] - 1)
        color = tuple(round(a + (b - a) * amount) for a, b in zip(top, bottom))
        draw.line((0, y, SIZE[0], y), fill=color)

    glow = Image.new("L", (320, 160), 0)
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((96, -48, 336, 192), fill=154)
    glow = glow.filter(ImageFilter.GaussianBlur(50)).resize(SIZE, Image.Resampling.LANCZOS)
    color = Image.new("RGB", SIZE, (0, 146, 255))
    image.paste(color, mask=glow.point(lambda value: value // 3))
    return image.convert("RGBA")


def approved_mark(path: Path, maximum: tuple[int, int]) -> Image.Image:
    with Image.open(path) as source:
        source = source.convert("RGBA")
        cropped = source.crop(source.getchannel("A").getbbox())
    cropped.thumbnail(maximum, Image.Resampling.LANCZOS)
    return cropped


def rounded_paste(canvas: Image.Image, artwork: Image.Image, box: tuple[int, int, int, int], radius: int) -> None:
    left, top, right, bottom = box
    fitted = artwork.resize((right - left, bottom - top), Image.Resampling.LANCZOS)
    mask = Image.new("L", fitted.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, fitted.width - 1, fitted.height - 1), radius=radius, fill=255)
    canvas.paste(fitted, (left, top), mask)


def pill(draw: ImageDraw.ImageDraw, x: int, y: int, label: str, accent: str) -> int:
    text_font = font("seguisb.ttf", 15)
    bounds = draw.textbbox((0, 0), label, font=text_font)
    width = bounds[2] - bounds[0] + 50
    draw.rounded_rectangle((x, y, x + width, y + 36), radius=18, fill="#0d2239", outline="#244766", width=1)
    draw.ellipse((x + 15, y + 14, x + 23, y + 22), fill=accent)
    draw.text((x + 31, y + 8), label, font=text_font, fill="#e8f2ff")
    return x + width


def render(root: Path = ROOT) -> Image.Image:
    canvas = gradient_background()
    draw = ImageDraw.Draw(canvas)

    mark = approved_mark(root / "assets/brand/explorertweaks-mark-master.png", (58, 58))
    canvas.alpha_composite(mark, (64, 61))
    draw.text((137, 62), VISIBLE_COPY[0], font=font("seguisb.ttf", 15), fill="#3ed7ff")
    draw.text((137, 85), VISIBLE_COPY[1], font=font("seguisb.ttf", 29), fill="#f7fbff")

    draw.text((64, 169), VISIBLE_COPY[2], font=font("seguibl.ttf", 54), fill="#f8fbff")
    draw.text((64, 229), VISIBLE_COPY[3], font=font("seguibl.ttf", 54), fill="#f8fbff")
    draw.text((64, 320), VISIBLE_COPY[4], font=font("segoeui.ttf", 21), fill="#c8d8ea")
    draw.text((64, 353), VISIBLE_COPY[5], font=font("segoeui.ttf", 21), fill="#c8d8ea")

    right = pill(draw, 64, 424, VISIBLE_COPY[6], "#2be88a")
    pill(draw, right + 12, 424, VISIBLE_COPY[7], "#20bdff")
    right = pill(draw, 64, 471, VISIBLE_COPY[8], "#79a7ff")
    pill(draw, right + 12, 471, VISIBLE_COPY[9], "#2be88a")
    draw.text((64, 577), VISIBLE_COPY[10], font=font("segoeui.ttf", 16), fill="#6fa9d8")

    shadow = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((568, 53, 1250, 600), radius=25, fill=(0, 0, 0, 190))
    shadow = shadow.filter(ImageFilter.GaussianBlur(15))
    canvas.alpha_composite(shadow)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((576, 56, 1242, 592), radius=22, fill="#081525", outline="#2d6a96", width=2)
    draw.ellipse((593, 74, 601, 82), fill="#2bd4ff")
    draw.ellipse((608, 74, 616, 82), fill="#3e6685")
    draw.ellipse((623, 74, 631, 82), fill="#3e6685")
    draw.text((646, 66), "ExplorerTweaks", font=font("seguisb.ttf", 15), fill="#d9e9f8")

    with Image.open(root / "assets/screenshots/01-appearance.png") as source:
        source = source.convert("RGB").crop((285, 0, 1600, 1000))
    rounded_paste(canvas, source, (584, 96, 1234, 590), 13)
    return canvas.convert("RGB")


def comparison(before: Image.Image, after: Image.Image) -> Image.Image:
    board = Image.new("RGB", (1280, 700), "#07111f")
    draw = ImageDraw.Draw(board)
    draw.text((50, 35), "Previous artwork", font=font("seguisb.ttf", 22), fill="#94a8bd")
    draw.text((660, 35), "Selected README hero", font=font("seguisb.ttf", 22), fill="#f6fbff")
    rounded_paste(board, before.convert("RGB"), (50, 78, 620, 363), 12)
    rounded_paste(board, after.convert("RGB"), (660, 78, 1230, 363), 12)
    draw.text((50, 407), "Logo and tagline only", font=font("segoeui.ttf", 19), fill="#94a8bd")
    draw.text((50, 440), "No product proof in the frame", font=font("segoeui.ttf", 19), fill="#94a8bd")
    draw.text((660, 407), "Approved identity and real product capture", font=font("segoeui.ttf", 19), fill="#c8d8ea")
    draw.text((660, 440), "Readable hierarchy at the same 2:1 ratio", font=font("segoeui.ttf", 19), fill="#c8d8ea")
    return board


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--proof-dir", type=Path)
    parser.add_argument("--comparison", type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    artwork = render(ROOT)
    artwork.save(output, format="PNG", optimize=True)
    if args.proof_dir:
        proof_dir = args.proof_dir.resolve()
        proof_dir.mkdir(parents=True, exist_ok=True)
        for width in (960, 640):
            preview = artwork.resize((width, width // 2), Image.Resampling.LANCZOS)
            preview.save(proof_dir / f"readme-width-{width}.png", format="PNG", optimize=True)
    if args.comparison:
        comparison_output = args.comparison.resolve()
        comparison_output.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(ROOT / "assets/marketing/social-card.png") as before:
            comparison(before, artwork).save(comparison_output, format="PNG", optimize=True)
    print(output)


if __name__ == "__main__":
    main()
