import PIL.Image
from enum import IntEnum, auto
import pyaudio
from threading import Lock, Event
from common import *


class AudioPlayerState(IntEnum):
    PLAYING = auto()
    POSED = auto()
    TEMPORARY_POSED = auto()
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
    def __init__(self, nchannels:int, samplewidth:int, framerate:int, frames:bytes):
        self.__nchannels = nchannels
        self.__samplewidth = samplewidth
        self.__framerate = framerate
        self.__frames = frames
        self.__nframes = round(len(frames) / samplewidth / nchannels)
        self.__current_pos = 0
        self.__next_pos = 0
        self.__lock = Lock()

    def read_frames(self, n:int) -> bytes: # returns at most n frames of audio
        with self.__lock:
            start = self.__next_pos
            end = start + n
            if end > self.__nframes:
                end = self.__nframes
                
            self.__current_pos = start
            self.__next_pos = end

        c = self.__samplewidth * self.__nchannels
        start = round(start * c)
        end = round(end * c)
        return self.__frames[start:end]

    def rewind(self):
        with self.__lock:
            self.__current_pos = 0
            self.__next_pos = 0

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
                self.__current_pos = 0
            elif pos < 0:
                self.__current_pos = 0
            else:
                self.__current_pos = pos

            self.__next_pos = self.__current_pos


class AudioPlayer():
    def __init__(self):
        self.__state_lock = Lock()
        self.__state = AudioPlayerState.NOT_READY

    def load(self, audio:Audio, event_for_play: Event):
        self.__audio = audio
        self.__event_for_play = event_for_play
        self.__state = AudioPlayerState.READY

    def close(self):
        self.__state = AudioPlayerState.NOT_READY

    def play(self):
        if self.state != AudioPlayerState.NOT_READY:
            self.state = AudioPlayerState.PLAYING
        
        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(self.__audio.samplewidth),
                            channels=self.__audio.nchannels, rate=self.__audio.framerate,
                            frames_per_buffer=CHUNK_SIZE*4, output=True)

            while True:
                if self.state == AudioPlayerState.NOT_READY:
                    break
                if not self.__event_for_play.is_set():
                    if self.state != AudioPlayerState.TEMPORARY_POSED:
                        self.state = AudioPlayerState.POSED
                    self.__event_for_play.wait()
                    if self.state != AudioPlayerState.NOT_READY:
                        self.state = AudioPlayerState.PLAYING

                if self.state == AudioPlayerState.PLAYING:
                    data = self.__audio.read_frames(CHUNK_SIZE)
                    if len(data) == 0:
                        self.__audio.rewind()
                        break
                    stream.write(data)
            
            stream.close()
            p.terminate()

            if self.state != AudioPlayerState.NOT_READY:
                self.state = AudioPlayerState.READY

        except:
            print('Error: cannot play the audio')
            return

    def forward(self):
        offset = round(self.__audio.framerate * TIME_OFFSET)
        next_pos = self.__audio.current_pos + offset
        self.__audio.current_pos = next_pos

    def backward(self):
        offset = round(self.__audio.framerate * TIME_OFFSET)
        next_pos = self.__audio.current_pos - offset
        self.__audio.current_pos = next_pos

    @property
    def state(self):
        with self.__state_lock:
            return self.__state

    @state.setter
    def state(self, state:AudioPlayerState):
        with self.__state_lock:
            self.__state = state
