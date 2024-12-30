"""
This module defines a `ProgressBar` class for visually representing the progress 
of a video.
"""

class ProgressBar():
    """Represents a video's progress bar with a slider denoting the elapsed time.
    
    Attributes:
    -----------
    `vid_length` (int): The length of the video, in seconds.
    `size` (int): The character length of the progress bar.
    `line` (str): The character used to represent the line.
    `slider` (str): The character used to represent the current time in the progress bar.
    """
    def __init__(self, vid_length: int):
        self.vid_length = vid_length
        self.size = 20
        self.line = "▬"
        self.slider = "🔘"

    def is_complete(self, elapsed_time: int):
        """Returns if whether video is completed or not.
        
        Params:
        ------
            elapsed_time (int): The elapsed time of the video, in seconds.
        """
        return elapsed_time >= self.vid_length

    def display(self, elapsed_time: int):
        """Returns a string representation of progress bar.
        
        Params:
        ------
            elapsed_time (int): The elapsed time of the video, in seconds.
        """
        if self.is_complete(elapsed_time):
            string_bar = self.line * (self.size - 1) + self.slider
            return string_bar
        else:
            percentage_elapsed = elapsed_time / self.vid_length
            progress_position = round(self.size * percentage_elapsed)
            remaining_time = self.size - progress_position

            progress_line_slider = "▶️ " + (self.line * progress_position) + self.slider
            remaining_line = self.line * remaining_time
            string_bar = progress_line_slider + remaining_line
            return string_bar
