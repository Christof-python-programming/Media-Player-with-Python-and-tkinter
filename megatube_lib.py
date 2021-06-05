"""
    __future_releases__ = None
    __copyright__ = by Christof
    __author__ = Christof Haidegger
    __date__ = 01.06.2021
    __version__ 1.0
    __test_and_debugging__ = by Christof
    __description__ = library to create easy a media player with python and tkinter to try start the main function:

"""
from PIL import Image as _Image, ImageTk  # is required for creating images on a tkinter canvas
import tkinter as tk  # to create the interface layouts
import threading  # is needed for the timer to run it in background
import time  # time library is required for sleep function in timer
import vlc  # for video playing
import cv2  # to get the length of the video


class Media_player:
    def __init__(self, master):
        """

        :param master: root (interface)

        Description:
            -> This class is able to create a full Media Player using Python and tkinter.
            To test it pleas run this library -> on the bottom of it is a main function with a test program

        """
        self._warning_list = list()  # in this list is stored which items are not in default value
        self._player = None  # is the media player instance (self._instance.media_player_new)
        self._instance = None  # is the instance from the vlc media Player it is used to create the player itself
        self._playing = False  # if this is True a media will be on work, else no media is actually playing
        self.progress_bar_length = None  # the size of the progress bar is need to create it
        self._video_file = None  # in this var will be the path of the video stored when playing a media
        self._playlist = None  # this is going to be a list when a playlist is set
        self._check_if_timer_is_set = False  # to check if the timer thread is only started once
        self._count_timer_sets = 0  # count timer starts
        self._playlist_counter = 0  # index of the video which is actually played of the Playlist
        self.kill = False  # if this is True the media player will be destroyed and the master killed
        self._scale_var = tk.DoubleVar()  # var for the Progressbar (it is actually not need)
        self.master = master  # master (root where the Media Player is placed)
        self._video_image_size = None  # set the size of the image canvas
        self._resized_frame = None  # this variable is need to get no issue with tkinter -> variable have to be global
        self.image_canvas = None  # canvas with a single frame on it of the actually playing video
        self.interface = tk.Canvas(master, bg='black')  # interface is a Canvas, where the Video File is displayed
        self.pause_button = tk.Button(master, text='||', command=self._pause_unpause_playing)  # just place
        self.previous_button = tk.Button(master, text='<', command=None)  # only place with playlist
        self.following_button = tk.Button(master, text='>', command=None)  # only place with playlist
        self.actually_song_label = tk.Label(master)  # Label which shows the actually playing video name
        self.progress_bar = tk.Scale(master, variable=self._scale_var, command=None, from_=0, troughcolor='black',
                                     activebackground='gray', highlightthickness=2, sliderrelief='flat',
                                     tickinterval=None, to=1000, showvalue=False,
                                     orient=tk.HORIZONTAL)  # progress bar to slide between the clip

        self._create_interface()  # creates the vlc instance, player and set the hwd to master

        self.master.protocol("WM_DELETE_WINDOW", self._kill_scrollbar_thread)  # to detect if the master is destroyed

    def set_color(self, item_id, color):
        """

        :param item_id: id of the object (example: self.pause_button)
        :param color: color which should be set als background for the button
        :return: the same object with new color as self object
        """
        item_id.config(bg=color)
        self._warning_list.append(('color:', item_id, color))

    def set_size(self, item_id, size):
        """

        :param item_id: id of the object (example: self.pause_button)
        :param size: new size for the object
        :return: the same object with new size as self object
        """
        item_id.config(width=size[0], height=size[1])
        self._warning_list.append(('size:', item_id, size))

    def set_text(self, item_id, text, font=('Sans', 12), fg='black'):
        """

        :param item_id: id of the object (example: self.pause_button)
        :param text: text on the object
        :param font: font for the text default is Sans with size 12
        :param fg: color of the text
        :return: the same object with new size as self object
        """
        item_id.config(text=text, font=font, fg=fg)
        self._warning_list.append(('text', item_id, text, font))

    def set_video_file(self, file_path):
        """

        :param file_path: path of the mp4 file
        :only set the song as now play -> the song will be start by running the function start_player
        """

        self._video_file = file_path
        self.actually_song_label.config(text=self._video_file.split('/')[len(self._video_file.split('/')) - 1]
                                        .split('.')[0])  # only works well in Linux because of the \ (backslash)
        if self.image_canvas is not None:
            self._resized_frame = self.get_video_image(self._video_image_size)
            self._resized_frame = ImageTk.PhotoImage(image=self._resized_frame)

            self.image_canvas.create_image((self._video_image_size[0] / 2) + 2, (self._video_image_size[1] / 2) + 2,
                                           image=self._resized_frame)

        self.kill = True  # to kill the old timer thread
        time.sleep(0.3)   # this time is required to get no issue by killing the old thread

        if self._playing is True:
            # stop actually playing video
            self._player.stop()

        media = self._instance.media_new(file_path)
        self._player.set_media(media)

    def create_image_canvas(self, size, master=None):
        """

        :param size: size of the image canvas
        :param master: master for the image canvas (must only be set when you want an other canvas then master to set
        : set the variable image canvas from None to Canvas (it is now ready to place on the interface)
        """
        self._video_image_size = size
        if master is None:
            self.image_canvas = tk.Canvas(self.master, height=size[1], width=size[0], bg='black')
        else:
            self.image_canvas = tk.Canvas(master, height=size[1], width=size[0], bg='black')

    def get_video_image(self, size, video_path=None):
        """

        :param size: tuple (x, y) x = length of the image y = height of the image
        :param video_path: path of the video
        :return: a Canvas with a single Frame of the Video on it
        """
        video_file = video_path
        if video_path is None:
            if self._video_file is None:
                raise Exception('Pleas give the path of the video to function ore play a video and run the function '
                                'after')
            video_file = self._video_file

        video_capture = cv2.VideoCapture(video_file)
        video_capture.set(cv2.CAP_PROP_POS_FRAMES, int(video_capture.get(7) / 2))
        ret, video_image = video_capture.read()
        video_capture.release()
        if ret is False:
            raise FileNotFoundError('File path: ' + video_file + 'not found')

        resized_frame = cv2.cvtColor(cv2.resize(video_image.copy(), size), cv2.COLOR_BGR2RGB)
        pil_array = _Image.fromarray(resized_frame)

        return pil_array

    def start_player(self):
        """

        :start the video or playlist
        """
        self._player.play()
        self._playing = True
        if self._check_if_timer_is_set is False:
            self.set_timer(False)

    def set_timer(self, __manuel_set=True):
        """

        : start the timer value of the progress bar (time slider)
        """
        self._count_timer_sets += 1

        # catch available errors
        if self._count_timer_sets > 1:
            self._player.stop()
            raise Exception('Timer is set twice this is going to get an error when the song is finished!\n'
                            'Make sure that you run the function set_timer() before you start playing the video!')
        if __manuel_set is True:
            self._check_if_timer_is_set = True
            if self.progress_bar_length is None:
                raise Exception('Pleas set the length of the progress bar before placing!')

        # get video length in sec to set progress bar to the right lenght
        video_length = self._get_video_length_in_sec()
        self.progress_bar.config(length=self.progress_bar_length, to=video_length)

        # start new thread for timer -> Make sure, that every thread is killed before the next is started
        threading.Thread(target=self._run_timer, args=(self._player, self.progress_bar, video_length)).start()

    def set_playlist(self, playlist):
        """

        :param playlist: list of song paths
        :only set the playlist not start it
        """
        self.following_button.config(command=self._following_video)
        self.previous_button.config(command=self._previous_video)

        self._playlist = playlist
        self._playlist_counter = 0
        if self._playing is True:
            # stop actually playing video
            self._player.stop()
        self.set_video_file(self._playlist[0])

    def _run_timer(self, player, slider, video_length_s):
        """

        :param player: vlc media player object
        :param slider: time slider (self.progress_bar)
        :param video_length_s: length of the actually video

        : start the timer itself until the clip is finished or the root has been destroyed
        """
        # self.kill is true when the previous Thread had been killed so set is back to false for the new Thread
        self.kill = False
        expected = 0  # expect is the actually running time of the video
        expected_list = [0]  # this is only required for videos that have a runtime under 1 Second
        try:
            while expected < video_length_s and not self.kill:
                expected = player.get_time() * 0.001  # player times is given in milliseconds, so calc *0.001 to get sec
                expected_list.append(expected)
                if video_length_s <= 1:  # this if clause came normally when a giv is played
                    if expected_list[len(expected_list) - 2] == expected_list[len(expected_list) - 1] and self._playing:
                        break
                if abs(slider.get() - expected) > 5:  # when difference between the slider value and the timer
                    if self._check_if_timer_is_set is True:
                        player.set_time(slider.get() * 1000)  # set new time to timer
                    time.sleep(0.3)  # sleep 0.3 seconds to set the timer
                    continue
                if self._check_if_timer_is_set is True:
                    slider.set(expected)  # only set timer when the user want it
                time.sleep(0.3)
        except RuntimeError:
            # There might be a Runtime Error when closing the Media Player to catch this issue
            # use pass cause there is no problem at all
            pass
        self._playing = False

        if self._playlist is not None and not self.kill:
            self._start_next_playlist_song()

    def _start_next_playlist_song(self, mode=1):
        """

        :param mode: when mode 1 play the next video in the list -> list_index + 1
                     else mode is an other value play the previous video in the list -> list_index - 1
        : start the next or previous song in the playlist
        """
        if mode == 1:
            if len(self._playlist) > self._playlist_counter + 1:
                self._playlist_counter += 1
            else:
                self._playlist_counter = 0
        else:
            self._playlist_counter -= 1

        self.set_video_file(self._playlist[self._playlist_counter])  # set new video file to play
        self._count_timer_sets = 0  # to get no error when starting timer function again
        self.progress_bar.set(0)  # set the slider back to 0 when starting a new Video
        self.set_timer()  # start timer
        self.start_player()

    def _kill_scrollbar_thread(self):
        """

        : kill the media player and destroy the master where it is placed
        """
        self.kill = True
        self._player.stop()
        self.master.after(300, self.master.destroy)  # wait for 300ms to make sure, the slider thread is not in sleep

    def _get_video_length_in_sec(self):
        """

        :return: the length of the video in seconds
        """
        video_cap = cv2.VideoCapture(self._video_file)
        try:
            video_length_in_sec = int(video_cap.get(7) / video_cap.get(cv2.CAP_PROP_FPS))
        except ZeroDivisionError:
            raise IOError('File not found (' + self._video_file + ')')

        video_cap.release()  # close the video when knowing the runtime
        return video_length_in_sec

    def _create_interface(self):
        """

        :return: set the interface of the player
        """
        self._instance = vlc.Instance()
        self._player = self._instance.media_player_new()
        self._player.set_hwnd(self.interface.winfo_id())

    def _pause_unpause_playing(self):
        """

        :return: stop and start playing the actually video file
        """
        if self._playing is True:
            self._player.pause()
            self._playing = False
        else:
            self._player.play()
            self._playing = True

    def _following_video(self):
        """

        : start next song in the playlist
        """
        self.kill = True
        time.sleep(0.3)
        self._start_next_playlist_song()

    def _previous_video(self):
        """

        : start previous song in the playlist
        """
        self.kill = True
        time.sleep(0.3)
        self._start_next_playlist_song(0)

    def _get_warnings(self):
        """

        :return: return a list of all defined functions
        """
        print(self._warning_list)


def main():
    # from megatube_lib import *
    # import tkinter as tk

    root = tk.Tk()
    root.title('Media Player')
    root.geometry('1200x600')

    media_player = Media_player(root)

    '# set the wished colors for the buttons'
    media_player.set_color(media_player.previous_button, 'gray25')
    media_player.set_color(media_player.following_button, 'gray25')
    media_player.set_color(media_player.pause_button, 'gray30')

    '# set the wished size for the buttons and the slide bar and interface'
    media_player.set_size(media_player.previous_button, (10, 1))
    media_player.set_size(media_player.following_button, (10, 1))
    media_player.set_size(media_player.pause_button, (10, 1))
    media_player.set_size(media_player.interface, (1200, 550))
    media_player.progress_bar_length = 830

    '# set text for objects'
    media_player.set_text(media_player.actually_song_label, '')

    '# set Playlist (songs to play in a row)'
    media_player.set_playlist(['2.mp4', '3.mp4', '4.mp4', '5.mp4', '6.mp4'])

    '# place all Media Player objects'
    media_player.interface.place(x=-2, y=-2)
    media_player.previous_button.place(x=2, y=570)
    media_player.pause_button.place(x=102, y=570)
    media_player.following_button.place(x=202, y=570)
    media_player.actually_song_label.place(x=302, y=570)
    media_player.progress_bar.place(x=360, y=570)

    '# start media playing'
    media_player.set_timer()
    media_player.start_player()

    root.mainloop()


if __name__ == '__main__':
    main()
