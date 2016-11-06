
import os
import sys
import yaml
import module
import click
from PIL import Image

class Module(module.Module):

    templates = {}

    rendered_galleries = None
    rendered_gallery = None

    def __init__(self, builder):
        for template in ['category', 'gallery', 'image']:
            self.templates[template] = builder.read_template(name=os.path.join('gallery', template))
        self.templates['body'] = builder.read_template(name='body')

    def interpret(self, page, builder):
        if 'menu' in builder.config:
            builder.config['bottomMenu'] = builder.config['menu'][1]
            if self.rendered_galleries is None:
                self.rendered_galleries = {}
                for page_name in builder.config['bottomMenu']:
                    self.rendered_galleries[page_name] = ''
        else:
            builder.config['bottomMenu'] = []

        if 'images' in page.config:
            changed = False
            if builder.options['discover_images']:
                for child in page.children:
                    try:
                        Image.open(os.path.join(builder.src, child))
                        child = child.split('/')
                        child = child[len(child)-1]
                        dupe = False
                        for image in page.config['images']:
                            if child == image or isinstance(image, dict) and child == list(image.keys())[0]:
                                dupe = True
                        if not dupe:
                            page.config['images'].append(child)
                            page.raw_config['images'].append(child)
                            changed = True
                    except KeyboardInterrupt:
                        raise
                    except:
                        pass

            imageHTML = ''
            page.config['pageTitle'] = page.config['title']
            if 'image_prefix' in builder.config:
                base_prefix = builder.config['image_prefix']
                out_prefix = base_prefix + page.config['dirName'] + '-'
            else:
                base_prefix = None
                out_prefix = ''

            if page.config['body'] != '':
                page.config['body'] = self.templates['body'].replace('{{body}}', page.config['body'])
            body = self.templates['gallery'].replace('{{title}}', page.config['pageTitle'])
            body = body.replace('{{body}}', page.config['body'])

            if isinstance(page.config['images'][0], list):
                images = []
                for lists in page.config['images']:
                    images = images + lists
                    images.append({'n':None})
                del images[-1]
                page.config['images'] = images

            for image in page.config['images']:
                ori = image
                title = None
                if isinstance(image, dict):
                    path = list(image.keys())[0]
                    if path == 'n':
                        imageHTML += '</div><div class="gallery">'
                    elif '.' in path and 'isCategory' not in page.config:
                        title = image[path]
                        image = path
                    else:
                        image = image[path]
                        if '/'in path or image is not None and '/' in image and '.com' not in image:
                            categoryPath = path + '/'
                            out_prefix = ''
                            if '/' in path:
                                ps = path.split('/')
                                out_prefix = ''
                                image = base_prefix + ps[len(ps)-1] + '-' + image
                        else:
                            categoryPath = page.src_path[2:] + '/' + path + '/'
                            out_prefix = base_prefix + path + '-'
                        if image is not None and '/' in image and '.com' not in image:
                            image = image.split('/')
                            out_prefix = base_prefix + image[0] + '-'
                            image = image[1]
                        body = self.templates['category'].replace('{{title}}', page.config['pageTitle'])
                        body = body.replace('{{body}}', page.config['body'])
                        page.config['isCategory'] = True

                        if '.' in path and '..' not in path:
                            attitle = ' '.join([s.capitalize() for s in path[22:-4].split('-')])
                            alt = page.config['pageTitle'] + ' - ' + attitle
                            icfg = {
                                'href': 'https://'+image,
                                'src': builder.config['path']+page.src_path[2:]+'/'+path,
                                'alt': alt,
                                'title': attitle,
                            }
                            ichtml = self.templates['image']
                            for key in icfg:
                                ichtml = ichtml.replace('{{%s}}' % key, icfg[key])
                            imageHTML += ichtml
                        else:
                            file = open(builder.src+'/' + categoryPath+'index.yaml', 'r')
                            cfg = file.read()
                            file.close()
                            cfg = yaml.load(cfg)
                            attitle = cfg['title']
                            alt = page.config['pageTitle'] + ' - ' + attitle
                            icfg = {
                                'href': builder.config['path']+categoryPath,
                                'src': builder.config['path']+categoryPath+'thumb-'+out_prefix+image,
                                'alt': alt,
                                'title': attitle,
                            }
                            ichtml = self.templates['image']
                            for key in icfg:
                                ichtml = ichtml.replace('{{%s}}' % key, icfg[key])
                            imageHTML += ichtml
                        page.config['categoryTitle'] = ''
                else:
                    name = image.split('.')[0]
                    cat = page.src_path.split('/')[-2]
                    if name.isdigit() and cat != 'collaborations':
                        title = page.config['title'] + ' #' + name
                if 'isCategory' not in page.config:
                    if not builder.options['remove_images'] or os.path.isfile(os.path.join(page.full_path, image)) and page.raw_config['images'].count(image) < 2:
                        if page.parent.is_index:
                            alt = ''
                        else:
                            alt = page.parent.config['pageTitle']
                        alt += ' - '
                        if title is not None:
                            alt += title
                        else:
                            alt += page.config['title']
                            title = ''
                        icfg = {
                            'href': out_prefix+image,
                            'src': 'thumb-'+out_prefix+image,
                            'alt': alt,
                            'title': title,
                        }
                        ichtml = self.templates['image'] 
                        for key in icfg:
                            ichtml = ichtml.replace('{{%s}}' % key, icfg[key])
                        imageHTML += ichtml
                        if not page.parent.is_index:
                            page.config['categoryTitle'] = ''
                        if 'childDescription' in page.parent.config:
                            page.config['description'] = page.parent.config['childDescription'].replace('{{title}}', page.config['title'])
                        page.config['isGallery'] = True
                    else:
                        click.echo('Removed ' + os.path.join(page.full_path, image))
                        page.raw_config['images'].remove(ori)
                        changed = True

            page.config['images'] = page.raw_config['images']
            if changed:
                file = open(page.full_path + '/index.yaml', 'w')
                file.write(yaml.dump(page.raw_config))
                file.close()
            
            body = body.replace('{{images}}', imageHTML)
            page.config['body'] = body
            if 'isCategory' in page.config and page.config['isCategory'] and page.web_path in builder.config['bottomMenu']:
                self.rendered_galleries[page.web_path] = page.config['body']
            else:
                if page.config['categoryTitle'] != '':
                    page.config['title'] = page.config['categoryTitle'] + ' - ' + page.config['title']
        else:
            page.config['pageTitle'] = ''
            page.config['categoryTitle'] = ''

    def render_page(self, page, builder):
        if self.rendered_gallery is None:
            self.rendered_gallery = ''.join(self.rendered_galleries[path] for path in builder.config['bottomMenu'])

        page.config['body'] = page.config['body'].replace('{{gallery}}', self.rendered_gallery)

        if 'isGallery' in page.config:
            for imageFile in page.config['images']:
                if isinstance(imageFile, dict):
                    imageFile = list(imageFile.keys())[0]
                file = os.path.join(page.dist_path, imageFile)
                if 'image_prefix' in builder.config:
                    outName = builder.config['image_prefix'] + page.config['dirName'] + '-'+ imageFile
                else:
                    outName = imageFile
                try:
                    image = Image.open(file)
                    image.thumbnail((500, 200), Image.ANTIALIAS)
                    image.save(os.path.join(page.dist_path, 'thumb-' + outName), "JPEG")
                    os.rename(file, os.path.join(page.dist_path, outName))
                except KeyboardInterrupt:
                    raise
                except:
                    click.echo("Failed thumbnail %s: %s" % (file, sys.exc_info()[0]))

