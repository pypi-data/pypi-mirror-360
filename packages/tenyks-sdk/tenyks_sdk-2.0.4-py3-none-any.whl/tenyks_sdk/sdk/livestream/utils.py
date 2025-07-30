from datetime import datetime, timedelta, timezone
from typing import List


def parse_iso_timestamp(timestamp_str: str) -> datetime:
    """
    Parse an ISO format timestamp string in a way that's compatible with Python 3.10.
    Handles both 'Z' and '+00:00' timezone formats.
    """
    # Replace 'Z' with '+00:00' for Python 3.10 compatibility
    if timestamp_str.endswith("Z"):
        timestamp_str = timestamp_str[:-1] + "+00:00"
    return datetime.fromisoformat(timestamp_str)


def fill_gaps_with_no_data(
    segments: List[dict],
    no_data_path: str,
    segment_duration: float = 2.0,
    start_timestamp: datetime | None = None,
    end_timestamp: datetime | None = None,
) -> List[dict]:
    """
    Fills temporal gaps in HLS segments using a local no-data.ts segment.

    Args:
        segments (List[dict]): List of segments with 'timestamp', 'duration_seconds', 'signed_url'.
        no_data_path (str): Local path to no-data.ts file.
        segment_duration (float): Duration to assume per segment (default: 2.0).
        start_timestamp (datetime | None): Optional forced start time.
        end_timestamp (datetime | None): Optional forced end time.

    Returns:
        List[dict]: Ordered list of real and filler segments.
    """
    if not segments:
        return []

    segments = sorted(segments, key=lambda s: s["timestamp"])
    result = []

    expected_time = start_timestamp or parse_iso_timestamp(segments[0]["timestamp"])

    for segment in segments:
        actual_time = parse_iso_timestamp(segment["timestamp"])

        while actual_time - expected_time >= timedelta(seconds=segment_duration + 0.1):
            result.append(
                {
                    "local_path": no_data_path,
                    "timestamp": expected_time,
                    "duration_seconds": segment_duration,
                    "is_filler": True,
                }
            )
            expected_time += timedelta(seconds=segment_duration)

        result.append(
            {
                **segment,
                "is_filler": False,
            }
        )
        expected_time = actual_time + timedelta(seconds=segment["duration_seconds"])

    if end_timestamp:
        while expected_time <= end_timestamp - timedelta(seconds=segment_duration):
            result.append(
                {
                    "local_path": no_data_path,
                    "timestamp": expected_time,
                    "duration_seconds": segment_duration,
                    "is_filler": True,
                }
            )
            expected_time += timedelta(seconds=segment_duration)

    return result
