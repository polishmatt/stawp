
import module

class Module(module.Module):

    menu_pages = None

    def interpret(self, page, builder, source_path, file_name, default, configPage, children, parents, index, bodyhtml):
        self.menu_pages = []
        for menu in builder.config['menu']:
            self.menu_pages.append({})

        if 'menuTitle' not in page:
            page['menuTitle'] = page['title']

        for index, menu in enumerate(builder.config['menu']):
            if configPage in menu:
                self.menu_pages[index][configPage] = page

    def render(self, builder):
        file = open(builder.base+'/html/menu.html', 'r')
        menu_html = file.read()
        file.close()

        for index, menu in enumerate(builder.config['menu']):
            builder.config['menu[%d]' % index] = ''
            for path in menu:
                if path in self.menu_pages[index]:
                    page = self.menu_pages[index][path]
                    page_html = menu_html
                    for key in page:
                        page_html = page_html.replace('{{%s}}' % key, str(page[key]))
                    builder.config['menu[%d]' % index] += page_html

