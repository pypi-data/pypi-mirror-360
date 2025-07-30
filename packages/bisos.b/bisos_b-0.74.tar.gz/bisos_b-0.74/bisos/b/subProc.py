# -*- coding: utf-8 -*-
"""\
* *[Summary]* :: A /library/ Beginning point for development of new ICM oriented libraries.
"""

import typing

csInfo: typing.Dict[str, typing.Any] = { 'moduleDescription': ["""
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Description:* | ]]
**  [[elisp:(org-cycle)][| ]]  [Xref]          :: *[Related/Xrefs:]*  <<Xref-Here->>  -- External Documents  [[elisp:(org-cycle)][| ]]

**  [[elisp:(org-cycle)][| ]]   Model and Terminology                                      :Overview:
*** concept             -- Desctiption of concept
**      [End-Of-Description]
"""], }

csInfo['moduleUsage'] = """
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Usage:* | ]]

**      How-Tos:
**      [End-Of-Usage]
"""

csInfo['moduleStatus'] = """
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Status:* | ]]
**  [[elisp:(org-cycle)][| ]]  [Info]          :: *[Current-Info:]* Status/Maintenance -- General TODO List [[elisp:(org-cycle)][| ]]
** TODO [[elisp:(org-cycle)][| ]]  Current     :: For now it is an ICM. Turn it into ICM-Lib. [[elisp:(org-cycle)][| ]]
**      [End-Of-Status]
"""

"""
*  [[elisp:(org-cycle)][| *ICM-INFO:* |]] :: Author, Copyleft and Version Information
"""
####+BEGIN: bx:cs:py:name :style "fileName"
csInfo['moduleName'] = "subProc"
####+END:

####+BEGIN: bx:cs:py:version-timestamp :style "date"
csInfo['version'] = "202209073150"
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
*  This file:/bisos/git/auth/bxRepos/bisos-pip/b/py3/bisos/b/subProc.py :: [[elisp:(org-cycle)][| ]]
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

####+BEGIN: b:py3:cs:orgItem/basic :type "=PyImports= " :title "*Py Library IMPORTS*" :comment "-- with classification based framework/imports"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =PyImports=  [[elisp:(outline-show-subtree+toggle)][||]] *Py Library IMPORTS* -- with classification based framework/imports  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:framework/imports :basedOn "classification"
""" #+begin_org
** Imports Based On Classification=cs-u
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io

import collections
####+END:

#import shlex
import subprocess
import io
import sys

import select

"""
*  [[elisp:(org-cycle)][| ]]  /subProc/            :: *SubProcess -- Bash or Command Syncronous invokations* [[elisp:(org-cycle)][| ]]
"""

####+BEGIN: bx:dblock:python:class :className "Op" :superClass "b.op.BasicOp" :comment "" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /Op/ b.op.BasicOp  [[elisp:(org-cycle)][| ]]
#+end_org """
class Op(b.op.BasicOp):
####+END:
    """
** Basic Operation -- Obsoleted By WOpW.
"""
    def __init__(
            self,
            outcome=None,
            log=0,
            cd="",
            uid=""
    ):
        super().__init__(outcome, log,)
        self.cd=cd
        self.uid=uid

####+BEGIN: b:py3:cs:method/typing :methodName "bash" :methodType "eType" :deco "default" :comment "calles process.wait()"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-eType [[elisp:(outline-show-subtree+toggle)][||]] /bash/ deco=default  =calles process.wait()= deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def bash(
####+END:
            self,
            cmndStr,
            stdin="",
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| DocStr| ]]   subprocess.Popen() -- shell=True, runs cmndStr in bash.
        #+end_org """

        if not self.outcome: self.outcome = b.op.Outcome()

        if not stdin:  stdin = ""

        fullCmndStr = cmndStr
        if self.cd: fullCmndStr = f"""pushd {self.cd} > /dev/null; {cmndStr}; popd > /dev/null;"""
        if self.uid: fullCmndStr = f"""sudo -u {self.uid} -- bash -c '{fullCmndStr}'"""

        if self.log == 1:
            print(f"** cmnd= {fullCmndStr}")

        try:
            process = subprocess.Popen(
                fullCmndStr,
                shell=True,
                encoding='utf8',
                executable="/bin/bash",
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except OSError:
            self.outcome.error = OSError
        else:
            process.stdin.write(stdin)
            process.stdin.close() # type: ignore

        stdoutStrFile = io.StringIO("")
        stderrStrFile = io.StringIO("")

        pollStdout = select.poll()
        pollStderr = select.poll()

        pollStdout.register(process.stdout, select.POLLIN)
        pollStderr.register(process.stderr, select.POLLIN)

        stdoutEOF = False
        stderrEOF = False

        while True:
            stdoutActivity = pollStdout.poll(0)
            if stdoutActivity:
                c= process.stdout.read(1)
                if c:
                    stdoutStrFile.write(c)
                    if self.log == 1:
                        sys.stdout.write(c)
                else:
                   stdoutEOF = True

            stderrActivity = pollStderr.poll(0)
            if stderrActivity:
                c= process.stderr.read(1)
                if c:
                    stderrStrFile.write(c)
                    if self.log == 1:
                        sys.stderr.write(c)
                else:
                   stderrEOF = True
            if stdoutEOF and stderrEOF:
                break

        process.wait() # type: ignore

        self.outcome.stdcmnd = fullCmndStr
        self.outcome.stdout = stdoutStrFile.getvalue()
        self.outcome.stderr = stderrStrFile.getvalue()
        self.outcome.error = process.returncode # type: ignore

        if self.log == 1:
            if self.outcome.error:
                print(f"*** exit= {self.outcome.error}")

        return self.outcome

####+BEGIN: b:py3:cs:method/typing :methodName "bashWait" :methodType "eType" :deco "default" :comment "calles process.wait()"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-eType [[elisp:(outline-show-subtree+toggle)][||]] /bashWait/ deco=default  =calles process.wait()= deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def bashWait(
####+END:
            self,
            cmndStr,
            stdin=None,
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| DocStr| ]]      subprocess.Popen() -- shell=True, runs cmndStr in bash.
** TODO This should be renamed to subProc_bashOutcome and subProc_bashOut should become subProc_bash.

** TODO BISOS Py Framework -- OpedSubProc -- Desired Usages:
if not (resStr := b.OpSubProc(outcome=cmndOutcome, log=1).sudoBash(
    fa2ensite {ploneBaseDomain}.conf,
).stdOut):  return(io.eh.badOutcome(cmndOutcome))

if b.OpSubProc(outcome=cmndOutcome, cd=someDirBase, log=1).bash(
    fa2ensite {ploneBaseDomain}.conf,
).isProblematic():  return(io.eh.badOutcome(cmndOutcome))
        #+end_org """

        if not self.outcome:
            self.outcome = b.op.Outcome()

        if not stdin:
            stdin = ""

        fullCmndStr = cmndStr

        if self.cd:
            fullCmndStr = f"""pushd {self.cd}; {cmndStr}; popd;"""

        if self.uid:
            fullCmndStr = f"""sudo -u {self.uid} -- bash -c '{fullCmndStr}'"""

        self.outcome.stdcmnd = fullCmndStr
        try:
            process = subprocess.Popen(
                fullCmndStr,
                shell=True,
                encoding='utf8',
                executable="/bin/bash",
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except OSError:
            self.outcome.error = OSError
        else:
            #self.outcome.stdout, self.outcome.stderr = process.communicate(input=format(stdin.encode()))
            #self.outcome.stdout, self.outcome.stderr = process.communicate(input=stdin)
            process.stdin.write(stdin)
            process.stdin.close() # type: ignore

        process.wait() # type: ignore

        self.outcome.error = process.returncode # type: ignore

        if self.log == 1:
            print(self.outcome.stdout)

        return self.outcome


    #@io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def exec(
            self,
            cmndStr,
            stdin=None,
    ):
        """
    subprocess.Popen() -- shell=True, runs cmndStr in bash.
** TODO This should be renamed to subProc_bashOutcome and subProc_bashOut should become subProc_bash.

** TODO BISOS Py Framework -- OpedSubProc -- Desired Usages:
if not (resStr := b.OpSubProc(outcome=cmndOutcome, log=1).sudoBash(
    f"a2ensite {ploneBaseDomain}.conf",
).stdOut):  return(io.eh.badOutcome(cmndOutcome))

if b.OpSubProc(outcome=cmndOutcome, cd=someDirBase, log=1).bash(
    f"a2ensite {ploneBaseDomain}.conf",
).isProblematic():  return(io.eh.badOutcome(cmndOutcome))
        """
        if not self.outcome:
            self.outcome = b.op.Outcome()

        if not stdin:
            stdin = ""

        self.outcome.stdcmnd = cmndStr
        try:
            process = subprocess.Popen(
                cmndStr,
                encoding='utf8',
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except OSError as exception:
            self.outcome.error = exception
            print(exception)
        else:
            self.outcome.stdout, self.outcome.stderr = process.communicate(input=format(stdin.encode()))
            process.stdin.close() # type: ignore

        process.wait() # type: ignore

        self.outcome.error = process.returncode # type: ignore


        return self.outcome

####+BEGIN: bx:dblock:python:class :className "WOpW" :superClass "b.op.AbstractWithinOpWrapper" :comment "Basic Subprocess Within Operation Wrapper" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /WOpW/ b.op.AbstractWithinOpWrapper =Basic Subprocess Within Operation Wrapper=  [[elisp:(org-cycle)][| ]]
#+end_org """
class WOpW(b.op.AbstractWithinOpWrapper):
####+END:
    """
** NOTY BUG, Should be based on b.op.AbstractWithinOpWrapper.
    Should be called AbstWrappedOp. The class should be  subproc.WOp not WOpW
** Basic Subprocess Within Operation Wrapper (bash and exec),  returns an OpOutcome.
"""
    def __init__(
            self,
            invedBy=None,
            log=1,
            cd="",
            uid=""
    ):
        super().__init__(invedBy, log,)
        self.cd=cd
        self.uid=uid


####+BEGIN: b:py3:cs:method/typing :methodName "bash" :methodType "eType" :deco "default" :comment "calles process.wait()"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-eType [[elisp:(outline-show-subtree+toggle)][||]] /bash/ deco=default  =calles process.wait()= deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def bash(
####+END:
            self,
            cmndStr,
            stdin="",
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| DocStr| ]]   subprocess.Popen() -- shell=True, runs cmndStr in bash.
        #+end_org """

        if not self.outcome: self.outcome = b.op.Outcome()

        if not stdin:  stdin = ""

        fullCmndStr = cmndStr
        if self.cd: fullCmndStr = f"""pushd {self.cd} > /dev/null; {cmndStr}; popd > /dev/null;"""
        if self.uid: fullCmndStr = f"""sudo -u {self.uid} -- bash -c '{fullCmndStr}'"""

        if self.log == 1:
            print(f"** cmnd= {fullCmndStr}")

        try:
            process = subprocess.Popen(
                fullCmndStr,
                shell=True,
                encoding='utf8',
                executable="/bin/bash",
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except OSError:
            self.outcome.error = OSError
        else:
            process.stdin.write(stdin)
            process.stdin.close() # type: ignore

        stdoutStrFile = io.StringIO("")
        stderrStrFile = io.StringIO("")

        pollStdout = select.poll()
        pollStderr = select.poll()

        pollStdout.register(process.stdout, select.POLLIN)
        pollStderr.register(process.stderr, select.POLLIN)

        stdoutEOF = False
        stderrEOF = False

        while True:
            stdoutActivity = pollStdout.poll(0)
            if stdoutActivity:
                c= process.stdout.read(1)
                if c:
                    stdoutStrFile.write(c)
                    if self.log == 1:
                        sys.stdout.write(c)
                else:
                   stdoutEOF = True

            stderrActivity = pollStderr.poll(0)
            if stderrActivity:
                c= process.stderr.read(1)
                if c:
                    stderrStrFile.write(c)
                    if self.log == 1:
                        sys.stderr.write(c)
                else:
                   stderrEOF = True
            if stdoutEOF and stderrEOF:
                break

        process.wait() # type: ignore

        self.outcome.stdcmnd = fullCmndStr
        self.outcome.stdout = stdoutStrFile.getvalue()
        self.outcome.stdoutRstrip = self.outcome.stdout.rstrip('\n')
        self.outcome.stderr = stderrStrFile.getvalue()
        self.outcome.error = process.returncode # type: ignore

        if self.log == 1:
            if self.outcome.error:
                print(f"*** exit= {self.outcome.error}")

        return self.outcome


    #@io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def bashWait (
            self,
            cmndStr,
            stdin=None,
    ):
        """
    subprocess.Popen() -- shell=True, runs cmndStr in bash.
** TODO This should be renamed to subProc_bashOutcome and subProc_bashOut should become subProc_bash.

** TODO BISOS Py Framework -- OpedSubProc -- Desired Usages:
if not (resStr := b.OpSubProc(outcome=cmndOutcome, log=1).sudoBash(
    fa2ensite {ploneBaseDomain}.conf,
).stdOut):  return(io.eh.badOutcome(cmndOutcome))

if b.OpSubProc(outcome=cmndOutcome, cd=someDirBase, log=1).bash(
    fa2ensite {ploneBaseDomain}.conf,
).isProblematic():  return(io.eh.badOutcome(cmndOutcome))
        """
        #print(self.outcome)
        if not self.outcome:
            #print("No self.outcome")
            self.outcome = b.op.Outcome()

        if not stdin:
            stdin = ""

        fullCmndStr = cmndStr

        if self.cd:
            fullCmndStr = f"""pushd {self.cd}; {cmndStr}; popd;"""

        if self.uid:
            fullCmndStr = f"""sudo -u {self.uid} -- bash -c '{fullCmndStr}'"""

        self.outcome.stdcmnd = fullCmndStr
        try:
            process = subprocess.Popen(
                fullCmndStr,
                shell=True,
                encoding='utf8',
                executable="/bin/bash",
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except OSError:
            self.outcome.error = OSError
        else:
            self.outcome.stdout, self.outcome.stderr = process.communicate(input=format(stdin.encode()))
            self.outcome.stdoutRstrip = self.outcome.stdout.rstrip('\n')
            process.stdin.close() # type: ignore

        process.wait() # type: ignore

        self.outcome.error = process.returncode # type: ignore

        if self.log == 1:
            print(f"** cmnd= {fullCmndStr}")
            if self.outcome.error:
                print(f"*** exit= {self.outcome.error}")
            if self.outcome.stdout:
                print(f"*** stdout= {self.outcome.stdout}")
            if self.outcome.stderr:
                print(f"*** stderr= {self.outcome.stderr}")

        return self.outcome


    #@io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def exec(
            self,
            cmndStr,
            stdin=None,
    ):
        """
    subprocess.Popen() -- shell=True, runs cmndStr in bash.
** TODO This should be renamed to subProc_bashOutcome and subProc_bashOut should become subProc_bash.

** TODO BISOS Py Framework -- OpedSubProc -- Desired Usages:
if not (resStr := b.OpSubProc(outcome=cmndOutcome, log=1).sudoBash(
    f"a2ensite {ploneBaseDomain}.conf",
).stdOut):  return(io.eh.badOutcome(cmndOutcome))

if b.OpSubProc(outcome=cmndOutcome, cd=someDirBase, log=1).bash(
    f"a2ensite {ploneBaseDomain}.conf",
).isProblematic():  return(io.eh.badOutcome(cmndOutcome))
        """
        if not self.outcome:
            self.outcome = b.op.Outcome()

        if not stdin:
            stdin = ""

        self.outcome.stdcmnd = cmndStr
        try:
            process = subprocess.Popen(
                cmndStr,
                encoding='utf8',
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except OSError as exception:
            self.outcome.error = exception
            print(exception)
        else:
            self.outcome.stdout, self.outcome.stderr = process.communicate(input=format(stdin.encode()))
            process.stdin.close() # type: ignore

        process.wait() # type: ignore

        self.outcome.error = process.returncode # type: ignore

        return self.outcome


#
# NOTYET, we should do sameInstance b.instantiate.same(x)
#
opLog = Op(log=1,)

opSilent = Op()



####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :title " ~End Of Editable Text~ "
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _ ~End Of Editable Text~ _: |]]    [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/bisos/apps/defaults/software/plusOrg/dblock/inserts/endOfFileControls.org"
#+STARTUP: showall
####+END:
