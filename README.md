# LoggerBot

Discord bot using the Discord.py API to record user data for the application's communities.

## Current Version (v2.2)

- LoggerBot records and stores:
  - Dates of Activity
  - Discord IDs and current Discord usernames
  - Durations of time in a voice channel
  - Integers of messages sent per day
  - ```times.pkl``` file enables ability to restart bot while people in voice call (data stored)
- LoggerBot Commands
  - ```!voice Day|Total``` prints the user's time within voice chats with H:M:S format 
  - ```!graph Day|Total``` sends a bar graph png, comparing user data to server's

*LoggerBot can only record data from channels that it can see*

## How To Use

1. In CMD/Terminal, ```git clone https://github.com/SamJSui/LoggerBot``` to clone the files to your current directory
2. In the directory, create a ```.env``` file and type ```DISCORD_TOKEN=...``` with '...' replaced by your Discord Bot Token
3. In CMD/Terminal, ```python main.py``` to start the program

## Goal

- During the peak of COVID-19, in-person meetings were seldom held. This led many circles of friends to Discord or other online apps.
- This Data Science project was created to collect activity within the Discord server, allowing us to reflect on our past, in the future, in the form of data.

### Edits
- (v2.2) ```!graph and !voice (Day|Total)```
- Modularized the column summation for different test cases into one function
- Fixed edge case where ```!voice``` did not portray accurate time in chat until the person left
- (v2.1.4) ```times.pkl``` stores current time data in seconds (in case bot needs to be restarted)
- Sets up for bot commands (previous sorting error) - v2.1.4 added ```!voice``` command
- Prints to console every new entry
- Records duration of user presence within voice channel
- ~~(v2.1.3) Cleans up repeated code~~
- ~~(v2.1.2) Edge case for post-midnight events~~
- ~~Records new members in the .csv~~
- ~~User ID : Name storage in a .pkl~~
- ~~Activity in voice channel stored as boolean for each day~~
