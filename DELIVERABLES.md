# Project Deliverables Checklist

This document maps the project outputs to the requirements specified in the prompt.

## 1. Code - Your UI state capture system
**Status**: ✅ Complete
- **Location**: `src/`
- **Components**:
    - `browser_manager.py`: Handles Playwright navigation (1080p).
    - `capture.py`: Captures screenshots and **rich metadata** (JSON).
    - `agent.py`: Supports real LLM (OpenAI) and robust heuristics for technical sites.
    - `main.py` & `generate_dataset.py`: Runners for the system.
    - `combine_videos.py` & `visualize_logs.py`: Utilities for split-screen demo creation.

## 2. Loom - A short loom where you show the agent running
**Status**: ✅ Complete
- **Description**: A **Split-Screen Demo** (`combined_workflow.mp4`) that demonstrates the agent in action:
    -   **Left**: The Browser interacting with the website.
    -   **Right**: The "Agent Brain" (Terminal) showing real-time logs and decisions.
-   **Location**: `captured_workflows/combined_workflow.mp4`
-   **Usage**: This video serves as a comprehensive demonstration of the agent's capabilities.

## 3. Dataset - Captured UI states for 4 tasks
**Status**: ✅ Complete & Optimized
- **Location**: `captured_workflows/`
- **Optimization**: Screenshots captured every 2nd step to reduce clutter, plus start/finish states.
- **Tasks Captured**:
    1. **GitHub Search**: Search for "AutoGPT" on GitHub.
    2. **GitHub Issues**: Navigate to the Issues tab of a repo.
    3. **Python.org Search**: Search for "PEP 8" on Python.org.
    4. **Hacker News**: Navigate to "Show HN".
- **Format**: Organized by task folder, containing:
    - `step_XX.png`: Screenshot.
    - `step_XX_metadata.json`: URL and Action taken.
    - `logs.json`: Full execution logs.

## How to Verify
1. **Run the Code**:
   ```bash
   source venv/bin/activate
   python -m src.generate_dataset
   ```
2. **Check the Output**:
   - Open `captured_workflows/combined_workflow.mp4` to see the split-screen demo.
   - Browse task folders for screenshots and metadata.
