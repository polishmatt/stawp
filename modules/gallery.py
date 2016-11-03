
import os
import yaml
import module
from PIL import Image

class Module(module.Module):

    templates = {}

    rendered_galleries = {}
    rendered_gallery = None

    # should be options
    discover = True
    clear = True

    def __init__(self, base_path, config):
        for template in ['category', 'gallery', 'image']:
            file = open('%s/html/gallery/%s.html' % (base_path, template), 'r')
            self.templates[template] = file.read()
            file.close()

        for page in config['bottomMenu']:
            self.rendered_galleries[page] = None

    def interpret_config(self, page, config, source_path, source, file_name, default, configPage, children, parents, index, bodyhtml):
        if 'images' in page:
            changed = False
            if self.discover:
                for child in children:
                    try:
                        Image.open(os.path.join(source, child))
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
            body = self.templates['gallery'].replace('{{title}}', page['pageTitle'])
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
                            categoryPath = file_name[2:] + '/' + path + '/'
                            outPrefix = 'matt-wisniewski-'+ path + '-'
                        if image is not None and '/' in image and '.com' not in image:
                            image = image.split('/')
                            outPrefix = 'matt-wisniewski-'+ image[0] + '-'
                            image = image[1]
                        body = self.templates['category'].replace('{{title}}', page['pageTitle'])
                        body = body.replace('{{body}}', page['body'])
                        page['isCategory'] = True

                        if '.' in path and '..' not in path:
                            attitle = ' '.join([s.capitalize() for s in path[22:-4].split('-')])
                            alt = page['pageTitle'] + ' - ' + attitle
                            icfg = {
                                'href': 'https://'+image,
                                'src': config['path']+file_name[2:]+'/'+path,
                                'alt': alt,
                                'title': attitle,
                            }
                            ichtml = self.templates['image']
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
                            ichtml = self.templates['image']
                            for key in icfg:
                                ichtml = ichtml.replace('{{%s}}' % key, icfg[key])
                            imageHTML += ichtml
                        page['categoryTitle'] = ''
                else:
                    name = image.split('.')[0]
                    cat = file_name.split('/')[-2]
                    if name.isdigit() and cat != 'collaborations':
                        title = page['title'] + ' #' + name
                if 'isCategory' not in page:
                    if not self.clear or os.path.isfile(os.path.join(source_path, image)) and default['images'].count(image) < 2:
                        if parents[file_name] == index:
                            alt = ''
                        else:
                            alt = parents[file_name]['pageTitle']
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
                        ichtml = self.templates['image'] 
                        for key in icfg:
                            ichtml = ichtml.replace('{{%s}}' % key, icfg[key])
                        imageHTML += ichtml
                        if parents[file_name] != index:
                            page['categoryTitle'] = ''
                            # parents[file_name]['pageTitle']
                        if 'childDescription' in parents[file_name]:
                            page['description'] = parents[file_name]['childDescription'].replace('{{title}}', page['title'])
                        page['isGallery'] = True
                    else:
                        print(os.path.join(source_path, image))
                        default['images'].remove(ori)
                        changed = True

            page['images'] = default['images']
            if changed:
                file = open(source_path + '/index.yaml', 'w')
                file.write(yaml.dump(default))
                file.close()
            
            body = body.replace('{{images}}', imageHTML)
            page['body'] = body
            if 'isCategory' in page and page['isCategory'] and configPage in config['bottomMenu']:
                self.rendered_galleries[configPage] = page['body']
            else:
                if page['categoryTitle'] != '':
                    page['title'] = page['categoryTitle'] + ' - ' + page['title']
        else:
            page['pageTitle'] = ''
            page['categoryTitle'] = ''

    def render_page(self, page, config):
        if self.rendered_gallery is None:
            self.rendered_gallery = ''.join(self.rendered_galleries[page] for page in config['bottomMenuPages'])

        page['body'] = page['body'].replace('{{gallery}}', self.rendered_gallery)

