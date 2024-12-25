class ProgressBar():
    """Represents a video's progress bar with a slider denoting the elapsed time."""
    def __init__(self, vid_length: int):
        self.vid_length = vid_length
        self.size = 20
        self.line = "▬"
        self.slider = "🔘"
        
    def is_complete(self, elapsed_time: float):
        """Returns a bool representing if the video is completed."""
        return elapsed_time >= self.vid_length

    def display(self, elapsed_time: float):
        """Returns a string representation of progress bar."""
        if self.is_complete(elapsed_time):
            string_bar = self.line * (self.size - 1) + self.slider
            return string_bar
        else:
            percentage_elapsed = elapsed_time / self.vid_length
            current_progress = round(self.size * percentage_elapsed)
            remaining_time = self.size - current_progress
            
            progress_line_slider = "▶️ " + (self.line * current_progress) + self.slider
            remaining_line = self.line * remaining_time
            string_bar = progress_line_slider + remaining_line
            return string_bar