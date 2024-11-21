import PIL.Image
from enum import IntEnum, auto
import pyaudio
from threading import Lock

CHUNK_SIZE = 1024


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

    def read_frames(self, n:int) -> bytes: # returns at most n frames of audio
        if n < 0:
            return self.__frames

        c = self.__samplewidth * self.__nchannels
        start = round(self.__current_pos * c)
        end = start + round(n * c)
        self.__current_pos = self.__current_pos + n

        return self.__frames[start:end]

    def rewind(self):
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
        return self.__current_pos
    @property
    def frames(self):
        return self.__frames

    @current_pos.setter
    def current_pos(self, pos:int): # seeks to the specified position
        if pos >= self.__nframes:
            self.__current_pos = self.__nframes
        else:
            self.__current_pos = pos


class AudioPlayer():
    def __init__(self):
        self.__state_lock = Lock()
        self.__audio_lock = Lock()
        self.__state = AudioPlayerState.NOT_READY

    def load(self, audio:Audio):
        self.__audio = audio
        self.__state = AudioPlayerState.READY

    def play(self):
        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(self.__audio.samplewidth), channels=self.__audio.nchannels, rate=self.__audio.framerate, output=True)

            while True:
                print(self.__state)
                self.__state_lock.acquire()
                state = self.__state
                self.__state_lock.release()
                print(self.__state)
                if state != AudioPlayerState.PLAYING:
                    break
                print(self.__state)
                data = self.__audio.read_frames(CHUNK_SIZE)
                if len(data) == 0:
                    self.__audio.rewind()
                    self.__state_lock.acquire()
                    self.__state = AudioPlayerState.READY
                    self.__state_lock.release()
                    break
                stream.write(data)
            
            p.terminate()
        except:
            print('Error: cannot play the audio')
            return

    def forward(self):
        self.__audio_lock.acquire()
        self.__audio.current_pos = self.__audio.current_pos + 44100
        self.__audio_lock.release()

    @property
    def state(self):
        self.__state_lock.acquire()
        state = self.__state
        self.__state_lock.release()
        return state

    @state.setter
    def state(self, state:AudioPlayerState):
        self.__state_lock.acquire()
        self.__state = state
        self.__state_lock.release()
