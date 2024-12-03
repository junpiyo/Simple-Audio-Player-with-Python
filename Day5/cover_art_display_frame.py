import customtkinter
import PIL.Image
from audio import AudioTag
from common import *


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
        self._cover_art_display_label.grid(row=0, column=0, padx=(10, 10), pady=(5, 10), sticky="NWE", columnspan=2)
        self._audio_title_label.grid(row=1, column=0, padx=(10, 10), pady=(5, 0), sticky="WE", columnspan=2)
        self._audio_album_and_artist_label.grid(row=2, column=0, padx=(10, 10), pady=(5, 10), sticky="WE")

    def load(self, tags: AudioTag):
        self.__set_cover_art(tags.cover_art)
        self.__set_audio_title(tags.title)
        self.__set_audio_album_and_artist(tags.album, tags.artist)

    def __set_cover_art(self, cover_art:PIL.Image=None):
        if cover_art is None:
            if self._default_light_image is None and self._default_dark_image is None:
                None
            else:
                self._cover_art_display_label.configure(image=customtkinter.CTkImage(light_image=self._default_light_image, dark_image=self._default_dark_image, size=(250, 300)))
                self._cover_art_display_label.configure(text='')
        else:
            w, h = cover_art.width, cover_art.height
            if w > h:
                width = self.__cover_art_width
                height = int(h * self.__cover_art_width / w)
            else:
                height = self.__cover_art_height
                width = int(w * self.__cover_art_height / h)
            self._cover_art_display_label.configure(image=customtkinter.CTkImage(light_image=cover_art, dark_image=cover_art, size=(width, height)))
            self._cover_art_display_label.configure(text='')

    def __set_audio_title(self, title:str=None):
        if title is None:
            title = 'Title'
        self._audio_title_label.configure(text=title)

    def __set_audio_album_and_artist(self, album:str=None, artist:str=None):
        if album is None:
            album = 'Album'
        if artist is None:
            artist = 'Artist'
        self._audio_album_and_artist_label.configure(text=f'{album}/{artist}')