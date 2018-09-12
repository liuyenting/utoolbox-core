import abc
from collections import OrderedDict
import logging
import re

logger = logging.getLogger(__name__)

class AttrDict(OrderedDict):
    """
    Metadata provides the means to get and set keys as attributes while behaves
    as much as possible as a normal dict. Keys that are not valid identifiers or
    names of keywords cannot be used as attributes.

    Reference
    ---------
    imageio.core.util.Dict
    """
    __reserved_names__ = dir(OrderedDict())
    __pure_names__ = dir(dict())

    def __getattribute__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            if key in self:
                return self[key]
            else:
                raise

    def __setattr__(self, key, val):
        if key in AttrDict.__reserved_names__:
            if key not in AttrDict.__pure_names__:
                return OrderedDict.__setattr__(self, key, val)
            else:
                raise AttributeError(
                    "reserved name can only be set via dictionary interface" \
                    .format(key)
                )
        else:
            self[key] = val

    def __dir__(self):
        is_identifier = lambda x: bool(re.match(r'[a-z_]\w*$', x, re.I))
        names = [
            k for k in self.keys() if isinstance(k, str) and is_identifier(k)
        ]
        return AttrDict.__reserved_names__ + names
