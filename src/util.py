from pathlib import Path


def get_project_root():
    # assumes this file lives in root/src
    return Path(__file__).parent.parent

def path(f):
    return get_project_root() / f