import os
from playwright.async_api import Page
from datetime import datetime

class StateCapturer:
    def __init__(self, output_dir: str = "captured_workflows"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    async def capture_state(self, page: Page, step_name: str, task_id: str, action_description: str = ""):
        """
        Captures the current state of the page:
        - Screenshot
        - Metadata (URL, Action)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_dir = os.path.join(self.output_dir, task_id)
        os.makedirs(task_dir, exist_ok=True)

        # Screenshot
        screenshot_path = os.path.join(task_dir, f"{step_name}_{timestamp}.png")
        await page.screenshot(path=screenshot_path, full_page=False)
        
        # Metadata
        metadata = {
            "timestamp": timestamp,
            "url": page.url,
            "step": step_name,
            "action_taken": action_description
        }
        import json
        with open(os.path.join(task_dir, f"{step_name}_{timestamp}_metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)
        
        return screenshot_path
