import sys
import json
from media_manipulator import process_video_request
from media_manipulator.utils.logger import logger

def main():
    if len(sys.argv) != 2:
        print("Usage: python -m video_editor.cli input.json")
        sys.exit(1)

    try:
        with open(sys.argv[1], 'r') as f:
            request = json.load(f)

        result = process_video_request(request)

        if result:
            with open("output.mp4", "wb") as f:
                f.write(result["bytes"].getvalue())
            logger.success("Video saved to output.mp4")
        else:
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error while running CLI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
