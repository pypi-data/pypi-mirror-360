import logging
import os
from typing import Any

from mediacatch.viz.annotator import Annotator
from mediacatch.viz.base_viz import BaseViz

logger = logging.getLogger('mediacatch.viz.ocr')


class OCRViz(BaseViz):
    """Class to visualize OCR results."""

    def __init__(
        self,
        file_path: str,
        results: list[dict[str, Any]],
        output_path: str,
        max_text_length: int = 30,
        avg_char_width: int = 10,
        min_chars: int = 3,
    ) -> None:
        """Initialize OCRViz.

        Args:
            file_path (str): File path.
            results (list[dict[str, Any]]): Results from OCR API.
            output_path (str): Output path.
            max_text_length (int, optional): Max text length to show (will add ... at the end). Defaults to 30.
            avg_char_width (int, optional): Average character. Defaults to 10.
            min_chars (int, optional): Minimum characters to alway show. Defaults to 3.
        """
        assert os.path.isfile(file_path), f'File not found: {file_path}'
        assert results, 'No OCR results found'
        assert max_text_length > 0, 'max_text_length must be greater than 0'

        self.file_path = file_path
        self.results = results
        self.results = sorted(self.results, key=lambda x: x['start_frame_idx'])
        self.output_path = output_path
        self.max_text_length = max_text_length
        self.avg_char_width = avg_char_width
        self.min_chars = min_chars

    def draw_results(self, anno: Annotator, frame_idx: int, width: int, height: int) -> None:
        for r in self.results:
            start_frame = r['start_frame_idx']
            end_frame = r['end_frame_idx']

            if start_frame <= frame_idx <= end_frame:
                x, y, w, h = r['bbox']
                bbox = [x, y, x + w, y + h]
                text = r['text']
                max_chars = max(self.min_chars, w // self.avg_char_width)
                text = text if len(text) <= max_chars else text[:max_chars] + '...'
                anno.bbox_label(
                    bbox,
                    label=text,
                )
