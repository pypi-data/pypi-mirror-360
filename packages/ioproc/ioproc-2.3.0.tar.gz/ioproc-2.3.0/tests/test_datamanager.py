#-*- coding:utf-8 -*-

import pytest
import pandas as pd
import pathlib as pt
import os

import ioproc.datamanager as datamanager
from ioproc.config import configProvider

__author__ = ["Benjamin Fuchs", "Felix Nitsch"]
__copyright__ = "Copyright 2020, German Aerospace Center (DLR)"
__credits__ = []

__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Felix Nitsch"
__email__ = "ioProc@dlr.de"
__status__ = "Production"

@pytest.fixture(scope='module')
def valid_action_config():
    c = {
        "project": "general",
        "call": "parse_excel",
        "data": {
            "read_from_dmgr": None,
            "write_to_dmgr": "parsedData",
        },
        "args": {
            "fileLink": "spreadsheet",
        },
    }

    return c


def test_dataManager_exists():
    assert hasattr(datamanager, 'DataManager'), 'No class DataManager exists'


def test_dataFieldError_exists(valid_action_config):
    d = datamanager.DataManager(run_in_debug_mode=False)
    valid_action_config['data']['read_from_dmgr'] = 'test'
    d.entersAction(valid_action_config)

    with pytest.raises(datamanager.DataFieldError):
        _ = d['test']


def test_DataDict_exists():
    assert hasattr(datamanager, 'DataDict'), 'No class DataDict exists'


def test_DataDict_serialize():
    d = datamanager.DataDict()

    with pytest.raises(datamanager.DataFieldError):
        d['test'] = [1, 2, 3]

    d['test'] = pd.Series([1, 2, 3])

    res = d.dataSerialize('label')
    res = list(res)
    assert len(res) == 1, 'expected exactly one item'

    item = res[0]
    assert len(item) == 2, 'expected two items per key in DataManager returned by serialize'

    parts = item[0].split('/')
    assert len(parts) == 2
    assert parts[0] == 'label'
    assert parts[1] == 'test'
    assert isinstance(item[1], pd.Series)
    assert item[1].iloc[0] == 1
    assert item[1].iloc[1] == 2
    assert item[1].iloc[2] == 3


def test_overwriteFlag(valid_action_config):
    valid_action_config['data']['write_to_dmgr'] = 'test'
    valid_action_config['data']['read_from_dmgr'] = 'test'
    d = datamanager.DataManager(run_in_debug_mode=False)
    d.entersAction(valid_action_config)

    d['test'] = pd.Series([1, 2, 3])

    with pytest.raises(AssertionError):
        d['test'] = pd.Series(['a', 'b', 'c'])

    d['test'].iloc[0] = 10
    assert d['test'].iloc[0] == 10

    with d.overwrite:
        d['test'] = pd.Series(['a', 'b', 'c'])
        assert d._overwriteFlag is True

    assert d._overwriteFlag is False
    assert d['test'].iloc[0] == 'a'


def test_entersActionIsActive(valid_action_config):
    valid_action_config['data']['write_to_dmgr'] = 'test'
    d = datamanager.DataManager(run_in_debug_mode=False)

    assert not d._inAction

    d.entersAction(valid_action_config)
    assert d._inAction

    d.leavesAction()
    assert not d._inAction
    assert len(d._accessLog) == 0


def test_addToAccessLog(valid_action_config):
    valid_action_config['data']['write_to_dmgr'] = 'test'
    valid_action_config['data']['read_from_dmgr'] = 'test'
    d = datamanager.DataManager(run_in_debug_mode=False)
    d.entersAction(valid_action_config)

    d['test'] = pd.Series([1, 2, 3])
    _ = d['test']

    assert len(d._accessLog) == 2
    assert d._accessLog[1] == 'test (r)'

    with d.overwrite:
        d['test'] = pd.Series(['a', 'b'])

    assert d._accessLog[-1] == 'test (w)'

    d.leavesAction()
    assert len(d._accessLog) == 0


def test_validateIfInDmgr(valid_action_config):
    valid_action_config['data']['write_to_dmgr'] = ['test', 'test2']
    valid_action_config['data']['read_from_dmgr'] = None
    d = datamanager.DataManager(run_in_debug_mode=False)
    d.entersAction(valid_action_config)

    d['test'] = pd.Series([1, 2, 3])

    with pytest.raises(datamanager.DataFieldError):
        d.validate(['test', 'test2'])

    d['test2'] = pd.Series(dtype=float)

    d.validate(['test', 'test2'])

    # should not raise an error. Partial required fields are ok
    d.validate(['test',])



def test_writeToDict(valid_action_config):
    d = datamanager.DataManager(run_in_debug_mode=False)
    valid_action_config['data']['write_to_dmgr'] = {'key': 'VALUE'}
    d.entersAction(valid_action_config)

    with d.overwrite:
        d['VALUE'] = pd.Series(['a', 'b', 'c'])
        assert d._overwriteFlag is True

# see issue #87, needs cleanup operation after test case end.
# def test_toCacheWriting():
#     assert pt.Path.cwd() == defaultFS
#
#     d = datamanager.DataManager()
#     d['test'] = pd.Series([1, 2, 3])
#
#     d.toCache('testtag')
#
#     assert (defaultFS/'Cache_testtag.h5f').exists(), list(defaultFS.glob('*'))


# see issue #87, needs cleanup operation after test case end.
# def test_fromCacheReading(defaultFS):
#     assert pt.Path.cwd() == defaultFS
#
#     d = datamanager.DataManager()
#     d['test'] = pd.Series([1, 2, 3])
#
#     d.toCache('testtag')
#
#     del d
#
#     d = datamanager.DataManager()
#
#     assert 'test' not in d
#
#     d.fromCache('testtag')
#
#     assert isinstance(d['test'], pd.Series)
#     assert d['test'].iloc[0] == 1
#     assert d['test'].iloc[1] == 2
#     assert d['test'].iloc[2] == 3

