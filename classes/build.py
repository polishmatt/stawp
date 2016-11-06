
import os
import yaml
import imp
import click
import distutils.dir_util
import classes.page

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
        modules_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'modules')
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

    def interpolate(self, template, values):
        if hasattr(values, 'iteritems'):
            iterator = values.iteritems()
        else:
            iterator = values.items()
        for key, value in iterator:
            template = template.replace('{{%s}}' % key, str(value))
        return template

    def echo(self, message, verbose=False, error=False):
        if not verbose or self.options.get('verbose', False):
            click.echo(message, err=error)

    def interpret(self):
        self.echo('interpreting config...', verbose=True)
        self.config = self.read_config(self.base, 'config')
        if self.config is None:
            self.config = {}
        if 'path' not in self.config:
            self.config['path'] = '/'

        dirs = ['.']
        self.pages = []
        parents = {
            '.': None,
        }

        while dirs:
            next_dirs = []
            for path in dirs:
                if os.path.isdir(os.path.join(self.src, path)):
                    page = classes.page.Page(src=self.src, path=path, builder=self, parent=parents[path])
                    next_dirs.extend(page.children)

                    if page.config is None:
                        continue

                    page.config['body'] = self.read_template(path=page.full_path)
                    page.config['pagePath'] = self.config.get('path', '') + path[2:]
                    if not page.is_index:
                        page.config['pagePath'] += '/'

                    for module in self.modules:
                        module.interpret(page=page, builder=self)

                    if 'description' in page.config:
                        page.config['description'] = ' ' + page.config['description']
                    else:
                        page.config['description'] = ''

                    for child in page.children:
                        parents[child] = page
                    self.pages.append(page)

            dirs = next_dirs

    def render(self):
        self.echo('rendering templates...', verbose=True)
        template = self.read_template()

        for module in self.modules:
            module.render(builder=self)

        template = self.interpolate(template, self.config)

        for page in self.pages:
            try:
                os.remove(os.path.join(page.dist_path, 'index.yaml'))
            except FileNotFoundError:
                pass

            for module in self.modules:
                module.render_page(page=page, builder=self)

            output = self.interpolate(template, page.config)
            file = open(os.path.join(page.dist_path, 'index.html'), 'w')
            file.write(output)
            file.close()
        self.echo('done', verbose=True)

