import os
from pygame import mixer
from tkinter import filedialog,ttk
import datetime
import eyed3
import webbrowser
import shutil

class Model:
    # Khởi tạo
    def __init__(self,conx,path) -> None:
        self.path = path
        self.conx = conx
        self.cursor = self.conx.cursor()

    # Update list song
    def update_song(self):
        source_dir = "C:/Users/Mai Mai/Downloads/"
        files = os.listdir(source_dir)
        for file_name in files:
            if os.path.splitext(file_name)[1]=='.mp3':
                source_file = os.path.join(source_dir, file_name)
                if os.path.isfile(source_file):
                    shutil.move(source_file, self.path)

        # Ghi vào CSDL
        add = '''INSERT INTO song (id_song,name_song,singer,date_download,love,listen)
                VALUES (?,?,?,?,?,?)'''
        
        # Loại bỏ bài không tồn tại trong CSDL
        ds = list(self.cursor.execute('SELECT id_song FROM song'))
        self.cursor.commit()
        for a in ds:
            if not os.path.exists(a[0]):
                self.cursor.execute(f"DELETE TOP(1) FROM song WHERE id_song = '{a[0]}'")
                self.cursor.commit()

        # Ghi vào CSDL
        for root,dirs,files in os.walk(self.path):
            for file in files:
                if os.path.splitext(file)[1]=='.mp3':
                    directory = (root+file).replace('\\','/')
                    tag = eyed3.load(directory)
                    value = list()
                    value.append(directory)
                    value.append(tag.tag.title)
                    value.append(tag.tag.artist)
                    value.append(datetime.datetime.strftime(datetime.datetime.today(),"%d/%m/%Y"))
                    value.append(0)
                    value.append(0)
                    try:
                        self.cursor.execute(add,value)
                        self.conx.commit()
                    except:
                        pass
        
        # Lấy ds
        self.cursor.execute('SELECT * FROM song')
        return self.cursor
    
    # Bài đang được chọn
    def current_song(self,name):
        self.cursor.execute(f"UPDATE song SET listen = listen + 1 WHERE name_song=N'{name}'")
        self.cursor.commit()
        self.cursor.execute(f"SELECT TOP(1) * FROM song WHERE song.name_song=N'{name}'")
        a = list(self.cursor)
        self.cursor.commit()
        return a[0]

    # Xóa khỏi CSDL
    def delete_song(self,name):
        os.remove(name)
        self.cursor.execute(f"DELETE TOP(1) FROM song WHERE id_song=N'{name}'")
        self.conx.commit()
        
    # Thêm vào danh sách yêu thích
    def add_lovelist(self,name):
        self.cursor.execute(f"UPDATE song SET love = CASE\
                                            WHEN love = 1 then 0\
                                            ELSE 1\
                                        END\
                            WHERE id_song = N'{name}'")
        self.conx.commit()
        
    # Danh sách yêu thích
    def current_lovesong(self):
        self.cursor.execute('SELECT * FROM song WHERE love = 1')
        return self.cursor

    # Tìm kiếm
    def search(self,value):
        value = value.lower()
        self.cursor.execute(f"SELECT *,LOWER(name_song), LOWER(singer) FROM song AS song1 WHERE song1.name_song LIKE N'%{value}%'\
                            or song1.singer LIKE N'%{value}%'")
        a = list(self.cursor)
        self.conx.commit()
        return a
    
    # Tìm kiếm trong ds yêu thích
    def search_lovelist(self,value):
        value = value.lower()
        self.cursor.execute(f"SELECT *,LOWER(name_song), LOWER(singer) FROM song AS song1 WHERE (song1.name_song LIKE N'%{value}%'\
                            or song1.singer LIKE N'%{value}%') and song1.love = 1")
        a = list(self.cursor)
        self.conx.commit()
        return a
    
    def download_song(self):
        webbrowser.open("https://www.nhaccuatui.com/")

    
                    
                    
        

