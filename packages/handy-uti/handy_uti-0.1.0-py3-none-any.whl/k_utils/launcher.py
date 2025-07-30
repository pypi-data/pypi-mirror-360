import signal
import subprocess
import sys
from pathlib import Path


def main():
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
