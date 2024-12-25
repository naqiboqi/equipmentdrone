import asyncio
import discord
import time

from cogs.video import Video

class Player:
    """Assigned to each server currently using the bot.
    
    Is created when the bot joins a voice channel, and is destroyed when
    the bot leaves the voice channel.
    """
    def __init__(self, ctx):
        self.bot = ctx.bot
        self.channel = ctx.channel
        self.cog = ctx.cog
        self.ctx = ctx
        self.guild = ctx.guild
        self.next = asyncio.Event()
        self.queue = asyncio.Queue()
        
        self.current: Video = None
        self.now_playing_embed: discord.Embed = None
        self.queue_embed: discord.Embed = None
        self.loop = False
        self.paused = False
        self.volume = .25
        
        ctx.bot.loop.create_task(self.player_loop())
        
        
    async def timer(self, start_time: float):
        """Keeps track of the video's runtime, and calls update_player_details()
        with the current time.
        
        Additionally keeps track of whether or not the video is paused.
        """
        paused_time = 0.00
        while True:
            await asyncio.sleep(1.00)
            if self.guild.voice_client.is_playing():
                elapsed_time = time.perf_counter() - (start_time + paused_time)
                await self.update_player_details(elapsed_time)
                
            elif self.paused:
                paused_time += 1.00
            else:
                # Case for when the video is finished playing
                elapsed_time = time.perf_counter() - (start_time + paused_time)
                await self.update_player_details(elapsed_time)
                break    
            
    async def show_player_details(self):
        """Creates and sends an embed showing the current details of the player:
        
        * The current video title and link
        * The progress bar
        * The current volume
        * The user who requested the video
        
        If the embed already exists, updates the current embed.
        """
        now_playing_embed = await self.current.display()
        try:
            self.now_playing_embed = await self.now_playing_embed.edit(embed=now_playing_embed)
        except:
            self.now_playing_embed = await self.channel.send(embed=now_playing_embed)
        
    async def update_player_details(self, elapsed_time: float):
        """Updates the currently existed embed."""
        now_playing_embed = await self.current.display(elapsed_time)
        await self.now_playing_embed.edit(embed=now_playing_embed)
        
    async def add_to_front_queue(self, new_source: Video):
        """Adds a source to the front of the queue."""
        if not isinstance(new_source, Video):
            raise TypeError("Source must be an instance of Video.")

        queue = asyncio.Queue()
        await queue.put(new_source)
        
        while not self.queue.empty():
            source = await self.queue.get()
            await queue.put(source)
            
        self.queue = queue

    async def player_loop(self):
        """The main loop for the media player.
        Runs as long as the bot is in a voice channel.
        """
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()
            try:
                async with asyncio.timeout(1200):
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self.guild)
            except asyncio.exceptions.CancelledError:
                return self.destroy(self.guild) 

            if not isinstance(source, Video):
                try:
                    source = await Video.prepare_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self.channel.send(F"There was an error processing your song.")
                    print(F"Error processing song {e}")
                    continue
            
            start_time = time.perf_counter() - source.seeked_time
            await source.start(start_time, self.volume)
            
            self.current = source
            self.guild.voice_client.play(
                source, 
                after=lambda song:self.bot.loop.call_soon_threadsafe(self.next.set))
            
            await self.show_player_details()      
            await self.timer(self.current.start_time)

            source.cleanup()
            self.current = None

    def destroy(self, guild):
        """Disconnects and cleans the player.
        Useful if there is a timeout, or if the bot is no longer playing.
        """
        print("Destroying player instance.")
        return self.bot.loop.create_task(self.cog.cleanup(guild, None))
