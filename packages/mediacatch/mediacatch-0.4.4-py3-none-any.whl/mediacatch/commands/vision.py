import json
import logging
from argparse import ArgumentParser
from pathlib import Path
from pprint import pprint

from mediacatch.commands import BaseCLICommand
from mediacatch.vision import upload, wait_for_result

logger = logging.getLogger('mediacatch.cli.vision')


def vision_cli_factory(args):
    # Handle store_true arguments
    args.get_detection_histogram = True if args.get_detection_histogram else None
    args.face_recognition = False if args.no_face_recognition else None
    args.face_age = False if args.no_face_age else None
    args.face_gender = False if args.no_face_gender else None
    args.face_expression = False if args.no_face_expression else None
    args.face_ethnicity = False if args.no_face_ethnicity else None

    return VisionCLI(
        file_path=args.file_path,
        type=args.type,
        save_result=args.save_result,
        fps=args.fps,
        tolerance=args.tolerance,
        min_levensthein_ratio=args.min_levensthein_ratio,
        min_bbox_iou=args.min_bbox_iou,
        min_text_confidence=args.min_text_confidence,
        max_text_confidence=args.max_text_confidence,
        max_text_length=args.max_text_length,
        moving_text_threshold=args.moving_text_threshold,
        max_height_width_ratio=args.max_height_width_ratio,
        get_detection_histogram=args.get_detection_histogram,
        detection_histogram_bins=args.detection_histogram_bins,
        max_height_difference_ratio=args.max_height_difference_ratio,
        max_horizontal_distance_ratio=args.max_horizontal_distance_ratio,
        only_upload=args.only_upload,
        face_recognition=args.face_recognition,
        face_age=args.face_age,
        face_gender=args.face_gender,
        face_expression=args.face_expression,
        face_ethnicity=args.face_ethnicity,
    )


class VisionCLI(BaseCLICommand):
    @staticmethod
    def register_subcommand(parser: ArgumentParser):
        vision_parser: ArgumentParser = parser.add_parser(
            'vision', help='CLI tool to run inference with MediaCatch Vision API'
        )
        vision_parser.add_argument(
            'type',
            type=str,
            choices=['ocr', 'face'],
            help='Type of inference to run on the file',
        )
        vision_parser.add_argument(
            'file_path', type=str, help='Path to the file to run inference on'
        )
        vision_parser.add_argument(
            '--save-result',
            type=str,
            default=None,
            help='Save result to a file',
        )
        vision_parser.add_argument(
            '--fps',
            type=int,
            default=None,
            help='FPS for the OCR results',
        )
        vision_parser.add_argument(
            '--tolerance',
            type=int,
            default=None,
            help='Tolerance in seconds for merging text detection for OCR',
        )
        vision_parser.add_argument(
            '--min-levensthein-ratio',
            type=float,
            default=None,
            help='Minimum Levenshtein ratio for merging text detection for OCR (more info here: https://rapidfuzz.github.io/Levenshtein/levenshtein.html#ratio)',
        )
        vision_parser.add_argument(
            '--min-bbox-iou',
            type=float,
            default=None,
            help='Minimum bounding box intersection over union for merging text detection for OCR',
        )
        vision_parser.add_argument(
            '--max-text-length',
            type=int,
            default=None,
            help='If text length is less than this value, use max_text_confidence as confidence threshold for OCR',
        )
        vision_parser.add_argument(
            '--min-text-confidence',
            type=float,
            default=None,
            help='Confidence threshold for text detection for OCR (if text length is greater than max_text_length)',
        )
        vision_parser.add_argument(
            '--max-text-confidence',
            type=float,
            default=None,
            help='Confidence threshold for text detection for OCR (if text length is less than max_text_length)',
        )
        vision_parser.add_argument(
            '--moving-text-threshold',
            type=int,
            default=None,
            help='If merged text detections center moves more pixels than this threshold, it will be considered moving text for OCR',
        )
        vision_parser.add_argument(
            '--max-height-width-ratio',
            type=float,
            default=None,
            help='Discard detection if height/width ratio is greater than this value',
        )
        vision_parser.add_argument(
            '--get-detection-histogram',
            action='store_true',
            help='Calculate histogram for detection',
        )
        vision_parser.add_argument(
            '--detection-histogram-bins',
            type=int,
            default=None,
            help='Number of bins for histogram calculation',
        )
        vision_parser.add_argument(
            '--max-height-difference-ratio',
            type=float,
            default=None,
            help='Determine the maximum allowed difference in height between two text boxes for them to be merged',
        )
        vision_parser.add_argument(
            '--max-horizontal-distance-ratio',
            type=float,
            default=None,
            help='Determine if two boxes are close enough horizontally to be considered part of the same text line',
        )
        vision_parser.add_argument(
            '--only-upload',
            action='store_true',
            help='Only upload the file to MediaCatch Vision API',
        )
        vision_parser.add_argument(
            '--no-face-recognition',
            action='store_true',
            help='Do not run face recognition',
        )
        vision_parser.add_argument(
            '--no-face-age',
            action='store_true',
            help='Do not run face age detection',
        )
        vision_parser.add_argument(
            '--no-face-gender',
            action='store_true',
            help='Do not run face gender detection',
        )
        vision_parser.add_argument(
            '--no-face-expression',
            action='store_true',
            help='Do not run face expression detection',
        )
        vision_parser.add_argument(
            '--no-face-ethnicity',
            action='store_true',
            help='Do not run face ethnicity detection',
        )
        vision_parser.set_defaults(func=vision_cli_factory)

    def __init__(
        self,
        file_path: str,
        type: str,
        save_result: str | None = None,
        fps: int | None = None,
        tolerance: int | None = None,
        min_levensthein_ratio: float | None = None,
        min_bbox_iou: float | None = None,
        min_text_confidence: float | None = None,
        max_text_confidence: float | None = None,
        max_text_length: int | None = None,
        moving_text_threshold: int | None = None,
        max_height_width_ratio: float | None = None,
        get_detection_histogram: bool | None = None,
        detection_histogram_bins: int | None = None,
        max_height_difference_ratio: float | None = None,
        max_horizontal_distance_ratio: float | None = None,
        only_upload: bool = False,
        face_recognition: bool | None = None,
        face_age: bool | None = None,
        face_gender: bool | None = None,
        face_expression: bool | None = None,
        face_ethnicity: bool | None = None,
    ) -> None:
        self.file_path = file_path
        self.type = type
        self.save_result = save_result
        self.fps = fps
        self.tolerance = tolerance
        self.min_levensthein_ratio = min_levensthein_ratio
        self.min_bbox_iou = min_bbox_iou
        self.min_text_confidence = min_text_confidence
        self.max_text_confidence = max_text_confidence
        self.max_text_length = max_text_length
        self.moving_text_threshold = moving_text_threshold
        self.max_height_width_ratio = max_height_width_ratio
        self.get_detection_histogram = get_detection_histogram
        self.detection_histogram_bins = detection_histogram_bins
        self.max_height_difference_ratio = max_height_difference_ratio
        self.max_horizontal_distance_ratio = max_horizontal_distance_ratio
        self.only_upload = only_upload
        self.face_recognition = face_recognition
        self.face_age = face_age
        self.face_gender = face_gender
        self.face_expression = face_expression
        self.face_ethnicity = face_ethnicity

    def run(self) -> None:
        # Upload file to MediaCatch Vision API
        file_id = upload(
            self.file_path,
            self.type,
            fps=self.fps,
            tolerance=self.tolerance,
            min_bbox_iou=self.min_bbox_iou,
            min_levenshtein_ratio=self.min_levensthein_ratio,
            moving_threshold=self.moving_text_threshold,
            max_text_length=self.max_text_length,
            min_text_confidence=self.min_text_confidence,
            max_text_confidence=self.max_text_confidence,
            max_height_width_ratio=self.max_height_width_ratio,
            get_detection_histogram=self.get_detection_histogram,
            detection_histogram_bins=self.detection_histogram_bins,
            max_height_difference_ratio=self.max_height_difference_ratio,
            max_horizontal_distance_ratio=self.max_horizontal_distance_ratio,
            face_recognition=self.face_recognition,
            face_age=self.face_age,
            face_gender=self.face_gender,
            face_expression=self.face_expression,
            face_ethnicity=self.face_ethnicity,
        )
        if self.only_upload:
            logger.info(f'Find result at https://api.mediacatch.io/vision/result/{file_id}')
            return

        # Wait for result
        result = wait_for_result(file_id)
        if not result:
            logger.error('Failed to get result from MediaCatch Vision API')
            return

        logger.info('Results:')
        pprint(result)

        # Save result to a file
        if self.save_result:
            Path(self.save_result).write_text(
                json.dumps(result, indent=4, ensure_ascii=False, default=str)
            )
            logger.info(f'Result saved to {self.save_result}')
