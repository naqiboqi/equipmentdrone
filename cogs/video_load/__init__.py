"""
The `video_load` package. Includes classes and utilities for handling `video` playback,
queue management, and embed creation.
"""



from .constants import emojis
from .eq import Eq
from .progress import ProgressBar
from .video import Video
from .videoplayer import VideoPlayer
from .videoplaylist import VideoPlaylist



LYRICS_URL = "https://some-random-api.ml/lyrics?title="
"""API url for getting video lyrics."""