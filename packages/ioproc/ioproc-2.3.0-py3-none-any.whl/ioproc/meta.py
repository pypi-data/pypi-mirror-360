
from typing import Any
import warnings
import json
import pprint


__author__ = ["Benjamin Fuchs"]
__copyright__ = "Copyright 2022, German Aerospace Center (DLR)"
__credits__ = [
    "Felix Nitsch",
    "Jan Buschmann",
]

__license__ = "MIT"
__maintainer__ = "Benjamin Fuchs"
__email__ = "ioProc@dlr.de"
__status__ = "Production"

HAS_IOPROVENANCE = True
try:
    import ioprovenance
except ImportError:
    HAS_IOPROVENANCE = False

ALLOWED_ATTRS = ['requested_metadata_format', 'error_msg']


class MetaDataManager:
    def __init__(self):
        self.__input = {}
        self.__output = {}

    def __getitem__(self, k):
        assert k in ('input', 'output'), f'Metadata has to be either in "input" or "output" category not in "{k}"'

        if k == 'input':
            return self.__input
        return self.__output
    
    def __repr__(self) -> str:
        ret = '\nMetadata:\n'
        ret += '  Input:\n'
        for k, v in self.__input.items():
            ret += f'    {k}\n'
        ret += '  Output:\n'
        for k, v in self.__output.items():
            ret += f'    {k}\n'
        return ret


def create_metadata_store(*categories):
    '''dynamically creates an instance of MetadataStore with forzen attributes. '''
    attrs = {}
    # attrs['__slots__'] = categories
    t = type("MetadataStore", (), attrs)
    for k in categories:
        setattr(t, k, None)
    return t()



class MissingMetaFormatProxy:
    def __init__(self, requested_metadata_format):
        self.error_msg = []
        if not HAS_IOPROVENANCE:
            self.error_msg.append("ioProvenance is not installed. This library is needed to process meta information. Please install ioprovenance.")
        if requested_metadata_format is not None:
            self.error_msg.append(f'Unknown meta format "{requested_metadata_format}" requested. Please specify a meta data format supported by ioprovenance via the command line parameter "-m".')
        self.error_msg = '\n    '+'\n    Also:\n    '.join(self.error_msg)

    def __setattr__(self, k, v):
        if k in ALLOWED_ATTRS:
            super().__setattr__(k, v)
        else:
            warnings.warn(self.error_msg)
    
    def __getattribute__(self, k):
        if k in ALLOWED_ATTRS:
            return super().__getattribute__(k)

        raise AttributeError(self.error_msg)

    def type(self):
        return 'missing'



class JSONBasedMetaData:
    _freeze = False

    def __init__(self, file_path):
        self.file_path = file_path
        self.rawmeta = json.load(self.file_path.open('r'))
        self._freeze = True
    
    def __getattr__(self, k):
        if k in self.rawmeta:
            return self.rawmeta[k]
        raise AttributeError(f"No attribute '{k}' in {self.__class__.__name__}")
        
    def __setattr__(self, __name: str, __value: Any) -> None:
        if not self.__getattribute__('_freeze'): 
            super().__setattr__(__name, __value)
        else:
            raise AttributeError('meta data are read only!')
        
    def __repr__(self):
        return pprint.pformat(self.rawmeta)