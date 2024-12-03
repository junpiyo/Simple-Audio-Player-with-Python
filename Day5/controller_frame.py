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

        self._player = AudioPlayer()

        # threads
        self.__thread_for_play = Thread()
        self.__thread_for_progress_bar = Thread()
        self.__thread_for_audio_form = Thread()
        self.__thread_for_button = Thread()
        self.__event_for_play = Event()

        # widgets
        self._audio_progress_bar = customtkinter.CTkProgressBar(
            master=self,
            width=None, height=12, corner_radius=6, border_width=0,
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
            text='Play', font=(FONT_TYPE, FONT_SIZE+2, 'normal'),
            height=40, width=40, corner_radius=6,
            state="disabled",
            command=self.__play
        )
        self._audio_pose_button = customtkinter.CTkButton(
            self,
            image=None, hover=True,
            text="Pose", font=(FONT_TYPE, FONT_SIZE+2, 'normal'),
            height=40, width=40, corner_radius=6,
            state="disabled",
            command=self.__pose
        )
        self._audio_forward_button = customtkinter.CTkButton(
            self,
            image=None, hover=True,
            text=">>", font=(FONT_TYPE, FONT_SIZE+2, 'normal'),
            height=40, width=40, corner_radius=6,
            state="disabled",
            command=self.__forward
        )
        self._audio_backward_button = customtkinter.CTkButton(
            self,
            image=None, hover=True,
            text="<<", font=(FONT_TYPE, FONT_SIZE+2, 'normal'),
            height=40, width=40, corner_radius=6,
            state="disabled",
            command=self.__backward
        )

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        self._audio_progress_bar.grid(row=0, column=0, padx=(5, 5), pady=(10, 0), sticky="WE", columnspan=4)
        self._audio_progress_label.grid(row=1, column=0, padx=(10, 10), pady=(5, 0), sticky="E", columnspan=4)
        self._audio_backward_button.grid(row=2, column=0, padx=(0, 5), pady=(10, 10), sticky="E")
        self._audio_play_button.grid(row=2, column=1, padx=(5, 5), pady=(10, 10), sticky="E")
        self._audio_pose_button.grid(row=2, column=1, padx=(5, 5), pady=(10, 10), sticky="W")
        self._audio_pose_button.grid_remove()
        self._audio_forward_button.grid(row=2, column=2, padx=(5, 0), pady=(10, 10), sticky="W")

        self.__load_icons()

        # bind
        self._audio_progress_bar.bind("<Button>", self.__press_progress_bar)
        self._audio_progress_bar.bind("<B1-Motion>", self.__drag_progress_bar)
        self._audio_progress_bar.bind("<ButtonRelease>", self.__release_progress_bar)

    def load(self, audio:Audio):
        self.close()

        # init widgets
        self._audio = audio
        self._audio_play_button.configure(state='normal')
        self._audio_pose_button.configure(state='normal')
        self._audio_backward_button.configure(state='normal')
        self._audio_forward_button.configure(state='normal')
        self._audio_play_button.grid()
        self._audio_pose_button.grid_remove()

        self._audio_progress_bar.set(0.0)
        self._audio_progress_label.configure(text=self.__pos_to_time(0) + " / " + self.__pos_to_time(self._audio.nframes-1))

        # load audio
        self._player.load(audio, self.__event_for_play)

        # clear all events not to run threads
        self.__event_for_play.clear()

        if not self.__thread_for_button.is_alive():
            self.__thread_for_button = Thread(target=self.__update_button, daemon=False)
            self.__thread_for_button.start()

    def close(self): # kill living threads
        self._player.close()

        while True:
            self.__event_for_play.set()
            if self.__thread_for_play.is_alive():
                self.update()
                continue
            if self.__thread_for_progress_bar.is_alive():
                self.update()
                continue
            if self.__thread_for_audio_form.is_alive():
                self.update()
                continue
            if self.__thread_for_button.is_alive():
                self.update()
                continue
            break

    def __play(self):
        state = self._player.state
        if state == AudioPlayerState.PLAYING:
            return
        if state == AudioPlayerState.NOT_READY:
            return

        # if threads are not alive, generate new threads and start
        if not self.__thread_for_play.is_alive():
            self.__thread_for_play = Thread(target=self._player.play, daemon=False)
            self.__thread_for_play.start()
        
        if not self.__thread_for_progress_bar.is_alive():
            self.__thread_for_progress_bar = Thread(target=self.__update_audio_progress_bar_while_playing, daemon=False)
            self.__thread_for_progress_bar.start()

        if not self.__thread_for_audio_form.is_alive():
            self.__thread_for_audio_form = Thread(target=self.__update_audio_form_while_playing, daemon=False)
            self.__thread_for_audio_form.start()

        self.__event_for_play.set() # to run threads

    def __pose(self): # kill living threads
        state = self._player.state
        if state != AudioPlayerState.PLAYING:
            return
        
        self.__event_for_play.clear() # not to run threads

    def __forward(self):
        state = self._player.state
        if state == AudioPlayerState.NOT_READY:
            return
        
        self._player.forward()

        if not self.__event_for_play.is_set():
            self.__update_audio_progress_bar()
        if not self.__event_for_play.is_set():
            self.master._audio_form_frame.update_audio_form()

    def __backward(self):
        state = self._player.state
        if state == AudioPlayerState.NOT_READY:
            return
        
        self._player.backward()

        if not self.__event_for_play.is_set():
            self.__update_audio_progress_bar()
        if not self.__event_for_play.is_set():
            self.master._audio_form_frame.update_audio_form()

    def __press_progress_bar(self, event:tkinter.Event):
        # pause if playing
        print(event)
        state = self._player.state
        if state == AudioPlayerState.NOT_READY:
            return
        if state == AudioPlayerState.PLAYING:
            self.__event_for_play.clear()
            self._player.state = AudioPlayerState.TEMPORARY_POSED

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
        self.master._audio_form_frame.update_audio_form()

    def __drag_progress_bar(self, event:tkinter.Event):
        print(event)
        state = self._player.state
        if state == AudioPlayerState.NOT_READY:
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
        self.master._audio_form_frame.update_audio_form()

    def __release_progress_bar(self, event:tkinter.Event):
        print(event)
        state = self._player.state
        if state == AudioPlayerState.NOT_READY:
            return
        if state == AudioPlayerState.TEMPORARY_POSED:
            self.__event_for_play.set()
            self._player.state = AudioPlayerState.PLAYING

    def __update_audio_progress_bar_while_playing(self):
        while True:
            state = self._player.state
            if state == AudioPlayerState.NOT_READY:
                break
            if state == AudioPlayerState.PLAYING:
                self.__event_for_play.wait()
                self.__update_audio_progress_bar()

            time.sleep(0.1)

    def __update_audio_progress_bar(self):
        current_pos = self._audio.current_pos
        val = current_pos / self._audio.nframes
        self._audio_progress_bar.set(val)
        print(current_pos, val, self._audio.nframes)
        self._audio_progress_label.configure(text=self.__pos_to_time(current_pos) + " / " + self.__pos_to_time(self._audio.nframes-1))
        self.update_idletasks()

    def __update_audio_form_while_playing(self):
        while True:
            state = self._player.state
            if state == AudioPlayerState.NOT_READY:
                break
            if state == AudioPlayerState.PLAYING:
                self.__event_for_play.wait()
                self.master._audio_form_frame.update_audio_form()

            time.sleep(0.1)

    def __update_button(self):
        while True:
            state = self._player.state
            if state == AudioPlayerState.NOT_READY:
                break

            if state == AudioPlayerState.PLAYING or state == AudioPlayerState.TEMPORARY_POSED:
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
            button.configure(image=customtkinter.CTkImage(light_image=light_image, dark_image=dark_image, size=(35, 35)))
            button.configure(text="")
            button.configure(fg_color="transparent")
