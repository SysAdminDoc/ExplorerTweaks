#!/usr/bin/env python3
"""Export the approved folder-controls master without redrawing the artwork."""
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    raise SystemExit("Pillow is required. Run: python -m pip install --requirement requirements.txt")

ROOT = Path(__file__).resolve().parent
MASTER = ROOT / "assets/brand/explorertweaks-mark-master.png"
SIZES = (16, 24, 32, 48, 64, 96, 128, 256, 512, 1024)


def create_icon():
    """Create PNG sizes and a multi-resolution Windows icon from the selected source."""
    with Image.open(MASTER) as source:
        if source.mode != "RGBA" or source.getextrema()[3][0] != 0:
            raise ValueError("The approved master must retain its transparent alpha channel.")
        mark = source.crop(source.getchannel("A").getbbox())
        canvas = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
        mark.thumbnail((896, 896), Image.Resampling.LANCZOS)
        canvas.alpha_composite(mark, ((1024 - mark.width) // 2, (1024 - mark.height) // 2))
    output = ROOT / "branding"
    output.mkdir(exist_ok=True)
    for size in SIZES:
        canvas.resize((size, size), Image.Resampling.LANCZOS).save(output / f"icon-{size}.png")
    target = output / "icon.ico"
    canvas.save(target, sizes=[(size, size) for size in SIZES if size <= 256])
    print(f"Exported approved artwork: {target}")
    return target


if __name__ == "__main__":
    create_icon()
