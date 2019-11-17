import click
import importing.gold_miner
from post import listing, create


@click.group()
def bloom():
    print('Welcome to bloom!')


@click.command(name='import')
@click.argument('file')
def import_command(file):
    importing.gold_miner.import_from_file(file)


@click.command(name='list')
def list_command():
    listing.list_all()


@click.command(name='new')
@click.argument('title')
def new_command(title):
    create.create_post(title)


if __name__ == '__main__':
    bloom.add_command(import_command)
    bloom.add_command(list_command)
    bloom.add_command(new_command)
    bloom()
