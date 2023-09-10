import asyncio
import random
import discord
from discord.ext import commands


class Team:
    def __init__(self, name, team, under_cover):
        self.name = name
        self.team = team
        self.under_cover = under_cover


class StartGame(commands.Cog, Team):
    def __init__(self, bot):
        self.bot = bot
        self.msg_id = None
        self.num_undercover = random.choice([1, 2, 1, 2, 5])
        self.teamA = Team('A', [], [])
        self.teamB = Team('B', [], [])

    @commands.command()
    async def bothelp(self, ctx):
        await ctx.send("输入 /start 开始内战 \n" +
                       "输入 /game 分配内鬼 \n" +
                       "输入 /botvote 开始投票 \n" +
                       "输入 /result 公布内鬼 ")

    @commands.command()
    async def start(self, ctx):
        # Send a message with buttons
        embed = discord.Embed(title="开始内战", description="请A，B队的成员分别点下面的🅰️ 🅱️, 每人只点一个，点错及时修改",
                              color=discord.Color.blue())
        msg = await ctx.send(embed=embed)
        self.msg_id = msg.id

        # Add reaction emojis
        emojis = ['🅰️', '🅱️']
        for emoji in emojis:
            await msg.add_reaction(emoji)

        # Define a check for reaction response
        def reaction_check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in emojis

        try:
            await self.bot.wait_for('reaction_add', timeout=60.0, check=reaction_check)
        except asyncio.TimeoutError:
            await ctx.send("You didn't make a choice in time.")

    @commands.command()
    async def game(self, ctx):
        if self.msg_id is None:
            await ctx.send("The game has not been started yet.")
            return
        message = await ctx.fetch_message(self.msg_id)

        for reaction in message.reactions:
            if str(reaction.emoji) == '🅰️':
                users = [user async for user in reaction.users() if user.global_name is not None]
                self.teamA.team.extend(users)
                print(f"team A: {', '.join(user.global_name for user in users)}")
            elif str(reaction.emoji) == '🅱️':
                users = [user async for user in reaction.users() if user.global_name is not None]
                self.teamB.team.extend(users)
                print(f"team B: {', '.join(user.global_name for user in users)}")

        des = (f"A队: {', '.join(user.global_name for user in self.teamA.team)}\n"
               f"B队: {', '.join(user.global_name for user in self.teamB.team)}")
        embed = discord.Embed(title="开始组队", description=des,
                              color=discord.Color.blue())
        await ctx.send(embed=embed)

        # Select and message the under covers
        teamA_under_cover = self.handle_undercover(ctx, self.teamA)
        teamB_under_cover = self.handle_undercover(ctx, self.teamB)

        self.teamA.under_cover, self.teamB.under_cover = await asyncio.gather(teamA_under_cover, teamB_under_cover)

    async def handle_undercover(self, ctx, team_) -> []:
        chosen_users = random.sample(team_.team, min(len(team_.team), self.num_undercover))
        print(f'len chosen_users: {len(chosen_users)}')
        print(f'undercover num: {self.num_undercover}')
        print(f'内鬼是：{[u.global_name for u in chosen_users]}')

        await ctx.send(f'{team_.name}队内鬼已经选出，请查看Discord私信')
        await asyncio.wait([self.message_undercover(u) for u in chosen_users])

        await ctx.send(f'已收到 {team_.name.upper()} 队内鬼的回复')
        return chosen_users

    async def message_undercover(self, chosen_user):
        await chosen_user.send('你是内鬼，收到请回复（回复任何字符都可）')

        def check_yes(m):
            return m.author == chosen_user and len(m.content) != 0 and isinstance(
                m.channel, discord.DMChannel)

        await self.bot.wait_for('message', check=check_yes)

    @commands.command()
    async def botvote(self, ctx):
        if self.msg_id is None:
            await ctx.send("The game has not been started yet.")
            return

        nums_emoji = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']

        voted_teamA = self.vote_team(ctx, nums_emoji, self.teamA)
        voted_teamB = self.vote_team(ctx, nums_emoji, self.teamB)

        asyncio.gather(voted_teamA, voted_teamB)

    async def vote_team(self, ctx, nums_emoji, team_):
        if (len(team_.under_cover) == len(team_.team)):
            await ctx.send(f"👻👻👻👻👻 奥斯卡之夜！全员内鬼 👻👻👻👻👻")
            return

        des = (f"{team_.name}队有{len(team_.under_cover)}个内鬼\n"
               f"{team_.name.upper()}队内鬼投票：{', '.join([nums_emoji[i] + ': ' + v.global_name for i, v in enumerate(team_.team)])}")
        embed = discord.Embed(title="内鬼投票", description=des,
                              color=discord.Color.blue())

        msg = await ctx.send(embed=embed)
        for emoji in nums_emoji[:len(team_.team)]:
            await msg.add_reaction(emoji)

    @commands.command()
    async def result(self, ctx):
        des = (f"A队内鬼是: {', '.join([u.global_name for u in self.teamA.under_cover])}\n"
               f"B队内鬼是: {', '.join([u.global_name for u in self.teamB.under_cover])}")
        embed = discord.Embed(title="公布内鬼", description=des,
                              color=discord.Color.blue())
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(StartGame(bot))
