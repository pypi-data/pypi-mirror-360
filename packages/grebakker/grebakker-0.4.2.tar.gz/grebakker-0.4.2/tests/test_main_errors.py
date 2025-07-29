#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""grebakker - Tests for error handling in the main method."""
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


DEFINITION1 = """{
    "destination": "d/",
    "copy": [ 
        "document.txt",
        "something_else.csv",
        "subfolder1",
        "subfolder2"
    ]
}
"""

DEFINITION2 = """{
    "destination": "d/",
    "compress": [ 
        "document.txt",
        "subfolder1",
        "subfolder2"
    ]
}
"""

DEFINITION3A = """{
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
DEFINITION3B = """{
    "destination": "d/subfolder1",
    "compress": [ 
        "subfolder11",
        "subfolder12"
    ]
}
"""


# --- helper functions --------------------------------------------------------
def patch(string):
    return string.replace("__main__.py", "degrotesque").replace("pytest", "degrotesque").replace("optional arguments", "options").replace("choose from 'csv', 'json'", "choose from csv, json")



# --- test functions ----------------------------------------------------------
def test_main_missing3(capsys):
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

def test_main_missing2(capsys):
    try:
        ret = grebakker.main(["foo"])
        assert False # pragma: no cover
    except SystemExit as e:
        assert type(e)==type(SystemExit())
        assert e.code==2
    captured = capsys.readouterr()
    assert patch(captured.err) == """usage: grebakker [-h] [-c FILE] [--version] [--continue] [--log-name LOG_NAME]
                 [--log-restart] [--log-off] [--log-format {csv,json}] [-v]
                 action destination definition
grebakker: error: the following arguments are required: destination, definition
"""
    assert patch(captured.out) == ""

def test_main_missing1(capsys):
    try:
        ret = grebakker.main(["foo", "bar"])
        assert False # pragma: no cover
    except SystemExit as e:
        assert type(e)==type(SystemExit())
        assert e.code==2
    captured = capsys.readouterr()
    assert patch(captured.err) == """usage: grebakker [-h] [-c FILE] [--version] [--continue] [--log-name LOG_NAME]
                 [--log-restart] [--log-off] [--log-format {csv,json}] [-v]
                 action destination definition
grebakker: error: the following arguments are required: definition
"""
    assert patch(captured.out) == ""


def test_main_unknown_action(capsys):
    try:
        ret = grebakker.main(["foo", "bar", "boo"])
        assert False # pragma: no cover
    except SystemExit as e:
        assert type(e)==type(SystemExit())
        assert e.code==2
    captured = capsys.readouterr()
    assert patch(captured.err) == """grebakker: error: unkown action 'foo'
"""
    assert patch(captured.out) == ""


def test_main_unknown_logformat(capsys):
    try:
        ret = grebakker.main(["backup", "bar", "boo", "--log-format", "foo"])
        assert False # pragma: no cover
    except SystemExit as e:
        assert type(e)==type(SystemExit())
        assert e.code==2
    captured = capsys.readouterr()
    assert patch(captured.err) == """usage: grebakker [-h] [-c FILE] [--version] [--continue] [--log-name LOG_NAME]
                 [--log-restart] [--log-off] [--log-format {csv,json}] [-v]
                 action destination definition
grebakker: error: argument --log-format: invalid choice: 'foo' (choose from csv, json)
"""
    assert patch(captured.out) == ""    


def test_main_copy_missing_valid(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION1, "set2", tmp_path)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-vv"])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Copying '<DIR>/set2/document.txt'... done. (<DUR>)
 Copying '<DIR>/set2/something_else.csv'... done. (<DUR>)
 Copying '<DIR>/set2/subfolder1'... done. (<DUR>)
 Copying '<DIR>/set2/subfolder2'... done. (<DUR>)
Completed after <DUR>
"""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION1)


def test_main_copy_missing_file_default(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION1, "set2", tmp_path)
    os.remove(os.path.join(tmp_path, "set2", "something_else.csv"))
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-vv"])
    assert ret==2
    captured = capsys.readouterr()
    assert pdirtime(captured.err, tmp_path) == """grebakker: error: file/folder '<DIR>/set2/something_else.csv' to copy does not exist.
"""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Copying '<DIR>/set2/document.txt'... done. (<DUR>)
"""
    #check_generated(tmp_path, actions, dst, "csv")
    #check_def(tmp_path, DEFINITION1A)

def test_main_copy_missing_file_none(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION1, "set2", tmp_path)
    os.remove(os.path.join(tmp_path, "set2", "something_else.csv"))
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-vv", "--log-off"])
    assert ret==2
    captured = capsys.readouterr()
    assert pdirtime(captured.err, tmp_path) == """grebakker: error: file/folder '<DIR>/set2/something_else.csv' to copy does not exist.
"""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Copying '<DIR>/set2/document.txt'... done. (<DUR>)
"""
    #check_generated(tmp_path, actions, dst, "csv")
    #check_def(tmp_path, DEFINITION1A)

def test_main_copy_missing_file_csv(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION1, "set2", tmp_path)
    os.remove(os.path.join(tmp_path, "set2", "something_else.csv"))
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-vv", "--log-format", "csv"])
    assert ret==2
    captured = capsys.readouterr()
    assert pdirtime(captured.err, tmp_path) == """grebakker: error: file/folder '<DIR>/set2/something_else.csv' to copy does not exist.
"""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Copying '<DIR>/set2/document.txt'... done. (<DUR>)
"""
    #check_generated(tmp_path, actions, dst, "csv")
    #check_def(tmp_path, DEFINITION1A)

def test_main_copy_missing_file_json(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION1, "set2", tmp_path)
    os.remove(os.path.join(tmp_path, "set2", "something_else.csv"))
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-vv", "--log-format", "json"])
    assert ret==2
    captured = capsys.readouterr()
    assert pdirtime(captured.err, tmp_path) == """grebakker: error: file/folder '<DIR>/set2/something_else.csv' to copy does not exist.
"""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Copying '<DIR>/set2/document.txt'... done. (<DUR>)
"""
    #check_generated(tmp_path, actions, dst, "csv")
    #check_def(tmp_path, DEFINITION1A)


def test_main_copy_missing_folder_default(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION1, "set2", tmp_path)
    shutil.rmtree(os.path.join(tmp_path, "set2", "subfolder2"), ignore_errors=True)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-vv"])
    assert ret==2
    captured = capsys.readouterr()
    assert pdirtime(captured.err, tmp_path) == """grebakker: error: file/folder '<DIR>/set2/subfolder2' to copy does not exist.
"""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Copying '<DIR>/set2/document.txt'... done. (<DUR>)
 Copying '<DIR>/set2/something_else.csv'... done. (<DUR>)
 Copying '<DIR>/set2/subfolder1'... done. (<DUR>)
"""
    #check_generated(tmp_path, actions, dst, "csv")
    #check_def(tmp_path, DEFINITION1A)

def test_main_copy_missing_folder_none(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION1, "set2", tmp_path)
    shutil.rmtree(os.path.join(tmp_path, "set2", "subfolder2"), ignore_errors=True)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-vv", "--log-off"])
    assert ret==2
    captured = capsys.readouterr()
    assert pdirtime(captured.err, tmp_path) == """grebakker: error: file/folder '<DIR>/set2/subfolder2' to copy does not exist.
"""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Copying '<DIR>/set2/document.txt'... done. (<DUR>)
 Copying '<DIR>/set2/something_else.csv'... done. (<DUR>)
 Copying '<DIR>/set2/subfolder1'... done. (<DUR>)
"""
    #check_generated(tmp_path, actions, dst, "csv")
    #check_def(tmp_path, DEFINITION1A)

def test_main_copy_missing_folder_csv(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION1, "set2", tmp_path)
    shutil.rmtree(os.path.join(tmp_path, "set2", "subfolder2"), ignore_errors=True)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-vv", "--log-format", "csv"])
    assert ret==2
    captured = capsys.readouterr()
    assert pdirtime(captured.err, tmp_path) == """grebakker: error: file/folder '<DIR>/set2/subfolder2' to copy does not exist.
"""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Copying '<DIR>/set2/document.txt'... done. (<DUR>)
 Copying '<DIR>/set2/something_else.csv'... done. (<DUR>)
 Copying '<DIR>/set2/subfolder1'... done. (<DUR>)
"""
    #check_generated(tmp_path, actions, dst, "csv")
    #check_def(tmp_path, DEFINITION1A)

def test_main_copy_missing_folder_json(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION1, "set2", tmp_path)
    shutil.rmtree(os.path.join(tmp_path, "set2", "subfolder2"), ignore_errors=True)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-vv", "--log-format", "json"])
    assert ret==2
    captured = capsys.readouterr()
    assert pdirtime(captured.err, tmp_path) == """grebakker: error: file/folder '<DIR>/set2/subfolder2' to copy does not exist.
"""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Copying '<DIR>/set2/document.txt'... done. (<DUR>)
 Copying '<DIR>/set2/something_else.csv'... done. (<DUR>)
 Copying '<DIR>/set2/subfolder1'... done. (<DUR>)
"""
    #check_generated(tmp_path, actions, dst, "csv")
    #check_def(tmp_path, DEFINITION1A)


def test_main_compress_missing_valid(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION2, "set2", tmp_path)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-vv"])
    assert ret==0
    captured = capsys.readouterr()
    assert pname(captured.err) == ""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Compressing '<DIR>/set2/document.txt'... done. (<DUR>)
 Compressing '<DIR>/set2/subfolder1'... done. (<DUR>)
 Compressing '<DIR>/set2/subfolder2'... done. (<DUR>)
Completed after <DUR>
"""
    check_generated(tmp_path, actions, dst, "csv")
    check_def(tmp_path, DEFINITION2)

def test_main_compress_missing_file_default(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION2, "set2", tmp_path)
    os.remove(os.path.join(tmp_path, "set2", "document.txt"))
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-vv"])
    assert ret==2
    captured = capsys.readouterr()
    assert pdirtime(captured.err, tmp_path) == """grebakker: error: file/folder '<DIR>/set2/document.txt' to compress does not exist.
"""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
"""
    #check_generated(tmp_path, actions, dst, "csv")
    #check_def(tmp_path, DEFINITION2)

def test_main_compress_missing_file_none(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION2, "set2", tmp_path)
    os.remove(os.path.join(tmp_path, "set2", "document.txt"))
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-vv", "--log-off"])
    assert ret==2
    captured = capsys.readouterr()
    assert pdirtime(captured.err, tmp_path) == """grebakker: error: file/folder '<DIR>/set2/document.txt' to compress does not exist.
"""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
"""
    #check_generated(tmp_path, actions, dst, "csv")
    #check_def(tmp_path, DEFINITION2)

def test_main_compress_missing_file_csv(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION2, "set2", tmp_path)
    os.remove(os.path.join(tmp_path, "set2", "document.txt"))
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-vv", "--log-format", "csv"])
    assert ret==2
    captured = capsys.readouterr()
    assert pdirtime(captured.err, tmp_path) == """grebakker: error: file/folder '<DIR>/set2/document.txt' to compress does not exist.
"""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
"""
    #check_generated(tmp_path, actions, dst, "csv")
    #check_def(tmp_path, DEFINITION2)

def test_main_compress_missing_file_json(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION2, "set2", tmp_path)
    os.remove(os.path.join(tmp_path, "set2", "document.txt"))
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-vv", "--log-format", "json"])
    assert ret==2
    captured = capsys.readouterr()
    assert pdirtime(captured.err, tmp_path) == """grebakker: error: file/folder '<DIR>/set2/document.txt' to compress does not exist.
"""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
"""
    #check_generated(tmp_path, actions, dst, "csv")
    #check_def(tmp_path, DEFINITION2)


def test_main_compress_missing_folder_default(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION2, "set2", tmp_path)
    shutil.rmtree(os.path.join(tmp_path, "set2", "subfolder2"), ignore_errors=True)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-vv"])
    assert ret==2
    captured = capsys.readouterr()
    assert pdirtime(captured.err, tmp_path) == """grebakker: error: file/folder '<DIR>/set2/subfolder2' to compress does not exist.
"""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Compressing '<DIR>/set2/document.txt'... done. (<DUR>)
 Compressing '<DIR>/set2/subfolder1'... done. (<DUR>)
"""
    #check_generated(tmp_path, actions, dst, "csv")
    #check_def(tmp_path, DEFINITION2)

def test_main_compress_missing_folder_none(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION2, "set2", tmp_path)
    shutil.rmtree(os.path.join(tmp_path, "set2", "subfolder2"), ignore_errors=True)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-vv", "--log-off"])
    assert ret==2
    captured = capsys.readouterr()
    assert pdirtime(captured.err, tmp_path) == """grebakker: error: file/folder '<DIR>/set2/subfolder2' to compress does not exist.
"""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Compressing '<DIR>/set2/document.txt'... done. (<DUR>)
 Compressing '<DIR>/set2/subfolder1'... done. (<DUR>)
"""
    #check_generated(tmp_path, actions, dst, "csv")
    #check_def(tmp_path, DEFINITION2)

def test_main_compress_missing_folder_csv(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION2, "set2", tmp_path)
    shutil.rmtree(os.path.join(tmp_path, "set2", "subfolder2"), ignore_errors=True)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-vv", "--log-format", "csv"])
    assert ret==2
    captured = capsys.readouterr()
    assert pdirtime(captured.err, tmp_path) == """grebakker: error: file/folder '<DIR>/set2/subfolder2' to compress does not exist.
"""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Compressing '<DIR>/set2/document.txt'... done. (<DUR>)
 Compressing '<DIR>/set2/subfolder1'... done. (<DUR>)
"""
    #check_generated(tmp_path, actions, dst, "csv")
    #check_def(tmp_path, DEFINITION2)

def test_main_compress_missing_folder_json(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION2, "set2", tmp_path)
    shutil.rmtree(os.path.join(tmp_path, "set2", "subfolder2"), ignore_errors=True)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-vv", "--log-format", "json"])
    assert ret==2
    captured = capsys.readouterr()
    assert pdirtime(captured.err, tmp_path) == """grebakker: error: file/folder '<DIR>/set2/subfolder2' to compress does not exist.
"""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Compressing '<DIR>/set2/document.txt'... done. (<DUR>)
 Compressing '<DIR>/set2/subfolder1'... done. (<DUR>)
"""
    #check_generated(tmp_path, actions, dst, "csv")
    #check_def(tmp_path, DEFINITION2)


def test_main_subs_missing_valid(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION3A, "set2", tmp_path, add_defs={"subfolder1": DEFINITION3B})
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
    check_def(tmp_path, DEFINITION3A)
    
    
def test_main_subs_missing_sub_default(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION3A, "set2", tmp_path, add_defs={"subfolder1": DEFINITION3B})
    shutil.rmtree(os.path.join(tmp_path, "set2", "subfolder1"), ignore_errors=True)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-v", "-v"])
    assert ret==2
    captured = capsys.readouterr()
    assert pdirtime(captured.err, tmp_path) == """grebakker: error: file/folder '<DIR>/set2/subfolder1' to recurse into does not exist.
"""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Copying '<DIR>/set2/document.txt'... done. (<DUR>)
 Copying '<DIR>/set2/something_else.csv'... done. (<DUR>)
 Compressing '<DIR>/set2/subfolder2'... done. (<DUR>)
"""
    #check_generated(tmp_path, actions, dst, "csv")
    #check_def(tmp_path, DEFINITION3A)
    
def test_main_subs_missing_sub_none(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION3A, "set2", tmp_path, add_defs={"subfolder1": DEFINITION3B})
    shutil.rmtree(os.path.join(tmp_path, "set2", "subfolder1"), ignore_errors=True)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-v", "-v", "--log-off"])
    assert ret==2
    captured = capsys.readouterr()
    assert pdirtime(captured.err, tmp_path) == """grebakker: error: file/folder '<DIR>/set2/subfolder1' to recurse into does not exist.
"""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Copying '<DIR>/set2/document.txt'... done. (<DUR>)
 Copying '<DIR>/set2/something_else.csv'... done. (<DUR>)
 Compressing '<DIR>/set2/subfolder2'... done. (<DUR>)
"""
    #check_generated(tmp_path, actions, dst, "csv")
    #check_def(tmp_path, DEFINITION3A)
    
def test_main_subs_missing_sub_csv(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION3A, "set2", tmp_path, add_defs={"subfolder1": DEFINITION3B})
    shutil.rmtree(os.path.join(tmp_path, "set2", "subfolder1"), ignore_errors=True)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-v", "-v", "--log-format", "csv"])
    assert ret==2
    captured = capsys.readouterr()
    assert pdirtime(captured.err, tmp_path) == """grebakker: error: file/folder '<DIR>/set2/subfolder1' to recurse into does not exist.
"""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Copying '<DIR>/set2/document.txt'... done. (<DUR>)
 Copying '<DIR>/set2/something_else.csv'... done. (<DUR>)
 Compressing '<DIR>/set2/subfolder2'... done. (<DUR>)
"""
    #check_generated(tmp_path, actions, dst, "csv")
    #check_def(tmp_path, DEFINITION3A)
    
def test_main_subs_missing_sub_json(capsys, tmp_path):
    actions, dstroot, dst = prepare(DEFINITION3A, "set2", tmp_path, add_defs={"subfolder1": DEFINITION3B})
    shutil.rmtree(os.path.join(tmp_path, "set2", "subfolder1"), ignore_errors=True)
    os.chdir(tmp_path) # !!!
    ret = grebakker.main(["backup", dstroot, str(tmp_path / "set2"), "-v", "-v", "--log-format", "json"])
    assert ret==2
    captured = capsys.readouterr()
    assert pdirtime(captured.err, tmp_path) == """grebakker: error: file/folder '<DIR>/set2/subfolder1' to recurse into does not exist.
"""
    assert pdirtime(captured.out, tmp_path) == """Starting...
Processing '<DIR>/set2'...
 Copying '<DIR>/set2/document.txt'... done. (<DUR>)
 Copying '<DIR>/set2/something_else.csv'... done. (<DUR>)
 Compressing '<DIR>/set2/subfolder2'... done. (<DUR>)
"""
    #check_generated(tmp_path, actions, dst, "csv")
    #check_def(tmp_path, DEFINITION3A)
    
    