import json
import os
import math
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy import VideoClip, concatenate_videoclips

def create_log_video(logs_path, output_path, duration, width=600, height=1080, fps=10):
    """
    Creates a video of scrolling logs from a json file.
    
    Args:
        logs_path: Path to logs.json (list of {time, message})
        output_path: Path to save .mp4
        duration: Total duration of the video in seconds
        width: Width of the video
        height: Height of the video
        fps: Frames per second
    """
    try:
        with open(logs_path, 'r') as f:
            logs = json.load(f)
    except Exception as e:
        print(f"Error reading logs {logs_path}: {e}")
        return

    # Setup font
    try:
        # Try to use a monospace font
        font = ImageFont.truetype("/System/Library/Fonts/Monaco.ttf", 14)
    except:
        font = ImageFont.load_default()

    # Pre-calculate lines for all logs
    # Each log might need multiple lines if it wraps (simple wrapping)
    char_width = 8 # Approximate
    max_chars = width // char_width
    
    processed_logs = []
    for entry in logs:
        msg = f"[{entry['time']:.2f}s] {entry['message']}"
        # Simple wrap
        while len(msg) > max_chars:
            processed_logs.append({'time': entry['time'], 'text': msg[:max_chars]})
            msg = "  " + msg[max_chars:] # Indent wrapped lines
        processed_logs.append({'time': entry['time'], 'text': msg})

    line_height = 20
    max_lines_on_screen = height // line_height
    
    def make_frame(t):
        # Find logs that have happened by time t
        current_lines = [l['text'] for l in processed_logs if l['time'] <= t]
        
        # Scroll: keep only the last N lines
        if len(current_lines) > max_lines_on_screen:
            current_lines = current_lines[-max_lines_on_screen:]
            
        # Draw
        img = Image.new('RGB', (width, height), color=(10, 10, 10)) # Dark background
        draw = ImageDraw.Draw(img)
        
        y = 10
        for line in current_lines:
            # Color coding based on content
            fill = (200, 200, 200) # Default gray
            if "Action:" in line:
                fill = (100, 255, 100) # Green
            elif "Step" in line:
                fill = (255, 255, 100) # Yellow
            elif "Error" in line:
                fill = (255, 100, 100) # Red
            elif "Thinking" in line:
                fill = (100, 200, 255) # Blue
                
            draw.text((10, y), line, font=font, fill=fill)
            y += line_height
            
        return np.array(img)

    # Create clip
    clip = VideoClip(make_frame, duration=duration)
    clip.fps = fps
    clip.write_videofile(output_path, codec="libx264", audio=False, logger=None)
    print(f"Created log video: {output_path}")

if __name__ == "__main__":
    # Test
    pass
