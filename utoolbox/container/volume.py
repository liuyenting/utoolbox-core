import numpy as np

from .registry import BaseContainer

class Volume(BaseContainer, np.ndarray):
    """Container for 3-D volumetric image"""
    def __new__(cls, source, shape=None, dtype=None):
        if source is None:
            # create array of specified size
            if shape is None:
                raise ValueError("Volume size is not specified.")
            return super(Volume, cls).__new__(cls, shape=shape, dtype=dtype)
        else:
            #TODO use utoolbox.io to determine the proper way to open
            import imageio
            array = imageio.volread(source)
            return array.view(cls)

    def __array_finalize__(self, obj):
        """Fill-in default metadata."""
        pass
