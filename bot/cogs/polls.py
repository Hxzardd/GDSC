import discord
from discord.ext import commands
from datetime import datetime

class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_polls = {}  # key: poll message ID, value: poll data

    @commands.command()
    async def poll(self, ctx, *, message: str = None):
        """
        Create a poll.
        Usage: !poll Question | Option1 | Option2 | Option3
        """
        if not message:
            await ctx.send("Please use the correct format: !poll Question | Option1 | Option2 | Option3")
            return
        parts = message.split("|")
        if len(parts) < 2:
            await ctx.send("Invalid format! Use: !poll Question | Option1 | Option2 | Option3")
            return
        question = parts[0].strip()
        options = [opt.strip() for opt in parts[1:]]
        if len(options) > 10:
            await ctx.send("You can have a maximum of 10 options in a poll.")
            return
        reactions = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯"]
        poll_start_time = datetime.now()
        poll_timestamp = int(poll_start_time.timestamp())
        embed = discord.Embed(
            title=f"Poll: {question}",
            description="\n".join([f"{reactions[i]} **{opt}**" for i, opt in enumerate(options)]),
            color=discord.Color.blue(),
            timestamp=poll_start_time
        )
        embed.add_field(name="Started On:",
                        value=f"<t:{poll_timestamp}:F> (<t:{poll_timestamp}:R>)",
                        inline=False)
        embed.add_field(name="How to Vote:",
                        value="React with the corresponding emoji!",
                        inline=False)
        embed.set_footer(text=f"Poll created by {ctx.author.display_name}")
        poll_message = await ctx.send(embed=embed)
        for i in range(len(options)):
            await poll_message.add_reaction(reactions[i])
        self.active_polls[poll_message.id] = {
            "author": ctx.author.id,
            "question": question,
            "options": options,
            "message": poll_message,
            "votes": {opt: 0 for opt in options},
            "start_time": poll_start_time
        }

    @commands.command()
    async def closepoll(self, ctx, poll_id: int = None):
        """Close a poll. If no poll ID is provided, closes your most recent poll."""
        if not self.active_polls:
            await ctx.send("No active polls found.")
            return
        if poll_id is None:
            user_polls = [p_id for p_id, poll in self.active_polls.items() if poll["author"] == ctx.author.id]
            if not user_polls:
                await ctx.send("You have not created any polls.")
                return
            poll_id = user_polls[-1]
        poll = self.active_polls.get(poll_id)
        if not poll:
            await ctx.send(f"Poll with ID {poll_id} not found.")
            return
        if poll["author"] != ctx.author.id:
            await ctx.send("You can only close polls that you created.")
            return
        del self.active_polls[poll_id]
        await ctx.send(f"Poll {poll_id} has been closed.")

    @commands.command()
    async def pollresults(self, ctx, poll_id: int = None):
        """Display the results for a poll."""
        if not self.active_polls:
            await ctx.send("No active polls found.")
            return
        if poll_id is None:
            user_polls = [p_id for p_id, poll in self.active_polls.items() if poll["author"] == ctx.author.id]
            if not user_polls:
                await ctx.send("You have not created any polls.")
                return
            poll_id = user_polls[-1]
        poll = self.active_polls.get(poll_id)
        if not poll:
            await ctx.send(f"Poll with ID {poll_id} not found.")
            return
        results = "\n".join([f"{opt}: **{poll['votes'][opt]} votes**" for opt in poll["options"]])
        embed = discord.Embed(
            title=f"Poll Results: {poll['question']}",
            description=results,
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Update poll votes when a reaction is added."""
        if user.bot:
            return
        poll = self.active_polls.get(reaction.message.id)
        if not poll:
            return
        if reaction.emoji in ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯"]:
            index = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯"].index(reaction.emoji)
            option = poll["options"][index]
            poll["votes"][option] += 1

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        """Update poll votes when a reaction is removed."""
        if user.bot:
            return
        poll = self.active_polls.get(reaction.message.id)
        if not poll:
            return
        if reaction.emoji in ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯"]:
            index = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯"].index(reaction.emoji)
            option = poll["options"][index]
            poll["votes"][option] -= 1

async def setup(bot):
    await bot.add_cog(Polls(bot))
