import click
import importing.gold_miner


@click.group()
def bloom():
    print('Welcome to bloom!')


@click.command(name='import')
@click.argument('file')
def import_command(file):
    importing.gold_miner.import_from_file(file)


if __name__ == '__main__':
    bloom.add_command(import_command)
    bloom()
