import asyncio
import json
import random
import discord
from discord import app_commands
from discord.ext import commands


class Team:
    def __init__(self, name, members, under_cover):
        self.name = name
        self.members = members
        self.under_cover = under_cover


class StartGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_init()

    def game_init(self):
        self.msg_id = None
        self.num_undercover = random.choice([1, 2, 1, 2, 1, 2, 5])
        self.teamA = Team('A', [], [])
        self.teamB = Team('B', [], [])
        # with open('undercover_tasks.json') as f:
        #     self.tasks = json.load(f)['tasks']

    @app_commands.command(name='help', description='列出所有commands')
    async def help(self, ctx: discord.Interaction):
        await ctx.response.send_message("输入 /start 开始内战 \n" +
                                        "输入 /game 分配内鬼 \n" +
                                        "输入 /vote 开始投票 \n" +
                                        "输入 /result 公布内鬼 ")

    @app_commands.command(name='start', description='开始内战')
    async def start(self, ctx: discord.Interaction):
        self.game_init()

        embed = discord.Embed(title="开始内战", description="房间左边对应🅰️队，右边对应🅱️队，每个人只点一次。点错后再点一次取消，重新选择正确的",
                              color=discord.Color.blue())
        await ctx.response.send_message(embed=embed)
        msg = await ctx.original_response()
        self.msg_id = msg.id

        # Add reaction emojis
        emojis = ['🅰️', '🅱️']
        for emoji in emojis:
            await msg.add_reaction(emoji)

        # Define a check for reaction response
        def reaction_check(reaction, user):
            return user == ctx.user and str(reaction.emoji) in emojis

        try:
            await self.bot.wait_for('reaction_add', timeout=60.0, check=reaction_check)
        except asyncio.TimeoutError:
            await ctx.response.send_message("You didn't make a choice in time.")

    @app_commands.command(name='game', description='分配内鬼')
    async def game(self, ctx: discord.Interaction):
        if self.msg_id is None:
            await ctx.response.send_message("The game has not been started yet.")
            return

        message = await ctx.channel.fetch_message(self.msg_id)

        for reaction in message.reactions:
            if str(reaction.emoji) == '🅰️':
                users = [user async for user in reaction.users() if user.global_name is not None]
                self.teamA.members.extend(users)
                print(f"team A: {', '.join(user.global_name for user in users)}")
            elif str(reaction.emoji) == '🅱️':
                users = [user async for user in reaction.users() if user.global_name is not None]
                self.teamB.members.extend(users)
                print(f"team B: {', '.join(user.global_name for user in users)}")

        des = (f"A队: {', '.join(user.global_name for user in self.teamA.members)}\n"
               f"B队: {', '.join(user.global_name for user in self.teamB.members)}")
        embed = discord.Embed(title="开始组队", description=des,
                              color=discord.Color.blue())
        await ctx.response.send_message(embed=embed)

        # Select and message the under covers
        teamA_under_cover = self.handle_undercover(ctx, self.teamA)
        teamB_under_cover = self.handle_undercover(ctx, self.teamB)

        self.teamA.under_cover, self.teamB.under_cover = await asyncio.gather(teamA_under_cover, teamB_under_cover)

    async def handle_undercover(self, ctx: discord.Interaction, team) -> []:
        chosen_users = random.sample(team.members, min(len(team.members), self.num_undercover))
        print(f'len chosen_users: {len(chosen_users)}')
        print(f'undercover num: {self.num_undercover}')
        print(f'内鬼是：{[u.global_name for u in chosen_users]}')

        await ctx.followup.send(f'{team.name}队内鬼已经选出，请查看Discord私信')
        await asyncio.wait([self.message_undercover(u) for u in chosen_users])

        await ctx.followup.send(f'已收到 {team.name.upper()} 队内鬼的回复')
        return chosen_users

    async def message_undercover(self, chosen_user, task=None):
        if task is not None:
            await chosen_user.send(f'你是内鬼，收到请回复（回复任何字符都可）\n你的内鬼任务是：{task}')
        else:
            await chosen_user.send(f'你是内鬼，收到请回复（回复任何字符都可）')

        def check_yes(m):
            return m.author == chosen_user and len(m.content) != 0 and isinstance(
                m.channel, discord.DMChannel)

        await self.bot.wait_for('message', check=check_yes)

    @app_commands.command(name='vote', description='开始投票')
    async def vote(self, ctx):
        if self.msg_id is None:
            await ctx.response.send_message("The game has not been started yet.")
            return

        nums_emoji = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']

        voted_teamA = self.vote_team(ctx, nums_emoji, self.teamA)
        voted_teamB = self.vote_team(ctx, nums_emoji, self.teamB)

        await ctx.response.defer()
        await asyncio.gather(voted_teamA, voted_teamB)

    async def vote_team(self, ctx, nums_emoji, team):
        if len(team.under_cover) == len(team.members):
            await ctx.followup.send(f"'👻''👻''👻''👻''👻'奥斯卡之夜！全员内鬼'👻''👻''👻''👻''👻'")
            return

        des = (f"{team.name}队有{len(team.under_cover)}个内鬼\n"
               f"{team.name.upper()}队内鬼投票：{', '.join([nums_emoji[i] + ': ' + v.global_name for i, v in enumerate(team.members)])}")
        embed = discord.Embed(title=f"{team.name.upper()}队内鬼投票", description=des,
                              color=discord.Color.blue())

        msg = await ctx.followup.send(embed=embed)
        for emoji in nums_emoji[:len(team.members)]:
            await msg.add_reaction(emoji)

    @app_commands.command(name='result', description='公布内鬼')
    async def result(self, ctx):
        des = (f"A队内鬼: {', '.join([u.global_name for u in self.teamA.under_cover])}\n"
               f"B队内鬼: {', '.join([u.global_name for u in self.teamB.under_cover])}")
        embed = discord.Embed(title="公布内鬼", description=des,
                              color=discord.Color.blue())
        await ctx.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(StartGame(bot))
