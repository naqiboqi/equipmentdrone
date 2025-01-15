import asyncio 

from random import randint
from time import gmtime, strftime
from .video import Video



class VideoNode:
    def __init__(self, content: Video, prev: "VideoNode"=None, next: "VideoNode"=None):
        self.content = content
        self.prev = prev
        self.next = next

    async def get_embed(self):
        return self.content.get_embed()

    def __str__(self):
        return (f"**[{self.content['title']}]({self.content['web_url']})** |"
            f"`{strftime('%H:%M:%S', gmtime(self.content['duration']))}`")



class VideoPlaylist:
    def __init__(self):
        self.now_playing: VideoNode = None
        self.head: VideoNode = None
        self.tail: VideoNode = None
        self.size = 0
        
        self.forward = True
        self.ready = asyncio.Event()
        
    async def _add_first(self, new_video):
        self.head = new_video
        self.tail = new_video
        self.now_playing = new_video
        self.ready.set()

    async def add_to_end(self, video):
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
        
    async def add_to_front(self, video):
        new_video = VideoNode(video)
        if not self.head:
            await self._add_first(new_video)
        else:
            self.head.prev = new_video
            new_video.next = self.head
            self.head = new_video
            
        self.size += 1
        
    def advance(self):
        print("advancing")
        if self.forward:
            self.move_to_next()

    def move_to_next(self):
        if not self.now_playing.next:
            print("end of playlist")
            self.ready.clear()
            return
        
        print(f"going forward from {self.now_playing}")
        self.now_playing = self.now_playing.next
        print(f"now at {self.now_playing}")
        self.ready.set()
    
    def get_upcoming(self):
        descriptions: list[str] = []
        for spot, node in enumerate(self, 1):
            descriptions.append(f"{spot}. {node}")

        return descriptions
    
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
            self.head = self.head.next
            if self.head:
                self.head.prev = None
            else:
                self.tail = None
                
        elif spot == self.size:
            self.tail = self.tail.prev
            if self.tail:
                self.tail.next = None
            else:
                self.head = None
        else:    
            current = self.head
            for i in range(spot - 1):
                current = current.next
            
            removed = current.content
            prev = current.prev
            new_next = current.next
            prev.next = new_next
            new_next.prev = prev
            
            return removed
            
        self.size -= 1
        if self.size == 0:
            self.ready.clear()
            
    def cleanup(self):
        self.head = None
        self.tail = None
        self.now_playing = None
        self.size = 0
        
        self.forward = True
        self.ready.clear()
        
    def __iter__(self):
        current = self.head
        while current:
            yield current
            current = current.next

    def __str__(self):
        total_runtime = sum(node.content['duration'] for node in self)
        formatted_runtime = strftime('%H:%M:%S', gmtime(total_runtime))
        return f"({self.size}) | Total runtime: `{formatted_runtime}`"
