#!/usr/bin/env python3
"""
phone_mockup.py — Hero art phone mockup compositor
Draws a clean iPhone-style frame, composites your screenshot,
applies perspective tilt, drop shadow, and exports a transparent PNG.

Usage:
    python phone_mockup.py <screenshot.png> [options]

Options:
    --angle      flat | tilt | isometric | dramatic  (default: tilt)
    --color      black | white | titanium             (default: black)
    --shadow     soft | hard | none                   (default: soft)
    --output     output filename                       (default: mockup_<angle>.png)
    --scale      float, e.g. 0.5 for half size        (default: 1.0)
    --padding    pixels of transparent padding         (default: 120)

Examples:
    python phone_mockup.py screenshot.png
    python phone_mockup.py screenshot.png --angle isometric --color white
    python phone_mockup.py screenshot.png --angle dramatic --shadow hard
"""

import argparse
import sys
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import numpy as np


# ── Phone frame dimensions (at 1x scale, based on iPhone 16 Pro proportions) ──
FRAME_W = 393
FRAME_H = 852
SCREEN_X = 20
SCREEN_Y = 20
SCREEN_W = 353
SCREEN_H = 812
CORNER_R = 44          # outer frame corner radius
SCREEN_CORNER_R = 36   # screen corner radius
DYNAMIC_ISLAND_W = 120
DYNAMIC_ISLAND_H = 34
BUTTON_W = 6


# ── Color palettes ─────────────────────────────────────────────────────────────
PALETTES = {
    "black": {
        "frame_outer":  (22, 22, 24),
        "frame_inner":  (10, 10, 12),
        "bezel":        (30, 30, 32),
        "button":       (18, 18, 20),
        "island":       (0, 0, 0),
        "edge_light":   (60, 60, 65),
    },
    "white": {
        "frame_outer":  (242, 242, 244),
        "frame_inner":  (225, 225, 228),
        "bezel":        (235, 235, 238),
        "button":       (220, 220, 223),
        "island":       (10, 10, 12),
        "edge_light":   (200, 200, 205),
    },
    "titanium": {
        "frame_outer":  (100, 98, 95),
        "frame_inner":  (80, 78, 75),
        "bezel":        (90, 88, 85),
        "button":       (75, 73, 70),
        "island":       (10, 10, 10),
        "edge_light":   (140, 138, 135),
    },
}


# ── Perspective angle presets ──────────────────────────────────────────────────
# Each preset maps the 4 corners of the image to destination points
# Expressed as fractions of (width, height) relative to a padded canvas

def get_angle_corners(angle: str, w: int, h: int):
    """
    Returns (src_pts, dst_pts) as lists of (x,y) tuples for perspective warp.
    src_pts: corners of the original image (TL, TR, BR, BL)
    dst_pts: where those corners land after the perspective transform
    """
    src = [(0, 0), (w, 0), (w, h), (0, h)]

    if angle == "flat":
        return src, src

    elif angle == "tilt":
        # Subtle 3/4 view — top leans right, slight foreshortening
        skew_x = w * 0.06
        squeeze_top = h * 0.04
        dst = [
            (skew_x,          squeeze_top),
            (w - skew_x * 0.3, 0),
            (w,               h),
            (0,               h - squeeze_top),
        ]
        return src, dst

    elif angle == "isometric":
        # Classic isometric / 45° hero view
        x_offset = w * 0.15
        y_compress = h * 0.12
        dst = [
            (x_offset,        y_compress),
            (w,               0),
            (w - x_offset,    h - y_compress),
            (0,               h),
        ]
        return src, dst

    elif angle == "dramatic":
        # Steep receding perspective — right side far away
        x_vanish = w * 0.25
        y_compress = h * 0.22
        dst = [
            (x_vanish,        y_compress),
            (w,               0),
            (w - x_vanish * 0.5, h - y_compress * 0.5),
            (0,               h),
        ]
        return src, dst

    else:
        raise ValueError(f"Unknown angle: {angle}. Use flat/tilt/isometric/dramatic")


def find_coeffs(src_pts, dst_pts):
    """Solve 8 perspective transform coefficients for PIL."""
    matrix = []
    for (x, y), (X, Y) in zip(src_pts, dst_pts):
        matrix.append([x, y, 1, 0, 0, 0, -X * x, -X * y])
        matrix.append([0, 0, 0, x, y, 1, -Y * x, -Y * y])
    A = np.matrix(matrix, dtype=float)
    B = np.array([X for (_, _), (X, Y) in zip(src_pts, dst_pts)] +
                 [Y for (_, _), (X, Y) in zip(src_pts, dst_pts)])
    # interleave X and Y the way the matrix was built
    b = []
    for (_, _), (X, Y) in zip(src_pts, dst_pts):
        b.append(X)
        b.append(Y)
    b = np.array(b, dtype=float)
    res = np.linalg.solve(A, b)
    return np.array(res).flatten().tolist()


def round_rect_mask(size, radius, color=255):
    """Create a rounded-rectangle mask."""
    w, h = size
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=color)
    return mask


def draw_phone_frame(screenshot: Image.Image, color: str = "black") -> Image.Image:
    """
    Composite screenshot onto a drawn phone frame.
    Returns RGBA image at FRAME_W × FRAME_H.
    """
    pal = PALETTES[color]
    frame = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(frame)

    # ── Outer frame body ──
    d.rounded_rectangle(
        [0, 0, FRAME_W - 1, FRAME_H - 1],
        radius=CORNER_R,
        fill=pal["frame_outer"] + (255,),
    )

    # ── Subtle edge highlight (simulates chamfered edge) ──
    d.rounded_rectangle(
        [1, 1, FRAME_W - 2, FRAME_H - 2],
        radius=CORNER_R - 1,
        outline=pal["edge_light"] + (60,),
        width=1,
    )

    # ── Inner bezel ──
    d.rounded_rectangle(
        [SCREEN_X - 4, SCREEN_Y - 4, SCREEN_X + SCREEN_W + 3, SCREEN_Y + SCREEN_H + 3],
        radius=SCREEN_CORNER_R + 4,
        fill=pal["bezel"] + (255,),
    )

    # ── Screen area: transparent punch-through ──
    screen_mask = round_rect_mask((SCREEN_W, SCREEN_H), SCREEN_CORNER_R)

    # Fit screenshot to screen: scale to max width, align top, crop bottom.
    # This handles full-page / scrolling screenshots without distortion.
    ss = screenshot.convert("RGBA")
    src_w, src_h = ss.size
    scale_factor = SCREEN_W / src_w          # scale so width fills the screen
    scaled_h = int(src_h * scale_factor)
    ss = ss.resize((SCREEN_W, scaled_h), Image.LANCZOS)
    # Crop to screen height from the top (drop whatever runs off the bottom)
    if scaled_h > SCREEN_H:
        ss = ss.crop((0, 0, SCREEN_W, SCREEN_H))
    elif scaled_h < SCREEN_H:
        # Screenshot is shorter than screen — pad the bottom with its bg color
        padded = Image.new("RGBA", (SCREEN_W, SCREEN_H), ss.getpixel((SCREEN_W // 2, scaled_h - 1)))
        padded.paste(ss, (0, 0), ss)
        ss = padded
    screen_layer = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    screen_layer.paste(ss, (SCREEN_X, SCREEN_Y), screen_mask)

    # Composite: frame first, then screen content on top.
    # The frame is drawn as a solid rounded-rect (no transparent screen
    # cutout), so the screen layer must go ON TOP. The dynamic island and
    # buttons are drawn after this composite, on top of the screen content.
    result = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    result = Image.alpha_composite(result, frame)
    result = Image.alpha_composite(result, screen_layer)

    # ── Dynamic Island ──
    di_x = (FRAME_W - DYNAMIC_ISLAND_W) // 2
    di_y = SCREEN_Y + 12
    d2 = ImageDraw.Draw(result)
    d2.rounded_rectangle(
        [di_x, di_y, di_x + DYNAMIC_ISLAND_W, di_y + DYNAMIC_ISLAND_H],
        radius=DYNAMIC_ISLAND_H // 2,
        fill=pal["island"] + (255,),
    )

    # ── Side buttons ──
    # Volume up / down (left side)
    for btn_y in [170, 230]:
        d2.rounded_rectangle(
            [-1, btn_y, BUTTON_W, btn_y + 55],
            radius=3,
            fill=pal["button"] + (255,),
        )
    # Power button (right side)
    d2.rounded_rectangle(
        [FRAME_W - BUTTON_W, 200, FRAME_W + 1, 200 + 75],
        radius=3,
        fill=pal["button"] + (255,),
    )

    # ── Bottom home indicator ──
    ind_w, ind_h = 120, 5
    ind_x = (FRAME_W - ind_w) // 2
    ind_y = FRAME_H - 20
    indicator_color = (180, 180, 180) if color == "white" else (80, 80, 82)
    d2.rounded_rectangle(
        [ind_x, ind_y, ind_x + ind_w, ind_y + ind_h],
        radius=ind_h // 2,
        fill=indicator_color + (200,),
    )

    return result


def add_drop_shadow(img: Image.Image, style: str = "soft", padding: int = 120) -> Image.Image:
    """
    Adds drop shadow below/around the phone. Returns enlarged RGBA image.
    """
    if style == "none":
        # Just add padding
        canvas = Image.new("RGBA", (img.width + padding * 2, img.height + padding * 2), (0, 0, 0, 0))
        canvas.paste(img, (padding, padding), img)
        return canvas

    # Build shadow from alpha channel
    alpha = img.split()[3]
    shadow_color = (0, 0, 0)
    shadow_img = Image.new("RGBA", img.size, shadow_color + (0,))
    shadow_img.putalpha(alpha)

    # Offset and blur settings
    if style == "soft":
        offset_x, offset_y = 0, 30
        blur_radius = 45
        opacity = 0.45
    else:  # hard
        offset_x, offset_y = 8, 16
        blur_radius = 12
        opacity = 0.65

    # Create padded canvas
    W = img.width + padding * 2
    H = img.height + padding * 2

    # Shadow layer
    shadow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sx = padding + offset_x
    sy = padding + offset_y
    shadow_layer.paste(shadow_img, (sx, sy), shadow_img)

    # Extract and scale alpha for opacity
    sr, sg, sb, sa = shadow_layer.split()
    sa_arr = np.array(sa, dtype=float) * opacity
    sa = Image.fromarray(sa_arr.astype(np.uint8))
    shadow_layer = Image.merge("RGBA", (sr, sg, sb, sa))

    # Blur the shadow
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(blur_radius))

    # Compose: shadow first, then phone on top
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    canvas = Image.alpha_composite(canvas, shadow_layer)
    phone_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    phone_layer.paste(img, (padding, padding), img)
    canvas = Image.alpha_composite(canvas, phone_layer)

    return canvas


def apply_perspective(img: Image.Image, angle: str) -> Image.Image:
    """Apply perspective warp for the given angle preset."""
    if angle == "flat":
        return img

    w, h = img.size
    src, dst = get_angle_corners(angle, w, h)

    # PIL transform needs INVERSE coefficients (dst -> src)
    coeffs = find_coeffs(dst, src)

    # Compute output bounding box from dst points
    xs = [p[0] for p in dst]
    ys = [p[1] for p in dst]
    out_w = int(max(xs)) + 1
    out_h = int(max(ys)) + 1

    warped = img.transform(
        (out_w, out_h),
        Image.PERSPECTIVE,
        coeffs,
        Image.BICUBIC,
    )
    return warped


def build_mockup(
    screenshot_path: str,
    angle: str = "tilt",
    color: str = "black",
    shadow: str = "soft",
    scale: float = 1.0,
    padding: int = 120,
    output: str = None,
):
    print(f"  Loading screenshot: {screenshot_path}")
    screenshot = Image.open(screenshot_path)

    print(f"  Drawing phone frame ({color})...")
    phone = draw_phone_frame(screenshot, color=color)

    print(f"  Applying perspective: {angle}...")
    phone = apply_perspective(phone, angle)

    print(f"  Adding drop shadow: {shadow}...")
    result = add_drop_shadow(phone, style=shadow, padding=padding)

    if scale != 1.0:
        new_size = (int(result.width * scale), int(result.height * scale))
        result = result.resize(new_size, Image.LANCZOS)

    if output is None:
        stem = Path(screenshot_path).stem
        output = f"{stem}_mockup_{angle}.png"

    result.save(output, "PNG")
    print(f"  ✓ Saved: {output}  ({result.width}×{result.height}px)")
    return output


# ── CLI ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hero phone mockup compositor")
    parser.add_argument("screenshot", help="Path to your screenshot PNG/JPG")
    parser.add_argument("--angle",   default="tilt",
                        choices=["flat", "tilt", "isometric", "dramatic"],
                        help="Perspective angle preset")
    parser.add_argument("--color",   default="black",
                        choices=["black", "white", "titanium"],
                        help="Phone frame color")
    parser.add_argument("--shadow",  default="soft",
                        choices=["soft", "hard", "none"],
                        help="Drop shadow style")
    parser.add_argument("--scale",   default=1.0, type=float,
                        help="Output scale (e.g. 0.5 = half size)")
    parser.add_argument("--padding", default=120, type=int,
                        help="Transparent padding around mockup in px")
    parser.add_argument("--output",  default=None,
                        help="Output filename (default: <input>_mockup_<angle>.png)")
    parser.add_argument("--all-angles", action="store_true",
                        help="Export all 4 angle presets at once")

    args = parser.parse_args()

    if args.all_angles:
        print(f"\n🎨 Generating all angle variants for: {args.screenshot}\n")
        for ang in ["flat", "tilt", "isometric", "dramatic"]:
            stem = Path(args.screenshot).stem
            out = f"{stem}_mockup_{ang}.png"
            build_mockup(
                args.screenshot,
                angle=ang,
                color=args.color,
                shadow=args.shadow,
                scale=args.scale,
                padding=args.padding,
                output=out,
            )
        print("\n✅ All variants exported.")
    else:
        print(f"\n🎨 Building mockup: {args.screenshot}\n")
        build_mockup(
            args.screenshot,
            angle=args.angle,
            color=args.color,
            shadow=args.shadow,
            scale=args.scale,
            padding=args.padding,
            output=args.output,
        )
        print("\n✅ Done.")
