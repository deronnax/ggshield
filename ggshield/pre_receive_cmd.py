import sys
import traceback
from typing import List

import click

from ggshield.dev_scan import scan_commit_range
from ggshield.utils import EMPTY_SHA, EMPTY_TREE, SupportedScanMode

from .git_shell import check_git_dir, get_list_commit_SHA


@click.command()
@click.argument("prereceive_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def prereceive_cmd(
    ctx: click.Context, prereceive_args: List[str]
) -> int:  # pragma: no cover
    """
    scan as a pre-push git hook.
    """
    config = ctx.obj["config"]

    oldref, newref, *_ = sys.stdin.read().strip().split()

    if newref == EMPTY_SHA:
        click.echo("Deletion event or nothing to scan.")
        return 0

    if oldref == EMPTY_SHA:
        click.echo(
            f"New tree event. Scanning last {config.max_commits_for_hook} commits."
        )
        before = EMPTY_TREE
        after = newref
        cmd_range = f"--max-count={config.max_commits_for_hook+1} {EMPTY_TREE} {after}"
    else:
        before = oldref
        after = newref
        cmd_range = (
            f"--max-count={config.max_commits_for_hook+1} {before}...{after}"  # noqa
        )

    commit_list = get_list_commit_SHA(cmd_range)

    if not commit_list:
        click.echo(
            "Unable to get commit range.\n"
            f"  before: {before}\n"
            f"  after: {after}\n"
            "Skipping pre-receive hook\n"
        )
        return 0

    if len(commit_list) > config.max_commits_for_hook:
        click.echo(
            f"Too many commits. Scanning last {config.max_commits_for_hook} commits\n"
        )
        commit_list = commit_list[-config.max_commits_for_hook :]

    if config.verbose:
        click.echo(f"Commits to scan: {len(commit_list)}")

    try:
        check_git_dir()
        return_code = scan_commit_range(
            client=ctx.obj["client"],
            cache=ctx.obj["cache"],
            commit_list=commit_list,
            output_handler=ctx.obj["output_handler"],
            verbose=config.verbose,
            filter_set=ctx.obj["filter_set"],
            matches_ignore=config.matches_ignore,
            all_policies=config.all_policies,
            scan_id=" ".join(commit_list),
            mode_header=SupportedScanMode.PRE_RECEIVE.value,
            banlisted_detectors=config.banlisted_detectors,
        )
        if return_code:
            click.echo(
                """Rewrite your git history to delete evidence of your secrets.
Use environment variables to use your secrets instead and store them in a file not tracked by git.

If you don't want to go through this painful git history rewrite in the future,
you can set up ggshield in your pre commit:
https://docs.gitguardian.com/internal-repositories-monitoring/integrations/git_hooks/pre_commit

Use it carefully: if those secrets are false positives and you still want your push to pass, run:
'git push -o breakglass'"""
            )
        return return_code

    except click.exceptions.Abort:
        return 0
    except click.ClickException as exc:
        raise exc
    except Exception as error:
        if config.verbose:
            traceback.print_exc()
        raise click.ClickException(str(error))
