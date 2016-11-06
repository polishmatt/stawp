
import os
import yaml
import imp
import copy
import distutils.dir_util

class Builder:

    dist = None
    base = None
    src = None
    templates = None
    options = None

    config = None
    modules = None
    pages = None

    def __init__(self, dist, base, options):
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
            return config
        except FileNotFoundError:
            return None

    def interpret(self):
        self.config = self.read_config(self.base, 'config')
        body_template = self.read_template(name='body')

        dirs = ['.']
        self.pages = []
        index = None
        topLevel = []
        parents = {}

        while dirs:
            nextDirs = []
            for fileName in dirs:
                if os.path.isdir(os.path.join(self.src, fileName)):
                    sourcePath = os.path.join(self.src, fileName)
                    children = [fileName + '/' + item for item in os.listdir(sourcePath)]
                    nextDirs.extend(children)

                    page = self.read_config(sourcePath)
                    if page is None:
                        continue
                    default = copy.copy(page)

                    page['body'] = self.read_template(path=sourcePath)

                    page['file'] = fileName
                    dirName = fileName.split('/')
                    page['dirName'] = dirName[len(dirName)-1]
                    page['path'] = self.config['path'] + fileName[2:]
                    if fileName == '.':
                        index = page
                    else:
                        page['path'] += '/'
                    if fileName == '.' or fileName.rfind('/') == 1:
                        topLevel.append(page)

                    configPage = page['file'][1:] + '/'

                    page['header'] = ''
                    page['categoryTitle'] = ''

                    for module in self.modules:
                        module.interpret(page, self, sourcePath, fileName, default, configPage, children, parents, index, body_template)

                    for child in children:
                        parents[child] = page
                    self.pages.append(page)

            dirs = nextDirs

    def render(self):
        template = self.read_template()

        for module in self.modules:
            module.render(self)

        for key in self.config:
            template = template.replace('{{%s}}' % key, str(self.config[key]))

        for page in self.pages:
            newPath = os.path.join(self.dist, page['file'])
            try:
                os.remove(newPath + '/index.yaml')
            except FileNotFoundError:
                pass
            output = template

            for module in self.modules:
                module.render_page(page=page, builder=self, newPath=newPath)

            if 'description' in page:
                page['description'] = ' ' + page['description']
            else:
                page['description'] = ''

            page['pagePath'] = page['path']
            for key in page:
                output = output.replace('{{%s}}' % key, str(page[key]))

            file = open(newPath + '/index.html', 'w')
            file.write(output)
            file.close()

