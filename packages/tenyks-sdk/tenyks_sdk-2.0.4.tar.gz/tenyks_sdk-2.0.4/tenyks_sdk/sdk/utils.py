from datetime import datetime, timedelta
from importlib.resources import files

import cv2
import requests


def get_no_data_ts_path() -> str:
    """
    Return the absolute path to the no-data.ts file bundled in the SDK.
    """
    return str(files("tenyks_sdk.sdk.static").joinpath("no-data.ts"))


def download_file(url: str, dest_path: str):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def annotate_video_with_bboxes(
    video_path: str,
    predictions: list[dict],
    output_path: str,
    predictions_per_second: int,
):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    start_time = None

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = None

    frame_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if start_time is None:
            start_time = datetime.fromisoformat(
                predictions[0]["timestamp"].replace("Z", "+00:00")
            )

        current_ts = start_time + (frame_idx / fps) * timedelta(seconds=1)

        linger_seconds = 0.8 / predictions_per_second

        for pred in predictions:
            ts = datetime.fromisoformat(pred["timestamp"].replace("Z", "+00:00"))
            time_diff = (ts - current_ts).total_seconds()

            if -linger_seconds <= time_diff <= 0:
                # Draw bbox: show it from the moment it's detected up to `linger_seconds` after
                x1, y1, x2, y2 = map(int, pred["bbox"])
                label = pred["label"]
                score = pred["score"]
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    f"{label} ({score:.2f})",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                )

        if out is None:
            height, width = frame.shape[:2]
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        out.write(frame)
        frame_idx += 1

    cap.release()
