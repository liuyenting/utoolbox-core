# pylint: disable=E1102
from abc import abstractmethod
from collections import OrderedDict
from collections.abc import MutableMapping
from functools import reduce
import logging
import mmap
from operator import mul
import sys

import numpy as np

from .error import (
    ImmutableUriListError,
    ReadOnlyDataError
)

logger = logging.getLogger(__name__)

__all__ = [
    'Datastore',
    'BufferedDatastore'
]

class Datastore(MutableMapping):
    """Basic datastore that includes abstract read logic."""
    def __init__(self, read_func=None, write_func=None, del_func=None,  
                 immutable=False):
        """
        :param func read_func: read operation
        :param func write_func: write operation
        :param func del_func: delete operation
        :param bool immutable: is URI entries modifiable
        """
        self._uri = OrderedDict()
        self._read_func, self._write_func, self._del_func, self._immutable = \
            read_func, write_func, del_func, immutable

    def __delitem__(self, key):
        try:
            uri = self._uri[key]
            self._del_func(uri)
            del self._uri[key]
        except TypeError:
            raise ImmutableUriListError("datastore is immutable")
        except KeyError:
            raise FileNotFoundError("unknown key \"{}\"".format(key))

    def __getitem__(self, key):
        try:
            uri = self._uri[key]
            return self._read_func(uri)
        except TypeError:
            # nop
            return key
        except KeyError:
            raise FileNotFoundError("unknown key \"{}\"".format(key))
    
    def __iter__(self):
        return iter(self._uri)

    def __len__(self):
        return len(self._uri)

    def __setitem__(self, key, value):
        try:
            uri = self._uri[key]
        except TypeError:
            raise ReadOnlyDataError("current dataset is read-only")
        except KeyError:
            if self.immutable:
                raise ImmutableUriListError("datastore is immutable")
            else:
                # create new entry
                uri = self._key_to_uri(key)
                self._uri[key] = uri
        self._write_func(uri, value)

    @property
    def immutable(self):
        return self._immutable
    
    def _key_to_uri(self, key):
        raise ImmutableUriListError("key transform function not defined")

class TransientDatastore(Datastore):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __enter__(self):
        self._allocate_resources()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    
    def close(self):
        self._free_resources()
    
    @abstractmethod
    def _allocate_resources(self):
        pass
    
    @abstractmethod
    def _free_resources(self):
        pass

class BufferedDatastore(TransientDatastore):
    """
    Reading data that requires internal buffer to piece together the fractions before returning it.
    """
    def __init__(self, *args, **kwargs):
        # staging area
        self._mmap, self._buffer = None, None

        super().__init__(*args, **kwargs)

    @abstractmethod
    def _buffer_shape(self):
        """
        Determine shape and type of the internal buffer.
        
        :return: a tuple, (shape, dtype)
        """
        raise NotImplementedError
    
    @abstractmethod
    def _load_to_buffer(self, x):
        """
        Load data definition x into the internal buffer.
        
        :param x: any definition that can be successfully interpreted internally
        """
        raise NotImplementedError

    def _allocate_resources(self):
        shape, dtype = self._buffer_shape()
        nbytes = dtype.itemsize * reduce(mul, shape)
        logger.info(
            "dimension {}, {}, {} bytes".format(shape[::-1], dtype, nbytes)
        )

        self._mmap = mmap.mmap(-1, nbytes)
        self._buffer = np.ndarray(shape, dtype, buffer=self._mmap)

    def _free_resources(self):
        if sys.getrefcount(self._buffer) > 2:
            # getrefcount + self._buffer -> 2 references
            logger.warning("buffer is referenced externally")
        self._buffer = None
        self._mmap.close()

        logger.debug("internal buffer destroyed")
