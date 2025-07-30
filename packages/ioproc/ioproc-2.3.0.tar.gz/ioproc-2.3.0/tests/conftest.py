#-*- coding:utf-8 -*-

import pytest

import pathlib as pt


__author__ = ["Benjamin Fuchs", "Jan Buschmann"]
__copyright__ = "Copyright 2020, German Aerospace Center (DLR)"
__credits__ = []

__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Felix Nitsch"
__email__ = "ioProc@dlr.de"
__status__ = "Production"


@pytest.fixture(scope='session', autouse=True)
def test_file_path(request):

    return pt.Path(request.config.rootdir) / 'tests' / 'testfiles' / 'workflows'


@pytest.fixture(scope='session', autouse=True)
def test_root_path(request):

    return pt.Path(request.config.rootdir) / 'tests' / 'testfiles'

# flag to check if pytest is done
# def pytest_configure(config):
#     import sys
#     sys._called_from_test = True
#
#
# def pytest_unconfigure(config):
#     import sys
#     del sys._called_from_test
