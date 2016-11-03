#!/usr/bin/python3

import sys
import json
from os import listdir, remove, mkdir, rename
from os.path import isdir, isfile, join
import shutil
import yaml
from PIL import Image
import copy
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

file = open(base + '/html/gallery/category.html', 'r')
category = file.read()
file.close()
file = open(base + '/html/gallery/gallery.html', 'r')
exhibit = file.read()
file.close()
file = open(base + '/html/gallery/image.html', 'r')
ihtml = file.read()
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
gallery = {}
config['css'] = 1
config['js'] = 1
config['bottomMenu'] = config['menu'][1]
config['topMenu'] = config['menu'][0]
for page in config['bottomMenu']:
    gallery[page] = None
topMenu = {}
bottomMenu = {}
sitemap = [{
    'url': '',
  'priority': '1.0',
}, {
    'url': 'images/',
    'priority': '0.8',
}]

# should be options
discover = True
clear = True

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
            if 'images' in page:
                changed = False
                if discover:
                    for child in children:
                        try:
                            Image.open(join(source, child))
                            child = child.split('/')
                            child = child[len(child)-1]
                            dupe = False
                            for image in page['images']:
                                if child == image or isinstance(image, dict) and child == list(image.keys())[0]:
                                    dupe = True
                            if not dupe:
                                page['images'].append(child)
                                default['images'].append(child)
                                changed = True
                        except:
                            pass

                imageHTML = ''
                page['pageTitle'] = page['title']
                outPrefix = 'matt-wisniewski-' + page['dirName'] + '-'

                if page['body'] != '':
                    page['body'] = bodyhtml.replace('{{body}}', page['body'])
                body = exhibit.replace('{{title}}', page['pageTitle'])
                body = body.replace('{{body}}', page['body'])

                if isinstance(page['images'][0], list):
                    images = []
                    for lists in page['images']:
                        images = images + lists
                        images.append({'n':None})
                    del images[-1]
                    page['images'] = images

                for image in page['images']:
                    ori = image
                    title = None
                    if isinstance(image, dict):
                        path = list(image.keys())[0]
                        if path == 'n':
                            imageHTML += '</div><div class="gallery">'
                        elif '.' in path and 'isCategory' not in page:
                            title = image[path]
                            image = path
                        else:
                            image = image[path]
                            if '/'in path or image is not None and '/' in image and '.com' not in image:
                                categoryPath = path + '/'
                                outPrefix = ''
                                if '/' in path:
                                    ps = path.split('/')
                                    outPrefix = ''
                                    image = 'matt-wisniewski-' + ps[len(ps)-1] + '-' + image
                            else:
                                categoryPath = fileName[2:] + '/' + path + '/'
                                outPrefix = 'matt-wisniewski-'+ path + '-'
                            if image is not None and '/' in image and '.com' not in image:
                                image = image.split('/')
                                outPrefix = 'matt-wisniewski-'+ image[0] + '-'
                                image = image[1]
                            body = category.replace('{{title}}', page['pageTitle'])
                            body = body.replace('{{body}}', page['body'])
                            page['isCategory'] = True

                            if '.' in path and '..' not in path:
                                attitle = ' '.join([s.capitalize() for s in path[22:-4].split('-')])
                                alt = page['pageTitle'] + ' - ' + attitle
                                icfg = {
                                    'href': 'https://'+image,
                                    'src': config['path']+fileName[2:]+'/'+path,
                                    'alt': alt,
                                    'title': attitle,
                                }
                                ichtml = ihtml
                                for key in icfg:
                                    ichtml = ichtml.replace('{{%s}}' % key, icfg[key])
                                imageHTML += ichtml
                            else:
                                file = open(source+'/' + categoryPath+'index.yaml', 'r')
                                cfg = file.read()
                                file.close()
                                cfg = yaml.load(cfg)
                                attitle = cfg['title']
                                alt = page['pageTitle'] + ' - ' + attitle
                                icfg = {
                                    'href': config['path']+categoryPath,
                                    'src': config['path']+categoryPath+'thumb-'+outPrefix+image,
                                    'alt': alt,
                                    'title': attitle,
                                }
                                ichtml = ihtml
                                for key in icfg:
                                    ichtml = ichtml.replace('{{%s}}' % key, icfg[key])
                                imageHTML += ichtml
                            page['categoryTitle'] = ''
                    else:
                        name = image.split('.')[0]
                        cat = fileName.split('/')[-2]
                        if name.isdigit() and cat != 'collaborations':
                            title = page['title'] + ' #' + name
                    if 'isCategory' not in page:
                        if not clear or isfile(join(sourcePath, image)) and default['images'].count(image) < 2:
                            if parents[fileName] == index:
                                alt = ''
                            else:
                                alt = parents[fileName]['pageTitle']
                            alt += ' - '
                            if title is not None:
                                alt += title
                            else:
                                alt += page['title']
                                title = ''
                            icfg = {
                                'href': outPrefix+image,
                                'src': 'thumb-'+outPrefix+image,
                                'alt': alt,
                                'title': title,
                            }
                            ichtml = ihtml
                            for key in icfg:
                                ichtml = ichtml.replace('{{%s}}' % key, icfg[key])
                            imageHTML += ichtml
                            if parents[fileName] != index:
                                page['categoryTitle'] = ''
                                # parents[fileName]['pageTitle']
                            if 'childDescription' in parents[fileName]:
                                page['description'] = parents[fileName]['childDescription'].replace('{{title}}', page['title'])
                            page['isGallery'] = True
                        else:
                            print(join(sourcePath, image))
                            default['images'].remove(ori)
                            changed = True

                page['images'] = default['images']
                if changed:
                    file = open(sourcePath + '/index.yaml', 'w')
                    file.write(yaml.dump(default))
                    file.close()
                
                body = body.replace('{{images}}', imageHTML)
                page['body'] = body
                if 'isCategory' in page and page['isCategory'] and configPage in config['bottomMenu']:
                    gallery[configPage] = page['body']
                else:
                    if page['categoryTitle'] != '':
                        page['title'] = page['categoryTitle'] + ' - ' + page['title']
            else:
                page['pageTitle'] = ''
                page['categoryTitle'] = ''

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

gallery = ''.join(gallery[page] for page in config['bottomMenuPages'])

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

    page['body'] = page['body'].replace('{{gallery}}', gallery)
    if 'description' in page:
        page['description'] = ' ' + page['description']
    else:
        page['description'] = ''

    if 'isGallery' in page:
        for imageFile in page['images']:
            if isinstance(imageFile, dict):
                imageFile = list(imageFile.keys())[0]
            file = join(newPath, imageFile)
            outName = 'matt-wisniewski-' + page['dirName'] + '-'+ imageFile
            try:
                image = Image.open(file)
                image.thumbnail((500, 200), Image.ANTIALIAS)
                image.save(join(newPath, 'thumb-' + outName), "JPEG")
                rename(file, join(newPath, outName))
            except:
                print("Failed thumbnail %s: %s" % (file, sys.exc_info()[0]))

    page['pagePath'] = page['path']
    for key in page:
        output = output.replace('{{%s}}' % key, str(page[key]))

    file = open(newPath + '/index.html', 'w')
    file.write(output)
    file.close()

