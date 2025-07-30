# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =bpf-lib= for
#+end_org """

####+BEGIN: b:py3:cs:file/dblockControls :classification "bpf-lib"
""" #+begin_org
* [[elisp:(org-cycle)][| /Control Parameters Of This File/ |]] :: dblk ctrls classifications=bpf-lib
#+BEGIN_SRC emacs-lisp
(setq-local b:dblockControls t) ; (setq-local b:dblockControls nil)
(put 'b:dblockControls 'py3:cs:Classification "bpf-lib") ; one of cs-mu, cs-u, cs-lib, bpf-lib, pyLibPure
#+END_SRC
#+RESULTS:
: cs-mu
#+end_org """
####+END:

####+BEGIN: b:prog:file/proclamations :outLevel 1
""" #+begin_org
* *[[elisp:(org-cycle)][| Proclamations |]]* :: Libre-Halaal Software --- Part Of BISOS ---  Poly-COMEEGA Format.
** This is Libre-Halaal Software. © Neda Communications, Inc. Subject to AGPL.
** It is part of BISOS (ByStar Internet Services OS)
** Best read and edited  with Blee in Poly-COMEEGA (Polymode Colaborative Org-Mode Enhance Emacs Generalized Authorship)
#+end_org """
####+END:

####+BEGIN: b:prog:file/particulars :authors ("./inserts/authors-mb.org")
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars |]]* :: Authors, version
** This File: /l/pip/b/py3/bisos/b/utils.py
** File True Name: /bisos/git/auth/bxRepos/bisos-pip/b/py3/bisos/b/utils.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:py3:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['utils'], }
csInfo['version'] = '202503034933'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'utils-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/COMEEGA/_nodeBase_/fullUsagePanel-en.org][BISOS COMEEGA Panel]]
Module description comes here.
** Relevant Panels:
** Status: In use with BISOS
** /[[elisp:(org-cycle)][| Planned Improvements |]]/ :
*** TODO complete fileName in particulars.
#+end_org """

####+BEGIN: b:prog:file/orgTopControls :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Controls |]] :: [[elisp:(delete-other-windows)][(1)]] | [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
** /Version Control/ ::  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]]

#+end_org """
####+END:

####+BEGIN: b:py3:file/workbench :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Workbench |]] :: [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pyclbr %s" (bx:buf-fname))))][pyclbr]] || [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pydoc ./%s" (bx:buf-fname))))][pydoc]] || [[elisp:(python-check (format "/bisos/pipx/bin/pyflakes %s" (bx:buf-fname)))][pyflakes]] | [[elisp:(python-check (format "/bisos/pipx/bin/pychecker %s" (bx:buf-fname))))][pychecker (executes)]] | [[elisp:(python-check (format "/bisos/pipx/bin/pycodestyle %s" (bx:buf-fname))))][pycodestyle]] | [[elisp:(python-check (format "/bisos/pipx/bin/flake8 %s" (bx:buf-fname))))][flake8]] | [[elisp:(python-check (format "/bisos/pipx/bin/pylint %s" (bx:buf-fname))))][pylint]]  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

from bisos import b
# from bisos.b import cs

import glob
from datetime import datetime

import sys
import types
import pathlib
import shutil
import os


def runOnceOnly(f):
    """Meant to be used as a decorator or manually to ensure that we run f only once

@run_once
def my_function(foo, bar):
    return foo+bar

Now my_function will only run once. Other calls to it will return
None. Just add an else clause to the if if you want it to return
something else. From your example, it doesn't need to return anything
ever.

If you don't control the creation of the function, or the function
needs to be used normally in other contexts, you can just apply the
decorator manually as well.

action = run_once(my_function)
while 1:
    if predicate:
        action()

This will leave my_function available for other uses.

Finally, if you need to only run it once twice, then you can just do

action = run_once(my_function)
action() # run once the first time

action.has_run = False
action() # run once the second time
    """
    def wrapper(*args, **kwargs):
        if not wrapper.retVal:
            retVal = f(*args, **kwargs)
            wrapper.retVal = retVal
            return retVal
        else:
            return wrapper.retVal
    wrapper.retVal = None
    return wrapper


    # From the web before my imporvements
    #
    # def wrapper(*args, **kwargs):
    #     if not wrapper.has_run:
    #         wrapper.has_run = True
    #         return f(*args, **kwargs)
    # wrapper.has_run = False
    # return wrapper


runOnceOnlyReturnFirstInvokation = runOnceOnly
idempotentMake = runOnceOnlyReturnFirstInvokation

def TIME_nowTag():
    INTERVAL_TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"
    startTime = datetime.strftime(datetime.now(), INTERVAL_TIMESTAMP_FORMAT)
    return startTime


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  DIR_ensure    [[elisp:(org-cycle)][| ]]
"""
def DIR_ensure(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        try: os.makedirs(directory, 0o777 )
        except OSError: pass

####+BEGIN: bx:icm:python:func :funcName "DIR_ensureDir" :funcType "void" :retType "bool" :deco "" :argsList "dirPath"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-void     [[elisp:(outline-show-subtree+toggle)][||]] /DIR_ensureDir/ retType=bool argsList=(dirPath)  [[elisp:(org-cycle)][| ]]
#+end_org """
def DIR_ensureDir(
    dirPath,
):
####+END:
    """ Ensure that specified directory exists."""
    try:
        os.makedirs(dirPath)
    except OSError:
        if not os.path.isdir(dirPath):
            raise

####+BEGIN: bx:icm:python:func :funcName "DIR_ensureForFile" :funcType "void" :retType "bool" :deco "" :argsList "filePath"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-void     [[elisp:(outline-show-subtree+toggle)][||]] /DIR_ensureForFile/ retType=bool argsList=(filePath)  [[elisp:(org-cycle)][| ]]
#+end_org """
def DIR_ensureForFile(
    filePath,
):
####+END:
    dirPath = os.path.dirname(filePath)
    DIR_ensureDir(dirPath)


####+BEGIN: bx:icm:python:func :funcName "FN_latestInDir" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "dirPath"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /FN_latestInDir/ retType=bool argsList=(dirPath)  [[elisp:(org-cycle)][| ]]
#+end_org """
def FN_latestInDir(
    dirPath,
):
####+END:
    list_of_files = glob.glob("{}/*".format(dirPath))
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

"""
*  [[elisp:(org-cycle)][| ]]  /Chunking/           :: *chunks(l, n) -- chunksNuOf(l, n)*    [[elisp:(org-cycle)][| ]]
"""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  chunks    [[elisp:(org-cycle)][| ]]
"""

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  chunksNuOf    [[elisp:(org-cycle)][| ]]
"""

def chunksNuOf(l, n):
    """Report NuOfChunks of  n-sized chunks from l."""
    listLength = len(l)
    remainder = listLength % n
    if remainder == 0:
        return listLength / n
    else:
        return listLength / n + 1



####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
