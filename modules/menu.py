
import module

class Module(module.Module):

    def interpret(self, page, builder):
        if 'menu' in builder.config:
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
            menu_html = builder.read_template('menu')

            for index, menu in enumerate(builder.config['menu']):
                builder.config['menu[%d]' % index] = ''
                for path in menu:
                    if path in self.menu_pages[index]:
                        page = self.menu_pages[index][path]
                        page_html = menu_html
                        for key, value in enumerate(page.config):
                            page_html = page_html.replace('{{%s}}' % key, str(value))
                        builder.config['menu[%d]' % index] += page_html

