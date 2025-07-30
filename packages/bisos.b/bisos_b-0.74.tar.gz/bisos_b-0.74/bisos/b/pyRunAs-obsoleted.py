# -*- coding: utf-8 -*-
"""\
* *[Summary]* :: A /library/ for allowing a decorated piece of code to run as different user.
"""

import typing

csInfo: typing.Dict[str, typing.Any] = { 'moduleDescription': ["""
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Description:* | ]]
**  [[elisp:(org-cycle)][| ]]  [Xref]          :: *[Related/Xrefs:]*  <<Xref-Here->>  -- External Documents  [[elisp:(org-cycle)][| ]]

**  [[elisp:(org-cycle)][| ]]   Concept:                                                      :Overview:
*** Instead of running a shell command as sudo in a subprocess, we want to run a
piece of python code as a different user. We end up doing a subprocess and a sudo,
but all of that is hidden in a decorator.
The implementation involves marshal, functools, subprocess.

**  [[elisp:(org-cycle)][| ]]   Prior Work:

*** Py2 implemetations:  https://gist.github.com/barneygale/8ff070659178135b10b5e202a1ecaa3f
*** Py2 implemetations:  https://pastebin.com/DHPdDU9W
***
*** Mohsen BANAN ported these to py3 on <2021-10-23 Sat 21:19>

**      [End-Of-Description]
"""], }

csInfo['moduleUsage'] = """
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Usage:* | ]]
**      Installation:  pypi -- pip install bisos.basics
**      Import:  from bisos.basics import pyRunAs
**      Use:   @pyRunAs.User("root")
**      Examples and Testing:  icmEx-pyRunAs.py
**     [End-Of-Usage]
"""

csInfo['moduleStatus'] = """
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Status:* | ]]
**  [[elisp:(org-cycle)][| ]]  [Info]          :: *[Current-Info:]* Status/Maintenance -- General TODO List [[elisp:(org-cycle)][| ]]
** TODO [[elisp:(org-cycle)][| ]]  Current     :: In use. Should be imporved by dynamic and additional deco params. [[elisp:(org-cycle)][| ]]
**      [End-Of-Status]
"""

"""
*  [[elisp:(org-cycle)][| *ICM-INFO:* |]] :: Author, Copyleft and Version Information
"""
####+BEGIN: bx:cs:py:name :style "fileName"
csInfo['moduleName'] = "pyRunAs"
####+END:

####+BEGIN: bx:cs:py:version-timestamp :style "date"
csInfo['version'] = "202209072629"
####+END:

####+BEGIN: bx:cs:py:status :status "Production"
csInfo['status']  = "Production"
####+END:

csInfo['credits'] = ""

####+BEGINNOT: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/bisos/apps/defaults/update/sw/icm/py/csInfo-mbNedaGplByStar.py"
####+END:

csInfo['panel'] = "{}-Panel.org".format(csInfo['moduleName'])
csInfo['groupingType'] = "IcmGroupingType-pkged"
csInfo['cmndParts'] = "IcmCmndParts[common] IcmCmndParts[param]"


####+BEGIN: bx:cs:python:top-of-file :partof "bystar" :copyleft "halaal+minimal"
""" #+begin_org
*  This file:/bisos/git/auth/bxRepos/bisos-pip/b/py3/bisos/b/pyRunAs.py :: [[elisp:(org-cycle)][| ]]
 is part of The Libre-Halaal ByStar Digital Ecosystem. http://www.by-star.net
 *CopyLeft*  This Software is a Libre-Halaal Poly-Existential. See http://www.freeprotocols.org
 A Python Interactively Command Module (PyICM).
 Best Developed With COMEEGA-Emacs And Best Used With Blee-ICM-Players.
 *WARNING*: All edits wityhin Dynamic Blocks may be lost.
#+end_org """
####+END:

####+BEGIN: bx:cs:python:topControls :partof "bystar" :copyleft "halaal+minimal"
""" #+begin_org
*  [[elisp:(org-cycle)][|/Controls/| ]] :: [[elisp:(org-show-subtree)][|=]]  [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(delete-other-windows)][(1)]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
** /Version Control/ ::  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]]
#+end_org """
####+END:
####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/bisos/apps/defaults/software/plusOrg/dblock/inserts/pyWorkBench.org"
"""
*  /Python Workbench/ ::  [[elisp:(org-cycle)][| ]]  [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pyclbr %s" (bx:buf-fname))))][pyclbr]] || [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pydoc ./%s" (bx:buf-fname))))][pydoc]] || [[elisp:(python-check (format "/bisos/pipx/bin/pyflakes %s" (bx:buf-fname)))][pyflakes]] | [[elisp:(python-check (format "/bisos/pipx/bin/pychecker %s" (bx:buf-fname))))][pychecker (executes)]] | [[elisp:(python-check (format "/bisos/pipx/bin/pycodestyle %s" (bx:buf-fname))))][pycodestyle]] | [[elisp:(python-check (format "/bisos/pipx/bin/flake8 %s" (bx:buf-fname))))][flake8]] | [[elisp:(python-check (format "/bisos/pipx/bin/pylint %s" (bx:buf-fname))))][pylint]]  [[elisp:(org-cycle)][| ]]
"""
####+END:

####+BEGIN: bx:cs:python:icmItem :itemType "=Imports=" :itemTitle "*IMPORTS*"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =Imports=  [[elisp:(outline-show-subtree+toggle)][||]] *IMPORTS*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

from bisos.b import b_io
from bisos.b import cs

import sys, marshal, functools, subprocess

####+BEGIN: bx:dblock:python:section :title "Subproc Execution Code As String"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Subproc Execution Code As String*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:

child_script = """
import marshal, sys, types;
fn, args, kwargs = marshal.loads(sys.stdin.buffer.read())
sys.stdout.buffer.write(
    marshal.dumps(
       types.FunctionType(fn, globals())(*args, **kwargs),
    )
)
"""

####+BEGIN: bx:dblock:python:section :title "Class Definitions"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Class Definitions*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:

####+BEGIN: bx:dblock:python:class :className "User" :superClass "object" :comment "" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /User/ object  [[elisp:(org-cycle)][| ]]
#+end_org """
class User(object):
####+END:
    def __init__(
            self,
            user,
    ):

        self.__user = None

        if user is None:
            #io.eh.problem_usageError("User Can't be None")
            print("User Can't be None")
            return
        elif not isinstance(user, str):
            #io.eh.problem_usageError("Expected A String")
            print("Expected A String")
            return

        user = user.strip()

        if len(user) == 0:
            #io.eh.problem_usageError("Expected A Non-Blank String")
            print("Expected A Non-Blank String")
            #
            return

        if user == 'root':
            # icm.TM_here("Running As Root")  # TM_ module, has not been setup yet
            pass

        self.__user = user

    @property
    def user(self):
        return self.__user

    def __call__(self, func):

        @functools.wraps(func)
        def inner(*args, **kwargs):
            if not self.user:
                #io.eh.problem_info("Bad None user.")
                print("Bad None user.")
                return None
            proc_args = [
                "sudo",
                "-u",
                self.user,
                sys.executable,
                "-c",
                child_script
            ]
            #print(f"{proc_args}")
            proc = subprocess.Popen(
                proc_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE
            )
            ex = None
            retval = None

            try:
                send_data = marshal.dumps((
                func.__code__,
                    args,
                    kwargs))
                recv_data = proc.communicate(send_data)[0]


                retval = marshal.loads(recv_data)
            except Exception as e:
                ex = e

            returncode = proc.wait()
            if returncode != 0 or ex is not None:
                #raise GotSomeSplaininToDo(returncode, retval, ex)
                pass

            return retval

        return inner

####+BEGIN: b:py3:cs:func/typing :funcName "as_root_writeToFile" :funcType "" :retType "" :deco "default" :argsList ""  :comment "_ALERT_"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-       [[elisp:(outline-show-subtree+toggle)][||]] /as_root_writeToFile/  _ALERT_ deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def as_root_writeToFile(
####+END:
        destFilePath,
        inBytes,
):
    """A warpper to allow for logging, etc. And also to enforce typing."""

    writeToFileAs_root(str(destFilePath), inBytes,)



####+BEGIN: bx:cs:py3:func :funcName "writeToFileAs_root" :funcType "" :retType "" :deco "User(\"root\")" :argsList ""  :comment "_ALERT_"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-         [[elisp:(outline-show-subtree+toggle)][||]] /writeToFileAs_root/ =_ALERT_= deco=User("root")  [[elisp:(org-cycle)][| ]]
#+end_org """
@User("root")
def writeToFileAs_root(
####+END:
        destFilePath: str,
        inBytes,
):
    """Common usage would be @b.pyRunAs.User("root")"""
    with open(destFilePath, "w") as thisFile:
        thisFile.write(inBytes + '\n')

####+BEGIN: b:py3:cs:func/typing :funcName "as_root_osSystem" :funcType "" :retType "" :deco "default" :argsList ""  :comment "_ALERT_"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-       [[elisp:(outline-show-subtree+toggle)][||]] /as_root_osSystem/  _ALERT_ deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def as_root_osSystem(
####+END:
        sysCmnd: str,
):
    """A warpper to allow for logging, etc. And also to enforce typing."""
    return (
        osSystemAs_root(sysCmnd)
    )


####+BEGIN: bx:cs:py3:func :funcName "osSystemAs_root" :funcType "" :retType "" :deco "User(\"root\")" :argsList ""  :comment "_ALERT_"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-         [[elisp:(outline-show-subtree+toggle)][||]] /osSystemAs_root/ =_ALERT_= deco=User("root")  [[elisp:(org-cycle)][| ]]
#+end_org """
@User("root")
def osSystemAs_root(
####+END:
        sysCmnd: str,
):
    """Common usage would be @b.pyRunAs.User("root")"""
    import os
    return os.system(sysCmnd)



####+BEGIN: b:py3:cs:func/typing :funcName "as_gitSh_writeToFile" :funcType "" :retType "" :deco "default" :argsList ""  :comment "_ALERT_"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-       [[elisp:(outline-show-subtree+toggle)][||]] /as_gitSh_writeToFile/  _ALERT_ deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def as_gitSh_writeToFile(
####+END:
        destFilePath,
        inBytes,
):
    """A warpper to allow for logging, etc."""
    writeToFileAs_gitSh(destFilePath, inBytes,)


####+BEGIN: bx:cs:py3:func :funcName "writeToFileAs_gitSh" :funcType "" :retType "" :deco "User(\"gitSh\")" :argsList ""  :comment "_ALERT_"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-         [[elisp:(outline-show-subtree+toggle)][||]] /writeToFileAs_gitSh/ =_ALERT_= deco=User("gitSh")  [[elisp:(org-cycle)][| ]]
#+end_org """
@User("gitSh")
def writeToFileAs_gitSh(
####+END:
        destFilePath,
        inBytes,
):
    """Common usage would be @b.pyRunAs.User("root")"""
    with open(destFilePath, "w") as thisFile:
        thisFile.write(inBytes + '\n')


####+BEGIN: b:py3:cs:func/typing :funcName "as_root_readFromFile" :funcType "" :retType "" :deco "default" :argsList ""  :comment "_ALERT_"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-       [[elisp:(outline-show-subtree+toggle)][||]] /as_root_readFromFile/  _ALERT_ deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def as_root_readFromFile(
####+END:
        srcFilePath,
):
    """A warpper to allow for logging, etc."""
    return (
        readFromFileAs_root(str(srcFilePath))
    )


####+BEGIN: bx:cs:py3:func :funcName "readFromFileAs_root" :funcType "" :retType "" :deco "User(\"root\")" :argsList ""  :comment "_ALERT_"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-         [[elisp:(outline-show-subtree+toggle)][||]] /readFromFileAs_root/ =_ALERT_= deco=User("root")  [[elisp:(org-cycle)][| ]]
#+end_org """
@User("root")
def readFromFileAs_root(
####+END:
        srcFilePath,
):
    """This is a lower layer function. Consider using b.pyRunAs.s_root_readFromFile.
    Common usage would be b.pyRunAs.readFromFileAs_root("fileName")"""
    with open(srcFilePath, "r") as thisFile:
        data = thisFile.read()
    return data

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :title " ~End Of Editable Text~ "
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _ ~End Of Editable Text~ _: |]]    [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/bisos/apps/defaults/software/plusOrg/dblock/inserts/endOfFileControls.org"
#+STARTUP: showall
####+END:
