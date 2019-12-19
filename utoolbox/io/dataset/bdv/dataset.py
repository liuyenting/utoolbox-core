from functools import reduce
import logging
import operator
import os
from xml.etree.ElementTree import Element, ElementTree, SubElement

import h5py
import numpy as np

from ..base import DenseDataset, MultiChannelDataset, MultiViewDataset, TiledDataset

__all__ = ["BDVDataset"]

logger = logging.getLogger(__name__)


class BigDataViewerXML(object):
    """
    Args:
        path (str): path to the dataset
    """

    class View(object):
        attributes = dict()

        def __init__(
            self, vid, data, name="untitled", voxel_size=(1, 1, 1), **attributes
        ):
            self.vid = vid
            self.shape = data.shape
            self.name = name
            self.voxel_size = voxel_size
            self.attributes = {
                key: BigDataViewerXML.View.archive_attribute(key, value)
                for key, value in attributes.items()
            }

            self.reset_transform()

        def add_transform(self, name, matrix):
            self.transforms.append((name, matrix))

        def reset_transform(self):
            self.transforms = []

            voxel_size = self.voxel_size[::-1]
            # upsample low-res axes
            min_voxel_size = min(voxel_size)
            voxel_size = tuple(s / min_voxel_size for s in voxel_size)

            matrix = np.zeros((3, 4))
            matrix[range(3), range(3)] = voxel_size
            self.add_transform("calibration", matrix)

        def serialize(self):
            # abstract definitions
            setup = Element("ViewSetup")
            SubElement(setup, "id").text = str(self.vid)
            SubElement(setup, "name").text = self.name
            SubElement(setup, "size").text = " ".join(
                str(s) for s in reversed(self.shape)
            )

            # attach attributes
            attributes = SubElement(setup, "attributes")
            for key, index in self.attributes.items():
                SubElement(attributes, key).text = str(index)

            # spatial calibrations
            voxel = SubElement(setup, "voxelSize")
            SubElement(voxel, "unit").text = "micron"
            SubElement(voxel, "size").text = " ".join(
                str(s) for s in reversed(self.voxel_size)
            )

            transforms = Element("ViewRegistration")
            transforms.set("timepoint", str(0))
            transforms.set("setup", str(self.vid))
            for name, matrix in self.transforms:
                transform = SubElement(transforms, "ViewTransform")
                transform.set("type", "affine")
                SubElement(transform, "Name").text = name
                SubElement(transform, "affine").text = " ".join(
                    "{:.4f}".format(v) for v in matrix.ravel()
                )

            return setup, transforms

        ##

        @classmethod
        def archive_attribute(cls, key, value):
            """
            Archive an attribute and returns its respective ID.
            """
            # XML can only accept strings
            value = str(value)
            try:
                attribute = cls.attributes[key]
                try:
                    return attribute.index(value)
                except ValueError:
                    # new value
                    attribute.append(value)
                    return len(attribute) - 1
            except KeyError:
                # new attribute
                cls.attributes[key] = [value]
                return 0

    def __init__(self, h5_path):
        h5_path = os.path.realpath(h5_path)
        self._init_tree(h5_path)

        # XML will place next to the dataset
        fname, _ = os.path.splitext(h5_path)
        self._path = f"{fname}.xml"

        self._views = []

    def add_view(self, channel, data, name="untitled", voxel_size=(1, 1, 1), tile=None):
        """
        Add a new view and return its stored view ID.
        """
        vid = len(self._views)
        tile = vid if tile is None else tile
        view = BigDataViewerXML.View(
            vid, data, name=name, voxel_size=voxel_size, channel=channel, tile=tile
        )
        self._views.append(view)
        return vid

    def serialize(self):
        for view in self._views:
            setup, transforms = view.serialize()
            self._setups.append(setup)
            self._registrations.append(transforms)

        for key, values in BigDataViewerXML.View.attributes.items():
            attribute = SubElement(self._setups, "Attributes")
            attribute.set("name", key)
            for i, value in enumerate(values):
                variants = SubElement(attribute, key.capitalize())
                SubElement(variants, "id").text = str(i)
                SubElement(variants, "name").text = str(value)

        tree = ElementTree(self.root)
        tree.write(self.path)
        logger.info(f'XML saved to "{self.path}"')

    ##

    @property
    def path(self):
        return self._path

    @property
    def root(self):
        return self._root

    @property
    def views(self):
        return self._views

    ##

    def _init_tree(self, h5_path):
        # init XML
        root = Element("SpimData")
        root.set("version", "0.2")

        # using relative path
        base_path = SubElement(root, "BasePath")
        base_path.set("type", "relative")
        base_path.text = "."

        sequence = SubElement(root, "SequenceDescription")

        # a HDF data source
        loader = SubElement(sequence, "ImageLoader")
        loader.set("format", "bdv.hdf5")
        loader_path = SubElement(loader, "hdf5")
        loader_path.set("type", "relative")
        loader_path.text = os.path.basename(h5_path)

        # populate default fields
        setups = SubElement(sequence, "ViewSetups")
        timepoints = SubElement(sequence, "Timepoints")
        timepoints.set("type", "pattern")
        registrations = SubElement(root, "ViewRegistrations")

        # TODO no timeseries
        SubElement(timepoints, "integerpattern").text = str(0)

        # save internal arguments
        self._root = root
        self._setups, self._registrations = setups, registrations


class BDVDataset(DenseDataset, MultiChannelDataset, MultiViewDataset, TiledDataset):
    def __init__(self, root_dir):
        self._root_dir = root_dir

        super().__init__()

        self.preload()

    ##

    @property
    def read_func(self):
        pass

    @property
    def root_dir(self):
        return self._root_dir

    ##

    @staticmethod
    def dump(
        dst_dir,
        dataset,
        pyramid=[(1, 1, 1), (2, 4, 4)],
        chunks=(64, 128, 128),
        compression="gzip",
    ):
        try:
            os.makedirs(dst_dir)
        except FileExistsError:
            logger.warning(f'folder "{dst_dir}" already exists')
        h5_path = os.path.join(dst_dir, f"dataset.h5")

        xml = BigDataViewerXML(h5_path)
        if not isinstance(dataset, DenseDataset):
            raise TypeError("dataset is not a DenseDataset")
        voxel_size = dataset._load_voxel_info()

        # estimate cache size
        chunk_size = (64, 64, 64)
        max_slots = reduce(operator.mul, (1024 // c for c in chunk_size[1:]), 1)
        rdcc_nbytes = reduce(operator.mul, chunk_size, 1) * max_slots * 2
        logger.info(f"cache size: {rdcc_nbytes} bytes")


        for _, row in dataset.inventory.iterrows():
            print(row)
            raise RuntimeError

            
        with h5py.File(
            h5_path, "w", rdcc_nbytes=rdcc_nbytes, rdcc_nslots=max_slots
        ) as h:
            # TODO Why declare this?
            h["__DATA_TYPES__/Enum_Boolean"] = np.dtype("bool")

            for _, row in dataset.inventory.iterrows():
                print(row['c1'], row['c2'])

            for channel, datastore in dataset.items():
                with datastore as source:
                    for i_tile, (key, data) in enumerate(source.items()):
                        ss = xml.add_view(
                            channel, data, name=key, voxel_size=voxel_size, tile=i_tile
                        )
                        logger.info(f".. [{ss}] {key}")
                        #save_to_hdf(h, ss, data, downsamples, chunk_size)
        xml.serialize()

    ##

    def _can_read(self):
        pass

    def _enumerate_files(self):
        pass

    def _load_array_info(self):
        pass

    def _load_channel_info(self):
        pass

    def _retrieve_file_list(self, coord_dict):
        pass

    def _load_metadata(self):
        pass

    def _load_tiling_coordinates(self):
        pass

    def _load_tiling_info(self):
        pass

    def _load_view_info(self):
        pass