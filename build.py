
import os
import yaml
import imp
import distutils.dir_util
import page_container

class Builder:

    dist = None
    base = None
    src = None
    templates = None
    options = None

    config = None
    modules = None
    pages = None

    def __init__(self, dist, base, options={}):
        self.dist = dist
        self.base = base
        self.src = os.path.join(self.base, 'src')
        self.templates = os.path.join(self.base, 'html')
        self.options = options

        distutils.dir_util.copy_tree(self.src, self.dist)

        self.modules = []
        modules_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'modules')
        for module_file in os.listdir(modules_path):
            module_path = os.path.join(modules_path, module_file)
            if os.path.isfile(module_path):
                module = imp.load_source('swp_module_' + module_file, module_path)
                module = module.Module(self)
                self.modules.append(module)

    def read_template(self, path=None, name='index'):
        if path is None:
            path = self.templates
        try:
            file = open(os.path.join(path, name + '.html'), 'r')
            template = file.read()
            file.close()
            return template
        except FileNotFoundError:
            return ''

    def read_config(self, path, name='index'):
        try:
            file = open(os.path.join(path, name + '.yaml'), 'r')
            config = file.read()
            file.close()
            config = yaml.load(config)
            if config is None:
                return {}
            else:
                return config
        except FileNotFoundError:
            return None

    def interpolate(self, string, values):
        pass

    def interpret(self):
        self.config = self.read_config(self.base, 'config')
        if self.config is None:
            self.config = {}
        if 'path' not in self.config:
            self.config['path'] = '/'

        dirs = ['.']
        self.pages = []
        topLevel = []
        parents = {
            '.': None,
        }

        while dirs:
            nextDirs = []
            for name in dirs:
                if os.path.isdir(os.path.join(self.src, name)):
                    page = page_container.Page(src=self.src, path=name, builder=self, parent=parents[name])
                    nextDirs.extend(page.children)

                    if page.config is None:
                        continue

                    page.config['body'] = self.read_template(path=page.full_path)
                    page.config['file'] = name
                    dirName = name.split('/')
                    page.config['dirName'] = dirName[len(dirName)-1]
                    page.config['path'] = self.config['path'] + name[2:]

                    if not page.is_index:
                        page.config['path'] += '/'
                    if name == '.' or name.rfind('/') == 1:
                        topLevel.append(page)


                    page.config['header'] = ''
                    page.config['categoryTitle'] = ''

                    for module in self.modules:
                        module.interpret(page=page, builder=self)
                    for child in page.children:
                        parents[child] = page
                    self.pages.append(page)

            dirs = nextDirs

    def render(self):
        template = self.read_template()

        for module in self.modules:
            module.render(builder=self)

        for key in self.config:
            template = template.replace('{{%s}}' % key, str(self.config[key]))

        for page in self.pages:
            try:
                os.remove(os.path.join(page.dist_path, 'index.yaml'))
            except FileNotFoundError:
                pass
            output = template

            for module in self.modules:
                module.render_page(page=page, builder=self)

            if 'description' in page.config:
                page.config['description'] = ' ' + page.config['description']
            else:
                page.config['description'] = ''

            page.config['pagePath'] = page.config['path']
            for key in page.config:
                output = output.replace('{{%s}}' % key, str(page.config[key]))

            file = open(os.path.join(page.dist_path, 'index.html'), 'w')
            file.write(output)
            file.close()

