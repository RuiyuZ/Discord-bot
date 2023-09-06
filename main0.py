#=========== ThePao's Code =======#
import discord
from discord.ext import commands
import os
import random

intents = discord.Intents.all()
intents.members = True
client = discord.Client(intents=intents)
GUILD = 871501115454283797
teamA = []
teamB = []
teamA_active = False
teamB_active = False
teamSize = 5


@client.event
async def on_ready():
  print("We have logged in as {0.user}".format(client))
  print("TestCommand Ready!")


@client.event
async def on_message(message):
  global teamA_active, teamB_active

  if message.author == client.user:
    return
  print(message.content)
  if message.content == '开始内战':
    await message.channel.send("选择开始组建A队或B队，输入'A'或者'B'")

  def check_team_choice(m):
    return m.author == message.author and m.channel == message.channel and m.content.lower(
    ) in ['a', 'b']

  team_choice_response = await client.wait_for('message',
                                               check=check_team_choice)

  team_choice = team_choice_response.content.lower()

  print('==== team choice: ', team_choice)
  if team_choice == 'a' and not teamA_active:
    teamA_active = True
    await listenToTeam(message, team_choice_response, team_choice)

  elif team_choice == 'b' and not teamB_active:
    teamB_active = True
    await listenToTeam(message, team_choice_response, team_choice)


async def listenToTeam(message, team_choice_response, team_choice):
  team = teamA if team_choice == 'a' else teamB

  await message.channel.send(
      f"{team_choice_response.author} 选择了 {team_choice.upper()}队.")

  await message.channel.send(f"请@出{team_choice.upper()}队的成员:")

  def check(m):
    return m.author == message.author and m.channel == message.channel

  user_response = await client.wait_for('message', check=check, timeout=60)
  message = user_response
  if message.mentions:
    mentioned_users = message.mentions

    for a in mentioned_users:
      if len(team) < teamSize:
        team.append(a)
      else:
        await message.channel.send(
            f'{team_choice.upper()}队不能超过{teamSize}人，请重新输入')
    res = ','.join(x.global_name for x in team)
    await message.channel.send(f'{team_choice.upper()}队: {res}')

    print(message.mentions)
    choosed_user = random.choice(mentioned_users)
    await message.channel.send(f'内鬼是：{choosed_user}')

    await choosed_user.send('你是内鬼，收到回复（回复任何字符都可）')

    def check_yes(m):
      print('Received a message. Performing checks...')
      print('Author: {}, content: {}, channel: {}'.format(
          m.author, m.content, m.channel))
      return m.author == choosed_user and len(m.content) != 0 and isinstance(
          m.channel, discord.DMChannel)

  user_response = await client.wait_for('message', check=check_yes)

  print(f'==== user response: {user_response}')
  if len(user_response.content) != 0:
    await message.channel.send(
        f'已收到 {team_choice.upper()} 队内鬼： {choosed_user} 的回复')


client.run(os.getenv('TOKEN'))
