
import os
import copy

class Page:

    src_path = None
    web_path = None
    full_path = None
    dist_path = None
    dir_name = None
    is_index = False

    parent = None
    children = None
    config = None 

    def __init__(self, src, path, builder, parent):
        self.src_path = path
        self.full_path = os.path.join(src, self.src_path)
        self.web_path = os.path.join(self.src_path[1:], '')
        self.dist_path = os.path.join(builder.dist, self.src_path)
        self.dir_name = self.src_path.split(os.sep)[-1]
        self.is_index = self.src_path == '.'

        self.children = [os.path.join(self.src_path, child) for child in os.listdir(self.full_path)]
        self.parent = parent
        self.config = builder.read_config(self.full_path)
        self.raw_config = copy.copy(self.config)

