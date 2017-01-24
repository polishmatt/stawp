
import re
import os
import sys
import yaml
import click

class Mover:

    path = None

    def __init__(self, path):
        self.path = path

    def move(self, image, to):
        config = os.path.join(self.path, 'index.yaml')
        with open(config, 'r') as file:
            page = file.read()
        page = yaml.load(page)
        images = page['images']

        if image == 'sort':
            images.sort(key=self.separate_digits)
        else:
            images.remove(image)
            if to == 'first' or to == 'front' or to == 'start':
                to = 0
            elif to == 'last' or to == 'back' or to == 'end':
                to = len(images)
            else:
                to = images.index(to)
            images.insert(to, image)

        page['images'] = images
        click.echo(page['images'])

        page = yaml.dump(page)
        with open(config, 'w') as file:
            file.write(page)

    def separate_digits(self, string):
        return [ int(char) if char.isdigit() else char for char in re.split('(\d+)', string) ]

