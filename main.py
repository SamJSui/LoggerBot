import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import pickle
import pandas as pd
import datetime as dt
import time
import matplotlib.pyplot as plt
import gc

# Bot initialization
client = commands.Bot(command_prefix='!')


# Loading
load_dotenv()  # Create '.env' file and type DISCORD_TOKEN=<Discord Bot Token>
TOKEN = os.getenv("DISCORD_TOKEN")
df = pd.DataFrame(columns=['Date', 'ID', 'Username', 'Duration', 'Messages'])
user_times = dict({})


def csv_print():
    df['Date'] = pd.to_datetime(df['Date'], errors='ignore')
    df.sort_values(by='Date', inplace=True, ascending=False)
    df.to_csv(path_or_buf="data.csv", index=False)


def row_finder(date, member_id):
    return df.index[((df['Date'] == date) & (df['ID'] == member_id))].tolist()


def dict_update(user_id, action):
    if action == 'update':
        user_times.update({user_id: time.time()})
        file_to_write = open("times.pkl", "wb")
        pickle.dump(user_times, file_to_write)
    elif action == 'pop':
        user_times.pop(user_id)
        file_to_write = open("times.pkl", "wb")
        pickle.dump(user_times, file_to_write)


@client.event
async def on_ready():
    global df
    global user_times
    print("DISCORD TRACKER IS RUNNING")
    if os.stat("data.csv").st_size != 0:
        df = pd.read_csv("data.csv")
        df.sort_values(by='Date', inplace=True, ascending=False)
    if os.stat("times.pkl").st_size != 0:
        file = open("times.pkl", "rb")
        user_times = pickle.load(file)


# Data Collection
@client.event
async def on_voice_state_update(member, before, after):
    date = dt.datetime.today().replace(hour=0, minute=0, second=0, microsecond=1)
    tomorrow = date + dt.timedelta(days=1)
    null_duration = time.mktime((1970, 1, 1, 0, 0, 0, 0, 0, 0)) - 18000
    if not before.channel and after.channel:  # Joins chat
        if not ((df['Date'] == date) & (df['ID'] == member.id)).any(): # If no entry
            df.loc[len(df.index)] = [date, member.id, member.name, null_duration, 0]
            df.loc[len(df.index)] = [tomorrow, member.id, member.name, null_duration, 0] # Append at the bottom of list
            dict_update(member.id, 'update')
        else:
            index = row_finder(date, member.id)[0]
            if df.at[index, 'Duration'] != date:
                dict_update(member.id, 'update')
            if not ((df['Date'] == tomorrow) & (df['ID'] == member.id)).any():
                df.loc[len(df.index)] = [tomorrow, member.id, member.name, null_duration, 0]
    if before.channel and not after.channel:  # Leaves chat
        index = row_finder(date, member.id)[0]
        df.at[index, 'Duration'] += (time.time() - user_times.get(member.id))  # Adds accumulated time
        dict_update(member.id, 'pop')
        csv_print()
        print(df.loc[index, :])


@client.event
async def on_message(message):
    date = dt.datetime.today().replace(hour=0, minute=0, second=0, microsecond=1)
    tomorrow = date + dt.timedelta(days=1)
    null_duration = time.mktime((1970, 1, 1, 0, 0, 0, 0, 0, 0)) - 18000
    if message.author.name != str(client.user).rstrip('#1455'): # Tests if the message is the bot
        if not ((df['Date'] == date) & (df['ID'] == message.author.id)).any():
            df.loc[len(df.index)] = [date, message.author.id, message.author.name, null_duration, 1]
            df.loc[len(df.index)] = [tomorrow, message.author.id, message.author.name, null_duration, 0]
            csv_print()
        else:
            index = row_finder(date, message.author.id)[0]
            df.at[index, 'Messages'] += 1
            csv_print()
            print(df.loc[index, :])
    await client.process_commands(message)


@client.command(name='voice')
async def voice(ctx):
    data = df.copy(deep=True)
    data['Date'] = str(data['Date']).split()[1] # Month
    data['Date'] = str(data['Date']).split('-')[1]

    duration_sum = 0.0
    for i in range(len(data.index)):
        if df.at[i, 'ID'] == ctx.message.author.id:
            duration_sum += float(df.at[i, 'Duration'])

    HMS_format = str(dt.timedelta(seconds=duration_sum)).split('.')[0]
    await ctx.send(HMS_format)
    del data
    gc.collect()

if __name__ == "__main__":
    client.run(TOKEN)
