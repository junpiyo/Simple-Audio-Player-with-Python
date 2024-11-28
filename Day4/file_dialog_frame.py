import customtkinter
import os
import wave
from io import BytesIO
import PIL
from pydub import AudioSegment
from mutagen.id3 import ID3
from audio import Audio, AudioTag
from common import *


class FileDialogFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # widgets
        self._input_path_entry = customtkinter.CTkEntry(self, font=(FONT_TYPE, FONT_SIZE, 'normal'), state='readonly')
        self._browse_button = customtkinter.CTkButton(self, width=30, font=(FONT_TYPE, FONT_SIZE, 'bold'), text='Browse', command=self._browse)
        
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self._input_path_entry.grid(row=0, column=1, padx=(10, 0), pady=(10, 10), sticky="WE")
        self._browse_button.grid(row=0, column=2, padx=(5, 10), pady=(10, 10), sticky="E")

    def _browse(self):
        input_path = customtkinter.filedialog.askopenfilename(filetypes=[("Audio File", "*.wav;*.mp3")])
        if input_path is None:
            return
        
        self._input_path_entry.configure(state="normal")
        self._input_path_entry.delete(0, customtkinter.END)
        self._input_path_entry.insert(0, input_path)
        self._input_path_entry.configure(state="readonly")
        
        if os.path.splitext(input_path)[1] == '.wav':
            audio, tags =  self._open_wav(input_path)
        elif os.path.splitext(input_path)[1] == '.mp3':
            audio, tags =  self._open_mp3(input_path)
        else:
            return

        if audio != None:
            self.master.load(audio, tags)

    def _open_mp3(self, input_path:str):
        try:
            mp3_data = AudioSegment.from_mp3(input_path)
            framerate = mp3_data.frame_rate
            nchannels = mp3_data.channels
            samplewidth = mp3_data.sample_width
            frames = bytes(mp3_data.get_array_of_samples())
            
        except FileNotFoundError:
            print(f"Error: cannot find {input_path}")
            return None

        print(f"{input_path} has been loaded")
        print(f'{nchannels}ch {samplewidth * 8}bit {framerate}Hz')

        try:
            tags = ID3(input_path)
            print(tags.pprint())

            attached_picture_data = tags.get("APIC:").data
            cover_art = PIL.Image.open(BytesIO(attached_picture_data))
            artist = tags.get('TPE1')
            album = tags.get('TALB')
            title = tags.get('TIT2')
            return Audio(nchannels, samplewidth, framerate, frames), AudioTag(cover_art, album, artist, title)
        except:
            print("Error: cannot get any tags")
            return Audio(nchannels, samplewidth, framerate, frames), AudioTag(title=os.path.basename(input_path))

    def _open_wav(self, input_path:str):
        try:
            wave_data = wave.open(input_path, mode='rb')
            nchannels, samplewidth, framerate, nframes, _, _ = wave_data.getparams()
            frames = wave_data.readframes(-1)
        except FileNotFoundError:
            print(f"Error: cannot find {input_path}")
            return None

        print(f"{input_path} has been loaded")
        print(f'{nchannels}ch {samplewidth * 8}bit {framerate}Hz')
        return Audio(nchannels, samplewidth, framerate, frames), AudioTag(title=os.path.basename(input_path))
    