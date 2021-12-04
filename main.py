from discord.ext import commands
import os
from dotenv import load_dotenv
import pandas as pd
import datetime as dt

# Bot initialization
client = commands.Bot(command_prefix="#")

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

# Data Collection
@client.event
async def on_voice_state_update(member, before, after):
    date = dt.datetime.today().strftime("%d-%m-%Y")
    now_date = dt.datetime.now()
    null_time = dt.datetime(now_date.year, now_date.month, now_date.day, 0, 0)
    if not before.channel and after.channel:  # Joins chat
        if not ((df['Date'] == date) & (df['ID'] == member.id)).any():  # If no entry
            df.loc[len(df.index)] = [date, member.id, member.name, null_time, 0]  # Append at the bottom of list
            user_times.update({member.id : dt.datetime.now()})
        else:
            row = df.index[((df['Date'] == date) & (df['ID'] == member.id)).any()]  # If entry - finds row index
            row_index = row[0][0]
            if df.at[row_index, 'Duration'] != null_time:
                user_times.update({member.id: dt.datetime.now()})
    if before.channel and not after.channel:  # Leaves chat
        row = df.index[((df['Date'] == date) & (df['ID'] == member.id))].tolist()
        row_index = row[0]
        df.at[row_index, 'Duration'] += (dt.datetime.now() - user_times.get(member.id))  # Adds accumulated time
        user_times.pop(member.id)
        df.to_csv(path_or_buf="data.csv")
        print(df.tail())

@client.event
async def on_message(message):
    date = dt.datetime.today().strftime("%d-%m-%Y")
    now_date = dt.datetime.now()
    null_time = now_date.replace(hour=0, minute=0, second=0, microsecond=1)
    if not ((df['Date'] == date) & (df['ID'] == message.author.id)).any():
        df.loc[len(df.index)] = [date, message.author.id, message.author.name, null_time, 1]
        df.to_csv(path_or_buf="data.csv")
        print(df.tail())
    else:
        row = df.index[((df['Date'] == date) & (df['ID'] == message.author.id))].tolist()
        row_index = row[0]
        df.at[row_index, 'Messages'] += 1
        df.to_csv(path_or_buf="data.csv")
        print(df.tail())

if __name__ == "__main__":
    client.run(TOKEN)