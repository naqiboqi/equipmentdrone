"""
This module defines a `ProgressBar` class for visually representing the progress 
of a video.
"""


from .constants import emojis



play_emoji = emojis.get("play")
circle_emoji = emojis.get("play_circle")
remaining_emoji = emojis.get("remaining_line")
elapsed_emoji = emojis.get("elapsed_line")



class ProgressBar():
    """Represents a video's progress bar with a slider denoting the elapsed time.

    Attributes:
    -----------
    vid_length: float
        The length of the tracked video, in seconds.
    size: int
        The length of the progress bar (in number of symbols).
    """
    def __init__(self, vid_length: float):
        self.vid_length = vid_length
        self.size = 14

    def is_complete(self, elapsed_time: float):
        """Returns if whether the video is completed or not.

        Params:
        ------
            elapsed_time: float
                The elapsed time of the video, in seconds.
        """
        return elapsed_time >= self.vid_length

    def get_progress(self, elapsed_time: float):
        """Returns a string representation of progress bar with the current progress of the video.

        Params:
        ------
            elapsed_time: float
                The elapsed time of the video, in seconds.
        """
        
        if self.is_complete(elapsed_time):
            string_bar = play_emoji + elapsed_emoji * self.size + circle_emoji
            return string_bar
        else:
            percentage_elapsed = elapsed_time / self.vid_length
            progress_position = round(self.size * percentage_elapsed)
            remaining_time = self.size - progress_position

            elapsed_line = play_emoji + (elapsed_emoji * progress_position) + circle_emoji
            remaining_line = remaining_emoji * remaining_time
            string_bar = elapsed_line + remaining_line
            return string_bar
