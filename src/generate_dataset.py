import asyncio
import os
import shutil
import time
import json
from src.browser_manager import BrowserManager
from src.capture import StateCapturer
from src.agent import AgentBrain
from src.main import extract_interactive_elements
from src.combine_videos import combine_videos

class TaskLogger:
    def __init__(self):
        self.logs = []
        self.start_time = time.time()
        
    def log(self, message):
        elapsed = time.time() - self.start_time
        print(f"[{elapsed:.2f}s] {message}")
        self.logs.append({
            "time": elapsed,
            "message": message
        })
        
    def save(self, path):
        with open(path, 'w') as f:
            json.dump(self.logs, f, indent=2)

async def run_task(task_name, start_url, goal):
    logger = TaskLogger()
    logger.log(f"=== Running Task: {task_name} ===")
    
    browser_manager = BrowserManager(headless=False)
    capturer = StateCapturer()
    brain = AgentBrain()
    
    await browser_manager.start()
    try:
        logger.log(f"Navigating to {start_url}")
        await browser_manager.navigate(start_url)
        step = 1
        max_steps = 15 # Increased for longer flows
        
        while step <= max_steps:
            logger.log(f"Step {step}")
            
            # Observe first to get elements for decision
            elements = await extract_interactive_elements(browser_manager.page)
            current_url = await browser_manager.get_current_url()
            
            # Think
            logger.log(f"Thinking about goal: {goal}")
            action = await brain.get_next_action(goal, current_url, elements)
            logger.log(f"Action: {action}")
            
            # Capture (Reduced frequency: Step 1, every 2nd step, or finish)
            if step == 1 or step % 2 == 0 or action["type"] == "finish":
                await capturer.capture_state(
                    browser_manager.page, 
                    f"step_{step:02d}", 
                    task_name, 
                    action_description=str(action)
                )
            
            # Act
            if action["type"] == "finish":
                logger.log(f"Task {task_name} completed.")
                break
            elif action["type"] == "click":
                await browser_manager.click(action["selector"])
            elif action["type"] == "type":
                await browser_manager.type(action["selector"], action["text"])
                if "search" in action["selector"].lower() or "input" in action["selector"].lower():
                     await browser_manager.press("Enter")
            elif action["type"] == "navigate":
                await browser_manager.navigate(action["url"])
                
            # Wait a bit for network/animations
            await browser_manager.page.wait_for_timeout(2000)
            step += 1
            
    except Exception as e:
        logger.log(f"Error in task {task_name}: {e}")
    finally:
        await browser_manager.stop()
        
        # Save logs
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        task_dir = os.path.join(base_dir, "captured_workflows", task_name)
        os.makedirs(task_dir, exist_ok=True)
        logger.save(os.path.join(task_dir, "logs.json"))

async def main():
    tasks = [
        {
            "name": "task_01_github_search",
            "start_url": "https://github.com/",
            "goal": "Search for 'AutoGPT' on GitHub"
        },
        {
            "name": "task_02_github_issues",
            "start_url": "https://github.com/Significant-Gravitas/AutoGPT",
            "goal": "Navigate to the Issues tab"
        },
        {
            "name": "task_03_python_org_search",
            "start_url": "https://www.python.org/",
            "goal": "Search for 'PEP 8'"
        },
        {
            "name": "task_04_hackernews_show",
            "start_url": "https://news.ycombinator.com/",
            "goal": "Navigate to 'Show HN'"
        }
    ]
    
    # Clean up old data
    if os.path.exists("captured_workflows"):
        shutil.rmtree("captured_workflows")
    
    for task in tasks:
        await run_task(task["name"], task["start_url"], task["goal"])
        
    # Combine videos
    print("Combining videos...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level from src to root
    root_dir = os.path.dirname(base_dir)
    video_dir = os.path.join(root_dir, "captured_workflows", "videos")
    output_file = os.path.join(root_dir, "captured_workflows", "combined_workflow.mp4")
    
    # Run in thread pool to avoid blocking asyncio loop with heavy processing
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, combine_videos, video_dir, output_file)

if __name__ == "__main__":
    asyncio.run(main())
