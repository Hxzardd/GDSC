# cogs/reminders.py
import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
from utils.utils import load_reminders, save_reminders, parse_reminder_time

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminder_data = load_reminders()  # persistent storage
        self.reminders = {}  # in-memory tasks, keyed by user ID

    def save_data(self):
        save_reminders(self.reminder_data)

    async def handle_reminder(self, user_id, time_seconds, message, channel, index):
        """Wait for the specified duration then send the reminder."""
        await asyncio.sleep(time_seconds)
        await channel.send(f"⏰ Reminder for <@{user_id}>: {message}")
        user_key = str(user_id)
        if user_key in self.reminder_data and index < len(self.reminder_data[user_key]):
            del self.reminder_data[user_key][index]
            if not self.reminder_data[user_key]:
                del self.reminder_data[user_key]
            self.save_data()
        if user_key in self.reminders and index in self.reminders[user_key]:
            del self.reminders[user_key][index]

    @commands.command()
    async def remind(self, ctx, date: str, time: str, *, message: str):
        """
        Set a reminder.
        Usage: !remind DD-MM-YYYY HH:MM Your reminder message
        Example: !remind 05-03-2025 19:13 Hello
        """
        datetime_str = f"{date} {time}"
        result = parse_reminder_time(datetime_str)
        if result[0] is None:
            await ctx.send(result[1])
            return
        time_seconds, reminder_dt = result
        trigger_time = int(reminder_dt.timestamp())
        user_key = str(ctx.author.id)
        if user_key not in self.reminder_data:
            self.reminder_data[user_key] = []
        index = len(self.reminder_data[user_key])
        task = asyncio.create_task(self.handle_reminder(ctx.author.id, time_seconds, message, ctx.channel, index))
        self.reminders.setdefault(user_key, {})[index] = task
        self.reminder_data[user_key].append({
            "time": time_seconds,
            "trigger_time": trigger_time,
            "message": message,
            "channel_id": ctx.channel.id
        })
        self.save_data()
        await ctx.send(f"✅ Reminder set for {datetime_str}: {message}")

    @commands.command()
    async def modify(self, ctx, reminder_index: int, date: str, time: str, *, message: str):
        """
        Modify an existing reminder.
        Usage: !modify <index> DD-MM-YYYY HH:MM <new message>
        """
        user_key = str(ctx.author.id)
        if user_key not in self.reminder_data or reminder_index < 1 or reminder_index > len(self.reminder_data[user_key]):
            await ctx.send("❌ Invalid reminder index! Use !reminderslist to check your reminders.")
            return
        datetime_str = f"{date} {time}"
        result = parse_reminder_time(datetime_str)
        if result[0] is None:
            await ctx.send(result[1])
            return
        time_seconds, reminder_dt = result
        new_trigger_time = int(reminder_dt.timestamp())
        reminder_index -= 1  # convert to 0-based index
        self.reminders[user_key][reminder_index].cancel()
        task = asyncio.create_task(self.handle_reminder(ctx.author.id, time_seconds, message, ctx.channel, reminder_index))
        self.reminders[user_key][reminder_index] = task
        self.reminder_data[user_key][reminder_index] = {
            "time": time_seconds,
            "trigger_time": new_trigger_time,
            "message": message,
            "channel_id": ctx.channel.id
        }
        self.save_data()
        await ctx.send(f"✏️ Reminder modified: {message} set for {datetime_str}.")

    @commands.command()
    async def cancelreminder(self, ctx, reminder_index: int = None):
        """
        Cancel a specific reminder, or all reminders if no index is provided.
        """
        user_key = str(ctx.author.id)
        if user_key not in self.reminder_data:
            await ctx.send("❌ You have no active reminders.")
            return
        if reminder_index is None:
            for task in self.reminders[user_key].values():
                task.cancel()
            del self.reminders[user_key]
            del self.reminder_data[user_key]
            self.save_data()
            await ctx.send("🗑️ All reminders canceled.")
        else:
            reminder_index -= 1  # convert to 0-based index
            if reminder_index < 0 or reminder_index >= len(self.reminder_data[user_key]):
                await ctx.send("❌ Invalid reminder index! Use !reminderslist to check your reminders.")
                return
            self.reminders[user_key][reminder_index].cancel()
            del self.reminders[user_key][reminder_index]
            del self.reminder_data[user_key][reminder_index]
            self.save_data()
            await ctx.send(f"🗑️ Reminder {reminder_index + 1} canceled.")

    @commands.command()
    async def reminderslist(self, ctx):
        """List all your active reminders with human-readable time left."""
        user_key = str(ctx.author.id)
        if user_key not in self.reminder_data or not self.reminder_data[user_key]:
            await ctx.send("📭 You have no active reminders.")
            return
        embed = discord.Embed(title="📝 Your Active Reminders", color=discord.Color.blue())
        for idx, reminder in enumerate(self.reminder_data[user_key], start=1):
            trigger_time = reminder.get("trigger_time")
            if not trigger_time:
                from datetime import timedelta
                trigger_time = int((datetime.now() + timedelta(seconds=reminder["time"])).timestamp())
            time_left = f"<t:{trigger_time}:R>"
            embed.add_field(name=f"{idx}. {reminder['message']}",
                            value=f"⏳ Time left: {time_left}",
                            inline=False)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        # Restart pending reminders on bot startup
        for user_key, user_reminders in self.reminder_data.items():
            self.reminders.setdefault(user_key, {})
            for idx, reminder in enumerate(user_reminders):
                channel = self.bot.get_channel(reminder["channel_id"])
                task = asyncio.create_task(
                    self.handle_reminder(int(user_key), reminder["time"], reminder["message"], channel, idx)
                )
                self.reminders[user_key][idx] = task

async def setup(bot):
    await bot.add_cog(Reminders(bot))
