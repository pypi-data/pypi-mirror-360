import os.path 
class JekyllPost:

    def __init__(self, file_path):
        self.file_path = file_path
        try:
            f = open(file_path)
            state = 0
            self.contents = ""
            for line in f:
                # remove newline character 
                line = line[:-1]
                if len(line.split(":")) > 1 and state == 1:
                    self.__setattr__("_post_" + line.split(":")[0].strip(), line.split(":")[1].strip())
                elif line.strip() == "---":
                    state = state ^ 1
                else:
                    self.contents += line + "\n"
        except FileNotFoundError:
            pass
    
    def get_title(self) -> str:
        try:
            return self._post_title.replace("\"", "")
        except AttributeError:
            return ""
    
    def get_layout(self):
        try:
            return self._post_layout
        except AttributeError:
            return "post"

    def get_contents(self) -> str:
        try:
            return self.contents
        except AttributeError:
            return ""
    
    def get_categories(self):
        try:
            return self._post_category.split(" ")
        except AttributeError:
            return []
    
    def set_title(self, title):
        self._post_title = "\"%s\"" %  title
    
    def set_contents(self, contents):
        self.contents = contents
    
    def set_string_date(self, string_date):
        self._post_date = string_date
    
    def set_layout(self, layout):
        self._post_layout = layout
    
    def get_filename(self):
        """
        Returns filename without extension 
        """
        filename = os.path.split(self.file_path)[-1]
        if filename.split(".")[-1] in ["markdown", "md"]:
            return ".".join(filename.split(".")[:-1])
        else:
            return filename 
    
    def save(self):
        if not hasattr(self, "_post_layout"):
            self._post_layout = "post"
        f = open(self.file_path, "w")
        f.write("---\n")
        for attr in dir(self):
            if attr.startswith("_post_"):
                f.write("%s: %s\n" % (attr[6:], self.__getattribute__(attr)))
        f.write("---\n")
        f.write(self.contents)
        f.close()