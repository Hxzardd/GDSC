import discord
from discord.ext import commands
import json
import os

WELCOME_FILE = "welcome.json"

def load_welcome():
    """Load welcome settings from the JSON file."""
    if os.path.exists(WELCOME_FILE):
        try:
            with open(WELCOME_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_welcome(data):
    """Save welcome settings to the JSON file."""
    with open(WELCOME_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_data = load_welcome()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """When a new member joins, send the welcome message in the configured channel."""
        guild = member.guild
        guild_id = str(guild.id)
        if guild_id in self.welcome_data:
            channel_id = self.welcome_data[guild_id].get("channel_id")
            message = self.welcome_data[guild_id].get(
                "message",
                "Welcome to {server}, {member}! Enjoy your stay."
            )
            channel = guild.get_channel(channel_id)
            if channel:
                # Replace placeholders in the message.
                welcome_message = message.replace("{member}", member.mention)\
                                         .replace("{server}", guild.name)
                await channel.send(welcome_message)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setwelcome(self, ctx, channel: discord.TextChannel):
        """
        Set the welcome channel.
        
        **Usage:** `!setwelcome #channel`
        
        **Example:** `!setwelcome #welcome`
        
        This command sets the channel where new members will be welcomed.
        """
        guild_id = str(ctx.guild.id)
        if guild_id not in self.welcome_data:
            self.welcome_data[guild_id] = {}
        self.welcome_data[guild_id]["channel_id"] = channel.id
        save_welcome(self.welcome_data)
        await ctx.send(f"✅ Welcome channel set to {channel.mention}.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def editwelcome(self, ctx, *, message: str):
        """
        Edit the welcome message.
        
        **Usage:** `!editwelcome <message>`
        
        **Example:** `!editwelcome Welcome {member} to {server}! Enjoy your stay.`
        
        **Formatting Instructions:**
        - Use `{member}` to include a mention of the new member.
        - Use `{server}` to include the server's name.
        You can also include emojis and other text.
        """
        guild_id = str(ctx.guild.id)
        if guild_id not in self.welcome_data:
            self.welcome_data[guild_id] = {}
        self.welcome_data[guild_id]["message"] = message
        save_welcome(self.welcome_data)
        await ctx.send("✅ Welcome message updated.")

    @commands.command()
    async def welcomesettings(self, ctx):
        """
        Display the current welcome settings for this server.
        
        **Usage:** `!welcomesettings`
        """
        guild_id = str(ctx.guild.id)
        if guild_id not in self.welcome_data:
            await ctx.send("No welcome settings found for this server.")
        else:
            channel_id = self.welcome_data[guild_id].get("channel_id")
            message = self.welcome_data[guild_id].get("message", "Not set")
            channel = ctx.guild.get_channel(channel_id)
            channel_mention = channel.mention if channel else "Channel not found"
            embed = discord.Embed(
                title="Welcome Settings",
                color=discord.Color.blurple()
            )
            embed.add_field(name="Welcome Channel", value=channel_mention, inline=False)
            embed.add_field(name="Welcome Message", value=message, inline=False)
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
