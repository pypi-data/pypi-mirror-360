import logging

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from mediacatch.utils.general import get_assets_data

logger = logging.getLogger('mediacatch.viz.annotator')

dark_colors = {
    (235, 219, 11),
    (243, 243, 243),
    (183, 223, 0),
    (221, 111, 255),
    (0, 237, 204),
    (68, 243, 0),
    (255, 255, 0),
    (179, 255, 1),
    (11, 255, 162),
}
light_colors = {
    (255, 42, 4),
    (79, 68, 255),
    (255, 0, 189),
    (255, 180, 0),
    (186, 0, 221),
    (0, 192, 38),
    (255, 36, 125),
    (104, 0, 123),
    (108, 27, 255),
    (47, 109, 252),
    (104, 31, 17),
}


def get_txt_color(
    color: tuple[int, int, int] = (128, 128, 128),
    txt_color: tuple[int, int, int] = (255, 255, 255),
) -> tuple[int, int, int]:
    if color in dark_colors:
        return (104, 31, 17)
    elif color in light_colors:
        return (255, 255, 255)
    return txt_color


class Annotator:
    def __init__(
        self,
        im: Image.Image | np.ndarray,
        line_width: int | None = 5,
        font_size: int | None = 25,
        font: str = 'Arial.ttf',
        rounded_rectangle_radius: int = 10,
    ) -> None:
        self.im = im if isinstance(im, Image.Image) else Image.fromarray(im)
        self.draw = ImageDraw.Draw(self.im)
        self.line_width = line_width or max(round(sum(im.size) / 2 * 0.006), 2)
        self.rounded_rectangle_radius = rounded_rectangle_radius

        try:
            font = get_assets_data(font)
            font_size = font_size or max(round(sum(im.size) / 2 * 0.035), 12)
            self.font = ImageFont.truetype(font, font_size)
        except Exception:
            self.font = ImageFont.load_default(font_size)

    def bbox_label(
        self,
        bbox: tuple[int, int, int, int],
        label: str | None = None,
        color: tuple[int, int, int] = (236, 56, 131),
        txt_color: tuple[int, int, int] = (255, 255, 255),
        padding: int = 5,
    ) -> None:
        txt_color = get_txt_color(color, txt_color)
        p1 = (bbox[0], bbox[1])
        bbox = (bbox[0] - padding, bbox[1] - padding, bbox[2] + padding, bbox[3] + padding)
        self.draw.rounded_rectangle(
            bbox, width=self.line_width, radius=self.rounded_rectangle_radius, outline=color
        )
        if label:
            if not label[0].isupper():
                label = label.capitalize()
            w = self.font.getlength(label)
            h = self.font.font.height
            outside = p1[1] >= h
            self.draw.rectangle(
                (
                    p1[0],
                    p1[1] - h if outside else p1[1],
                    p1[0] + w + 6,
                    p1[1] + 1 if outside else p1[1] + h + 1,
                ),
                fill=color,
            )
            self.draw.text(
                (p1[0] + 3, p1[1] if outside else p1[1] + h),
                label,
                fill=txt_color,
                font=self.font,
                anchor='ls',
            )

    def asarray(self) -> np.ndarray:
        return np.array(self.im)
