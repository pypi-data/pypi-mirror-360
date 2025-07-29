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

DEFINITION2 = """{
    "destination": "d/",
    "copy": [ 
        "subfolder2"
    ]
}
"""

DEFINITION3A = """{
    "destination": "d/",
    "subfolders": [ "subfolder1" ]
}
"""
DEFINITION3B = """{
    "destination": "d/subfolder1",
    "compress": [ 
        { "name": "subfolder11" },
        { "name": "subfolder12" }
    ]
}
"""

# --- test functions ----------------------------------------------------------
def test_main_skip_clean_v2(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION1, "set1", tmp_path)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1"), "-v", "-v"])
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


def test_main_skip_doc1_exists_v2(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION1, "set1", tmp_path, skipped=["document1.txt"])
    os.makedirs(os.path.join(dst, "d"))
    shutil.copy(tmp_path / "set1" / "document1.txt", os.path.join(dstroot, "d", "document1.txt"))
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1"), "-v", "-v"])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set1'...
 Skipping '<DIR>/backup/d/document1.txt' - exists.
 Copying '<DIR>/set1/something_else1.csv'... done. (<DUR>)
 Compressing '<DIR>/set1/subfolder'... done. (<DUR>)
Completed after <DUR>
"""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION1)


def test_main_skip_archive1_exists_v2(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION1, "set1", tmp_path, skipped=["subfolder"])
    os.makedirs(os.path.join(dstroot, "d"))
    shutil.copy(os.path.join(TEST_PATH, "subfolder.zip"), os.path.join(dstroot, "d", "subfolder.zip"))
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set1"), "-v", "-v"])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set1'...
 Copying '<DIR>/set1/document1.txt'... done. (<DUR>)
 Copying '<DIR>/set1/something_else1.csv'... done. (<DUR>)
 Skipping '<DIR>/backup/d/subfolder.zip' - exists.
Completed after <DUR>
"""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION1)


def test_main_skip_folderfile_exists__plain_v2(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION2, "set2", tmp_path)#, skipped=["subfolder"])
    os.makedirs(os.path.join(dstroot, "d"))
    #shutil.copy(os.path.join(TEST_PATH, "subfolder.zip"), os.path.join(dstroot, "d", "subfolder.zip"))
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-v", "-v"])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Copying '<DIR>/set2/subfolder2'... done. (<DUR>)
Completed after <DUR>
"""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION2)


def test_main_skip_folderfile_exists__exists_v2(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION2, "set2", tmp_path, skipped=["document2.txt"])
    #shutil.copy(os.path.join(TEST_PATH, "subfolder.zip"), os.path.join(dstroot, "d", "subfolder.zip"))
    os.makedirs(os.path.join(dstroot, "d", "subfolder2"))
    shutil.copy(os.path.join(TEST_PATH, "set2", "subfolder2", "document2.txt"), os.path.join(dstroot, "d", "subfolder2", "document2.txt"))
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-v", "-v"])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Copying '<DIR>/set2/subfolder2'... 
 Skipping '<DIR>/backup/d/subfolder2/document2.txt' - exists.
done. (<DUR>)
Completed after <DUR>
"""
    check_generated(tmp_path, actions, dst, "csv", log_head='"copy";"<DIR>/set2/subfolder2/subfolder2/document2.txt";"<DIR>/backup/d/subfolder2/document2.txt";"skipped"\n')
    check_def(tmp_path, DEFINITION2)


def test_main_skip_subfolder_exists__plain_v2(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION3A, "set2", tmp_path, add_defs={"subfolder1": DEFINITION3B})
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-v", "-v"])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Processing '<DIR>/set2/subfolder1'...
  Compressing '<DIR>/set2/subfolder1/subfolder11'... done. (<DUR>)
  Compressing '<DIR>/set2/subfolder1/subfolder12'... done. (<DUR>)
Completed after <DUR>
"""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION3A)
    #check_def(tmp_path / "subfolder1", DEFINITION3B)


def test_main_skip_subfolder_exists__exists_v2(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION3A, "set2", tmp_path, add_defs={"subfolder1": DEFINITION3B})
    os.makedirs(os.path.join(dstroot, "d", "subfolder1"))
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-v", "-v"])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Processing '<DIR>/set2/subfolder1'...
  Compressing '<DIR>/set2/subfolder1/subfolder11'... done. (<DUR>)
  Compressing '<DIR>/set2/subfolder1/subfolder12'... done. (<DUR>)
Completed after <DUR>
"""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION3A)
    #check_def(tmp_path / "subfolder1", DEFINITION3B)
