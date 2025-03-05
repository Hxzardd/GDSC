import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

# Suppress yt-dlp bug report messages.
youtube_dl.utils.bug_reports_message = lambda: ''

# yt-dlp extraction options.
YTDL_OPTS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

# Default FFmpeg options.
FFMPEG_DEFAULT_OPTS = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(YTDL_OPTS)

class AudioSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, info, volume: float = 0.5):
        super().__init__(source, volume)
        self.info = info
        self.title = info.get('title')
        self.url = info.get('url')

    @classmethod
    async def create_source(cls, url: str, *, stream: bool = True, ffmpeg_opts: dict = None):
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        if ffmpeg_opts is None:
            ffmpeg_opts = FFMPEG_DEFAULT_OPTS
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_opts), info=data)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.track_queue = []  # Holds queued track URLs.
        self.volume_level = 0.5  # Default volume (50%).
        self.ffmpeg_opts = FFMPEG_DEFAULT_OPTS.copy()  # Allows bass adjustment.

    @commands.command(name='join', help="Join the voice channel you are in.")
    async def join(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("You must be in a voice channel to use this command.")
            return
        channel = ctx.author.voice.channel
        try:
            await channel.connect()
            await ctx.send(f"Joined {channel.name}.")
        except Exception as e:
            await ctx.send("Failed to join the voice channel.")
            print(e)

    @commands.command(name='leave', help="Disconnect from the voice channel.")
    async def leave(self, ctx):
        vc = ctx.guild.voice_client
        if vc and vc.is_connected():
            await vc.disconnect()
            await ctx.send("Disconnected from the voice channel.")
        else:
            await ctx.send("I am not connected to any voice channel.")

    @commands.command(name='play', help="Play audio from a URL. Usage: !play <url>")
    async def play(self, ctx, *, url: str):
        vc = ctx.guild.voice_client
        # Auto-join if not connected.
        if not vc:
            if ctx.author.voice and ctx.author.voice.channel:
                channel = ctx.author.voice.channel
                try:
                    vc = await channel.connect()
                    await ctx.send(f"Automatically joined {channel.name}.")
                except Exception as e:
                    await ctx.send("Unable to join your voice channel.")
                    return
            else:
                await ctx.send("You must be in a voice channel or use !join first.")
                return

        async with ctx.typing():
            try:
                source = await AudioSource.create_source(url, stream=True, ffmpeg_opts=self.ffmpeg_opts)
            except Exception as e:
                await ctx.send("Failed to extract audio. Please check your URL and try again.")
                print(e)
                return

            def after_play(error):
                coro = self._play_next(ctx)
                fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
                try:
                    fut.result()
                except Exception as exc:
                    print(f"Error scheduling next track: {exc}")

            vc.play(source, after=after_play)
        await ctx.send(f"Now playing: **{source.title}**.")

    async def _play_next(self, ctx):
        if self.track_queue:
            next_track = self.track_queue.pop(0)
            await self.play(ctx, url=next_track)

    @commands.command(name='enqueue', help="Add a track URL to the queue. Usage: !enqueue <url>")
    async def enqueue(self, ctx, *, url: str):
        self.track_queue.append(url)
        await ctx.send(f"Track added to the queue: `{url}`.")

    @commands.command(name='queue', help="Display the upcoming tracks in the queue.")
    async def show_queue(self, ctx):
        if not self.track_queue:
            await ctx.send("The queue is empty.")
        else:
            preview = "\n".join(f"{idx+1}. {track}" for idx, track in enumerate(self.track_queue[:5]))
            await ctx.send(f"Upcoming tracks:\n{preview}")

    @commands.command(name='pause', help="Pause the current track.")
    async def pause(self, ctx):
        vc = ctx.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await ctx.send("Playback paused.")
        else:
            await ctx.send("Nothing is playing right now.")

    @commands.command(name='resume', help="Resume the paused track.")
    async def resume(self, ctx):
        vc = ctx.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await ctx.send("Playback resumed.")
        else:
            await ctx.send("No track is paused.")

    @commands.command(name='skip', help="Skip the current track.")
    async def skip(self, ctx):
        vc = ctx.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await ctx.send("Skipped the current track.")
        else:
            await ctx.send("Nothing is playing to skip.")

    @commands.command(name='stop', help="Stop playback and clear the queue.")
    async def stop(self, ctx):
        vc = ctx.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            self.track_queue.clear()
            await ctx.send("Playback stopped and the queue cleared.")
        else:
            await ctx.send("Nothing is playing at the moment.")

    @commands.command(name='volume', help="Set the playback volume (0-100).")
    async def volume(self, ctx, volume: int):
        vc = ctx.guild.voice_client
        if vc is None:
            await ctx.send("I am not in a voice channel.")
            return
        if not 0 <= volume <= 100:
            await ctx.send("Volume must be between 0 and 100.")
            return
        self.volume_level = volume / 100
        if vc.source:
            vc.source.volume = self.volume_level
        await ctx.send(f"Volume set to {volume}%.")

    @commands.command(name='bass', help="Set bass boost level. Usage: !bass <gain> (0 disables bass boost)")
    async def bass(self, ctx, gain: int):
        if gain < 0:
            await ctx.send("Gain cannot be negative.")
            return
        if gain == 0:
            self.ffmpeg_opts['options'] = "-vn"
            await ctx.send("Bass boost disabled.")
        else:
            self.ffmpeg_opts['options'] = f'-vn -af "bass=g={gain}"'
            await ctx.send(f"Bass boost set to {gain}.")
        # This setting will affect tracks played after this command.

async def setup(bot):
    await bot.add_cog(Music(bot))
