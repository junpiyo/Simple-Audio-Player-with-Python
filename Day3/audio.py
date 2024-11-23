import PIL.Image
from enum import IntEnum, auto
import pyaudio
from threading import Lock
# from multiprocessing import Lock

CHUNK_SIZE = 1024
TIME_OFFSET = 2 # sec


class AudioPlayerState(IntEnum):
    PLAYING = auto()
    POSED = auto()
    READY = auto()
    NOT_READY = auto()


class AudioTag():
    def __init__(self, cover_art:PIL.Image=None, album:str=None, artist:str=None, title:str=None):
        self.__cover_art = cover_art
        self.__album = album
        self.__artist = artist
        self.__title = title

    @property
    def cover_art(self):
        return self.__cover_art
    @property
    def album(self):
        return self.__album
    @property
    def artist(self):
        return self.__artist
    @property
    def title(self):
        return self.__title


class Audio():
    def __init__(self, nchannels:int, samplewidth:int, framerate:int, frames:bytes, album:str=None, artist:str=None, title:str=None):
        self.__nchannels = nchannels
        self.__samplewidth = samplewidth
        self.__framerate = framerate
        self.__frames = frames
        self.__nframes = round(len(frames) / samplewidth / nchannels)
        self.__current_pos = 0
        self.__lock = Lock()

    def read_frames(self, n:int) -> bytes: # returns at most n frames of audio
        with self.__lock:
            start = self.__current_pos
            end = start + n
            if end > self.__nframes:
                end = self.__nframes

        self.__current_pos = end

        c = self.__samplewidth * self.__nchannels
        start = round(start * c)
        end = round(end * c)
        return self.__frames[start:end]

    def rewind(self):
        with self.__lock:
            self.__current_pos = 0

    @property
    def nchannels(self):
        return self.__nchannels
    @property
    def samplewidth(self):
        return self.__samplewidth
    @property
    def framerate(self):
        return self.__framerate
    @property
    def samplewidth(self):
        return self.__samplewidth
    @property
    def nframes(self):
        return self.__nframes
    @property
    def current_pos(self):
        with self.__lock:
            return self.__current_pos
    @property
    def frames(self):
        return self.__frames

    @current_pos.setter
    def current_pos(self, pos:int): # seeks to the specified position
        with self.__lock:
            if pos >= self.__nframes:
                self.__current_pos = self.__nframes
            else:
                self.__current_pos = pos


class AudioPlayer():
    def __init__(self):
        self.__state_lock = Lock()
        self.__state = AudioPlayerState.NOT_READY

    def load(self, audio:Audio):
        self.__audio = audio
        self.__state = AudioPlayerState.READY

    def play(self):
        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(self.__audio.samplewidth), channels=self.__audio.nchannels, rate=self.__audio.framerate, output=True)

            while True:
                data = self.__audio.read_frames(CHUNK_SIZE)
                if len(data) == 0:
                    self.__audio.rewind()
                    break
                stream.write(data)

                if self.state != AudioPlayerState.PLAYING:
                    break
            
            stream.close()
            p.terminate()
            self.state = AudioPlayerState.READY
        except:
            print('Error: cannot play the audio')
            return

    def forward(self):
        offset = round(self.__audio.framerate * TIME_OFFSET)
        next_pos = self.__audio.current_pos + offset
        next_pos = next_pos if next_pos < self.__audio.nframes else 0
        self.__audio.current_pos = next_pos

    def backward(self):
        offset = round(self.__audio.framerate * TIME_OFFSET)
        next_pos = self.__audio.current_pos - offset
        next_pos = 0 if next_pos < 0 else next_pos
        self.__audio.current_pos = next_pos

    @property
    def state(self):
        with self.__state_lock:
            return self.__state

    @state.setter
    def state(self, state:AudioPlayerState):
        with self.__state_lock:
            self.__state = state
