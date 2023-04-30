class Controller:
    # Khởi tạo
    def __init__(self,model,view) -> None:
        self.model = model
        self.view = view

    def update_song(self):
        return self.model.update_song()
    
    def current_song(self,name):
        return self.model.current_song(name)
    
    def delete_song(self,name):
        self.model.delete_song(name)

    def add_lovelist(self,name):
        self.model.add_lovelist(name)

    def current_lovesong(self):
        return self.model.current_lovesong()

    def search(self,value):
        return self.model.search(value)
    
    def search_lovelist(self,value):
        return self.model.search_lovelist(value)
    
    def download_song(self):
        self.model.download_song()
    

