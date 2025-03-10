### **Equipment Drone**
A Discord.py bot that can play music, games and roll dice! Let the Equipment Drone spice up your server life! 🎶🕹️🪩



#### Prerequisites:
-------------------

1. **Python 3.10+** **https://www.python.org/downloads/**

    * Make sure that Python is included under your `$PATH`

2. **Packages**
    * To install the necessary packages,
    run this command:
    `pip install -r path/to/requirements.txt` or
    `python -m install -r path/to/requirements.txt`

3. **FFMPEG**
    * `ffmpeg` can be downloaded from their official site **[here](https://ffmpeg.org/download.html)**

    * Their site only directly provides the source code, so I recommend checking the link dropdowns from the OS images, where you can find downloadable archives with the executable ready:

    ![alt text](/images/ffmpeg.png)

    * Within the downloaded archive, navitage to `./bin/ffmpeg.exe` and extract the `ffmpeg.exe` executable to the bot's directory


#### Further Setup
-------------------

1. You will need to create an application though the **[Discord Developer Portal](https://discordapp.com/developers/applications/me)**

    * Follow the instructions carefully, and when you get your token, *do not* share it with anyone else. This token is the key to what controls what your bot can (and cannot) do. 

2. Create a new file, `.env` in the bot's directory

3. Open your new `.env` file and make it look like the following, replace `your_token` with your bot's token

![alt text](/images/env.png)

After completing all of the above steps, the bot's directory should look like this (not including any `__pycache__`)

![alt text](/images/dir.png)


#### Using the bot
----------------------

* To start, run this command:
```python path/to/bot.py```

    * Make sure that the cwd for your terminal is in the bot's folder


**Commands**

The bot supports stardard prefix commands and hybrid commands.

I prefer hybrid commands, as only one bot will respond, and Discord will show a help string for the command when typing `/`.

You can also see all of the possible hybrid commands for any bot by typing `/[bot_name_here]`

![alt text](/images/all_slash.png)

Alternatively you can invoke commands via the bot's specific prefix `!`

Note that this will not allow to see the available commands, and if there are multiple bots on the server
that share this prefix `!` (and the command name), then *both* bots will respond.


#### Useful things
-------------------
**[Discord.py  documentation](https://discordpy.readthedocs.io/en/latest/)**

Contains everything you need to know about the `discord.py` library


#### To-Do
-----------
- [ ] Add seeking to media controls (this is difficult....)
- [X] Add looping and play previous to media controls
- [X] Make the bot smarter when attacking in battleship
- [X] Add grid labels to the board in battleship
- [X] Don't hardcode bot messages