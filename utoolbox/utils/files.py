import os
import re
import logging
logger = logging.getLogger(__name__)

from PyQt5 import QtWidgets

class ExtensionFilter(object):
    def __init__(self, extensions):
        if isinstance(extensions, list):
            self._extensions = [e.lower() for e in extensions]
            self._judge = lambda x: all([x == e for e in self._extensions])
        else:
            self._extensions = extensions.lower()
            self._judge = lambda x: x == self._extensions

    def __call__(self, name):
        _, name = os.path.splitext(name)
        return self._judge(name[1:])

class SPIMFilter(object):
    FORMAT = '.*_ch{0}_stack\d+_.*_\d+msec_.*'
    def __init__(self, channel=None):
        if not channel:
            channel = '\d+'
        self._program = re.compile(SPIMFilter.FORMAT.format(channel))

    def __call__(self, name):
        return self._program.match(name) is not None

def list_files(root, name_filters=None):
    """List valid files under specific folder by filter conditions.

    Parameters
    ----------
    root : str
        Relative or absolute path that will be the root directory.
    filter : (optional) list of filters
        Filtering conditions.
    """
    file_list = []
    for name in os.listdir(root):
        if not name_filters or all([f(name) for f in name_filters]):
            file_list.append(os.path.join(root, name))
    logger.info("{} data found under \"{}\"".format(len(file_list), root))
    return file_list

def get_local_directory(root='.', prompt="Select a directory..."):
    return QtWidgets.QFileDialog.getExistingDirectory(None, prompt, root)
