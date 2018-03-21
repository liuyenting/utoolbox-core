import os
import logging

import numpy as np

import utoolbox.utils.files as fileutils
from utoolbox.container import Volume

#####

handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(levelname).1s %(asctime)s [%(name)s] %(message)s', '%H:%M:%S'
)
handler.setFormatter(formatter)
logging.basicConfig(level=logging.DEBUG, handlers=[handler])
logger = logging.getLogger(__name__)

#####

source_folder = os.path.join(*["data", "RFiSHp2aLFCYC", "decon", "488"])
file_list = fileutils.list_files(
    source_folder,
    name_filters=[
        fileutils.ExtensionFilter('tif'),
        fileutils.SPIMFilter(channel=0)
    ]
)

print("[0] = {}".format(file_list[0]))

#####

raw = Volume(file_list[0], resolution=(0.3, 0.102, 0.102))
print("resolution = {}".format(raw.metadata.resolution))

raw_xy = np.sum(raw, axis=0)
print("resolution = {}".format(raw_xy.metadata.resolution))