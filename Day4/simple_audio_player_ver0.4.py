import customtkinter
from audio import Audio, AudioTag
from audio_form_frame import AudioFormFrame
from file_dialog_frame import FileDialogFrame
from cover_art_display_frame import CoverArtDisplayFrame
from controller_frame import ControllerFrame
from common import *


class SimpleAudioPlayer(customtkinter.CTk):
    def __init__(self, fg_color= None, **kwargs):
        super().__init__(fg_color, **kwargs)

        self.title("Simple Audio Player version 0.4")
        self.geometry(f'{MAIN_WINDOW_WIDTH}x{MAIN_WINDOW_HEIGHT}')

        # frames
        self._cover_art_display_frame = CoverArtDisplayFrame(self) # , width=MAIN_WINDOW_WIDTH-20)
        self._audio_form_frame = AudioFormFrame(self)
        self._controller_frame = ControllerFrame(self) # , width=MAIN_WINDOW_WIDTH-20)
        self._file_dialog_frame = FileDialogFrame(self) #, width=MAIN_WINDOW_WIDTH-20)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self._cover_art_display_frame.grid(row=0, column=0, padx=(10, 10), pady=(10, 0), sticky="NSWE")
        self._audio_form_frame.grid(row=1, column=0, padx=(10, 10), pady=(10, 0), sticky="WE")
        self._controller_frame.grid(row=2, column=0, padx=(10, 10), pady=(10, 0), sticky="WE")
        self._file_dialog_frame.grid(row=3, column=0, padx=(10, 10), pady=(10, 10), sticky="WE")

    def load(self, audio: Audio, tags: AudioTag):
        self._controller_frame.load(audio)
        self._audio_form_frame.load(audio)
        self._cover_art_display_frame.load(tags)

    def close(self):
        self._controller_frame.close()
        self.destroy()


if __name__ == '__main__':
    app = SimpleAudioPlayer()
    app.protocol('WM_DELETE_WINDOW', lambda: app.close())
    app.mainloop()
