#### Prerequisites:

1. **Python 3.10+** https://www.python.org/downloads/

    Make sure that Python is included under your `$PATH`

2. **Packages**
    To install the necessary packages,
    run this command:
    `pip install -r path/to/requirements.txt` or
    `python -m install -r requirements.txt`

3. **FFMPEG**
    `ffmpeg` is used by the bot to play audio streams to a voice channel, so it can be skipped if you have no intention of playing media

    Can be downloaded from their official site here: https://ffmpeg.org/download.html

    The folks at `ffmpeg` only provide the source code, so I recommend checking the links that provide it already compiled and ready

    With the downloaded archive, navitage to `./bin/ffmpeg.exe` and extract that executable to the bot's directory


#### Further Setup

1. You will need to create an application on the Discord developer portal through here: https://discordapp.com/developers/applications/me

    * Follow the instructions carefully, and when you get your token, *do not* share it with anyone else. This token is the key to what controls what your bot can (and cannot) do. 

    * If your token is compromised, you can regenerate your token, but also inform the admin(s) of any server(s) the bot was present on so that they may remove it

2. Create a new file, `.env` in the bot's directory.

3. Type this into your new file, `DISCORD_TOKEN = your_token`, and paste your bot's token where it says `your_token`

#### Starting the bot

Run this command:
```python path/to/./bot.py```

Make sure that the cwd for your terminal is in the bot's folder


#### Useful things
* `discord.py(rewrite)` documentation
https://discordpy.readthedocs.io/en/latest/

Contains everything you need to know about the `discord.py` library


#### Roadmap

- [ ] Add seeking to media controls
- [ ] Complete battleship implementation
- [ ] Host the bot with Docker