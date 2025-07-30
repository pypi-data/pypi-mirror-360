import logging
import os
from typing import Any

from mediacatch.viz.annotator import Annotator
from mediacatch.viz.base_viz import BaseViz

logger = logging.getLogger('mediacatch.viz.face')


class FaceViz(BaseViz):
    """Class to visualize face detection results."""

    def __init__(
        self,
        file_path: str,
        results: list[dict[str, Any]],
        output_path: str,
        gender: bool = False,
        age: bool = False,
    ) -> None:
        """Initialize FaceViz.

        Args:
            file_path (str): File path.
            results (list[dict[str, Any]]): Results from MediaCatch Vision API.
            output_path (str): Output path.
            gender (bool, optional): Show gender. Defaults to False.
            age (bool, optional): Show age. Defaults to False.
        """
        # TODO: Add support for expression and ethnicity
        assert os.path.isfile(file_path), f'File not found: {file_path}'
        assert results, 'No face detection results found'

        self.file_path = file_path
        self.results = results
        self.results = sorted(self.results, key=lambda x: x['frame'])
        self.output_path = output_path
        self.gender = gender
        self.age = age

    def draw_results(self, anno: Annotator, frame_idx: int, width: int, height: int) -> None:
        for r in self.results:
            frame = r['frame']
            if frame == frame_idx:
                x, y, w, h = r['bbox']
                x1 = x - w / 2.0
                y1 = y - h / 2.0
                x2 = x + w / 2.0
                y2 = y + h / 2.0
                x1 = int(x1 * width)
                y1 = int(y1 * height)
                x2 = int(x2 * width)
                y2 = int(y2 * height)
                label = ''
                if self.gender:
                    label += f' {r["gender"]}'
                if self.age:
                    label += f' {r["age"]} years'
                label = label.strip()
                anno.bbox_label(
                    (x1, y1, x2, y2),
                    label=label if label else None,
                )
