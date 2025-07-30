#!/usr/bin/env python
# -*- coding:utf-8 -*-
from typing import Union
import os
import pathlib as pt

import arrow as ar
import click

from ioproc.actionmanager import getActionManager
from ioproc.config import configProvider
from ioproc.datamanager import DataManager
from ioproc.defaults import defaultConfigContent
from ioproc.exceptions import (
    CheckPointError,
    UnknownAction,
    UnknownActionModule,
    MissingCheckpointFileError,
)
from ioproc.logger import datalogger as dlog
from ioproc.logger import mainlogger as log
from ioproc.tools import freeze, setupFolderStructure
from ioproc.meta import JSONBasedMetaData, MetaDataManager
from ioproc.appconfig import AppConfig


IOPROVENANCE_INSTALLED = True

try:
    import ioprocmeta
except ImportError:
    IOPROVENANCE_INSTALLED = False

__author__ = ["Benjamin Fuchs", "Judith Vesper", "Felix Nitsch"]
__copyright__ = "Copyright 2020, German Aerospace Center (DLR)"
__credits__ = ["Niklas Wulff", "Hedda Gardian", "Gabriel Pivaro", "Kai von Krbek"]

__license__ = "MIT"
__maintainer__ = "Felix Nitsch"
__email__ = "ioProc@dlr.de"
__status__ = "Production"


IOPROCINSTALLROOT = pt.Path(__file__).resolve().parent
SCHEMAPATH = pt.Path(IOPROCINSTALLROOT, "schema")
HOME = pt.Path.home()

defaultConfigContent = defaultConfigContent.format(IOPROCINSTALLROOT.as_posix())


@click.group()
@click.pass_context
def ioproc(ctx):
    ctx.ensure_object(dict)


@ioproc.command(help="setup default folder structure")
@click.option("--workflowname", default="workflow1", help="name of your workflow")
@click.option(
    "--path",
    "-p",
    default=None,
    help="path to folder where to create the default structure. By default this is the current directory ioProc is executed in.",
)
def setupfolders(workflowname, path):
    setupFolderStructure(workflowname, path)


@ioproc.command(
    help="start the configuration wizard to create an ioproc configuration in your user space."
)
def appwizard():
    AppConfig.wizard()


@ioproc.command(
    help="create all necessary files for workflow in current folder or at userconfig location"
)
@click.option(
    "--path", "-p", default=None, help="path to folder where to create workflow"
)
def setupworkflow(path):
    path = pt.Path.cwd() if path is None else pt.Path(path)
    if not path.exists():
        raise IOError(f"workflow folder not found: {path.as_posix()}")

    with (IOPROCINSTALLROOT / "templatefiles" / "workflow.yaml").open("r") as ipf:
        src = ipf.read()

    p = path / "user.yaml"
    if not p.exists():
        with p.open("w") as opf:
            opf.write(src)

    with (IOPROCINSTALLROOT / "templatefiles" / "run.py").open("r") as ipf:
        src = ipf.read()

    p = path / "run.py"
    if not p.exists():
        with p.open("w") as opf:
            opf.write(src)


@ioproc.command(
    help="recreate the general.py action file in the current work directory. Overwrite without prompting."
)
@click.option(
    "--path", "-p", default=None, help="path to folder where to create general.py"
)
def recreate_default_actions(path):

    path = pt.Path.cwd() / "general.py" if path is None else pt.Path(path)

    if path.exists():
        click.confirm(
            "There is already an general.py file existing. Do you want to overwrite and continue?",
            abort=True,
        )

    with (IOPROCINSTALLROOT / "templatefiles" / "general.py").open("r") as ipf:
        src = ipf.read()

    with (path).open("w") as opf:
        opf.write(src)


@ioproc.command(
    help="recreate the noioproc.py file in the current work directory. Overwrite without prompting."
)
@click.option(
    "--path", "-p", default=None, help="path to folder where to create noioproc.py"
)
def create_noioproc(path):

    path = pt.Path.cwd() / "noioproc.py" if path is None else pt.Path(path)

    if path.exists():
        click.confirm(
            "There is already an noioproc.py file existing. Do you want to overwrite and continue?",
            abort=True,
        )

    with (IOPROCINSTALLROOT / "templatefiles" / "noioproc.py").open("r") as ipf:
        src = ipf.read()

    with (path).open("w") as opf:
        opf.write(src)


@ioproc.command(
    help="Display the code snipped that needs to be added to ioproc action files to make them useable without ioproc. Requires the noioproc.py file."
)
def show_noioproc():
    log.info("add this to your actions file:")
    print(
        "# this is a safe guard to make the below actions useable without an ioproc installation."
    )
    print("try:")
    print("    from ioproc.tools import action")
    print("    from ioproc.logger import mainlogger")
    print("except ImportError:")
    print("    from noioproc import action, overwrite, mainlogger")
    print(
        "    print('ioproc is not installed and the integration into ioproc workflows is disabled.')"
    )


@ioproc.command(help="create an empty user.yaml file")
@click.option(
    "--path", "-p", default=None, help="path to folder where to create the user.yaml"
)
def create_workflow_file(path):

    with (IOPROCINSTALLROOT / "templatefiles" / "workflow.yaml").open("r") as ipf:
        src = ipf.read()

    if path is not None:

        path = pt.Path(path)

        if path.exists():
            click.confirm(
                "There is already an user.yaml file existing. Do you want to overwrite and continue?",
                abort=True,
            )

        with (path / "user.yaml").open("w") as opf:
            opf.write(src)

        log.info(f'"user.yaml" was written to "{path.as_posix()}"')
    else:
        log.info("user.yaml default structure:")
        for iline in src.split("\n"):
            print(iline)


@ioproc.command(
    help="list all actions known to this ioproc workflow or display the details for a specific action in a given project. For details specify the requested action as project.action e.g. general.readExcel"
)
@click.option(
    "--useryaml",
    "-u",
    default=None,
    help="path to user.yaml, defaults to './user.yaml'",
)
@click.argument("details", nargs=-1)
def actions(useryaml, details):
    userConfigPath = pt.Path(pt.Path.cwd(), "user.yaml")

    if useryaml is not None:
        userConfigPath = pt.Path(useryaml)

    old_pwd = pt.Path.cwd()

    os.chdir(userConfigPath.parent.as_posix())
    userConfigPath = userConfigPath.relative_to(userConfigPath.parent)

    configProvider.setPathes(
        userConfigPath=userConfigPath,
    )

    config = configProvider.get({})

    update_log_level(config, log, dlog)

    actionMgr = getActionManager(config)

    if len(details) > 0:
        for i in details:
            d = i.split(".")
            if len(d) > 2:
                log.error(
                    f'the requested action "{i}" is not in the correct format. See help for details.'
                )
                return
            project, action_name = d
            if project not in actionMgr:
                log.error(
                    f'the requested project "{project}" is not available to ioproc. Known projects are: {", ".join(actionMgr.keys())}.'
                )
                return
            if action_name not in actionMgr[project]:
                log.error(
                    f'the requested action "{action_name}" is not available to ioproc. Known actions in project "{project}" are: {", ".join(actionMgr[project].keys())}.'
                )
                return
            act = actionMgr[project][action_name]
            log.info(f'doc string for action "{project}.{action_name}":')
            log.info(act.__doc__)
        return

    try:
        log.info("actions known to this workflow:")
        log.info("paths in which ioproc looks for actions:")
        for ipath in config["user"]["action_folder"]:
            log.info(
                f'  - {ipath} :: {"valid" if pt.Path(ipath).exists() else "invalid"}'
            )
        log.info("-------------------------------")
        if len(actionMgr) == 0:
            log.info("no actions found")
        else:
            for k, v in actionMgr.items():
                log.info(f"  {k}:")
                for i in v.keys():
                    log.info(f"     {i}")
    finally:
        os.chdir(old_pwd.as_posix())


def format_override(ctx, self, s):
    try:
        d = tuple(i.strip().split("=") for i in s)
        d = dict(d)
    except Exception as e:
        raise click.exceptions.BadArgumentUsage(
            "the overwrites need to be of shape: ioproc overwrites a=1 b=2"
        ) from e

    return d


@ioproc.command(
    help="list all actions known to this ioproc workflow or display the details for a specific action in a given project. For details specify the requested action as project.action e.g. general.readExcel"
)
@click.option(
    "--useryaml",
    "-u",
    default=None,
    help="path to user.yaml, defaults to './user.yaml'",
)
@click.argument("details", nargs=-1)
def check(useryaml, details):
    userConfigPath = pt.Path(pt.Path.cwd(), "user.yaml")

    if useryaml is not None:
        userConfigPath = pt.Path(useryaml)

    old_pwd = pt.Path.cwd()

    os.chdir(userConfigPath.parent.as_posix())
    userConfigPath = userConfigPath.relative_to(userConfigPath.parent)

    configProvider.setPathes(
        userConfigPath=userConfigPath,
    )

    config = configProvider.get({})

    update_log_level(config, log, dlog)

    actionMgr = getActionManager(config)

    if len(details) > 0:
        for i in details:
            d = i.split(".")
            if len(d) > 2 or len(d) == 1:
                log.error(
                    f'the requested action "{i}" is not in the correct format. See help for details.'
                )
                return
            project, action_name = d
            if project not in actionMgr:
                log.error(
                    f'the requested project "{project}" is not available to ioproc. Known projects are: {", ".join(actionMgr.keys())}.'
                )
                return
            if action_name not in actionMgr[project]:
                log.error(
                    f'the requested action "{action_name}" is not available to ioproc. Known actions in project "{project}" are: {", ".join(actionMgr[project].keys())}.'
                )
                return
            act = actionMgr[project][action_name]
            from ioproc.qualitychecks import check_action

            ret = check_action(act)
        return

    try:
        log.info("actions known to this workflow:")
        log.info("paths in which ioproc looks for actions:")
        for ipath in config["user"]["action_folder"]:
            log.info(
                f'  - {ipath} :: {"valid" if pt.Path(ipath).exists() else "invalid"}'
            )
        log.info("-------------------------------")
        if len(actionMgr) == 0:
            log.info("no actions found")
        else:
            for k, v in actionMgr.items():
                log.info(f"  {k}:")
                for i in v.keys():
                    log.info(f"     {i}")
    finally:
        os.chdir(old_pwd.as_posix())


@ioproc.command(help="execute ioproc workflow defined by user.yaml in current folder")
@click.option("--useryaml", "-u", default=None, help="path to user.yaml")
@click.option(
    "--override/--no-override",
    "-o",
    default=False,
    help="override values of the user.yaml (based on jinja2 syntax)",
)
@click.option(
    "--metaformat",
    "-m",
    default=None,
    help="the metadata format that should be used during the workflow. Requires ioprovenance to be installed. Extended support for metadata formats are currently available for: [ oep150, ]",
)
@click.argument("overridedata", nargs=-1, callback=format_override)
def execute(useryaml, metaformat, override, overridedata):

    if override and not overridedata:
        raise click.exceptions.ClickException("Missing override data")
    elif not override and overridedata:
        raise click.exceptions.ClickException(
            "overrides need to be specified with ioproc execute -o"
        )

    _execute(
        useryaml, metaformat=metaformat, overridedata=overridedata, return_data=False
    )


def _execute(
    path_to_user_yaml: pt.Path,
    metaformat: Union[str, None] = None,
    overridedata: Union[dict, None] = None,
    return_data: bool = False,
) -> Union[dict, None]:
    start = ar.now()

    if overridedata is None:
        overridedata = {}

    userConfigPath = pt.Path(pt.Path.cwd(), "user.yaml")

    if path_to_user_yaml is not None:
        userConfigPath = pt.Path(path_to_user_yaml)

    old_pwd = pt.Path.cwd()

    os.chdir(userConfigPath.parent.as_posix())
    userConfigPath = userConfigPath.relative_to(userConfigPath.parent)

    try:
        data = _execute_workflow(
            userConfigPath, metaformat, overridedata, return_data, log, dlog
        )
    finally:
        os.chdir(old_pwd.as_posix())
        log.info(
            "total duration of workflow: {}".format(
                start.humanize(
                    granularity=["hour", "minute", "second"], only_distance=True
                )
            )
        )

    if return_data:
        return data


def _execute_workflow(userConfigPath, metaformat, overridedata, return_data, log, dlog):

    configProvider.setPathes(userConfigPath=userConfigPath)

    config = configProvider.get(overridedata)

    update_log_level(config, log, dlog)

    log.setupDefaultFileHandlers("./main.log")
    dlog.setupDefaultFileHandlers("./datatrace.log")
    log.setupDefaultFormat()
    dlog.setupDefaultFormat()

    config["meta"] = MetaDataManager()  # create_metadata_store('input')

    if "metadata_files" in config["user"]:
        for itag, imeta in config["user"]["metadata_files"].items():
            if imeta["flavor"] == "generic_json":
                m = JSONBasedMetaData(pt.Path(imeta["path"]))
            elif (
                IOPROVENANCE_INSTALLED
                and imeta["flavor"] in ioprocmeta.available_standard_formats
            ):
                m = ioprocmeta.available_standard_formats[imeta["flavor"]].read_json(
                    pt.Path(imeta["path"])
                )
            else:
                print(ioprocmeta.available_standard_formats)
                raise IOError(
                    f'metadata file "{imeta["path"]}" is of unknown format "{imeta["flavor"]}"'
                )
            config["meta"]["input"][itag] = m

    config["appconfig"] = AppConfig.from_disk()

    log, dlog = _setup_workflow_logger(config)

    actionMgr = getActionManager(config)
    assert (
        len(actionMgr) > 0
    ), "ActionManager is not defined. Ensure 'actionFolder' path in 'user.yaml' is set correctly."
    dmgr = DataManager(config["user"]["debug"]["enable_development_mode"])

    log.info("starting workflow")

    log.debug("commencing action calling")

    FROM_CHECK_POINT = config["user"]["from_check_point"] != "start"
    IGNORE_CHECK_POINTS = False
    if "ignore_check_points" in config["user"]:
        IGNORE_CHECK_POINTS = config["user"]["ignore_check_points"]

    if IGNORE_CHECK_POINTS:
        FROM_CHECK_POINT = False

    _validate_workflow_actions(config, actionMgr)

    CHECK_POINT_DEFINED_IN_WORKFLOW = False

    if FROM_CHECK_POINT:
        _check_for_checkpoint_data(config)

    for iActionInfo in config["user"]["workflow"]:
        iActionInfo = iActionInfo[list(iActionInfo.keys())[0]]
        if FROM_CHECK_POINT:
            if (
                "tag" in iActionInfo
                and iActionInfo["tag"] == config["user"]["from_check_point"]
            ):
                FROM_CHECK_POINT = False
                CHECK_POINT_DEFINED_IN_WORKFLOW = True
                dmgr.fromCache(config["user"]["from_check_point"], iActionInfo)
                log.info(
                    f'reading from cache for tag "{config["user"]["from_check_point"]}"'
                )
            continue
        log.debug('executing action "' + iActionInfo["call"] + '"')
        dmgr.entersAction(iActionInfo)

        if IGNORE_CHECK_POINTS and iActionInfo["call"] == "checkpoint":
            log.warning(
                f'skipping checkpoint "{iActionInfo["tag"]}" due to "ignore check points" option set to true'
            )
            continue

        try:
            actionMgr[iActionInfo["project"]][iActionInfo["call"]](
                dmgr, config, freeze(iActionInfo)
            )
        except Exception as e:
            log.exception(
                'Fatal error during execution of action "'
                + iActionInfo["call"]
                + '":\nData manager log:\n'
                + dmgr.report()
            )
            raise e
        dmgr.leavesAction()

    if not CHECK_POINT_DEFINED_IN_WORKFLOW and FROM_CHECK_POINT:
        raise CheckPointError(
            f'The requested checkpoint "{config["user"]["from_check_point"]}" '
            f"is not defined in the workflow!"
        )

    if return_data:
        return dmgr.export_to_dict()


def _check_for_checkpoint_data(config):
    given_tag = config["user"]["from_check_point"]
    if not pt.Path(f"./.checkpoint_data/Cache_{given_tag}.h5f").is_file():
        message = (
            f"cannot find cache file with given tag name '{given_tag}' "
            f" in './.checkpoint_data/Cache_{given_tag}.h5f'"
        )
        log.exception(message)
        raise MissingCheckpointFileError(message)


def _setup_workflow_logger(config):
    if "debug" in config["user"] and "log_level" in config["user"]["debug"]:
        log.setLevel(config["user"]["debug"]["log_level"])
        dlog.setLevel(config["user"]["debug"]["log_level"])
    else:
        log.setLevel("INFO")
        dlog.setLevel("INFO")
    return log, dlog


def _validate_workflow_actions(config, actionMgr):
    # this is a cross check loop to identify early problems in the workflow.
    for iActionInfo in config["user"]["workflow"]:
        iActionInfo = iActionInfo[list(iActionInfo.keys())[0]]
        if iActionInfo["project"] not in actionMgr:
            raise UnknownActionModule(
                f'The action module "{iActionInfo["project"]}" is not known to ioproc.\n'
                f'please check in the action folder for it: "{config["user"]["action_folder"]}"'
            )

        if iActionInfo["call"] not in actionMgr[iActionInfo["project"]]:
            raise UnknownAction(
                f'The action "{iActionInfo["call"]}" is not known to ioproc.\n'
                f'please check in the action folder "{config["user"]["action_folder"]}"\n'
                f'in the module {iActionInfo["project"]} for the action.'
            )


def update_log_level(config, log, dlog):
    if "debug" in config["user"] and "log_level" in config["user"]["debug"]:
        log.debug(f'setting log level to: {config["user"]["debug"]["log_level"]}')
        log.setLevel(config["user"]["debug"]["log_level"])
        dlog.setLevel(config["user"]["debug"]["log_level"])


if __name__ == "__main__":
    ioproc()
