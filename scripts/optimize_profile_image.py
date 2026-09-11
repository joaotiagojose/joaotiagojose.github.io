"""Generate the responsive WebP assets from the original portrait.

Run with Python and Pillow installed. The site itself has no build dependency.
"""

from pathlib import Path

from PIL import Image, ImageOps


def main():
    assets = Path(__file__).resolve().parents[1] / "assets"
    source = assets / "joao-jose-profile.png"
    with Image.open(source) as original:
        portrait = ImageOps.exif_transpose(original).convert("RGB")
        if portrait.width != portrait.height:
            raise ValueError("The profile portrait must be square; review its crop first.")

        for width in (100, 150, 200, 300):
            output = assets / f"joao-jose-profile-{width}.webp"
            resized = portrait.resize((width, width), Image.Resampling.LANCZOS)
            resized.save(output, "WEBP", quality=84, method=6)
            reduction = 100 * (1 - output.stat().st_size / source.stat().st_size)
            print(f"{output.name}: {output.stat().st_size:,} bytes ({reduction:.1f}% smaller)")


if __name__ == "__main__":
    main()
