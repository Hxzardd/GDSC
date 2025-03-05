import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

all_cogs = [
    'cogs.reminders',
    'cogs.polls',
    'cogs.gemini',
    'cogs.welcome',
    'cogs.help',
    'cogs.music'
]

async def main():
    for cogs in all_cogs:
        try:
            await bot.load_extension(cogs)
            print(f"Loaded cog '{cogs}'")
        except Exception as e:
            print(f"Failed to load cog {cogs}: {e}")
    await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
