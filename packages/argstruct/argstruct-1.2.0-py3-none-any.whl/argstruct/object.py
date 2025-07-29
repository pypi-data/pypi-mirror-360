# Copyright 2023-2025 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Reusable Argument Structure,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import logging
import typing
import json
import re
from pathlib import Path

from deepmerge.merger import Merger

from atckit.utilfuncs import UtilFuncs
from specker.loader import SpecLoader

parser_T:typing.Union[typing.Type,typing.Union[typing.Any,typing.Any]]
try:
    import argparser_ng
    parser_T = typing.Union[argparser_ng.ArgumentParserCommand,argparser_ng.ArgumentParserGroup]
    from argstruct.argparser_ng_object import _build_console_arg as build_console_arg
except ModuleNotFoundError:
    import argparse
    parser_T = argparse.ArgumentParser
    from argstruct.argparse_object import _build_console_arg as build_console_arg

### To be removed in the future, Used here until Specker has its own static definition
try:
    # pylint: disable=ungrouped-imports
    from specker.static import StaticSpecker
    # pylint: enable=ungrouped-imports
except (ModuleNotFoundError,NameError):
    class StaticSpecker: # type: ignore[no-redef]
        """Static Specker Instance for Performance
        """
        _specker:SpecLoader
        instance:"StaticSpecker"

        @property
        def specker_instance(self) -> SpecLoader:
            """Specker Instance
            @retval SpecLoader Specker Instance
            """
            return self._specker

        def __init__(self) -> None:
            StaticSpecker.instance = self
            self._specker = SpecLoader(Path(__file__).resolve().parent.joinpath("specs"),False)

        @staticmethod
        def load_specs(spec_path:Path) -> None:
            """Scan Common Modules for Specs
            @retval None Nothing
            """
            StaticSpecker.instance.specker_instance.load_specs(spec_path)

class ArgStruct:
    """ArgStruct Main Object. Contains all Commands and Arguments from a processed arg file"""
    OVERRIDE_TYPE_TOML:str = "toml"
    OVERRIDE_TYPE_YAML:str = "yaml"
    OVERRIDE_TYPE_JSON:str = "json"
    OVERRIDE_TYPE_AUTO:str = "auto"

    _specker:SpecLoader
    _argmap:dict[str,typing.Any]
    _SPECKER_ROOT:str = "argmap.root"

    _commands_grouped:dict[str,dict[str,"ArgStructCommand"]]
    _commands_all:dict[str,"ArgStructCommand"]
    empty:"ArgStructCommand"

    @property
    def grouped(self) -> dict[str,dict[str,"ArgStructCommand"]]:
        """Commands grouped by the `group` tag
        @retval dict[str,dict[str,ArgStructCommand]] Dictionary of Groups, which contain Commands
        """
        if not hasattr(self,"_commands_grouped"):
            self._build_maps()
        return self._commands_grouped

    @property
    def commands(self) -> dict[str,"ArgStructCommand"]:
        """All Commands in flat dictionary
        @retval dict[str,ArgStructCommand] Dictionary of Commands
        """
        if not hasattr(self,"_commands_all"):
            self._build_maps()
        return self._commands_all

    def __init__(self,argmap:typing.Union[Path,dict[typing.Any,typing.Any]],override_type:str = "auto",additional_argmap_specs:typing.Union[list[Path],None] = None) -> None:
        """ArgStruct Initialize
        @param Union[Path,dict[Any,Any]] \c argmap Path to ArgStruct file, or dictionary containing ArgStruct
        @param str \c override_type File Type override / definition when loading a file with odd file extension
        @param Union[list[Path],None] \c additional_argmap_specs Additional Specker Specs to load for the ArgStruct processing, or items to override from the defaults
        """
        try:
            self._specker = StaticSpecker.instance.specker_instance
        except AttributeError:
            StaticSpecker()
            self._specker = StaticSpecker.instance.specker_instance
        if additional_argmap_specs is not None:
            for p in additional_argmap_specs:
                self._specker.load_specs(p)
        default_config:dict[str,typing.Any] = {}
        default_config = self._specker.defaults(self._SPECKER_ROOT)
        merger:Merger = Merger([
                (list, ["prepend"]),
                (dict, ["merge"]),
            ],
            ["override"],
            ["override_if_not_empty"]
        )
        new_argmap:dict[str,typing.Any] = {}
        if isinstance(argmap,Path):
            new_argmap = UtilFuncs.load_sfile(argmap,override_type)
        else:
            new_argmap = argmap
        merged_map:dict[str,typing.Any] = merger.merge(default_config,new_argmap)
        spec_check:bool = self._specker.compare(self._SPECKER_ROOT,merged_map)
        if not spec_check:
            raise SyntaxError("Config Validation Failed")
        if self.__class__.__qualname__ == "ArgStruct":
            empty_command:dict[str,typing.Any] = {
                "auth_required": False,
                "cli_hidden": True,
                "api_hidden": True,
                "help": "EMPTY",
                "group": "EMPTY",
                "ui_label": "EMPTY"
            }
            ArgStruct.empty = ArgStructCommand(empty_command)
        self._argmap = merged_map

    def _build_maps(self) -> None:
        """Build ArgStructs
        @retval None Nothing
        """
        self._commands_all = {}
        self._commands_grouped = {"Uncategorized": {}}
        for command, cmd_config in self.get("commands").items():
            config:ArgStructCommand = ArgStructCommand(cmd_config)
            cmd_group:str = config.get("group")
            if cmd_group != "":
                if cmd_group not in self._commands_grouped.keys():
                    self._commands_grouped[cmd_group] = {}
                self._commands_grouped[cmd_group][command] = config
            else:
                self._commands_grouped["Uncategorized"][command] = config
            self._commands_all[command] = config

    @staticmethod
    def process_any_arg(any_args:typing.Union[list[str],None]) -> typing.Any:
        """Any Arg processing
        @param Union[list[str],None] \c any_args Argument to process
        @retval dict[str,Any] Processed Arguments, may be empty
        """
        if any_args is not None:
            if isinstance(any_args,list):
                arg_args:dict[str,typing.Any] = {}
                for any_arg in any_args:
                    if re.match(r'^\w+\=',any_arg):
                        arg_parts:list[str] = any_arg.split('=',1)
                        arg_args[arg_parts[0]] = arg_parts[1]
                    else:
                        if any_arg.startswith('{'):
                            arg_args = json.loads(any_arg)
                return arg_args
            logging.debug("Parsing of any_arg when `any_args` is not a list. not parsing; probably already parsed") # type: ignore[unreachable]
            return any_args
        return {}

    @staticmethod
    # pylint: disable=unused-argument
    def build_console_arg(parser:parser_T, arg_name:str, arg_config:dict[str,typing.Any]) -> None: # type: ignore
        """Build a single argument from an argument config block
        @param parser_T \c parser Argument Parser to attach arguments to
        @param str \c arg_name Name of Argument to add
        @param dict[str,Any] \c arg_config Argument Configuration data
        @retval None Nothing
        parser_T may either be Union[argparser_ng.ArgumentParserCommand,argparser_ng.ArgumentParserGroup] or argparse.ArgumentParser, depending on availability
        """
        v:dict[str,typing.Any] = locals()
        build_console_arg(**v)
    # pylint: enable=unused-argument

    @staticmethod
    def validate(spec_name:str,argmap:dict[typing.Any,typing.Any]) -> bool:
        """Explicitly Validate ArgStruct Block
        @param str \c spec_name Name of Spec to use for validation
        @param dict[Any,Any] \c argmap ArgStruct block to Validate
        @retval bool Validation Result
        """
        result:bool = StaticSpecker.instance.specker_instance.compare(spec_name,argmap)
        return result

    def get(self,argmap_name:typing.Union[str,None]) -> typing.Any:
        """Get ArgStruct Value
        @param str \c or \c None \c argmap_name Name of argmap value to get
        @param bool \c processed Whether to process value and return the rendered result (True), or the raw result (False)
        @retval Any ArgStruct value, if it exists
        @throws ValueError Cannot find a key of the requested argmap tree
        @throws IndexError Index in argmap list is out of range
        @throws TypeError Attempting to scan a part of the argmap tree that is not a list or dict
        """
        if argmap_name is None:
            return self._argmap
        argmap_tree:list[str] = argmap_name.split('.')
        current_branch:typing.Union[list,dict[typing.Any,typing.Any],str,int,bool] = self._argmap.copy()
        traversed_tree:list[str] = []
        for i in range(0,len(argmap_tree)):
            tree_part:str = argmap_tree[i]
            if isinstance(current_branch,dict):
                if tree_part not in current_branch.keys():
                    raise ValueError("Cannot Locate branch of argmap",'.'.join(traversed_tree),tree_part)
                current_branch = current_branch[tree_part]
            elif isinstance(current_branch,list):
                branch_idx:int = int(tree_part)
                if branch_idx >= len(current_branch):
                    raise IndexError("Branch of Configuration out of Index Range",'.'.join(traversed_tree),tree_part)
                current_branch = current_branch[branch_idx]
            else:
                if i != len(argmap_tree):
                    raise TypeError("Attempt to traverse argmap tree on non-traversable type",'.'.join(traversed_tree),tree_part,type(current_branch).__name__)
                return current_branch
            traversed_tree.append(tree_part)
        return current_branch

class ArgStructCommand(ArgStruct):
    """ArgStruct Command Block"""
    _SPECKER_ROOT:str = "argmap.command"

class ArgStructArgument(ArgStruct):
    """ArgStruct Argument Block"""
    _SPECKER_ROOT:str = "argmap.command.args"

ArgStructCmdCallback = typing.Callable[[str,ArgStructCommand,typing.Any,typing.Any],typing.Any]
ArgStructArgCallback = typing.Callable[[str,ArgStructCommand,str,dict[str,typing.Any],typing.Any,typing.Any],typing.Any]

#### CHECKSUM bbcb28d228d5ec311eb4a199258575dc2757ca57afc3764f6d0305330415f0ce
