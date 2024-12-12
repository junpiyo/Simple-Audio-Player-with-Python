import PIL.Image
from enum import IntEnum, auto
import pyaudio
from threading import Lock
import numpy as np
import time
import wave
import PIL.Image
from pydub import AudioSegment
from mutagen.id3 import ID3
from io import BytesIO
from common import *
import os


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


class Tag():
    def __init__(self, cover_art:PIL.Image=None, album:str=None, artist:str=None, title:str=None, lyrics:str=None):
        self.__cover_art = cover_art
        self.__album = album
        self.__artist = artist
        self.__title = title
        self.__lyrics = lyrics

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
    @property
    def lyrics(self):
        return self.__lyrics   


class Raw():
    def __init__(self,nchannels:int=None, samplewidth:int=None, framerate:int=None, frames:bytes=None, nframes:int=None):
        self.__nchannels = nchannels
        self.__samplewidth = samplewidth
        self.__framerate = framerate
        self.__frames = frames
        self.__nframes = nframes

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
    def frames(self):
        return self.__frames
    @property
    def current_pos(self):
        with self.__lock:
            return self.__current_pos
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


class Audio():
    def __init__(self, file_path:str):
        self.__file_path = file_path
        self.__raw:Raw = None
        self.__tag:Tag = None

    def open_file(self, is_audio:bool=False):
        if os.path.splitext(self.__file_path)[1] == '.wav':
            return self.__open_wav(is_audio)
        elif os.path.splitext(self.__file_path)[1] == '.mp3':
            return self.__open_mp3(is_audio)
        else:
            return False

    def __open_mp3(self, is_audio:bool=False):
        # load audio data
        if is_audio:
            try:
                mp3_data = AudioSegment.from_mp3(self.__file_path)
                framerate = mp3_data.frame_rate
                nchannels = mp3_data.channels
                samplewidth = mp3_data.sample_width
                frames = bytes(mp3_data.get_array_of_samples())
                nframes = round(len(frames) / samplewidth / nchannels)

                logging.info(f"{self.__file_path} has been loaded")
                logging.info(f'{nchannels}ch {samplewidth * 8}bit {framerate}Hz')
                self.__raw = Raw(nchannels, samplewidth, framerate, frames, nframes)
            
            except FileNotFoundError:
                logging.info(f"Error: cannot find {self.__file_path}")
                return False

        # load tags
        try:
            tags = ID3(self.__file_path)
            print(tags.pprint())

            attached_picture_data = tags.get("APIC:").data
            cover_art = PIL.Image.open(BytesIO(attached_picture_data))
            artist = tags.get('TPE1')
            album = tags.get('TALB')
            title = tags.get('TIT2')
            if title is None:
                title=os.path.splitext(os.path.basename(self.__file_path))[0]

            lyrics_keys = [key for key in tags.keys() if 'USLT' in key]
            if len(lyrics_keys) != 0:
                lyrics = tags.get(lyrics_keys[0])
            else:
                lyrics = None

            self.__tag = Tag(cover_art, album, artist, title, lyrics)
        except:
            logging.info("Error: cannot get some tags")
            return False
        
        return True

    def __open_wav(self, is_audio:bool=False):
        #load wave data
        if is_audio:
            try:
                wave_data = wave.open(self.__file_path, mode='rb')
                nchannels, samplewidth, framerate, nframes, _, _ = wave_data.getparams()
                frames = wave_data.readframes(-1)
                nframes = round(len(frames) / samplewidth / nchannels)

                logging.info(f"{self.__file_path} has been loaded")
                logging.info(f'{nchannels}ch {samplewidth * 8}bit {framerate}Hz')
                self.__raw = Raw(nchannels, samplewidth, framerate, frames, nframes)
            except FileNotFoundError:
                logging.info(f"Error: cannot find {self.__file_path}")
                return False

        # load tags
        self.__tag = Tag(title=os.path.splitext(os.path.basename(self.__file_path))[0])

        return True

    @property
    def file_path(self):
        return self.__file_path
    @property
    def raw(self):
        return self.__raw
    @property
    def tag(self):
        return self.__tag


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
            self.state = AudioPlayerState.CLOSED
        elif self.state == AudioPlayerState.CLOSING:
            self.state = AudioPlayerState.CLOSED

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
    
        volume = self.volume
        # volume =  0 if volume == 0 else 10 ** (volume / 50)
        nchannels = self.__audio.nchannels
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