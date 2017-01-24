
import os
import shutil
import yaml
import imp
import click
import distutils.dir_util
from page import Page

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

        try:
            for path in os.listdir(self.dist):
                path = os.path.join(self.dist, path)
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
        except (OSError, IOError):
            pass
        distutils.dir_util.copy_tree(self.src, self.dist)

        self.modules = []
        enabled = options.get('enable_modules', '').split(',')
        # all are disabled by default so this is just a placeholder for potential future behavior
        disabled = options.get('disable_modules', '').split(',')

        modules_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'modules')
        for module_file in os.listdir(modules_path):
            if module_file[:-3] in enabled:
                module_path = os.path.join(modules_path, module_file)
                if os.path.isfile(module_path):
                    module = imp.load_source('stawp_module_' + module_file, module_path)
                    module = module.Module(self)
                    self.modules.append(module)

    def read_template(self, path=None, name='index'):
        if path is None:
            path = self.templates
        try:
            with open(os.path.join(path, name + '.html'), 'r') as file:
                template = file.read()
            return template
        except (OSError, IOError):
            return ''

    def read_config(self, path, name='index'):
        try:
            with open(os.path.join(path, name + '.yaml'), 'r') as file:
                config = file.read()
            config = yaml.load(config)
            if config is None:
                return {}
            else:
                return config
        except (OSError, IOError):
            return None

    def interpolate(self, template, values):
        if hasattr(values, 'iteritems'):
            iterator = values.iteritems()
        else:
            iterator = values.items()
        for key, value in iterator:
            template = template.replace('{{%s}}' % key, unicode(value))
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
                    page = Page(src=self.src, path=path, builder=self, parent=parents[path])
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
            except (OSError, IOError):
                pass

            for module in self.modules:
                module.render_page(page=page, builder=self)

            output = self.interpolate(template, page.config)
            with open(os.path.join(page.dist_path, 'index.html'), 'w') as file:
                output = output.encode('utf-8')
                file.write(output)
        self.echo('done', verbose=True)

