#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""grebakker - Tests for the main method."""
# =============================================================================
__author__     = "Daniel Krajzewicz"
__copyright__  = "Copyright 2025, Daniel Krajzewicz"
__credits__    = ["Daniel Krajzewicz"]
__license__    = "GPL"
__version__    = "0.4.4"
__maintainer__ = "Daniel Krajzewicz"
__email__      = "daniel@krajzewicz.de"
__status__     = "Development"
# =============================================================================
# - https://github.com/dkrajzew/degrotesque
# - http://www.krajzewicz.de/docs/degrotesque/index.html
# - http://www.krajzewicz.de
# =============================================================================


# --- imports -----------------------------------------------------------------
import sys
import os
sys.path.append(os.path.join(os.path.split(__file__)[0], "..", "grebakker"))
import grebakker



# --- helper functions --------------------------------------------------------
def patch(string):
    return string.replace("__main__.py", "degrotesque").replace("pytest", "degrotesque").replace("optional arguments", "options")



# --- test functions ----------------------------------------------------------
def test_main_empty1(capsys):
    """Test behaviour if no arguments are given"""
    try:
        ret = grebakker.main([])
        assert False # pragma: no cover
    except SystemExit as e:
        assert type(e)==type(SystemExit())
        assert e.code==2
    captured = capsys.readouterr()
    assert patch(captured.err) == """usage: grebakker [-h] [-c FILE] [--version] [--continue] [--log-name LOG_NAME]
                 [--log-restart] [--log-off] [--log-format {csv,json}] [-v]
                 action destination definition
grebakker: error: the following arguments are required: action, destination, definition
"""
    assert patch(captured.out) == ""


def test_main_empty2(capsys):
    """Test behaviour if no arguments are given"""
    try:
        ret = grebakker.main()
        assert False # pragma: no cover
    except SystemExit as e:
        assert type(e)==type(SystemExit())
        assert e.code==2
    captured = capsys.readouterr()
    assert patch(captured.err) == """usage: grebakker [-h] [-c FILE] [--version] [--continue] [--log-name LOG_NAME]
                 [--log-restart] [--log-off] [--log-format {csv,json}] [-v]
                 action destination definition
grebakker: error: the following arguments are required: action, destination, definition
"""
    assert patch(captured.out) == ""


def test_main_help(capsys):
    """Test behaviour when help is wished"""
    try:
        grebakker.main(["--help"])
        assert False # pragma: no cover
    except SystemExit as e:
        assert type(e)==type(SystemExit())
        assert e.code==0
    captured = capsys.readouterr()
    assert patch(captured.out) == """usage: grebakker [-h] [-c FILE] [--version] [--continue] [--log-name LOG_NAME]
                 [--log-restart] [--log-off] [--log-format {csv,json}] [-v]
                 action destination definition

greyrat's backupper for hackers

positional arguments:
  action
  destination
  definition

options:
  -h, --help            show this help message and exit
  -c FILE, --config FILE
                        Reads the named configuration file
  --version             show program's version number and exit
  --continue            Continues a stopped backup.
  --log-name LOG_NAME   Change logfile name (default: 'grebakker_log.csv').
  --log-restart         An existing logfile will be removed.
  --log-off             Does not generate a log file.
  --log-format {csv,json}
                        Select log format to use ['csv', 'json']
  -v, --verbose         Increases verbosity level (up to 2).

(c) Daniel Krajzewicz 2025
"""
    assert captured.err == ""


def test_main_version(capsys):
    """Test behaviour when version information is wished"""
    try:
        grebakker.main(["--version"])
        assert False # pragma: no cover
    except SystemExit as e:
        assert type(e)==type(SystemExit())
        assert e.code==0
    captured = capsys.readouterr()
    assert patch(captured.out) == """grebakker 0.4.4
"""
    assert patch(captured.err) == ""

