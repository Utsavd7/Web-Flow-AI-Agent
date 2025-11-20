import os
from moviepy import VideoFileClip, concatenate_videoclips, clips_array
from src.visualize_logs import create_log_video

def combine_videos(video_dir, output_file):
    """
    Combines all .webm files in video_dir into a single .mp4 file.
    Also generates log videos and creates a split-screen layout.
    """
    # Find all tasks
    base_dir = os.path.dirname(video_dir)
    task_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d.startswith("task_")]
    task_dirs.sort()
    
    if not task_dirs:
        print("No task directories found.")
        return

    final_clips = []
    
    for task in task_dirs:
        task_path = os.path.join(base_dir, task)
        logs_path = os.path.join(task_path, "logs.json")
        
        # Find corresponding video
        # The video name is a hash, so we don't know it directly.
        # But we can look in the videos dir and try to match timestamps?
        # Actually, BrowserManager saves with a random hash.
        # We need to know which video belongs to which task.
        # FIX: BrowserManager should return the video path or we should rename it.
        # For now, let's assume we can't easily match them without changing BrowserManager.
        # Wait, BrowserManager records to 'videos/'. 
        # Let's modify BrowserManager to save to 'task_dir/video.webm' or return the path.
        # Since I can't easily change BrowserManager's return in the loop without restarting,
        # I will rely on the fact that I run tasks sequentially.
        # The 'videos' dir will have files sorted by creation time.
        pass

    # Alternative: Just grab all videos from 'videos' dir and assume order matches tasks.
    # This is risky but might work if we deleted the dir before running.
    video_files = [f for f in os.listdir(video_dir) if f.endswith(".webm")]
    # Sort by modification time to ensure order matches execution order
    video_files.sort(key=lambda x: os.path.getmtime(os.path.join(video_dir, x)))
    
    if len(video_files) != len(task_dirs):
        print(f"Warning: Mismatch between tasks ({len(task_dirs)}) and videos ({len(video_files)}).")
        # Fallback to just concatenating videos if mismatch
        # But we really want the split screen.
        # Let's try to pair them up as best as we can.
        pass

    print(f"Found {len(video_files)} videos and {len(task_dirs)} tasks.")
    
    for i, vf in enumerate(video_files):
        if i >= len(task_dirs): break
        
        task_name = task_dirs[i]
        video_path = os.path.join(video_dir, vf)
        logs_path = os.path.join(base_dir, task_name, "logs.json")
        log_video_path = os.path.join(base_dir, task_name, "logs.mp4")
        
        try:
            browser_clip = VideoFileClip(video_path)
            
            # Create log video
            if os.path.exists(logs_path):
                print(f"Generating log video for {task_name}...")
                create_log_video(logs_path, log_video_path, browser_clip.duration)
                
                if os.path.exists(log_video_path):
                    log_clip = VideoFileClip(log_video_path)
                    # Resize log clip to match height if needed, or just stack
                    # Browser is 1920x1080. Logs are 600x1080.
                    # Stack side by side
                    combined = clips_array([[browser_clip, log_clip]])
                    final_clips.append(combined)
                else:
                    final_clips.append(browser_clip)
            else:
                final_clips.append(browser_clip)
                
        except Exception as e:
            print(f"Error processing {task_name}: {e}")

    if final_clips:
        try:
            final_clip = concatenate_videoclips(final_clips, method="compose")
            final_clip.write_videofile(output_file, codec="libx264", audio=False)
            print(f"Successfully created combined split-screen video: {output_file}")
        except Exception as e:
            print(f"Error combining videos: {e}")
        finally:
            # Close clips
            for clip in final_clips:
                clip.close()
            if 'final_clip' in locals():
                final_clip.close()
    else:
        print("No valid clips to combine.")

if __name__ == "__main__":
    # Default paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    video_dir = os.path.join(base_dir, "captured_workflows", "videos")
    output_file = os.path.join(base_dir, "captured_workflows", "combined_workflow.mp4")
    
    combine_videos(video_dir, output_file)
