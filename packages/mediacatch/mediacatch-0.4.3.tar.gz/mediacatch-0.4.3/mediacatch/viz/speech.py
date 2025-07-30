import logging
import subprocess
from datetime import timedelta
from pathlib import Path
from typing import Any

from srt import Subtitle, compose
from tqdm.auto import tqdm

logger = logging.getLogger('mediacatch.viz.speech')


class SpeechViz:
    """Class to visualize speech results."""

    def __init__(
        self,
        file_path: str | Path,
        results: dict[str, Any],
        output_path: str | Path,
        subtitles: bool = True,
        meta: bool = True,
        max_subtitle_length: int = 10,
        max_chars_in_subtitle: int = 100,
    ) -> None:
        """Visualize speech results.

        Args:
            file_path (str | Path): Path to file.
            results (dict[str, Any]): Results from speech API.
            output_path (str | Path): Output path.
            subtitles (bool, optional): If true, add subtitles. Defaults to True.
            meta (bool, optional): If true, add meta data. Defaults to True.
            max_subtitle_length (int, optional): Maximum length of subtitle. Defaults to 10.
            max_chars_in_subtitle (int, optional): Maximum characters in subtitle. Defaults to 100.
        """
        if not isinstance(file_path, Path):
            file_path = Path(file_path)

        if not isinstance(output_path, Path):
            output_path = Path(output_path)

        assert file_path.is_file(), f'File not found: {file_path}'
        assert results

        self.file_path = file_path
        self.results = results
        self.output_path = output_path
        self.subtitles = subtitles
        self.meta = meta
        self.max_subtitle_length = max_subtitle_length
        self.max_chars_in_subtitle = max_chars_in_subtitle

    def create_viz(self) -> None:
        """Create visualization."""
        utterances = self.results['result']['utterances']

        text_srt_file = None
        if self.subtitles:
            text_subtitles = self.create_text_subtitle(utterances)
            text_srt_file = self.write_srt_file(self.output_path, '.text.srt', text_subtitles)

        meta_srt_file = None
        if self.meta:
            meta_subtitles = self.create_meta_subtitle(utterances)
            meta_srt_file = self.write_srt_file(self.output_path, '.meta.srt', meta_subtitles)

        self.burn_subtitles(text_srt_file, meta_srt_file)

    def create_text_subtitle(self, utterances: list[dict[str, Any]]) -> str:
        """Create text subtitles.

        Args:
            utterances (list[dict[str, Any]]): Utterances for speech results.

        Returns:
            str: Subtitles in SRT format.
        """
        subtitles = []
        current_subtitle = []
        sub_start = 0
        sub_end = 0
        for utterance in tqdm(utterances, desc='Creating text subtitles'):
            for word_data in utterance.get('words', []):
                word = word_data.get('word', '')
                i_start = word_data.get('start', 0)
                i_end = word_data.get('end', 0)

                if not current_subtitle:
                    sub_start = i_start

                current_subtitle.append(word)
                sub_end = i_end

                if self._should_end_subtitle(current_subtitle, sub_start, sub_end, word):
                    subtitles.append((' '.join(current_subtitle), sub_start, sub_end))
                    current_subtitle = []

        if current_subtitle:
            subtitles.append((' '.join(current_subtitle), sub_start, sub_end))

        return compose(
            [
                Subtitle(
                    index=i,
                    start=timedelta(seconds=start),
                    end=timedelta(seconds=end),
                    content=text,
                )
                for i, (text, start, end) in enumerate(subtitles)
            ]
        )

    def _should_end_subtitle(
        self, words: list[str], start: float, end: float, last_word: str
    ) -> bool:
        """Check if subtitle should end.

        Args:
            words (list[str]): List of words in subtitle.
            start (float): Start time of subtitle.
            end (float): End time of subtitle.
            last_word (str): Last word in subtitle.

        Returns:
            bool: True if subtitle should end else False.
        """
        return (
            end - start >= self.max_subtitle_length
            or len(' '.join(words)) >= self.max_chars_in_subtitle
            or last_word[-1] in ['.', '!', '?']
        )

    def create_meta_subtitle(self, utterances: list[dict[str, Any]]) -> str:
        """Create meta subtitles.

        Args:
            utterances (list[dict[str, Any]]): Utterances for speech results.

        Returns:
            str: Subtitles in SRT format.
        """
        subs = []
        for i, utterance in tqdm(enumerate(utterances), desc='Creating meta subtitles'):
            meta = utterance.get('meta', {})
            if not meta:
                continue

            sub_parts = [meta.get('speaker', 'Unknown').capitalize()]

            for attribute in ['language', 'gender']:
                attr_data = meta.get(attribute, {})
                if attr_data:
                    label = attr_data.get('label')
                    confidence = attr_data.get('confidence')
                    if label:
                        sub_parts.append(f'{label.capitalize()}')
                    if confidence:
                        sub_parts.append(f'{confidence * 100:.02f}%')

            sub = '\t\t'.join(sub_parts)

            start_second = utterance.get('start')
            end_second = utterance.get('end')
            if start_second is not None and end_second is not None:
                subs.append(
                    Subtitle(
                        index=i,
                        start=timedelta(seconds=start_second),
                        end=timedelta(seconds=end_second),
                        content=sub,
                    )
                )

        return compose(subs)

    @staticmethod
    def write_srt_file(input_path: str, output_suffix: str, subtitles: str) -> Path:
        """Write subtitles to file as SRT.

        Args:
            input_path (str): Input path.
            output_suffix (str): Output suffix.
            subtitles (str): Subtitles in SRT format.

        Returns:
            Path: Output path.
        """
        output_path = Path(input_path).with_suffix(output_suffix)
        output_path.write_text(subtitles)
        return output_path

    def burn_subtitles(
        self, text_srt_file: Path | None, meta_srt_file: Path | None, stream: bool = False
    ) -> None:
        """Burn subtitles to video.

        Args:
            text_srt_file (Path | None): Subtitles in SRT format.
            meta_srt_file (Path | None): Meta data in SRT format.
            stream (bool, optional): Set text style to stream. Defaults to False.
        """
        logger.info(f'Burning subtitles to {self.output_path}')

        text_style = "'BackColour=&H40000000,BorderStyle=4'" + (',Alignment=1' if stream else '')
        meta_style = "'Alignment=6,BackColour=&H40000000,BorderStyle=4'"

        ffmpeg_commands = []

        if text_srt_file and meta_srt_file:
            tmp_file = self.output_path.with_name('tmp.mkv')
            ffmpeg_commands = [
                self._create_ffmpeg_command(self.file_path, tmp_file, text_srt_file, text_style),
                self._create_ffmpeg_command(tmp_file, self.output_path, meta_srt_file, meta_style),
            ]
        elif text_srt_file:
            ffmpeg_commands = [
                self._create_ffmpeg_command(
                    self.file_path, self.output_path, text_srt_file, text_style
                )
            ]
        elif meta_srt_file:
            ffmpeg_commands = [
                self._create_ffmpeg_command(
                    self.file_path, self.output_path, meta_srt_file, text_style
                )
            ]

        for command in ffmpeg_commands:
            subprocess.run(command, shell=True, check=True)

        if len(ffmpeg_commands) > 1:
            tmp_file.unlink()

    def _create_ffmpeg_command(
        self, input_file: Path, output_file: Path, srt_file: Path, style: str
    ) -> str:
        """Create ffmpeg command.

        Args:
            input_file (Path): Input file.
            output_file (Path): Output file.
            srt_file (Path): SRT file.
            style (str): Style for subtitles.

        Returns:
            str: ffmpeg command.
        """
        return f'ffmpeg -hide_banner -loglevel error -stats -i {input_file} -vf "subtitles={srt_file}:force_style={style}" {output_file}'
