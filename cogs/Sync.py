from typing import Optional, Literal

import discord
from discord.ext import commands
from discord.ext.commands import Context


class Sync(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def sync(self, ctx: Context, spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        ctx.bot.tree.copy_global_to(guild=ctx.guild)
        synced = await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}")


async def setup(client):
    await client.add_cog(Sync(client))