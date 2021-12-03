import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import pandas as pd
import pickle

# Bot initialization
client = commands.Bot(command_prefix="#")

# Loads Token
load_dotenv()  # Create '.env' file and type DISCORD_TOKEN=<Discord Bot Token>
TOKEN = os.getenv("DISCORD_TOKEN")

users = dict({})

@client.event
async def on_ready():
    global users
    print("DISCORD TRACKER IS RUNNING")
    if os.stat("users.pkl").st_size != 0:
        file = open("users.pkl", "rb")
        users = pickle.load(file)


# Data Collection

@client.event
async def on_voice_state_update(member, before, after):
    if not before.channel and after.channel:
        user_id = str(after.channel.members).split()[1].lstrip('id=')
        if user_id in users:
            user = users.get(id)


@client.event
async def on_message(message):
    user_id = str(message.author.id)
    user_name = str(message.author)
    if user_id not in users:
        users.update({user_id: user_name})
        user_data = open("users.pkl", "wb")
        pickle.dump(users, user_data)
        user_data.close()


# Dataframe

# Writing to CSV

if __name__ == "__main__":
    client.run(TOKEN)

