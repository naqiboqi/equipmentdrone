#### Prerequisites:
-------------------

1. **Python 3.10+** https://www.python.org/downloads/

    * Make sure that Python is included under your `$PATH`

2. **Packages**
    * To install the necessary packages,
    run this command:
    `pip install -r path/to/requirements.txt` or
    `python -m install -r requirements.txt`

3. **FFMPEG**
    * `ffmpeg` is used by the bot to play audio streams to a voice channel, so it can be skipped if you have no intention of playing media


    * Can be downloaded from their official site [here](https://ffmpeg.org/download.html  )

    * The folks at `ffmpeg` only provide the source code, so I recommend checking the links that provide it already compiled and ready


    * Within the downloaded archive, navitage to `./bin/ffmpeg.exe` and extract that executable to the bot's directory


#### Further Setup
-------------------

1. You will need to create an application though the [Discord Developer Portal](https://discordapp.com/developers/applications/me)

    * Follow the instructions carefully, and when you get your token, *do not* share it with anyone else. This token is the key to what controls what your bot can (and cannot) do. 

2. Create a new file, `.env` in the bot's directory.

3. Type this into your new file, `DISCORD_TOKEN = your_token`, and paste your bot's token where it says `your_token`


#### Using the bot
----------------------

* Run this command:
```python path/to/bot.py```

    * Make sure that the cwd for your terminal is in the bot's folder

* Using commands:

The bot supports stardard prefix commands and ~~slash~~ hybrid commands. Personally I prefer hybrid commands, as Discord will show a help string for each command (and autocomplete)


Example hybrid command usage:
    # Placeholder

Example prefix command usage:
    # Placeholder


#### Useful things
-------------------
* [Discord.py  documentation](https://discordpy.readthedocs.io/en/latest/)

    * Contains everything you need to know about the `discord.py` library


#### Roadmap
-------------
- [ ] Add seeking to media controls
- [ ] Complete battleship implementation
- [ ] Host the bot with Docker