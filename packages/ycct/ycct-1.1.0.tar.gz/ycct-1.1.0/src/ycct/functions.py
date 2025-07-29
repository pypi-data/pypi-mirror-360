# Copyright 2024-2025 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of You Cant Change That - A File Monitoring and change prevention process,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###

import typing
from hashlib import sha256
import logging
import re
import subprocess
from pathlib import Path

# pylint: disable=too-many-public-methods
class attr_result:
    """Attribute Object
    Broken down output of lsattr
    """

    _attrs:dict[str,bool]
    _file:Path

    @property
    def file(self) -> Path:
        """Path for which the attributes are for"""
        return self._file
    @property
    def append(self) -> bool:
        """Attribute: 'a'"""
        return self._attrs["a"]
    @append.setter
    def append(self,value:bool) -> None:
        """Set Attribute: 'a'"""
        self._attrs["a"] = value
    @property
    def no_atime(self) -> bool:
        """Attribute: 'A'"""
        return self._attrs["A"]
    @no_atime.setter
    def no_atime(self,value:bool) -> None:
        """Set Attribute: 'A'"""
        self._attrs["A"] = value
    @property
    def compressed(self) -> bool:
        """Attribute: 'c'"""
        return self._attrs["c"]
    @compressed.setter
    def compressed(self,value:bool) -> None:
        """Set Attribute: 'c'"""
        self._attrs["c"] = value
    @property
    def no_cow(self) -> bool:
        """Attribute: 'C'"""
        return self._attrs["C"]
    @no_cow.setter
    def no_cow(self,value:bool) -> None:
        """Set Attribute: 'C'"""
        self._attrs["C"] = value
    @property
    def no_dump(self) -> bool:
        """Attribute: 'd'"""
        return self._attrs["d"]
    @no_dump.setter
    def no_dump(self,value:bool) -> None:
        """Set Attribute: 'd'"""
        self._attrs["d"] = value
    @property
    def dirsync(self) -> bool:
        """Attribute: 'D'"""
        return self._attrs["D"]
    @dirsync.setter
    def dirsync(self,value:bool) -> None:
        """Set Attribute: 'D'"""
        self._attrs["D"] = value
    @property
    def extents(self) -> bool:
        """Attribute: 'e'"""
        return self._attrs["e"]
    @extents.setter
    def extents(self,value:bool) -> None:
        """Set Attribute: 'e'"""
        self._attrs["e"] = value
    @property
    def encrypted(self) -> bool:
        """Attribute: 'E'"""
        return self._attrs["E"]
    @encrypted.setter
    def encrypted(self,value:bool) -> None:
        """Set Attribute: 'E'"""
        self._attrs["E"] = value
    @property
    def case_insensitive(self) -> bool:
        """Attribute: 'F'"""
        return self._attrs["F"]
    @case_insensitive.setter
    def case_insensitive(self,value:bool) -> None:
        """Set Attribute: 'F'"""
        self._attrs["F"] = value
    @property
    def immutable(self) -> bool:
        """Attribute: 'i'"""
        return self._attrs["i"]
    @immutable.setter
    def immutable(self,value:bool) -> None:
        """Set Attribute: 'i'"""
        self._attrs["i"] = value
    @property
    def indexed(self) -> bool:
        """Attribute: 'I'"""
        return self._attrs["I"]
    @indexed.setter
    def indexed(self,value:bool) -> None:
        """Set Attribute: 'I'"""
        self._attrs["I"] = value
    @property
    def journaled(self) -> bool:
        """Attribute: 'j'"""
        return self._attrs["j"]
    @journaled.setter
    def journaled(self,value:bool) -> None:
        """Set Attribute: 'j'"""
        self._attrs["j"] = value
    @property
    def no_compression(self) -> bool:
        """Attribute: 'm'"""
        return self._attrs["m"]
    @no_compression.setter
    def no_compression(self,value:bool) -> None:
        """Set Attribute: 'm'"""
        self._attrs["m"] = value
    @property
    def inline_data(self) -> bool:
        """Attribute: 'N'"""
        return self._attrs["N"]
    @inline_data.setter
    def inline_data(self,value:bool) -> None:
        """Set Attribute: 'N'"""
        self._attrs["N"] = value
    @property
    def project_hierarchy(self) -> bool:
        """Attribute: 'P'"""
        return self._attrs["P"]
    @project_hierarchy.setter
    def project_hierarchy(self,value:bool) -> None:
        """Set Attribute: 'P'"""
        self._attrs["P"] = value
    @property
    def secure_delete(self) -> bool:
        """Attribute: 's'"""
        return self._attrs["s"]
    @secure_delete.setter
    def secure_delete(self,value:bool) -> None:
        """Set Attribute: 's'"""
        self._attrs["s"] = value
    @property
    def sync(self) -> bool:
        """Attribute: 'S'"""
        return self._attrs["S"]
    @sync.setter
    def sync(self,value:bool) -> None:
        """Set Attribute: 'S'"""
        self._attrs["S"] = value
    @property
    def no_tail_merge(self) -> bool:
        """Attribute: 't'"""
        return self._attrs["t"]
    @no_tail_merge.setter
    def no_tail_merge(self,value:bool) -> None:
        """Set Attribute: 't'"""
        self._attrs["t"] = value
    @property
    def top_hierarchy(self) -> bool:
        """Attribute: 'T'"""
        return self._attrs["T"]
    @top_hierarchy.setter
    def top_hierarchy(self,value:bool) -> None:
        """Set Attribute: 'T'"""
        self._attrs["T"] = value
    @property
    def allow_undelete(self) -> bool:
        """Attribute: 'u'"""
        return self._attrs["u"]
    @allow_undelete.setter
    def allow_undelete(self,value:bool) -> None:
        """Set Attribute: 'u'"""
        self._attrs["u"] = value
    @property
    def direct_access(self) -> bool:
        """Attribute: 'x'"""
        return self._attrs["x"]
    @direct_access.setter
    def direct_access(self,value:bool) -> None:
        """Set Attribute: 'x'"""
        self._attrs["x"] = value
    @property
    def fs_verify(self) -> bool:
        """Attribute: 'V'"""
        return self._attrs["V"]
    @fs_verify.setter
    def fs_verify(self,value:bool) -> None:
        """Set Attribute: 'V'"""
        self._attrs["V"] = value

    def getdict(self) -> dict[str,bool]:
        """Return Raw Dictionary of Attrs
        @retval dict[str,bool] Attr -> Set
        """
        return self._attrs

    def getparam(self,enabled:bool = False) -> list[str]:
        """Return Value as a chattr ready parameter string
        @param bool enabled Which direction to return the output; False = `-`, True = `+`
        @retval list[str] parameters that are (Set/Unset) as a list, for individual application
        """
        output:str = ""
        for k,v in self._attrs.items():
            if v and enabled:
                output += k
            elif not enabled and not v:
                output += k
        return list(f"{output}")

    def __init__(self,file:Path,attrs_raw:typing.Union[str,dict[str,bool]]) -> None:
        self._file = file
        if isinstance(attrs_raw,dict):
            self._attrs = attrs_raw
            return
        map:list[str] = [
            "a","A","c","C","d","D","e","E",
            "F","i","I","j","m","N","P","s",
            "S","t","T","u","x","V"
        ]
        self._attrs = {}
        for v in map:
            if v in attrs_raw:
                self._attrs[v] = True
            else:
                self._attrs[v] = False

    def __eq__(self,other:object) -> bool:
        if not isinstance(other,attr_result):
            raise NotImplementedError()
        comp:dict[str,bool] = other.getdict()
        for k,v in self._attrs.items():
            if comp[k] != v:
                return False
        return True

    def __ne__(self,other:object) -> bool:
        if not isinstance(other,attr_result):
            raise NotImplementedError()
        comp:dict[str,bool] = other.getdict()
        for k,v in self._attrs.items():
            if comp[k] != v:
                return True
        return False
# pylint: enable=too-many-public-methods

def getfattr(path:Path) -> attr_result:
    """Get File Attrs (lsattr) of a file or directory
    @param Path path Path to get attributes for
    @retval attr_result Attribute Object
    """
    if not path.exists():
        raise FileNotFoundError(f"No Such File / Directory: {path.as_posix()}")
    output:str = "_INVALID_"
    with subprocess.Popen(["lsattr",path.as_posix()],stdout=subprocess.PIPE,stderr=subprocess.PIPE) as p:
        p.wait()
        if p.stdout is None:
            raise IOError(f"lsattr {path.as_posix()} did not output any data")
        output = re.sub(r'^((\-{1,}|[aAcCdDeFijmPsStTux]){1,}).*$',r'\1', p.stdout.read().decode("utf-8").split("\n")[0])
    return attr_result(path,output)

def setfattr(attr_obj:attr_result) -> None:
    """Set File Attrs (chattr) of a file or directory
    @param attr_result attr_obj Attribue Object to apply. You can use getfattr() to get an attr_result, and then modify it
    @retval None Nothing
    @note You likely need to be root to use this in most cases, or need to pre-apply sudo/elevation actions.
    """
    if not attr_obj.file.exists():
        raise FileNotFoundError(f"No Such File / Directory: {attr_obj.file.as_posix()}")
    for i in range(0,2):
        enabled:bool = True
        d:str = "+"
        if i == 0:
            enabled = False
            d = "-"
        param:list[str] = attr_obj.getparam(enabled)
        for v in param:
            cmd:list[str] = ["chattr", f"{d}{v}", attr_obj.file.as_posix()]
            with subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE) as p:
                if p.stdout is not None:
                    stdout:bytes = p.stdout.read()
                    if len(stdout) > 0:
                        logging.debug("chattr stdout:")
                        logging.debug(stdout.decode("utf-8").rstrip("\n"))
                if p.stderr is not None:
                    stderr:str = p.stderr.read().decode("utf-8")
                    if len(stderr) > 0 and not re.match(r'^(Must use|Usage:)',stderr):
                        logging.error(' '.join(cmd))
                        logging.error(stderr.rstrip("\n"))
                p.wait()

def getfsha256(path:Path) -> bytes:
    """Read File, get SHA256 of content (as binary content)
    @param Path path Path of File (Must be a file)
    @retval bytes SHA256 Digest of file
    """
    if not path.is_file():
        raise ValueError(f"{path.as_posix()} is not a file, cannot read")
    with open(path,"rb") as f:
        return sha256(f.read()).digest()

def send_wall(message:str) -> None:
    """Post a message via `wall` on the active system
    @param str message Message to post to `wall`
    @retval None Nothing
    """
    with subprocess.Popen(["wall","-n",message],stdout=subprocess.PIPE,stderr=subprocess.PIPE) as p:
        if p.stdout is not None:
            logging.debug("wall stdout:")
            logging.debug(p.stdout.read().decode("utf-8"))
        if p.stderr is not None:
            logging.debug("wall stderr")
            logging.debug(p.stderr.read().decode("utf-8"))
        p.wait()

def scan_dir(target_path:Path,
                callback:typing.Callable[[Path,dict[str,typing.Any]],None],
                callback_data:dict[str,typing.Any],
                exclude_dirs:typing.Optional[list[re.Pattern]] = None,
                exclude_files:typing.Optional[list[re.Pattern]] = None,
                include_files:typing.Optional[list[re.Pattern]] = None
            ) -> None:
    """Scan A Directory, and Execute callback on discovered files, that do not match the exclusions
    @param Path \c target_path Path to Scan for Files
    @param typing.Callable[[Path,dict[str,Any]],None] \c callback Callback function to execute on each file
    @param dict[str,Any] \c callback_data Data to pass to the callback function
    @param list[re.Pattern] \c exclude_dirs (optional) Regex Compiled list of directory patterns to exclude
    @param list[re.Pattern] \c exclude_files (optional) Regex Compiled list of file patterns to exclude
    @param list[re.Pattern] \c include_files (optional) Regex Compiled list of file patterns to include
    """
    files:typing.Generator[Path, None, None] = target_path.glob("*")
    skip:bool = False
    for file in files:
        file_path:Path = Path(file)
        if file_path.is_dir():
            skip = False
            if exclude_dirs is not None:
                for reg in exclude_dirs:
                    if reg.match(file_path.name):
                        skip = True
                        break
            if not skip:
                callback(file_path,callback_data)
                scan_dir(target_path=file_path,callback=callback,callback_data=callback_data,exclude_dirs=exclude_dirs,exclude_files=exclude_files,include_files=include_files)
        if file_path.is_file():
            if include_files is not None:
                skip = True
                for reg in include_files:
                    if reg.match(file_path.name):
                        skip = False
                        break
            if exclude_files is not None:
                skip = False
                for reg in exclude_files:
                    if reg.match(file_path.name):
                        skip = True
                        break
            if not skip:
                callback(file_path,callback_data)

#### CHECKSUM 5710e61a9382365f62b2a86c0d6dcf56d33199d375cd2c7599bea88cbcdafe52
