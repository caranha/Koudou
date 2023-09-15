import os

from definitions.paths import ROOT_DIR

def fromRoot(path):
    return os.path.join(ROOT_DIR, path)

