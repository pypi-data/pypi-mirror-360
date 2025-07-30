"""Main CLI module for Talem AI."""

import asyncio  # Standard library imports should come first
import click
import pyfiglet
from main.helper.creditionals import read_db_config, write_db_config
from main.helper.store_vectors import store_vectors

@click.command()
def main():
    """Entry point for the Talem AI CLI tool."""
    ascii_art = pyfiglet.figlet_format("Talem AI CLI")
    click.echo(click.style(ascii_art, fg="blue"))

    db_config = read_db_config()

    if db_config is None:
        new_api_endpoint = click.prompt('Enter new AstraDB URL')
        new_token = click.prompt('Enter new AstraDB Token')

        write_db_config(new_api_endpoint, new_token)
        click.echo(click.style("AstraDB configurations updated successfully.", fg="green"))
    else:
        click.echo(click.style("Already have configuration, using them...", fg="yellow"))

    # Continue with the program (store_vectors re-reads the db config anyway)
    collection_name = click.prompt("Enter collection name to update")
    namespace = click.prompt("Enter namespace to update")
    pdf_or_web = click.prompt("Are you using a PDF or a webpage (pdf/web)")
    url = click.prompt("Enter URL")

    click.echo(click.style("Using stored AstraDB URL", fg="yellow"))

    if pdf_or_web not in {"pdf", "web"}:
        raise ValueError("Invalid input: please enter 'pdf' or 'web'.")

    # Run the logic to store vectors in AstraDB
    asyncio.run(store_vectors(pdf_or_web, url, collection_name, namespace))
