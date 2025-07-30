import sys
from .read_images import get_frames_from_mp4
from .video_downloader import download_video

SIGMA = 4
KERNEL_SIZE = int(SIGMA * 3) + 1

# Define videos and their frame limits
VIDEOS = {
    "bse_one.mp4": 120,
    "bse_two.mp4": 1900,
    "cell_one.mp4": 750,
    "cell_two.mp4": 450,
    "dendrites_one.mp4": 1000,
    "nucleation_one.mp4": 650,
}

LOADED = {}

def safe_download(video_name: str):
    try:
        sourcePath = download_video(video_name)
        return sourcePath
    except Exception as e:
        print(f"[ERROR] Failed to download {video_name}: {e}", file=sys.stderr)
        return None

for video_filename, frame_limit in VIDEOS.items():
    key = video_filename.split(".")[0].upper()
    path = safe_download(video_filename)
    if path:
        LOADED[key] = get_frames_from_mp4(str(path), frame_limit)
    else:
        LOADED[key] = None
        print(f"[WARN] {key} is not available.", file=sys.stderr)

# Raise error if all videos failed
if all(v is None for v in LOADED.values()):
    raise RuntimeError("None of the videos could be downloaded — check GITHUB_TOKEN or internet access.")

# Optional: expose individual variables
BSE_ONE = LOADED.get("BSE_ONE")
BSE_TWO = LOADED.get("BSE_TWO")
CELL_ONE = LOADED.get("CELL_ONE")
CELL_TWO = LOADED.get("CELL_TWO")
DENDRITES_ONE = LOADED.get("DENDRITES_ONE")
NUCLEATION_ONE = LOADED.get("NUCLEATION_ONE")

