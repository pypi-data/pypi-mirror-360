from .JekyllPostContainer import * 
import os 
import os.path
class JekyllSite:

    def __init__(self, site_path):
        self.site_path = site_path
    
    def get_post_container(self):
        return JekyllPostContainer(os.path.join(self.site_path, "_posts"))
    
    