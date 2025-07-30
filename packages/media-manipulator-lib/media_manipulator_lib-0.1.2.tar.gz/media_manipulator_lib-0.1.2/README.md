# 🎬 Media Manipulator Library

A modular, pluggable video editing library built with Python and FFmpeg. 
Supports programmatic video transformations like text (watermark) overlay and audio merging using strategy and interpreter design patterns.

---

## 🚀 Features

- Add watermark (text overlay) to videos
- Overlay audio tracks onto videos
- Process nested JSON editing instructions
- In-memory and tempfile-based FFmpeg pipelines
- Clean, extendable strategy-based architecture
- Custom command interpreter for complex video editing workflows
- Developer-friendly logging using `colorlog`

---

## 📦 Installation

### From PyPI (coming soon)
```bash
pip install video-editing-lib
```

### From source
```bash
git clone https://github.com/angel-one/media-manipulator-library
cd media-manipulator-library
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

## 🧪 Testing

```bash
pytest            # all tests
pytest tests/unit         # only unit tests
pytest tests/integration  # only integration tests
```

---

## 🔧 Usage Example

```python
from video_editor import process_json_command

command = {
    "operation": "overlay",
    "left": {
        "operation": "overlay",
        "left": {
            "type": "video",
            "bytes": open("video.mp4", "rb").read()
        },
        "right": {
            "type": "text",
            "value": "Watermark Text",
            "position": "bottom"
        }
    },
    "right": {
        "type": "audio",
        "bytes": open("audio.mp3", "rb").read()
    }
}

result = process_json_command(command)

with open("output.mp4", "wb") as f:
    f.write(result["bytes"].getvalue())
```

---

## 📂 Project Structure

```
media-manipulator-lib/
├──media_manipulator/              # Main package
│   ├── __init__.py
│   ├── processor.py           # Command executor
│   ├── interpreter.py         # JSON → command parser
│   └── strategies/           # mediaManipulatorStrategy implementations
├── tests/                    # Unit and integration tests
├── README.md
├── pyproject.toml
├── setup.py
└── requirements.txt          # Optional (for dev setup)
```

---

## 🛠️ Built With

- **Python 3.11+**
- **FFmpeg + ffmpeg-python**
- **pytest** for testing
- **colorlog** for colored logging

---

## 📜 License

MIT License © 2025 Aditya Sharma / AngelOne

---

## 🙋‍♂️ Contributing

Contributions welcome! Please submit issues or pull requests for improvements or new features.

---

## 📫 Contact

For questions or support, open a GitHub issue or reach out to itsadityasharma7124@gmail.com
