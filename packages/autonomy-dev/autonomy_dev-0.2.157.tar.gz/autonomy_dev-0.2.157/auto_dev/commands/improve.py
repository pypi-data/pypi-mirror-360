"""Group to implement improvements."""

import os
from pathlib import Path

import rich_click as click

from auto_dev.base import build_cli
from auto_dev.constants import CheckResult
from auto_dev.commands.repo import TEMPLATES, RepoScaffolder


cli = build_cli()


@cli.command()
@click.option(
    "-p",
    "--path",
    help="Path to repo to verify format. Default is current directory.",
    type=click.Path(exists=True, file_okay=True, dir_okay=True),
    default=None,
)
@click.option(
    "-t",
    "--type-of-repo",
    help="Type of repo to scaffold",
    type=click.Choice(TEMPLATES),
    required=True,
    default="autonomy",
)
@click.option(
    "--author",
    help="Author of the repo",
    type=str,
    required=True,
)
@click.option(
    "--name",
    help="Name of the repo",
    type=str,
    required=True,
)
@click.option(
    "-y",
    "--yes",
    help="Automatically answer yes to all questions.",
    is_flag=True,
)
@click.pass_context
def improve(ctx, path, type_of_repo, author, name, yes) -> None:
    r"""Verify and improve repository structure and files.

    Required Parameters:

        type_of_repo (-t): Type of repository to verify (autonomy, python)

        author (--author): Author of the repository

        name (--name): Name of the repository

    Optional Parameters:

        path (-p): Path to repository to verify. (Default: current directory)

        yes (-y): Auto-confirm all prompts. (Default: False)

    Usage:
        Verify current directory:
            adev improve -t autonomy --author myname --name myrepo

        Verify specific path:
            adev improve -p /path/to/repo -t autonomy --author myname --name myrepo

        Auto-confirm fixes:
            adev improve -t autonomy --author myname --name myrepo -y

    Notes
    -----
        - Verifies repository structure against template
        - Shows detailed verification results
        - Can automatically fix differences if confirmed
        - Reports pass/fail/modified/skipped counts
        - Exits with error if files are modified or verification fails

    """
    if path is None:
        path = Path.cwd()
    os.chdir(path)
    verbose = ctx.obj["VERBOSE"]
    logger = ctx.obj["LOGGER"]
    remote = ctx.obj["REMOTE"]
    logger.info(f"Remote: {remote}")
    scaffolder = RepoScaffolder(
        type_of_repo=type_of_repo,
        logger=logger,
        verbose=verbose,
        render_overrides={"author": author, "project_name": name},
    )
    results = scaffolder.verify(True, yes=yes)
    failed = results.count(CheckResult.FAIL)
    modified = results.count(CheckResult.MODIFIED)
    logger.info(f"""Verification completed with results:
        Pased:    - {results.count(CheckResult.PASS)}
        Failed:   - {failed}
        Modified: - {modified}
        Skipped:  - {results.count(CheckResult.SKIPPED)}
        """)

    if modified:
        msg = f"Verification completed with {modified} modified."
        raise click.ClickException(msg)
    if failed:
        msg = f"Verification failed with {failed} failed."
        raise click.ClickException(msg)
    logger.info("Verification completed successfully. All files are formatted correctly.")
