import click
from dataset_sh.utils.author import load_author_profile, save_author_profile


@click.group(name="author")
def author_cli():
    """Update default author name and email"""
    pass


@author_cli.command(name="name")
@click.argument("name")
def name_cli(name):
    """Set default author name"""
    cfg = load_author_profile()
    if cfg is None:
        cfg = {}

    author = name
    author_email = cfg.get("author_email")

    save_author_profile(author, author_email)
    click.echo(f"Author name updated to: {author}")


@author_cli.command(name="email")
@click.argument("email")
def email_cli(email):
    """Set default author email"""
    cfg = load_author_profile()
    if cfg is None:
        cfg = {}

    author = cfg.get("author")
    author_email = email

    save_author_profile(author, author_email)
    click.echo(f"Author email updated to: {author_email}")


@author_cli.command(name="show")
def show_cli():
    """Show current author profile"""
    cfg = load_author_profile()
    if cfg:
        author = cfg.get("author", "None")
        author_email = cfg.get("author_email", "None")
        click.echo(f"Author: {author}")
        click.echo(f"Author Email: {author_email}")
    else:
        click.echo("No author profile found.")