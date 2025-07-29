# -*- coding: UTF-8 -*-
import os
import subprocess
import sys
from typing import Annotated

import typer
from typer import Argument, Context, Option, Typer

import cli.prompt as pmt
from __version__ import __version__
from cli.config import app as config_app
from cli.utils import complete_items
from core import Blog
from core.models import Formatter, Item, ItemType
from core.repository import get_items
from settings import AppSettings, get_settings, update_settings


app = Typer(
    name="blog",
    help="Jekyll Blog CLI Tool.",
    rich_markup_mode="rich",
    invoke_without_command=True,
)

app.add_typer(config_app, rich_help_panel="Configuration")

try:
    app_settings: AppSettings = get_settings()
    items = get_items(app_settings.root, app_settings.mode)
except Exception as e:
    pmt.error(f"Error: {e}")
    sys.exit(1)


@app.callback()
def before(
    context: Context,
    version: Annotated[bool, Option("--version", help="Print version and exit.")] = None
):
    if context.invoked_subcommand is None:
        if version:
            pmt.info(f"Jekyll CLI Version: {__version__}")
        else:
            typer.echo(context.get_help())
        raise typer.Exit()

    if context.invoked_subcommand not in ["init", "config"] and app_settings.root is None:
        pmt.error_exit(f"No blog root. Use \"blog init\" to initialize the blog.")


@app.command(rich_help_panel="Generation")
def serve(
    draft: Annotated[bool, Option(help="Start blog server with drafts.")] = app_settings.generate.draft,
    port: Annotated[int, Option(help="Listen on the given port.")] = app_settings.generate.port
):
    """Start blog server locally through jekyll."""
    command = ["bundle", "exec", "jekyll", "serve"]
    # draft option
    if draft:
        command.append("--drafts")
    if port is not None:
        command.extend(["--port", str(port)])
    try:
        os.chdir(app_settings.root)
        subprocess.run(command, shell=True)
    except Exception as e:
        pmt.error_exit(f"Error: {e}")


@app.command(rich_help_panel="Generation")
def build(
    draft: Annotated[bool, Option(help="Build including drafts.")] = app_settings.generate.draft
):
    """Build jekyll site."""
    command = ["bundle", "exec", "jekyll", "build"]
    if draft:
        command.append("--drafts")
    try:
        os.chdir(app_settings.root)
        subprocess.run(command, shell=True)
    except Exception as e:
        pmt.error_exit(f"Error: {e}")


@app.command(rich_help_panel="Operation")
def info(name: Annotated[str, Argument(help="Name of post or draft.", autocompletion=complete_items(items.articles))]):
    """Show info about post or draft."""
    blog = Blog(app_settings.root, app_settings.mode)
    result = blog.find(name, "all")
    if not result.success:
        pmt.error_exit(f"Error: {result}")

    item = result.unwrap()
    pmt.print_dict(item.info, title="[bold green]Info", show_header=False)


@app.command(name="list", rich_help_panel="Operation")
def list_items(
    draft: Annotated[bool, Option("--draft", "-d", help="List only all drafts.")] = False,
    post: Annotated[bool, Option("--post", "-p", help="List only all posts.")] = False,
):
    """List all posts and drafts or find items by name."""
    blog = Blog(app_settings.root, app_settings.mode)
    match (draft, post):
        case (True, False):
            drafts = blog.drafts
            posts = None
        case (False, True):
            drafts = None
            posts = blog.posts
        case _:
            drafts, posts = (blog.drafts, blog.posts)
    if posts:
        pmt.print_list(posts, title="[bold green]Posts", show_header=False)
    if drafts:
        pmt.print_list(drafts, title="[bold green]Drafts", show_header=False)
    if not posts and not drafts:
        pmt.error_exit("No posts or drafts found.")


@app.command(name="open", rich_help_panel="Operation")
def open_item(
    name: Annotated[str, Argument(help="Name of post or draft.", autocompletion=complete_items(items.articles))],
    editor: Annotated[str, Option("--editor", "-e", help="Open item in given editor")] = None,
):
    """Open post or draft in editor."""
    blog = Blog(app_settings.root, app_settings.mode)
    result = blog.find(name, "all")
    if not result.success:
        pmt.error_exit(f"Error: {result}")

    item = result.unwrap()
    if not editor:
        editor = app_settings.editor
    pmt.success(f"Opening \"{item.md_path}\"...")
    result = blog.open(item, editor=editor)
    if not result.success:
        pmt.error_exit(f"Error: {result}")
    pmt.success(f"Open \"{item.md_path}\" successfully.")


@app.command(rich_help_panel="Operation")
def draft(
    name: Annotated[str, Argument(help="Name of draft item.")],
    title: Annotated[str, Option("--title", "-t", help="Title of draft.")] = None,
    class_: Annotated[list[str], Option("--class", "-c", help="Categories of draft.")] = None,
    tag: Annotated[list[str], Option("--tag", "-g", help="Tags of draft.")] = None,
    editor: Annotated[str, Option("--editor", "-e", help="Open draft in given editor.")] = None,
    open_: Annotated[bool, Option("--open", "-o", help="Open draft automatically.")] = False,
):
    """Create a draft."""
    blog = Blog(app_settings.root, app_settings.mode)
    item = Item(name=name, type=ItemType.Draft)
    formatter = Formatter(
        title=title if title else "",
        categories=class_ if class_ else [],
        tags=tag if tag else [],
    )
    result = blog.create(item, formatter)
    if not result.success:
        pmt.error_exit(f"Error: {result}")

    item = result.unwrap()
    pmt.success(f"\"{item.md_path}\" created successfully.")
    if editor or open_:
        editor = app_settings.editor if not editor else editor
        pmt.info("Opening...")
        result = blog.open(item, editor=editor)
        if not result.success:
            pmt.error_exit(f"Error: {result}")
        pmt.success(f"Open \"{item.md_path}\" successfully.")


@app.command(rich_help_panel="Operation")
def post(
    name: Annotated[str, Argument(help="Name of post item.")],
    title: Annotated[str, Option("--title", "-t", help="Title of post.")] = None,
    class_: Annotated[list[str], Option("--class", "-c", help="Categories of post.")] = None,
    tag: Annotated[list[str], Option("--tag", "-g", help="Tags of post.")] = None,
    editor: Annotated[str, Option("--editor", "-e", help="Open post in given editor.")] = None,
    open_: Annotated[bool, Option("--open", "-o", help="Open post automatically.")] = False,
):
    """Create a post."""
    blog = Blog(app_settings.root, app_settings.mode)
    item = Item(name=name, type=ItemType.Post)
    formatter = Formatter(
        title=title if title else "",
        categories=class_ if class_ else [],
        tags=tag if tag else [],
    )
    result = blog.create(item, formatter)
    if not result.success:
        pmt.error_exit(f"Error: {result}")

    item = result.unwrap()
    pmt.success(f"\"{item.md_path}\" created successfully.")
    if editor or open_:
        editor = app_settings.editor if not editor else editor
        pmt.info("Opening...")
        result = blog.open(item, editor=editor)
        if not result.success:
            pmt.error_exit(f"Error: {result}")
        pmt.success(f"Open \"{item.md_path}\" successfully.")


@app.command(rich_help_panel="Operation")
def remove(
    name: Annotated[str, Argument(help="Name of post or draft.", autocompletion=complete_items(items.articles))]
):
    """Remove a post or draft."""
    blog = Blog(app_settings.root, app_settings.mode)
    result = blog.remove(name)
    if not result.success:
        pmt.error_exit(f"Error: {result}")
    pmt.success("Remove successfully.")


@app.command(rich_help_panel="Operation")
def publish(
    name: Annotated[str, Argument(help="Name of draft.", autocompletion=complete_items(items.drafts))]
):
    """Publish a draft."""
    blog = Blog(app_settings.root, app_settings.mode)
    result = blog.publish(name)
    if not result.success:
        pmt.error_exit(f"Error: {result}")
    pmt.success("Publish successfully.")


@app.command(rich_help_panel="Operation")
def unpublish(name: Annotated[str, Argument(help="Name of post.", autocompletion=complete_items(items.posts))]):
    """Unpublish a post."""
    blog = Blog(app_settings.root, app_settings.mode)
    result = blog.unpublish(name)
    if not result.success:
        pmt.error_exit(f"Error: {result}")
    pmt.success(f"Unpublish successfully.")


@app.command(rich_help_panel="Configuration")
def init():
    """Initialize the application interactively."""
    pmt.info("[bold cyan]Welcome to the Jekyll CLI application!:wave::wave::wave:")
    pmt.info("Let's set up your basic configuration.:wink:")
    root = pmt.input_path("Please enter the root path of your blog:", path_type="directory")
    mode_choices = {
        "file (A markdown file denotes a blog item.)": "file",
        "directory (A directory containing a markdown file and an assets directory denotes a blog item.)": "directory"
    }
    mode = pmt.select(message="Please choose the management mode (file or directory):", choices=mode_choices)
    editor = pmt.input_text("Please enter your editor:")

    pmt.info("You have entered the following configurations:")
    summary = {
        "Blog root path": str(root),
        "Management mode": mode,
        "Editor": editor if editor else "null",
    }
    pmt.print_dict(summary, show_header=False)

    if not pmt.confirm("Confirm your configurations?", default=True):
        pmt.error_exit("Aborted.")

    init_settings = AppSettings(
        root=root,
        mode=mode,
        editor=editor
    )
    update_settings(init_settings)
    pmt.success("Basic configuration set up successfully!")
    pmt.info("Type \"--help\" for more information.")


@app.command(rich_help_panel="Operation")
def rename(
    name: Annotated[str, Argument(help="Name of post or draft.", autocompletion=complete_items(items.articles))],
    new_name: Annotated[str, Argument(help="New name.")]
):
    """Rename a post or draft."""
    blog = Blog(app_settings.root, app_settings.mode)
    result = blog.rename(name, new_name)
    if not result.success:
        pmt.error_exit(str(result))
    pmt.success(f"Renamed successfully.")


@app.command(rich_help_panel="Configuration")
def sync():
    """Synchronize article index from <root>."""
    blog = Blog(app_settings.root, app_settings.mode)
    result = blog.synchronize()
    if not result.success:
        pmt.error_exit(f"Error: {result}")
    pmt.success("Synchronize index successfully.")
