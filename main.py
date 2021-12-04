from discord.ext import commands
import os
from dotenv import load_dotenv
import pandas as pd
import pickle
import datetime as dt

# Bot initialization
client = commands.Bot(command_prefix="#")

# Loading
load_dotenv()  # Create '.env' file and type DISCORD_TOKEN=<Discord Bot Token>
TOKEN = os.getenv("DISCORD_TOKEN")
users = dict({})
df = pd.DataFrame(columns=['Date', 'ID', 'Username', 'Voice', 'Message', 'New Member'])

@client.event
async def on_ready():
    global users
    global df
    print("DISCORD TRACKER IS RUNNING")
    if os.stat("users.pkl").st_size != 0:  # Load {ID: Users} Dict if the file is not empty
        file = open("users.pkl", "rb")
        users = pickle.load(file)
    if os.stat("data.csv").st_size != 0:
        df = pd.read_csv("data.csv")

# Data Collection
@client.event
async def on_voice_state_update(member, before, after):
    date = dt.datetime.today().strftime("%d-%m-%Y")
    if not before.channel and after.channel:
        if not ((df['Date'] == date) & (df['ID'] == member.id)).any():  # Checks if there is already an entry
            df.loc[len(df.index)] = [date, member.id, member.name, True, 0, False]
            df.to_csv(path_or_buf="data.csv")
        else:
            row = df.index[((df['Date'] == date) & (df['ID'] == member.id)).any()]
            row_index = row[0][0]
            df.at[row_index, 'Voice'] = True
            df.to_csv(path_or_buf="data.csv")

@client.event
async def on_message(message):
    date = dt.datetime.today().strftime("%d-%m-%Y")
    user_id = str(message.author.id)
    user_name = str(message.author.name)

    if not ((df['Date'] == date) & (df['ID'] == message.author.id)).any():
        df.loc[len(df.index)] = [date, message.author.id, message.author.name, False, 1, False]
        df.to_csv(path_or_buf="data.csv")
    else:
        row = df.index[((df['Date'] == date) & (df['ID'] == message.author.id)).any()]
        row_index = row[0][0]
        df.at[row_index, 'Message'] += 1
        df.to_csv(path_or_buf="data.csv")

@client.event
async def on_member_join(member):
    date = dt.datetime.today().strftime("%d-%m-%Y")
    df.loc[len(df.index)] = [date, member.id, member.name, False, 0, True]

if __name__ == "__main__":
    client.run(TOKEN)
