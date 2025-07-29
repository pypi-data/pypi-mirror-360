# Copyright 2023-2025 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Reusable Argument Structure,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import typing
import logging
from pathlib import Path

import argparse

from argstruct.object import ArgStruct, ArgStructArgCallback, ArgStructCmdCallback, ArgStructCommand
from argstruct.documentation import markdown_documentation

def parse(argstruct_obj:ArgStruct,parser_or_args:typing.Union[argparse.ArgumentParser,dict[str,typing.Any]],command_arg_name:str = "command") -> typing.Union[dict[str,typing.Any],None]:
    """Process arguments from either parser or dictionary and return arguments dictionary with defaults
    @param ArgStruct \c argstruct_obj ArgStruct Object
    @param Union[argparse.ArgumentParser,dict[str,Any]] \c parser_or_args Pre-Parsed Arguments as a dictionary, or the main ArgumentParser instance to process arguments on
    @param str \c command_arg_name Name of Argument that indicates the command being run
    @retval dict[str,Any] Readjusted Input args, including defaults, etc
    """
    arguments:dict[str,typing.Any] = {}
    if isinstance(parser_or_args,argparse.ArgumentParser):
        arguments = vars(parser_or_args.parse_args())
    else:
        arguments = parser_or_args
    command:str = arguments[command_arg_name]
    data:dict[str,typing.Any] = {}
    commandStruct:ArgStructCommand = argstruct_obj.commands[command]
    for arg,arg_config in commandStruct.get("args").items():
        if arg not in arguments.keys():
            if "default" in arg_config.keys():
                data[arg] = arg_config["default"]
        else:
            if arg in data.keys():
                if isinstance(data[arg],list):
                    data[arg].append(arguments[arg])
                else:
                    logging.warning(f"Overriding Argument: {arg} as it located twice in the arguments list")
                    data[arg] = arguments[arg]
            else:
                data[arg] = arguments[arg]
        if arg_config["required"] and arg not in data.keys():
            logging.error(f"Missing required argument: '{arg}'")
            return None
        if arg_config["any_arg"]:
            data[arg] = ArgStruct.process_any_arg(data.pop(arg))
            if data[arg] is not None and len(data[arg]) > 0:
                arguments.pop(arg)
    for arg,val in arguments.items():
        if arg not in data.keys():
            data[arg] = val
    return data

def api(argstruct_obj:ArgStruct,command_callback:ArgStructCmdCallback,arg_callback:ArgStructArgCallback,command_options:typing.Any = None,arg_options:typing.Any = None) -> typing.Any:
    """Convert ArgStruct data into some other process via callbacks
    @param ArgStruct \c argstruct_obj ArgStruct Object
    @param ArgStructCmdCallback \c command_callback Method to execute for each Command processed, Arguments: (command,commandStruct,command_options,result), and returns `result` after manipulation
    @param ArgStructArgCallback \c arg_callback Method to execute for each Argument from each Command processed, Arguments (command,commandStruct,argument,argumentStruct,arg_options,result), and returns `result` after manipulation
    @param Any \c command_options Option(s) to pass to the `command_callback`, default `None`
    @param Any \c arg_options Option(s) to pass to the `arg_callback`, default `None`
    @retval Any Any data returned from resulting callback methods
    """
    result:typing.Any = None
    cmd_config:ArgStructCommand
    for command,cmd_config in argstruct_obj.get("commands").items():
        if cmd_config.get("api_hidden"):
            continue
        result = command_callback(command,cmd_config,command_options,result)
        args:dict[str,typing.Any] = cmd_config.get("args")
        for arg,arg_config in args.items():
            result = arg_callback(command,cmd_config,arg,arg_config,arg_options,result)
        if cmd_config.get("auth_required"):
            for arg,arg_config in argstruct_obj.get("auth_args").items():
                result = arg_callback(command,cmd_config,arg,arg_config,arg_options,result)
    return result

def console(argstruct_obj:ArgStruct,parser:argparse.ArgumentParser,enable_subparser:bool = True,subparser_kwargs:typing.Any = None) -> None:
    """Convert ArgStruct data into argparse commands and arguments
    @param ArgStruct \c argstruct_obj ArgStruct Object
    @param Union[argparse._SubParsersAction,argparse.ArgumentParser] \c Upper Level argparse.ArgumentParser, or an existing argparse._SubParsersAction (subparser) to add commands and arguments to
    @retval None Nothing
    """
    subparser:typing.Union[argparse._SubParsersAction,None] = None
    if enable_subparser:
        if subparser_kwargs is not None:
            subparser = parser.add_subparsers(**subparser_kwargs)
        else:
            subparser = parser.add_subparsers()
    for command,cmd_config in argstruct_obj.get("commands").items():
        if cmd_config.get("cli_hidden"):
            continue
        command_parser:argparse.ArgumentParser
        if enable_subparser and subparser is not None:
            command_parser = subparser.add_parser(command,help=cmd_config.get("help"))
        else:
            command_parser = parser
        args:dict[str,typing.Any] = cmd_config.get("args")
        for arg,arg_config in args.items():
            ArgStruct.build_console_arg(command_parser,arg,arg_config)
        if cmd_config.get("auth_required"):
            for arg,arg_config in argstruct_obj.get("auth_args").items():
                ArgStruct.build_console_arg(command_parser,arg,arg_config)

def documentation_bin() -> str:
    """argstruct-doc Entrypoint
    @retval str Processed Documentation
    """
    parser:argparse.ArgumentParser = argparse.ArgumentParser(description="ArgStruct Documentation Generator")
    parser.add_argument("--no-api",dest="enable_api",help="Include commands which are `api_hidden=False`",default=False,action="store_true")
    parser.add_argument("--no-cli",dest="enable_cli",help="Include commands which are `cli_hidden=False`",default=False,action="store_true")
    parser.add_argument("-p","--path",help="Path to ArgStruct Map",required=True)
    args:argparse.Namespace = parser.parse_args()

    input_args:dict[typing.Any,typing.Any] = vars(args)
    argmap_file:Path = Path(input_args["path"]).resolve()
    enable_api:bool = not input_args["enable_api"]
    enable_cli:bool = not input_args["enable_cli"]
    if not argmap_file.is_file():
        argmap_str:str = argmap_file.as_posix()
        raise FileNotFoundError(argmap_str)
    return markdown_documentation(argmap_file,enable_cli,enable_api)

#### CHECKSUM 160eeeadb95cf676d6bf06854375ec008c6d4e5c934c694dd186ec5dc5e3c9f5
