import aiohttp
import asyncio
import os
import subprocess
import wavelink

from discord.ext import commands


PORT = os.getenv('LAVALINK_PORT')
PASSWORD = os.getenv("LAVALINK_PASSWORD")



class WavelinkController(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.lava: subprocess.Popen = None

    async def cog_load(self):
        self.lava = self.start_lavalink()
        await self.ping()
        await self.connect()

    def start_lavalink(self):
        env = os.environ.copy()
        env["LAVALINK_PORT"] = PORT
        env["LAVALINK_PASSWORD"] = PASSWORD
        print("Starting Lavalink server...")
        lava = subprocess.Popen(["java", "-jar", "Lavalink.jar"], env=env)

        return lava

    async def ping(self):
        uri = f"http://localhost:{PORT}/version"
        headers = {"Authorization": PASSWORD}

        async with aiohttp.ClientSession() as session:
            for _ in range(10):
                await asyncio.sleep(5)

                print("Waiting for Lavalink to be ready....\n")
                try:
                    async with session.get(uri, headers=headers, timeout=5) as response:
                        if response.status == 200:
                            print("Lavalink is ready!\n")
                            return
                except aiohttp.ClientError as e:
                    print(f"Not ready: {e}. Retrying....\n")

    async def connect(self):
        print(PORT)
        print(PASSWORD)
        uri = f"http://localhost:{PORT}"
        nodes = [wavelink.Node(uri=uri, password=PASSWORD)]

        await wavelink.Pool.connect(nodes=nodes, client=self.bot, cache_capacity=100)


async def setup(bot: commands.Bot):
    await bot.add_cog(WavelinkController(bot))
