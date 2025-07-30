"""Download commands for EOIR FOIA data."""

from datetime import datetime
from pathlib import Path
from typing import Optional

import click
import structlog

from eoir.core.db import init_download_tracking
from eoir.core.download import check_file_status, download_file, unzip
from eoir.settings import DOWNLOAD_DIR

logger = structlog.get_logger()


@click.group()
def download():
    """Download EOIR FOIA data files."""
    init_download_tracking()


@download.command()
def status():
    """See if new files are available."""
    try:
        current, local, message = check_file_status()
        click.echo(message + "\n")

        click.echo("Online version:")
        click.echo(f"Last modified: {current.last_modified}")
        click.echo(f"Size: {current.content_length:,} bytes")
        if local:
            click.echo("\nLocal Version:")
            click.echo(f"Last modified: {local.last_modified}")
            click.echo(f"Size: {local.content_length:,} bytes")
    except Exception as e:
        logger.error("Check failed", error=str(e))
        raise click.ClickException(str(e))


@download.command()
@click.option(
    "--no-retry",
    is_flag=True,
    default=False,
    help="Disable automatic retry on failure",
)
@click.option(
    "--no-unzip",
    is_flag=True,
    default=False,
    help="Disable automatic unzipping of the file on download success",
)
def fetch(no_retry: bool, no_unzip: bool):
    """Download latest EOIR FOIA data."""
    try:
        current, local, message = check_file_status()

        click.echo(message)
        if current == local:
            return

        with click.progressbar(
            length=current.content_length,
            label="Downloading",
            fill_char="=",
            empty_char="-",
        ) as bar:

            def update_progress(downloaded: int, total: int):
                bar.update(downloaded - bar.pos)

            output_path = DOWNLOAD_DIR / f"FOIA-TRAC-{current.last_modified:%Y%m}.zip"
            download_file(
                output_path=output_path,
                metadata=current,
                max_retries=0 if no_retry else 3,
                progress_callback=update_progress,
            )

        click.echo(f"\nDownload complete: {output_path}")

        if not no_unzip:
            unzip(current)
            click.echo(f"Extracted to downloads folder...")

    except Exception as e:
        logger.error("Download failed", error=str(e))
        raise click.ClickException(str(e))
