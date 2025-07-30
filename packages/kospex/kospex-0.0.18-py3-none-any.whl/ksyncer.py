import os
import sys
import time
import signal
import subprocess
from pathlib import Path
import click
from loguru import logger

PID_FILE = Path("/tmp/kospex_syncer.pid")

logger.remove()
logger.add("ksyncer.log", serialize=True, backtrace=True, diagnose=True, rotation="1 day", retention="7 days")

@click.group()
def researcher():
    """Run or manage the Kospex researcher daemon."""
    pass

@researcher.command()
@click.option("--interval", default=60, show_default=True, help="Interval in seconds between enrichment runs.")
def start(interval):
    """Start the background researcher daemon."""
    if PID_FILE.exists():
        click.echo("Researcher already running.")
        logger.warning("Kospex Syncer already running")
        sys.exit(1)

    pid = os.fork()
    if pid > 0:
        # Parent: store the child PID and exit
        with open(PID_FILE, "w") as f:
            f.write(str(pid))
        click.echo(f"Researcher started with PID {pid}")
        logger.info(f"Researcher started with PID {pid}", pid=pid)
        sys.exit(0)

    # Child process continues
    os.setsid()  # Start new session
    run_daemon(interval)

@researcher.command()
def stop():
    """Stop the researcher daemon."""
    if not PID_FILE.exists():
        click.echo("Researcher is not running.")
        return

    with open(PID_FILE) as f:
        pid = int(f.read())
    try:
        os.kill(pid, signal.SIGTERM)
        click.echo(f"Researcher process {pid} stopped.")
    except ProcessLookupError:
        click.echo("No such process found.")
    PID_FILE.unlink(missing_ok=True)

@researcher.command()
def status():
    """Show if the researcher daemon is running."""
    if PID_FILE.exists():
        with open(PID_FILE) as f:
            pid = int(f.read())
        try:
            os.kill(pid, 0)
            click.echo(f"Researcher is running with PID {pid}.")
        except ProcessLookupError:
            click.echo("Stale PID file found. Cleaning up.")
            PID_FILE.unlink()
    else:
        click.echo("Researcher is not running.")

def run_daemon(interval):
    """Main loop for enrichment daemon."""
    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(0))

    while True:
        try:
            research_loop()
        except Exception as e:
            # Optional: log exception
            print(f"Error in research loop: {e}")
        time.sleep(interval)

def research_loop():
    """
    Your enrichment logic goes here.
    For example:
    - Check for newly synced entries in DB
    - Query external APIs
    - Update the Kospex DB with new info
    """
    print("Running research task... (stub)")  # Replace with real work

if __name__ == "__main__":
    researcher()
