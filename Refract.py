import discord
import asyncio
import time
import sqlite3
import requests
import requests.auth
from configobj import ConfigObj

def setup():
	print(config);
	print('This appears to be the first time you\'ve used this server, setting up neccessary files');
	c.execute('''CREATE TABLE games (name text, timePlayed integer, player text)''');
	c.execute('''CREATE TABLE accounts (discord text, steam text)''');
	conn.commit();
	print('Database Setup complete.');
	print('Please enter the following information:');
	config['apiKeys'] = {};
	config['apiKeys']['discord'] = input('What is your discord apiKey?\n');
	config['apiKeys']['steam'] = input('What is your steam apiKey?\n');
	config.write();

conn = sqlite3.connect('Refract.db');
c = conn.cursor();
try:
	config = ConfigObj('refract.conf');
	test = config['apiKeys']['discord'];
except KeyError:
	setup();

client = discord.Client();

@client.event
async def on_member_join(member):
	server = member.server;
	fmt = 'Welcome to {1.name} {0.mention}'
	await client.send_message(server, fmt.format(member, server));

@client.event
async def on_message(message):
	if(message.content.startswith('!1984')):
		await nineteenEightyFour(message.channel, 6);
	elif(message.content.startswith('!games')):
		await games(message.server, message.channel);
	elif(message.content == '!timePlayed'):
		await timePlayedRead(message.server, message.channel);

async def nineteenEightyFour(channel, loops):
	msg = await client.send_message(channel, "War Is Peace!");
	mod = 1;
	await asyncio.sleep(1);
	for i in range(0, loops-1):
		await client.edit_message(msg, ["War Is Peace!", "Freedom Is Slavery!", "Ignorance Is Strength!"][mod]);
		mod = (mod + 1) % 3;
		await asyncio.sleep(1);

async def games(server, channel):
	played = [];
	for member in server.members:
		try:
			memberPlaying = member.game.name;
			onList = False;
			for game in played:
				if(memberPlaying == game[0]):
					game[1] += 1;
					onList = True;
			if(onList == False):
				played.append([memberPlaying, 1]);
		except AttributeError:
			pass;
	played.sort(key=lambda x: -x[1]);
	await client.send_message(channel, "The games being played on this server are:");
	for game in played:
		await asyncio.sleep(1);
		await client.send_message(channel, game[0] + ': ' + str(game[1]) + " player(s)");


async def timePlayedCounter():
	await client.wait_until_ready();
	while not client.is_closed:
		alreadyCounted = [];
		for server in client.servers:
			for member in server.members:
				try:
					if((member.id in alreadyCounted) == False and member.game.name != None):
						alreadyCounted.append(member.id);
						c.execute('SELECT * FROM games WHERE player = ? AND name = ?', [member.id, member.game.name]);
						row = c.fetchone();
						if(row != None):
							c.execute('UPDATE games SET timePlayed=(?) WHERE player = ? AND name = ?', [row[1] + 15, member.id, member.game.name]);
						else:
							c.execute('INSERT INTO games VALUES(?,?,?)', [member.game.name, 15, member.id]);
				except AttributeError:
					pass
		conn.commit();
		await asyncio.sleep(900);		# 15 minute loop

async def timePlayedRead(server, channel):
	command = "SELECT name, SUM(timePlayed) from games WHERE player IN (";
	members = list(server.members);
	for i in range(0, len(members)):
		members[i] = members[i].id;
	command += '?,' * len(members);
	command = command[0:-1];
	command += ') GROUP BY name'
	c.execute(command, members);
	row = c.fetchone();
	if(row == (None, None)):
		return(None);
	while(row != None):
		await client.send_message(channel, str(row[0]) + ' has been played for: ' + str(row[1]/60) + ' hour(s)');
		await asyncio.sleep(1);
		row = c.fetchone();



@client.event
async def on_ready():
	print('Successfully logged in as: ');
	print(client.user.name);

client.loop.create_task(timePlayedCounter());
client.run(config['apiKeys']['discord']);