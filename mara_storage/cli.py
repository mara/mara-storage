import click

from mara_storage import manage, storages


@click.command()
@click.option('--alias', required=True, help="Storage alias", type=click.STRING)
def ensure_storage(alias: str):
    """Creates the storage if it do not exist"""
    manage.ensure_storage(storages.storage(alias))

@click.command()
@click.option('--alias', required=True, help="Storage alias", type=click.STRING)
@click.option('-f', '--force', default=False, help="Forces the deletion of the storage including its content")
def drop_storage(alias: str, force: bool):
    """Drops a storage. The storage must be empty."""
    manage.drop_storage(storages.storage(alias), force=force)
