import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ======================================================
# RACK RENDER ENGINE v3 (mini-CAD style)
# ======================================================

# ================= STYLE =================
COLOR_BG = (236, 239, 243)
COLOR_FRAME = (18, 18, 18)
COLOR_FRAME_INNER = (70, 70, 70)
COLOR_RAIL = (28, 28, 28)
COLOR_RAIL_HOLE = (6, 6, 6)
COLOR_PANEL_BORDER = (22, 22, 22)
COLOR_PANEL_FILL_TOP = (252, 252, 252)
COLOR_PANEL_FILL_BOTTOM = (231, 234, 238)
COLOR_EMPTY_BORDER = (154, 160, 168)
COLOR_EMPTY_FILL = (242, 245, 248)
COLOR_TEXT = (12, 12, 12)
COLOR_DIM = (92, 98, 108)
COLOR_GRID_MINOR = (214, 219, 225)
COLOR_GRID_MAJOR = (188, 194, 202)
COLOR_SHADOW = (0, 0, 0, 86)
COLOR_SCREW = (58, 62, 70)

# ================= GEOMETRY =================
UNIT_HEIGHT = 72
TOP_HEIGHT = 110
BOTTOM_HEIGHT = 100

RACK_WIDTH = 860
SIDE_MARGIN = 140

LABEL_SPLIT = 120
HOLE_SPACING = UNIT_HEIGHT / 3
PANEL_RADIUS = 8


@dataclass
class Device:
    u: int
    label: str
    size: int


# ======================================================
# ASCII PARSER
# ======================================================
def parse_ascii(ascii_text: str) -> List[Device]:
    devices: List[Device] = []

    for raw_line in ascii_text.strip().split("\n"):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        # Format: 12U CORE SWITCH 2U
        m = re.match(r"(\d+)U\s+(.+)", line, flags=re.IGNORECASE)
        if not m:
            continue

        u = int(m.group(1))
        label = m.group(2).strip()

        size = 1
        multi = re.search(r"\b(\d+)U$", label, flags=re.IGNORECASE)
        if multi:
            size = max(1, int(multi.group(1)))
            label = label[: multi.start()].strip()

        devices.append(Device(u=u, label=label, size=size))

    return devices


# ======================================================
# FONTS
# ======================================================
def load_fonts() -> Tuple[ImageFont.ImageFont, ImageFont.ImageFont, ImageFont.ImageFont]:
    try:
        font_u = ImageFont.truetype("DejaVuSans-Bold.ttf", 24)
        font_label = ImageFont.truetype("DejaVuSans.ttf", 24)
        font_dim = ImageFont.truetype("DejaVuSans.ttf", 14)
    except Exception:
        font_u = ImageFont.load_default()
        font_label = ImageFont.load_default()
        font_dim = ImageFont.load_default()

    return font_u, font_label, font_dim


# ======================================================
# UTILITIES
# ======================================================
def draw_text_center(draw: ImageDraw.ImageDraw, box, text: str, font, color):
    x1, y1, x2, y2 = box
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    x = x1 + (x2 - x1 - w) / 2
    y = y1 + (y2 - y1 - h) / 2 - 1
    draw.text((x, y), text, fill=color, font=font)


def load_font_with_size(size: int):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def draw_text_autoscale(draw: ImageDraw.ImageDraw, box, text: str, max_size: int, color):
    x1, _, x2, _ = box
    size = max_size

    while size > 10:
        font = load_font_with_size(size)
        bbox = font.getbbox(text)
        width = bbox[2] - bbox[0]
        if width <= (x2 - x1 - 14):
            break
        size -= 1

    draw_text_center(draw, box, text, font, color)


def vertical_gradient(width: int, height: int, color_top, color_bottom) -> Image.Image:
    grad = Image.new("RGB", (width, height), color_top)
    pix = grad.load()

    for y in range(height):
        t = y / max(1, height - 1)
        r = int(color_top[0] * (1 - t) + color_bottom[0] * t)
        g = int(color_top[1] * (1 - t) + color_bottom[1] * t)
        b = int(color_top[2] * (1 - t) + color_bottom[2] * t)
        for x in range(width):
            pix[x, y] = (r, g, b)

    return grad


# ======================================================
# RACK DRAWING
# ======================================================
def draw_background_grid(draw: ImageDraw.ImageDraw, width: int, height: int):
    step_minor = 24
    step_major = 72

    for x in range(0, width, step_minor):
        color = COLOR_GRID_MAJOR if (x % step_major == 0) else COLOR_GRID_MINOR
        draw.line((x, 0, x, height), fill=color, width=1)

    for y in range(0, height, step_minor):
        color = COLOR_GRID_MAJOR if (y % step_major == 0) else COLOR_GRID_MINOR
        draw.line((0, y, width, y), fill=color, width=1)


def draw_rack_shadow(img: Image.Image):
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(shadow)

    left = SIDE_MARGIN - 26
    right = RACK_WIDTH - SIDE_MARGIN + 26
    top = 20
    bottom = img.height - 24

    d.rounded_rectangle((left + 8, top + 10, right + 8, bottom + 10), radius=12, fill=COLOR_SHADOW)
    shadow = shadow.filter(ImageFilter.GaussianBlur(9))
    img.paste(shadow, (0, 0), shadow)


def draw_rack_frame(draw: ImageDraw.ImageDraw, height: int):
    outer = (SIDE_MARGIN - 26, 20, RACK_WIDTH - SIDE_MARGIN + 26, height - 24)
    inner = (SIDE_MARGIN - 20, 26, RACK_WIDTH - SIDE_MARGIN + 20, height - 30)

    draw.rounded_rectangle(outer, radius=10, outline=COLOR_FRAME, width=4)
    draw.rounded_rectangle(inner, radius=8, outline=COLOR_FRAME_INNER, width=2)


def draw_dimension_marks(draw: ImageDraw.ImageDraw, rack_units: int, font_dim):
    left = SIDE_MARGIN - 70
    start_y = TOP_HEIGHT
    total_h = rack_units * UNIT_HEIGHT

    draw.line((left, start_y, left, start_y + total_h), fill=COLOR_DIM, width=1)
    draw.line((left - 8, start_y, left + 8, start_y), fill=COLOR_DIM, width=1)
    draw.line((left - 8, start_y + total_h, left + 8, start_y + total_h), fill=COLOR_DIM, width=1)

    draw_text_center(draw, (left - 45, start_y + total_h / 2 - 12, left - 5, start_y + total_h / 2 + 12), f"{rack_units}U", font_dim, COLOR_DIM)


def draw_rack_rails(draw: ImageDraw.ImageDraw, rack_units: int):
    holes = rack_units * 3
    rail_left = SIDE_MARGIN - 18
    rail_right = RACK_WIDTH - SIDE_MARGIN + 18
    start_y = TOP_HEIGHT

    draw.line((rail_left, start_y - 6, rail_left, start_y + rack_units * UNIT_HEIGHT + 6), fill=COLOR_RAIL, width=4)
    draw.line((rail_right, start_y - 6, rail_right, start_y + rack_units * UNIT_HEIGHT + 6), fill=COLOR_RAIL, width=4)

    for i in range(holes):
        y = start_y + i * HOLE_SPACING
        draw.ellipse((rail_left - 3, y - 3, rail_left + 3, y + 3), fill=COLOR_RAIL_HOLE)
        draw.ellipse((rail_right - 3, y - 3, rail_right + 3, y + 3), fill=COLOR_RAIL_HOLE)


def draw_panel_base(img: Image.Image, rect):
    x1, y1, x2, y2 = rect
    width = int(x2 - x1)
    height = int(y2 - y1)

    grad = vertical_gradient(width, height, COLOR_PANEL_FILL_TOP, COLOR_PANEL_FILL_BOTTOM)
    mask = Image.new("L", (width, height), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rounded_rectangle((0, 0, width - 1, height - 1), radius=PANEL_RADIUS, fill=255)

    img.paste(grad, (int(x1), int(y1)), mask)


def draw_screws(draw: ImageDraw.ImageDraw, left: int, right: int, y: int, h: int):
    pad_x = 14
    points = [
        (left + pad_x, y + 12),
        (left + pad_x, y + h - 12),
        (right - pad_x, y + 12),
        (right - pad_x, y + h - 12),
    ]

    for sx, sy in points:
        draw.ellipse((sx - 4, sy - 4, sx + 4, sy + 4), fill=COLOR_SCREW)
        draw.line((sx - 2, sy, sx + 2, sy), fill=(185, 188, 196), width=1)


def draw_panel(img: Image.Image, draw: ImageDraw.ImageDraw, y: int, height: int, unit: int, label: str, font_u):
    left = SIDE_MARGIN
    right = RACK_WIDTH - SIDE_MARGIN

    draw_panel_base(img, (left, y, right, y + height))
    draw.rounded_rectangle((left, y, right, y + height), radius=PANEL_RADIUS, outline=COLOR_PANEL_BORDER, width=2)

    draw.line((left + LABEL_SPLIT, y + 2, left + LABEL_SPLIT, y + height - 2), fill=COLOR_PANEL_BORDER, width=2)

    draw_text_center(draw, (left, y, left + LABEL_SPLIT, y + height), f"{unit}U", font_u, COLOR_TEXT)
    draw_text_autoscale(draw, (left + LABEL_SPLIT + 6, y, right - 6, y + height), label.upper(), 25, COLOR_TEXT)

    draw.line((left + 3, y + 3, right - 3, y + 3), fill=(255, 255, 255), width=1)
    draw_screws(draw, left, right, y, height)


def draw_empty(draw: ImageDraw.ImageDraw, y: int, unit: int, font):
    left = SIDE_MARGIN
    right = RACK_WIDTH - SIDE_MARGIN

    draw.rectangle((left, y, right, y + UNIT_HEIGHT), outline=COLOR_EMPTY_BORDER, width=1, fill=COLOR_EMPTY_FILL)
    # CAD-like hatch
    for x in range(left - 40, right + 40, 16):
        draw.line((x, y + UNIT_HEIGHT, x + 24, y), fill=(226, 230, 235), width=1)

    draw_text_center(draw, (left, y, left + LABEL_SPLIT, y + UNIT_HEIGHT), f"{unit}U", font, COLOR_EMPTY_BORDER)


def generate_rack(ascii_text: str, rack_units: int = 15) -> Image.Image:
    devices = parse_ascii(ascii_text)

    width = RACK_WIDTH
    height = TOP_HEIGHT + rack_units * UNIT_HEIGHT + BOTTOM_HEIGHT

    img = Image.new("RGB", (width, height), COLOR_BG)
    draw = ImageDraw.Draw(img)

    draw_background_grid(draw, width, height)
    draw_rack_shadow(img)

    draw = ImageDraw.Draw(img)
    font_u, _, font_dim = load_fonts()

    device_map: Dict[int, Device] = {}
    for d in devices:
        for i in range(d.size):
            device_map[d.u - i] = d

    for u in range(rack_units, 0, -1):
        y = TOP_HEIGHT + (rack_units - u) * UNIT_HEIGHT

        if u in device_map:
            d = device_map[u]
            if d.u != u:
                continue
            draw_panel(img, draw, y, d.size * UNIT_HEIGHT, d.u, d.label, font_u)
        else:
            draw_empty(draw, y, u, font_u)

    draw_rack_rails(draw, rack_units)
    draw_rack_frame(draw, height)
    draw_dimension_marks(draw, rack_units, font_dim)

    return img
