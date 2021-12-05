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
        df['Duration'] = pd.to_datetime(df['Duration'])
        df['Date'] = pd.to_datetime(df['Date'])

# Data Collection
@client.event
async def on_voice_state_update(member, before, after):

    date = dt.datetime.today().strftime("%d-%m-%Y") # Current
    now_date = dt.datetime.now()
    null_time = dt.datetime(now_date.year, now_date.month, now_date.day, 0, 0)
    date_tomorrow = (dt.datetime.today() + dt.timedelta(days=1)).strftime("%d-%m-%Y") # Tomorrow
    null_tomorrow = null_time + dt.timedelta(days=1)

    if not before.channel and after.channel:  # Joins chat
        if not ((df['Date'] == date) & (df['ID'] == member.id)).any(): # If no entry
            df.loc[len(df.index)] = [date, member.id, member.name, null_time, 0]
            df.loc[len(df.index)] = [date_tomorrow, member.id, member.name, null_tomorrow, 0] # Append at the bottom of list
            user_times.update({member.id : dt.datetime.now()})
        else:
            row = df.index[((df['Date'] == date) & (df['ID'] == member.id))].tolist()
            row_index = row[0]
            if df.at[row_index, 'Duration'] != null_time:
                user_times.update({member.id: dt.datetime.now()})
            if not ((df['Date'] == date_tomorrow) & (df['ID'] == member.id)).any():
                df.loc[len(df.index)] = [date_tomorrow, member.id, member.name, null_tomorrow, 0]
    if before.channel and not after.channel:  # Leaves chat
        row = df.index[((df['Date'] == date) & (df['ID'] == member.id))].tolist()
        row_index = row[0]
        df.at[row_index, 'Duration'] += (dt.datetime.now() - user_times.get(member.id))  # Adds accumulated time
        user_times.pop(member.id)
        df.sort_values(by=['Date'], ascending=False)
        df.to_csv(path_or_buf="data.csv", index=False)
        print(df.loc[row_index])

@client.event
async def on_message(message):

    date = dt.datetime.today().strftime("%d-%m-%Y")
    date_tomorrow = (dt.datetime.today() + dt.timedelta(days=1)).strftime("%d-%m-%Y")
    now_date = dt.datetime.now()
    null_time = now_date.replace(hour=0, minute=0, second=0, microsecond=1)
    null_tomorrow = null_time + dt.timedelta(days=1)

    if not ((df['Date'] == date) & (df['ID'] == message.author.id)).any():
        df.loc[len(df.index)] = [date, message.author.id, message.author.name, null_time, 1]
        df.loc[len(df.index)] = [date_tomorrow, message.author.id, message.author.name, null_tomorrow, 1]
        df.sort_values(by=['Date'], inplace=True, ascending=False)
        df.to_csv(path_or_buf="data.csv", index=False)
    else:
        row = df.index[((df['Date'] == date) & (df['ID'] == message.author.id))].tolist()
        row_index = row[0]
        df.at[row_index, 'Messages'] += 1
        df.sort_values(by=['Date'], inplace=True, ascending=False)
        df.to_csv(path_or_buf="data.csv", index=False)
        print(df.loc[row_index])

if __name__ == "__main__":
    client.run(TOKEN)
