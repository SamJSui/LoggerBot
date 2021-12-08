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
null_duration = time.mktime((1970, 1, 1, 0, 0, 0, 0, 0, 0)) - 18000


def check_row_exists(row_date, user_id, dataframe):
    for i in range(len(dataframe)):
        if str(dataframe.at[i, 'Date']) == str(row_date) and str(dataframe.at[i, 'ID']) == str(user_id): # If there is a row with the date and ID
            return False
    return True


def row_finder(row_date, user_id, dataframe):
    for i in range(len(dataframe)):
        if str(dataframe.at[i, 'Date']) == str(row_date) and str(dataframe.at[i, 'ID']) == str(user_id):  # If there is a row with the date and ID
            return i
    return False


def csv_print():
    df['Date'] = pd.to_datetime(df['Date'], errors='raise')
    df.sort_values(by='Date', inplace=True, ascending=False)
    df.to_csv(path_or_buf="data.csv", index=False)


def dict_update(user_id, action):
    if action == 'update':
        user_times.update({user_id: time.time()})
        file_to_write = open("times.pkl", "wb")
        pickle.dump(user_times, file_to_write)
    elif action == 'pop':
        user_times.pop(user_id)
        file_to_write = open("times.pkl", "wb")
        pickle.dump(user_times, file_to_write)


def duration_summation(time_span, user_id, dataframe, data_column):
    data_sum = 0.0
    if user_id == 'server': # Totaling the Server
        if time_span == 'total':
            return sum(dataframe[data_column])
        if time_span == 'day':
            for i in range(len(dataframe.index)):
                if dataframe.at[i, 'Date'] == str(dt.datetime.today().day):
                    data_sum += float(dataframe.at[i, 'Duration'])
        return data_sum

    if time_span == 'total': # Totaling User
        for i in range(len(dataframe.index)):
            if dataframe.at[i, 'ID'] == user_id:
                data_sum += float(dataframe.at[i, data_column])
        if user_id in user_times and data_column == 'Duration':
            data_sum += (time.time() - user_times.get(user_id))

    elif time_span == 'day':
        dataframe['Date'] = dataframe["Date"].dt.strftime("%d").str.lstrip('0')
        for i in range(len(dataframe.index)):
            if dataframe.at[i, 'ID'] == user_id and dataframe.at[i, 'Date'] == str(dt.datetime.today().day):
                data_sum += float(dataframe.at[i, 'Duration'])
        if user_id in user_times and data_column == 'Duration':
            data_sum += (time.time() - user_times.get(user_id))
    return data_sum


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
    if not before.channel and after.channel:  # Joins chat
        if check_row_exists(date, member.id, df): # If no entry
            df.loc[len(df.index)] = [date, member.id, member.name, null_duration, 0]
            df.loc[len(df.index)] = [tomorrow, member.id, member.name, null_duration, 0] # Append at the bottom of list
            dict_update(member.id, 'update')
        else:
            index = row_finder(date, member.id, df)
            if df.at[index, 'Duration'] != date:
                dict_update(member.id, 'update')
            if check_row_exists(tomorrow, member.id, df):
                df.loc[len(df.index)] = [tomorrow, member.id, member.name, null_duration, 0]
    if before.channel and not after.channel:  # Leaves chat
        index = row_finder(date, member.id, df)
        df.at[index, 'Duration'] += (time.time() - user_times.get(member.id))  # Adds accumulated time
        dict_update(member.id, 'pop')
        csv_print()
        print(df.loc[index, :])


@client.event
async def on_message(message):
    date = dt.datetime.today().replace(hour=0, minute=0, second=0, microsecond=1)
    tomorrow = date + dt.timedelta(days=1)
    if message.author.name != str(client.user).rstrip('#1455'): # Tests if the message is the bot
        if check_row_exists(date, message.author.id, df):
            df.loc[len(df.index)] = [date, message.author.id, message.author.name, null_duration, 1]
            df.loc[len(df.index)] = [tomorrow, message.author.id, message.author.name, null_duration, 0]
            csv_print()
        else:
            index = row_finder(date, message.author.id, df)
            df.at[index, 'Messages'] += 1
            csv_print()
            print(df.loc[index, :])
    await client.process_commands(message)


@client.command(name='voice')
async def voice(ctx):
    try:
        argv = str(ctx.message.content).lower().split()
        data = df.copy(deep=True)
        data_sum = duration_summation(argv[1], ctx.message.author.id, data, 'Duration')
        HMS_format = str(dt.timedelta(seconds=data_sum)).split('.')[0]
        await ctx.send(HMS_format)
    except IndexError:
        await ctx.send("!voice Day|Total")
    del data
    gc.collect()


@client.command(name='graph')
async def graph(ctx):
    try:
        argv = ctx.message.content.split()
        data = df.copy(deep=True)
        y_label = [
            duration_summation(argv[1], ctx.message.author.id, data, 'Duration'),
            duration_summation(argv[1], 'server', data, 'Duration')
        ]

        fig, ax = plt.subplots() # Plot initialization
        fig.canvas.draw()
        x_label = [str(ctx.message.author), 'Server']
        plt.bar(x_label, y_label, color='blue')
        rects = ax.patches

        y_time = [] # y_tick labeling
        for i in plt.yticks()[0]:
            y_time.append(str(dt.timedelta(seconds=i)).split('.')[0])
        bar_time = []
        for i in y_label:
            bar_time.append(str(dt.timedelta(seconds=i)).split('.')[0])

        ax.set_yticks(plt.yticks()[0])
        ax.set_yticklabels(y_time)
        ax.set_title('Total User Time in Voice Chat vs. Server\'s')
        ax.set_ylabel("Time")
        for rect, label in zip(rects, bar_time):
            height = rect.get_height()
            ax.text(
                rect.get_x() + rect.get_width() / 2, height + 5, label, ha="center", va="bottom"
            )

        plt.savefig("bar_graph")
        await ctx.send(file=discord.File('bar_graph.png'))

        del data
        gc.collect()
    except IndexError:
        await ctx.send('!graph Day|Total')


if __name__ == "__main__":
    client.run(TOKEN)
