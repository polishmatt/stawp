from __future__ import absolute_import
import os
import sys
import yaml
from PIL import Image
from stawp.module import Module

class Module(Module):

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

        page.config['categoryTitle'] = ''

        if 'images' in page.config:
            # If the page config has changed and should be written
            changed = False

            if builder.options['discover_images']:
                for child in page.children:
                    try:
                        Image.open(os.path.join(builder.src, child))
                        child = child.split('/')[-1]
                        found = False
                        for image in page.config['images']:
                            if child == image or isinstance(image, dict) and child == list(image.keys())[0]:
                                found = True
                                break

                        if not found:
                            page.config['images'].append(child)
                            page.raw_config['images'].append(child)
                            changed = True
                    except KeyboardInterrupt:
                        raise
                    except:
                        pass

            rendered_gallery = ''
            page.config['pageTitle'] = page.config['title']
            if 'image_prefix' in builder.config:
                base_prefix = builder.config['image_prefix']
                out_prefix = base_prefix + page.dir_name + '-'
            else:
                base_prefix = None
                out_prefix = ''

            if isinstance(page.config['images'][0], list):
                images = []
                for group in page.config['images']:
                    images += group
                    images.append({'n': None})
                del images[-1]
                page.config['images'] = images

            for image in page.config['images']:
                original = image
                title = None

                if isinstance(image, dict):
                    path = list(image.keys())[0]
                    if path == 'n':
                        rendered_gallery += '</div><div class="gallery">'
                    elif '.' in path and 'isCategory' not in page.config:
                        title = image[path]
                        image = path
                    else:
                        image = image[path]
                        if '/'in path or image is not None and '/' in image and '.com' not in image:
                            category_path = path + '/'
                            out_prefix = ''
                            if '/' in path:
                                out_prefix = ''
                                image = base_prefix + path.split('/')[-1] + '-' + image
                        else:
                            category_path = page.src_path[2:] + '/' + path + '/'
                            out_prefix = base_prefix + path + '-'
                        if image is not None and '/' in image and '.com' not in image:
                            image = image.split('/')
                            out_prefix = base_prefix + image[0] + '-'
                            image = image[1]

                        page.config['isCategory'] = True
                        page.config['categoryTitle'] = ''

                        if '.' in path and '..' not in path:
                            alt_title = ' '.join([segment.capitalize() for segment in path[22:-4].split('-')])
                            rendered_gallery += builder.interpolate(self.templates['image'], {
                                'href': 'https://' + image,
                                'src': builder.config['path'] + page.src_path[2:] + '/' + path,
                                'alt': page.config['pageTitle'] + ' - ' + alt_title,
                                'title': alt_title,
                            })
                        else:
                            category_config = builder.read_config(path=os.path.join(builder.src, category_path))
                            alt_title = category_config['title']
                            rendered_gallery += builder.interpolate(self.templates['image'], {
                                'href': builder.config['path'] + category_path,
                                'src': builder.config['path'] + category_path + 'thumb-' + out_prefix + image,
                                'alt': page.config['pageTitle'] + ' - ' + alt_title,
                                'title': alt_title,
                            })
                else:
                    name = image.split('.')[0]
                    category = page.src_path.split('/')[-2]
                    if name.isdigit() and category not in builder.config.get('gallery_autocaption_ignore', []):
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
                        rendered_gallery += builder.interpolate(self.templates['image'], {
                            'href': out_prefix + image,
                            'src': 'thumb-' + out_prefix + image,
                            'alt': alt,
                            'title': title,
                        })

                        if not page.parent.is_index:
                            page.config['categoryTitle'] = ''
                        if 'childDescription' in page.parent.config:
                            page.config['description'] = builder.interpolate(page.parent.config['childDescription'], {
                                'title': page.config['title'],
                            })
                        page.config['isGallery'] = True
                    else:
                        builder.echo('Removed ' + os.path.join(page.full_path, image))
                        page.raw_config['images'].remove(original)
                        changed = True

            page.config['images'] = page.raw_config['images']
            if changed:
                with open(os.path.join(page.full_path, 'index.yaml'), 'w') as file:
                    file.write(yaml.dump(page.raw_config))
            
            if page.config['body'] != '':
                page.config['body'] = builder.interpolate(self.templates['body'], {
                    'body': page.config['body'],
                })
            body_template = 'category' if page.config.get('isCategory', False) else 'gallery'
            page.config['body'] = builder.interpolate(self.templates[body_template], {
                'title': page.config['pageTitle'],
                'body': page.config['body'],
                'images': rendered_gallery,
            })

            if page.config.get('isCategory', False) and page.web_path in builder.config['bottomMenu']:
                self.rendered_galleries[page.web_path] = page.config['body']
            elif page.config['categoryTitle'] != '':
                page.config['title'] = page.config['categoryTitle'] + ' - ' + page.config['title']
        else:
            page.config['pageTitle'] = ''
            page.config['categoryTitle'] = ''

    def render_page(self, page, builder):
        if self.rendered_gallery is None:
            self.rendered_gallery = ''.join(self.rendered_galleries[path] for path in builder.config['bottomMenu'])

        page.config['body'] = builder.interpolate(page.config['body'], {
            'gallery': self.rendered_gallery,
        })

        if 'isGallery' in page.config:
            for original_name in page.config['images']:
                if isinstance(original_name, dict):
                    original_name = list(original_name.keys())[0]
                file = os.path.join(page.dist_path, original_name)
                if 'image_prefix' in builder.config:
                    output_name = builder.config['image_prefix'] + page.dir_name + '-'+ original_name
                else:
                    output_name = original_name
                try:
                    image = Image.open(file)
                    image.thumbnail((500, 200), Image.ANTIALIAS)
                    image.save(os.path.join(page.dist_path, 'thumb-' + output_name), 'JPEG')
                    os.rename(file, os.path.join(page.dist_path, output_name))
                except KeyboardInterrupt:
                    raise
                except:
                    raise
                    builder.echo("Failed thumbnail %s: %s" % (file, sys.exc_info()[0]), error=True)

