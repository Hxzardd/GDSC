import discord
from discord.ext import commands
import google.generativeai as genai
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure the Gemini SDK with your API key.
genai.configure(api_key=GEMINI_API_KEY)

# Settings for text generation.
text_generation_config = {"temperature": 0.9, "top_p": 1, "top_k": 1}
safety_settings = []

# A template to prime the conversation context.
bot_template = [
    {"role": "user", "parts": ["Hi!"]},
    {"role": "model", "parts": ["Hello! I am a Discord bot."]},
    # {"role": "user", "parts": ["Please give concise answers."]},
    # {"role": "model", "parts": ["Sure, I'll keep it brief."]}
]

# Create a Gemini GenerativeModel instance.
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=text_generation_config,
    safety_settings=safety_settings
)

# Maximum length for Discord messages.
DISCORD_MAX_MESSAGE_LENGTH = 2000
ERROR_MESSAGE = "There was an issue processing your request. Please try again."

# Dictionary to store conversation context per channel.
message_history = {}

async def generate_response(channel_id: int, prompt: str) -> str:
    """
    Generate a response using the Gemini AI model based on the conversation context.
    If no context exists for the channel, a new session is started with a predefined template.
    """
    if channel_id not in message_history:
        message_history[channel_id] = model.start_chat(history=bot_template)
    try:
        response = await message_history[channel_id].send_message_async(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating response: {e}")
        raise e

async def send_message_in_chunks(destination, message: str):
    """
    Sends a long message in chunks to respect Discord's message length limit.
    """
    while message:
        # Get the first 2000 characters (or less) from the message.
        chunk = message[:DISCORD_MAX_MESSAGE_LENGTH]
        message = message[DISCORD_MAX_MESSAGE_LENGTH:]
        await destination.send(chunk)

class Gemini(commands.Cog):
    """
    A cog to handle interactions with the Gemini AI.
    This includes commands to chat and summarize, and it automatically responds in DMs or when mentioned.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def chat(self, ctx, *, prompt: str):
        """
        Chat with the bot using Gemini AI.
        Usage: !chat <your message>
        """
        try:
            async with ctx.typing():
                response_text = await generate_response(ctx.channel.id, prompt)
            await send_message_in_chunks(ctx, response_text)
        except Exception as e:
            await ctx.send(ERROR_MESSAGE)

    @commands.command()
    async def summarize(self, ctx, *, text: str):
        """
        Summarize the given text using Gemini AI.
        Usage: !summarize <text to summarize>
        """
        summary_prompt = f"Please provide a concise summary of the following text:\n\n{text}"
        try:
            async with ctx.typing():
                response_text = await generate_response(ctx.channel.id, summary_prompt)
            await send_message_in_chunks(ctx, response_text)
        except Exception as e:
            await ctx.send(ERROR_MESSAGE)

    @commands.command()
    async def forget(self, ctx):
        """
        Clear the conversation history for this channel.
        Usage: !forget
        """
        channel_id = ctx.channel.id
        if channel_id in message_history:
            message_history.pop(channel_id)
            await ctx.send("Conversation history cleared for this channel.")
        else:
            await ctx.send("No conversation history to clear.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Automatically respond to messages in DMs or when the bot is mentioned.
        Commands (starting with '!') and the bot's own messages are ignored.
        """
        if message.author == self.bot.user or message.content.startswith("!"):
            return
        if isinstance(message.channel, discord.DMChannel) or self.bot.user in message.mentions:
            try:
                async with message.channel.typing():
                    prompt = message.clean_content
                    # Remove bot mention(s) from the prompt.
                    for mention in message.mentions:
                        if mention == self.bot.user:
                            prompt = prompt.replace(mention.mention, "").strip()
                    if not prompt:
                        return
                    response_text = await generate_response(message.channel.id, prompt)
                    await send_message_in_chunks(message.channel, response_text)
            except Exception as e:
                await message.channel.send(ERROR_MESSAGE)

async def setup(bot):
    await bot.add_cog(Gemini(bot))
