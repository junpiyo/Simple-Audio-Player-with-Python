import customtkinter
from CTkTable import CTkTable
from common import *
from audio import Audio
from typing import List


MAX_NUMBER_OF_FILES = 50


class PlayListFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs, fg_color='transparent')

        self.__audio_list = []
        self.__header = ['Track','Title', 'Album', 'Artist']
        self.__current_track = 0
        self.__root = self.master.master.master

        self._play_list_table = CTkTable(
            master=self,
            row=MAX_NUMBER_OF_FILES, column=4, values=[self.__header],
            width=80, font=(FONT_TYPE, FONT_SIZE-1, 'normal'), corner_radius=6,
            command=self.__play_list_table_command
        )

        self.columnconfigure(0, weight=0)
        # self._file_table.columnconfigure(1, weight=0)
        self._play_list_table.grid(row=0, column=0, padx=0, pady=0)

    def load(self, audio_list:List[Audio]):
        if len(audio_list) == 0:
            return False
        
        self.__audio_list = audio_list

        values = [self.__header]
        for i, audio in enumerate(audio_list):
            values.append([i+1, audio.tag.title, audio.tag.album, audio.tag.artist])

        self._play_list_table.update_values(values)

        row_idx = 1
        if self.__select_row(row_idx):
            self.__load(track=row_idx-1)

    def __load(self, track:int):
        audio = self.__audio_list[track]
        if audio.raw is None:
            if not audio.open_file(is_audio=True):
                return False
        
        self.__root.load(audio)
        return True

    def __select_row(self, row_idx):
        if row_idx == 0:
            return False
        if row_idx > len(self.__audio_list):
            return False
        
        selected_row_idx, _ = self._play_list_table.get_selected_row().values()
        if selected_row_idx is not None:
            self._play_list_table.deselect_row(selected_row_idx)

        self._play_list_table.select_row(row_idx)
        return True

    def __play_list_table_command(self, event):
        logging.info(event)
        row = event['row']
        column = event['column']
        value = event['value']

        if self.__select_row(row):
            self.__load(track=row-1)
 