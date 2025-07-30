<div align="center">

[<img src="docs/assets/mc_logo.svg" alt="mc-logo" width=400>](https://api.mediacatch.io/mediacatch/docs/)<br>

[![Unit Tests](https://github.com/mediacatch/mediacatch/actions/workflows/test.yaml/badge.svg)](https://github.com/mediacatch/mediacatch/actions/workflows/test.yaml)
[![codecov](https://codecov.io/gh/mediacatch/mediacatch/graph/badge.svg?token=D3bBQ64Cs9)](https://codecov.io/gh/mediacatch/mediacatch)
[![Quality Check](https://github.com/mediacatch/mediacatch/actions/workflows/check.yaml/badge.svg)](https://github.com/mediacatch/mediacatch/actions/workflows/check.yaml)
[![Publish](https://github.com/mediacatch/mediacatch/actions/workflows/publish.yaml/badge.svg)](https://github.com/mediacatch/mediacatch/actions/workflows/publish.yaml)
[![Documentation](https://github.com/mediacatch/mediacatch/actions/workflows/documentation.yaml/badge.svg)](https://github.com/mediacatch/mediacatch/actions/workflows/documentation.yaml)<br>

<h4 align="center">
    <p>
        <a href="#requirements">Requirements</a> |
        <a href="#installation">Installation</a> |
        <a href="#getting-started">Getting Started</a> |
    <p>
</h4>

</div>

Python package for easily interfacing with MediaCatch APIs and data formats. Documentation can be found at [api.mediacatch.io/mediacatch/docs/](https://api.mediacatch.io/mediacatch/docs/).

## Requirements

- Python >= 3.10
- MediaCatch API key (contact support@medicatch.io)

## Installation

Install with pip

```bash
pip install mediacatch
```

## Getting Started

Firstly, add your MediaCatch API key to your environment variables

```bash
export MEDIACATCH_API_KEY=<your-api-key-here>
```

Then you can start using the command line interface

```bash
mediacatch --help
usage: mediacatch <command> [<args>]

MediaCatch CLI tool

positional arguments:
  {speech,vision,viz}  mediacatch command helpers
    speech             CLI tool to run inference with MediaCatch Speech API
    vision             CLI tool to run inference with MediaCatch Vision API
    viz                CLI tool to visualize the results of MediaCatch

options:
  -h, --help           show this help message and exit
```

Upload a file to MediaCatch Speech API and get the results

```bash
mediacatch speech path/to/file --save-result path/to/save/result.json
# or to see options
mediacatch speech --help
```

Upload a file to MediaCatch vision API and get the results

```bash
mediacatch vision path/to/file ocr --save-result path/to/save/result.json
# or to see options
mediacatch vision --help
```

Or import as a module
  
```python
from mediacatch.vision import upload, wait_for_result

file_id = upload(
  fpath='path/to/file',
  type='ocr',
  # Optional parameters with their default values
  fps=1, # Frames per second for video processing. Defaults to 1.
  tolerance=10, # Tolerance for text detection. Defaults to 10.
  min_bbox_iou=0.5 # Minimum bounding box intersection over union for text detection. Defaults to 0.5.
  min_levenshtein_ratio=0.75 # Minimum Levenshtein ratio for merging text detection (more info here: https://rapidfuzz.github.io/Levenshtein/levenshtein.html#ratio). Defaults to 0.75.
  moving_threshold=50, # If merged text detections center moves more pixels than this threshold, it will be considered moving text. Defaults to 50.
  max_text_length=3, # If text length is less than this value, use max_text_confidence as confidence threshold. Defaults to 3.
  min_text_confidence=0.5, # Confidence threshold for text detection (if text length is greater than max_text_length). Defaults to 0.5.
  max_text_confidence=0.8, # Confidence threshold for text detection (if text length is less than max_text_length). Defaults to 0.8.
  max_height_width_ratio=2.0, # Discard detection if height/width ratio is greater than this value. Defaults to 2.0.
  get_detection_histogram=False, # If true, get histogram of detection. Defaults to False.
  detection_histogram_bins=8, # Number of bins for histogram calculation. Defaults to 8.
)

result = wait_for_result(file_id)
```

Visualize the results from MediaCatch

```bash
mediacatch viz ocr path/to/file path/to/result.json path/to/save.mp4
# or to see options
mediacatch viz --help
```
