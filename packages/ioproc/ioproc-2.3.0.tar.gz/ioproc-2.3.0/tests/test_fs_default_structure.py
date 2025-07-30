#-*- coding:utf-8 -*-
import pytest
from ioproc.driver import setupFolderStructure
import os
import pathlib as pt
from ioproc.config import configProvider


__author__ = ["Benjamin Fuchs", "Felix Nitsch"]
__copyright__ = "Copyright 2020, German Aerospace Center (DLR)"
__credits__ = []

__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Felix Nitsch"
__email__ = "ioProc@dlr.de"
__status__ = "Production"

# See issue: #87
# Should we keep this test case and run a cleanup after execution (even if it fails this would be necessary)
# or should we remove the test case?

# def test_structure_generation(test_root_path):
#
#     listOfFSItems = set([i.as_posix() for i in defaultFS.glob('**/*')])
#
#     listOfPathsToTest = [
#         (test_root_path / 'workflows'),
#         (test_root_path / 'actions'),
#         (test_root_path / 'actions' / 'general.py'),
#         (test_root_path / 'workflows' / 'project1'),
#         (test_root_path / 'workflows' / 'project1' / 'user.yaml'),
#         (test_root_path / 'workflows' / 'project1' / 'run.py'),
#         (test_root_path / 'create_folder_structure.py'),
#     ]
#
#     accounted = set()
#
#     configProvider.setPathes('.', '')
#
#     for testPath in listOfFSItems:
#         name = testPath.lower()
#         if 'cache' in name and name.endswith('.h5f'):
#             accounted.add(testPath)
#
#     for testPath in listOfPathsToTest:
#         testPath = testPath.as_posix()
#         assert testPath in listOfFSItems
#         accounted.add(testPath)
#
#     assert len(listOfFSItems.difference(accounted)) == 0, f"unaccounted files: {listOfFSItems}"
