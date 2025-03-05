import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

initial_extensions = [
    'cogs.reminders',
    'cogs.polls',
    'cogs.gemini',
    'cogs.welcome',
    'cogs.help',
    'cogs.music'
]

async def main():
    for ext in initial_extensions:
        try:
            await bot.load_extension(ext)
            print(f"Loaded extension '{ext}'")
        except Exception as e:
            print(f"Failed to load extension {ext}: {e}")
    await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
