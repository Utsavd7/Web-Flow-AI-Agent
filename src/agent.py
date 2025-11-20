import os
import json
from typing import List, Dict, Any
from openai import AsyncOpenAI

class AgentBrain:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None

    async def get_next_action(self, goal: str, page_url: str, interactive_elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        print(f"Thinking about goal: {goal}")
        print(f"Current URL: {page_url}")
        
        # 1. Try LLM if available
        if self.client:
            try:
                prompt = self._construct_prompt(goal, page_url, interactive_elements)
                response = await self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a web navigation agent. Output only JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                action = json.loads(response.choices[0].message.content)
                return action
            except Exception as e:
                print(f"LLM Error: {e}. Falling back to heuristics.")

        # 2. Fallback Heuristics (for demo/testing without API key)
        
        # GitHub
        if "github.com" in page_url:
            if "search" in goal.lower():
                if "search" not in page_url:
                    # Try to find the search button or input
                    for el in interactive_elements:
                        # GitHub often has a button that opens a modal
                        aria_label = el.get("attributes", {}).get("ariaLabel")
                        if (aria_label and "Search" in aria_label) or \
                           "search-input" in el.get("selector", ""):
                            return {"type": "click", "selector": el["selector"]}
                        
                        # If we see the input directly
                        if "query-builder-test" in el.get("attributes", {}).get("id", ""):
                             return {"type": "type", "selector": el["selector"], "text": "AutoGPT"}
                    
                    # Fallback: Navigate to search page
                    return {"type": "navigate", "url": "https://github.com/search?q=AutoGPT"}
                else:
                     return {"type": "finish"}

            if "issues" in goal.lower():
                if "/issues" in page_url:
                    return {"type": "finish"}
                for el in interactive_elements:
                    if "Issues" in el.get("text", "") and "tab" in el.get("selector", "").lower():
                         return {"type": "click", "selector": el["selector"]}

        # Python.org (Replaces StackOverflow)
        if "python.org" in page_url:
            if "search" in goal.lower():
                if "search" not in page_url:
                    for el in interactive_elements:
                        if "q" == el.get("attributes", {}).get("name", "") or "search" in el.get("attributes", {}).get("id", ""):
                            return {"type": "type", "selector": el["selector"], "text": "PEP 8"}
                else:
                    return {"type": "finish"}

        # Hacker News
        if "news.ycombinator.com" in page_url:
            if "show hn" in goal.lower():
                if "show" in page_url:
                    return {"type": "finish"}
                for el in interactive_elements:
                    if "Show" in el.get("text", ""): # Relaxed match
                        return {"type": "click", "selector": el["selector"]}

        # Default: Finish if stuck
        return {"type": "finish"}

    def _construct_prompt(self, goal, url, elements):
        # Simplify elements to save tokens
        simplified_elements = []
        for el in elements:
            simplified_elements.append({
                "tag": el["tagName"],
                "text": el["text"][:50],
                "selector": el["selector"],
                "id": el.get("attributes", {}).get("id", "")
            })
            
        return f"""
        Goal: {goal}
        Current URL: {url}
        
        Available Elements:
        {json.dumps(simplified_elements[:50], indent=2)} # Limit to 50 elements for context window
        
        Decide the next action. Return a JSON object with one of the following structures:
        - {{"type": "click", "selector": "..."}}
        - {{"type": "type", "selector": "...", "text": "..."}}
        - {{"type": "navigate", "url": "..."}}
        - {{"type": "finish"}}
        """
