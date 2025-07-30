# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SyncNet_py313 is a Python 3.13 implementation of SyncNet, a neural network model for audio-visual synchronization detection. It evaluates lip-sync quality in videos by computing synchronization confidence scores between audio and visual features.

## Common Commands

### Setup and Dependencies
```bash
# Install dependencies
pip install -r requirements.txt

# Ensure ffmpeg is installed on the system
# Ubuntu/Debian: sudo apt-get install ffmpeg
# macOS: brew install ffmpeg
```

### Running SyncNet

```bash
# Run on a single example
cd script
python run_syncnet_pipeline_on_1example.py

# Run on MoChaBench evaluation set
python run_syncnet_pipeline_on_mocha_generation_on_mocha_bench.py

# Run on custom model results
python run_syncnet_pipeline_on_your_own_model_results.py
```

## Architecture Overview

### Core Components

1. **SyncNetModel** (`script/SyncNetModel.py`): The neural network architecture
   - Audio encoder: 1D convolutions + FC layers for audio feature extraction
   - Visual encoder: 3D convolutions + FC layers for video feature extraction
   - Outputs 1024-dimensional embeddings for both modalities

2. **SyncNetInstance** (`script/SyncNetInstance.py`): Inference wrapper
   - Loads pre-trained weights from `weights/syncnet_v2.model`
   - Calculates synchronization scores using sliding window approach
   - Returns offset values and confidence scores

3. **Pipeline** (`script/syncnet_pipeline.py`): End-to-end processing
   - Face detection using S3FD detector
   - Audio extraction and MFCC feature computation
   - Video frame extraction and face cropping
   - Synchronization score calculation

4. **Face Detector** (`script/detectors/s3fd/`): S3FD implementation
   - Uses pre-trained weights from `weights/sfd_face.pth`
   - Handles multi-scale face detection

### Data Flow

1. Input: Video file (e.g., `.avi`, `.mp4`)
2. Face detection → Face tracking → Face cropping
3. Audio extraction → MFCC features (13 coefficients)
4. Parallel processing of audio and visual streams
5. Output: Synchronization scores and offset values

### Key Implementation Details

- Audio: 16kHz sampling, 25ms windows, 10ms stride
- Video: 25 FPS, 224x224 face crops, 5-frame sequences
- Embeddings: 1024-dimensional for both modalities
- Scoring: Cosine similarity between audio/visual embeddings

## Important Notes

- The model requires pre-trained weights in `weights/` directory
- GPU is strongly recommended for inference (falls back to CPU if unavailable)
- Face detection is critical - videos without detectable faces will fail
- The pipeline creates temporary directories for intermediate processing