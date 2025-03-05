# GDSC Bot

GDSC Bot is a feature-rich Discord bot designed for community engagement and productivity. It integrates several useful functions into a single, modular package, including:

- **Reminders:** Schedule and manage reminders with ease.
- **Polls:** Create and run interactive polls.
- **Gemini Chat:** Chat with an AI powered by Gemini for conversation and text summarization.
- **Welcome Messages:** Automatically welcome new members with custom messages.
- **Music Playback:** Play, queue, and control music streaming from YouTube, with additional options like bass boost and volume control.

This bot is built using discord.py (v2+) and employs a modular structure with separate cogs for each feature. All configuration and sensitive information is managed via environment variables.

## Setup Instructions

### 1. Clone the Repository
Clone the repository to your local machine:
```bash
git clone https://github.com/Hxzardd/GDSC.git
cd gdsc-bot
```

### 2. Create and Activate a Virtual Environment
```bash
python -m venv venv
```
Activate the virtual environment
 - Windows:
 ```bash
venv\Scripts\activate
```
 - macOS/Linux:
 ```bash
 source venv/bin/activate
 ```

### 3. Install Required Dependencies
Install all required packages using:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Rename the provided `.env-sample` to `.env` and update it with your credentials:
```bash
DISCORD_BOT_TOKEN=YOUR_DISCORD_BOT_TOKEN
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

### 5. Set Up FFmpeg
 - For Windows, follow https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/
 - For Linux, follow https://www.geeksforgeeks.org/how-to-install-ffmpeg-in-linux/
  - For macOS, follow https://phoenixnap.com/kb/ffmpeg-mac/

### 6. Run the Bot
Start the bot with:
```bash
python bot.py
```