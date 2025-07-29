# Copyright 2023-2025 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Reusable Argument Structure,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import argparse
import re
import typing

def _build_console_arg(parser:argparse.ArgumentParser, arg_name:str, arg_config:dict[str,typing.Any]) -> None:
    """Build a single argument from an argument config block
    @param argparse.ArgumentParser \c parser Argument Parser to attach arguments to
    @param str \c arg_name Name of Argument to add
    @param dict[str,Any] \c arg_config Argument Configuration data
    @retval None Nothing
    """
    aargs:list[str] = arg_config["cli_flag_names"]
    kargs:dict[str,typing.Any] = {
        "dest": re.sub(r'-','_',arg_name),
        "help": arg_config["help"]
    }
    if arg_config["required"]:
        kargs["required"] = arg_config["required"]
    if arg_config["multi"]:
        kargs["nargs"] = "+"
    if arg_config["type"] == "bool":
        kargs["action"] = "store_true"
    if arg_config["values"] is not None:
        kargs["choices"] = arg_config["values"]
    if "default" in arg_config.keys():
        kargs["default"] = arg_config["default"]
    parser.add_argument(*aargs,**kargs)

#### CHECKSUM 7e4a2cf2fe10c3cf3b7be17090f9c30aec31ef3e2a6ba55e830e009ebc640891
