import customtkinter
import PIL.Image
from file_dialog_frame import FileDialogFrame
from common import *



class SideMenuFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(width=30)
        self.configure(corner_radius=0)
        self.configure(fg_color='transparent')

        # widgets
        self._file_dialog_button = customtkinter.CTkButton(
            master=self,
            image=None, hover=True,
            text='FILE', font=(FONT_TYPE, FONT_SIZE-5, 'normal'),
            height=30, width=30, corner_radius=4,
            state="normal",
            command=self.__file_dialog_button_command
        )
        self._play_list_button = customtkinter.CTkButton(
            master=self,
            image=None, hover=True,
            text='Setting', font=(FONT_TYPE, FONT_SIZE-5, 'normal'),
            height=30, width=30, corner_radius=4,
            state="normal",
            command=self.__play_list_button_command
        )
        self._wave_form_button = customtkinter.CTkButton(
            master=self,
            image=None, hover=True,
            text='Wave', font=(FONT_TYPE, FONT_SIZE-5, 'normal'),
            height=30, width=30, corner_radius=4,
            state="normal",
            command=self.__wave_form_button_command
        )
        self._setting_button = customtkinter.CTkButton(
            master=self,
            image=None, hover=True,
            text='Setting', font=(FONT_TYPE, FONT_SIZE-5, 'normal'),
            height=30, width=30, corner_radius=4,
            state="normal",
            # command=self.__open_setting_frame
        )
        self._file_dialog_frame = FileDialogFrame(self)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._file_dialog_button.grid(  row=0, column=0, padx=(10, 10), pady=(20, 0), sticky="")
        self._play_list_button.grid(    row=1, column=0, padx=(10, 10), pady=(15, 0), sticky="")
        self._wave_form_button.grid(    row=2, column=0, padx=(10, 10), pady=(15, 0), sticky="")
        self._setting_button.grid(      row=3, column=0, padx=(10, 10), pady=(0, 20), sticky="S")

        self.__load_icons()

    def __file_dialog_button_command(self):
        file_dialog_frame_height = 100
        file_dialog_frame_width = 200
        # volume_button_height = self._volume_button.winfo_height()
        volume_button_width = self._file_dialog_button.winfo_width()
        scaling = self._file_dialog_button._get_widget_scaling()

        x = int(self._file_dialog_button.winfo_rootx() - 0.5 * (file_dialog_frame_width * scaling - volume_button_width))
        y = int(self._file_dialog_button.winfo_rooty() - file_dialog_frame_height * scaling)
        geometry = f'{file_dialog_frame_width}x{file_dialog_frame_height}' + f'+{x}+{y}'

        self._file_dialog_frame.open(geometry)

    def __play_list_button_command(self):
        self.master.switch_play_list()

    def __wave_form_button_command(self):
        self.master.switch_wave_form()

    def __load_icons(self):
        folder_light_image_path = "../Image/folder_light.png"
        folder_dark_image_path = "../Image/folder_dark.png"
        play_list_light_image_path = "../Image/play_list_light.png"
        play_list_dark_image_path = "../Image/play_list_dark.png"
        wave_form_light_image_path = "../Image/wave_form_light.png"
        wave_form_dark_image_path = "../Image/wave_form_dark.png"
        vdots_light_image_path = "../Image/vdots_light.png"
        vdots_dark_image_path = "../Image/vdots_dark.png"

        self.__load_icon(self._file_dialog_button, folder_light_image_path, folder_dark_image_path, (15, 15))
        self.__load_icon(self._play_list_button, play_list_light_image_path, play_list_dark_image_path, (15, 15))
        self.__load_icon(self._wave_form_button, wave_form_light_image_path, wave_form_dark_image_path, (15, 15))
        self.__load_icon(self._setting_button, vdots_light_image_path, vdots_dark_image_path, (15, 15))

    def __load_icon(self, button:customtkinter.CTkButton, light_path:str, dark_icon_path:str, size:tuple[int, int]):
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
            button.configure(image=customtkinter.CTkImage(light_image=light_image, dark_image=dark_image, size=size))
            button.configure(text="", fg_color="transparent")
