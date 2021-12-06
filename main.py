import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt


# Bot initialization
client = commands.Bot(command_prefix='!', strip_after_prefix=True)


# Loading
load_dotenv()  # Create '.env' file and type DISCORD_TOKEN=<Discord Bot Token>
TOKEN = os.getenv("DISCORD_TOKEN")
df = pd.DataFrame(columns=['Date', 'ID', 'Username', 'Duration', 'Messages'])
user_times = dict({})


@client.event
async def on_ready():
    global df
    print("DISCORD TRACKER IS RUNNING")
    if os.stat("data.csv").st_size != 0:
        df = pd.read_csv("data.csv")
        df['Duration'] = pd.to_datetime(df['Duration'])
        df['Date'] = pd.to_datetime(df['Date'])
        df.sort_values(by='Date', inplace=True, ascending=False)


def csv_print():
    df.sort_values(by='Date', inplace=True, ascending=False)
    df.to_csv(path_or_buf="data.csv", index=False)


def row_finder(date, member_id):
    return df.index[((df['Date'] == date) & (df['ID'] == member_id))].tolist()


# Data Collection
@client.event
async def on_voice_state_update(member, before, after):
    date = dt.datetime.today().replace(hour=0, minute=0, second=0, microsecond=1)
    tomorrow = date + dt.timedelta(days=1)

    if not before.channel and after.channel:  # Joins chat
        if not ((df['Date'] == date) & (df['ID'] == member.id)).any(): # If no entry
            df.loc[len(df.index)] = [date, member.id, member.name, date, 0]
            df.loc[len(df.index)] = [tomorrow, member.id, member.name, tomorrow, 0] # Append at the bottom of list
            user_times.update({member.id : dt.datetime.now()})
        else:
            index = row_finder(date, member.id)[0]
            if df.at[index, 'Duration'] != date:
                user_times.update({member.id: dt.datetime.now()})
            if not ((df['Date'] == tomorrow) & (df['ID'] == member.id)).any():
                df.loc[len(df.index)] = [tomorrow, member.id, member.name, tomorrow, 0]
    if before.channel and not after.channel:  # Leaves chat
        index = row_finder(date, member.id)[0]
        df.at[index, 'Duration'] += (dt.datetime.now() - user_times.get(member.id))  # Adds accumulated time
        user_times.pop(member.id)
        csv_print()
        print(df.loc[index])


@client.event
async def on_message(message):
    date = dt.datetime.today().replace(hour=0, minute=0, second=0, microsecond=1)
    tomorrow = date + dt.timedelta(days=1)
    if message.author.name != str(client.user).rstrip('#1455'): # Tests if the message is the bot
        if not ((df['Date'] == date) & (df['ID'] == message.author.id)).any():
            df.loc[len(df.index)] = [date, message.author.id, message.author.name, date, 1]
            df.loc[len(df.index)] = [tomorrow, message.author.id, message.author.name, tomorrow, 0]
            csv_print()
        else:
            index = row_finder(date, message.author.id)[0]
            df.at[index, 'Messages'] += 1
            csv_print()
            print(df.loc[index])
    await client.process_commands(message)


@client.command(name='graph')
async def graph(ctx):
    message = ctx.message.content
    await ctx.send(message)


if __name__ == "__main__":
    client.run(TOKEN)
