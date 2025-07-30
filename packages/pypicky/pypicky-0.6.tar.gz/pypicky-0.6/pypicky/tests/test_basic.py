import os
import sys
import time
import contextlib
import subprocess


@contextlib.contextmanager
def timemachine(date, port=8100):

    with open("requirements.txt", "w") as f:
        f.write("numpy==2.2.6\n")

    process = subprocess.Popen(["pypicky", "requirements.txt", "--port", str(port)])

    try:
        time.sleep(2)
        yield
    finally:
        process.terminate()
        process.wait()


def test_basic(tmpdir):
    subprocess.check_output([sys.executable, "-m", "venv", tmpdir])
    python_executable = os.path.join(
        tmpdir,
        "Scripts" if os.name == "nt" else "bin",
        "python",
    )
    with timemachine("2024-12-03T22:12:33"):
        subprocess.check_output(
            [
                python_executable,
                "-m",
                "pip",
                "install",
                "-i",
                "http://localhost:8100",
                "astropy",
            ]
        )
    freeze_output = subprocess.check_output([python_executable, "-m", "pip", "freeze"])
    assert "numpy==2.2.6" in freeze_output.decode("utf-8").strip().splitlines()
