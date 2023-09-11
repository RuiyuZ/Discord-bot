import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)
load_dotenv()
GUILD = os.getenv('GUILD')
TEST_GUILD = bot.get_guild(GUILD)


class Bot(commands.Bot):

    def __init__(self):
        super().__init__(intents=discord.Intents.all(), command_prefix='/')

    async def on_ready(self):
        print(f'Logged in as {bot.user.name}')

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Command not found. Use `/help`, `/start`, `/game`, `/vote` or `/result`")

    async def setup_hook(self):
        for file in os.listdir(f'./cogs'):
            if file.endswith('.py'):
                await self.load_extension(f'cogs.{file[:-3]}')


load_dotenv()
bot = Bot()
bot.run(os.getenv('TOKEN'))
