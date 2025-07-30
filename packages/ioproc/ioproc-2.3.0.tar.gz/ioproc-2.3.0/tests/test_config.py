#-*- coding:utf-8 -*-

import pytest

from ioproc import config


__author__ = ["Benjamin Fuchs", "Felix Nitsch"]
__copyright__ = "Copyright 2020, German Aerospace Center (DLR)"
__credits__ = []

__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Felix Nitsch"
__email__ = "ioProc@dlr.de"
__status__ = "Production"


def test_configProvider_exists():
    assert hasattr(config, "configProvider"), "module does not have configProvider instance"

def test_ConfigurationError_exists():
    assert hasattr(config, "ConfigurationError"), "module does not have any ConfigurationError"


class TestConvertList:
    def test_ignoresEmptyDict(self):
        a = {}
        res_a = config.convertList(a)
        assert res_a is a

    def test_neutralToEmptyConfigDict(self):
        a = config.ConfigDict()
        res_a = config.convertList(a)
        assert res_a is a

    def test_neutralToDict(self):
        a = {"a": 1, "b": {"c": 3, "d": 4}}
        res_a = config.convertList(a)
        assert res_a["a"] is a["a"]
        assert res_a["b"] is a["b"]
        assert res_a["b"]["c"] is a["b"]["c"]
        assert res_a["b"]["d"] is a["b"]["d"]

    def test_convertsListToConfigList(self):
        a = {"a": [1, 11], "b": {"c": [3, 33], "d": 4}}
        res_a = config.convertList(a)
        assert isinstance(res_a["a"], config.ConfigList)
        assert isinstance(res_a["b"]["c"], config.ConfigList)


class TestConfigDict:
    a = {"a": [1, 11], "b": {"c": [3, 33], "d": 4}}

    def test_getExistingField(self):
        res_a = config.ConfigDict(self.a)
        res_a["a"]

    def test_missingField(self):
        res_a = config.ConfigDict(self.a)
        with pytest.raises(config.ConfigurationError):
            res_a["c"]


class TestConfigList:
    a = [1, 3, 5, 7, 11, 13]

    def test_getExistingField(self):
        res_a = config.ConfigList(self.a)
        res_a[0]

    def test_missingField(self):
        res_a = config.ConfigList(self.a)
        with pytest.raises(config.ConfigurationError):
            res_a[42]


class TestLoadAndValidate:

    def test_emptyConfigYaml(self, test_file_path):
        path = test_file_path / 'empty_config' / 'user.yaml'
        res_dict = config.loadAndValidate(path.as_posix())
        assert isinstance(res_dict, dict)
        assert not res_dict

    def test_loadingSaneConfigYaml(self, test_file_path):

        path = test_file_path / 'valid_project' / 'user.yaml'
        res_dict = config.loadAndValidate(path.as_posix())

        assert isinstance(res_dict, dict)

    def test_loadingInsaneConfigYaml(self, test_file_path):

        path = test_file_path / 'insane_project' / 'user.yaml'

        with pytest.raises(config.ConfigurationError) as e:
            config.loadAndValidate(path.as_posix())

        assert 'unallowed value None' in e.value.args[0]

    def test_loadingInsaneConfigYamlWithAdditions(self, test_file_path):

        path = test_file_path / 'insane_additions_project' / 'user.yaml'

        with pytest.raises(config.ConfigurationError) as e:
            config.loadAndValidate(path.as_posix())

        assert 'unknown field' in e.value.args[0]

    def test_loadingSaneSimpleConfigYaml(self, test_file_path):

        path = test_file_path / 'valid_project' / 'user.yaml'

        res_dict = config.loadAndValidate(path.as_posix())
        assert isinstance(res_dict, dict)

    def test_loadingSaneSuperSimpleConfigYaml(self, test_file_path):

        path = test_file_path / 'valid_simple_project' / 'user.yaml'

        res_dict = config.loadAndValidate(path.as_posix())
        assert isinstance(res_dict, dict)

    def test_loadingInsaneSuperSimpleConfigYaml(self, test_file_path):

        path = test_file_path / 'insane_simple_project' / 'user.yaml'

        with pytest.raises(config.ConfigurationError) as e:
            config.loadAndValidate(path.as_posix())

        assert 'required field' in e.value.args[0]

    def test_loadingSecondInsaneSuperSimpleConfigYaml(self, test_file_path):

        path = test_file_path / 'second_insane_simple_project' / 'user.yaml'

        with pytest.raises(config.ConfigurationError) as e:
            config.loadAndValidate(path.as_posix())

        assert 'null value not allowed' in e.value.args[0]
