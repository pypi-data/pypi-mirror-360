import subprocess
import sys

try:
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "cgcsdk",
        ]
    )
    print("Update successful!")
except subprocess.CalledProcessError:
    print(
        "Update unsuccessful, try again or install update manually with: pip install --upgrade cgcsdk"
    )
