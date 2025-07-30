import click
import signal
import subprocess
import sys
from dotenv import load_dotenv
from handy_uti import __version__
from pathlib import Path


def version_callback(ctx: click.Context, param: click.Parameter, value: bool) -> None:
    """Show version and exit."""
    if not value or ctx.resilient_parsing:
        return
    click.echo(f"handy-uti {__version__}")
    ctx.exit()


@click.command()
@click.option(
    "--version",
    is_flag=True,
    callback=version_callback,
    expose_value=False,
    is_eager=True,
    help="Show version and exit.",
)
@click.argument(
    "env_path",
    required=False,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
def main(env_path: Path | None) -> None:
    """Launch Streamlit app with optional .env file path."""
    if env_path:
        load_dotenv(env_path)

    base_dir = Path(__file__).resolve().parent
    main_py = base_dir / "main.py"
    cmd = [sys.executable, "-m", "streamlit", "run", str(main_py)]
    proc = subprocess.Popen(cmd)
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.send_signal(signal.SIGINT)
        proc.wait()
    sys.exit(proc.returncode)
