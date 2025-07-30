import logging

import click

from .checker import check_urls  # Relative import from sibling module

# This is the APPLICATION, so it can configure logging.
# Basic configuration for console output.
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)-8s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Get a logger for the CLI module itself
log = logging.getLogger(__name__)


@click.command()
@click.argument("urls", nargs=-1)  # Read multiple URLs from command line
@click.option("--timeout", default=5, help="Timeout in seconds for each request.")
@click.option("--verbose", "-v", is_flag=True, help="Enable debug logging.")
def main(urls, timeout, verbose):
    """
    A simple CLI to check the status of one or more URLs.
    Example: check-urls https://google.com https://github.com
    """
    if verbose:
        # Set root logger level to DEBUG if -v is passed
        logging.getLogger().setLevel(logging.DEBUG)
        log.debug("Verbose logging enabled.")

    if not urls:
        log.warning("No URLs provided to check.")
        click.echo("Usage: check-urls <URL1> <URL2> ...")
        return

    log.info(f"Starting check for {len(urls)} URLs.")
    results = check_urls(list(urls), timeout)

    click.echo("\n--- Results ---")
    for url, status in results.items():
        # Use color for better UX
        if "OK" in status:
            click.secho(f"{url:<40} -> {status}", fg="green")
        else:
            click.secho(f"{url:<40} -> {status}", fg="red")
