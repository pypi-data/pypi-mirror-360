import os

from packaging import version


version_path = os.path.join(os.path.dirname(__file__), "VERSION")

if not os.path.isfile(version_path):
    version_line = "0.0.0+unknown"
else:
    with open(version_path, "r") as f:
        version_line = f.read().strip()

__version__ = version.parse(version_line)
