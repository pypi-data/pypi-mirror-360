#-*- coding:utf-8 -*-

import pytest

from ioproc.tools import freeze, ActionArgs
from frozendict import frozendict


__author__ = ["Benjamin Fuchs", "Felix Nitsch"]
__copyright__ = "Copyright 2020, German Aerospace Center (DLR)"
__credits__ = []

__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Felix Nitsch"
__email__ = "ioProc@dlr.de"
__status__ = "Production"


def test_freeze():
    config = {
        'test': {
            'sub1': 'xyz',
            'sub2': [1, 2, 3],
            'sub3': 12
        }
    }

    new = freeze(config)

    assert isinstance(new['test']['sub2'], tuple)
    assert isinstance(new['test'], ActionArgs)

    with pytest.raises(TypeError):
        new['test']['sub3'] = 4
