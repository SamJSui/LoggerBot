# Discord Logger

Discord bot using the the Discord.py API to record user data for the application's communities.

## Current Version (v1.0)

- Discord Logger is able to parse information from Discord server voice channels and chats that it can view
- The ID's and current usernames of members who sent a message into chat will be held in ```data.pkl```

## How To Use

1. In CMD/Terminal, ```git clone https://github.com/SamJSui/Discord-Logger``` to clone the files to your current directory
2. In the directory, create a ```.env``` file and type ```DISCORD_TOKEN=...``` with '...' replaced by your Discord Bot Token
3. In CMD/Terminal, ```python main.py``` to start the program

## Goal

I created this bot as a Data Science project to record the activity of my friends and I on a platform that we all use. I wanted to be able to store this data into a ```.csv``` and sort the information, allowing my friends and I to reflect on how often we talked to each other virtually (This idea came from our experience with COVID-19 applying restrictions).
