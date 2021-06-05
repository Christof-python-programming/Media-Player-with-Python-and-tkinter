from tkinter import filedialog
from megatube_lib import *
import tkinter as tk
import glob


def get_video_list():
    path = filedialog.askdirectory(title='Wähle Ordner mit Videos aus')
    files = glob.glob(path + '/*.mp4')
    media_player.set_playlist(files)

    media_player.set_timer()
    media_player.start_player()

root = tk.Tk()
root.title('Media Player')
root.geometry('1200x600')
root.resizable(0, 0)

'# create menu bar'
menu = tk.Menu(root)

select_video_menu = tk.Menu(menu)
menu.add_cascade(label='Select', menu=select_video_menu)
select_video_menu.add_command(label='Select Directory', command=get_video_list)
root.config(menu=menu)

media_player = Media_player(root)

'# set color for media Player objects'
media_player.set_color(media_player.previous_button, 'gray25')
media_player.set_color(media_player.following_button, 'gray25')
media_player.set_color(media_player.pause_button, 'gray30')
media_player.set_color(media_player.actually_song_label, 'black')

media_player.set_text(media_player.actually_song_label, '', ('Sans', 12), 'white')

'# set size for media Player objects'
media_player.set_size(media_player.previous_button, (10, 1))
media_player.set_size(media_player.following_button, (10, 1))
media_player.set_size(media_player.pause_button, (10, 1))

media_player.set_size(media_player.interface, (1200, 550))
media_player.progress_bar_length = 830

'# get image from song witch is actually playing'
media_player.create_image_canvas((50, 25))

'# Place objects'
media_player.interface.place(x=-2, y=-2)
media_player.previous_button.place(x=2, y=570)
media_player.pause_button.place(x=102, y=570)
media_player.following_button.place(x=202, y=570)
media_player.actually_song_label.place(x=70, y=525)
media_player.progress_bar.place(x=360, y=570)
media_player.image_canvas.place(x=0, y=522)

root.mainloop()
