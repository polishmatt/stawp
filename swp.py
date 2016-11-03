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

modules = []
modules_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'modules')
for module_file in listdir(modules_path):
    module_path = os.path.join(modules_path, module_file)
    if os.path.isfile(module_path):
        module = imp.load_source('swp_module_' + module_file, module_path)
        module = module.Module(base_path=base, site=config)
        modules.append(module)

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
            dirName = fileName.split('/')
            page['dirName'] = dirName[len(dirName)-1]
            page['path'] = config['path'] + fileName[2:]
            if fileName == '.':
                index = page
            else:
                page['path'] += '/'
            if fileName == '.' or fileName.rfind('/') == 1:
                topLevel.append(page)

            configPage = page['file'][1:] + '/'

            page['header'] = ''
            page['categoryTitle'] = ''

            for module in modules:
                module.interpret_config(page, config, sourcePath, source, fileName, default, configPage, children, parents, index, bodyhtml)

            for child in children:
                parents[child] = page
            pages.append(page)

    dirs = nextDirs

file = open(base+'/html/index.html', 'r')
template = file.read()
file.close()

for module in modules:
    module.render(site=config, dist=dist, base=base)

for key in config:
    template = template.replace('{{%s}}' % key, str(config[key]))

for page in pages:
    newPath = join(dist, page['file'])
    try:
        remove(newPath + '/index.yaml')
    except FileNotFoundError:
        pass
    output = template

    for module in modules:
        module.render_page(page=page, site=config, newPath=newPath)

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

