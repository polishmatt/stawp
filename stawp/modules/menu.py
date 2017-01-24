from __future__ import absolute_import
from stawp.module import Module

class Module(Module):

    menu_pages = None
    menu_html = None

    def interpret(self, page, builder):
        if 'menu' in builder.config:
            if self.menu_pages is None:
                self.menu_pages = []
                for menu in builder.config['menu']:
                    self.menu_pages.append({})

            if 'menuTitle' not in page.config:
                page.config['menuTitle'] = page.config['title']

            for index, menu in enumerate(builder.config['menu']):
                if page.web_path in menu:
                    self.menu_pages[index][page.web_path] = page

    def render(self, builder):
        if 'menu' in builder.config:
            if self.menu_html is None:
                self.menu_html = builder.read_template(name='menu')

            for index, menu in enumerate(builder.config['menu']):
                builder.config['menu[%d]' % index] = ''
                for path in menu:
                    if path in self.menu_pages[index]:
                        page = self.menu_pages[index][path]
                        builder.config['menu[%d]' % index] += builder.interpolate(self.menu_html, page.config)

