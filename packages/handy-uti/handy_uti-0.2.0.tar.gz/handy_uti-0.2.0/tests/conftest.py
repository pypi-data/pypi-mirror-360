import pytest
import socket
import sys
import time
from pathlib import Path
from subprocess import Popen

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))


def wait_starting(process: Popen, timeout: int = 30):
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket() as s:
            try:
                s.settimeout(1)
                s.connect(("localhost", 9507))
                break
            except Exception:
                time.sleep(0.5)
    else:
        process.kill()
        pytest.fail("Streamlit app did not start on port 9507 within timeout")


def st_server_process(filename: str, port: int = 9507):
    cmd = (
        f"streamlit run handy_uti/{filename} --server.port {port} --server.headless true"
    )
    process = Popen(cmd.split())
    wait_starting(process)
    return process
