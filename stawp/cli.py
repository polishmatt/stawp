
import click
import config
from build import Builder
from move import Mover

@click.group()
@click.version_option(version=config.version)
def cli():
    pass

@cli.command()
@click.argument('source')
@click.argument('dest')
@click.option(
    '--verbose/-v',
    is_flag=True,
    default=False
)
@click.option(
    '--enable-modules',
    default=''
)
@click.option(
    '--disable-modules',
    default=''
)
@click.option(
    '--discover-images/--no-discover-images', 
    default=True, 
    help='add images to a page\'s config if they are not already present'
)
@click.option(
    '--remove-images/--no-remove-images', 
    default=True, 
    help='remove images from a page\'s config if they cannot be opened'
)
def build(source, dest, **kwargs):
    try:
        builder = Builder(dist=dest, base=source, options=kwargs)
        builder.interpret()
        builder.render()
    except KeyboardInterrupt:
        click.echo('stopping...')

@cli.command()
@click.argument('image')
@click.argument('to', required=False)
def mvi(image, to):
    mover = Mover(path='.')
    mover.move(image=image, to=to)

if __name__ == '__main__':
    cli()

