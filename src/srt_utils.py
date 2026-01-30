"""SRT subtitle utilities for parsing, timing sync, and manipulation"""

import re
from typing import List, Dict, Optional


def parse_timestamp(timestamp: str) -> int:
    """
    Parse SRT timestamp to milliseconds

    Args:
        timestamp: SRT timestamp format "HH:MM:SS,mmm"

    Returns:
        Time in milliseconds
    """
    # Handle both comma and period as decimal separator
    timestamp = timestamp.replace('.', ',')
    match = re.match(r'(\d{1,2}):(\d{2}):(\d{2}),(\d{3})', timestamp.strip())
    if not match:
        raise ValueError(f"Invalid timestamp format: {timestamp}")

    hours, minutes, seconds, millis = map(int, match.groups())
    return (hours * 3600 + minutes * 60 + seconds) * 1000 + millis


def format_timestamp(ms: int) -> str:
    """
    Format milliseconds to SRT timestamp

    Args:
        ms: Time in milliseconds

    Returns:
        SRT timestamp format "HH:MM:SS,mmm"
    """
    if ms < 0:
        ms = 0

    hours = ms // 3600000
    ms %= 3600000
    minutes = ms // 60000
    ms %= 60000
    seconds = ms // 1000
    millis = ms % 1000

    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def parse_timing_line(timing: str) -> tuple:
    """
    Parse SRT timing line to start and end timestamps

    Args:
        timing: SRT timing line "HH:MM:SS,mmm --> HH:MM:SS,mmm"

    Returns:
        Tuple of (start_ms, end_ms)
    """
    parts = timing.split('-->')
    if len(parts) != 2:
        raise ValueError(f"Invalid timing line: {timing}")

    start_ms = parse_timestamp(parts[0].strip())
    end_ms = parse_timestamp(parts[1].strip())
    return start_ms, end_ms


def format_timing_line(start_ms: int, end_ms: int) -> str:
    """
    Format start and end times to SRT timing line

    Args:
        start_ms: Start time in milliseconds
        end_ms: End time in milliseconds

    Returns:
        SRT timing line
    """
    return f"{format_timestamp(start_ms)} --> {format_timestamp(end_ms)}"


def parse_srt(content: str) -> List[Dict]:
    """
    Parse SRT content into list of subtitle blocks

    Args:
        content: Raw SRT file content

    Returns:
        List of dicts with index, start_ms, end_ms, timing, text
    """
    blocks = []
    raw_blocks = re.split(r'\n\n+', content.strip())

    for raw_block in raw_blocks:
        lines = raw_block.strip().split('\n')
        if len(lines) >= 3:
            try:
                index = int(lines[0].strip())
                timing = lines[1].strip()
                start_ms, end_ms = parse_timing_line(timing)
                text = '\n'.join(lines[2:])

                blocks.append({
                    "index": index,
                    "start_ms": start_ms,
                    "end_ms": end_ms,
                    "timing": timing,
                    "text": text,
                })
            except (ValueError, IndexError):
                continue

    return blocks


def build_srt(blocks: List[Dict]) -> str:
    """
    Build SRT content from blocks

    Args:
        blocks: List of subtitle blocks

    Returns:
        SRT file content
    """
    output_lines = []
    for i, block in enumerate(blocks, 1):
        output_lines.append(str(i))

        if "start_ms" in block and "end_ms" in block:
            timing = format_timing_line(block["start_ms"], block["end_ms"])
        else:
            timing = block["timing"]

        output_lines.append(timing)
        output_lines.append(block["text"])
        output_lines.append("")

    return '\n'.join(output_lines)


def sync_subtitles(content: str, first_subtitle_time_ms: int) -> str:
    """
    Sync all subtitles by adjusting timing so the first subtitle
    starts at the specified time.

    Args:
        content: Raw SRT file content
        first_subtitle_time_ms: When the first subtitle should start (in ms)

    Returns:
        Synced SRT content
    """
    blocks = parse_srt(content)

    if not blocks:
        return content

    # Calculate offset: new start time minus current first subtitle start
    current_first_start = blocks[0]["start_ms"]
    offset_ms = first_subtitle_time_ms - current_first_start

    # Apply offset to all blocks
    for block in blocks:
        block["start_ms"] = max(0, block["start_ms"] + offset_ms)
        block["end_ms"] = max(0, block["end_ms"] + offset_ms)

    return build_srt(blocks)


def shift_subtitles(content: str, offset_ms: int) -> str:
    """
    Shift all subtitles by a given offset (positive or negative)

    Args:
        content: Raw SRT file content
        offset_ms: Offset in milliseconds (positive = later, negative = earlier)

    Returns:
        Shifted SRT content
    """
    blocks = parse_srt(content)

    for block in blocks:
        block["start_ms"] = max(0, block["start_ms"] + offset_ms)
        block["end_ms"] = max(0, block["end_ms"] + offset_ms)

    return build_srt(blocks)


def time_string_to_ms(time_str: str) -> int:
    """
    Convert various time string formats to milliseconds

    Supported formats:
    - "HH:MM:SS,mmm" or "HH:MM:SS.mmm" (SRT format)
    - "MM:SS" (minutes:seconds)
    - "SS" or "SS.mmm" (just seconds)
    - "+/-SS" (offset in seconds)

    Args:
        time_str: Time string

    Returns:
        Time in milliseconds
    """
    time_str = time_str.strip()

    # Check for SRT format
    if re.match(r'\d{1,2}:\d{2}:\d{2}[,\.]\d{3}', time_str):
        return parse_timestamp(time_str)

    # Check for MM:SS format
    if re.match(r'\d{1,2}:\d{2}$', time_str):
        parts = time_str.split(':')
        minutes, seconds = int(parts[0]), int(parts[1])
        return (minutes * 60 + seconds) * 1000

    # Check for MM:SS.mmm format
    if re.match(r'\d{1,2}:\d{2}\.\d+$', time_str):
        parts = time_str.split(':')
        minutes = int(parts[0])
        seconds = float(parts[1])
        return int((minutes * 60 + seconds) * 1000)

    # Check for seconds (with optional decimal)
    if re.match(r'^[+-]?\d+\.?\d*$', time_str):
        return int(float(time_str) * 1000)

    raise ValueError(f"Unrecognized time format: {time_str}")
