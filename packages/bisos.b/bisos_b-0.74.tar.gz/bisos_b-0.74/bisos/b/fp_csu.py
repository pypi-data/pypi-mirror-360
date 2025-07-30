# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CS-Unit= to capture fp.py
#+end_org """

####+BEGIN: b:py3:cs:file/dblockControls :classification "cs-u"
""" #+begin_org
* [[elisp:(org-cycle)][| /Control Parameters Of This File/ |]] :: dblk ctrls classifications=cs-u
#+BEGIN_SRC emacs-lisp
(setq-local b:dblockControls t) ; (setq-local b:dblockControls nil)
(put 'b:dblockControls 'py3:cs:Classification "cs-u") ; one of cs-mu, cs-u, cs-lib, bpf-lib, pyLibPure
#+END_SRC
#+RESULTS:
: cs-u
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
** This File: /l/b/fp_csu.py
** File True Name: /bisos/git/auth/bxRepos/bisos-pip/b/py3/bisos/b/fp_csu.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:py3:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['fp_csu'], }
csInfo['version'] = '202503095420'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'fp_csu-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/COMEEGA/_nodeBase_/fullUsagePanel-en.org][BISOS COMEEGA Panel]]
This a =Cs-Unit= for running the equivalent of facter in py and remotely with rpyc.
With BISOS, it is used in CMDB remotely.

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

####+BEGIN: b:py3:cs:orgItem/basic :type "=PyImports= "  :title "*Py Library IMPORTS*" :comment "-- Framework and External Packages Imports"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =PyImports=  [[elisp:(outline-show-subtree+toggle)][||]] *Py Library IMPORTS* -- Framework and External Packages Imports  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

# import os
import collections
# import pathlib
# import invoke

####+BEGIN: b:py3:cs:framework/imports :basedOn "classification"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] *Imports* =Based on Classification=cs-u=
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io
from bisos.common import csParam

import collections
####+END:

from bisos.facter import facter
from bisos.banna import bannaPortNu

import pathlib

import os

####+BEGIN: b:py3:cs:orgItem/basic :type "=Executes=  "  :title "CSU-Lib Executions" :comment "-- cs.invOutcomeReportControl"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =Executes=   [[elisp:(outline-show-subtree+toggle)][||]] CSU-Lib Executions -- cs.invOutcomeReportControl  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

cs.invOutcomeReportControl(cmnd=True)


####+BEGIN: bx:dblock:python:section :title "Common Parameters Specification"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Common Parameters Specification*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:

####+BEGIN: bx:dblock:python:func :funcName "commonParamsSpecify" :funcType "ParSpec" :retType "" :deco "" :argsList "icmParams"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-ParSpec  [[elisp:(outline-show-subtree+toggle)][||]] /commonParamsSpecify/ retType= argsList=(icmParams)  [[elisp:(org-cycle)][| ]]
#+end_org """
def commonParamsSpecify(
    icmParams,
):
####+END:
    icmParams.parDictAdd(
        parName='fpBase',
        parDescription="File Parameters Directory Base Path.",
        parDataType=None,
        parDefault=None,
        parChoices=list(),
        #parScope=icm.ICM_ParamScope.TargetParam,  # type: ignore
        argparseShortOpt=None,
        argparseLongOpt='--fpBase',
    )

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Direct Command Services" :anchor ""  :extraInfo "Examples and CSs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Direct Command Services_: |]]  Examples and CSs  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "examples_csu" :extent "verify" :ro "noCli" :comment "FrameWrk: CS-Main-Examples" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<examples_csu>>  *FrameWrk: CS-Main-Examples*  =verify= ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class examples_csu(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}
    rtInvConstraints = cs.rtInvoker.RtInvoker.new_noRo() # NO RO From CLI

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:
        """FrameWrk: CS-Main-Examples"""
        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
####+END:

        od = collections.OrderedDict
        cmnd = cs.examples.cmndEnter
        literal = cs.examples.execInsert

        fileParamPath = "/tmp/fpExampleBase"

        paramValueFile1 = "/etc/motd"

        paramName1 = "somePar"
        fileParamFullPath1 = f"{fileParamPath}/{paramName1}"
        paramValue1 = "someValue"

        paramName2 = "someOtherPar"
        fileParamFullPath2 = f"{fileParamPath}/{paramName2}"
        paramValue2 = "someOtherValue"

        fpPathNameValueArgs1 = f"{fileParamPath} {paramName1} {paramValue1}"
        fpPathNameValueArgs2 = f"{fileParamPath} {paramName2} {paramValue2}"

        fpFullPathValueArgs1 = f"{fileParamFullPath1} {paramValue1}"
        fpFullPathValueArgs2 = f"{fileParamFullPath2} {paramValue2}"

        fpPathNameArgs1 = f"{fileParamPath} {paramName1}"
        fpPathNameArgs2 = f"{fileParamPath} {paramName2}"

        cs.examples.menuChapter('=Write One File Parameter:: (args: fpBase paramName paramValue)=')

        cmnd('fileParamWrite', args=fpPathNameValueArgs1, comment="# maps to b.fp.FileParamWriteTo(parRoot, name, value)")
        cmnd('fileParamWrite', args=fpPathNameValueArgs2, comment="# maps to b.fp.FileParamWriteTo(parRoot, name, value)")

        cs.examples.menuSection('*Write One File Parameter:: (args: fpFullPath paramValue)*')

        cmnd('fileParamWritePath', args=fpFullPathValueArgs1, comment="# maps to b.fp.FileParamWriteToPath(parPath, value)")

        cs.examples.menuSection('*Write One FilePar With Content of File*')

        cmnd('fileParamWriteFromFile', args=f"{fileParamPath} {paramName1}  {paramValueFile1}", comment="# Real Usage is Questionable")

        cs.examples.menuChapter('=Read One File Parameter:: (args: fpBase paramName)=')

        cmnd('fileParamRead', args=fpPathNameArgs1, comment="# maps to b.fp.FileParamReadFrom(parRoot, name)" )
        cmnd('fileParamRead', args=fpPathNameArgs2, comment="# maps to b.fp.FileParamReadFrom(parRoot, name)" )

        cs.examples.menuSection('*Read One File Parameter With Path:: (args: fileParamFullPath)*')

        cmnd('fileParamReadPath', args=fileParamFullPath1)

        cs.examples.menuChapter('=Read File Parameters Dictionary=')

        cmnd('fileParamDictRead', args=fileParamPath, comment="# Dict of parName:FileParam -- not Values")
        cmnd('fileParamDictReadWop', args=fileParamPath, comment="# Dict of parName:FileParam -- WrappedOp")

        cmnd('fileParamDictReadDeep', args=fileParamPath, comment="# Dict of path:value")

        examplesFpBase(fpBase=pathlib.Path(fileParamPath), parName=paramName1, parValue=paramValue1)

        return(cmndOutcome)

####+BEGIN: b:py3:cs:func/typing :funcName "examplesFpBase" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /examplesFpBase/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def examplesFpBase(
####+END:
        fpBase: os.PathLike,
        parName: str = "",
        parValue: str = "",
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    od = collections.OrderedDict
    cmnd = cs.examples.cmndEnter
    literal = cs.examples.execInsert

    if not fpBase.is_dir():
        print(f"Missing {fpBase} -- creating it.")
        fpBase.mkdir(exist_ok=True)


    fpBasePars = od([('fpBase', fpBase),])

    cs.examples.menuChapter('=fpBase Set/Get File Parameter=')

    if parValue != "":
        cmnd('fpBaseWrite',  pars=fpBasePars, args=f"{parName} {parValue}", comment="# Write ONE fileParam Value")

    if parName != "":
        cmnd('fpBaseRead', pars=fpBasePars, args=parName, comment="# Read Value of ONE Named fileParam")
        cmnd('fpBaseParsGetAsDictValue', pars=fpBasePars, args=parName, comment=f"# Read {parName} as dict name:values")

    cmnd('fpBaseParsGetAsDictValue', pars=fpBasePars, comment="| pyLiteralTo.cs -i stdinToBlack  # Read as dict ALL name:values")

    cmnd('fpBaseDictRead', pars=fpBasePars, comment="# Dict of parName:FileParam -- not Values")

    cmnd('fpBaseDictReadDeep', pars=fpBasePars, comment="| pyLiteralTo.cs -i stdinToBlack  # Dict of path:value")


####+BEGIN: b:py3:cs:orgItem/section :title "CS-Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS-Commands*   [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fpBaseWrite" :comment "" :extent "verify" :ro "cli" :parsMand "fpBase" :parsOpt "" :argsMin 2 :argsMax 2 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fpBaseWrite>>  =verify= parsMand=fpBase argsMin=2 argsMax=2 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fpBaseWrite(cs.Cmnd):
    cmndParamsMandatory = [ 'fpBase', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 2, 'Max': 2,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             fpBase: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'fpBase': fpBase, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        fpBase = csParam.mappedValue('fpBase', fpBase)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  maps to b.fp.FileParamWriteTo(parRoot, name, value)
        #+end_org """)

        parRoot = fpBase

        parName = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        if not parName: return(b_io.eh.badOutcome(cmndOutcome))

        parValue = self.cmndArgsGet("1", cmndArgsSpecDict, argsList)
        if not parValue: return(b_io.eh.badOutcome(cmndOutcome))

        opResults = b.fp.FileParamWriteTo(
            parRoot=parRoot,
            parName=parName,
            parValue=parValue,
        )
        return cmndOutcome.set(opResults=opResults,)

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """  #+begin_org
*** [[elisp:(org-cycle)][| *cmndArgsSpec:* | ]] arg0 is ~inFile~
        #+end_org """

        cmndArgsSpecDict = cs.arg.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0",
            argName="parName",
            argDescription="Name of baseDir of fileParam"
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="1",
            argName="parValue",
            argDefault=None,
            argChoices=[],
            argDescription="Value to be assigned to fileParam"
        )

        return cmndArgsSpecDict




####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fileParamWrite" :comment "" :extent "verify" :ro "cli" :parsMand "" :parsOpt "" :argsMin 3 :argsMax 3 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fileParamWrite>>  =verify= argsMin=3 argsMax=3 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fileParamWrite(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 3, 'Max': 3,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  maps to b.fp.FileParamWriteTo(parRoot, name, value)
        #+end_org """)

        parRoot = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        if not parRoot: return(b_io.eh.badOutcome(cmndOutcome))

        parName = self.cmndArgsGet("1", cmndArgsSpecDict, argsList)
        if not parName: return(b_io.eh.badOutcome(cmndOutcome))

        parValue = self.cmndArgsGet("2", cmndArgsSpecDict, argsList)
        # parVale can be an empty string -- if not parValue: return(b_io.eh.badOutcome(cmndOutcome))

        opResults = b.fp.FileParamWriteTo(
            parRoot=parRoot,
            parName=parName,
            parValue=parValue,
        )

        # return cmndOutcome.set(opResults=opResults,)
        return cmndOutcome.set(opResults=None,)

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """  #+begin_org
*** [[elisp:(org-cycle)][| *cmndArgsSpec:* | ]] arg0 is ~inFile~
        #+end_org """

        cmndArgsSpecDict = cs.arg.CmndArgsSpecDict()

        cmndArgsSpecDict.argsDictAdd(
            argPosition="0",
            argName="parRoot",
            argDescription="Path to directory in which ~parName~ will be created"
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="1",
            argName="parName",
            argDescription="Name of baseDir of fileParam"
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="2",
            argName="parValue",
            argDefault=None,
            argChoices=[],
            argDescription="Value to be assigned to fileParam"
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fileParamWritePath" :comment "" :extent "verify" :ro "cli" :parsMand "" :parsOpt "" :argsMin 2 :argsMax 2 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fileParamWritePath>>  =verify= argsMin=2 argsMax=2 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fileParamWritePath(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 2, 'Max': 2,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Maps to pyFunc:  b.fp.FileParamWriteToPath
        #+end_org """)

        parNameFullPath = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        if not parNameFullPath: return(b_io.eh.badOutcome(cmndOutcome))

        parValue = self.cmndArgsGet("1", cmndArgsSpecDict, argsList)
        if not parValue: return(b_io.eh.badOutcome(cmndOutcome))

        opResults = b.fp.FileParamWriteToPath(
            parNameFullPath=parNameFullPath,
            parValue=parValue,
        )

        return cmndOutcome.set(opResults=opResults,)

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """  #+begin_org
*** [[elisp:(org-cycle)][| *cmndArgsSpec:* | ]] arg0 is ~inFile~
        #+end_org """

        cmndArgsSpecDict = cs.arg.CmndArgsSpecDict()

        cmndArgsSpecDict.argsDictAdd(
            argPosition="0",
            argName="parNameFullPath",
            argDescription="Full path of fileParam"
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="1",
            argName="parValue",
            argDescription="Value to be assigned"
        )

        return cmndArgsSpecDict



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fileParamWriteFromFile" :comment "" :extent "verify" :ro "cli" :parsMand "" :parsOpt "" :argsMin 3 :argsMax 3 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fileParamWriteFromFile>>  =verify= argsMin=3 argsMax=3 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fileParamWriteFromFile(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 3, 'Max': 3,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Value taken from file. Maps to: b.fp.FileParamWriteToFromFile
        #+end_org """)

        parRoot = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        if not parRoot: return(b_io.eh.badOutcome(cmndOutcome))

        parName = self.cmndArgsGet("1", cmndArgsSpecDict, argsList)
        if not parName: return(b_io.eh.badOutcome(cmndOutcome))

        parValueFile = self.cmndArgsGet("2", cmndArgsSpecDict, argsList)
        if not parValueFile: return(b_io.eh.badOutcome(cmndOutcome))

        opResults = b.fp.FileParamWriteToFromFile(
            parRoot=parRoot,
            parName=parName,
            parValueFile=parValueFile,
        )

        return cmndOutcome.set(opResults=opResults,)

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """  #+begin_org
*** [[elisp:(org-cycle)][| *cmndArgsSpec:* | ]] arg0 is ~inFile~
        #+end_org """

        cmndArgsSpecDict = cs.arg.CmndArgsSpecDict()

        cmndArgsSpecDict.argsDictAdd(
            argPosition="0",
            argName="parRoot",
            argDescription="Root"
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="1",
            argName="parName",
            argDescription="Name"
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="2",
            argName="parValueFile",
            argDescription="Value"
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:orgItem/section :title "CS-Commands For fileParamRead"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS-Commands For fileParamRead*   [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fpBaseRead" :comment "" :extent "verify" :ro "cli" :parsMand "fpBase" :parsOpt "" :argsMin 1 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fpBaseRead>>  =verify= parsMand=fpBase argsMin=1 argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fpBaseRead(cs.Cmnd):
    cmndParamsMandatory = [ 'fpBase', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             fpBase: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'fpBase': fpBase, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        fpBase = csParam.mappedValue('fpBase', fpBase)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  arg0 is ~inPypiPkg~.
*** NOTYET, Problem. If there is only one version available, there is no LATEST
        #+end_org """)

        parRoot = fpBase

        parName = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        if not parName: return(b_io.eh.badOutcome(cmndOutcome))

        try:
            fileParam = b.fp.FileParamReadFrom(
                parRoot=parRoot,
                parName=parName,
            )
        except IOError:
            cmndOutcome.set(opError="IOError", opErrInfo=f"Missing parRoot={parRoot} parName={parName}")
            return failed(cmndOutcome)

        # print((fileParam.parValueGet()))

        return cmndOutcome.set(opResults=fileParam.parValueGet(),)

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """  #+begin_org
*** [[elisp:(org-cycle)][| *cmndArgsSpec:* | ]] arg0 is ~inFile~
        #+end_org """

        cmndArgsSpecDict = cs.arg.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0",
            argName="parName",
            argDescription="Name"
        )
        
        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fpBaseParsGetAsDictValue" :comment "" :extent "verify" :ro "cli" :parsMand "fpBase" :parsOpt "" :argsMin 0 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fpBaseParsGetAsDictValue>>  =verify= parsMand=fpBase argsMax=9999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fpBaseParsGetAsDictValue(cs.Cmnd):
    cmndParamsMandatory = [ 'fpBase', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             fpBase: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'fpBase': fpBase, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        fpBase = csParam.mappedValue('fpBase', fpBase)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  arg0 is ~inPypiPkg~.
*** NOTYET, Problem. If there is only one version available, there is no LATEST
        #+end_org """)


        parNamesList = argsList

        try:
            if not pathlib.Path(fpBase).exists():
                return failed(cmndOutcome)
        except:
            print(fpBase)
            return failed(cmndOutcome)

        return  ( b.fp.parsGetAsDictValue_wOp(parNamesList, fpBase, cmndOutcome) )


####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """  #+begin_org
*** [[elisp:(org-cycle)][| *cmndArgsSpec:* | ]] arg0 is ~inFile~
        #+end_org """

        cmndArgsSpecDict = cs.arg.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&9999",
            argName="parNamesList",

        )
        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fileParamRead" :comment "" :extent "verify" :ro "cli" :parsMand "" :parsOpt "" :argsMin 2 :argsMax 3 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fileParamRead>>  =verify= argsMin=2 argsMax=3 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fileParamRead(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 2, 'Max': 3,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  arg0 is ~inPypiPkg~.
*** NOTYET, Problem. If there is only one version available, there is no LATEST
        #+end_org """)

        parRoot = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        if not parRoot: return(b_io.eh.badOutcome(cmndOutcome))

        parName = self.cmndArgsGet("1", cmndArgsSpecDict, argsList)
        if not parName: return(b_io.eh.badOutcome(cmndOutcome))

        try:
            fileParam = b.fp.FileParamReadFrom(
                parRoot=parRoot,
                parName=parName,
            )
        except IOError:
            cmndOutcome.set(opError="IOError", opErrInfo=f"Missing parRoot={parRoot} parName={parName}")
            return failed(cmndOutcome)

        # print((fileParam.parValueGet()))

        return cmndOutcome.set(opResults=fileParam.parValueGet(),)

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """  #+begin_org
*** [[elisp:(org-cycle)][| *cmndArgsSpec:* | ]] arg0 is ~inFile~
        #+end_org """

        cmndArgsSpecDict = cs.arg.CmndArgsSpecDict()

        cmndArgsSpecDict.argsDictAdd(
            argPosition="0",
            argName="parRoot",
            argDefault=None,
            argChoices=[],
            argDescription="Path"
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="1",
            argName="parName",
            argDescription="Name"
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="2",
            argName="parVer",
            argDescription="Version, optional"
        )

        return cmndArgsSpecDict



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fileParamReadPath" :comment "" :extent "verify" :ro "cli" :parsMand "" :parsOpt "" :argsMin 1 :argsMax 2 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fileParamReadPath>>  =verify= argsMin=1 argsMax=2 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fileParamReadPath(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 2,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  arg0 is ~inPypiPkg~.
*** NOTYET, Problem. If there is only one version available, there is no LATEST
        #+end_org """)

        parRoot = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        if not parRoot: return(b_io.eh.badOutcome(cmndOutcome))

        try:
            fileParam = b.fp.FileParamReadFromPath(
                parRoot=parRoot,
            )
        except IOError:
            cmndOutcome.set(opError="IOError", opErrInfo=f"Missing parRoot={parRoot} parName={parName}")
            return failed(cmndOutcome)

        # print((fileParam.parValueGet()))

        return cmndOutcome.set(opResults=fileParam.parValueGet(),)

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """  #+begin_org
*** [[elisp:(org-cycle)][| *cmndArgsSpec:* | ]] arg0 is ~inFile~
        #+end_org """

        cmndArgsSpecDict = cs.arg.CmndArgsSpecDict()

        cmndArgsSpecDict.argsDictAdd(
            argPosition="0",
            argName="parRoot",
            argDescription="Path"
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="1",
            argName="parVer",
            argDescription="Version. Optional"
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:orgItem/section :title "CS-Commands For fileParamDictRead"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS-Commands For fileParamDictRead*   [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fpBaseDictRead" :comment "" :extent "verify" :ro "cli" :parsMand "fpBase" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fpBaseDictRead>>  =verify= parsMand=fpBase ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fpBaseDictRead(cs.Cmnd):
    cmndParamsMandatory = [ 'fpBase', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             fpBase: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'fpBase': fpBase, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        fpBase = csParam.mappedValue('fpBase', fpBase)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Reads and recurses through all FPs.
*** When interactive, also prints out parValues as read.
        #+end_org """)

        # Interactive py invokation
        return fileParamDictReadWop().pyCmnd(rtInv=rtInv, argsList=[fpBase])

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fileParamDictRead" :comment "" :extent "verify" :ro "cli" :parsMand "" :parsOpt "" :argsMin 1 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fileParamDictRead>>  =verify= argsMin=1 argsMax=9999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fileParamDictRead(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Reads and recurses through all FPs.
*** When interactive, also prints out parValues as read.
        #+end_org """)

        if argsList is None:
            return failed(cmndOutcome)

        for fpBase in argsList:
            try:
                if not pathlib.Path(fpBase).exists():
                    return failed(cmndOutcome)
            except:
                return failed(cmndOutcome)

            blankParDictObj  = b.fp.FileParamDict()
            thisParamDict = blankParDictObj.readFrom(path=fpBase)
            b_io.tm.here(f"path={fpBase}")

            if thisParamDict == None:
                b_io.ann.write("Problem usageError thisParamDict == None")
                return (cmndOutcome)

            if rtInv.outs:
                 b_io.ann.write(fpBase)
                 b.fp.FILE_paramDictPrint(thisParamDict)

            return cmndOutcome.set(
                # opError=cs.OpError.Success,
                opResults=thisParamDict,
            )

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """  #+begin_org
*** [[elisp:(org-cycle)][| *cmndArgsSpec:* | ]] arg0 is ~inFile~
        #+end_org """

        cmndArgsSpecDict = cs.arg.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&9999",
            argName="fpBases",

        )
        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fileParamDictReadWop" :comment "" :extent "verify" :ro "cli" :parsMand "" :parsOpt "" :argsMin 1 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fileParamDictReadWop>>  =verify= argsMin=1 argsMax=9999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fileParamDictReadWop(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Reads and recurses through all FPs.
*** When interactive, also prints out parValues as read.
        #+end_org """)

        if argsList is None:
            return failed(cmndOutcome)

        for fpBase in argsList:
            try:
                if not pathlib.Path(fpBase).exists():
                    return failed(cmndOutcome)
            except:
                return failed(cmndOutcome)

            # b.fp.readTreeAtBaseDir_wOp(fpBase, cmndOutcome)
            cmndOutcome = b.fp.readTreeAtBaseDir_wOp(fpBase,)

            if rtInv.outs:
                 b_io.ann.write(fpBase)
                 b.fp.FILE_paramDictPrint(cmndOutcome.results)

            return ( cmndOutcome )


####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """  #+begin_org
*** [[elisp:(org-cycle)][| *cmndArgsSpec:* | ]] arg0 is ~inFile~
        #+end_org """

        cmndArgsSpecDict = cs.arg.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&9999",
            argName="fpBases",

        )
        return cmndArgsSpecDict




####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fpBaseDictReadDeep" :comment "" :extent "verify" :ro "cli" :parsMand "fpBase" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fpBaseDictReadDeep>>  =verify= parsMand=fpBase ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fpBaseDictReadDeep(cs.Cmnd):
    cmndParamsMandatory = [ 'fpBase', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             fpBase: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'fpBase': fpBase, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        fpBase = csParam.mappedValue('fpBase', fpBase)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Interactive py invokation of /fileParamDictReadDeep/ Command.
        #+end_org """)

        return fileParamDictReadDeep().pyCmnd(rtInv=rtInv, argsList=[fpBase])

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fileParamDictReadDeep" :comment "" :extent "verify" :ro "cli" :parsMand "" :parsOpt "" :argsMin 1 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fileParamDictReadDeep>>  =verify= argsMin=1 argsMax=9999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fileParamDictReadDeep(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  arg0 is ~inPypiPkg~.
*** NOTYET, Problem. If there is only one version available, there is no LATEST
        #+end_org """)

        results = b.fp.FILE_paramDictReadDeep(inPathList=argsList)

        return cmndOutcome.set(opResults=results,)

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """  #+begin_org
*** [[elisp:(org-cycle)][| *cmndArgsSpec:* | ]] arg0 is ~inFile~
        #+end_org """

        cmndArgsSpecDict = cs.arg.CmndArgsSpecDict()

        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&9999",
            argName="inPathList",
            argDescription="Iterated through."
        )

        return cmndArgsSpecDict



####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
