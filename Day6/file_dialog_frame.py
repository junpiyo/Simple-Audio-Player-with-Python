import customtkinter
import os
from audio import Audio
from common import *
from typing import List



class FileDialogFrame(customtkinter.CTkToplevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title('file dialog')

        self.overrideredirect(boolean=True)
        self.attributes("-transparentcolor", self._apply_appearance_mode(self._fg_color))

        self._frame = customtkinter.CTkFrame(self, corner_radius=6, border_width=1)
        self._file_open_button = customtkinter.CTkButton(
            master=self._frame,
            image=None, hover=True,
            text='Open File...', font=(FONT_TYPE, FONT_SIZE-2, 'normal'),
            height=30, corner_radius=4,
            state="normal",
            command=self.__open_file
        )
        self._folder_open_button = customtkinter.CTkButton(
            master=self._frame,
            image=None, hover=True,
            text='Open Folder...', font=(FONT_TYPE, FONT_SIZE-2, 'normal'),
            height=30, corner_radius=4,
            state="normal",
            command=self.__open_folder
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._frame.grid(row=0, column=0, padx=0, pady=0, sticky='')

        self._frame.grid_columnconfigure(0, weight=1)
        self._frame.grid_rowconfigure(0, weight=1)
        self._frame.grid_rowconfigure(1, weight=1)
        self._file_open_button.grid(row=0, column=0, sticky='NSWE', padx=(10, 10), pady=(10, 0))
        self._folder_open_button.grid(row=1, column=0, sticky='E', padx=(10, 10), pady=(10, 10))

        self.master.bind("<Button-1>", lambda event: self.close(), add=True)
        self.master.bind("<Configure>", lambda event: self.close(), add=True)

        self.resizable(width=False, height=False)
        self.transient(self.master)

        self.withdraw()
        self.__is_displayed = False

    def open(self, geometry):
        if self.__is_displayed:
            self.close()
            return
        else:
            self.geometry(geometry)
            self.deiconify()
            self.update()
            self.focus()
            self.__is_displayed = True

    def close(self):
        self.withdraw()
        self.__is_displayed = False

    def __open_folder(self):
        self.close()

        dir_path = customtkinter.filedialog.askdirectory()
        if dir_path is None or dir_path == '':
            return False
        
        file_list = [file for file in os.listdir(dir_path) if os.path.splitext(file)[1] == '.wav' or os.path.splitext(file)[1] == '.mp3']
        file_path_list = [os.path.join(dir_path, file) for file in file_list]

        audio_list:List[Audio] = []
        for file_path in file_path_list:
            audio = Audio(file_path)
            if audio.open_file(is_audio=False):
                audio_list.append(audio)

        if len(audio_list) != 0:
            self.master.master.load_play_list(audio_list)
            return True
        else:
            return False

    def __open_file(self):
        self.close()

        file_path = customtkinter.filedialog.askopenfilename(filetypes=[("Audio File", "*.wav;*.mp3")])
        if file_path is None or file_path == '':    
            return False
        
        audio = Audio(file_path)
        if audio.open_file(is_audio=False):
            self.master.master.load_play_list([audio])
            return True
        else:
            return False
            
