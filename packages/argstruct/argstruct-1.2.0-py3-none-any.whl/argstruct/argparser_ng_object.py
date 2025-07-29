# Copyright 2023-2025 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Reusable Argument Structure,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import re
import typing
from pydoc import locate
import argparser_ng

def _build_console_arg(parser:typing.Union[argparser_ng.ArgumentParserCommand,argparser_ng.ArgumentParserGroup], arg_name:str, arg_config:dict[str,typing.Any]) -> None:
    """Build a single argument from an argument config block
    @param argparse.ArgumentParser \c parser Argument Parser to attach arguments to
    @param str \c arg_name Name of Argument to add
    @param dict[str,Any] \c arg_config Argument Configuration data
    @retval None Nothing
    """
    kargs:dict[str,typing.Any] = {
        "name": re.sub(r'-','_',arg_name),
        "help": arg_config["help"]
    }
    if arg_config["required"]:
        kargs["required"] = arg_config["required"]
    if arg_config["multi"]:
        kargs["repeatable"] = argparser_ng.ArgumentItemRepeat.REPEAT_APPEND
    if arg_config["values"] is not None:
        kargs["values"] = arg_config["values"]
    if "default" in arg_config.keys():
        kargs["default"] = arg_config["default"]
    kargs["store_type"] = locate(arg_config["type"])
    kargs["flags"] = [ f.lstrip('-') for f in arg_config["cli_flag_names"] ]
    parser.add_argument_item(**kargs)

#### CHECKSUM 2d0a443c925c1df0144fb0d61f9f140cddf0fa80984e14a8136e5e7e8d00d18b
