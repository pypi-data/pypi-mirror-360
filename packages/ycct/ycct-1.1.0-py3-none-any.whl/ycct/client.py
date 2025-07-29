# Copyright 2024-2025 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of You Cant Change That - A File Monitoring and change prevention process,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import socket
import typing
import getpass
from sys import exit as sys_exit
from pathlib import Path

class YCCTClient:
    """You Cant Change That! Comms Client"""
    _socket:socket.socket
    _socket_path:Path
    _socket_str:str

    def __init__(self) -> None:
        if getpass.getuser() != "root":
            self._socket_path = Path("~/ycct.sock").expanduser().resolve()
        else:
            self._socket_path = Path("/var/run/ycct.sock").expanduser().resolve()
        self._socket_str:str = self._socket_path.as_posix()
        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self._socket.connect(self._socket_str)
        except FileNotFoundError:
            print(f"Cannot Connect, Socket: {self._socket_str} does not exist (is the service running?)")
            sys_exit(1)

    def scan(self) -> bool:
        """Force Rescan
        @retval bool Success/Failure
        """
        self._socket.send("scan:".encode("utf-8"))
        result:bytes = self._socket.recv(8)
        self._socket.close()
        return bool(result)

    def status(self) -> bool:
        """Show Status information
        @retval bool Success/Failure
        """
        self._socket.send("status:".encode("utf-8"))
        result:bytes = self._socket.recv(8192)
        print(result.decode("utf-8"))
        self._socket.close()
        return True

    def monitor(self,file:typing.Union[str,Path],type:typing.Union[list[str],str],recursive:bool) -> bool:
        """Add New File to be Monitored
        @param Union[str,Path] file Path to File or Dir to monitor
        @param Union[list[str],str] type Monitoring Types
        @param bool recursive If a directory, recursively monitor
        @retval bool Success/Failure
        """
        if isinstance(file,str):
            file = Path(file).expanduser().resolve()
        monitor:str = ','.join(type)
        self._socket.send(f"monitor:file={file.as_posix()}:recurse={str(1) if recursive else str(0)}:type=[{monitor}]".encode("utf-8"))
        result:bytes = self._socket.recv(8)
        self._socket.close()
        return bool(result)

    def shutdown(self) -> bool:
        """Shutdown Command Send
        @retval bool Success/Failure (Always returns success)
        """
        self._socket.send("shut".encode("utf-8"))
        self._socket.close()
        return True

    def enable(self,file:typing.Union[str,Path]) -> bool:
        """Re-Enable Monitoring for a file/dir
        @param Union[str,Path] file Path to File or Dir to monitor
        @retval bool Success/Failure
        """
        if isinstance(file,str):
            file = Path(file).expanduser().resolve()
        self._socket.send(f"enable:file={file.as_posix()}".encode("utf-8"))
        result:bytes = self._socket.recv(8)
        self._socket.close()
        return bool(result.decode("utf-8"))

    def disable(self,file:typing.Union[str,Path]) -> bool:
        """Disable Monitoring Temporarily
        @param Union[str,Path] file Path to File or Dir to monitor
        @retval bool Success/Failure
        """
        if isinstance(file,str):
            file = Path(file).expanduser().resolve()
        self._socket.send(f"disable:file={file.as_posix()}".encode("utf-8"))
        result:bytes = self._socket.recv(8)
        self._socket.close()
        return bool(result.decode("utf-8"))

    def remove(self,file:typing.Union[str,Path]) -> bool:
        """Remove a file/dir from monitoring
        @param Union[str,Path] file Path to File or Dir to remove
        @retval bool Success/Failure
        """
        if isinstance(file,str):
            file = Path(file).expanduser().resolve()
        self._socket.send(f"remove:file={file.as_posix()}".encode("utf-8"))
        result:bytes = self._socket.recv(8)
        self._socket.close()
        return bool(result.decode("utf-8"))

#### CHECKSUM 5d92a7e0b9a778a88c40e8241a79fa261cbbb1fa67e957622f673fce6ce55e0b
