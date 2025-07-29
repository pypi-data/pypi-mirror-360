# Copyright 2023-2025 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Reusable Argument Structure,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import logging
try:
    import argparser_ng
    from argstruct.argparser_ng_module import parse,api,console,documentation_bin
    logging.debug("Using argparser-ng")
except ModuleNotFoundError:
    from argstruct.argparse_module import parse,api,console,documentation_bin
    logging.debug("Using argparse")

from argstruct.object import ArgStruct

#### CHECKSUM bc680a0fe186b01e795ae963b519cca6cd2932d35d1002df3ee97d39d1cb59ac
