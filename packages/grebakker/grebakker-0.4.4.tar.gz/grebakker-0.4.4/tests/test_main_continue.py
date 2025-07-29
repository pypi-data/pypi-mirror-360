#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""grebakker - Tests for continuing backups."""
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
from util import pname, TEST_PATH, check_def, prepare, check_generated, pdirtime


# --- definitions -------------------------------------------------------------
DEFINITION1 = """{
    "destination": "d/",
    "copy": [ 
        "document1.txt",
        "something_else1.csv"
    ],
    "compress": [ 
        { "name": "subfolder" }
    ]
}
"""


# --- test functions ----------------------------------------------------------
def test_main_continue_clean_v0(capsys, tmp_path):
    """Test behaviour if no arguments are given"""
    actions, dstroot, dst = prepare(DEFINITION1, "set1", tmp_path)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1")])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pname(captured.out) == ""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION1)

def test_main_continue_clean_v1(capsys, tmp_path):
    """Test behaviour if no arguments are given"""
    actions, dstroot, dst = prepare(DEFINITION1, "set1", tmp_path)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1"), "-v"])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set1'...
Completed after <DUR>
"""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION1)


def test_main_continue_log_exists_plain_v0(capsys, tmp_path):
    """Test behaviour if no arguments are given"""
    actions, dstroot, dst = prepare(DEFINITION1, "set1", tmp_path)
    (tmp_path / "grebakker_log.csv").write_text("initial content\n") # generate existing log file
    os.chdir(tmp_path) # !!!
    try:
        grebakker.main(["backup", dstroot, str(tmp_path / "set1")])
        assert False # pragma: no cover
    except SystemExit as e:
        assert type(e)==type(SystemExit())
        assert e.code==2
    captured = capsys.readouterr()
    assert pname(captured.err) == """grebakker: error: a log file exists, but it is not defined whether to restart or to continue.
"""
    assert pname(captured.out) == ""
    #check_generated(tmp_path, actions, "csv")
    #check_def(tmp_path, DEFINITION1)

def test_main_continue_log_exists_plain_v1(capsys, tmp_path):
    """Test behaviour if no arguments are given"""
    actions, dstroot, dst = prepare(DEFINITION1, "set1", tmp_path)
    (tmp_path / "grebakker_log.csv").write_text("initial content\n") # generate existing log file
    os.chdir(tmp_path) # !!!
    try:
        grebakker.main(["backup", dstroot, str(tmp_path / "set1"), "-v"])
        assert False # pragma: no cover
    except SystemExit as e:
        assert type(e)==type(SystemExit())
        assert e.code==2
    captured = capsys.readouterr()
    assert pname(captured.err) == """grebakker: error: a log file exists, but it is not defined whether to restart or to continue.
"""
    assert pname(captured.out) == ""
    #check_generated(tmp_path, actions, "csv")
    #check_def(tmp_path, DEFINITION1)


def test_main_continue_log_exists_continue_v0(capsys, tmp_path):
    """Test behaviour if no arguments are given"""
    actions, dstroot, dst = prepare(DEFINITION1, "set1", tmp_path)
    (tmp_path / "grebakker_log.csv").write_text("initial content\n") # generate existing log file
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1"), "--continue"])
    assert ret == 0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pname(captured.out) == """A log file exists; contents will be appended.
"""
    check_generated(tmp_path, actions, dst, "csv", log_head="initial content\n")
    check_def(tmp_path, DEFINITION1)

def test_main_continue_log_exists_continue_v1(capsys, tmp_path):
    """Test behaviour if no arguments are given"""
    actions, dstroot, dst = prepare(DEFINITION1, "set1", tmp_path)
    (tmp_path / "grebakker_log.csv").write_text("initial content\n") # generate existing log file
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1"), "--continue", "-v"])
    assert ret == 0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pdirtime(captured.out, tmp_path) == """A log file exists; contents will be appended.
Starting...
Processing '<DIR>/set1'...
Completed after <DUR>
"""
    check_generated(tmp_path, actions, dst, "csv", log_head="initial content\n")
    check_def(tmp_path, DEFINITION1)

def test_main_continue_log_exists_continue_csv(capsys, tmp_path):
    """Test behaviour if no arguments are given"""
    actions, dstroot, dst = prepare(DEFINITION1, "set1", tmp_path)
    (tmp_path / "grebakker_log.csv").write_text("initial content\n") # generate existing log file
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1"), "--continue", "--log-format", "csv"])
    assert ret == 0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pname(captured.out) == """A log file exists; contents will be appended.
"""
    check_generated(tmp_path, actions, dst, "csv", log_head="initial content\n")
    check_def(tmp_path, DEFINITION1)

def test_main_continue_log_exists_continue_json(capsys, tmp_path):
    """Test behaviour if no arguments are given"""
    actions, dstroot, dst = prepare(DEFINITION1, "set1", tmp_path)
    (tmp_path / "grebakker_log.csv").write_text("initial content\n") # generate existing log file
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1"), "--continue", "--log-format", "json"])
    assert ret == 0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pname(captured.out) == """A log file exists; contents will be appended.
"""
    check_generated(tmp_path, actions, dst, "json", log_head="initial content\n")
    check_def(tmp_path, DEFINITION1)


def test_main_continue_log_exists_restart_v0(capsys, tmp_path):
    """Test behaviour if no arguments are given"""
    actions, dstroot, dst = prepare(DEFINITION1, "set1", tmp_path)
    (tmp_path / "grebakker_log.csv").write_text("initial content\n") # generate existing log file
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1"), "--log-restart"])
    assert ret == 0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pname(captured.out) == """The existing log file will be replaced by new contents.
"""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION1)

def test_main_continue_log_exists_restart_v1(capsys, tmp_path):
    """Test behaviour if no arguments are given"""
    actions, dstroot, dst = prepare(DEFINITION1, "set1", tmp_path)
    (tmp_path / "grebakker_log.csv").write_text("initial content\n") # generate existing log file
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1"), "--log-restart", "-v"])
    assert ret == 0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pdirtime(captured.out, tmp_path) == """The existing log file will be replaced by new contents.
Starting...
Processing '<DIR>/set1'...
Completed after <DUR>
"""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION1)
