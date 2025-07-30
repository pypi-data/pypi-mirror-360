import logging
import os
from typing import Any

import numpy as np

from mediacatch.viz.annotator import Annotator
from mediacatch.viz.base_viz import BaseViz

logger = logging.getLogger('mediacatch.viz.detect')


def color_gradient(
    start_color: tuple[int, int, int], end_color: tuple[int, int, int], steps: int
) -> list:
    """Create a color gradient.

    Args:
        start_color (tuple[int, int, int]): Start color (r, g, b).
        end_color (tuple[int, int, int]): End color (r, g, b).
        steps (int): Number of steps.

    Returns:
        list: List of colors (r, g, b).
    """
    start = np.array(start_color)
    end = np.array(end_color)
    colors = [start + (end - start) * i / (steps - 1) for i in range(steps)]
    return [(int(r), int(g), int(b)) for r, g, b in colors]


class DetectViz(BaseViz):
    """Class to visualize detection results."""

    _color1 = (101, 16, 50)
    _color2 = (250, 139, 172)

    def __init__(
        self,
        file_path: str,
        results: list[dict[str, Any]],
        output_path: str,
        color: tuple[int, int, int] | None = None,
        min_conf: float = 0.5,
        classes: list[str] = None,
    ) -> None:
        """Initialize DetectViz.

        Args:
            file_path (str): Path to file.
            results (list[dict[str, Any]]): Results from Medicatch Vision API.
            output_path (str): Output path.
            color (tuple[int, int, int] | None, optional): Set a fixed color for all bounding boxes (r, g, b). Defaults to None.
            min_conf (float, optional): Minium confidence threshold. Defaults to 0.5.
            classes (list[str], optional): List of classes to overwrite model classes labels. Defaults to None.
        """
        assert os.path.isfile(file_path), f'File not found: {file_path}'
        assert results, 'No detections results found'

        self.file_path = file_path
        self.results = results
        self.results = sorted(self.results, key=lambda x: x['frame'])
        self.output_path = output_path
        self.color = color
        self.min_conf = min_conf
        self.classes = classes

        if not self.classes:
            self.classes = list(set(r['label'] for r in self.results))

        self.colors = (
            [(236, 56, 131)]
            if len(self.classes) == 1
            else color_gradient(self._color1, self._color2, len(self.classes))
        )

    def draw_results(self, anno: Annotator, frame_idx: int, width: int, height: int) -> None:
        for r in self.results:
            frame = r['frame']
            conf = r['conf']
            label: str = r['label']
            if frame == frame_idx and conf > self.min_conf and label in self.classes:
                x1, y1, x2, y2 = r['bbox']
                x1 = int(x1 * width)
                y1 = int(y1 * height)
                x2 = int(x2 * width)
                y2 = int(y2 * height)
                bbox = [x1, y1, x2, y2]
                color = self.colors[self.classes.index(label)]
                # Convert redbull labels and colors
                if label == 'rb_at':
                    label = 'AlphaTauri'
                    color = (236, 56, 131)
                elif label == 'rb_wfl':
                    label = 'Wings for Life'
                    color = (236, 56, 131)
                elif label.startswith('rb_'):
                    label = 'Red Bull'
                    color = (236, 56, 131)
                elif label == 'danske_spil_oddset':
                    label = 'Oddset'
                else:
                    label = label.replace('_', ' ').title()
                if self.color:
                    color = self.color
                anno.bbox_label(
                    bbox,
                    label=label,
                    color=color,
                )
