import customtkinter
import PIL.Image
import wave
import pyaudio
import os


MAIN_WINDOW_HEIGHT = 600
MAIN_WINDOW_WIDTH = 400
FONT_TYPE = 'Yu Gothic'
FONT_SIZE = 16
CHUNK_SIZE = 1024


class CoverArtDisplayFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # cover art
        self.__cover_art_height = 300
        self.__cover_art_width = 300
        self.__default_cover_art_light_image_path = '../Image/default_cover_art_light.png'
        self.__default_cover_art_dark_image_path = '../Image/default_cover_art_dark.png'
        try:
            self._default_light_image = PIL.Image.open(self.__default_cover_art_light_image_path)
        except FileNotFoundError:
            self._default_light_image = None
            print(f'Error: cannot find {self.__default_cover_art_light_image_path}')
        try:
            self._default_dark_image = PIL.Image.open(self.__default_cover_art_dark_image_path)
        except FileNotFoundError:
            self._default_dark_image = None
            print(f'Error: cannot find {self.__default_cover_art_dark_image_path}')

        # wights
        self._cover_art_display_label = customtkinter.CTkLabel(
            self,
            width=self.__cover_art_width, height=self.__cover_art_height, corner_radius=6,
            font=(FONT_TYPE, FONT_SIZE, 'normal'), text='The cover art of a audio is to be displayed...'
        )
        self._audio_title_label = customtkinter.CTkLabel(self, font=(FONT_TYPE, FONT_SIZE+4, 'bold'), text='Title', anchor='center')
        self._audio_album_and_artist_label = customtkinter.CTkLabel(self, font=(FONT_TYPE, FONT_SIZE-2, 'normal'), text='Album/Artist', anchor='center')

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self._cover_art_display_label.grid(row=0, column=0, padx=(10, 10), pady=(5, 10), sticky='NSWE', columnspan=2)
        self._audio_title_label.grid(row=1, column=0, padx=(10, 10), pady=(5, 0), sticky='WE', columnspan=2)
        self._audio_album_and_artist_label.grid(row=2, column=0, padx=(10, 10), pady=(5, 10), sticky='WE')

    def set_cover_art(self):
        if self._default_light_image is None and self._default_dark_image is None:
            None
        else:
            self._cover_art_display_label.configure(image=customtkinter.CTkImage(light_image=self._default_light_image, dark_image=self._default_dark_image, size=(250, 300)))
            self._cover_art_display_label.configure(text='')

    def set_audio_title(self, title:str=None):
        if title is None:
            title = 'Title'
        self._audio_title_label.configure(text=title)


class Audio():
    def __init__(self, nchannels:int, samplewidth:int, framerate:int, frames:bytes, album:str=None, artist:str=None, title:str=None):
        self.__nchannels = nchannels
        self.__samplewidth = samplewidth
        self.__framerate = framerate
        self.__frames = frames
        self.__nframes = round(len(frames) / samplewidth / nchannels)
        self.__current_pos = 0

    def read_frames(self, n:int) -> bytes: # returns at most n frames of audio
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


class AudioPlayerControllerFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._audio = None

        self._audio_play_button = customtkinter.CTkButton(
            self,
            image=None, hover=True,
            text='Play', font=(FONT_TYPE, FONT_SIZE+2, 'normal'),
            height=40, width=40, corner_radius=6,
            state='disabled',
            command=lambda: self.__play()
        )
        self._audio_pose_button = customtkinter.CTkButton(
            self,
            image=None, hover=True,
            text='Pose', font=(FONT_TYPE, FONT_SIZE+2, 'normal'),
            height=40, width=40, corner_radius=6,
            state='disabled',
            command=lambda: print('not implemented')
        )
        self._audio_forward_button = customtkinter.CTkButton(
            self,
            image=None, hover=True,
            text='>>', font=(FONT_TYPE, FONT_SIZE+2, 'normal'),
            height=40, width=40, corner_radius=6,
            state='disabled',
            command=lambda: print('not implemented')
        )
        self._audio_backward_button = customtkinter.CTkButton(
            self,
            image=None, hover=True,
            text='<<', font=(FONT_TYPE, FONT_SIZE+2, 'normal'),
            height=40, width=40, corner_radius=6,
            state='disabled',
            command=lambda: print('not implemented')
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=1)
        self._audio_backward_button.grid(row=0, column=0, padx=(0, 5), pady=(0, 0), sticky='E')
        self._audio_play_button.grid(row=0, column=1, padx=(5, 5), pady=(0, 0))
        self._audio_pose_button.grid(row=0, column=2, padx=(5, 5), pady=(0, 0))
        self._audio_forward_button.grid(row=0, column=3, padx=(5, 0), pady=(0, 0), sticky='W')

        self.__load_icons()

    def load(self, audio:Audio):
        self._audio = audio
        self._audio_play_button.configure(state='normal')
        self._audio_pose_button.configure(state='normal')
        self._audio_backward_button.configure(state='normal')
        self._audio_forward_button.configure(state='normal')

    def __play(self):
        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(self._audio.samplewidth),
                            channels=self._audio.nchannels, rate=self._audio.framerate,
                            frames_per_buffer=CHUNK_SIZE, output=True)
            self._audio.rewind()
            while True:
                data = self._audio.read_frames(CHUNK_SIZE)
                if len(data) == 0:
                    self._audio.rewind()
                    break
                stream.write(data)

            stream.close()
            p.terminate()
        except:
            print('Error: cannot play the audio')
            return

    def __load_icons(self):
        play_button_light_image_path = '../Image/play_light.png'
        play_button_dark_image_path = '../Image/play_dark.png'
        pose_button_light_image_path = '../Image/pose_light.png'
        pose_button_dark_image_path = '../Image/pose_dark.png'
        forward_button_light_image_path = '../Image/forward_light.png'
        forward_button_dark_image_path = '../Image/forward_dark.png'
        backward_button_light_image_path = '../Image/backward_light.png'
        backward_button_dark_image_path = '../Image/backward_dark.png'

        self.__load_icon(self._audio_play_button, play_button_light_image_path, play_button_dark_image_path)
        self.__load_icon(self._audio_pose_button, pose_button_light_image_path, pose_button_dark_image_path)
        self.__load_icon(self._audio_forward_button, forward_button_light_image_path, forward_button_dark_image_path)
        self.__load_icon(self._audio_backward_button, backward_button_light_image_path, backward_button_dark_image_path)

    def __load_icon(self, button:customtkinter.CTkButton, light_path:str, dark_icon_path:str):
        try:
            light_image = PIL.Image.open(light_path)
        except FileNotFoundError:
            light_image = None
            print(f'Error: cannot find {light_path}')
        try:
            dark_image = PIL.Image.open(dark_icon_path)
        except FileNotFoundError:
            dark_image = None
            print(f'Error: cannot find {dark_icon_path}')

        if light_image is None and dark_image is None:
            return
        else:
            button.configure(image=customtkinter.CTkImage(light_image=light_image, dark_image=dark_image, size=(40, 40)))
            button.configure(text='')
            button.configure(fg_color='transparent')


class FileDialogFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # widgets
        self._input_path_entry = customtkinter.CTkEntry(self, font=(FONT_TYPE, FONT_SIZE, 'normal'), state='readonly')
        self._browse_button = customtkinter.CTkButton(self, width=30, font=(FONT_TYPE, FONT_SIZE, 'bold'), text='Browse', command=self._browse)
        
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self._input_path_entry.grid(row=0, column=1, padx=(10, 0), pady=(10, 10), sticky='WE')
        self._browse_button.grid(row=0, column=2, padx=(5, 10), pady=(10, 10), sticky='E')

    def _browse(self):
        input_path = customtkinter.filedialog.askopenfilename(filetypes=[('Audio File', '*.wav')])
        if input_path is None:
            return

        self._input_path_entry.configure(state='normal')
        self._input_path_entry.delete(0, customtkinter.END)
        self._input_path_entry.insert(0, input_path)
        self._input_path_entry.configure(state='readonly')
        
        if os.path.splitext(input_path)[1] == '.wav':
            audio, tags =  self._open_wav(input_path)
        else:
            return

        if audio != None:
            self.master.load(audio, tags)

    def _open_wav(self, input_path:str):
        try:
            wave_data = wave.open(input_path, mode='rb')
            nchannels, samplewidth, framerate, nframes, _, _ = wave_data.getparams()
            frames = wave_data.readframes(-1)
        except FileNotFoundError:
            print(f'Error: cannot find {input_path}')
            return None

        print(f'{input_path} has been loaded')
        print(f'{nchannels}ch {samplewidth * 8}bit {framerate}Hz')
        return Audio(nchannels, samplewidth, framerate, frames),os.path.basename(input_path)


class SimpleAudioPlayer(customtkinter.CTk):
    def __init__(self, fg_color= None, **kwargs):
        super().__init__(fg_color, **kwargs)

        self.title('Simple Audio Player version 0.1')
        self.geometry(f'{MAIN_WINDOW_WIDTH}x{MAIN_WINDOW_HEIGHT}')

        # frames
        self._cover_art_display_frame = CoverArtDisplayFrame(self, width=MAIN_WINDOW_WIDTH-20, height=MAIN_WINDOW_WIDTH-20)
        self._audio_player_controller_frame = AudioPlayerControllerFrame(self, width=MAIN_WINDOW_WIDTH-20)
        self._file_dialog_frame = FileDialogFrame(self, width=MAIN_WINDOW_WIDTH-20)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self._cover_art_display_frame.grid(row=0, column=0, padx=(10, 10), pady=(10, 0), sticky='NSWE')
        self._audio_player_controller_frame.grid(row=1, column=0, padx=(10, 10), pady=(10, 0), sticky='WE')
        self._file_dialog_frame.grid(row=2, column=0, padx=(10, 10), pady=(10, 10), sticky='WE')

    def load(self, audio: Audio, title: str):
        self._audio_player_controller_frame.load(audio)
        self._cover_art_display_frame.set_cover_art()
        self._cover_art_display_frame.set_audio_title(title)


if __name__ == '__main__':
    app = SimpleAudioPlayer()
    app.mainloop()
