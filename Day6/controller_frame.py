import customtkinter
import tkinter
import PIL.Image
from threading import Thread, Lock
import time
from audio import Audio, AudioPlayer, AudioPlayerState, AudioPlayerInstruction
from common import *
import logging


class ControllerFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.__is_wave_form_displayed = True

        # threads
        self.__thread_for_play = Thread()
        self.__thread_for_progress_bar = Thread()
        self.__thread_for_audio_form = Thread()
        self.__thread_for_button = Thread()

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
        # self._clip_A_button = customtkinter.CTkButton(
        #     self,
        #     image=None, hover=True,
        #     text="A", font=(FONT_TYPE, FONT_SIZE, 'normal'),
        #     height=30, width=30, corner_radius=4,
        #     state="disabled",
        #     command=self.__clip_A
        # )
        # self._clip_B_button = customtkinter.CTkButton(
        #     self,
        #     image=None, hover=True,
        #     text="B", font=(FONT_TYPE, FONT_SIZE, 'normal'),
        #     height=30, width=30, corner_radius=4,
        #     state="disabled",
        #     command=self.__clip_B
        # )

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=0)

        self._audio_progress_bar.grid(row=0, column=0, padx=(10, 10), pady=(10, 0), sticky="WE", columnspan=7)
        self._audio_progress_label.grid(row=1, column=0, padx=(10, 10), pady=(5, 0), sticky="E", columnspan=7)

        # self._clip_A_button.grid(row=2, column=0, padx=(25, 0), pady=(10, 10), sticky="E")
        # self._clip_B_button.grid(row=2, column=1, padx=(5, 0), pady=(10, 10), sticky="E")
        self._loop_button.grid(row=2, column=0, padx=(25, 0), pady=(10, 10), sticky="W")
        self._loop_off_button.grid(row=2, column=0, padx=(25, 0), pady=(10, 10), sticky="W")
        self._loop_off_button.grid_remove()
        self._audio_backward_button.grid(row=2, column=1, padx=(5, 0), pady=(10, 10), sticky="E")
        self._audio_play_button.grid(row=2, column=2, padx=(5, 0), pady=(10, 10), sticky="E")
        self._audio_pose_button.grid(row=2, column=2, padx=(5, 0), pady=(10, 10), sticky="W")
        self._audio_pose_button.grid_remove()
        self._audio_forward_button.grid(row=2, column=3, padx=(5, 0), pady=(10, 10), sticky="W")
        self._volume_button.grid(row=2, column=4, padx=(0, 25), pady=(10, 10), sticky="W")
        self._volume_off_button.grid(row=2, column=4, padx=(0, 25), pady=(10, 10), sticky="W")
        self._volume_off_button.grid_remove()

        self.__load_icons()

        # bind
        self._audio_progress_bar.bind("<Button>", self.__press_progress_bar)
        self._audio_progress_bar.bind("<B1-Motion>", self.__drag_progress_bar)
        self._audio_progress_bar.bind("<ButtonRelease>", self.__release_progress_bar)

        self._player = AudioPlayer()

    def load(self, audio:Audio):
        # load audio
        self._player.instruction = AudioPlayerInstruction.STOP
        self._player.load(audio)
        logging.info(f'instruction: {self._player.instruction.name}, state: {self._player.state.name}')
        logging.info(f'__thread_for_play: {'alive' if self.__thread_for_play.is_alive() else 'dead'}')
        logging.info(f'__thread_for_progress_bar: {'alive' if self.__thread_for_progress_bar.is_alive() else 'dead'}')
        logging.info(f'__thread_for_audio_form: {'alive' if self.__thread_for_audio_form.is_alive() else 'dead'}')
        logging.info(f'__thread_for_button: {'alive' if self.__thread_for_button.is_alive() else 'dead'}')

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
        # self._clip_A_button.configure(state='normal')
        # self._clip_B_button.configure(state='normal')

        self._audio_play_button.grid()
        self._audio_pose_button.grid_remove()

        self._audio_progress_bar.set(0.0)
        self._audio_progress_label.configure(text=self.__pos_to_time(0) + " / " + self.__pos_to_time(self._audio.nframes-1))

        if not self.__thread_for_progress_bar.is_alive():
            self.__thread_for_progress_bar = Thread(target=self.__update_audio_progress_bar_when_playing, daemon=False)
            self.__thread_for_progress_bar.start()
        if not self.__thread_for_audio_form.is_alive():
            self.__thread_for_audio_form = Thread(target=self.__update_audio_form_when_playing, daemon=False)
            self.__thread_for_audio_form.start()
        if not self.__thread_for_button.is_alive():
            self.__thread_for_button = Thread(target=self.__update_buttons_when_playing, daemon=False)
            self.__thread_for_button.start()

    def close(self):
        logging.info(f'close button was pressed')
        self._player.close()
        
        while True:
            logging.info(f'instruction: {self._player.instruction.name}, state: {self._player.state.name}')
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
                self.is_wave_form_displayed = True
                self.update()
                time.sleep(0.05)
                continue
            if self.__thread_for_button.is_alive():
                self.update()
                time.sleep(0.05)
                continue
            break

        logging.info(f'instruction: {self._player.instruction.name}, state: {self._player.state.name}')

    def __play(self):
        logging.info(f'Play button was pressed.')
        state = self._player.state
        if state == AudioPlayerState.PLAYING:
            return
        elif state == AudioPlayerState.POSED:
            pass
        elif state == AudioPlayerState.READY:
            pass
        elif state == AudioPlayerState.NOT_READY:
            return
        elif state == AudioPlayerState.CLOSING:
            return
        elif state == AudioPlayerState.CLOSED:
            return

        # if threads are not alive, generate new threads and start
        if not self.__thread_for_play.is_alive():
            self.__thread_for_play = Thread(target=self._player.loop_for_playback, daemon=False)
            self.__thread_for_play.start()

        self._player.instruction = AudioPlayerInstruction.PLAY
        logging.info(f'instruction: {self._player.instruction.name}, state: {self._player.state.name}')

    def __pose(self):
        logging.info(f'Pose button was pressed.')
        state = self._player.state
        if state == AudioPlayerState.PLAYING:
            pass
        elif state == AudioPlayerState.POSED:
            return
        elif state == AudioPlayerState.READY:
            return
        elif state == AudioPlayerState.NOT_READY:
            return
        elif state == AudioPlayerState.CLOSING:
            return
        elif state == AudioPlayerState.CLOSED:
            return

        self._player.instruction = AudioPlayerInstruction.POSE
        logging.info(f'instruction: {self._player.instruction.name}, state: {self._player.state.name}')
    
    def __forward(self):
        logging.info(f'Forward button was pressed.')
        state = self._player.state
        if state == AudioPlayerState.PLAYING:
            pass
        elif state == AudioPlayerState.POSED:
            pass
        elif state == AudioPlayerState.READY:
            pass
        elif state == AudioPlayerState.NOT_READY:
            return
        elif state == AudioPlayerState.CLOSING:
            return
        elif state == AudioPlayerState.CLOSED:
            return
        
        self._player.forward()

        if state != AudioPlayerState.PLAYING:
            pos = self._audio.current_pos
            self.__update_audio_progress_bar(pos)
            self.master._audio_form_frame.update_audio_form(pos)

    def __backward(self):
        logging.info(f'Backward button was pressed.')
        state = self._player.state
        if state == AudioPlayerState.PLAYING:
            pass
        elif state == AudioPlayerState.POSED:
            pass
        elif state == AudioPlayerState.READY:
            pass
        elif state == AudioPlayerState.NOT_READY:
            return
        elif state == AudioPlayerState.CLOSING:
            return
        elif state == AudioPlayerState.CLOSED:
            return
        
        self._player.backward()

        if state != AudioPlayerState.PLAYING:
            pos = self._audio.current_pos
            self.__update_audio_progress_bar(pos)
            self.master._audio_form_frame.update_audio_form(pos)

    # def __clip_A(self):
    #     self._clip_A_button.configure(fg_color='orange')
    
    # def __clip_B(self):
    #     self._clip_B_button.configure(fg_color='orange')

    def __volume(self):
        logging.info(f'Volume button was pressed.')
        
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
        logging.info(f'Loop button was pressed.')

        loop = self._player.loop
        if loop:
            self._player.loop = False
            self._loop_off_button.grid()
            self._loop_button.grid_remove()
        else:
            self._player.loop = True
            self._loop_button.grid()
            self._loop_off_button.grid_remove()

    def __press_progress_bar(self, event:tkinter.Event):
        logging.info(f'Progress bar was pressed.')
        # logging.info(event)

        # pause if playing
        state = self._player.state
        if state == AudioPlayerState.PLAYING:
            pass
        elif state == AudioPlayerState.POSED:
            pass
        elif state == AudioPlayerState.READY:
            pass
        elif state == AudioPlayerState.NOT_READY:
            return
        elif state == AudioPlayerState.CLOSING:
            return
        elif state == AudioPlayerState.CLOSED:
            return

        if state == AudioPlayerState.PLAYING:
            self._player.instruction = AudioPlayerInstruction.POSE
            logging.info(f'instruction: {self._player.instruction.name}, state: {self._player.state.name}')
            self.__is_temporary_posed = True
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
        logging.info(f'Progress bar is being dragging.')
        # logging.info(event)

        state = self._player.state
        if state == AudioPlayerState.PLAYING:
            pass
        elif state == AudioPlayerState.POSED:
            pass
        elif state == AudioPlayerState.READY:
            pass
        elif state == AudioPlayerState.NOT_READY:
            return
        elif state == AudioPlayerState.CLOSING:
            return
        elif state == AudioPlayerState.CLOSED:
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
        logging.info(f'Progress bar was released.')
        # logging.info(event)
                      
        state = self._player.state
        if state == AudioPlayerState.PLAYING:
            pass
        elif state == AudioPlayerState.POSED:
            pass
        elif state == AudioPlayerState.READY:
            pass
        elif state == AudioPlayerState.NOT_READY:
            return
        elif state == AudioPlayerState.CLOSING:
            return
        elif state == AudioPlayerState.CLOSED:
            return

        if self.__is_temporary_posed:
            self._player.instruction = AudioPlayerInstruction.PLAY
            self.__is_temporary_posed = False
            logging.info(f'instruction: {self._player.instruction.name}, state: {self._player.state.name}')

    def __update_audio_progress_bar_when_playing(self):
        is_updated_during_ready = False

        while True:
            state = self._player.state
            if state == AudioPlayerState.PLAYING:
                self.__update_audio_progress_bar(self._audio.current_pos)
                is_updated_during_ready = True
            elif state == AudioPlayerState.POSED:
                pass
            elif state == AudioPlayerState.READY:
                if is_updated_during_ready:
                    self.__update_audio_progress_bar(self._audio.current_pos)
                    is_updated_during_ready = False
            elif state == AudioPlayerState.NOT_READY:
                pass
            elif state == AudioPlayerState.CLOSING:
                return
            elif state == AudioPlayerState.CLOSED:
                return
            
            time.sleep(0.1)

    def __update_audio_progress_bar(self, current_pos):
        val = current_pos / self._audio.nframes

        self._audio_progress_bar.set(val)
        self._audio_progress_label.configure(text=self.__pos_to_time(current_pos) + " / " + self.__pos_to_time(self._audio.nframes-1))
        self.update_idletasks()

    def __update_audio_form_when_playing(self):
        is_updated_during_ready = False

        while True:
            if not self.is_wave_form_displayed:
                time.sleep(0.1)
                continue

            state = self._player.state
            if state == AudioPlayerState.PLAYING:
                self.master._audio_form_frame.update_audio_form(self._audio.current_pos)
                is_updated_during_ready = True
            elif state == AudioPlayerState.POSED:
                pass
            elif state == AudioPlayerState.READY:
                if is_updated_during_ready:
                    self.master._audio_form_frame.update_audio_form(self._audio.current_pos)
                    is_updated_during_ready = False
            elif state == AudioPlayerState.NOT_READY:
                pass
            elif state == AudioPlayerState.CLOSING:
                return
            elif state == AudioPlayerState.CLOSED:
                return
 
            time.sleep(0.1)

    def __update_buttons_when_playing(self):
        while True:
            state = self._player.state
            if state == AudioPlayerState.PLAYING:
                pass
            elif state == AudioPlayerState.POSED:
                pass
            elif state == AudioPlayerState.READY:
                pass
            elif state == AudioPlayerState.NOT_READY:
                return
            elif state == AudioPlayerState.CLOSING:
                return
            elif state == AudioPlayerState.CLOSED:
                return

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
        # clip_A_button_light_image_path = "../Image/clip_A_light.png"
        # clip_A_button_dark_image_path = "../Image/clip_A_dark.png"
        # clip_B_button_light_image_path = "../Image/clip_B_light.png"
        # clip_B_button_dark_image_path = "../Image/clip_B_dark.png"

        self.__load_icon(self._audio_play_button, play_button_light_image_path, play_button_dark_image_path, (30, 30))
        self.__load_icon(self._audio_pose_button, pose_button_light_image_path, pose_button_dark_image_path, (30, 30))
        self.__load_icon(self._audio_forward_button, forward_button_light_image_path, forward_button_dark_image_path, (30, 30))
        self.__load_icon(self._audio_backward_button, backward_button_light_image_path, backward_button_dark_image_path, (30, 30))
        self.__load_icon(self._loop_button, loop_button_light_image_path, loop_button_dark_image_path, (20, 20))
        self.__load_icon(self._loop_off_button, loop_off_button_light_image_path, loop_off_button_dark_image_path, (20, 20))
        self.__load_icon(self._volume_button, volume_button_light_image_path, volume_button_dark_image_path, (20, 20))
        self.__load_icon(self._volume_off_button, volume_button_off_light_image_path, volume_button_off_dark_image_path, (20, 20))
        # self.__load_icon(self._clip_A_button, clip_A_button_light_image_path, clip_A_button_dark_image_path, (15, 15))
        # self.__load_icon(self._clip_B_button, clip_B_button_light_image_path, clip_B_button_dark_image_path, (15, 15))

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

    @property
    def is_wave_form_displayed(self):
        return self.__is_wave_form_displayed
    @is_wave_form_displayed.setter
    def is_wave_form_displayed(self, flag):
        self.__is_wave_form_displayed = flag


class VolumeControlloerFrame(customtkinter.CTkToplevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title('volume controller')

        self.overrideredirect(boolean=True)
        self.attributes("-transparentcolor", self._apply_appearance_mode(self._fg_color))

        self._frame = customtkinter.CTkFrame(self, corner_radius=6, border_width=1)
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

        self.master.bind("<Button-1>", lambda event: self.close(), add=True)
        self.master.bind("<Configure>", lambda event: self.close(), add=True)

        self.resizable(width=False, height=False)
        self.transient(self.master)

        self.attributes('-alpha', 0.9)

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
