# YOLO Zone Detector

A comprehensive Python package for person detection and tracking in danger zones using YOLO models, with real-time RTSP streaming capabilities.

## ✨ Features

- **Person Detection**: Advanced YOLO-based person detection and tracking
- **Danger Zone Management**: Create and manage danger zones with file-based or interactive mouse-based setup
- **Real-time Tracking**: Track people entering/leaving danger zones with time-based warnings
- **RTSP Streaming**: Stream detection results via RTSP protocol
- **Flexible Configuration**: Support for various video sources (webcam, video files)
- **Warning System**: Configurable time-based warnings for safety monitoring

## 🚀 Installation

### Using Poetry (Recommended)

```bash
# Clone the repository
git clone https://git.aipower.vn/minhcq/zone-detect.git
cd zone-detector

# Install with Poetry
poetry install

# Activate virtual environment
poetry shell
```

### Using pip

```bash
# Install from PyPI (when published)
pip install yolo-zone-detector

# Or install from source
pip install git+https://git.aipower.vn/minhcq/zone-detect.git
```

## 📦 Dependencies

- Python 3.8+
- OpenCV (cv2)
- Ultralytics YOLO
- PyTorch
- NumPy
- CVZone

## 🎯 Quick Start

### Command Line Interface

```bash
# Interactive mode
yolo-zone-detector --interactive

# Direct usage with webcam
yolo-zone-detector --video 0 --zone-mode 1 --streaming

# Use video file with mouse-based zone creation
yolo-zone-detector --video path/to/video.mp4 --zone-mode 2

# Full configuration
yolo-zone-detector \
  --video path/to/video.mp4 \
  --model yolo11s.pt \
  --zone-mode 1 \
  --warning-time 15.0 \
  --streaming \
  --rtsp-url rtsp://localhost:8554/live
```

### Python API

```python
from zone_detector import YOLODetectionStreamer

# Create detector instance
detector = YOLODetectionStreamer(
    video_path='path/to/video.mp4',
    model_path='yolo11n.pt',
    zone_mode=1,  # 1: file-based, 2: mouse-based
    warning_time=10.0,
    enable_streaming=True,
    rtsp_url='rtsp://localhost:8554/live'
)

# Start detection
capture_thread, stream_thread = detector.start_streaming()

# Wait for completion
capture_thread.join()
if stream_thread:
    stream_thread.join()

# Clean up
detector.stop_streaming()
```

### Using Individual Components

```python
from yolo_zone_detector import ZoneManager, YOLOModel, PersonTracker

# Zone management
zone_manager = ZoneManager(zone_mode=1)

# YOLO model
yolo_model = YOLOModel(model_path='yolo11n.pt')

# Person tracking
tracker = PersonTracker(warning_time=10.0)

# Process frame
results = yolo_model.detect_and_track(frame)
people_in_zone = tracker.update_tracking(results, zone_manager, current_time)
```

## 🎮 Controls

### Keyboard Controls (During Detection)
- `q`: Quit application
- `r`: Reset tracking data
- `d`: Force detection update
- `s`: Start detection (after zone setup)

### Mouse Controls (Zone Mode 2)
- **Left Click**: Add point to zone
- **Right Click**: Complete zone creation
- `c`: Clear selected points
- `n`: Complete zone creation
- `z`: Toggle zone creation mode

## ⚙️ Configuration

### Zone Modes

1. **File-based (Mode 1)**: Load zones from `danger_zones.json`
2. **Mouse-based (Mode 2)**: Create zones interactively with mouse

### Zone File Format (`danger_zones.json`)

```json
{
    "default_zone": [
        [115,217],
        [868,227],
        [881,385],
        [122,395],
        [55,296]
    ],
    "custom_zones": [
        [
            [115,217],
            [868,227],
            [881,385],
            [122,395],
            [55,296]
        ]
    ]
}
```

### RTSP Streaming

The package supports RTSP streaming via FFmpeg. Make sure FFmpeg is installed:

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

## 📊 Performance

- **Detection Interval**: Configurable (default: 0.5s)
- **Supported Models**: All YOLO11 variants (n, s, m, l, x)
- **Video Sources**: Webcam, video files, network streams
- **Output**: Real-time annotation with RTSP streaming

## 🔧 Development

### Setup Development Environment



### Building Package

```bash
# Build package
poetry build

# Publish to PyPI
poetry publish
```

## Installation

```bash
pip install zone-detector

yolo-roi --video my_video.mp4 --zone-mode 1