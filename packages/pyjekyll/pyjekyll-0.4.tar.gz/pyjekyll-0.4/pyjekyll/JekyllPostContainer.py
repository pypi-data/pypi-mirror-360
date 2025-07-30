
from .JekyllPost import * 
import os 
import os.path

class JekyllPostContainer:
    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.posts = list([JekyllPost(dir_path + "/" + filename) for filename in os.listdir(dir_path)])
    
    def get_posts(self):
        return self.posts
    
    def get_post(self, name):
        return JekyllPost(os.path.join(self.dir_path, name + ".md"))
    
    def delete_post(self, name):
        os.remove(os.path.join(self.dir_path, name + ".md"))