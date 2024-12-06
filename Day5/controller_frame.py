import customtkinter
import tkinter
import PIL.Image
from threading import Thread, Event
import time
from audio import Audio, AudioPlayer, AudioPlayerState
from common import *
import logging


class ControllerFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # threads
        self.__thread_for_play = Thread()
        self.__thread_for_progress_bar = Thread()
        self.__thread_for_audio_form = Thread()
        self.__thread_for_button = Thread()
        self.__event_for_play = Event()

        # widgets
        self._audio_progress_bar = customtkinter.CTkProgressBar(
            master=self,
            width=None, height=8, corner_radius=6, border_width=0,
            bg_color='transparent', fg_color=None,
            border_color=None, progress_color=None,
            variable = customtkinter.DoubleVar(value=0.0)
        )
        self._audio_progress_label = customtkinter.CTkLabel(self,
            height=20, width=40,
            text=f"00:00 / 00:00", font=('consolas', FONT_SIZE-1, 'bold'), text_color=("gray16", "gray84"), text_color_disabled=("gray32", "gray68"),
        )
        self._audio_play_button = customtkinter.CTkButton(
            self,
            image=None, hover=True,
            text='PLAY', font=(FONT_TYPE, FONT_SIZE+2, 'normal'),
            height=40, width=40, corner_radius=4,
            state="disabled",
            command=self.__play
        )
        self._audio_pose_button = customtkinter.CTkButton(
            self,
            image=None, hover=True,
            text="POSE", font=(FONT_TYPE, FONT_SIZE+2, 'normal'),
            height=40, width=40, corner_radius=4,
            state="disabled",
            command=self.__pose
        )
        self._audio_forward_button = customtkinter.CTkButton(
            self,
            image=None, hover=True,
            text=">>", font=(FONT_TYPE, FONT_SIZE+2, 'normal'),
            height=40, width=40, corner_radius=4,
            state="disabled",
            command=self.__forward
        )
        self._audio_backward_button = customtkinter.CTkButton(
            self,
            image=None, hover=True,
            text="<<", font=(FONT_TYPE, FONT_SIZE+2, 'normal'),
            height=40, width=40, corner_radius=4,
            state="disabled",
            command=self.__backward
        )
        self._loop_button = customtkinter.CTkButton(
            self,
            image=None, hover=True,
            text="LOOP", font=(FONT_TYPE, FONT_SIZE, 'normal'),
            height=30, width=30, corner_radius=4,
            state="disabled",
            command=self.__loop
        )
        self._loop_off_button = customtkinter.CTkButton(
            self,
            image=None, hover=True,
            text="LOOP OFF", font=(FONT_TYPE, FONT_SIZE, 'normal'),
            height=30, width=30, corner_radius=4,
            state="disabled",
            command=self.__loop
        )
        self._volume_button = customtkinter.CTkButton(
            self,
            image=None, hover=True,
            text="VOLUME", font=(FONT_TYPE, FONT_SIZE, 'normal'),
            height=30, width=30, corner_radius=4,
            state="disabled",
            command=self.__volume
        )
        self._volume_off_button = customtkinter.CTkButton(
            self,
            image=None, hover=True,
            text="VOLUME OFF", font=(FONT_TYPE, FONT_SIZE, 'normal'),
            height=30, width=30, corner_radius=4,
            state="disabled",
            command=self.__volume
        )
        self._volume_controller_frame = VolumeControlloerFrame(self)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=0)

        self._audio_progress_bar.grid(row=0, column=0, padx=(10, 10), pady=(10, 0), sticky="WE", columnspan=5)
        self._audio_progress_label.grid(row=1, column=0, padx=(10, 10), pady=(5, 0), sticky="E", columnspan=5)

        self._loop_button.grid(row=2, column=0, padx=(20, 0), pady=(10, 10), sticky="W")
        self._loop_off_button.grid(row=2, column=0, padx=(20, 0), pady=(10, 10), sticky="W")
        self._loop_off_button.grid_remove()
        self._audio_backward_button.grid(row=2, column=1, padx=(5, 0), pady=(10, 10), sticky="E")
        self._audio_play_button.grid(row=2, column=2, padx=(5, 0), pady=(10, 10), sticky="E")
        self._audio_pose_button.grid(row=2, column=2, padx=(5, 0), pady=(10, 10), sticky="W")
        self._audio_pose_button.grid_remove()
        self._audio_forward_button.grid(row=2, column=3, padx=(5, 0), pady=(10, 10), sticky="W")
        self._volume_button.grid(row=2, column=4, padx=(5, 20), pady=(10, 10), sticky="W")
        self._volume_off_button.grid(row=2, column=4, padx=(5, 20), pady=(10, 10), sticky="W")
        self._volume_off_button.grid_remove()

        self.__load_icons()

        # bind
        self._audio_progress_bar.bind("<Button>", self.__press_progress_bar)
        self._audio_progress_bar.bind("<B1-Motion>", self.__drag_progress_bar)
        self._audio_progress_bar.bind("<ButtonRelease>", self.__release_progress_bar)

        self._player = AudioPlayer(self.__event_for_play)

    def load(self, audio:Audio):
        self.__event_for_play.clear()
        logging.info(f'state: {AudioPlayerState(self._player.state).name}, event_for_play: {self.__event_for_play.is_set()}')
        logging.info(f'__thread_for_play: {'alive' if self.__thread_for_play.is_alive() else 'dead'}')
        logging.info(f'__thread_for_progress_bar: {'alive' if self.__thread_for_progress_bar.is_alive() else 'dead'}')
        logging.info(f'__thread_for_audio_form: {'alive' if self.__thread_for_audio_form.is_alive() else 'dead'}')
        logging.info(f'__thread_for_button: {'alive' if self.__thread_for_button.is_alive() else 'dead'}')

        # load audio
        self._player.load(audio)

        # init widgets
        self._audio = audio
        self._audio_play_button.configure(state='normal')
        self._audio_pose_button.configure(state='normal')
        self._audio_backward_button.configure(state='normal')
        self._audio_forward_button.configure(state='normal')
        self._loop_button.configure(state='normal')
        self._loop_off_button.configure(state='normal')
        self._volume_button.configure(state='normal')
        self._volume_off_button.configure(state='normal')

        self._audio_play_button.grid()
        self._audio_pose_button.grid_remove()

        self._audio_progress_bar.set(0.0)
        self._audio_progress_label.configure(text=self.__pos_to_time(0) + " / " + self.__pos_to_time(self._audio.nframes-1))

        # clear all events not to run threads
        logging.info(f'state: {AudioPlayerState(self._player.state).name}, event_for_play: {self.__event_for_play.is_set()}')

        if not self.__thread_for_progress_bar.is_alive():
            self.__thread_for_progress_bar = Thread(target=self.__loop_for_updating_audio_progress_bar, daemon=False)
            self.__thread_for_progress_bar.start()
        if not self.__thread_for_audio_form.is_alive():
            self.__thread_for_audio_form = Thread(target=self.__loop_for_updating_audio_form, daemon=False)
            self.__thread_for_audio_form.start()
        if not self.__thread_for_button.is_alive():
            self.__thread_for_button = Thread(target=self.__loop_for_updating_buttons, daemon=False)
            self.__thread_for_button.start()

    def close(self): # kill all living threads
        logging.info(f'close button was pressed')
        self._player.close()
        
        while True:
            self.__event_for_play.set()
            logging.info(f'state: {AudioPlayerState(self._player.state).name}, event_for_play: {self.__event_for_play.is_set()}')
            logging.info(f'__thread_for_play: {'alive' if self.__thread_for_play.is_alive() else 'dead'}')
            logging.info(f'__thread_for_progress_bar: {'alive' if self.__thread_for_progress_bar.is_alive() else 'dead'}')
            logging.info(f'__thread_for_audio_form: {'alive' if self.__thread_for_audio_form.is_alive() else 'dead'}')
            logging.info(f'__thread_for_button: {'alive' if self.__thread_for_button.is_alive() else 'dead'}')

            if self.__thread_for_play.is_alive():
                time.sleep(0.05)
                continue
            if self.__thread_for_progress_bar.is_alive():
                self.update()
                time.sleep(0.05)
                continue
            if self.__thread_for_audio_form.is_alive():
                self.update()
                time.sleep(0.05)
                continue
            if self.__thread_for_button.is_alive():
                self.update()
                time.sleep(0.05)
                continue
            break

        self.__event_for_play.clear()
        logging.info(f'state: {AudioPlayerState(self._player.state).name}, event_for_play: {self.__event_for_play.is_set()}')

    def __play(self):
        logging.info(f'Play button was pressed.')
        state = self._player.state
        if state == AudioPlayerState.PLAYING:
            return
        if state == AudioPlayerState.NOT_READY:
            return
        if state == AudioPlayerState.CLOSING:
            return

        # if threads are not alive, generate new threads and start
        if not self.__thread_for_play.is_alive():
            self.__thread_for_play = Thread(target=self._player.loop_for_playback, daemon=False)
            self.__thread_for_play.start()

        self.__event_for_play.set() # to run threads
        logging.info(f'state: {AudioPlayerState(self._player.state).name}, event_for_play: {self.__event_for_play.is_set()}')

    def __pose(self): # kill living threads
        logging.info(f'Pose button was pressed.')
        state = self._player.state
        if state != AudioPlayerState.PLAYING:
            return
        
        self.__event_for_play.clear() # not to run threads
        logging.info(f'state: {AudioPlayerState(self._player.state).name}, event_for_play: {self.__event_for_play.is_set()}')

    def __forward(self):
        logging.info(f'Forward button was pressed.')
        state = self._player.state
        if state == AudioPlayerState.NOT_READY:
            return
        if state == AudioPlayerState.CLOSING:
            return
        
        self._player.forward()

        pos = self._audio.current_pos
        if not self.__event_for_play.is_set():
            self.__update_audio_progress_bar(pos)
        if not self.__event_for_play.is_set():
            self.master._audio_form_frame.update_audio_form(pos)

    def __backward(self):
        logging.info(f'Backward button was pressed.')
        state = self._player.state
        if state == AudioPlayerState.NOT_READY:
            return
        if state == AudioPlayerState.CLOSING:
            return
        
        self._player.backward()

        pos = self._audio.current_pos
        if not self.__event_for_play.is_set():
            self.__update_audio_progress_bar(pos)
        if not self.__event_for_play.is_set():
            self.master._audio_form_frame.update_audio_form(pos)

    def __volume(self):
        volume_controller_frame_height = 100
        volume_controller_frame_width = 200
        # volume_button_height = self._volume_button.winfo_height()
        volume_button_width = self._volume_button.winfo_width()
        scaling = self._volume_button._get_widget_scaling()

        x = int(self._volume_button.winfo_rootx() - 0.5 * (volume_controller_frame_width * scaling - volume_button_width))
        y = int(self._volume_button.winfo_rooty() - volume_controller_frame_height * scaling)
        geometry = f'{volume_controller_frame_width}x{volume_controller_frame_height}' + f'+{x}+{y}'

        # if not self._volume_controller_frame.winfo_exists():
        #     self._volume_controller_frame = VolumeControlloerFrame(self)
        self._volume_controller_frame.open(geometry)

    def __loop(self):
        loop = self._player.loop_play
        if loop:
            self._player.loop_play = False
            self._loop_off_button.grid()
            self._loop_button.grid_remove()
        else:
            self._player.loop_play = True
            self._loop_button.grid()
            self._loop_off_button.grid_remove()

    def __press_progress_bar(self, event:tkinter.Event):
        # logging.info(event)

        # pause if playing
        state = self._player.state
        if state == AudioPlayerState.NOT_READY:
            return
        if state == AudioPlayerState.CLOSING:
            return

        if state == AudioPlayerState.PLAYING:
            self.__event_for_play.clear()
            self.__is_temporary_posed = True
            logging.info(f'state: {AudioPlayerState(self._player.state).name}, event_for_play: {self.__event_for_play.is_set()}')
        else:
            self.__is_temporary_posed = False

        scaling_factor = self._audio_progress_bar._get_widget_scaling()
        border_witdh = self._audio_progress_bar.cget('border_width') * scaling_factor
        x = event.x -  border_witdh
        val = x / (self._audio_progress_bar.winfo_width() - border_witdh - border_witdh)
        val = 0 if val < 0 else val
        val = 1 if val > 1 else val
        pos = round(self._audio.nframes * val)

        self._audio.current_pos = pos
        self._audio_progress_bar.set(val)
        self._audio_progress_label.configure(text=self.__pos_to_time(pos) + " / " + self.__pos_to_time(self._audio.nframes-1))
        self.master._audio_form_frame.update_audio_form(pos)

    def __drag_progress_bar(self, event:tkinter.Event):
        # logging.info(event)

        state = self._player.state
        if state == AudioPlayerState.NOT_READY:
            return
        if state == AudioPlayerState.CLOSING:
            return

        scaling_factor = self._audio_progress_bar._get_widget_scaling()
        border_witdh = self._audio_progress_bar.cget('border_width') * scaling_factor
        x = event.x -  border_witdh
        val = x / (self._audio_progress_bar.winfo_width() - border_witdh - border_witdh)
        val = 0 if val < 0 else val
        val = 1 if val > 1 else val
        pos = round(self._audio.nframes * val)

        self._audio.current_pos = pos
        self._audio_progress_bar.set(val)
        self._audio_progress_label.configure(text=self.__pos_to_time(pos) + " / " + self.__pos_to_time(self._audio.nframes-1))
        self.master._audio_form_frame.update_audio_form(pos)

    def __release_progress_bar(self, event:tkinter.Event):
        # logging.info(event)
                      
        state = self._player.state
        if state == AudioPlayerState.NOT_READY:
            return
        if state == AudioPlayerState.CLOSING:
            return
        if self.__is_temporary_posed:
            self.__event_for_play.set()
            logging.info(f'state: {AudioPlayerState(self._player.state).name}, event_for_play: {self.__event_for_play.is_set()}')

    def __loop_for_updating_audio_progress_bar(self):
        while True:
            state = self._player.state
            if state == AudioPlayerState.NOT_READY:
                break
            if state == AudioPlayerState.CLOSING:
                break
                
            if not self.__event_for_play.is_set():
                if state == AudioPlayerState.READY:
                    self.__update_audio_progress_bar(0)
                self.__event_for_play.wait()
            
            self.__update_audio_progress_bar(self._audio.current_pos)
            time.sleep(0.2)

    def __update_audio_progress_bar(self, current_pos):
        val = current_pos / self._audio.nframes

        self._audio_progress_bar.set(val)
        self._audio_progress_label.configure(text=self.__pos_to_time(current_pos) + " / " + self.__pos_to_time(self._audio.nframes-1))
        self.update_idletasks()
        # self.update()

    def __loop_for_updating_audio_form(self):
        while True:
            state = self._player.state
            if state == AudioPlayerState.NOT_READY:
                break
            if state == AudioPlayerState.CLOSING:
                break

            if not self.__event_for_play.is_set():
                if state == AudioPlayerState.READY:
                    self.master._audio_form_frame.update_audio_form(0)
                self.__event_for_play.wait()
                
            self.master._audio_form_frame.update_audio_form(self._audio.current_pos)
            time.sleep(0.1)

    def __loop_for_updating_buttons(self):
        while True:
            state = self._player.state
            if state == AudioPlayerState.NOT_READY:
                break
            if state == AudioPlayerState.CLOSING:
                break

            if state == AudioPlayerState.PLAYING:
                self._audio_pose_button.grid()
                self._audio_play_button.grid_remove()
            else:
                self._audio_play_button.grid()
                self._audio_pose_button.grid_remove()

            time.sleep(0.1)

    def __pos_to_time(self, pos):
        t = pos / self._audio.framerate
        m = int(t / 60)
        s = int(t - 60 * m)
        return str(m).zfill(2) + ':' + str(s).zfill(2)

    def __load_icons(self):
        play_button_light_image_path = "../Image/play_light.png"
        play_button_dark_image_path = "../Image/play_dark.png"
        pose_button_light_image_path = "../Image/pose_light.png"
        pose_button_dark_image_path = "../Image/pose_dark.png"
        forward_button_light_image_path = "../Image/forward_light.png"
        forward_button_dark_image_path = "../Image/forward_dark.png"
        backward_button_light_image_path = "../Image/backward_light.png"
        backward_button_dark_image_path = "../Image/backward_dark.png"
        loop_button_light_image_path = "../Image/loop_light.png"
        loop_button_dark_image_path = "../Image/loop_dark.png"
        loop_off_button_light_image_path = "../Image/loop_off_light.png"
        loop_off_button_dark_image_path = "../Image/loop_off_dark.png"
        volume_button_light_image_path = "../Image/volume_light.png"
        volume_button_dark_image_path = "../Image/volume_dark.png"
        volume_button_off_light_image_path = "../Image/volume_off_light.png"
        volume_button_off_dark_image_path = "../Image/volume_off_dark.png"

        self.__load_icon(self._audio_play_button, play_button_light_image_path, play_button_dark_image_path, (30, 30))
        self.__load_icon(self._audio_pose_button, pose_button_light_image_path, pose_button_dark_image_path, (30, 30))
        self.__load_icon(self._audio_forward_button, forward_button_light_image_path, forward_button_dark_image_path, (30, 30))
        self.__load_icon(self._audio_backward_button, backward_button_light_image_path, backward_button_dark_image_path, (30, 30))
        self.__load_icon(self._loop_button, loop_button_light_image_path, loop_button_dark_image_path, (20, 20))
        self.__load_icon(self._loop_off_button, loop_off_button_light_image_path, loop_off_button_dark_image_path, (20, 20))
        self.__load_icon(self._volume_button, volume_button_light_image_path, volume_button_dark_image_path, (20, 20))
        self.__load_icon(self._volume_off_button, volume_button_off_light_image_path, volume_button_off_dark_image_path, (20, 20))
        
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


class VolumeControlloerFrame(customtkinter.CTkToplevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title('volume controller')

        self.overrideredirect(boolean=True)
        self.attributes("-transparentcolor", self._apply_appearance_mode(self._fg_color))

        self._frame = customtkinter.CTkFrame(self, corner_radius=6, border_width=0)
        self._slider = customtkinter.CTkSlider(self._frame, height=18, from_=0, to=100, number_of_steps=101, variable=customtkinter.Variable(value=100), command=self.__slide)
        self._label = customtkinter.CTkLabel(self._frame, text=f"100 / 100", font=('consolas', FONT_SIZE, 'bold'))

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._frame.grid(row=0, column=0, padx=0, pady=0, sticky='')
        self._frame.grid_columnconfigure(0, weight=1)
        self._frame.grid_rowconfigure(0, weight=1)
        self._frame.grid_rowconfigure(1, weight=0)
        self._slider.grid(row=0, column=0, sticky='NSWE', padx=(20, 20), pady=(20, 0))
        self._label.grid(row=1, column=0, sticky='E', padx=(20, 20), pady=(10, 15))

        self.master.bind("<Button-1>", lambda event: self.close())
        self.master.bind("<Configure>", lambda event: self.close())

        self.resizable(width=False, height=False)
        self.transient(self.master)

        self.wm_attributes('-alpha', 0.9)

        self.withdraw()
        self.__is_displayed = False

    def __slide(self, val):
        volume = round(val)
        self._label.configure(text=f'{volume} / 100')
        self.master._player.volume = volume
        if val == 0:
            self.master._volume_off_button.grid()
            self.master._volume_button.grid_remove()
        else:
            self.master._volume_button.grid()
            self.master._volume_off_button.grid_remove()

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
