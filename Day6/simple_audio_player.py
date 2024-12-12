import customtkinter
from audio import Audio
from audio_form_frame import AudioFormFrame
from cover_art_display_frame import CoverArtDisplayFrame
from controller_frame import ControllerFrame
from side_menu_frame import SideMenuFrame
from play_list_frame import PlayListFrame
from common import *
from typing import List


class SimpleAudioPlayer(customtkinter.CTk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.title("Simple Audio Player version 0.6")
        self.geometry(f'{MAIN_WINDOW_WIDTH}x{MAIN_WINDOW_HEIGHT}')

        # frames
        self._side_menu_frame = SideMenuFrame(self)
        self._cover_art_display_frame = CoverArtDisplayFrame(self) # , width=MAIN_WINDOW_WIDTH-20)
        self._audio_form_frame = AudioFormFrame(self)
        self._controller_frame = ControllerFrame(self) # , width=MAIN_WINDOW_WIDTH-20)
        self._play_list_frame = PlayListFrame(self)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        
        self._side_menu_frame.grid(         row=0,  column=0,   padx=(0, 0),    pady=(0, 0),    sticky="NS", rowspan=3)
        self._cover_art_display_frame.grid( row=0,  column=1,   padx=(0, 10),  pady=(10, 0),   sticky="NSWE")
        self._play_list_frame.grid(         row=0,  column=1,   padx=(0, 10),  pady=(10, 0),   sticky="NSWE")
        self._play_list_frame.grid_remove()
        self._audio_form_frame.grid(        row=1,  column=1,   padx=(0, 10),  pady=(10, 0),   sticky="WE")
        self._controller_frame.grid(        row=2,  column=1,   padx=(0, 10),  pady=(10, 10),  sticky="WE")

        # attributes
        # self.wattributes('-alpha', 0.9)

        # protocol
        self.protocol('WM_DELETE_WINDOW', self.close)
                
    def load(self, audio: Audio):
        self._cover_art_display_frame.load(audio.tag)
        self._audio_form_frame.load(audio.raw)
        self._controller_frame.load(audio.raw)

    def load_play_list(self, audio_list:List[Audio]):
        if len(audio_list) == 0:
            return
        
        self._play_list_frame.load(audio_list)
        if len(audio_list) == 1:
            self._cover_art_display_frame.grid()
            self._play_list_frame.grid_remove()
        else:
            self._play_list_frame.grid()
            self._cover_art_display_frame.grid_remove()

    def switch_play_list(self):
        if self._cover_art_display_frame.grid_info() == {}:
            self._cover_art_display_frame.grid()
            self._play_list_frame.grid_remove()
        else:
            self._play_list_frame.grid()
            self._cover_art_display_frame.grid_remove()  

    def switch_wave_form(self):
        if self._controller_frame.is_wave_form_displayed:
            self._audio_form_frame.grid_remove()
            self._controller_frame.is_wave_form_displayed = False
        else:
            self._audio_form_frame.grid()
            self._controller_frame.is_wave_form_displayed = True

    def close(self):
        self._controller_frame.close()
        self.quit()
        self.destroy()


if __name__ == '__main__':
    app = SimpleAudioPlayer()
    app.mainloop()
