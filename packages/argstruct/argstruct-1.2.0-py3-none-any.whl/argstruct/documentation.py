# Copyright 2023-2025 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Reusable Argument Structure,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import typing
from pathlib import Path

from tabulate import tabulate

from argstruct.object import ArgStruct, ArgStructArgCallback, ArgStructCmdCallback, ArgStructCommand

def _build_doc_commandmap(
        commandlist:dict[str,ArgStructCommand],
        enable_api:bool,enable_cli:bool,
        additional_columns:typing.Union[list[str],None] = None,
        command_callback:typing.Union[ArgStructCmdCallback,None] = None, command_options:typing.Any = None,
        arg_callback:typing.Union[ArgStructArgCallback,None] = None, arg_options:typing.Any = None
    ) -> str:
    """Build MarkDown Documentation for Each Command in a dictionary of command_name:ArgStructCommand
    @param dict[str,ArgStructCommand] \c commandlist Dictionary of command_name:ArgStructCommand
    @param bool enable_api \c Enable API-specific Documentation
    @param bool enable_cli \c Enable CLI-specific Documentation
    @param list[str] \c additional_columns List of additional column names to include in argument table outputs
    @param ArgStructCmdCallback \c command_callback Method to execute for each Command processed, Arguments: (command,commandStruct,command_options,result), and returns `result` after manipulation
    @param ArgStructArgCallback \c arg_callback Method to execute for each Argument from each Command processed, Arguments (command,commandStruct,argument,argumentStruct,arg_options,result), and returns `result` after manipulation
    @param Any \c command_options Option(s) to pass to the `command_callback`, default `None`
    @param Any \c arg_options Option(s) to pass to the `arg_callback`, default `None`
    @retval str All Commands processed into Markdown documentation (as a string)
    """
    output:str = ""
    arg_headers:list[str] = [ "API Name", "CLI Flag(s)", "Description", "Required", "Type", "Default", "Allowed Values" ]
    if additional_columns is not None:
        arg_headers += additional_columns
    for cmd, cmd_config in commandlist.items():
        can_cli:bool = not cmd_config.get("cli_hidden")
        can_api:bool = not cmd_config.get("api_hidden")
        if not can_api and not can_cli:
            continue
        if not (can_cli and enable_cli) and not (can_api and enable_api):
            continue
        ui_label:typing.Union[str,None] = cmd_config.get("ui_label")
        label:str = ""
        if ui_label is not None and len(ui_label) > 0 and ui_label != " ":
            label = f"{ui_label} (`{cmd}`)"
        else:
            label = f"`{cmd}`"
        output += f"### Command: {label}\n"
        output += cmd_config.get("help") + "\n\n"
        auth_flag:str = "**Y**" if cmd_config.get("auth_required") else "**N**"
        output += f"Authorization Required? {auth_flag}\n\n"
        access_method_rows:list[list[str]] = [
            [ "Access Method", "Available?" ]
        ]
        if enable_cli:
            access_method_rows.append([ "CLI", "**Y**" if can_cli else "**N**" ])
        if enable_api:
            access_method_rows.append([ "API", "**Y**" if can_api else "**N**" ])
        output += tabulate(access_method_rows,headers="firstrow",tablefmt="github")
        output += "\n"
        if command_callback is not None:
            output = command_callback(cmd,cmd_config,command_options,output)
        argmap_table:list[list[str]] = [
            arg_headers
        ]
        cmd_args:dict[str,typing.Any] = cmd_config.get("args")
        argmap_table += _build_doc_argmap(cmd,cmd_config,cmd_args,arg_callback,arg_options)
        if len(cmd_args) > 0:
            output += "\n"
            output += "#### Arguments\n"
            output += tabulate(argmap_table,headers="firstrow",tablefmt="github")
            output += "\n\n"
        else:
            output += "\n"
    return output

def _build_doc_argmap(command:str,command_config:ArgStructCommand, arglist:dict[str,typing.Any],arg_callback:typing.Union[ArgStructArgCallback,None] = None, arg_options:typing.Any = None) -> list[list[str]]:
    """Build MarkDown Documentation for Each Argument in a Command
    @param str \c command Command that arguments belong to
    @param ArgStructCommand \c command_config
    @param dict[str,typing.Any] \c arglist Argument data for command
    @param ArgStructArgCallback \c arg_callback Method to execute for each Argument from each Command processed, Arguments (command,commandStruct,argument,argumentStruct,arg_options,result), and returns `result` after manipulation
    @param Any \c arg_options Option(s) to pass to the `arg_callback`, default `None`
    @retval str All Commands processed into Markdown documentation (as a string)
    """
    out_list:list[list[str]] = []
    for arg, arg_data in arglist.items():
        arg_row:list[str] = []
        arg_row.append(arg)
        if "cli_flag_names" in arg_data.keys():
            arg_row.append(', '.join(arg_data["cli_flag_names"]))
        else:
            arg_row.append("**NONE**")
        arg_row.append(arg_data["help"])
        arg_row.append("**Y**" if arg_data["required"] else "**N**")
        arg_row.append(arg_data["type"])
        if "default" in arg_data.keys():
            arg_row.append(str(arg_data["default"]))
        else:
            arg_row.append("**NONE**")
        if "values" in arg_data.keys() and arg_data["values"] is not None:
            arg_row.append(', '.join(arg_data["values"]))
        if arg_callback is not None:
            arg_row = arg_callback(command,command_config,arg,arg_data,arg_options,arg_row)
        out_list.append(arg_row)
    return out_list

def markdown_documentation(
        argmap_file:Path,
        enable_cli:bool = True,
        enable_api:bool = True,
        additional_columns:typing.Union[list[str],None] = None,
        command_callback:typing.Union[ArgStructCmdCallback,None] = None, command_options:typing.Any = None,
        arg_callback:typing.Union[ArgStructArgCallback,None] = None, arg_options:typing.Any = None
    ) -> str:
    """Markdown Documentation Generator
    @param Path \c argmap_file Path to ArgMap
    @param bool \c enable_cli Enable CLI Command processing, default True
    @param bool \c enable_api Enable API Command processing, default False
    @param list[str] \c additional_columns List of additional column names to include in argument table outputs
    @param ArgStructCmdCallback \c command_callback Method to execute for each Command processed, Arguments: (command,commandStruct,command_options,result), and returns `result` after manipulation
    @param ArgStructArgCallback \c arg_callback Method to execute for each Argument from each Command processed, Arguments (command,commandStruct,argument,argumentStruct,arg_options,result), and returns `result` after manipulation
    @param Any \c command_options Option(s) to pass to the `command_callback`, default `None`
    @param Any \c arg_options Option(s) to pass to the `arg_callback`, default `None`
    @retval str Processed Documentation
    For `command_callback` the `result` is a str rendered between access method and arguments
    For `arg_callback` the `result` is a list[str] of the current argument table row
    """
    argstruct_obj:ArgStruct = ArgStruct(argmap_file,ArgStruct.OVERRIDE_TYPE_TOML)
    argmap_data:dict[str,dict[str,ArgStructCommand]] = argstruct_obj.grouped
    auth_args:dict[str,dict[str,typing.Any]] = argstruct_obj.get("auth_args")
    arg_headers:list[str] = [ "API Name", "CLI Flag(s)", "Description", "Required", "Type", "Default", "Allowed Values" ]
    if additional_columns is not None:
        arg_headers += additional_columns
    output:str = ""
    if len(auth_args) > 0:
        output += "## Authorization Arguments\n"
        autharg_table:list[list[str]] = [ arg_headers ]
        autharg_table += _build_doc_argmap("empty",ArgStruct.empty,auth_args,arg_callback,arg_options)
        output += tabulate(autharg_table,headers="firstrow",tablefmt="github")
        output += "\n"

    for group, commands in argmap_data.items():
        if len(commands) == 0:
            continue
        output += f"## {group}\n"
        output += _build_doc_commandmap(commands,enable_api,enable_cli,additional_columns,command_callback,command_options,arg_callback,arg_options)
    return output

#### CHECKSUM c13a7bac19a96c66ffcb5a2e78b02c6d08f619a953c4294e2cc5e716bb258ef8
