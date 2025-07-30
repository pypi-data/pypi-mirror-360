# -*- coding: utf-8 -*-
"""\
* *[pyIcmLib]* :: Operations Abstract Base Classes.
"""

import typing

csInfo: typing.Dict[str, typing.Any] = { 'moduleDescription': ["""
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Description:* | ]]
**  [[elisp:(org-cycle)][| ]]  [Xref]          :: *[Related/Xrefs:]*  <<Xref-Here->>  -- External Documents  [[elisp:(org-cycle)][| ]]
**  [[elisp:(org-cycle)][| ]]   Model and Terminology                                      :Overview:
** In Native-BISOS the primary entry to all that is executed is an Operation.
** All operations are derived from the class AbstractOperation.
** There are 4 abstractions under the AbstractOperation.
** 1) Operations Support Facilities, logging, tracing, audit-trail, etc.
** 2) AbstractWithinOperationWrappers: Wrappers that are aware of the context of operations
** 3) AbstractRemoteOperations: For when an Operation is delegated to remote performance
** 4) AbstractCommands: For enabling consistent invitation of Operations from command line.
**      [End-Of-Description]
"""], }

csInfo['moduleUsage'] = """
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Usage:* | ]]
** +
** These classes are to be sub-classed. There is no explicit direct usage.
**      [End-Of-Usage]
"""

csInfo['moduleStatus'] = """
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Status:* | ]]
**  [[elisp:(org-cycle)][| ]]  [Info]          :: *[Current-Info:]* Status/Maintenance -- General TODO List [[elisp:(org-cycle)][| ]]
** TODO Revisit implementation of all classes based on existing ICM.
SCHEDULED: <2021-12-18 Sat>
** TODO Transition to op.AbstractCommand from cs.Cmnd
** TODO Fully shape up this module to reflect best templates.
**      [End-Of-Status]
"""

"""
*  [[elisp:(org-cycle)][| *ICM-INFO:* |]] :: Author, Copyleft and Version Information
"""
####+BEGIN: bx:cs:py:name :style "fileName"
csInfo['moduleName'] = "op"
####+END:

####+BEGIN: bx:cs:py:version-timestamp :style "date"
csInfo['version'] = "202209071822"
####+END:

####+BEGIN: bx:cs:py:status :status "Production"
csInfo['status']  = "Production"
####+END:

csInfo['credits'] = ""

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/bisos/apps/defaults/update/sw/icm/py/csInfo-mbNedaGplByStar.py"
csInfo['authors'] = "[[http://mohsen.1.banan.byname.net][Mohsen Banan]]"
csInfo['copyright'] = "Copyright 2017, [[http://www.neda.com][Neda Communications, Inc.]]"
csInfo['licenses'] = "[[https://www.gnu.org/licenses/agpl-3.0.en.html][Affero GPL]]", "Libre-Halaal Services License", "Neda Commercial License"
csInfo['maintainers'] = "[[http://mohsen.1.banan.byname.net][Mohsen Banan]]"
csInfo['contacts'] = "[[http://mohsen.1.banan.byname.net/contact]]"
csInfo['partOf'] = "[[http://www.by-star.net][Libre-Halaal ByStar Digital Ecosystem]]"
####+END:

csInfo['panel'] = "{}-Panel.org".format(csInfo['moduleName'])
csInfo['groupingType'] = "IcmGroupingType-pkged"
csInfo['cmndParts'] = "IcmCmndParts[common] IcmCmndParts[param]"


####+BEGIN: bx:cs:python:top-of-file :partof "bystar" :copyleft "halaal+minimal"
""" #+begin_org
*  This file:/bisos/git/auth/bxRepos/bisos-pip/b/py3/bisos/b/op.py :: [[elisp:(org-cycle)][| ]]
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

#from bisos.b import cs
from bisos import b
#from bisos.b import io

from enum import Enum

####+BEGIN: bx:dblock:python:class :className "OpError" :superClass "Enum" :comment "" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /OpError/ Enum  [[elisp:(org-cycle)][| ]]
#+end_org """
class OpError(Enum):
####+END:
    Success = 0
    Failure = 1
    ShellBuiltinMisuse = 2
    ExtractionSuccess = 11
    PermissionProblem = 126
    CommandNotFound = 127
    ExitError = 128
    Signal1 = 128+1
    ControlC = 130
    Signal9 = 128+9
    UsageError = 201
    CmndLineUsageError = 202
    ExitStatusOutOfRange = 255



opErrorDesc = {}

opErrorDesc[OpError.Success] = "Successful Operation -- No Errors"
opErrorDesc[OpError.Failure] = "Catchall for general errors"
opErrorDesc[OpError.ShellBuiltinMisuse]= "Bash Problem"
opErrorDesc[OpError.ExtractionSuccess] = "NOTYET"
opErrorDesc[OpError.PermissionProblem] = "Command invoked cannot execute"


####+BEGIN: bx:dblock:python:func :funcName "notAsFailure" :funcType "succFail" :retType "bool" :deco "" :argsList "obj"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-succFail [[elisp:(outline-show-subtree+toggle)][||]] /notAsFailure/ retType=bool argsList=(obj)  [[elisp:(org-cycle)][| ]]
#+end_org """
def notAsFailure(
    obj,
):
####+END:
    if not obj:
        return  OpError.Failure
    else:
        return  OpError.Success


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  opErrorDescGet -- return opErrorDesc[opError]   [[elisp:(org-cycle)][| ]]
"""
def opErrorDescGet(opError):
    """ OpError is defined as Constants. A basic textual description is provided with opErrorDescGet().

Usage:  opOutcome.error = None  -- opOutcome.error = OpError.UsageError
OpError, eventually maps to Unix sys.exit(error). Therefore, the range is 0-255.
64-to-78 Should be made consistent with /usr/include/sysexits.h.
There are also qmail errors starting at 100.
"""
    # NOTYET, catch exceptions
    return opErrorDesc[opError]

# Default = type('Default', (), dict(__repr__=lambda self: 'Default'))()

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-Basic        ::  Outcome -- .log() .isProblematic()   [[elisp:(org-cycle)][| ]]
"""
class Outcome(object):
    """ Operation Outcome. Consisting Of Error and/or Result -- Operation Can Be Local Or Remote

** TODO Add exception and exceptionInfo For situations where try: is handled
** TODO Add opType as one of PyCallable -- SubProc, RemoteOp
** TODO Add a printer (repr) for Outcome

Outcome is a combination of OpError(SuccessOrError) and OpResults.

Typical Usage is like this:

On Definition of f():
thisOutcome = Outcome()
thisOutcome.results = itemOrList
)
return(thisOutcome.set(
    opError=None,
    ))

Then on invocation:
thisOutcome = Outcome()
opOutcome = f()
if opOutcome.error: return(thisOutcome.set(opError=opOutcome.error))
opResults = opOutcome.results
"""
    def __init__(self,
                 invokerName=None,
                 opError=None,
                 opErrInfo=None,
                 opResults=None,
                 opStdout=None,
                 opStderr=None,
                 opStdcmnd=None,
    ):
        '''Constructor'''
        self.invokerName = invokerName
        self.error = opError
        self.errInfo  = opErrInfo
        self.results = opResults
        self.stdout = opStdout
        self.stdoutRstrip = opStdout
        self.stderr = opStderr
        self.stdcmnd = opStdcmnd
        if self.stdout:
            self.stdoutRstrip = self.stdout.rstrip('\n')


    def set(self,
            invokerName=None,
            opError=None,
            opErrInfo=None,
            opResults=b.Void,
            opStdout=b.Void,
            opStderr=None,
            opStdcmnd=None,
    ):
        if invokerName is not None:
            self.name = invokerName
        if opError is not None:
            self.error = opError
        if opErrInfo is not  None:
            self.errInfo = opErrInfo
        if opResults is not b.Void:
            self.results = opResults
        if opStdout is not b.Void:
            self.stdout = opStdout
            self.stdoutRstrip = opStdout.rstrip('\n')
        if opStderr is not None:
            self.stderr = opStderr
        if opStdcmnd is not None:
            self.stdcmnd = opStdcmnd

        return self

    def isProblematic(self):
        if self.error:
            if self.error == b.OpError.Success:
                return False
            # NOTYET, these should be logged
            # print(f"isProblematic: error={self.error}")
            b.cs.globalContext.get().__class__.lastOutcome = self
            return True
        else:
            return False


    def log(self):
        G = b.cs.globalContext.get()
        b.io.log.here(G.icmMyFullName() + ':' + str(self.invokerName) + ':' + b.ast.stackFrameInfoGet(2))
        if self.stdcmnd: b.io.log.here("Stdcmnd: " +  self.stdcmnd)
        if self.stdout: b.io.log.here("Stdout: " +  self.stdout)
        if self.stderr: b.io.log.here("Stderr: " +  self.stderr)
        return self


    def out(self):
        G = cs.globalContext.get()
        icm.ANN_here(G.icmMyFullName() + ':' + str(self.invokerName) + ':' + b.ast.stackFrameInfoGet(2))
        if self.stdcmnd: icm.ANN_write("Stdcmnd: \n" +  self.stdcmnd)
        if self.stdout: icm.ANN_write("Stdout: ")
        if self.stdout: icm.OUT_write(self.stdout)
        if self.stderr: icm.ANN_write("Stderr: \n" +  self.stderr)
        return self


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  opSuccess    [[elisp:(org-cycle)][| ]]
"""
def opSuccess():
    """."""
    return (
        Outcome()
    )


def successAndNoResult(cmndOutcome):
    """."""
    return cmndOutcome.set(
        opError=OpError.Success,  # type: ignore
        opResults=None,
    )


####+BEGIN: bx:dblock:python:class :className "BasicOp" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /BasicOp/ object  [[elisp:(org-cycle)][| ]]
#+end_org """
class BasicOp(object):
####+END:
    """
** Basic Operation.
"""

    opVisibility = ["all"]  # users, developers, internal
    opUsers = []            # lsipusr
    opGroups = []           # bystar
    opImpact = []           # read, modify

    def __init__(self,
                 outcome=None,
                 log=0,
    ):
        self.outcome = outcome
        self.log = log

    def docStrClass(self,):
        return self.__class__.__doc__

    def users(self,):
        return self.__class__.opUsers

    def groups(self,):
        return self.__class__.opGroups

    def impact(self,):
        return self.__class__.opImpact

    def visibility(self,):
        return self.__class__.opVisibility

    def getOutcome(self):
        if self.outcome:
            return self.outcome
        return Outcome(invokerName=self.myName())

    def opMyName(self):
        return self.__class__.__name__

    def myName(self):
        return self.opMyName()


####+BEGIN: bx:dblock:python:class :className "AbstractWithinOpWrapper" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /AbstractWithinOpWrapper/ object  [[elisp:(org-cycle)][| ]]
#+end_org """
class AbstractWithinOpWrapper(object):
####+END:
    """
** Basic Operation.
"""

    opVisibility = ["all"]  # users, developers, internal
    opUsers = []            # lsipusr
    opGroups = []           # bystar
    opImpact = []           # read, modify

    def __init__(self,
                 invedBy=None,
                 log=0,
    ):
        self.invedBy = invedBy
        if invedBy:
            self.outcome = invedBy.cmndOutcome
        else:
            self.outcome = None
        self.log = log

    def docStrClass(self,):
        return self.__class__.__doc__

    def users(self,):
        return self.__class__.opUsers

    def groups(self,):
        return self.__class__.opGroups

    def impact(self,):
        return self.__class__.opImpact

    def visibility(self,):
        return self.__class__.opVisibility

    def getOutcome(self):
        if self.outcome:
            return self.outcome
        return Outcome(invokerName=self.myName())

    def opMyName(self):
        return self.__class__.__name__

    def myName(self):
        return self.opMyName()



####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :title " ~End Of Editable Text~ "
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _ ~End Of Editable Text~ _: |]]    [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/bisos/apps/defaults/software/plusOrg/dblock/inserts/endOfFileControls.org"
#+STARTUP: showall
####+END:
