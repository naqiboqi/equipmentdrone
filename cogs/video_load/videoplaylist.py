


import asyncio 

from random import randint
from time import gmtime, strftime
from .constants import emojis
from .video import Video



playlist_emoji = emojis.get("playlist")



class VideoNode:
    def __init__(self, content: Video, prev: "VideoNode"=None, next: "VideoNode"=None):
        self.content = content
        self.prev = prev
        self.next = next

    def __str__(self):
        """Returns a string representation of the video."""
        return (f"**[{self.content['title']}]({self.content['web_url']})** |"
            f"`{strftime('%H:%M:%S', gmtime(self.content['duration']))}`")



class VideoPlaylist:
    def __init__(self):
        self.now_playing: VideoNode = None
        self.head: VideoNode = None
        self.tail: VideoNode = None
        self.size = 0
        
        self.forward = True
        self.loop_one = False
        self.loop_all = False
        self.ready = asyncio.Event()
        
    def cleanup(self):
        self.head = None
        self.tail = None
        self.now_playing = None
        self.size = 0
        
        self.forward = True
        self.loop_one = False
        self.loop_all = False
        self.ready.clear()
        
    def set_loop_one(self):
        self.loop_all = False
        self.loop_one = not self.loop_one
        
        if self.now_playing:
            self.ready.set()
            
        return self.loop_one
    
    def set_loop_all(self):
        self.loop_one = False
        self.loop_all = not self.loop_all

        return self.loop_all

    async def _add_first(self, new_video):
        self.head = new_video
        self.tail = new_video
        self.now_playing = new_video
        self.ready.set()

    async def add_to_end(self, video: Video):
        new_video = VideoNode(video)

        if not self.head:
            await self._add_first(new_video)
        else:
            new_video.prev = self.tail
            self.tail.next = new_video
            self.tail = new_video
        
        self.size += 1
        if self.now_playing is None:
            self.now_playing = self.tail
            
        self.ready.set()
        
    async def add_to_front(self, video: Video):
        new_video = VideoNode(video)
        if not self.head:
            await self._add_first(new_video)
        else:
            self.head.prev = new_video
            new_video.next = self.head
            self.head = new_video
            
        self.size += 1
        
    def advance(self):
        """Advances to next video to play.
        
        If playing the previous, goes backwards and resets `self.forward`
        """
        if self.forward:
            self.move_forward()
        else:
            self.move_backward()

        self.forward = True

    def move_forward(self):
        """Moves to the next video in the playlist and sets it as current.
        
        If the player is looping the current video, replays it.
        
        If the player is looping the whole playlist and we are at the end,
        starts from the video.
        """
        if self.loop_one and self.now_playing:
            self.ready.set()
            return
        
        if not self.now_playing.next:
            if self.loop_all:
                self.now_playing = self.head
                self.ready.set()
            else:    
                self.ready.clear()
                
            return

        self.now_playing = self.now_playing.next
        self.ready.set()
        
    def backward(self):
        if not self.now_playing.prev:
            print("beginning of playlist")
            
            if self.loop_all:
                print("going back to end")
                self.now_playing = self.tail
            else:
                print("replaying first song")
                self.now_playing = self.head
            
        else:
            print(f"going backward from {self.now_playing}")
            self.now_playing = self.now_playing.prev
        
        print(f"now at {self.now_playing}")
        self.ready.set()
        
    async def replace_current(self, video: Video):
        next = self.now_playing.next
        prev = self.now_playing.prev
        self.now_playing = VideoNode(video, prev, next)
        
        # if this is the head
        if not self.now_playing.prev:
            self.head = self.now_playing
            print("is head")
        else:
            prev.next = self.now_playing
        
        # if this is the tail
        if not self.now_playing.next:
            self.tail = self.now_playing
            print("is tail")
        else:
            next.prev = self.now_playing

    def shuffle(self):
        if not self.head or self.head == self.tail:
            return

        def swap_nodes(node1, node2):
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
        
    def __iter__(self):
        current = self.head
        while current:
            yield current
            current = current.next

    def __str__(self):
        total_runtime = sum(node.content['duration'] for node in self)
        formatted_runtime = strftime('%H:%M:%S', gmtime(total_runtime))
        return f"**Upcoming Videos**: | Total runtime: {formatted_runtime}"
