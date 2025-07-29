# Copyright 2024-2025 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of You Cant Change That - A File Monitoring and change prevention process,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###

import typing
import logging
import getpass
from sys import exit as sys_exit
from pathlib import Path
import socket

import argparser_ng
import argstruct
try:
    from specker.static import StaticSpecker
except (ModuleNotFoundError,NameError):
    from argstruct.object import StaticSpecker

from ycct.service import YCCTService
from ycct.client import YCCTClient

def ycct_start() -> None:
    """Service Starter"""
    socket_path:typing.Union[None,Path] = None
    log_path:Path = Path("/var/log/ycct.log").expanduser().resolve()
    if getpass.getuser() != "root":
        socket_path = Path("~/ycct.sock").expanduser().resolve()
        log_path = Path("~/ycct.log").expanduser().resolve()
    logging_fh:logging.FileHandler = logging.FileHandler(log_path)
    logging_fh.formatter = logging.Formatter(fmt="%(asctime)s:%(levelname)s \t%(threadName)s\t%(module)s \t%(message)s")
    logging.getLogger().addHandler(logging_fh)
    service:YCCTService = YCCTService(socket_path)
    service.run()

def ycct_bin() -> None:
    """YCCT Execution Entry Point"""
    loglevel:int = logging.WARNING
    logging.basicConfig(level=loglevel,format="%(levelname)s \t%(threadName)s\t%(module)s \t%(message)s")
    parser:argparser_ng.ArgumentParserNG = argparser_ng.ArgumentParserNG(description="YCCT - You Cant Change That!")
    parser.add_argument_item(name="verbose",flags=["v","verbose"],help="Turn on Debugging",store_type=bool)
    argstruct_path:Path = Path(__file__).expanduser().resolve().parent.joinpath("command-map.toml")
    if not argstruct_path.is_file():
        print("Unable to locate option map!")
        sys_exit(1)
    argstruct_obj:argstruct.ArgStruct = argstruct.ArgStruct(argstruct_path,"toml")
    argstruct.console(argstruct_obj,parser,False)
    input_args:typing.Union[dict[typing.Any,typing.Any],None] = argstruct.parse(argstruct_obj,parser,"sub_command")
    if input_args is None:
        parser.show_help()
        sys_exit(1)

    if input_args["verbose"]:
        loglevel = logging.DEBUG
        StaticSpecker()
        logging.getLogger("specker.loader.SpecLoader").setLevel(loglevel)
        logging.root.setLevel(loglevel)
    input_args.pop("verbose")
    if input_args["sub_command"] == "start":
        ycct_start()
    else:
        client:YCCTClient = YCCTClient()
        ycct_commands:dict[str,typing.Callable] = {
            "stop": client.shutdown,
            "monitor": client.monitor,
            "enable": client.enable,
            "disable": client.disable,
            "remove": client.remove,
            "scan": client.scan,
            "status": client.status
        }
        if input_args["sub_command"] not in ycct_commands.keys():
            print("No Such Command")
            sys_exit(1)
        call:typing.Callable = ycct_commands[input_args["sub_command"]]
        input_args.pop("sub_command")
        result:bool = call(**input_args)
        if not result:
            print("Command Failed")
            sys_exit(1)
        print("Success")
        sys_exit(0)

#### CHECKSUM ab8d0b007080f2da92859d6fdfdb8e3d1c9ea09d3d9bbf998bb9e0c8a12fe24d
