import os


def get() -> str:
    """Identify version number"""
    parent_dir = os.path.dirname(__file__)
    version_file = os.path.join(parent_dir, "VERSION.txt")
    assert os.path.isfile(version_file)
    with open(version_file) as fh:
        version = fh.read().strip()

    version_parts = version[1:].split(".")
    valid_version = (
        len(version) >= 5
        and version[0] == "v"
        and len(version_parts) >= 3
        and version_parts[0].isdigit()
        and version_parts[1].isdigit()
        and version_parts[2].isdigit()
    )
    assert valid_version

    return version.strip("v")
