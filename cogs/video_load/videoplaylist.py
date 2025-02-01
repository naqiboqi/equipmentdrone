"""
This module provides an implementation of a video playlist system. It supports dynamic playlist management 
through a doubly-linked list structure, offering efficient navigation, modification, 
and playback controls.

Key Features:
- **Video Playlist Management**:
    - Maintain a playlist of `Video` objects using a doubly-linked list.
    - Add videos to the front or end of the playlist.
    - Remove videos by position and shuffle the playlist.

- **Playback Controls**:
    - Navigate through the playlist with forward or backward movement.
    - Support for looping a single video or the entire playlist.
    - Efficiently handle the currently playing video and transitions.

- **Asynchronous Support**:
    - Use `asyncio` for efficient, non-blocking playlist operations.
    - Trigger playback readiness using asynchronous events.

### Classes:
- **`VideoNode`**:
    Represents a single node in the playlist. Manages:
    - Video metadata and playback information.
    - References to the previous and next nodes for efficient navigation.

- **`VideoPlaylist`**:
    Manages the playlist as a doubly-linked list. Features include:
    - Adding and removing videos dynamically.
    - Navigating through the playlist with support for looping and direction changes.
    - Shuffling and cleaning up the playlist.

### Dependencies:
- **`asyncio`**: For handling asynchronous playlist operations.
- **`random`**: For shuffling the playlist.
- **`time`**: For formatting video durations.
- **`constants`**: For accessing custom emoji constants.
- **`video`**: Represents the media source for playback.
"""



import asyncio 

from random import randint
from time import gmtime, strftime
from .constants import emojis
from .video import Video



playlist_emoji = emojis.get("playlist")


class VideoNode:
    """Represents a video in a playlist.
    
    Attributes:
    -----------
        content : Video
            The video stored in the node.
        prev : VideoNode
            The previous node in the playlist.
        next : VideoNode
            The next node in the playlist.
    """
    def __init__(self, content: Video, prev: "VideoNode"=None, next: "VideoNode"=None):
        self.content = content
        self.prev = prev
        self.next = next

    def __str__(self):
        """Returns a string representation of the video."""
        return (f"**[{self.content['title']}]({self.content['web_url']})** |"
            f"`{strftime('%H:%M:%S', gmtime(self.content['duration']))}`")



class VideoPlaylist:
    """Represents a video playlist by the form of a doubly-linked list.
    
    Attributes:
    -----------
        head : VideoNode
            The head node.
        tail : VideoNode
            The tail node.
        now_playing : VideoNode
            The currently playing node.
        size : int
            Size of the playlist.
        forward: bool
            If the playlist is progressing forward.
        loop_one : bool
            If the current video is looping.
        loop_all : bool
            If the playlist is looping.
        ready : asyncio.Event
            The """
    def __init__(self):
        self.head: VideoNode = None
        self.tail: VideoNode = None
        self.now_playing: VideoNode = None
        self.size = 0

        self.forward = True
        self.loop_one = False
        self.loop_all = False
        self.ready = asyncio.Event()

    def __iter__(self):
        """Allows iterating over the playlist."""
        current = self.head
        while current:
            yield current
            current = current.next

    def __str__(self):
        """Returns a string representation of the playlist."""
        total_runtime = sum(node.content['duration'] for node in self)
        formatted_runtime = strftime('%H:%M:%S', gmtime(total_runtime))
        return f"**Upcoming Videos** | Total Duration: `{formatted_runtime}`"

    def cleanup(self):
        """Clears the playlsit and resets its settings."""
        self.head = None
        self.tail = None
        self.now_playing = None
        self.size = 0

        self.forward = True
        self.loop_one = False
        self.loop_all = False
        self.ready.clear()

    def set_loop_one(self):
        """Tells the player to replay the currently playing video, if it exists."""
        self.loop_all = False
        self.loop_one = not self.loop_one

        return self.loop_one

    def set_loop_all(self):
        """Tells the player to replay the entire playlist."""
        self.loop_one = False
        self.loop_all = not self.loop_all

        if not self.now_playing:
            if self.head:
                self.now_playing = self.head
                self.ready.set()

        return self.loop_all

    async def _add_first_node(self, new_video: VideoNode):
        """Adds a node to an initially empty playlist.
        
        Params:
        -------
            new_video : VideoNode
                The new node to add.
        """
        self.head = new_video
        self.tail = new_video
        self.now_playing = new_video

        self.ready.set()

    async def add_to_end(self, video: Video):
        """Adds a video to the end of the playlist.
        
        Params:
        -------
            video: Video
                The video to add.
        """
        new_node = VideoNode(video)

        if not self.head:
            await self._add_first_node(new_node)
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node

        if not self.now_playing:
            self.now_playing = self.tail
            self.ready.set()

        self.size += 1

    def advance(self):
        """Advances to next video to play depending on the playlist's current direction (`self.forward`)."""
        if not self.now_playing:
            return

        if self.forward:
            self.move_forward()
        else:
            self.move_backward()

        self.forward = True

    def move_forward(self):
        """Moves to the next video in the playlist and sets it as the current.
        
        Loops the current video if `loop_one = True`, or replays the playlist
        from the beginning if `loop_all = True` and the playlist is over.
        """
        if self.loop_one:
            self.ready.set()
            return

        if self.now_playing == self.tail:
            self.ready.clear()

        self.now_playing = self.now_playing.next
        if not self.now_playing:
            if self.loop_all:
                self.now_playing = self.head
                self.ready.set()
                return
            else:
                return

        self.ready.set()

    def move_backward(self):
        """Moves to the previous video in the playlist and sets it as the current.
        
        In the case that `loop_all = True` and the first video is playing, moves to the last video in the playlist.
        Otherwise loops the current video if `loop_one = True`.
        """
        if self.loop_one:
            self.ready.set()
            return

        self.now_playing = self.now_playing.prev
        if not self.now_playing:
            if self.loop_all:
                self.now_playing = self.tail
                self.ready.set()
                return
            else:
                self.now_playing = self.head
                self.ready.set()
                return

        self.ready.set()

    async def replace_current(self, video: Video):
        """Replaces the current video's source with a new source.
        
        This is because the original stream is depleted, and for replaying videos,
        requires an unplayed stream.
        
        Params:
        -------
            video : Video
                The video with the unplayed stream.
        """
        self.now_playing.content = video

    def shuffle(self):
        """Shuffles the playlist."""
        if not self.head or self.head == self.tail:
            return

        def swap_nodes(node1: VideoNode, node2):
            """Swaps the content of two nodes."""
            node1.content, node2.content = node2.content, node1.content

        current = self.head
        for i in range(self.size):
            swap_index = randint(i, self.size - 1)
            target = current

            for _ in range(swap_index - i):
                target = target.next

            swap_nodes(current, target)
            current = current.next

    def remove(self, spot: int):
        """Removes a video at the given spot in the playlist.
        
        Raises an `IndexError` if no video exists at that spot.
        
        Params:
        -------
            spot : int
                The spot to remove the video from.
        """
        if not self.head:
            raise IndexError("The playlist is empty.")

        if not 1 <= spot <= self.size:
            raise IndexError("That spot does not exist in the playlist.")
        elif spot == 1:
            removed = self.head
            self.head = self.head.next
            if self.head:
                self.head.prev = None
            else:
                self.tail = None

        elif spot == self.size:
            removed = self.tail
            self.tail = self.tail.prev
            if self.tail:
                self.tail.next = None
            else:
                self.head = None
        else:    
            current = self.head
            for i in range(spot - 1):
                current = current.next

            removed = current
            prev = current.prev
            new_next = current.next
            prev.next = new_next
            new_next.prev = prev

        self.size -= 1
        if self.size == 0:
            self.ready.clear()

        return removed.content

    def get_upcoming(self):
        """Returns a numbered list of upcoming videos with their descriptions."""
        descriptions: list[str] = []
        for spot, node in enumerate(self, 1):
            descriptions.append(f"{spot}. {node}")

        return descriptions
