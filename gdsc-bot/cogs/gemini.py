import discord
from discord.ext import commands
import google.generativeai as genai
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

text_generation_config = {"temperature": 0.9, "top_p": 1, "top_k": 1}
safety_settings = []
bot_template = [
    {"role": "user", "parts": ["Hi!"]},
    {"role": "model", "parts": ["Hello! I am a Discord bot."]},
    {"role": "user", "parts": ["Please give short and concise answers."]},
    {"role": "model", "parts": ["Sure, I'll keep it brief."]}
]
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=text_generation_config,
    safety_settings=safety_settings
)
# Store conversation context per channel/thread
message_history = {}

async def generate_response(channel_id: int, prompt: str) -> str:
    if channel_id not in message_history:
        message_history[channel_id] = model.start_chat(history=bot_template)
    response = await message_history[channel_id].send_message_async(prompt)
    return response.text

class Gemini(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def chat(self, ctx, *, prompt: str):
        """
        Chat with the bot using Gemini AI.
        Usage: !chat Your message here
        """
        try:
            async with ctx.typing():
                response_text = await generate_response(ctx.channel.id, prompt)
                await ctx.send(response_text)
        except Exception as e:
            await ctx.send("An error occurred while processing your request.")

    @commands.command()
    async def summarize(self, ctx, *, text: str):
        """
        Summarize the given text using Gemini AI.
        Usage: !summarize Text to be summarized
        """
        summary_prompt = f"Please provide a concise summary of the following text:\n\n{text}"
        try:
            async with ctx.typing():
                response_text = await generate_response(ctx.channel.id, summary_prompt)
                await ctx.send(response_text)
        except Exception as e:
            await ctx.send("An error occurred while summarizing the text.")

    @commands.command()
    async def forget(self, ctx):
        """
        Clear the AI conversation history for this channel/thread.
        Usage: !forget
        """
        channel_id = ctx.channel.id
        if channel_id in message_history:
            message_history.pop(channel_id)
            await ctx.send("💭 I have forgotten the conversation history for this channel.")
        else:
            await ctx.send("💭 There was no conversation history to forget.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore commands and messages from the bot
        if message.author == self.bot.user or message.content.startswith("!"):
            return
        # Auto-respond in DMs or if the bot is mentioned
        if isinstance(message.channel, discord.DMChannel) or self.bot.user in message.mentions:
            try:
                async with message.channel.typing():
                    prompt = message.clean_content
                    # Remove bot mentions from the prompt.
                    for mention in message.mentions:
                        if mention == self.bot.user:
                            prompt = prompt.replace(mention.mention, "").strip()
                    if not prompt:
                        return
                    response_text = await generate_response(message.channel.id, prompt)
                    await message.channel.send(response_text)
            except Exception as e:
                await message.channel.send("An error occurred while processing your message.")

async def setup(bot):
    await bot.add_cog(Gemini(bot))
