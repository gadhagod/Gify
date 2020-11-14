#!/usr/bin/env python

import discord
import giphy_client
from rockset import Client, ParamDict, Q, F
from os import getenv
from datetime import datetime

# Discord
client = discord.Client()

# Giphy
giphy_instance = giphy_client.DefaultApi()
giphy_key = getenv('GIPHY_SECRET')

# Rockset
rs = Client(api_key=getenv('ROCKSET_SECRET'), api_server="api.rs2.usw2.rockset.com")

user_collection_name = 'GifyUsers'
user_collection = rs.Collection.retrieve(user_collection_name)

history_collection_name = 'GifyHistory'
history_collection = rs.Collection.retrieve(history_collection_name)

get_history = rs.QueryLambda.retrieve(
    'GifyGetHistory',
    version='37dae3c9a4b14b54',
    workspace='commons'
)
params = ParamDict()

# Bot events
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game(name="!gif help"))

@client.event
async def on_message(message):
    msg = message.content.lower().replace('!', '')
    log = False

    if msg == 'help' or msg == 'gify' or msg == 'gif' or msg == 'gif help':
        embed = discord.Embed(title='Hey there, i\'m Gify!', description='''``gif help`: see this message
        `gif random`: get a completely random GIF
        `gif search {keyword}`: get a GIF by keyword
        `gif trending` to get a random trending GIF
        `gif history` to see your recent commands and GIF responses
        `gif code`: see source code''', color=0x00ff00)
        await message.channel.send(embed=embed)

    if msg.startswith('gif random'):
        if msg == 'gif random':
            res = giphy_instance.gifs_random_get(giphy_key, rating='pg')
        else:
            input = msg.replace('gif random ', '')
            res = giphy_instance.gifs_random_get(giphy_key, tag=input, rating='pg')
        res = res.to_dict()['data'] 
        image = res['image_original_url']
        print(res)
        embed = discord.Embed()
        embed.set_image(url=image)
        await message.channel.send(embed=embed)
        log = True

    if msg == 'gif trending':
        res = giphy_instance.gifs_trending_get(giphy_key, limit=1, rating='pg')
        res = res.to_dict()['data'][0]
        image = res['images']['original']['url']
        embed = discord.Embed()
        embed.set_image(url=image)
        await message.channel.send(embed=embed)
        log = True

    if msg.startswith('gif search'):
        input = msg.replace('gif search ', '')
        res = giphy_instance.gifs_search_get(giphy_key, input, limit=1, rating='pg', lang='en').to_dict()['data'][0]
        image = res['images']['original']['url']
        embed = discord.Embed()
        embed.set_image(url=image)
        await message.channel.send(embed=embed)
        log = True

    if msg == 'gif history':
        params['target_user_id'] = str(message.author.id)
        results = get_history.execute(parameters=params)['results']
        embed = discord.Embed(title='Recent commands from ' + message.author.name)
        print(results)
        await message.channel.send(embed=embed)
        for call in results:
            embed = discord.Embed()
            embed.add_field(name='Command', value=call['command'], inline=True)
            embed.add_field(name='Response', value=call['response'], inline=True)
            embed.add_field(name='Time', value=call['time'] + 'GMT', inline=True)
            await message.channel.send(embed=embed)

    if msg == 'gif code':
        await message.channel.send('https://github.com/gadhagod/Gify')

    print(message.author.id)
    docs = {
        '_id': str(message.author.id),
        'name': message.author.name
    }
    print(docs)
    print(user_collection.add_docs([docs]))

    if log:
        docs = {
            'command': message.content,
            'response': image,
            'user_id': str(message.author.id),
            'username': message.author.name,
            'time': datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        print(history_collection.add_docs([docs]))

client.run(getenv('GIFY_DISCORD_SECRET'))
