import json
import logging
from argparse import ArgumentParser
from pathlib import Path
from pprint import pprint

from mediacatch.commands import BaseCLICommand
from mediacatch.speech import upload, wait_for_result

logger = logging.getLogger('mediacatch.cli.speech')


def speech_cli_factory(args):
    return SpeechCLI(
        file_path=args.file_path,
        save_result=args.save_result,
        qouta=args.quota,
        fallback_language=args.fallback_language,
        only_upload=args.only_upload,
        url=args.url,
        max_threads=args.max_threads,
        max_request_retries=args.max_request_retries,
        request_delay=args.request_delay,
        chunk_size=args.chunk_size,
        compress_input=args.compress_input,
        sample_rate=args.sample_rate,
        get_result_timeout=args.get_result_timeout,
        get_result_delay=args.get_result_delay,
    )


class SpeechCLI(BaseCLICommand):
    @staticmethod
    def register_subcommand(parser: ArgumentParser):
        speech_parser: ArgumentParser = parser.add_parser(
            'speech', help='CLI tool to run inference with MediaCatch Speech API'
        )

        speech_parser.add_argument(
            'file_path', type=str, help='Path to the file to run inference on'
        )
        speech_parser.add_argument(
            '--save-result',
            type=str,
            default=None,
            help='Save result to a file',
        )
        speech_parser.add_argument(
            '--quota',
            type=str,
            default=None,
            help='Quota for the speech recognition',
        )
        speech_parser.add_argument(
            '--fallback-language',
            type=str,
            default=None,
            help='Fallback language for the speech recognition',
        )
        speech_parser.add_argument(
            '--only-upload',
            action='store_true',
            help='Only upload the file to MediaCatch Speech API',
        )
        speech_parser.add_argument(
            '--url',
            type=str,
            default='https://s2t.mediacatch.io/api/v2',
            help='URL to the MediaCatch Speech API',
        )
        speech_parser.add_argument(
            '--max-threads',
            type=int,
            default=5,
            help='Maximum number of threads to use for uploading and waiting for result',
        )
        speech_parser.add_argument(
            '--max-request-retries',
            type=int,
            default=3,
            help='Maximum number of retries for requests to the API',
        )
        speech_parser.add_argument(
            '--request-delay',
            type=float,
            default=1.0,
            help='Delay between requests to the API',
        )
        speech_parser.add_argument(
            '--chunk-size',
            type=int,
            default=100 * 1024 * 1024,
            help='Chunk size for uploading the file to the API',
        )
        speech_parser.add_argument(
            '--compress-input',
            action='store_true',
            help='Compress the input file to OGG format (requires FFMPEG >= 6.1)',
        )
        speech_parser.add_argument(
            '--sample-rate',
            type=int,
            default=16000,
            help='Sample rate of the audio file (only used if compress-input is set)',
        )
        speech_parser.add_argument(
            '--get-result-timeout',
            type=int,
            default=3600,
            help='Timeout for waiting for the result in seconds',
        )
        speech_parser.add_argument(
            '--get-result-delay',
            type=float,
            default=10.0,
            help='Delay between requests to get the result',
        )

        speech_parser.set_defaults(func=speech_cli_factory)

    def __init__(
        self,
        file_path: str,
        save_result: str | None = None,
        qouta: str | None = None,
        fallback_language: str | None = None,
        only_upload: bool = False,
        url: str = 'https://s2t.mediacatch.io/api/v2',
        max_threads: int = 5,
        max_request_retries: int = 3,
        request_delay: float = 1.0,
        chunk_size: int = 100 * 1024 * 1024,
        compress_input: bool = False,
        sample_rate: int = 16000,
        get_result_timeout: int = 3600,
        get_result_delay: float = 10.0,
    ) -> None:
        self.file_path = file_path
        self.save_result = save_result
        self.qouta = qouta
        self.fallback_language = fallback_language
        self.only_upload = only_upload
        self.url = url
        self.max_threads = max_threads
        self.max_request_retries = max_request_retries
        self.request_delay = request_delay
        self.chunk_size = chunk_size
        self.compress_input = compress_input
        self.sample_rate = sample_rate
        self.get_result_timeout = get_result_timeout
        self.get_result_delay = get_result_delay

    def run(self) -> None:
        # Upload file to MediaCatch Speech API
        file_id = upload(
            self.file_path,
            quota=self.qouta,
            fallback_language=self.fallback_language,
            max_threads=self.max_threads,
            max_request_retries=self.max_request_retries,
            request_delay=self.request_delay,
            chunk_size=self.chunk_size,
            url=self.url,
            compress_input=self.compress_input,
            sample_rate=self.sample_rate,
        )

        if self.only_upload:
            result_url = f'{self.url}/result/{file_id}'
            logger.info(f'File uploaded with ID {file_id}, get result at {result_url}')
            return

        # Wait for result
        result = wait_for_result(
            file_id, url=self.url, timeout=self.get_result_timeout, delay=self.get_result_delay
        )
        if not result:
            logger.error(f'Failed to get result for file {self.file_path}')
            return

        logger.info('Result:')
        pprint(result)

        # Save result to file
        if self.save_result:
            Path(self.save_result).write_text(json.dumps(result, indent=4, ensure_ascii=False, default=str))
            logger.info(f'Result saved to {self.save_result}')
