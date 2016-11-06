
import click
import build

VERSION = '0.1'

@click.command()
@click.argument('source')
@click.argument('dest')
@click.version_option(version=VERSION)
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
def main(source, dest, **kwargs):
    try:
        builder = build.Builder(dist=dest, base=source, options=kwargs)
        builder.interpret()
        builder.render()
    except KeyboardInterrupt:
        click.echo('stopping...')

if __name__ == '__main__':
    main()

