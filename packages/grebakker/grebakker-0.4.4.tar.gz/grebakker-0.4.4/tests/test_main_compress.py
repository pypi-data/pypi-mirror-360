#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""grebakker - Tests for compressing folders."""
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
    "compress": [ 
        { "name": "subfolder" }
    ]
}
"""

DEFINITION2 = """{
    "destination": "d/",
    "compress": [ 
        "document1.txt"
    ]
}
"""

DEFINITION3 = """{
    "destination": "d/",
    "compress": [ 
        "subfolder"
    ]
}
"""


# --- test functions ----------------------------------------------------------
def test_main_compress_subfolder_map_v0(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION1, "set1", tmp_path)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1")])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pname(captured.out) == ""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION1)

def test_main_compress_subfolder_map_v1(capsys, tmp_path):
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

def test_main_compress_subfolder_map_v2(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION1, "set1", tmp_path)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1"), "-vv"])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set1'...
 Compressing '<DIR>/set1/subfolder'... done. (<DUR>)
Completed after <DUR>
"""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION1)


def test_main_compress_file_v0(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION2, "set1", tmp_path)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1")])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pname(captured.out) == ""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION2)

def test_main_compress_file_v1(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION2, "set1", tmp_path)
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

def test_main_compress_file_v2(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION2, "set1", tmp_path)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1"), "-vv"])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set1'...
 Compressing '<DIR>/set1/document1.txt'... done. (<DUR>)
Completed after <DUR>
"""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION2)


def test_main_compress_subfolder_plain_v0(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION3, "set1", tmp_path)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1")])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pname(captured.out) == ""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION3)

def test_main_compress_subfolder_plain_v1(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION3, "set1", tmp_path)
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

def test_main_compress_subfolder_plain_v2(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION3, "set1", tmp_path)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1"), "-vv"])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set1'...
 Compressing '<DIR>/set1/subfolder'... done. (<DUR>)
Completed after <DUR>
"""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION3)
