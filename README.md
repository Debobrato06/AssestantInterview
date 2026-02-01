# AI Interview Assistant 🤖

This project helps you during interviews by listening to the interviewer and providing real-time answers using ChatGPT (GPT-4o).

## Features
- **Real-time Speech-to-Text**: Captures interviewer questions.
- **ChatGPT Integration**: Generates professional answers instantly.
- **Floating UI**: A modern, semi-transparent overlay that stays on top of your Google Meet or Zoom window.
- **Draggable Window**: Move it anywhere on your screen.

## Installation

1. Install Python 3.10+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your OpenAI API key in the `.env` file:
   ```
   OPENAI_API_KEY=your_actual_key_here
   ```

## How to capture Interviewer Audio (Windows)

To hear the interviewer (system sound) instead of just your microphone:
1. Right-click the **Sound icon** in taskbar -> **Sounds**.
2. Go to the **Recording** tab.
3. Right-click in the list and select **"Show Disabled Devices"**.
4. Enable **"Stereo Mix"**.
5. Set **Stereo Mix** as the default device or the app will try to detect it automatically.

## Running the App
```bash
python main.py
```

## Disclaimer
Use this responsibly. This tool is meant for preparation and technical assistance.
