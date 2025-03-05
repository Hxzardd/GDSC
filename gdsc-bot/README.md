# GDSC Bot

GDSC Bot is a modular Discord bot featuring powerful utilities and interactive commands. It comes with a variety of features including:

- **Reminders:** Set, modify, cancel, and view reminders.
- **Polls:** Create, close, and view poll results.
- **Gemini Chat:** Chat with an AI (Gemini) and get concise summaries.
- **Welcome Messages:** Automatically welcome new members and customize the welcome channel/message.
- **Music Playback:** Play, queue, skip, and adjust music from YouTube (or search by song name).

## Features Overview

### Reminders
- **!remind DD-MM-YYYY HH:MM message**  
  Set a reminder for a future date and time.
- **!modify \<index> DD-MM-YYYY HH:MM message**  
  Modify an existing reminder.
- **!cancelreminder [index]**  
  Cancel a specific reminder or all reminders.
- **!reminderslist**  
  List all active reminders with human-friendly time left.

### Polls
- **!poll Question | Option1 | Option2 | ...**  
  Create a poll with up to 10 options.
- **!closepoll [poll_id]**  
  Close your most recent (or specified) poll.
- **!pollresults [poll_id]**  
  Display the results of a poll.

### Gemini Chat
- **!chat Your message**  
  Chat with the Gemini AI-powered bot.
- **!summarize Text to summarize**  
  Receive a concise summary of a long text.
- **!forget**  
  Clear the conversation history for the current channel.
- *Also, the bot auto-responds to DMs or when mentioned (excluding commands).*

### Welcome Messages
- **!setwelcome #channel**  
  Set the channel where new members will be welcomed.
- **!editwelcome \<message>**  
  Customize the welcome message.  
  Use placeholders:  
  - `{member}` for the new member mention  
  - `{server}` for the server name  
  *Example:* `!editwelcome Welcome {member} to {server}! Enjoy your stay.`
- **!welcomesettings**  
  View the current welcome settings.

### Music Playback
- **!join**  
  Join the voice channel you are in.
- **!leave**  
  Disconnect from the voice channel.
- **!play <url or song name>**  
  Play audio from a URL or by searching YouTube.
- **!enqueue <url>**  
  Add a track to the queue.
- **!queue**  
  Display upcoming tracks in the queue.
- **!pause / !resume**  
  Pause or resume the current track.
- **!skip**  
  Skip the current track.
- **!stop**  
  Stop playback and clear the queue.
- **!volume <0-100>**  
  Set the playback volume.
- **!bass <gain>**  
  Set the bass boost level (use 0 to disable).

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/gdsc-bot.git
cd gdsc-bot
