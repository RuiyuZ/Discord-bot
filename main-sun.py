import discord
from discord.ext import commands
import os
import random

intents = discord.Intents.all()
intents.members = True
client = discord.Client(intents=intents)
GUILD = 871501115454283797
teams = [[], []]

teamSize = 5

inProgress = False


@client.event
async def on_ready():
  print("We have logged in as {0.user}".format(client))
  print("TestCommand Ready!")


@client.event
async def on_message(message):
  global inProgress, teamSize, teams, moles, moleResponses

  if message.author == client.user:
    return

  if inProgress:
    print(
        'You send a message, but we are in the middle of processing already, so ignoring this one.'
    )
    return

  print(message.content)
  if message.content != '开始内战':
    return

  inProgress = True
  print('开始新的内战组建')

  for i in range(len(teams)):
    await message.channel.send("请@出Team {}的成员:".format(i))

    def check_author_and_channel(m):
      return m.author == message.author and m.channel == message.channel

    user_response = await client.wait_for('message',
                                          check=check_author_and_channel,
                                          timeout=60)
    message = user_response
    if message.mentions:
      mentioned_users = message.mentions
      print(message.mentions)

      while len(mentioned_users) > teamSize:
        await message.channel.send("Team {}的成员不能超过{}人，请重新输入".format(
            i, teamSize))
        user_response = await client.wait_for('message',
                                              check=check_author_and_channel,
                                              timeout=60)
        mentioned_users = user_response.mentions
        print(message.mentions)

      for user in mentioned_users:
        teams[i].append(user)

  for i, team in enumerate(teams):
    print('Team {} 成员：{}'.format(i, ','.join([user.name for user in team])))

  # 选择内鬼
  for i in range(len(teams)):
    mole = random.choice(teams[i])
    print('Team {} 内鬼是 {}'.format(i, moles[i]))
    await mole.send('你是内鬼，收到回复（回复任何字符都可）')

    def check_message_from_mole(m):
      print('Received a message. Performing checks...')
      print('Author: {}, content: {}, channel: {}'.format(
          m.author, m.content, m.channel))
      return m.author in mole and len(m.content) != 0
      # and m.channel == discord.channel.DMChannel

    await client.wait_for('message', check=check_message_from_mole)
    print('已收到Team {} 内鬼回复'.format(i))

  print('内鬼选择已结束，收到所有内鬼回复，正在结束这段对话')
  inProgress = False


client.run(os.getenv('TOKEN'))
