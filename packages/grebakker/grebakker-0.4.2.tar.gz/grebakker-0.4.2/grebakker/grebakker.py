#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""grebakker - greyrat's backupper for hackers."""
# ===========================================================================
__author__     = "Daniel Krajzewicz"
__copyright__  = "Copyright 2025, Daniel Krajzewicz"
__credits__    = "Daniel Krajzewicz"
__license__    = "GPL"
__version__    = "0.4.2"
__maintainer__ = "Daniel Krajzewicz"
__email__      = "daniel@krajzewicz.de"
__status__     = "Development"
# ===========================================================================
# - https://github.com/dkrajzew/grebakker
# - http://www.krajzewicz.de
# ===========================================================================


# --- imports ---------------------------------------------------------------
import json
import sys
import os
import datetime
import argparse
import configparser
import shutil
import zipfile
import fnmatch
from typing import List, Dict, Any, Union, Generator


# --- class definitions -----------------------------------------------------
class Log:
    """Handles logging of performed actions in CSV or JSON format."""

    def __init__(self, name: str, restart: bool, log_format: str, off: bool) -> None:
        """Initialize the Log object.

        Args:
            name (str): Path to the log file
            restart (bool): If True, overwrites the existing log file
            log_format (str): Format of the log ('csv' or 'json')
            off (bool): If True, disables logging
        """
        self._format = log_format
        self._written = 0
        self._output = None
        self._name = name
        if off:
            return
        mode = "w" if restart else "a"
        self._output = open(name, mode, encoding="utf-8")
        if self._format=="json":
            self._output.write('[\n')

    def write(self, act: str, src: str, dst: str, duration: str) -> None:
        """Write a log entry about a performed action.

        Args:
            act (str): Action performed
            src (str): Source path
            dst (str): Destination path
            duration (str): Duration of the action
        """
        if self._output is None:
            return
        if self._format=="csv":
            self._output.write(f'"{act}";"{src}";"{dst}";"{duration}"\n')
        elif self._format=="json":
            if self._written!=0:
                self._output.write(',\n')
            self._output.write('    {"action": "' + act + '", "src": "' + src + '", "dst": "' + dst + '", "duration": "' + duration + '"}')
        self._output.flush()
        self._written += 1

    def error(self, error: str) -> None:
        """Write a log entry about an error.

        Args:
            error (str): The error occured
        """
        if self._output is None:
            return
        if self._format=="csv":
            self._output.write(f'"{error}"\n')
        elif self._format=="json":
            if self._written!=0:
                self._output.write(',\n')
            self._output.write('    {"error": "' + error + '"}')
        self._output.flush()
        self._written += 1

    def close(self) -> None:
        """Close the log file."""
        if self._output is None:
            return
        if self._format=="json":
            self._output.write('\n]\n')
        self._output.close()


class Grebakker:
    """Perform backup operations."""

    def __init__(self, dest: str, log: Log, verbosity: int):
        """Initialize the Grebakker object.

        Args:
            dest (str): Destination directory for backups
            log (Log): Log object for recording actions
            verbosity (int): Verbosity level for output
        """
        self._dest = dest
        self._log = log
        self._verbosity = verbosity
        self._line_ended = True

    def _action_begin(self, mml_action: str, path: str, level: int) -> datetime.datetime:
        """Report the beginning of an action, return starting time.

        Args:
            mml_action (str): Description of the action
            path (str): Path involved in the action
            level (int): Indentation level

        Returns:
            (datetime.datetime): Start time of the action.
        """
        if self._verbosity>1:
            print(f"{self._i(level+1)}{mml_action} '{path}'... ", end="", flush=True)
            self._line_ended = False
        return datetime.datetime.now()

    def _action_end(self, action: str, path: str, dst: str, level: int, t1: datetime.datetime) -> None:
        """Report the end of an action and logs it.

        Args:
            action (str): Action performed
            path (str): Source path
            dst (str): Destination path
            level (int): Indentation level
            t1 (datetime.datetime): Start time of the action
        """
        t2 = datetime.datetime.now()
        self._log.write(action, path, dst, str(t2-t1))
        if self._verbosity>1:
            print(f"done. ({t2-t1})")
            self._line_ended = True

    def _yield_files(self, src: str, exclude: List[str]) -> Generator:
        """Yield files from the source directory, excluding specified patterns.

        Args:
            src (str): Source directory.
            exclude (List[str]): List of patterns to exclude.

        Yields:
            source_path (str): Relative path to each file
        """
        for root, dirs, files in os.walk(src):
            dirs[:] = [d for d in dirs if d not in exclude]
            for file in files:
                srcf = os.path.relpath(os.path.join(root, file), src)
                use = True
                for e in exclude:
                    if fnmatch.fnmatchcase(srcf, e):
                        use = False
                        break
                if not use:
                    continue
                yield os.path.relpath(os.path.join(root, file), os.path.join(src, ".."))

    def _i(self, level: int) -> str:
        """Return indentation spaces for the given output level.

        Args:
            level (int): Indentation level.

        Returns:
            (str): Indentation spaces
        """
        return ' '*level

    def _destination_exists(self, action: str, src: str, dst: str, level: int) -> bool:
        """Determine the destination path for an action.

        Args:
            action (str): Action being performed
            src (str): Source path
            dst (str): Destination path
            level (int): Indentation level

        Returns:
            (str or None): Destination path or None if the destination file exists.
        """
        if not os.path.exists(dst):
            return False
        self._log.write(action, src, dst, "skipped")
        if self._verbosity>1:
            if not self._line_ended:
                print()
                self._line_ended = True
            print(f"{self._i(level+1)}Skipping '{dst}' - exists.")
        return True


    def copy(self, src_root: str, item: Union[str, Dict[str, str]], dst_root: str, level: int) -> None:
        """Copy files or directories from source to destination.

        Args:
            src_root (str): Root source directory
            item (Union[str, Dict[str, str]]): Item to copy. If dict, may contain 'name' and 'exclude'
            dst_root (str): Root destination directory
            level (int): Reporting level

        Raises:
            FileNotFoundError: If the source path does not exist.
        """
        path = item if isinstance(item, str) else item["name"]
        src = os.path.join(src_root, path)
        if not os.path.exists(src):
            self._log.error(f"file/folder '{src}' to copy does not exist")
            raise FileNotFoundError(f"file/folder '{src}' to copy does not exist")
        dst = os.path.join(dst_root, path)
        if os.path.isfile(src):
            if self._destination_exists("copy", src, dst, level):
                return
            t1 = self._action_begin("Copying", src, level)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            self._action_end("copy", src, dst, level, t1)
            return
        exclude = [] if "exclude" not in item else item["exclude"]
        exclude = [exclude] if isinstance(exclude, str) else exclude
        t1 = self._action_begin("Copying", src, level)
        for file in self._yield_files(src, list(exclude)):
            fsrc = os.path.abspath(os.path.join(src, "..", file))
            fdst = os.path.abspath(os.path.join(dst, "..", file))
            if self._destination_exists("copy", os.path.join(src, file), fdst, level):
                continue
            os.makedirs(os.path.dirname(fdst), exist_ok=True)
            shutil.copy2(fsrc, fdst)
        self._action_end("copy", src, dst, level, t1)


    def compress(self, root: str, item: Union[str, Dict[str, str]], dst_root: str, level: int) -> None:
        """Compress files or directories into a ZIP archive.

        Args:
            root (str): Root source directory
            item (Union[str, Dict[str, str]]): Item to compress. If dict, may contain 'name' and 'exclude'
            dst_root (str): Root destination directory
            level (int): Reporting level

        Raises:
            FileNotFoundError: If the source path does not exist
        """
        path = item if isinstance(item, str) else item["name"]
        src = os.path.join(root, path)
        if not os.path.exists(src):
            self._log.error(f"file/folder '{src}' to compress does not exist")
            raise FileNotFoundError(f"file/folder '{src}' to compress does not exist")
        dst = os.path.join(dst_root, path) + ".zip"
        if self._destination_exists("compress", src, dst, level):
            return
        exclude = [] if "exclude" not in item else item["exclude"]
        exclude = [exclude] if isinstance(exclude, str) else exclude
        t1 = self._action_begin("Compressing", src, level)
        zipf = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED, compresslevel=9)
        if os.path.isfile(src):
            dstf = os.path.relpath(src, os.path.join(src, '..'))
            zipf.write(src, dstf)
        else:
            for file in self._yield_files(src, list(exclude)):
                fsrc = os.path.join(src, "..", file)
                dstf = os.path.relpath(os.path.join(root, file), os.path.join(src, '..'))
                zipf.write(fsrc, dstf)
        zipf.close()
        self._action_end("compress", src, dst, level, t1)


    def decompress(self, root: str, item: Union[str, Dict[str, str]], dst_root: str, level: int) -> None:
        """Decompress ZIP archives.

        Args:
            root (str): Root source directory
            item (Union[str, Dict[str, str]]): Item to compress. If dict, may contain 'name' and 'exclude'
            dst_root (str): Root destination directory
            level (int): Reporting level

        Raises:
            FileNotFoundError: If the source path does not exist
        """
        path = item if isinstance(item, str) else item["name"]
        src = os.path.join(root, path) + ".zip"
        if not os.path.exists(src):
            self._log.error(f"file/folder '{src}' to decompress does not exist")
            raise FileNotFoundError(f"file/folder '{src}' to decompress does not exist")
        dst = dst_root#os.path.join(dst_root, path)
        #if self._destination_exists("decompress", src, dst, level):
        #    return
        t1 = self._action_begin("Decompressing", src, level)
        with zipfile.ZipFile(src, 'r') as zip_ref:
            zip_ref.extractall(dst)
        self._action_end("decompress", src, dst, level, t1)


    def run(self, action: str, root: str, level: int=0) -> None:
        """Perform an action.

        Args:
            action (str): The action to perform
            root (str): Root source directory
            level (int): Reporting level
        """
        if action not in ["backup", "restore"]:
            raise ValueError(f"unkown action '{action}'")
        # init
        if self._verbosity>0:
            print(f"{self._i(level)}Processing '{root}'...")
            self._line_ended = True
        definition = None
        with open(os.path.join(root, "grebakker.json"), encoding="utf-8") as fd:
            definition = json.load(fd)
        dst_path = os.path.join(self._dest, definition["destination"])
        os.makedirs(dst_path, exist_ok=True)
        # copy
        for path in [] if "copy" not in definition else definition["copy"]:
            self.copy(root, path, dst_path, level)
        # compress
        for path in [] if "compress" not in definition else definition["compress"]:
            if action=="backup":
                self.compress(root, path, dst_path, level)
            elif action=="restore":
                self.decompress(root, path, dst_path, level)
        # subfolders
        for sub in [] if "subfolders" not in definition else definition["subfolders"]:
            path = sub if type(sub)==str else sub["name"]
            src = os.path.join(root, path)
            if not os.path.exists(src):
                self._log.error(f"file/folder '{src}' to recurse into does not exist")
                raise FileNotFoundError(f"file/folder '{src}' to recurse into does not exist")
            dst = os.path.join(dst_path, path)
            # !!! add an option for what to do
            #if self._destination_exists("sub", src, dst, level):
            #    pass
            self._log.write("sub", src, dst, "0:00:00")
            self.run(action, os.path.join(root, sub), level+1)
        shutil.copy2(os.path.join(root, "grebakker.json"), dst_path)
        if level==0:
            self._log.close()
            if self._log._written!=0:
                shutil.move(self._log._name, os.path.join(dst_path, self._log._name))



# --- functions -------------------------------------------------------------
def main(arguments: List[str] = []) -> int:
    """Run grebaker using the given parameters.

    Args:
        arguments (List[str]): A list of command line arguments

    Returns:
        (int): The exit code (0 for success)
    """
    # parse options
    # https://stackoverflow.com/questions/3609852/which-is-the-best-way-to-allow-configuration-options-be-overridden-at-the-comman
    defaults = {}
    conf_parser = argparse.ArgumentParser(prog='grebakker', add_help=False)
    conf_parser.add_argument("-c", "--config", metavar="FILE", help="Reads the named configuration file")
    args, remaining_argv = conf_parser.parse_known_args(arguments)
    if args.config is not None:
        if not os.path.exists(args.config):
            print ("grebakker: error: configuration file '%s' does not exist" % str(args.config), file=sys.stderr)
            raise SystemExit(2)
        config = configparser.ConfigParser()
        config.read([args.config])
        defaults.update(dict(config.items("grebakker")))
    parser = argparse.ArgumentParser(prog='grebakker', parents=[conf_parser],
                                     description="greyrat's backupper for hackers",
                                     epilog='(c) Daniel Krajzewicz 2025')
    parser.add_argument("action" if "action" not in defaults else "--action")
    parser.add_argument("destination" if "destination" not in defaults else "--destination")
    parser.add_argument("definition" if "definition" not in defaults else "--definition")
    parser.add_argument('--version', action='version', version='%(prog)s 0.4.2')
    parser.add_argument('--continue', dest="cont", action="store_true", help="Continues a stopped backup.")
    parser.add_argument('--log-name', default="grebakker_log.csv", help="Change logfile name (default: 'grebakker_log.csv').")
    parser.add_argument('--log-restart', action="store_true", help="An existing logfile will be removed.")
    parser.add_argument('--log-off', action="store_true", help="Does not generate a log file.")
    parser.add_argument('--log-format', default="csv", choices=['csv', 'json'], help="Select log format to use ['csv', 'json']")
    """
    parser.add_argument('--compress-max-size', default="2g", help="Defines maximum archive size (default: 2g).")
    parser.add_argument('--compress-max-size-abort', action="store_true", help="Stop when an archive is bigger than the maximum size.")
    parser.add_argument('--compress-max-threads', type=int, default=1, help="Defines maximum thread number.")
    """
    #parser.add_argument('-e', '--excluded-log', metavar="FILE", default=None, help="Writes excluded files and folders to FILE.")
    parser.add_argument('-v', '--verbose', action='count', default=0, help="Increases verbosity level (up to 2).") # https://stackoverflow.com/questions/6076690/verbose-level-with-argparse-and-multiple-v-options
    parser.set_defaults(**defaults)
    args = parser.parse_args(remaining_argv)
    verbosity = int(args.verbose)
    # check
    errors = []
    if args.action not in ["backup", "restore"]:
        errors.append(f"unkown action '{args.action}'")
    if len(errors)!=0:
        for e in errors:
            print(f"grebakker: error: {e}", file=sys.stderr)
        raise SystemExit(2)
    #
    if os.path.exists(args.log_name):
        if not args.cont and not args.log_restart:
            print("grebakker: error: a log file exists, but it is not defined whether to restart or to continue.", file=sys.stderr)
            raise SystemExit(2)
        if args.cont:
            print("A log file exists; contents will be appended.")
        if args.log_restart:
            print("The existing log file will be replaced by new contents.")
    if not os.path.exists(args.destination):
        os.makedirs(args.destination, exist_ok=True)
    #
    ret = 0
    if verbosity>0:
        print("Starting...")
    t1 = datetime.datetime.now()
    log = Log(args.log_name, args.log_restart, args.log_format, args.log_off)
    grebakker = Grebakker(args.destination, log, verbosity)
    try:
        grebakker.run(args.action, args.definition)
    except FileNotFoundError as e:
        print(f"grebakker: error: {e}.", file=sys.stderr)
        ret = 2
    t2 = datetime.datetime.now()
    if verbosity>0 and ret==0:
        print(f"Completed after {(t2-t1)}")
    return ret


def script_run() -> int:
    """Execute from command line."""
    sys.exit(main(sys.argv[1:])) # pragma: no cover


# -- main check
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:])) # pragma: no cover
