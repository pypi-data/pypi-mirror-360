import argparse
import subprocess
import sys
import os
from kuv.ipynb_metadata import read_ipynb_script_metadata


def main():
    parser = argparse.ArgumentParser(description="kuv")
    parser.add_argument(
        "-f", "--connection-file", required=True, help="Path to connection file"
    )
    args = parser.parse_args()

    # Get metadata from notebook
    notebook_path = os.environ.get("JPY_SESSION_NAME", None)
    meta = read_ipynb_script_metadata(notebook_path)

    cmd = [
        "uv",
        "run",
        "--no-project",
        "--isolated",
    ]

    if meta is not None:
        if "requires-python" in meta:
            cmd += ["--python", meta["requires-python"]]
        if "dependencies" in meta:
            for dependency in meta["dependencies"]:
                cmd += ["--with", dependency]

    cmd += [
        "--with",
        "ipykernel",
        "python",
        "-m",
        "ipykernel_launcher",
        "-f",
        args.connection_file,
    ]

    proc = subprocess.Popen(cmd)
    proc.wait()
    sys.exit(proc.returncode)

# This is executable as a module, e.g. python -m kuv.kernel_launcher
if __name__ == '__main__':
    main()