#!/usr/bin/python3

import sys
import os
from os import listdir, remove, mkdir
from os.path import isdir, join
import shutil
import yaml
import copy
import imp
from distutils.dir_util import copy_tree

dist = sys.argv[2]
if dist is None or dist == "":
    sys.exit(0)
base = sys.argv[1]
source = base + '/src'

file = open(base + '/config.yaml', 'r')
config = file.read()
config = yaml.load(config)
file.close()

file = open(base+ '/html/body.html', 'r')
bodyhtml = file.read()
file.close()

copy_tree(source, dist)

dirs = ['.']
pages = []
index = None
topLevel = []
parents = {}
config['css'] = 1
config['js'] = 1
config['bottomMenu'] = config['menu'][1]
config['topMenu'] = config['menu'][0]

modules = []
modules_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'modules')
for module_file in listdir(modules_path):
    module_path = os.path.join(modules_path, module_file)
    if os.path.isfile(module_path):
        module = imp.load_source('swp_module_' + module_file, module_path)
        module = module.Module(base_path=base, config=config)
        modules.append(module)

topMenu = {}
bottomMenu = {}
sitemap = [{
    'url': '',
  'priority': '1.0',
}, {
    'url': 'images/',
    'priority': '0.8',
}]

while dirs:
    nextDirs = []
    for fileName in dirs:
        if isdir(join(source, fileName)):
            sourcePath = join(source, fileName)
            children = [fileName + '/' + item for item in listdir(sourcePath)]
            nextDirs.extend(children)

            try:
                file = open(sourcePath + '/index.yaml', 'r')
                page = yaml.load(file.read())
                default = copy.copy(page)
                file.close()
            except FileNotFoundError:
                continue

            try:
                file = open(sourcePath + '/index.html', 'r')
                page['body'] = file.read()
                file.close()
            except FileNotFoundError:
                page['body'] = ''

            page['file'] = fileName
            mapurl = {
                'url': 'images/'+fileName[2:] + '/',
                'priority': '0.5',
            }
            dirName = fileName.split('/')
            page['dirName'] = dirName[len(dirName)-1]
            page['path'] = config['path'] + fileName[2:]
            if fileName == '.':
                index = page
            else:
                page['path'] += '/'
            if fileName == '.' or fileName.rfind('/') == 1:
                topLevel.append(page)

            if 'menuTitle' not in page:
                page['menuTitle'] = page['title']

            configPage = page['file'][1:] + '/'
            if configPage in config['bottomMenu']:
                bottomMenu[configPage] = page
            elif configPage in config['topMenu']:
                topMenu[configPage] = page

            page['header'] = ''
            page['categoryTitle'] = ''

            for module in modules:
                module.interpret_config(page, config, sourcePath, source, fileName, default, configPage, children, parents, index, bodyhtml)

            for child in children:
                parents[child] = page
            pages.append(page)

            if fileName.count('/') == 1:
                mapurl['priority'] = '0.7'
            if mapurl['url'] != 'images//' and mapurl['url'] != 'images/not-found/' and mapurl['url'] != 'images/removed/':
                sitemap.append(mapurl)

    dirs = nextDirs

file = open(base+'/html/index.html', 'r')
template = file.read()
file.close()
file = open(base+'/html/menu.html', 'r')
menu = file.read()
file.close()

config['topMenuPages'] = config['topMenu']
config['bottomMenuPages'] = config['bottomMenu']
config['topMenu'] = ''
config['bottomMenu'] = ''
for file in config['topMenuPages']:
    page = topMenu[file]
    pageHTML = menu
    for key in page:
        pageHTML = pageHTML.replace('{{%s}}' % key, str(page[key]))
    config['topMenu'] += pageHTML
for file in config['bottomMenuPages']:
    page = bottomMenu[file]
    pageHTML = menu
    for key in page:
        pageHTML = pageHTML.replace('{{%s}}' % key, str(page[key]))
    config['bottomMenu'] += pageHTML
config['menu[0]'] = config['topMenu']
config['menu[1]'] = config['bottomMenu']    

for key in config:
    template = template.replace('{{%s}}' % key, str(config[key]))

site = '<?xml version="1.0" encoding="UTF-8"?>'+"\n"
site += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"\n"
for url in sitemap:
    site += "\t<url>\n"
    site += "\t\t<loc>"+config['url']+url['url']+"</loc>\n"
    site += "\t\t<priority>"+url['priority']+"</priority>\n"
    site += "\t</url>\n"
site += '</urlset>'
file = open(dist + '/../sitemap.xml', 'w')
file.write(site)
file.close()

for page in pages:
    newPath = join(dist, page['file'])
    try:
        remove(newPath + '/index.yaml')
    except FileNotFoundError:
        pass
    output = template

    for module in modules:
        module.render_page(page=page, config=config, newPath=newPath)

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

