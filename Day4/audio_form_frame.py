import customtkinter
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from audio import Audio, AudioPlayerState
from common import *
import time


AUDIO_FORM_RADIUS = 0.5 # sec
AUDIO_FORM_SUB_SAMPLES = 10


def lowpass_filter(input:np.ndarray, cutoff_frequency, mode="Lanczos2") -> np.ndarray:
    if mode == "Lanczos2":
        return lanczos2(input, cutoff_frequency)
    elif mode == "Lanczos3":
        return lanczos3(input, cutoff_frequency)
    else:
        return input

def lanczos2(input:np.ndarray, cutoff_frequency) -> np.ndarray:
    if cutoff_frequency >= 0.5:
        return input
    
    W = 2 * math.pi * cutoff_frequency
    filter_r = math.ceil(1/cutoff_frequency)
    filter_coeffs = [math.sin(0.5*W*t)/(0.5*W*t) * math.sin(W*t)/(W*t)  if t!=0 else 1 for t in range(-filter_r, filter_r+1)]
    filter_coeffs = np.array(filter_coeffs)
    # print(filter_coeffs.shape, np.sum(filter_coeffs), cutoff_frequency)
    return np.convolve(input, filter_coeffs/np.sum(filter_coeffs), mode="same")

def lanczos3(input:np.ndarray, cutoff_frequency) -> np.ndarray:
    if cutoff_frequency >= 0.5:
        return input
    
    W = 2 * math.pi * cutoff_frequency
    filter_r = math.ceil(1.5/cutoff_frequency)
    filter_coeffs = [math.sin(W*t/3)/(W*t/3) * math.sin(W*t)/(W*t)  if t!=0 else 1 for t in range(-filter_r, filter_r+1)]
    filter_coeffs = np.array(filter_coeffs)
    return np.convolve(input, filter_coeffs/np.sum(filter_coeffs), mode="same")


class AudioFormFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.__fig, self.__ax = plt.subplots(figsize=(4, 1), dpi=100, tight_layout=True, facecolor='#2B2B2B')
        self.__ax.axis("off")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.__canvas = FigureCanvasTkAgg(self.__fig, master=self)
        self.__canvas.get_tk_widget().grid(row=0, column=0, padx=(5, 5), pady=(5, 5), sticky='WE')

    def load(self, audio:Audio):
        self.__audio = audio
        audio_framerate = self.__audio.framerate
        nchannels = self.__audio.nchannels
        frames = np.frombuffer(self.__audio.frames, dtype=np.int16)[::nchannels]

        subsampled_frames = lowpass_filter(frames, 0.5 / AUDIO_FORM_SUB_SAMPLES)[::AUDIO_FORM_SUB_SAMPLES]

        self.__audio_form_radius = math.ceil(AUDIO_FORM_RADIUS * audio_framerate / AUDIO_FORM_SUB_SAMPLES)
        self.__frames = np.pad(subsampled_frames, (self.__audio_form_radius, self.__audio_form_radius), 'constant')
        self.__frames = self.__frames / self.__frames.max()

        self.update_audio_form()

    def __read_frames(self, pos):
        if pos >= self.__audio.nframes:
            return None
        pos_in_audio_form = math.floor(pos / AUDIO_FORM_SUB_SAMPLES)

        start = pos_in_audio_form
        end = start + 2 * self.__audio_form_radius + 1

        return self.__frames[start:end]

    def update_audio_form(self):
        current_pos = self.__audio.current_pos
        y = self.__read_frames(current_pos)
        if y is None:
            return

        x = np.arange(-self.__audio_form_radius, self.__audio_form_radius + 1)

        self.__ax.cla()
        self.__ax.axis('off')
        self.__ax.set_xlim(-self.__audio_form_radius, self.__audio_form_radius)
        self.__ax.set_ylim(-1, 1)
        self.__ax.vlines(0, -1, 1, colors='#888888', linewidth=1.5)
        self.__ax.plot(x, y)

        self.__canvas.draw()
        # self.__canvas.flush_events()
        # self.update()
