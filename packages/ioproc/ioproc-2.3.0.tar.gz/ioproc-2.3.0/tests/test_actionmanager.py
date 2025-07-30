#-*- coding:utf-8 -*-

import pytest

import pathlib as pt
import os

from ioproc import actionmanager
from ioproc.config import configProvider

__author__ = ["Benjamin Fuchs", "Felix Nitsch"]
__copyright__ = "Copyright 2020, German Aerospace Center (DLR)"
__credits__ = []

__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Felix Nitsch"
__email__ = "ioProc@dlr.de"
__status__ = "Production"


def test_actionManager_instantiation(test_file_path):
    path = test_file_path / 'valid_project'
    os.chdir(path.as_posix())
    configProvider.setPathes(userConfigPath='user.yaml')
    config = configProvider.get()
    a = actionmanager.getActionManager(config)
    assert isinstance(a, actionmanager.ActionManager)

    assert 'general' in a
    assert 'print_data' in a['general']
    assert 'checkpoint' in a['general']
    assert 'parse_excel' in a['general']
    assert 'execute' in a['general']

    assert len(a['general']) == 4


def test_actionManager_declared():
    assert hasattr(actionmanager, "ActionManager"), "module does not have class ActionManager"


def test_configurationError_exists():
    assert hasattr(actionmanager, "ActionError"), "module does not have an ActionError"
