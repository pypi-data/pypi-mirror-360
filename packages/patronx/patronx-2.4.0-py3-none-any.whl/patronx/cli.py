import signal
import sys
import time
from datetime import timedelta
from pathlib import Path

import click
import psycopg2

from patronx.logger import get_logger
from patronx.tasks import cleanup_old_backups, run_backup_job

from . import __version__
from .backup import diff_last_backup, run_backup, run_restore
from .config import BackupConfig
from .env import env_file_option
from .service import run_worker_and_scheduler

logger = get_logger(__name__)


@click.group(invoke_without_command=True)
@click.version_option(version=__version__)
@click.pass_context
def main(ctx: click.Context) -> None:
    """Entry point for the :command:`patronx` command."""
    if ctx.invoked_subcommand is None:
        click.echo("PatronX CLI invoked")
        logger.info("CLI invoked")
    else:
        logger.debug("Invoking subcommand: %s", ctx.invoked_subcommand)


@main.command("check-db")
@env_file_option
def check_db() -> None:
    """Check connection to the configured database."""
    cfg = BackupConfig.from_env()
    try:
        conn = psycopg2.connect(
            host=cfg.host,
            port=cfg.port,
            user=cfg.user,
            password=cfg.password,
            dbname=cfg.database,
            connect_timeout=5,
        )
        conn.close()
        click.echo("Database connection successful")
    except Exception as exc:  # pragma: no cover - connection can fail
        raise click.ClickException(f"Database connection failed: {exc}") from exc


@main.command("backup")
@env_file_option
@click.option("--no-progress", is_flag=True, help="Turn off progress bar (useful in CI)")
def backup_cmd(no_progress):
    cfg = BackupConfig.from_env()
    ts = time.strftime("%Y%m%dT%H%M%S")
    suffix = "dump"
    out = Path(f"{cfg.backup_dir}/{cfg.database}_{ts}.{suffix}")
    logger.info("CLI backup requested → %s", out)

    run_backup(
        cfg,
        out,
        show_progress=not no_progress,
    )


@main.command("restore")
@env_file_option
@click.option("--inp", required=True, help="Path of the backup file to restore from")
@click.option("--no-progress", is_flag=True, help="Turn off progress bar (useful in CI)")
def restore_cmd(inp, no_progress):
    cfg = BackupConfig.from_env()
    inp_path = Path(inp)
    logger.info("CLI restore requested from %s", inp_path)
    run_restore(
        cfg,
        inp_path,
        show_progress=not no_progress,
    )


@main.command(name="list")
def list_backups() -> None:
    """List all backups in the configured backup directory."""
    config = BackupConfig.from_env()
    path = Path(config.backup_dir)
    logger.debug("Listing backups in %s", path)

    if not path.exists():
        click.echo(f"Backup directory {path} does not exist")
        return

    # Sort by modification time (newest first)
    backups = sorted(
        (p for p in path.iterdir() if p.is_file()),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    if not backups:
        click.echo("No backups found")
        return

    entries = [
        (
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(b.stat().st_mtime)),
            b.name,
        )
        for b in backups
    ]

    date_width = max(len(r[0]) for r in entries + [("DATE", "NAME")])
    name_width = max(len(r[1]) for r in entries + [("DATE", "NAME")])
    fmt = f"{{:<{date_width}}}  {{:<{name_width}}}"

    click.echo(fmt.format("DATE", "NAME"))
    click.echo("-" * date_width + "  " + "-" * name_width)
    for row in entries:
        click.echo(fmt.format(*row))

@main.command("start")
@env_file_option
def start() -> None:
    """
    Starts the background worker and scheduler, then keeps the process alive.
    """
    def handle_shutdown(signum, frame):
        logger.info("Shutdown signal received (%s). Exiting...", signum)
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    logger.info("Starting worker and scheduler...")
    try:
        run_worker_and_scheduler()
    except Exception:
        logger.exception("Failed to start worker and scheduler.")
        sys.exit(1)

    logger.info("System running. Press Ctrl+C to stop.")
    while True:
        time.sleep(1)


@main.command("enqueue-backup")
@env_file_option
def enqueue_backup():
    """Fire an ad-hoc backup job right now."""
    logger.info("Enqueuing backup job")
    click.echo(run_backup_job.send())


@main.command("enqueue-cleanup")
@env_file_option
def enqueue_cleanup() -> None:
    """Fire an ad-hoc cleanup job right now."""
    logger.info("Enqueuing cleanup job")
    click.echo(cleanup_old_backups.send())
    
    
@main.command("list-schedule")
@env_file_option
def list_schedule() -> None:
    """Display currently configured scheduled jobs."""
    from patronx import schedule

    cfg = BackupConfig.from_env()
    jobs = schedule.init_scheduled_jobs(cfg.backup_cron, cfg.cleanup_cron)
    for job, cron in zip(jobs, [cfg.backup_cron, cfg.cleanup_cron]):
        next_run = job.last_queued + timedelta(seconds=job.interval)
        click.echo(f"{job.actor_name}\t{cron}\tnext: {next_run.isoformat()}")


@main.command("diff")
@env_file_option
def diff_cmd() -> None:
    """Diff the latest backup against the current database."""
    cfg = BackupConfig.from_env()
    try:
        output = diff_last_backup(cfg)
        click.echo(output)
    except FileNotFoundError as exc:  # pragma: no cover - no backups yet
        raise click.ClickException(str(exc)) from exc