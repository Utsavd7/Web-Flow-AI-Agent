import asyncio
import os
import json
from dotenv import load_dotenv
from src.browser_manager import BrowserManager
from src.capture import StateCapturer
from src.agent import AgentBrain

load_dotenv()

async def extract_interactive_elements(page):
    """
    Extracts interactive elements from the page using Playwright.
    Returns a list of dicts with selector, tag, text, etc.
    """
    # This is a simplified extraction. In a real system, we'd use a more robust script
    # or the Accessibility Tree.
    elements = await page.evaluate("""() => {
        const items = [];
        const tags = ['button', 'a', 'input', 'select', 'textarea'];
        document.querySelectorAll(tags.join(',')).forEach(el => {
            if (el.offsetParent !== null) { // Visible
                items.push({
                    tagName: el.tagName.toLowerCase(),
                    text: el.innerText || el.value || el.placeholder || '',
                    selector: el.id ? '#' + el.id : el.className ? '.' + el.className.split(' ').join('.') : el.tagName.toLowerCase(),
                    attributes: {
                        href: el.href,
                        type: el.type,
                        placeholder: el.placeholder,
                        ariaLabel: el.getAttribute('aria-label'),
                        name: el.name,
                        id: el.id
                    }
                });
            }
        });
        return items;
    }""")
    return elements

async def main():
    task = "Search for 'Artificial Intelligence' on Wikipedia"
    start_url = "https://www.wikipedia.org/"
    
    browser_manager = BrowserManager(headless=False) # Headless=False to see it
    capturer = StateCapturer()
    brain = AgentBrain()
    
    await browser_manager.start()
    
    try:
        print(f"Starting task: {task}")
        await browser_manager.navigate(start_url)
        
        step = 1
        max_steps = 10
        
        while step <= max_steps:
            print(f"--- Step {step} ---")
            
            # 1. Capture State
            current_url = await browser_manager.get_current_url()
            screenshot_path = await capturer.capture_state(browser_manager.page, f"step_{step:02d}", "task_001")
            print(f"Captured state: {screenshot_path}")
            
            # 2. Observe
            elements = await extract_interactive_elements(browser_manager.page)
            
            # 3. Think
            action = await brain.get_next_action(task, current_url, elements)
            print(f"Decided action: {action}")
            
            # 4. Act
            if action["type"] == "finish":
                print("Task completed.")
                break
            elif action["type"] == "click":
                await browser_manager.click(action["selector"])
            elif action["type"] == "type":
                await browser_manager.type(action["selector"], action["text"])
                # Often we need to press enter or click search after typing
                await browser_manager.press("Enter") 
            elif action["type"] == "navigate":
                await browser_manager.navigate(action["url"])
            
            await asyncio.sleep(2) # Pause for visual confirmation
            step += 1
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await browser_manager.stop()

if __name__ == "__main__":
    asyncio.run(main())
