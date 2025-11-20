import argparse
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.generate_dataset import main as generate_main
from src.combine_videos import combine_videos

def run_cli():
    parser = argparse.ArgumentParser(description="Web Flow Capture Agent CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate Command
    generate_parser = subparsers.add_parser("generate", help="Generate dataset from tasks")
    generate_parser.add_argument("--headless", action="store_true", help="Run in headless mode")

    # Combine Command
    combine_parser = subparsers.add_parser("combine", help="Combine captured videos")
    
    args = parser.parse_args()

    if args.command == "generate":
        print("Starting dataset generation...")
        # Note: generate_dataset.main currently doesn't accept args, 
        # but we can modify it later if needed. For now it runs the default suite.
        asyncio.run(generate_main())
        
    elif args.command == "combine":
        print("Combining videos...")
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        video_dir = os.path.join(base_dir, "captured_workflows", "videos")
        output_file = os.path.join(base_dir, "captured_workflows", "combined_workflow.mp4")
        
        if not os.path.exists(video_dir):
            print(f"Error: Video directory not found at {video_dir}")
            return
            
        combine_videos(video_dir, output_file)
        
    else:
        parser.print_help()

if __name__ == "__main__":
    run_cli()
