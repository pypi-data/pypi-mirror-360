import json
import logging
import os
import time
from typing import Literal

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from mediacatch.utils import MediacatchUploadError

logger = logging.getLogger('mediacatch.vision.upload')


def upload(
    fpath: str,
    type: Literal['ocr', 'face'],
    url: str = 'https://api.mediacatch.io/vision',
    api_key: str | None = None,
    fps: int | None = None,
    tolerance: int | None = None,
    min_bbox_iou: float | None = None,
    min_levenshtein_ratio: float | None = None,
    moving_threshold: int | None = None,
    max_text_length: int | None = None,
    min_text_confidence: float | None = None,
    max_text_confidence: float | None = None,
    max_height_width_ratio: float | None = None,
    get_detection_histogram: bool | None = None,
    detection_histogram_bins: int | None = None,
    max_height_difference_ratio: float | None = None,
    max_horizontal_distance_ratio: float | None = None,
    get_frame_index: bool | None = None,
    get_bbox: bool | None = None,
    face_recognition: bool | None = None,
    face_age: bool | None = None,
    face_gender: bool | None = None,
    face_expression: bool | None = None,
    face_ethnicity: bool | None = None,
    max_retries: int = 5,
    delay: float = 10.0,
    verbose: bool = True,
) -> str:
    """Upload a file to MediaCatch Vision API.

    Args:
        fpath (str): File path.
        type (Literal['ocr', 'face']): Type of inference to run on the file.
        url (str, optional): URL to the vision API. Defaults to 'https://api.mediacatch.io/vision'.
        api_key (str, optional): API key for the vision API. Defaults to None.
        fps (int, optional): Frames per second for video processing. Defaults to 1.
        tolerance (int, optional): Tolerance for text detection. Defaults to 10.
        min_bbox_iou (float, optional): Minimum bounding box intersection over union for merging text detection. Defaults to 0.5.
        min_levenshtein_ratio (float, optional): Minimum Levenshtein ratio for merging text detection (more info here: https://rapidfuzz.github.io/Levenshtein/levenshtein.html#ratio). Defaults to 0.75.
        moving_threshold (int, optional): If merged text detections center moves more pixels than this threshold, it will be considered moving text. Defaults to 50.
        max_text_length (int, optional): If text length is less than this value, use max_text_confidence as confidence threshold. Defaults to 3.
        min_text_confidence (float, optional): Confidence threshold for text detection (if text length is greater than max_text_length). Defaults to 0.5.
        max_text_confidence (float, optional): Confidence threshold for text detection (if text length is less than max_text_length). Defaults to 0.8.
        max_height_width_ratio (float, optional): Discard detection if height/width ratio is greater than this value. Defaults to 2.0.
        get_detection_histogram (bool, optional): If true, get histogram of detection. Defaults to False.
        detection_histogram_bins (int, optional): Number of bins for histogram calculation. Defaults to 8.
        max_height_difference_ratio (float, optional): Determine the maximum allowed difference in height between two text boxes for them to be merged. Defaults to 0.5.
        max_horizontal_distance_ratio (float, optional): Determine if two boxes are close enough horizontally to be considered part of the same text line. Defaults to 0.9.
        get_frame_index (bool, optional): If true, get frame index. Defaults to None.
        get_bbox (bool, optional): If true, get bounding box. Defaults to None.
        face_recognition (bool, optional): If true, run face recognition. Defaults to None.
        face_age (bool, optional): If true, get face age. Defaults to None.
        face_gender (bool, optional): If true, get face gender. Defaults to None.
        face_expression (bool, optional): If true, get face expression. Defaults to None.
        face_ethnicity (bool, optional): If true, get face ethnicity. Defaults to None.
        max_retries (int, optional): Maximum number of retries. Defaults to 5.
        delay (float, optional): Delay between retries. Defaults to 10.0.
        verbose (bool, optional): If True, print log messages. Defaults to True.

    Returns:
        str: File ID.
    """
    if verbose:
        logger.info(f'Uploading file {fpath} to MediaCatch Vision API')

    # Create headers with API key
    _api_key = api_key or os.getenv('MEDIACATCH_API_KEY')
    if not _api_key:
        raise MediacatchUploadError('API key is required')

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'X-API-KEY': _api_key,
    }

    extra = {}
    if fps is not None:
        extra['fps'] = fps
    if tolerance is not None:
        extra['tolerance'] = tolerance
    if min_bbox_iou is not None:
        extra['min_bbox_iou'] = min_bbox_iou
    if min_levenshtein_ratio is not None:
        extra['min_levenshtein_ratio'] = min_levenshtein_ratio
    if moving_threshold is not None:
        extra['moving_text_threshold'] = moving_threshold
    if max_text_length is not None:
        extra['max_text_length'] = max_text_length
    if min_text_confidence is not None:
        extra['min_text_confidence'] = min_text_confidence
    if max_text_confidence is not None:
        extra['max_text_confidence'] = max_text_confidence
    if max_height_width_ratio is not None:
        extra['max_height_width_ratio'] = max_height_width_ratio
    if get_detection_histogram is not None:
        extra['get_detection_histogram'] = get_detection_histogram
    if detection_histogram_bins is not None:
        extra['detection_histogram_bins'] = detection_histogram_bins
    if max_height_difference_ratio is not None:
        extra['max_height_difference_ratio'] = max_height_difference_ratio
    if max_horizontal_distance_ratio is not None:
        extra['max_horizontal_distance_ratio'] = max_horizontal_distance_ratio
    if get_frame_index is not None:
        extra['frame'] = get_frame_index
    if get_bbox is not None:
        extra['bbox'] = get_bbox
    if face_recognition is not None:
        extra['recognition'] = face_recognition
    if face_age is not None:
        extra['age'] = face_age
    if face_gender is not None:
        extra['gender'] = face_gender
    if face_expression is not None:
        extra['expression'] = face_expression
    if face_ethnicity is not None:
        extra['ethnicity'] = face_ethnicity

    # Get presigned URL
    data = {'filename': fpath, 'type': type, 'extra': extra}
    response = requests.post(f'{url}/upload/', headers=headers, data=json.dumps(data))
    if response.status_code != 201:
        raise MediacatchUploadError(f'Failed to get presigned URL: {response}')

    presigned_url_response = response.json()
    file_id = presigned_url_response['file_id']

    # Create a session with retry logic
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504, 400])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    # upload to s3
    success = False
    for _ in range(max_retries):
        try:
            with open(fpath, 'rb') as f:
                files = {'file': (presigned_url_response['fields']['key'], f)}
                fields_dict = dict(presigned_url_response['fields'])
                response = session.post(
                    presigned_url_response['url'],
                    data=fields_dict,
                    files=files,
                    verify=True,
                )

            if response.status_code != 204:
                raise MediacatchUploadError(f'Failed to upload to S3: {response}')

            success = True
            break

        except Exception:
            success = False
            time.sleep(delay)

    if not success:
        raise MediacatchUploadError(f'Failed to upload to S3: {response}')

    # Mark file as uploaded
    data = {'file_id': file_id}
    response = requests.post(f'{url}/upload/complete/', headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        raise MediacatchUploadError(f'Failed to mark file {fpath} as uploaded: {response}')

    if verbose:
        logger.info(f'File {fpath} uploaded with ID {file_id}')

    return file_id
