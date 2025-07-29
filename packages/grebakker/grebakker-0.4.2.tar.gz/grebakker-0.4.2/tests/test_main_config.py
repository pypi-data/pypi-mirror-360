#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""grebakker - Tests for continuing backups."""
# =============================================================================
__author__     = "Daniel Krajzewicz"
__copyright__  = "Copyright 2025, Daniel Krajzewicz"
__credits__    = ["Daniel Krajzewicz"]
__license__    = "GPL"
__version__    = "0.4.2"
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
import shutil
from pathlib import Path
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
def test_main_plain_v0(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION1, "set1", tmp_path)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1") ])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pname(captured.out) == ""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION1)


def test_main_config_missing(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION1, "set1", tmp_path)
    try:
        ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1"), "-c", "grebakker.cfg" ])
        assert False # pragma: no cover
    except SystemExit as e:
        assert type(e)==type(SystemExit())
        assert e.code==2
    captured = capsys.readouterr()
    assert pname(captured.err) == """grebakker: error: configuration file 'grebakker.cfg' does not exist
"""
    assert pname(captured.out) == ""


def test_main_config_v0(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION1, "set1", tmp_path)
    Path(tmp_path / "grebakker.cfg").write_text("[grebakker]\n")
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1"), "-c", "grebakker.cfg" ])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pname(captured.out) == ""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION1)

def test_main_config_v1(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION1, "set1", tmp_path)
    Path(tmp_path / "grebakker.cfg").write_text("[grebakker]\nverbose=1\n")
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1"), "-c", "grebakker.cfg"])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set1'...
Completed after <DUR>
"""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION1)

def test_main_config_v2(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION1, "set1", tmp_path)
    Path(tmp_path / "grebakker.cfg").write_text("[grebakker]\nverbose=2\n")
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1"), "-c", "grebakker.cfg"])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set1'...
 Copying '<DIR>/set1/document1.txt'... done. (<DUR>)
 Copying '<DIR>/set1/something_else1.csv'... done. (<DUR>)
 Compressing '<DIR>/set1/subfolder'... done. (<DUR>)
Completed after <DUR>
"""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION1)
