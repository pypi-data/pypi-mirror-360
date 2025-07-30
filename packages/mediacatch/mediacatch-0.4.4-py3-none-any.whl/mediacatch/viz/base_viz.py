import logging
import os
from abc import ABC, abstractmethod
from typing import Any

import cv2
from PIL import Image
from tqdm.auto import tqdm

from mediacatch.viz.annotator import Annotator

logger = logging.getLogger('mediacatch.viz')


class BaseViz(ABC):
    """Base class for visualization vision results."""

    file_path: str
    results = list[dict[str, Any]]
    output_path: str

    @abstractmethod
    def draw_results(self) -> None:
        raise NotImplementedError()

    def create_viz(self) -> None:
        """Create visualization."""
        assert os.path.isfile(self.file_path), f'File not found: {self.file_path}'
        assert self.results, 'No OCR results found'
        assert self.output_path, 'Output path is not defined'

        fname = os.path.basename(self.file_path)
        cap = cv2.VideoCapture(self.file_path)
        if not cap.isOpened():
            logger.error(f'Failed to open video: {self.file_path}')
            cap.release()
            return None

        num_frames = max(1, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
        input_fps = float(max(1, cap.get(cv2.CAP_PROP_FPS)))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video = cv2.VideoWriter(self.output_path, fourcc, input_fps, (width, height))

        failed_frames = 0
        try:
            for i in tqdm(range(num_frames), desc='Creating video'):
                ret, frame = cap.read()
                if not ret:
                    if failed_frames > 10:
                        logger.error(f'Failed to read frames for {failed_frames} times')
                        break
                    logger.warning(f'Failed to read frame {i} from {fname}')
                    failed_frames += 1
                    continue

                width = frame.shape[1]
                height = frame.shape[0]
                anno = Annotator(Image.fromarray(frame))
                self.draw_results(anno, i, width, height)
                video.write(anno.asarray())

        except KeyboardInterrupt:
            logger.warning('User interrupted the process')

        except Exception as e:
            logger.error(f'An error occurred: {e}')

        finally:
            video.release()
            cap.release()
            logger.info(f'Vizualization is saved to {self.output_path}')
