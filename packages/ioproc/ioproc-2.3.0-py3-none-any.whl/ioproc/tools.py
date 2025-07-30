#!/usr/bin/env python
# -*- coding:utf-8 -*-
import pathlib as pt
import shutil
from functools import wraps

import arrow as ar

from ioproc.actionmanager import getActionManager
from ioproc.datamanager import DataManager
from ioproc.logger import mainlogger as log
from ioproc.exceptions import ActionParamsError


__author__ = ["Benjamin Fuchs", "Judith Vesper", "Kai von Krbek"]
__copyright__ = "Copyright 2020, German Aerospace Center (DLR)"
__credits__ = [
    "Felix Nitsch",
    "Niklas Wulff",
    "Hedda Gardian",
    "Gabriel Pivaro",
    "Kai von Krbek",
]

__license__ = "MIT"
__maintainer__ = "Felix Nitsch"
__email__ = "ioProc@dlr.de"
__status__ = "Production"

IOPROCINSTALLROOT = pt.Path(__file__).resolve().parent


def setupFolderStructure(workflowName="", path=None):
    """
    Set up folder structure, which is required for use of the ioProc workflow manager.
    If path already exists, a warning is raised.
    """
    if workflowName.strip() == "":
        workflowName = "workflow1"

    workflowName = workflowName.replace(" ", "_")

    CWD = pt.Path.cwd() if path is None else pt.Path(path)

    path2actions = pt.Path(CWD, "actions", "general.py")
    path2workflow = pt.Path(CWD, "workflows", workflowName)
    path2userConfig = pt.Path(path2workflow, "user.yaml")

    path2actions.parent.mkdir(parents=True, exist_ok=True)
    path2workflow.mkdir(parents=True, exist_ok=True)

    if path2userConfig.exists():
        log.warning(f"UserConfig already exists at location {path2userConfig}")
    else:
        try:
            with (IOPROCINSTALLROOT / "templatefiles" / "workflow.yaml").open(
                "r"
            ) as ipf:
                src = ipf.readlines()

            in_action_folder_declaration = False
            with path2userConfig.open("w") as opf:
                for iline in src:
                    in_action_folder_declaration = (
                        "action_folder" in iline
                    ) or in_action_folder_declaration
                    if in_action_folder_declaration and ("-" in iline):
                        continue
                    elif iline.strip() == "" and in_action_folder_declaration:
                        in_action_folder_declaration = False
                        opf.write(iline)
                    elif in_action_folder_declaration:
                        opf.write(iline)
                        opf.write('  - "' + path2actions.as_posix() + '"\n')
                    else:
                        opf.write(iline)

        except Exception as e:
            shutil.rmtree(path2userConfig.as_posix())
            raise e

    if path2actions.exists():
        log.warning(f"General.py already exists at location {path2actions.parent}")
    else:
        with (IOPROCINSTALLROOT / "templatefiles" / "general.py").open("r") as ipf:
            src = ipf.read()
        with path2actions.open("w") as opf:
            opf.write(src)

    folderScript = CWD / "create_folder_structure.py"
    if not folderScript.exists():
        with (IOPROCINSTALLROOT / "templatefiles" / "create_folder_structure.py").open(
            "r"
        ) as ipf:
            src = ipf.read()
        with folderScript.open("w") as opf:
            opf.write(src)

    workflowStartScript = path2workflow / "run.py"
    if not workflowStartScript.exists():
        with (IOPROCINSTALLROOT / "templatefiles" / "run.py").open("r") as ipf:
            src = ipf.read()
        with workflowStartScript.open("w") as opf:
            opf.write(src)


class action:
    def __init__(self, project):
        """
        decorator to register actions in the ActionManager and validate input
        :param project: name of project
        """
        self.projectName = project

    def __call__(self, f):
        actionMgr = getActionManager()

        @wraps(f)
        def __actionwrapper__(dmgr, config, params):
            log.debug("calling wrapper")

            if type(dmgr) != DataManager:
                raise TypeError("no valid dataManager instance passed")

            start = ar.now()

            try:
                ret = f(dmgr, config, params)
            except Exception as e:
                log.exception(
                    f'Error occured calling action "{self.projectName}-{f.__name__}"'
                )
                raise e

            end = ar.now()
            log.info(f"duration '{self.projectName}.{f.__name__}': {end - start}")
            return ret

        actionMgr[self.projectName, f.__name__] = __actionwrapper__

        log.debug("wrapping complete for action: " + str(__actionwrapper__.__name__))
        return __actionwrapper__


class ActionArgs(dict):
    def __init__(self, *args, **kwargs):
        self.parents = kwargs.pop("parents", ())
        if len(self.parents) == 0:
            self.parents = ""
        else:
            self.parents = "under section [" + "][".join(self.parents) + "] "

        super().__init__(*args, **kwargs)

    def __getitem__(self, key):
        if key in self:
            return super().__getitem__(key)

        message = "Parameter '{}' is not a valid action input. Possible action input parameter/s {}is/are {}. Please check the user.yaml.".format(
            key, self.parents, list(self.keys())
        )
        raise ActionParamsError(message)

    def __setitem__(self, key, value):
        raise TypeError("Action arguments are read only.")


def freeze(d, parents=None):
    """
    This function converts a given dictionary in a read-only mapping, also called frozen-dictionary.
    :return a frozen dictionary where a key cannot be added nor removed
    """
    if parents is None:
        parents = tuple()

    for key, value in d.items():
        if (
            not hasattr(value, "lstrip")
            and not hasattr(value, "items")
            and hasattr(value, "__iter__")
        ):
            d[key] = tuple(value)
        elif hasattr(value, "items"):
            new_parents = list(parents)
            new_parents.append(key)
            new_parents = tuple(new_parents)
            d[key] = freeze(value, new_parents)
    return ActionArgs(d, parents=parents)
