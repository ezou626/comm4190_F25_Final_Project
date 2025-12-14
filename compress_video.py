#!/usr/bin/env python3
"""
Compress demo.mp4 to approximately 1/5 of its original size.
Requires ffmpeg to be installed on your system.
"""

import subprocess
import os

INPUT_FILE = "demo.mp4"
OUTPUT_FILE = "demo_compressed.mp4"

def compress_video():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found")
        return
    
    # Get original file size
    original_size = os.path.getsize(INPUT_FILE)
    print(f"Original file size: {original_size / (1024*1024):.2f} MB")
    
    # Calculate target bitrate for ~1/5 compression
    # Get video duration first
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
         "-of", "default=noprint_wrappers=1:nokey=1", INPUT_FILE],
        capture_output=True, text=True
    )
    duration = float(result.stdout.strip())
    
    # Target size is 1/5 of original
    target_size_bytes = original_size / 5
    # Target bitrate in kbps (leaving some room for audio ~128kbps)
    target_video_bitrate = int((target_size_bytes * 8 / duration - 128000) / 1000)
    target_video_bitrate = max(target_video_bitrate, 500)  # Minimum 500kbps
    
    print(f"Target video bitrate: {target_video_bitrate}k")
    print(f"Compressing...")
    
    # Compress using ffmpeg with CRF for quality-based compression
    # Using CRF 28-32 typically gives good compression
    subprocess.run([
        "ffmpeg", "-y",
        "-i", INPUT_FILE,
        "-c:v", "libx264",
        "-crf", "30",  # Higher CRF = more compression (18-28 is typical, 30+ is aggressive)
        "-preset", "slow",  # Slower = better compression
        "-c:a", "aac",
        "-b:a", "96k",  # Lower audio bitrate
        "-movflags", "+faststart",  # Optimize for web streaming
        OUTPUT_FILE
    ], check=True)
    
    # Report results
    compressed_size = os.path.getsize(OUTPUT_FILE)
    ratio = original_size / compressed_size
    print(f"\nCompression complete!")
    print(f"Compressed file size: {compressed_size / (1024*1024):.2f} MB")
    print(f"Compression ratio: {ratio:.2f}x")
    print(f"Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    compress_video()

