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
import shutil
sys.path.append(os.path.join(os.path.split(__file__)[0], "..", "grebakker"))
import grebakker
from util import pname, TEST_PATH, check_def, prepare, check_generated, pdirtime


# --- definitions -------------------------------------------------------------
DEFINITION1A = """{
    "destination": "d/",
    "copy": [ 
        "document.txt",
        "something_else.csv"
    ],
    "compress": [ 
        "subfolder2"
    ],
    "subfolders": [ "subfolder1" ]
}
"""
DEFINITION1B = """{
    "destination": "d/subfolder1",
    "compress": [ 
        "subfolder11",
        "subfolder12"
    ]
}
"""

DEFINITION2A = """{
    "destination": "d/",
    "copy": [ 
        "document.txt",
        "something_else.csv"
    ],
    "compress": [ 
        "subfolder2"
    ],
    "subfolders": [ "subfolder1" ]
}
"""
DEFINITION2B = """{
    "destination": "d/subfolder1",
    "compress": [ 
        { "name": "subfolder11", "exclude": ["*.csv"] },
        { "name": "subfolder12", "exclude": ["*.txt"] }
    ]
}
"""

DEFINITION3 = """{
    "destination": "d/",
    "copy": [ 
        "document.txt",
        "something_else.csv"
    ],
    "compress": [ 
        { "name": "subfolder1", "exclude" : [ "subfolder12" ] },
        "subfolder2"
    ]
}
"""

DEFINITION4 = """{
    "destination": "d/",
    "copy": [ 
        { "name": "subfolder1", "exclude" : [ "subfolder12" ] }
    ]
}
"""

# --- test functions ----------------------------------------------------------
def test_main_plain_v0(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION1A, "set2", tmp_path, add_defs={"subfolder1": DEFINITION1B})
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2")])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pname(captured.out) == ""
    #print(actions)
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION1A)

def test_main_plain_v1(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION1A, "set2", tmp_path, add_defs={"subfolder1": DEFINITION1B})
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-v"])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Processing '<DIR>/set2/subfolder1'...
Completed after <DUR>
"""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION1A)

def test_main_plain_v2(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION1A, "set2", tmp_path, add_defs={"subfolder1": DEFINITION1B})
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-v", "-v"])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Copying '<DIR>/set2/document.txt'... done. (<DUR>)
 Copying '<DIR>/set2/something_else.csv'... done. (<DUR>)
 Compressing '<DIR>/set2/subfolder2'... done. (<DUR>)
 Processing '<DIR>/set2/subfolder1'...
  Compressing '<DIR>/set2/subfolder1/subfolder11'... done. (<DUR>)
  Compressing '<DIR>/set2/subfolder1/subfolder12'... done. (<DUR>)
Completed after <DUR>
"""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION1A)


def test_main_exclude_compress_files_in_folder1_v2(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION2A, "set2", tmp_path, add_defs={"subfolder1": DEFINITION2B})
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-v", "-v"])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Copying '<DIR>/set2/document.txt'... done. (<DUR>)
 Copying '<DIR>/set2/something_else.csv'... done. (<DUR>)
 Compressing '<DIR>/set2/subfolder2'... done. (<DUR>)
 Processing '<DIR>/set2/subfolder1'...
  Compressing '<DIR>/set2/subfolder1/subfolder11'... done. (<DUR>)
  Compressing '<DIR>/set2/subfolder1/subfolder12'... done. (<DUR>)
Completed after <DUR>
"""
    check_generated(tmp_path, actions, dst, "csv", 
        testfiles={"subfolder11": "subfolder11_nocsv.zip", "subfolder12": "subfolder12_notxt.zip"})
    check_def(tmp_path, DEFINITION2A)


def test_main_exclude_compress_folder_in_folder1_v2(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION3, "set2", tmp_path)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-v", "-v"])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Copying '<DIR>/set2/document.txt'... done. (<DUR>)
 Copying '<DIR>/set2/something_else.csv'... done. (<DUR>)
 Compressing '<DIR>/set2/subfolder1'... done. (<DUR>)
 Compressing '<DIR>/set2/subfolder2'... done. (<DUR>)
Completed after <DUR>
"""
    check_generated(tmp_path, actions, dst, "csv", testfiles={"subfolder1": "subfolder1_nosubfolder12.zip"})
    check_def(tmp_path, DEFINITION3)


def test_main_exclude_copy_folder_in_folder1_v2(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION4, "set2", tmp_path)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-v", "-v"])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Copying '<DIR>/set2/subfolder1'... done. (<DUR>)
Completed after <DUR>
"""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION4)

