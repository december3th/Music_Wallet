import imageio #pip install imageio
import time
from mutagen.mp3 import MP3 #pip3 install mutagen
import random
import pygame
from pygame import mixer
from tkinter import * #thư viện giao diện GUI
import tkinter as tk
import tkinter.font as font 
from tkinter import filedialog,ttk
from PIL import Image,ImageTk #pip install pillow
from Controller import Controller
from Model import Model
from pygame import event
from ttkthemes import themed_tk #pip install ttkthemes
import pyodbc
import threading

volume_start = True
threads = []
shuffle_song = True
auto_play = True

class View(Frame):

    name_song = '...' #Tên bài đang phát
    singer = '.....' #Tên ca sĩ đang phát
    check = False # Kiểm tra pause
    song_now = '' #Link mp3
    current_list = list() #Danh sách hiện tại
    love = False #Trạng thái bài hát yêu thích?
    repeat = True #Phát lại
    dem = 0
    dem_shuffle = 0
    check_lovelist = True #Kiểm tra lovelist đã được bật?
    frames = [] #Lưu ảnh gif
    check_gui2 = False #Kiểm tra Gui2 đã được bật?
    check_scale = True
    current_time = 0
    check_shuffle_song = False
    check_header_playlist = ''
    a = [1,1,1,1]

    #Khởi tạo
    def __init__(self,parent,controller) -> None:
        Frame.__init__(self,parent)
        self.controller = controller
        self.parent = parent

        #Lưu ảnh gif
        self.gif = Image.open("./Project/images/gif.gif")
        for frame in range(0, self.gif.n_frames):
            self.gif.seek(frame)
            View.frames.append(ImageTk.PhotoImage(self.gif))

        self.init()
    
    # Playlist frame
    def init_frame_main(self):
        # Frame playlist
        self.frame_main = Label(self,bg='black') 

        # Types of font
        self.f = font.Font(size=13,family="Calibri", weight='bold')
        self.f1 = font.Font(size=15,family="Calibri")
        self.f2 = font.Font(size=10,family="Calibri")
        self.f3 = font.Font(size=12,family="Calibri")

        # Phần header ----------------------------
        self.header_background_image = PhotoImage(file="./Project/images/header.png")
        self.Header = Label(self.frame_main,
                            bg='black',
                            image=self.header_background_image)
        self.logo_icon = PhotoImage(file="./Project/images/logo_main.png")
        self.logo = Label(self.Header,
                          height=150,
                          width=200,
                          bg="#222222",
                          image=self.logo_icon)
        self.logo.place(x=20,y=20)

        # Show song_now
        self.playing_song = Label(self.Header,
                                  bg='#222222',
                                  fg='white',
                                  text=f'{View.name_song}\n{View.singer}',
                                  anchor=CENTER,
                                  highlightthickness=1,
                                  font=self.f)
        self.playing_song.place(x=255,y=20,width=500,height=55)

        # Thanh phát nhạc
        self.style.configure("greyish.Horizontal.TProgressbar", troughcolor ="white")
        self.progress_scale = ttk.Scale(self.Header,
                                        orient="horizontal",
                                        style='TScale',
                                        from_=0,
                                        value=1,
                                        length=455,
                                        cursor='hand2')
        self.progress_scale.place(x=280,y=90,height=5)

        self.progress_scale.bind('<ButtonRelease>',self.progress_scale_moved)

        self.time_elapsed_label = tk.Label(self.Header,
                                           fg="white",
                                           background="#222222",
                                           activebackground="#222222")
        self.music_duration_label = tk.Label(self.Header,
                                             fg="white",
                                             background="#222222",
                                             activebackground="#222222")
        self.progress_scale['value'] = View.current_time
        self.time_elapsed_label.config(text=time.strftime('%M:%S', time.gmtime(self.progress_scale.get())))
        if View.check_scale==True:
            self.music_duration_label.config(text="00:00")
            View.check_scale = False
        else:
            if len(View.song_now)>0:
                self.music_duration_label.config(text=time.strftime('%M:%S', time.gmtime(self.music_length)))
                self.progress_scale.config(to=self.music_length)
            else:
                self.music_duration_label.config(text="00:00")
        self.time_elapsed_label.place(x=240,y=83)
        self.music_duration_label.place(x=740,y=83)
       
        # Nút phát ngẫu nhiên (trộn list)
        self.fix_button = Button(self.Header,
                                 bd=0,
                                 cursor='hand2',
                                 bg="#222222",
                                 activebackground='#222222',
                                 command=self.shuffle_song)
        if View.check_shuffle_song == False:
            self.fix_icon = PhotoImage(file='./Project/images/fix.png')
            self.fix_button.config(image=self.fix_icon)
        else:
            self.fix_icon = PhotoImage(file='./Project/images/fix1.png')
            self.fix_button.config(image=self.fix_icon)
        self.fix_button.place(x=705,y=125,height=40,width=40)

        # Next button
        self.next_icon = PhotoImage(file='./Project/images/next.png')
        self.next_button = Button(self.Header,
                                  image=self.next_icon,
                                  bd=0,
                                  cursor='hand2',
                                  bg="#222222",
                                  activebackground='#222222',
                                  command=self.next_song)
        self.next_button.place(x=615,y=125,height=40,width=40)
        
        # Play/Pause button
        self.play_button = Button(self.Header,
                                  bd=0,
                                  cursor='hand2',
                                  bg="#222222",
                                  activebackground='#222222',
                                  command=self.pause_song)
        if View.check == False: # Nếu nhạc dừng
            self.play_icon=PhotoImage(file='./Project/images/pause1.png')
            self.play_button.config(image=self.play_icon)
        else:
            self.play_icon=PhotoImage(file='./Project/images/pause.png')
            self.play_button.config(image=self.play_icon)
        self.play_button.place(x=525,y=125,height=40,width=40)
        
        # Previous button
        self.previous_icon = PhotoImage(file='./Project/images/previous.png')
        self.previous_button = Button(self.Header,
                                      image=self.previous_icon,
                                      bd=0,cursor='hand2',
                                      bg="#222222",
                                      activebackground='#222222',
                                      command=self.previous_song)
        self.previous_button.place(x=435,y=125,height=40,width=40)

        # Again button => lặp lại 1 bài
        self.again_button = Button(self.Header,
                                   bd=0,
                                   cursor='hand2',
                                   bg="#222222",
                                   activebackground='#222222',
                                   command=self.repeat_song)
        if View.repeat==True:
            self.again_icon = PhotoImage(file='./Project/images/stt.png')
            self.again_button.config(image=self.again_icon)
        else:
            self.again_icon = PhotoImage(file='./Project/images/again.png')
            self.again_button.config(image=self.again_icon)
        self.again_button.place(x=345,y=125,height=40,width=40)
        
        # Love button => add lovelist
        self.love_button = Button(self.Header,
                                  bd=0,
                                  cursor='hand2',
                                  bg="#222222",
                                  activebackground='#222222',
                                  command=self.add_lovelist)
        if View.love==True:
            self.love_icon = PhotoImage(file="./Project/images/loved.png")
            self.love_button.config(image=self.love_icon)
        else:
            self.love_icon = PhotoImage(file="./Project/images/love.png")
            self.love_button.config(image=self.love_icon)
        self.love_button.place(x=250,y=125,height=40,width=40)

        self.Header.place(x=20,y=20,height=200,width=780)

        # Search box --------------------------
        self.text_var = tk.StringVar() # value of search box
        self.search_image = PhotoImage(file="./Project/images/search_box.png") 
        self.search_image_label = Label(self.frame_main,
                                        cursor='hand2',
                                        bd=0,
                                        image=self.search_image,
                                        bg='black',
                                        highlightthickness=0)
        
        # Khai báo search box kiểu Entry
        self.search_box = Entry(self.search_image_label,
                                textvariable=self.text_var,
                                cursor='hand2',
                                bd=0,
                                highlightthickness=0,
                                bg='white')
        self.search_box['font'] = self.f
        self.search_box.focus_set() #con trỏ nháy
        self.search_box.bind('<KeyRelease>',self.search) # bắt search event
        self.search_box.place(x=12,y=5,height=25,width=350)

        # Search button
        self.search_icon = PhotoImage(file='./Project/images/search.png')
        self.search_button = Button(self.search_image_label,
                                    image=self.search_icon,
                                    bd=0,
                                    cursor='hand2',
                                    bg='white',
                                    highlightthickness=2,
                                    command=self.search_song)
        self.search_button.place(x=370,y=4,height=25,width=25)
        self.search_image_label.place(x=190,y=230,height=35,width=415)

        # Main chính ----------------------------------
        self.main = Label(self.frame_main,bg='black')

        # Download
        self.download_icon = PhotoImage(file="./Project/images/download.png")
        self.download = Button(self.main,
                               image=self.download_icon,
                               bd=0,
                               cursor='hand2',
                               bg='black',
                               fg='white',
                            #    activebackground='black',
                               command=self.download_song,
                               anchor=CENTER)
        self.download.place(x=400,y=0,height=30,width=70)

        # Reset button => reset/update playlist
        self.reset_icon = PhotoImage(file='./Project/images/reset.png')
        self.reset_button = Button(self.main,
                                   image=self.reset_icon,
                                   bd=0,
                                   cursor='hand2',
                                   bg='black',
                                   fg='white',
                                   activebackground='black',
                                   command=self.update_playlist,
                                   anchor=CENTER)
        self.reset_button.place(x=500,y=0,height=30,width=70)

        # Delete button
        self.delete_icon = PhotoImage(file='./Project/images/cancel.png')
        self.delete_button = Button(self.main,
                                    image=self.delete_icon,
                                    bd=0,
                                    cursor='hand2',
                                    bg='black',
                                    fg='white',
                                    activebackground='black',
                                    command=self.delete_song)
        self.delete_button.place(x=600,y=0,width=70,height=30)
        
        # Sort button
        value = ['A->Z','Z->A','Listen','Date'] # Types of sort
        self.option_var = tk.StringVar(self.main) # Selected type
        self.sort_by = OptionMenu(self.main,self.option_var,
                                  *value,
                                  command=self.option_selected)
        self.sort_by.config(bg="black",
                            fg="white",
                            text="Sorted by",
                            compound=tk.LEFT,
                            bd=0,
                            highlightthickness=0,
                            cursor="hand2",
                            activebackground='black',
                            activeforeground="white")
        self.sort_by.place(x=700,y=0,width=70,height=30)

        # Playlist frame --------------------------------
        self.list = Label(self.main,
                          bg='black')
        scroll = Scrollbar(self.list,
                           width=15,
                           bd=0,
                           bg="black") # Thanh cuộn

        # Playlist
        colums = ('name_song','singer','date','listener')
        self.play_list = ttk.Treeview(self.list,
                                      columns=colums,
                                      show='headings',
                                      yscrollcommand=scroll.set,
                                      cursor='hand2')
        self.play_list.column('name_song',width=300)
        self.play_list.column('singer',width=250)
        self.play_list.column('date',width=110)
        self.play_list.column('listener',width=100)

        ttk.Style().theme_use("alt")
        ttk.Style().configure("Treeview",
                              background='black',
                              foreground="white",
                              fieldbackground="black",
                              highlightthickness=0,
                              font = self.f2)
        ttk.Style().map("Treeview",background=[('selected','#222222')])
        ttk.Style().configure("Treeview.Heading",
                              background='black',
                              foreground="white",
                              font=self.f3)
        
        # Set name columns
        self.play_list.heading('name_song',
                               text='Name song',
                               command=self.click_name_song)
        self.play_list.heading('singer',
                               text='Singer',
                               command=self.click_singer)
        self.play_list.heading('date',
                               text='Date',
                               command=self.click_date)
        self.play_list.heading('listener',
                               text='Listener',
                               command=self.click_listener)

        # Bắt sự kiện
        self.play_list.bind("<<TreeviewSelect>>", self.selected_song) 
        self.play_list.bind("<Delete>", self.delete)

        scroll.config(command=self.play_list.yview)
        scroll.pack(side=RIGHT,fill=Y)        
        self.play_list.pack(side=LEFT,fill=BOTH)
        self.list.place(x=0,y=35,height=350,width=775)
        self.main.place(x=20,y=290,height=390,width=780)
        self.frame_main.place(x=180,y=0,height=700,width=820)

        # Update list song
        self.update_playlist()

    # Gui 1 ----------------------------------
    def init(self):
        self.style = ttk.Style()
        self.style.theme_use("classic")
        self.style.configure("TScale",background="#222222")

        # Main frame
        self.background_main = Label(self,
                                     bg='black',
                                     height=700,
                                     width=1000)
        self.background_main.pack()

        # Playlist frame
        self.init_frame_main()
            
        # Thanh điều hướng app -------------------------------
        self.background_left = Label(self, 
                                     bg="#222222", 
                                     anchor=CENTER)
        
        # Home button
        self.home_icon = PhotoImage(file="./Project/images/home.png")
        self.Home_button = Button(self.background_left,
                                  image=self.home_icon,
                                  text='Home',
                                  compound=tk.LEFT,
                                  cursor='hand2',
                                  bg="#222222",
                                  command=self.hienThiHome,
                                  bd=0,
                                  anchor=SW,
                                  fg="white",
                                  font=self.f1,
                                  activebackground='#222222',
                                  activeforeground="white")
        self.Home_button.place(x=30,y=50,height=40,width=100)

        # Lovelist button => show lovelist
        self.list_icon = PhotoImage(file="./Project/images/list.png")
        self.List_button = Button(self.background_left,
                                  image=self.list_icon,
                                  text="List",
                                  compound=tk.LEFT,
                                  cursor='hand2',
                                  bg="#222222",
                                  bd=0,
                                  anchor=SW,
                                  fg="white",
                                  font=self.f1,
                                  activebackground='#222222',
                                  activeforeground="white",
                                  command=self.lovelist)
        self.List_button.place(x=30,y=150,height=40,width=100)

        # Player button => Show player
        self.player_icon = PhotoImage(file='./Project/images/player.png')
        self.player_button = Button(self.background_left, 
                                    image=self.player_icon,
                                    text='Play',
                                    compound=tk.LEFT,
                                    cursor='hand2',
                                    bg="#222222",
                                    command=self.display,
                                    bd=0,
                                    font=self.f1,
                                    anchor=SW,
                                    fg='white',
                                    activeforeground="white",
                                    activebackground='#222222')
        self.player_button.place(x=30,y=250,height=40,width=100)

        # Volume button => turn up/down
        self.volume_icon = PhotoImage(file="./Project/images/volume.png")
        self.Volumn_button = Button(self.background_left, 
                                    image=self.volume_icon,
                                    cursor='hand2',
                                    bg="#222222",
                                    bd=0,
                                    font=self.f1,
                                    anchor=CENTER,
                                    foreground='white',
                                    activebackground='#222222',
                                    command=self.volumn_song)
        self.Volumn_button.place(x=5,y=350,height=40,width=40)
        
        self.style.configure("myStyle.Horizontal.TScale")
        self.volu_song = ttk.Scale(self.background_left, 
                                   from_=0,
                                   to=1,
                                   value=1,
                                   orient=HORIZONTAL,
                                   cursor="hand2",
                                   command=self.vol,
                                   style="myStyle.Horizontal.TScale")
        self.volu_song.place(x=45,y=370,height=4,width=100)

        # Info
        self.about_us_icon = PhotoImage(file="./Project/images/about_us.png")
        self.About_us = Label(self.background_left,
                              image=self.about_us_icon, 
                              height=40, 
                              width=40, 
                              bg='#222222',
                              font=self.f2,
                              anchor=CENTER)
        self.About_us.place(x=60,y=550)
        self.About_us_text = Label(self.background_left,
                              text='About us\n\n laptrinhpython@gmail.com',
                              bg='#222222',
                              font=self.f2,
                              anchor=CENTER,
                              foreground='white')
        self.About_us_text.place(x=0,y=600,height=50,width=155)

        self.background_left.place(x=20,y=20,height=660,width=160)
        self.pack()

    # Update thời gian phát bài hát
    def scale_update(self):
        global auto_play
        if self.progress_scale['value'] < self.music_length:
            self.progress_scale['value'] += 1
            View.current_time = self.progress_scale.get()
            self.time_elapsed_label['text'] = time.strftime('%M:%S', time.gmtime(View.current_time))
            self.updater = self.after(1000, self.scale_update) 
        elif View.repeat==False:
            a = self.controller.current_song(View.name_song)
            self.play_and_show_song(a)
        elif auto_play == True :
            self.next_song()
        elif self.progress_scale['value'] > self.music_length:
            self.progress_scale['value'] = 0
            self.time_elapsed_label['text'] = "00:00"
            self.updater = self.after(1000, self.scale_update) 

    # Next song
    def next_song(self):
        a = list()
        kt = True
        if len(View.song_now)>0:
            for i in range(len(View.current_list)):
                if View.song_now==View.current_list[i][0] :
                    if i != len(View.current_list) - 1 :
                        a = View.current_list[i+1]
                    else:
                        a = View.current_list[0]
                    kt = False
                    break
            if kt:
                View.current_list = list(self.controller.update_song())
                for i in range(len(View.current_list)):
                    if View.song_now==View.current_list[i][0] :
                        if i != len(View.current_list) - 1 :
                            a = View.current_list[i+1]
                        else:
                            a = View.current_list[0]
                        break
            self.play_and_show_song(a)
    def next_song_th(self):
        mythread = threading.Thread(target=self.next_song,daemon=True)
        threads.append(mythread)
        mythread.start() 
    
    # Show trạng thái của bài đang phát
    def play_and_show_song(self,a):
        View.check = True
        pygame.init()
        mixer.init()
        try:
            if View.dem !=0 :
                self.after_cancel(self.updater)
            View.dem = 1
            View.name_song = a[1]
            View.singer = a[2]
            View.song_now = a[0]
            if a[4] == 1:
                self.love_icon = PhotoImage(file="./Project/images/loved.png")
                self.love_button.config(image=self.love_icon)
                View.love = True
            else:
                self.love_icon = PhotoImage(file="./Project/images/love.png")
                self.love_button.config(image=self.love_icon)
                View.love = False

            self.play_icon=PhotoImage(file='./Project/images/pause.png')
            self.play_button.config(image=self.play_icon)
            
            mixer.music.load(View.song_now)
            mixer.music.play()

            music_data = MP3(View.song_now)
            self.music_length = int(music_data.info.length)
            self.progress_scale.config(value=0,to=self.music_length)
            self.time_elapsed_label['text'] = "00:00"
            self.music_duration_label['text'] = time.strftime('%M:%S', time.gmtime(self.music_length))
            self.progress_scale['to'] = self.music_length
            self.playing_song.config(text=f'{View.name_song}\n{View.singer}')
            self.scale_update()
        except:
            pass
    
    # Bắt sự kiện bài được chọn trong playlist
    def selected_song(self,event):
        a = self.play_list.item(self.play_list.selection())['values'][0]
        info_song = self.controller.current_song(a)
        self.play_and_show_song(info_song)

    # Update playlist
    def update_playlist(self):
        View.current_list = list(self.controller.update_song())
        self.play_list.delete(*self.play_list.get_children())
        for i in View.current_list:
            value = [i[1],i[2],i[3],i[5]]
            self.play_list.insert('',END,values=value) 
        if not View.check_lovelist:
            View.check_lovelist = True

    # Delete a song which selected
    def delete_song(self): # use delete button 
        mixer.quit()
        self.controller.delete_song(View.song_now)
        self.update_playlist() 
    def delete(self,event): # use keyboard
        mixer.quit()
        self.controller.delete_song(View.song_now)
        self.update_playlist()       

    # Pause and play song
    def pause_song(self):
        if len(View.song_now)>0:
            if View.check == True:
                self.after_cancel(self.updater)
                mixer.music.pause()
                self.play_icon=PhotoImage(file='./Project/images/pause1.png')
                self.play_button.config(image=self.play_icon)
                View.check = False
            else:
                self.play_icon=PhotoImage(file='./Project/images/pause.png')
                self.play_button.config(image=self.play_icon)
                mixer.music.unpause()
                self.scale_update()
                View.check = True
    def pause_song_th(self):
        mythread = threading.Thread(target=self.pause_song,daemon=True)
        threads.append(mythread)
        mythread.start()   

    # Previous song
    def previous_song(self):
        a = list()
        kt = True
        if len(View.song_now)>0:
            for i in range(len(View.current_list)):
                if View.song_now==View.current_list[i][0] :
                    if i != 0 :
                        a = View.current_list[i-1]
                    else:
                        a = View.current_list[len(View.current_list)-1]
                    kt = False
                    break
            if kt:
                View.current_list = list(self.controller.update_song())
                for i in range(len(View.current_list)):
                    if View.song_now==View.current_list[i][0] :
                        if i != 0 :
                            a = View.current_list[i-1]
                        else:
                            a = View.current_list[len(View.current_list)-1]
                        break
            self.play_and_show_song(a)
    def previous_song_th(self):
        mythread = threading.Thread( target=self.previous_song,daemon=True)
        threads.append(mythread)
        mythread.start()  
    
    # Tua thời gian chạy bài hát
    def progress_scale_moved(self,event):
        self.after_cancel(self.updater)
        View.scale_at=self.progress_scale.get()
        mixer.music.load(View.song_now)
        mixer.music.play(0,View.scale_at)
        self.scale_update()

    # Lặp lại 1 bài hát
    def repeat_song(self):
        if View.repeat:
            self.again_icon = PhotoImage(file='./Project/images/again.png')
            self.again_button.config(image=self.again_icon)
            View.repeat=False
        else:
            self.again_icon = PhotoImage(file='./Project/images/stt.png')
            self.again_button.config(image=self.again_icon)
            View.repeat= True

    # Phát ngẫu nhiên
    def shuffle_song(self):
        global auto_play
        if View.check_shuffle_song == False :
            if View.dem != 0 and View.dem_shuffle != 0: 
                self.after_cancel(self.updater)
            random.shuffle(View.current_list)
            a = View.current_list[0]
            self.play_and_show_song(a)
            View.dem_shuffle = 1
            self.fix_icon = PhotoImage(file='./Project/images/fix1.png')
            self.fix_button.config(image=self.fix_icon)
            View.check_shuffle_song = True
        else :
            self.fix_icon = PhotoImage(file='./Project/images/fix.png')
            self.fix_button.config(image=self.fix_icon)
            View.check_shuffle_song = False

    # Turn up/down volume
    def volumn_song(self):
        global volume_start
        if volume_start == True:
            self.volume_icon = PhotoImage(file="./Project/images/volume0.png")
            self.Volumn_button.config(image=self.volume_icon)
            mixer.music.set_volume(self.volu_song.set(0))
            volume_start = False
        else :
            self.volume_icon = PhotoImage(file="./Project/images/volume.png")
            self.Volumn_button.config(image=self.volume_icon)
            mixer.music.set_volume(self.volu_song.set(1))
            volume_start = True

    # Search song
    def search(self,event): # Auto search
        if View.check_lovelist == False:
            View.current_list = self.controller.search_lovelist(self.text_var.get())
        else:
            View.current_list = self.controller.search(self.text_var.get())
        self.play_list.delete(*self.play_list.get_children())
        for i in View.current_list:
            value = [i[1],i[2],i[3],i[5]]
            self.play_list.insert('',END,values=value)
    def search_song(self): # Use search button
        if View.check_lovelist == False:
            View.current_list = self.controller.search_lovelist(self.text_var.get())
        else:
            View.current_list = self.controller.search(self.text_var.get())
        self.play_list.delete(*self.play_list.get_children())
        for i in View.current_list:
            value = [i[1],i[2],i[3],i[5]]
            self.play_list.insert('',END,values=value)

    # Bật/tắt loa
    def vol(self,*args):
        global volume_start
        mixer.music.set_volume(self.volu_song.get())
        if self.volu_song.get()==0:
            self.volume_icon = PhotoImage(file="./Project/images/volume0.png")
            self.Volumn_button.config(image=self.volume_icon)
            volume_start = False
        else:
            self.volume_icon = PhotoImage(file="./Project/images/volume.png")
            self.Volumn_button.config(image=self.volume_icon)
            volume_start = True

    # Add lovelist
    def add_lovelist(self):
        if View.love == False:
            self.love_icon = PhotoImage(file="./Project/images/loved.png")
            self.love_button.config(image=self.love_icon)
            View.love = True
        else:
            self.love_icon = PhotoImage(file="./Project/images/love.png")
            self.love_button.config(image=self.love_icon)
            View.love = False
        if len(View.song_now)>0:
            self.controller.add_lovelist(View.song_now)

    # Show lovelist 
    def lovelist(self):
        if View.check_gui2:
            self.init_frame_main()
            self.button_play.place_forget()
            View.check_gui2 = False
        if View.check_lovelist == True:
            View.current_list = list(self.controller.current_lovesong())
            self.play_list.delete(*self.play_list.get_children())
            for i in View.current_list:
                value = [i[1],i[2],i[3],i[5]]
                self.play_list.insert('',END,values=value)
            View.check_lovelist = False
        else:
            self.update_playlist()
            View.check_lovelist = True

    # Sắp xếp theo kiểu được chọn
    def option_selected(self, *args):
        a = self.option_var.get()
        self.play_list.delete(*self.play_list.get_children())
        if a == 'A->Z':
            View.current_list.sort(key=lambda x : x[1])
            for i in View.current_list:
                value = [i[1],i[2],i[3],i[5]]
                self.play_list.insert('',END,values=value)
        elif a == 'Z->A':
            View.current_list.sort(key=lambda x : x[1],reverse=True)
            for i in View.current_list:
                value = [i[1],i[2],i[3],i[5]]
                self.play_list.insert('',END,values=value)
        elif a == 'Listen':
            View.current_list.sort(key=lambda x : -x[5])
            for i in View.current_list:
                value = [i[1],i[2],i[3],i[5]]
                self.play_list.insert('',END,values=value)
        elif a == 'Date':
            View.current_list.sort(key=lambda x : x[3])
            for i in View.current_list:
                value = [i[1],i[2],i[3],i[5]]
                self.play_list.insert('',END,values=value)
    
    # Sắp xếp khi click vào header playlist
    def click_name_song(self):
        View.check_header_playlist = 'name'
        if View.a[0] == 1:
            View.a[0] = 0
        else:
            View.a[0] = 1
        self.sort_ds()
    def click_singer(self):
        View.check_header_playlist = 'singer'
        if View.a[1] == 1:
            View.a[1] = 0
        else:
            View.a[1] = 1
        self.sort_ds()
    def click_date(self):
        View.check_header_playlist = 'date'
        if View.a[2] == 1:
            View.a[2] = 0
        else:
            View.a[2] = 1
        self.sort_ds()
    def click_listener(self):
        View.check_header_playlist = 'listener'
        if View.a[3] == 1:
            View.a[3] = 0
        else:
            View.a[3] = 1
        self.sort_ds()
    def sort_ds(self):
        if View.check_header_playlist=='name':
            if View.a[0] == 0:
                View.current_list.sort(key=lambda x : x[1])
            else:
                View.current_list.sort(key=lambda x : x[1],reverse=True)
        elif View.check_header_playlist=='singer':
            if View.a[1] == 0:
                View.current_list.sort(key=lambda x : x[2])
            else:
                View.current_list.sort(key=lambda x : x[2],reverse=True)
        elif View.check_header_playlist=='date':
            if View.a[2] == 0:
                View.current_list.sort(key=lambda x : x[3])
            else:
                View.current_list.sort(key=lambda x : x[3],reverse=True)
        elif View.check_header_playlist=='listener':
            if View.a[3] == 0:
                View.current_list.sort(key=lambda x : x[5])
            else:
                View.current_list.sort(key=lambda x : x[5],reverse=True)
        self.play_list.delete(*self.play_list.get_children())
        for i in View.current_list:
            value = [i[1],i[2],i[3],i[5]]
            self.play_list.insert('',END,values=value)
    
    def download_song(self):
        self.controller.download_song()

    # Show Gui1
    def hienThiHome(self):
        if View.check_gui2:
            self.init_frame_main()
            self.button_play.place_forget()
            View.check_gui2 = False

    # Show Gui2
    def display(self):
        if not View.check_gui2:
            self.frame_main.place_forget()
            self.init_frame_play()

    # Gui2 -----------------------------------
    def init_frame_play(self):
        View.check_gui2 = True

        # Main Gui2 frame
        self.button_play = Label(self,bg='#222222')
        # font
        font1 = font.Font(size=20,family="Calibri", weight='bold')

        # Đĩa nhạc
        self.label = Label(self.button_play,bg='#222222')
        self.label.place(x=20,y=0,height=400,width=740)
        self.label.after(0, self.update_label, 0)

        # show song now
        self.playing_song = Label(self.button_play,
                                  bg='black',
                                  fg='white',
                                  text=f'{View.name_song}\n{View.singer}',
                                  anchor=CENTER,
                                  highlightthickness=1,
                                  font=self.f)
        self.playing_song.place(x=20,y=420,height=60,width=740)

        # Button --------------------------------
        self.nutBam =Label(self.button_play,
                           font=font1,
                           bg='#222222',
                           fg='white',
                           bd=0,
                           highlightthickness=1)
        
        self.style.configure("greyish.Horizontal.TProgressbar", troughcolor ="#E5E4E2")
        self.progress_scale = ttk.Scale(self.nutBam,
                                        orient="horizontal",
                                        style='TScale',
                                        from_=0,
                                        length=550,
                                        cursor='hand2')
        self.progress_scale.place(x=90,y=30,height=5)
        self.progress_scale.bind('<ButtonRelease>',self.progress_scale_moved)
        self.time_elapsed_label = tk.Label(self.nutBam,
                                           fg="white",
                                           background="#222222",
                                           activebackground="#222222")
        self.music_duration_label = tk.Label(self.nutBam,
                                             fg="white",
                                             background="#222222",
                                             activebackground="#222222")
        self.progress_scale['value'] = View.current_time
        self.time_elapsed_label.config(text=time.strftime('%M:%S', time.gmtime(self.progress_scale.get())))
        if View.check_scale==True:
            self.music_duration_label.config(text="00:00")
            View.check_scale = False
        else:
            if len(View.song_now)>0:
                self.music_duration_label.config(text=time.strftime('%M:%S', time.gmtime(self.music_length)))
                self.progress_scale.config(to=self.music_length)
            else:
                self.music_duration_label.config(text="00:00")
        self.time_elapsed_label.place(x=50,y=23)
        self.music_duration_label.place(x=650,y=23)

        # Phát ngẫu nhiên
        self.fix_button = Button(self.nutBam,
                                 bd=0,
                                 cursor='hand2',
                                 bg="#222222",
                                 activebackground='#222222',
                                 command=self.shuffle_song)
        if View.check_shuffle_song == False:
            self.fix_icon = PhotoImage(file='./Project/images/fix.png')
            self.fix_button.config(image=self.fix_icon)
        else:
            self.fix_icon = PhotoImage(file='./Project/images/fix1.png')
            self.fix_button.config(image=self.fix_icon)
        self.fix_button.place(x=650,y=80,height=40,width=40)

        # Next button
        self.next_button = Button(self.nutBam,
                                  image=self.next_icon,
                                  bd=0,
                                  cursor='hand2',
                                  bg="#222222",
                                  activebackground='#222222',
                                  command= self.next_song)
        self.next_button.place(x=530,y=80,height=40,width=40)

        # Play/pause song
        self.play_button = Button(self.nutBam,
                                  bd=0,
                                  cursor='hand2',
                                  bg="#222222",
                                  activebackground='#222222',
                                  command=self.pause_song)
        if View.check == False:
            self.play_icon=PhotoImage(file='./Project/images/pause1.png')
            self.play_button.config(image=self.play_icon)
        else:
            self.play_icon=PhotoImage(file='./Project/images/pause.png')
            self.play_button.config(image=self.play_icon)
        self.play_button.place(x=410,y=80,height=40,width=40)

        # Previous button
        self.previous_button = Button(self.nutBam,
                                      image=self.previous_icon,
                                      bd=0,
                                      cursor='hand2',
                                      bg="#222222",
                                      activebackground='#222222',
                                      command=self.previous_song)
        self.previous_button.place(x=290,y=80,height=40,width=40)

        # Again button => lặp lại 1 bài
        self.again_button = Button(self.nutBam,
                                   bd=0,
                                   cursor='hand2',
                                   bg="#222222",
                                   activebackground='#222222',
                                   command=self.repeat_song)
        if View.repeat==True:
            self.again_icon = PhotoImage(file='./Project/images/stt.png')
            self.again_button.config(image=self.again_icon)
        else:
            self.again_icon = PhotoImage(file='./Project/images/again.png')
            self.again_button.config(image=self.again_icon)
        self.again_button.place(x=170,y=80,height=40,width=40)
        
        # Love button
        self.love_button = Button(self.nutBam,
                                  bd=0,
                                  cursor='hand2',
                                  bg="#222222",
                                  activebackground='#222222',
                                  command=self.add_lovelist)
        if View.love==True:
            self.love_icon = PhotoImage(file="./Project/images/loved.png")
            self.love_button.config(image=self.love_icon)
        else:
            self.love_icon = PhotoImage(file="./Project/images/love.png")
            self.love_button.config(image=self.love_icon)
        self.love_button.place(x=50,y=80,height=40,width=40)

        self.nutBam.place(x=20,y=500,height=140,width=740)
        self.button_play.place(x=200,y=20,height=660,width=780)

    # Tạo gif đĩa nhạc -------------------------
    def update_label(self, frame):
        if View.check_gui2:
            if View.check:
                self.label.config(image=View.frames[frame])
                frame += 1
                if frame == len(View.frames):
                    frame = 0
                self.label.after(100, self.update_label, frame)
            else:
                self.label.config(image=View.frames[frame])
                self.label.after(100, self.update_label, frame)

# Khởi tạo window
class App(tk.Tk):
    def __init__(self):
        super().__init__() #tạo cửa sổ giao diện
        self.title('Music player') #Tiêu đề cho cửa sổ giao diện
        self.geometry('1000x700+250+50') #kích thước cửa sổ
        self.resizable(False,False) #zoom in, zoom out
        image_icon_app = PhotoImage(file = "./Project/images/logo.png")
        self.iconphoto(False,image_icon_app) #set icon app
        
        path = "C:/Users/Mai Mai/Documents/Python_VS/Project/playlist/" # link
        # Connect database
        conx = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server}; SERVER=DESKTOP-FUI7PID; Database=Music_player; Trusted_Connection=yes;')

        # Xử lý database
        model = Model(conx,path)
        controller = Controller(model, View)

        # show GUI
        view = View(self,controller)

# Main
if __name__ == '__main__':
    app = App() 
    app.mainloop()#vòng lặp vô tận hiển thị cửa sổ