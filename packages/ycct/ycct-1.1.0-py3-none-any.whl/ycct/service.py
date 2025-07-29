# Copyright 2024-2025 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of You Cant Change That - A File Monitoring and change prevention process,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###

import json
import os
import random
import re
import logging
import typing
import stat
import socket
import shutil
import threading
from pathlib import Path
from time import sleep
import getpass

from atckit.utilfuncs import UtilFuncs
from atckit.service import Service

from ycct.functions import getfsha256, getfattr, send_wall, attr_result, setfattr, scan_dir

class YCCTService(Service):
    """You Cant Change That! Service Runner"""

    _SERVICE_NAME:str = "ycct"
    _SERVICE_SHUTDOWN_LIMIT:int = 10

    _socket_path:Path
    _socket_path_str:str
    _connection:socket.socket
    _connected:bool

    _scan_db:dict[str,dict[str,typing.Any]]
    _scandb_path:Path
    _state_db:dict[str,dict[str,typing.Any]]
    _statedb_path:Path
    _scanners:dict[str,threading.Thread]

    __WALL_MESSAGE:str = """WARNING WARNING WARNING
A file or directory monitored by YCCT has been changed!!
An attempt to restore its state will be made automatically.
Please check the YCCT Logs for more information

Monitored File:
%s"""

    __WALL_MESSAGE_CRIT = """ALERT ALERT ALERT
CONTENT RESTORE FOR '%s' FAILED!!
Monitoring of this file has been disabled to prevent further damage
Please check the YCCT Logs for more information"""

    def __init__(self,socket_path:typing.Union[None,Path] = None) -> None:
        """Initializer
        @param Union[None,Path] socket_path Path to store socket file, default None; If None, default is /var/run/ycct/ycct.sock
        """
        self.logger = UtilFuncs.create_object_logger(self)
        self.logger.setLevel(logging.DEBUG)
        if socket_path is None:
            socket_path = Path("/var/run/ycct/ycct.sock").expanduser().resolve()
        self._socket_path = socket_path
        self._socket_path_str = self._socket_path.as_posix()
        self._scanners = {}
        if not self.__config_search():
            self.__first_config()
        super().__init__()
        self.__load_db()
        self.__monitor_start_all()
        self._connected = False
        # if not standalone:
        self.services += self._service_socket

    def __load_db(self) -> None:
        """Scanner and State DB Loaders
        @retval None Nothing
        Load Configured State DB and Monitoring DB
        """
        self._scandb_path = Path(self._config["scandb"]).expanduser().resolve()
        self._statedb_path = Path(self._config["statedb"]).expanduser().resolve()
        if self._scandb_path.is_file():
            with open(self._scandb_path, "r", encoding="utf-8") as f:
                self._scan_db = json.loads(f.read())
        else:
            self.logger.warning("No Scan DB Located. Creating an empty one")
            self._scan_db = {}
            self.__write_scandb()
        if self._statedb_path.is_file():
            with open(self._statedb_path, "r", encoding="utf-8") as f:
                self._state_db = json.loads(f.read())
        else:
            self.logger.warning("No State DB Located. Creating an empty one")
            self._state_db = {}
            self.__write_statedb()

    def __write_statedb(self) -> None:
        """Write the State Database
        @retval None Nothing
        """
        with open(self._statedb_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(self._state_db))

    def __write_scandb(self) -> None:
        """Write the Scanner Database
        @retval None Nothing
        """
        with open(self._scandb_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(self._scan_db,indent=4))

    def __first_config(self) -> None:
        """First time run, create default config file
        @retval None Nothing
        """
        default_file:Path = Path(__file__).expanduser().resolve().parent.joinpath("default.config.toml").resolve()
        self.logger.info("Creating New Config, Appears to be first run (we could not locate the service config)")
        for p in UtilFuncs.CONFIG_SCAN_BASE_PATHS:
            check_svcpath:Path = p.expanduser().resolve().joinpath(self._SERVICE_NAME).resolve()
            if not check_svcpath.is_dir():
                self.logger.debug(f"Attempting to Create Dir: {check_svcpath.as_posix()}")
                try:
                    check_svcpath.mkdir(parents=True)
                    self.logger.debug("Create Succeeded, Will Create Configuration Here")
                except BaseException as e:
                    self.logger.debug(f"Create Failed: {e}")
                    continue
            target_path:Path = check_svcpath.joinpath(f"{self._SERVICE_NAME}.toml").resolve()
            if target_path.is_file():
                self.logger.warning(f"We actually found a config here: {target_path.as_posix()}")
                return
            shutil.copy2(default_file,target_path)
            self.logger.info(f"Created new Config File at {target_path.as_posix()}")
            return

    def __config_search(self) -> bool:
        """Search for Config File, return whether we found one or not
        @retval bool Whether or not a configuration file was found at the typical locations
        """
        for p in UtilFuncs.CONFIG_SCAN_BASE_PATHS:
            check_svcpath:Path = p.expanduser().resolve().joinpath(self._SERVICE_NAME).resolve()
            if not check_svcpath.is_dir():
                continue
            for ext in UtilFuncs.CONFIG_SCAN_FILE_EXTS:
                check_file:Path = check_svcpath.joinpath(f"{self._SERVICE_NAME}.{ext}").resolve()
                if check_file.is_file():
                    return True
        return False

    def __monitor_start_all(self) -> None:
        """Scanner Start, Start all monitors
        @retval None Nothing
        """
        for file_data in self._scan_db.values():
            if file_data["file"] not in self._scanners.keys():
                self.__monitor_create(**file_data)
            sleep(0.1)

    # pylint: disable=unused-argument
    def __monitor_create(self,file:str,perms:bool,content:bool,attr:bool,enabled:bool,recursive:bool) -> None:
        """Create a new Monitoring Instance
        @param str file Path to monitor
        @param bool perms Whether to monitor permissions (uid, gid, mode)
        @param bool content Whether to monitor content changes
        @param bool attr Whether to monitor attribute changes (chattr)
        @param bool enabled Whether monitor is enabled
        @param bool recursive If a directory, recursively monitor
        @retval None Nothing
        """
        req_args:dict[str,typing.Any] = locals()
        req_args.pop("self")
        self._scanners[file] = threading.Thread(target=self.__monitoring_thread,name=f"ycct.scanner:{file}",kwargs=req_args)
        self._scanners[file].start()

    def __monitoring_thread(self,file:str,perms:bool,content:bool,attr:bool,enabled:bool,recursive:bool) -> None:
        """Actual Monitor thread for single monitor entry
        @param str file Path to monitor
        @param bool perms Whether to monitor permissions (uid, gid, mode)
        @param bool content Whether to monitor content changes
        @param bool attr Whether to monitor attribute changes (chattr)
        @param bool enabled Whether monitor is enabled
        @param bool recursive If a directory, recursively monitor
        @retval None Nothing
        """
        args:dict[str,typing.Any] = locals()
        args.pop("self")
        rand_interval:float = random.random() * self._config["monitor_interval"]
        self.logger.info(f"Starting Monitor for {file}")
        while self.should_run:
            if file not in self._scan_db.keys():
                self.logger.warning(f"File {file} removed from monitoring, Halting thread")
                break
            enabled = self._scan_db[file]["enabled"]
            if enabled:
                file_path:Path = Path(file).expanduser().resolve()
                if file_path.is_dir() and self._scan_db[file]["recursive"]:
                    scan_dir(file_path,self.__dir_check,args,[],[],[])
                else:
                    self.__single_check(**args)
            sleep(self._config["monitor_interval"] + rand_interval)
        self.logger.debug(f"Shutting down monitor for {file}")

    def __dir_check(self,file:Path,args:dict[str,typing.Any]) -> None:
        if args["file"] in self._scan_db.keys():
            if not self._scan_db[args["file"]]["enabled"]:
                return
        args["file"] = file.as_posix()
        self.__single_check(**args)

    def __single_check(self,file:str,perms:bool,content:bool,attr:bool,enabled:bool,recursive:bool) -> None:
        args:dict[str,typing.Any] = locals()
        args.pop("self")
        # self.logger.debug(f"Scanning: {file}")
        if file not in self._state_db.keys():
            self.__state_update(**args)
        if not self.__state_check(**args):
            if self._config["enable_wall"]:
                send_wall(self.__WALL_MESSAGE.replace('%s',file))
            self.__state_restore(**args)

    def __state_restore(self,file:str,perms:bool,content:bool,attr:bool,enabled:bool,recursive:bool) -> None:
        """State restoration method, called when expected state does not match current state
        @param str file Path to monitor
        @param bool perms Whether to monitor permissions (uid, gid, mode)
        @param bool content Whether to monitor content changes
        @param bool attr Whether to monitor attribute changes (chattr)
        @param bool enabled Whether monitor is enabled
        @param bool recursive If a directory, recursively monitor
        @retval None Nothing
        """
        file_path:Path = Path(file).expanduser().resolve()
        if perms:
            self.logger.warning(f"Restoring Owner/Group for {file}")
            os.chown(file_path,self._state_db[file]["uid"],self._state_db[file]["gid"])
            self.logger.warning(f"Restoring Permissions for {file}")
            os.chmod(file_path,self._state_db[file]["mode"])
        if attr:
            self.logger.warning(f"Restoring Attributes for {file}")
            attrinfo:attr_result = attr_result(file_path,self._state_db[file]["attrs"])
            setfattr(attrinfo)
        if content:
            save_path_root:Path = Path(self._config["content_dir"]).expanduser().resolve()
            file_path_root_strip:Path = Path(file_path.as_posix().lstrip('/'))
            save_path:Path = save_path_root.joinpath(file_path_root_strip).resolve()
            restore_hash:str = getfsha256(save_path).hex()
            if self._state_db[file]["content"] != restore_hash:
                self.logger.critical(f"ALERT, CONTENT RESTORATION FAILED FOR {file}, restoration sha256 does not match state sha256")
                self.logger.critical(f"This means that something has modified the file at {save_path.as_posix()}")
                self.logger.critical(f"Expected SHA256: {self._state_db[file]['content']}")
                self.logger.critical(f"Restore Location SHA256: {restore_hash}")
                self.logger.critical("To prevent further damage, this file has not been restored.")
                self.logger.critical("This monitor will now be disabled")
                if self._config["enable_wall"]:
                    send_wall(self.__WALL_MESSAGE_CRIT.replace('%s',file))
                self._scan_db[file]["enabled"] = False
                self.__write_scandb()
                return
            self.logger.warning(f"Restoring Content for {file}")
            shutil.copy2(save_path,file_path)

    def __state_update(self,file:str,perms:bool,content:bool,attr:bool,enabled:bool,recursive:bool) -> None:
        """State DB Updater for single monitoring instance
        @param str file Path to monitor
        @param bool perms Whether to monitor permissions (uid, gid, mode)
        @param bool content Whether to monitor content changes
        @param bool attr Whether to monitor attribute changes (chattr)
        @param bool enabled Whether monitor is enabled
        @param bool recursive If a directory, recursively monitor
        @retval None Nothing
        """
        self.logger.warning(f"Updating State for {file}")
        args:dict[str,typing.Any] = locals()
        args.pop("self")
        state:dict[str,typing.Any] = self.__state_get(**args)
        self._state_db[file] = state
        if content:
            save_path_root:Path = Path(self._config["content_dir"]).expanduser().resolve()
            file_path_root_strip:Path = Path(file.lstrip('/'))
            save_path:Path = save_path_root.joinpath(file_path_root_strip).resolve()
            if not save_path.parent.is_dir():
                save_path.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(Path(file).expanduser().resolve(),save_path)
        self.__write_statedb()

    def __state_get(self,file:str,perms:bool,content:bool,attr:bool,enabled:bool,recursive:bool) -> dict[str,typing.Any]:
        """Get Active State of file
        @param str file Path to monitor
        @param bool perms Whether to monitor permissions (uid, gid, mode)
        @param bool content Whether to monitor content changes
        @param bool attr Whether to monitor attribute changes (chattr)
        @param bool enabled Whether monitor is enabled
        @param bool recursive If a directory, recursively monitor
        @retval dict[str,typing.Any] State Dictionary object; Null/None values are not monitored.
        """
        file_path:Path = Path(file).expanduser().resolve()
        state:dict[str,typing.Any] = {}
        if perms:
            statinfo:os.stat_result = os.stat(file_path)
            state["gid"] = statinfo.st_gid
            state["uid"] = statinfo.st_uid
            state["mode"] = statinfo.st_mode
        else:
            state["gid"] = None
            state["uid"] = None
            state["mode"] = None
        if attr:
            attrinfo:attr_result = getfattr(file_path)
            state["attrs"] = attrinfo.getdict()
        else:
            state["attrs"] = {}
        if content:
            state["content"] = getfsha256(file_path).hex()
        else:
            state["content"] = None
        return state

    def __state_check(self,file:str,perms:bool,content:bool,attr:bool,enabled:bool,recursive:bool) -> bool:
        """State Checker, Get state of monitored file, and report whether it matches expected
        @param str file Path to monitor
        @param bool perms Whether to monitor permissions (uid, gid, mode)
        @param bool content Whether to monitor content changes
        @param bool attr Whether to monitor attribute changes (chattr)
        @param bool enabled Whether monitor is enabled
        @param bool recursive If a directory, recursively monitor
        @retval bool True = State is ok, False = State differs
        """
        args:dict[str,typing.Any] = locals()
        args.pop("self")
        if not Path(file).resolve().exists():
            self.logger.warning(f"{file} State has changed!")
            self.logger.warning(f"{file} WAS REMOVED!")
            return False
        known_state:dict[str,typing.Any] = self._state_db[file]
        current_state:dict[str,typing.Any] = self.__state_get(**args)
        result:bool = True
        for k,v in known_state.items():
            if v is None:
                continue
            if isinstance(v,dict):
                for a,en in v.items():
                    if a not in current_state[k].keys():
                        result = False
                        break
                    if current_state[k][a] != en:
                        result = False
                        break
            else:
                if k not in current_state.keys():
                    result = False
                    break
                if current_state[k] != v:
                    result = False
                    break
        if not result:
            self.logger.warning(f"{file} State has changed!")
            self.logger.warning(f"Expected: {json.dumps(known_state)}")
            self.logger.warning(f"Got:      {json.dumps(current_state)}")
        return result
    # pylint: enable=unused-argument

    #### COMMANDS
    def __command_monitor(self,sock:socket.socket,file:str,type:str,recurse:typing.Union[int,str,bool] = False) -> None:
        """COMMAND: `monitor` - Add a file/directory to be monitored
        @param socket.socket sock Socket that command was called on
        @param str file Path to file/directory that will be monitored
        @param str type Type of monitoring to perform, should be in the format of `'["",...]`, acceptable values: 'perms', 'content', 'attr', 'p', 'c', 'a'
        @param Union[int,str,bool] recurse Whether to recurse into directory, if the specified path is a directory; default False
        @retval None Nothing
        """
        long_values:list[str] = [ "perms", "content", "attr" ]
        short_values:list[str] = [ "p", "c", "a" ]
        req_monitors:list[str] = type.lstrip('[').rstrip(']').split(',')
        monitors:list[str] = [ long_values[short_values.index(v)] if len(v) == 1 else v for v in req_monitors ]
        # pylint: disable=simplifiable-if-statement
        if recurse in [ "1", 1, True ]:
            recurse = True
        else:
            recurse = False
        # pylint: enable=simplifiable-if-statement
        self.logger.info("Executing Monitor Addition")
        file_path:Path = Path(file).expanduser().resolve()
        if file_path.as_posix() not in self._scan_db.keys():
            self.logger.info(f"Adding {file_path.as_posix()} to scan db")
            self._scan_db[file_path.as_posix()] = {
                "file": file_path.as_posix(),
                "enabled": True,
                "recursive": recurse
            }
            for v in long_values:
                if v in monitors:
                    self._scan_db[file_path.as_posix()][v] = True
                else:
                    self._scan_db[file_path.as_posix()][v] = False
            self.__write_scandb()
            monitor_data:dict[str,typing.Any] = self._scan_db[file_path.as_posix()]
            self.__monitor_create(**monitor_data)
            sock.send(bytes(1))
        else:
            self.logger.warning(f"{file_path.as_posix()} is already being monitored")
            sock.send(bytes(0))
        sock.close()

    def __command_enable(self,sock:socket.socket,file:str) -> None:
        """COMMAND: `enable` - (Re-)enable monitoring of a file
        @param socket.socket sock Socket that command was called on
        @param str file Path to file/directory that will be monitored
        @retval None Nothing
        """
        file_path:Path = Path(file).expanduser().resolve()
        if not file_path.exists():
            self.logger.error(f"No Such File: {file}")
        if file not in self._scan_db.keys():
            self.logger.error(f"{file} is not Registered")
            sock.send(bytes(0))
            sock.close()
            return
        self.logger.info(f"Enabling Monitoring for {file}")
        self._scan_db[file]["enabled"] = True
        self.__write_scandb()
        sock.send(bytes(1))
        sock.close()

    def __command_disable(self,sock:socket.socket,file:str) -> None:
        """COMMAND: `disable` - disable monitoring of a file
        @param socket.socket sock Socket that command was called on
        @param str file Path to file/directory that was monitored
        @retval None Nothing
        """
        file_path:Path = Path(file).expanduser().resolve()
        if not file_path.exists():
            self.logger.error(f"No Such File: {file}")
        if file not in self._scan_db.keys():
            self.logger.error(f"{file} is not Registered")
            sock.send(bytes(0))
            sock.close()
            return
        self.logger.warning(f"Disabling Monitoring for {file}")
        self._scan_db[file]["enabled"] = False
        self.__write_scandb()
        sock.send(bytes(1))
        sock.close()

    def __command_remove(self,sock:socket.socket,file:str) -> None:
        """COMMAND: `remove` - Remove monitoring completely for a file/directory
        @param socket.socket sock Socket that command was called on
        @param str file Path to file/directory that will be monitored
        @retval None Nothing
        """
        if file not in self._scan_db.keys():
            self.logger.error(f"{file} is not Registered")
            sock.send(bytes(0))
            sock.close()
            return
        self.logger.warning(f"Removing Monitoring for {file}")
        self._scan_db.pop(file)
        self._state_db.pop(file)
        self.__write_scandb()
        self.__write_statedb()
        sock.send(bytes(1))
        sock.close()

    def __command_scan(self,sock:socket.socket) -> None:
        """COMMAND: `scan` - Remove State DB and force a rescan of all files/directories
        @param socket.socket sock Socket that command was called on
        @retval None Nothing
        """
        self.logger.warning("Clearing State DB, All items will rescan automatically, if they are enabled, or the next time they are enabled")
        self._state_db = {}
        self.__write_statedb()
        sock.send(bytes(1))
        sock.close()

    def __command_status(self,sock:socket.socket) -> None:
        """COMMAND: `status` - Show YCCT Status and monitored file information
        @param socket.socket sock Socket that command was called on
        @retval None Nothing
        """
        filedata_list:list[str] = []
        for f,info in self._scan_db.items():
            state:str = "[ENABLED]\t" if info["enabled"] else "[DISABLED]\t"
            monitors:list[str] = []
            padding:str = ""
            for m in [ "recursive", "perms", "attr", "content" ]:
                if info[m]:
                    monitors.append(m)
                else:
                    padding = ''.join([ " " for _ in range(0,len(m)) ]) + padding
            monitors[0] = padding + monitors[0]
            filedata_list.append(f"{state}\t{','.join(monitors)}\t{f}")
        sock.send('\n'.join([
            f"Total Files Monitored: {str(len(self._scan_db))}",
            "Files Monitored:",
            "\t"+'\n\t'.join(filedata_list)
        ]).encode("utf-8"))

    #### END COMMANDS

    # pylint: disable=unused-argument
    def __command_parse(self,sock:socket.socket,src:typing.Any,data:str) -> None:
        """Command Processor and argument builder
        @param socket.socket sock Socket that command was called on
        @param Any src Source Address / Port (Empty / Unused because using unix sockets for this service)
        @param str data Data received from socket
        @retval None Nothing
        """
        ycct_commands:dict[str,typing.Callable] = {
            "monitor": self.__command_monitor,
            "enable": self.__command_enable,
            "disable": self.__command_disable,
            "remove": self.__command_remove,
            "scan": self.__command_scan,
            "status": self.__command_status,
        }
        if data == "shut":
            self.logger.info("Shutting Down")
            self.shutdown = True
            sock.close()
            return
        self.logger.debug(data)
        if not re.match(r'^.*:.*?$',data):
            self.logger.error("Badly Formatted Message")
            sock.close()
            return
        command_data:dict[str,typing.Any] = {}
        parts:list[str] = data.split(':')
        command:str = parts.pop(0)
        if len(parts) >= 1 and len(parts[0]) > 0:
            for raw_value in parts:
                raw_part:list[str] = raw_value.split("=")
                command_data[raw_part[0]] = raw_part[1]
        if command not in ycct_commands.keys():
            self.logger.error(f"Unknown Command: {command}")
            sock.close()
            return
        command_data["sock"] = sock
        call:typing.Callable = ycct_commands[command]
        call(**command_data)
    # pylint: enable=unused-argument

    def _service_socket(self) -> None:
        """AF_UNIX Socket Setup
        @retval None Nothing
        """
        running_user:str = getpass.getuser()
        sock_mask:int = stat.S_IRGRP | stat.S_IWGRP | stat.S_IWUSR | stat.S_IRUSR | stat.S_IFSOCK
        service_user:str = "root"
        service_group:str = "root"
        if running_user != "root":
            service_user = service_group = running_user
        if not self._socket_path.parent.is_dir():
            self._socket_path.parent.mkdir(parents=True)
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as sock:
            try:
                sock.bind(self._socket_path_str)
                self.logger.info(f"Server Socket bound at {self._socket_path_str}")
                self._socket_path.chmod(sock_mask)
                try:
                    shutil.chown(self._socket_path,service_user,service_group)
                except PermissionError as e:
                    self.logger.warning(f"Failed to set user/group of socket to {service_user}:{service_group}. {e}")
                sock.listen(10)
            except BaseException as e:
                self.logger.critical(f"Binding to {self._socket_path_str} failed")
                self.logger.critical(e,exc_info=True)
                self._stop_threads()
                return
            conn:socket.socket
            addr:typing.Any
            while self.should_run: ## Service Level Loop
                try:
                    conn,addr = sock.accept()
                except OSError:
                    continue
                self.logger.info(f"Connection from {addr}")
                while True: ## Connection Level Loop; Read Data, Act, Respond, Repeat; Close on Error
                    try:
                        data:bytes = conn.recv(8192)
                    except OSError:
                        break
                    if not data:
                        break
                    self.__command_parse(conn,addr,data.decode("utf-8"))
            self._socket_path.unlink(True)

#### CHECKSUM 10ddec5d903e85079c4eb707ac3d91da8be360d65dbb62a3d05d2e363577df63
