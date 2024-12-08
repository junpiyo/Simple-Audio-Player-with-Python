import PIL.Image
from enum import IntEnum, auto
import pyaudio
from threading import Lock, Event
import numpy as np
import time
from common import *



class AudioPlayerState(IntEnum):
    PLAYING = auto()
    POSED = auto()
    READY = auto()
    NOT_READY = auto()
    CLOSING = auto()
    CLOSED = auto()


class AudioPlayerInstruction(IntEnum):
    PLAY = auto()
    POSE = auto()
    CLOSE = auto()
    STOP = auto()


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
                self.__current_pos = self.__nframes
            elif pos < 0:
                self.__current_pos = 0
            else:
                self.__current_pos = pos

            self.__next_pos = self.__current_pos


class AudioPlayer():
    def __init__(self, volume=100, loop=True):
        self.__volume = volume
        self.__loop = loop
        self.__state_lock = Lock()
        self.__volume_lock = Lock()
        self.__loop_lock = Lock()
        self.__instruction_lock = Lock()
        self.__instruction = AudioPlayerInstruction.STOP
        self.__state = AudioPlayerState.NOT_READY
        logging.info(f'instruction: {self.instruction.name}, state: {self.state.name}')

    def load(self, audio:Audio):
        self.__audio = audio
        self.state = AudioPlayerState.READY
        logging.info(f'instruction: {self.instruction.name}, state: {self.state.name}')

    def close(self):
        if self.state == AudioPlayerState.PLAYING:
            self.instruction = AudioPlayerInstruction.CLOSE
            self.state = AudioPlayerState.CLOSING
        elif self.state == AudioPlayerState.POSED:
            self.instruction = AudioPlayerInstruction.CLOSE
            self.state = AudioPlayerState.CLOSING
        elif self.state == AudioPlayerState.READY:
            self.instruction = AudioPlayerInstruction.CLOSE
            self.state = AudioPlayerState.CLOSING
        elif self.state == AudioPlayerState.NOT_READY:
            pass
        elif self.state == AudioPlayerState.CLOSING:
            pass

    def loop_for_playback(self):        
        while True:
            self.__play()
            if self.instruction == AudioPlayerInstruction.CLOSE:
                self.state = AudioPlayerState.CLOSED
                break

            if not self.__loop:
                break

    def __play(self):
        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(self.__audio.samplewidth),
                            channels=self.__audio.nchannels, rate=self.__audio.framerate,
                            frames_per_buffer=CHUNK_SIZE*10, output=True)

            # loop for play
            while True:
                if self.__instruction == AudioPlayerInstruction.CLOSE:
                    self.state = AudioPlayerState.CLOSING
                    logging.info(f'instruction: {self.instruction.name}, state: {self.state.name}')
                    break

                if self.__instruction == AudioPlayerInstruction.POSE:
                    self.state = AudioPlayerState.POSED
                    logging.info(f'instruction: {self.instruction.name}, state: {self.state.name}')
                    while True:
                        if self.__instruction != AudioPlayerInstruction.POSE:
                            break
                        time.sleep(0.1)

                if self.__instruction == AudioPlayerInstruction.STOP:
                    self.state = AudioPlayerState.READY
                    logging.info(f'instruction: {self.instruction.name}, state: {self.state.name}')
                    while True:
                        if self.__instruction != AudioPlayerInstruction.STOP:
                            break
                        time.sleep(0.1)

                if self.__instruction == AudioPlayerInstruction.PLAY:
                    self.state = AudioPlayerState.PLAYING
                    logging.info(f'instruction: {self.instruction.name}, state: {self.state.name}')

                    data = self.__audio.read_frames(CHUNK_SIZE)
                    if len(data) == 0:
                        self.__audio.rewind()
                        self.state = AudioPlayerState.READY
                        logging.info(f'instruction: {self.instruction.name}, state: {self.state.name}')
                        break
                    stream.write(self.__controll_volume(data))
            
            stream.close()
            p.terminate()

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

    def __controll_volume(self, data:bytes):
        if data == []:
            return data
        
        volume = self.volume
        if volume == 100:
            return data
    
        volume =  0 if volume == 0 else 10 ** (volume / 50)
        nchannels = self.__audio.nchannels
        volume = self.volume
        channels = [np.frombuffer(data, dtype=np.int16)[i::nchannels] for i in range(nchannels)]
        channels = [channel.astype(dtype=np.float32) * volume / 100 for channel in channels]
        channels = [channel.astype(dtype=np.int16) for channel in channels]
        
        return np.column_stack(channels).tobytes()

    @property
    def state(self):
        with self.__state_lock:
            return self.__state

    @state.setter
    def state(self, state:AudioPlayerState):
        with self.__state_lock:
            self.__state = state

    @property
    def instruction(self):
        with self.__instruction_lock:
            return self.__instruction

    @instruction.setter
    def instruction(self, instruction:AudioPlayerInstruction):
        with self.__instruction_lock:
            self.__instruction = instruction

    @property
    def volume(self):
        with self.__volume_lock:
            return self.__volume

    @volume.setter
    def volume(self, volume:int):
        volume = 0 if volume < 0 else volume
        volume = volume if volume < 100 else 100
        with self.__volume_lock:
            self.__volume = volume

    @property
    def loop(self):
        with self.__loop_lock:
            return self.__loop

    @loop.setter
    def loop(self, loop:bool):
        with self.__loop_lock:
            self.__loop = loop