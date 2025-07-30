import json
import logging
import os
from argparse import ArgumentParser
from typing import Literal

from mediacatch.commands import BaseCLICommand
from mediacatch.viz import DetectViz, FaceViz, OCRViz, SpeechViz

logger = logging.getLogger('mediacatch.cli.viz')


def viz_cli_factory(args):
    return VizCLI(
        type=args.type,
        file_path=args.file_path,
        results_path=args.results_path,
        output_path=args.output_path,
        bgr_color=tuple(args.bgr_color) if args.bgr_color else None,
        detect_classes=args.detect_classes,
        detect_min_conf=args.detect_min_conf,
        ocr_max_text_length=args.ocr_max_text_length,
        face_gender=args.face_gender,
        face_age=args.face_age,
        speech_no_subtitles=args.speech_no_subtitles,
        speech_no_meta=args.speech_no_meta,
    )


class VizCLI(BaseCLICommand):
    @staticmethod
    def register_subcommand(parser: ArgumentParser):
        viz_parser: ArgumentParser = parser.add_parser(
            'viz', help='CLI tool to visualize the results of MediaCatch'
        )
        viz_parser.add_argument(
            'type',
            type=str,
            choices=['ocr', 'face', 'detect', 'speech'],
            help='Type of inference to visualize',
        )
        viz_parser.add_argument('file_path', type=str, help='Path to the file to visualize')
        viz_parser.add_argument('results_path', type=str, help='Path to the results json file')
        viz_parser.add_argument(
            'output_path',
            type=str,
            help='Path to save the output visualization',
        )
        viz_parser.add_argument(
            '--bgr-color',
            type=int,
            nargs=3,
            default=None,
            help='BGR color to use for the visualization',
        )

        # Detect specific arguments (must start with --detect-)
        viz_parser.add_argument(
            '--detect-classes',
            type=str,
            nargs='+',
            default=None,
            help='Classes to visualize',
        )
        viz_parser.add_argument(
            '--detect-min-conf',
            type=float,
            default=0.5,
            help='Minimum confidence to consider a detection',
        )

        # OCR specific arguments (must start with --ocr-)
        viz_parser.add_argument(
            '--ocr-max-text-length',
            type=int,
            default=30,
            help='Maximum length of text to display',
        )

        # Face specific arguments (must start with --face-)
        viz_parser.add_argument(
            '--face-gender',
            action='store_true',
            help='Vizualize gender detection results',
        )
        viz_parser.add_argument(
            '--face-age',
            action='store_true',
            help='Vizualize age detection results',
        )

        # Speech specific arguments (must start with --speech-)
        viz_parser.add_argument(
            '--speech-no-subtitles',
            action='store_true',
            help='Do not create subtitles for speech',
        )
        viz_parser.add_argument(
            '--speech-no-meta',
            action='store_true',
            help='Do not create meta subtitles for speech',
        )

        viz_parser.set_defaults(func=viz_cli_factory)

    def __init__(
        self,
        type: Literal['ocr', 'face', 'detect'],
        file_path: str,
        results_path: str,
        output_path: str,
        bgr_color: tuple[int, int, int] | None = None,
        detect_classes: list[str] | None = None,
        detect_min_conf: float = 0.5,
        ocr_max_text_length: int = 30,
        face_gender: bool = False,
        face_age: bool = False,
        speech_no_subtitles: bool = False,
        speech_no_meta: bool = False,
    ) -> None:
        assert os.path.isfile(file_path), f'File not found: {file_path}'
        assert os.path.isfile(results_path), f'Results file not found: {results_path}'

        self.type = type
        self.file_path = file_path
        self.results_path = results_path
        self.output_path = output_path
        self.bgr_color = bgr_color
        self.detect_classes = detect_classes
        self.detect_min_conf = detect_min_conf
        self.ocr_max_text_length = ocr_max_text_length
        self.face_gender = face_gender
        self.face_age = face_age
        self.speech_no_subtitles = speech_no_subtitles
        self.speech_no_meta = speech_no_meta

        with open(results_path, 'r') as f:
            self.results = json.load(f)

    def run(self) -> None:
        if self.type == 'face':
            logger.info('Creating face visualization')
            viz = FaceViz(
                file_path=self.file_path,
                results=self.results,
                output_path=self.output_path,
                gender=self.face_gender,
                age=self.face_age,
            )
        elif self.type == 'detect':
            logger.info('Creating detection visualization')
            viz = DetectViz(
                file_path=self.file_path,
                results=self.results,
                output_path=self.output_path,
                color=self.bgr_color,
                classes=self.detect_classes,
                min_conf=self.detect_min_conf,
            )
        elif self.type == 'ocr':
            logger.info('Creating OCR visualization')
            viz = OCRViz(
                file_path=self.file_path,
                results=self.results,
                output_path=self.output_path,
                max_text_length=self.ocr_max_text_length,
            )
        elif self.type == 'speech':
            logger.info('Creating speech visualization')
            viz = SpeechViz(
                file_path=self.file_path,
                results=self.results,
                output_path=self.output_path,
                subtitles=not self.speech_no_subtitles,
                meta=not self.speech_no_meta,
            )
        else:
            raise NotImplementedError(f'Visualization for {self.type} is not implemented')

        viz.create_viz()
