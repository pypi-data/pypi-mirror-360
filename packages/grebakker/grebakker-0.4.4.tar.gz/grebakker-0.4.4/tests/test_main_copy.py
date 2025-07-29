#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""grebakker - Tests for the copying files."""
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
        "something_else1.csv",
        "subfolder/document2.txt",
        "subfolder/something_else2.csv"
    ]
}
"""

DEFINITION2 = """{
    "destination": "d/",
    "copy": [ 
        "document1.txt",
        "something_else1.csv",
        "subfolder"
    ]
}
"""

DEFINITION3 = """{
    "destination": "d/",
    "copy": [ 
        { "name": "document1.txt" },
        { "name": "something_else1.csv" },
        { "name": "subfolder" }
    ]
}
"""

# --- test functions ----------------------------------------------------------
def test_main_copy_files1_v0(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION1, "set1", tmp_path)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1")])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pname(captured.out) == ""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION1)

def test_main_copy_files1_v1(capsys, tmp_path):
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

def test_main_copy_files1_v2(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION1, "set1", tmp_path)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1"), "-vv"])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set1'...
 Copying '<DIR>/set1/document1.txt'... done. (<DUR>)
 Copying '<DIR>/set1/something_else1.csv'... done. (<DUR>)
 Copying '<DIR>/set1/subfolder/document2.txt'... done. (<DUR>)
 Copying '<DIR>/set1/subfolder/something_else2.csv'... done. (<DUR>)
Completed after <DUR>
"""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION1)


def test_main_copy_files2_v0(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION2, "set1", tmp_path)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1")])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pname(captured.out) == ""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION2)

def test_main_copy_files2_v1(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION2, "set1", tmp_path) # !!! should include files in subfolders
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
    check_def(tmp_path, DEFINITION2)

def test_main_copy_files2_v2(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION2, "set1", tmp_path)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1"), "-vv"])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set1'...
 Copying '<DIR>/set1/document1.txt'... done. (<DUR>)
 Copying '<DIR>/set1/something_else1.csv'... done. (<DUR>)
 Copying '<DIR>/set1/subfolder'... done. (<DUR>)
Completed after <DUR>
"""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION2)


def test_main_copy_files3_v0(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION3, "set1", tmp_path)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1")])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pname(captured.out) == ""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION3)

def test_main_copy_files3_v1(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION3, "set1", tmp_path) # !!! should include files in subfolders
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
    check_def(tmp_path, DEFINITION3)

def test_main_copy_files3_v2(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION3, "set1", tmp_path)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1"), "-vv"])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set1'...
 Copying '<DIR>/set1/document1.txt'... done. (<DUR>)
 Copying '<DIR>/set1/something_else1.csv'... done. (<DUR>)
 Copying '<DIR>/set1/subfolder'... done. (<DUR>)
Completed after <DUR>
"""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION3)