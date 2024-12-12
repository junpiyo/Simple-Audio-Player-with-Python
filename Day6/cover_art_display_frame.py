import customtkinter
import PIL.Image
from audio import Tag
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

        # widgets
        self._sub_frame = customtkinter.CTkFrame(
            master=self,
            width=self.__cover_art_width + 40, height=self.__cover_art_height + 40, corner_radius=0, border_width=2,
            fg_color='transparent'
        )
        self._tab_switching_button = customtkinter.CTkSegmentedButton(
            master=self._sub_frame,
            values=[" Album Art ", "  Lyrics  "],
            corner_radius=0, border_width=0,
            command=self.__switch_tabs,
            font=(FONT_TYPE, FONT_SIZE-3, 'bold'),
            state="disabled"
        )
        self._cover_art_display_label = customtkinter.CTkLabel(
            master=self._sub_frame,
            width=self.__cover_art_width + 20, height=self.__cover_art_height + 20,
            fg_color='transparent',
            font=(FONT_TYPE, FONT_SIZE, 'normal'), text='The cover art of a audio is to be displayed...'
        )
        self._lyrics_label = customtkinter.CTkTextbox(
            master=self._sub_frame,
            fg_color='transparent',
            font=(FONT_TYPE, FONT_SIZE+1, 'normal'), state="disabled",
            border_spacing=10
        )
        self._audio_title_label = customtkinter.CTkLabel(self, font=(FONT_TYPE, FONT_SIZE+6, 'bold'), text='Title', anchor='center')
        self._audio_album_and_artist_label = customtkinter.CTkLabel(self, font=(FONT_TYPE, FONT_SIZE-2, 'bold'), text='Album / Artist', anchor='center')

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self._sub_frame.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky="NSWE")
        self._audio_title_label.grid(row=1, column=0, padx=(10, 10), pady=(5, 0), sticky="WE")
        self._audio_album_and_artist_label.grid(row=2, column=0, padx=(10, 10), pady=(5, 10), sticky="WE")

        self._sub_frame.grid_rowconfigure(0, weight=0)
        self._sub_frame.grid_rowconfigure(1, weight=1)
        self._sub_frame.grid_columnconfigure(0, weight=1)
        self._tab_switching_button.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky="W")
        self._cover_art_display_label.grid(row=1, column=0, padx=(2, 2), pady=(2, 2), sticky="NSWE")
        self._lyrics_label.grid(row=1, column=0, padx=(2, 2), pady=(2, 2), sticky="NSWE")
        self._lyrics_label.grid_remove()

    def load(self, tag: Tag):
        self._tab_switching_button.configure(state='normal')
        self._tab_switching_button.set(' Album Art ')
        self.__switch_tabs(' Album Art ')

        self.__set_cover_art(tag.cover_art)
        self.__set_audio_lyrics(tag.lyrics)
        self.__set_audio_title(tag.title)
        self.__set_audio_album_and_artist(tag.album, tag.artist)

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

    def __set_audio_lyrics(self, lyrics:str=None):
        if lyrics is None:
            lyrics = 'not included'
        self._lyrics_label.configure(state='normal')
        self._lyrics_label.delete("0.0", "end")
        self._lyrics_label.insert(index='0.0', text=lyrics)
        self._lyrics_label.configure(state='disabled')

    def __set_audio_title(self, title:str=None):
        if title is None:
            title = 'Title'
        self._audio_title_label.configure(text=title)

    def __set_audio_album_and_artist(self, album:str=None, artist:str=None):
        if album is None:
            album = 'Album'
        if artist is None:
            artist = 'Artist'
        self._audio_album_and_artist_label.configure(text=f'{album}  / {artist}')

    def __switch_tabs(self, value):
        if value == " Album Art ":
            self._cover_art_display_label.grid()
            self._lyrics_label.grid_remove()
        elif value == "  Lyrics  ":
            self._lyrics_label.grid()
            self._cover_art_display_label.grid_remove()
            