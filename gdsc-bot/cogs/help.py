import discord
from discord.ext import commands
import asyncio

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", help="Show interactive help for all commands.")
    async def interactive_help(self, ctx):
        pages = []

        # Page 1: Main Menu / Overview
        embed_main = discord.Embed(
            title="🤖 Bot Help - Main Menu",
            description="Welcome! Use the arrow reactions to navigate through the help pages.",
            color=discord.Color.blurple()
        )
        embed_main.add_field(
            name="Categories",
            value=(
                "🔹 **Reminders**\n"
                "🔹 **Polls**\n"
                "🔹 **Gemini Chat**\n"
                "🔹 **Welcome**\n"
                "🔹 **Music**\n\n"
                "React with ▶️ to see more details."
            ),
            inline=False
        )
        pages.append(embed_main)

        # Page 2: Reminders
        embed_reminders = discord.Embed(
            title="🕒 Reminders Help",
            description="Manage your reminders with these commands:",
            color=discord.Color.blurple()
        )
        embed_reminders.add_field(
            name="!remind DD-MM-YYYY HH:MM message",
            value="Set a reminder at the specified date/time.",
            inline=False
        )
        embed_reminders.add_field(
            name="!modify <index> DD-MM-YYYY HH:MM message",
            value="Modify an existing reminder.",
            inline=False
        )
        embed_reminders.add_field(
            name="!cancelreminder [index]",
            value="Cancel a specific reminder or all reminders if no index is provided.",
            inline=False
        )
        embed_reminders.add_field(
            name="!reminderslist",
            value="List all your active reminders.",
            inline=False
        )
        pages.append(embed_reminders)

        # Page 3: Polls
        embed_polls = discord.Embed(
            title="📊 Polls Help",
            description="Create and manage polls with these commands:",
            color=discord.Color.blurple()
        )
        embed_polls.add_field(
            name="!poll Question | Option1 | Option2 | ...",
            value="Create a poll with up to 10 options.",
            inline=False
        )
        embed_polls.add_field(
            name="!closepoll [poll_id]",
            value="Close your most recent poll or a specific poll by ID.",
            inline=False
        )
        embed_polls.add_field(
            name="!pollresults [poll_id]",
            value="Display the results of a poll.",
            inline=False
        )
        pages.append(embed_polls)

        # Page 4: Gemini Chat
        embed_gemini = discord.Embed(
            title="💬 Gemini Chat Help",
            description="Interact with the bot using Gemini AI:",
            color=discord.Color.blurple()
        )
        embed_gemini.add_field(
            name="!chat message",
            value="Chat with the bot using a text prompt.",
            inline=False
        )
        embed_gemini.add_field(
            name="!summarize text",
            value="Get a concise summary of a long text.",
            inline=False
        )
        embed_gemini.add_field(
            name="!forget",
            value="Clear the conversation history for this channel/thread.",
            inline=False
        )
        embed_gemini.add_field(
            name="DM or Mention",
            value="You can also DM or mention the bot to start a conversation.",
            inline=False
        )
        pages.append(embed_gemini)

        # Page 5: Welcome
        embed_welcome = discord.Embed(
            title="🎉 Welcome Help",
            description="Configure and view welcome settings:",
            color=discord.Color.blurple()
        )
        embed_welcome.add_field(
            name="!setwelcome #channel",
            value="Set the channel where new members will be welcomed.",
            inline=False
        )
        embed_welcome.add_field(
            name="!editwelcome <message>",
            value=(
                "Edit the welcome message. Use `{member}` for the new member mention and `{server}` for the server name.\n"
                "Example: `!editwelcome Welcome {member} to {server}! Enjoy your stay.`"
            ),
            inline=False
        )
        embed_welcome.add_field(
            name="!welcomesettings",
            value="View the current welcome settings.",
            inline=False
        )
        pages.append(embed_welcome)

        # Page 6: Music
        embed_music = discord.Embed(
            title="🎶 Music Help",
            description="Control music playback with these commands:",
            color=discord.Color.blurple()
        )
        embed_music.add_field(
            name="!join",
            value="Join the voice channel you are in.",
            inline=False
        )
        embed_music.add_field(
            name="!leave",
            value="Disconnect from the voice channel.",
            inline=False
        )
        embed_music.add_field(
            name="!stream <url>",
            value="Play a track from a URL immediately (auto-joins if necessary).",
            inline=False
        )
        embed_music.add_field(
            name="!enqueue <url>",
            value="Add a track to the queue.",
            inline=False
        )
        embed_music.add_field(
            name="!queue",
            value="Show the upcoming tracks in the queue.",
            inline=False
        )
        embed_music.add_field(
            name="!pause / !resume",
            value="Pause or resume playback.",
            inline=False
        )
        embed_music.add_field(
            name="!skip",
            value="Skip the current track.",
            inline=False
        )
        embed_music.add_field(
            name="!stop",
            value="Stop playback and clear the queue.",
            inline=False
        )
        embed_music.add_field(
            name="!volume <0-100>",
            value="Set the playback volume.",
            inline=False
        )
        embed_music.add_field(
            name="!bass <gain>",
            value="Set the bass boost level (use 0 to disable).",
            inline=False
        )
        pages.append(embed_music)

        current_page = 0
        help_msg = await ctx.send(embed=pages[current_page])
        await help_msg.add_reaction("◀️")
        await help_msg.add_reaction("▶️")
        await help_msg.add_reaction("❌")

        def check(reaction, user):
            return (
                user == ctx.author and str(reaction.emoji) in ["◀️", "▶️", "❌"]
                and reaction.message.id == help_msg.id
            )

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                if str(reaction.emoji) == "▶️":
                    current_page = (current_page + 1) % len(pages)
                    await help_msg.edit(embed=pages[current_page])
                    await help_msg.remove_reaction(reaction, user)
                elif str(reaction.emoji) == "◀️":
                    current_page = (current_page - 1) % len(pages)
                    await help_msg.edit(embed=pages[current_page])
                    await help_msg.remove_reaction(reaction, user)
                elif str(reaction.emoji) == "❌":
                    await help_msg.delete()
                    break
            except asyncio.TimeoutError:
                try:
                    await help_msg.clear_reactions()
                except Exception:
                    pass
                break

async def setup(bot):
    await bot.add_cog(Help(bot))
