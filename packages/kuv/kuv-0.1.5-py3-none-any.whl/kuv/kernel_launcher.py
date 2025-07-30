import argparse
import os
import subprocess
import sys
import tempfile

import uv

from kuv.ipynb_metadata import get_ipynb_script_metadata

ipykernel_launch_script = """
from ipykernel import kernelapp as app
app.launch_new_instance()
"""

def main():
    # Get connection file from arguments
    parser = argparse.ArgumentParser(description="kuv")
    parser.add_argument( "-f", "--connection-file", required=True)
    args = parser.parse_args()

    # Get metadata from notebook
    notebook_path = os.environ.get("JPY_SESSION_NAME", None)
    if notebook_path is None:
        script_metadata = None
    else:
        script_metadata = get_ipynb_script_metadata(notebook_path)

    # uv executable from python package
    uv_executable = uv.find_uv_bin()

    with tempfile.NamedTemporaryFile("w+", suffix=".py") as f:
        # Paste in the metadata block from the notebook
        if script_metadata is not None:
            f.write(script_metadata)

        # The launch script runs ipykernel
        f.write(ipykernel_launch_script)
        f.flush()

        # Now we execute the script using uv to
        # create the virtualenv
        args = [
            uv_executable,
            "run",
            "--no-project",
            "--with",
            "ipykernel",
            f.name,
            "-f",
            args.connection_file,
        ]

        result = subprocess.run(args)

    sys.exit(result.returncode)


# This is executable as a module, e.g. python -m kuv.kernel_launcher
if __name__ == "__main__":
    main()
