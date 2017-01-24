from __future__ import absolute_import
import collections
from stawp.module import Module

class Module(Module):

    sitemap = None
    
    def interpret(self, page, builder):
        if self.sitemap == None:
            self.sitemap = collections.OrderedDict()
            for url in builder.config.get('sitemap_overrides', []):
                if url['loc'] is None:
                    url['loc'] = '/'
                self.sitemap[url['loc']] = url

        sitemap_path = page.src_path[2:]
        if len(sitemap_path) > 0:
            sitemap_path += '/'
        if page.src_path.count('/') == 1:
            priority = builder.config.get('sitemap_priority_toplevel', '0.7')
        else:
            priority = builder.config.get('sitemap_priority_default', '0.5')
        url = {
            'loc': builder.config.get('path', '/') + sitemap_path,
            'priority': priority,
        }
        
        if url['loc'] not in self.sitemap and url['loc'] not in builder.config.get('sitemap_ignore', []):
            self.sitemap[url['loc']] = url

    def render(self, builder):
        sitemap = '<?xml version="1.0" encoding="UTF-8"?>'+"\n"
        sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"\n"
        if hasattr(self.sitemap, 'iteritems'):
            values = self.sitemap.iteritems()
        else:
            values = self.sitemap.items()
        for loc, url in values:
            sitemap += "\t<url>\n"
            sitemap += "\t\t<loc>"+builder.config['url']+url['loc'][1:]+"</loc>\n"
            sitemap += "\t\t<priority>"+str(url['priority'])+"</priority>\n"
            sitemap += "\t</url>\n"
        sitemap += '</urlset>'
        with open(builder.dist + '/../sitemap.xml', 'w') as file:
            file.write(sitemap)

