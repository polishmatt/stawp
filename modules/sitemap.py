
import module

class Module(module.Module):
    sitemap = []
    
    def __init__(self, base_path):
        sitemap =[{
            'url': '',
          'priority': '1.0',
        }, {
            'url': 'images/',
            'priority': '0.8',
        }]

    def interpret_config(self, page, site, source_path, source, file_name, default, configPage, children, parents, index, bodyhtml):
        mapurl = {
            'url': 'images/' + file_name[2:] + '/',
            'priority': '0.5',
        }
        if file_name.count('/') == 1:
            mapurl['priority'] = '0.7'

        if mapurl['url'] != 'images//' and mapurl['url'] != 'images/not-found/' and mapurl['url'] != 'images/removed/':
            self.sitemap.append(mapurl)

    def render(self, site, dist, base):
        sitemap = '<?xml version="1.0" encoding="UTF-8"?>'+"\n"
        sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"\n"
        for url in self.sitemap:
            sitemap += "\t<url>\n"
            sitemap += "\t\t<loc>"+site['url']+url['url']+"</loc>\n"
            sitemap += "\t\t<priority>"+url['priority']+"</priority>\n"
            sitemap += "\t</url>\n"
        sitemap += '</urlset>'
        file = open(dist + '/../sitemap.xml', 'w')
        file.write(sitemap)
        file.close()

