import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)
load_dotenv()
GUILD=os.getenv('GUILD')
TEST_GUILD = bot.get_guild(GUILD)

@bot.event
async def on_ready():
    global GUILD
    GUILD = bot.get_guild(GUILD)
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Use `/start` or `/play`")

async def main():
    await bot.load_extension('startGame')
    await bot.start(os.getenv('TOKEN'))



loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()