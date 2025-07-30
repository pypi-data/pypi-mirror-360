# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =PyLib+CsLib= for manipulation of File Parameters (FP). ~bisos.b.fp~
#+end_org """

####+BEGIN: b:prog:file/proclamations :outLevel 1
""" #+begin_org
* *[[elisp:(org-cycle)][| Proclamations |]]* :: Libre-Halaal Software --- Part Of Blee ---  Poly-COMEEGA Format.
** This is Libre-Halaal Software. © Libre-Halaal Foundation. Subject to AGPL.
** It is not part of Emacs. It is part of Blee.
** Best read and edited  with Poly-COMEEGA (Polymode Colaborative Org-Mode Enhance Emacs Generalized Authorship)
#+end_org """
####+END:

####+BEGIN: b:prog:file/particulars :authors ("./inserts/authors-mb.org")
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars |]]* :: Authors, version
** This File: NOTYET
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:python:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['fp'], }
csInfo['version'] = '202209125155'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'fp-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* /[[elisp:(org-cycle)][| Description |]]/ ::  [[file:/bisos/panels/bisos-core/PyCsFwrk/bisos.b/fileParameters/fullUsagePanel-en.org][File Parameters --- BISOS.B.FP Panel]]
See panel for details.
** Status: In use with blee3
** /[[elisp:(org-cycle)][| Planned Improvements |]]/ :
*** TODO complete fileName in particulars.
#+end_org """

####+BEGIN: b:prog:file/orgTopControls :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Controls |]] :: [[elisp:(delete-other-windows)][(1)]] | [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
** /Version Control/ ::  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]]
#+end_org """
####+END:

####+BEGIN: b:python:file/workbench :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Workbench |]] :: [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pyclbr %s" (bx:buf-fname))))][pyclbr]] || [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pydoc ./%s" (bx:buf-fname))))][pydoc]] || [[elisp:(python-check (format "/bisos/pipx/bin/pyflakes %s" (bx:buf-fname)))][pyflakes]] | [[elisp:(python-check (format "/bisos/pipx/bin/pychecker %s" (bx:buf-fname))))][pychecker (executes)]] | [[elisp:(python-check (format "/bisos/pipx/bin/pycodestyle %s" (bx:buf-fname))))][pycodestyle]] | [[elisp:(python-check (format "/bisos/pipx/bin/flake8 %s" (bx:buf-fname))))][flake8]] | [[elisp:(python-check (format "/bisos/pipx/bin/pylint %s" (bx:buf-fname))))][pylint]]  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: bx:cs:python:icmItem :itemType "=PyImports= " :itemTitle "*Py Library IMPORTS*"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =PyImports=  [[elisp:(outline-show-subtree+toggle)][||]] *Py Library IMPORTS*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

import typing

from bisos import b
from bisos.b import cs
from bisos.b import io
from bisos.b import io
from bisos.b import b_io
from bisos.common import csParam

from bisos.transit import pattern

import os
import collections
#import pathLib


import __main__

import abc
import sys

cmndArgs = sys.argv

import pathlib
import black

#
# NOTYET -- This is temporarily replectaed in b.fp_csu
#

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



####+BEGIN: bx:cs:py3:section :title "*Class Based Interface*"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] **Class Based Interface**  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: b:py3:class/decl :className "FpCmndParam" :superClass "" :comment "Expected to be subclassed" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /FpCmndParam/  superClass=object =Expected to be subclassed=   [[elisp:(org-cycle)][| ]]
#+end_org """
class FpCmndParam(object):
####+END:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr:* | ]] FpCmndParam combines a CmndParam with a FileParam
    #+end_org """


####+BEGIN: b:py3:cs:method/typing :methodName "__init__" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /__init__/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def __init__(
####+END:
            self,
            cmndParam: cs.CmndParam | None = None,
            fileParam: b.fp.FileParam | None = None,
    ):
        self.cmndParam = cmndParam
        self.fileParam = fileParam


####+BEGIN: b:py3:class/decl :className "BaseDir" :superClass "abc.ABC, b.fto.FILE_TreeObject" :comment "Expected to be subclassed" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /BaseDir/  superClass=abc.ABC, b.fto.FILE_TreeObject =Expected to be subclassed=   [[elisp:(org-cycle)][| ]]
#+end_org """
class BaseDir(abc.ABC, b.fto.FILE_TreeObject):
####+END:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr:* | ]] b.fpCls.BaseDir is an abstract class for combining a set of csParams with an fps base.
FP_Base is also a FILE_TreeObject.
    This class merges:
    1) A dictionary of b.cs.param.CsParams, name of the CsParam is key
    3) A set of FPs b.fp.FileParam  -- Each FP maps to a CsParam
    3) A baseDir of FPs

    In this context each b.cs.param.CsParam can have two values.
       A CsValue in the Cmnd context.
       A FpValue in the FileParms context

    fps_ indicate that we are dealing with CsParms as FPs

    get involves reading from fpBase and returning a CsParam with fpValue set
    set involves writing of CsParam to fpBase
    fetch involves getting value of fpValue

    There are two different types of use cases:

    1) FPs provide persistence for CsParams
    2) CsParams provide generic Cls based access to FPs

    (1) Use Cases FP names are same as CsParam names,
         CsParams are dumped in dir  as FPs
         CsParams are read in as FPs and then used in Cmnds
         Blee Player is an example of such use.


    (2) FPs are assigned CsParam names and then generic cmnds allow manipulation of FPs.
        Configuration Management. FPs are auto subjected to CRUD.
         Registrars on top of FPs. RegFps  builds on this class.

    Both combine FPs and CsPrams.

    Implementation is still dirty and parts that were taken from ICM has not been cleaned.

    #+end_org """

####+BEGIN: b:py3:cs:method/typing :methodName "__init__" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /__init__/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def __init__(
####+END:
            self,
            fpBase,
            ftoNode="branch", # or "leaf"
    ):
        """Representation of a FILE_TreeObject when _objectType_ is FileParamBase (a node)."""
        super().__init__(fpBase,)
        self.fps_obtainedParams = {}
        self._cmndParPrefix = ""
        self.fps_manifestDictBuild()

####+BEGIN: b:py3:cs:method/typing :methodName "baseCreate" :deco ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /baseCreate/ deco=    [[elisp:(org-cycle)][| ]]
    #+end_org """
    def baseCreate(
####+END:
            self,
    ):
        """ And captures fpsBaseName based on fpsBasePath """
        return self.nodeCreate()

####+BEGIN: b:py3:cs:method/typing :methodName "basePath_obtain" :deco ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /basePath_obtain/   [[elisp:(org-cycle)][| ]]
    #+end_org """
    def basePath_obtain(
####+END:
            self,
    ):
        """ """
        return self.fileTreeBaseGet()


####+BEGIN: b:py3:cs:method/typing :methodName "baseValidityPredicate" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /baseValidityPredicate/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def baseValidityPredicate(
####+END:
                self,
    ):
        """  """
        pass

####+BEGINNOT: b:py3:cs:method/typing :methodName "fps_asCsParamsAdd" :deco "abc.abstractmethod staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fps_asIcmParamsAdd/ deco=abc.abstractmethod staticmethod  deco=abc.abstractmethod staticmethod   [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    @abc.abstractmethod
    def fps_asCsParamsAdd(
####+END:
            csParams,
    ):
        """AbstractMethod:: Order of decorators is important -- staticmethod: takes in csParms and augments it with fileParams. returns csParams.
        Example, at a minimum provide: parName, parDescription, argparseLongOpt.
        """
        csParams.parDictAdd(
            parName='exampleFp_name',
            parDescription="Name of Bpo of the live AALS Platform",
            parDataType=None,
            parDefault=None,
            parChoices=list(),
            parScope=icm.CmndParamScope.TargetParam,  # type: ignore
            argparseShortOpt=None,
            argparseLongOpt='--exampleFp_name',
        )

        return csParams


####+BEGIN: b:py3:cs:method/typing :methodName "cmndParNameToFileParName" :deco ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /cmndParNameToFileParName/   [[elisp:(org-cycle)][| ]]
    #+end_org """
    def cmndParNameToFileParName(
####+END:
            self,
            cmndParName: str,
            csParam,
    ) -> str:
        """ Map cmndParamName
        """
        fileParName = cmndParName.removeprefix(self._cmndParPrefix)
        if csParam.fileParName is not None:
                fileParName = csParam.fileParName
        return fileParName

####+BEGIN: b:py3:cs:method/typing :methodName "fileParNameToCmndParName" :deco ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fileParNameToCmndParName/   [[elisp:(org-cycle)][| ]]
    #+end_org """
    def fileParNameToCmndParName(
####+END:
            self,
            fileParName: str,
    ) -> str:
        """ Read the cmndParName attribute of fileParName FileParam
        """
        return "NOTYET-cmndParName"


####+BEGIN: b:py3:cs:method/typing :methodName "fps_manifestDictBuild" :deco "abc.abstractmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fps_manifestDictBuild/ deco=abc.abstractmethod  deco=abc.abstractmethod   [[elisp:(org-cycle)][| ]]
    #+end_org """
    @abc.abstractmethod
    def fps_manifestDictBuild(
####+END:
            self,
    ):
        """AbstractMethod::  Example: Abstract to become ConcreteMethod based on abstract pattern
        """
        csParams = cs.G.icmParamDictGet()
        self._manifestDict = {}
        self._cmndParPrefix = "exampleFp_"
        paramsList = [
            'exampleFp_name',
        ]
        for eachParam in paramsList:
            thisCsParam = csParams.parNameFind(eachParam)   # type: ignore
            fileParName = self.cmndParNameToFileParName(eachParam, thisCsParam)
            thisFpCmndParam = b.fpCls.FpCmndParam(
                cmndParam=thisCsParam,
                fileParam=b.fp.FileParam(
                    parName=fileParName,
                    storeBase=self.basePath_obtain(),
                )
            )
            self._manifestDict[eachParam] = thisFpCmndParam

        return self._manifestDict

####+BEGIN: b:py3:cs:method/typing :methodName "fps_manifestGet" :deco ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fps_manifestGet/ deco=    [[elisp:(org-cycle)][| ]]
    #+end_org """
    def fps_manifestGet(
####+END:
            self,
    ):
        """ """
        return self._manifestDict


####+BEGIN: b:py3:cs:method/typing :methodName "fps_namesWithRelPath" :deco "classmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fps_namesWithRelPath/  deco=classmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @classmethod
    def fps_namesWithRelPath(
####+END:
            cls,
    ):
        """OBSOLETED by fps_manifestDict -- classmethod: returns a dict with fp names as key and relBasePath as value.
        The names refer to icmParams.parDictAdd(parName) of fps_asIcmParamsAdd
        """
        relBasePath = "."
        return (
            {
                'exampleFP': relBasePath,
            }
        )



####+BEGIN: b:py3:cs:method/typing :methodName "fps_namesWithAbsPath" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fps_namesWithAbsPath/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def fps_namesWithAbsPath(
####+END:
            self,
    ):
        """Obsoleted -- Uses fps_namesWithRelPath to construct absPath for relPath values. Returns a dict."""
        namesWithRelPath = self.__class__.fps_namesWithRelPath()
        namesWithAbsPath = dict()
        for eachName, eachRelPath in namesWithRelPath.items():
            namesWithAbsPath[eachName] = os.path.join(self.fileTreeBaseGet(), eachRelPath)
        return namesWithAbsPath

####+BEGIN: b:py3:cs:method/typing :methodName "fps_readTree" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fps_readTree/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def fps_readTree(
####+END:
            self,
    ):
        """Returns a dict of FileParam s. Reads in all FPs at self.fps_absBasePath()."""
        cmndOutcome = b.op.Outcome()
        FP_readTreeAtBaseDir = b.fp.FP_readTreeAtBaseDir()
        FP_readTreeAtBaseDir.cmndOutcome = cmndOutcome

        FP_readTreeAtBaseDir.cmnd(
            interactive=False,
            FPsDir=self.fileTreeBaseGet(),
        )
        if cmndOutcome.error: return cmndOutcome

        self.fps_dictParams = cmndOutcome.results
        return cmndOutcome

####+BEGIN: b:py3:cs:method/typing :methodName "fps_setParam" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fps_setParam/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def fps_setParam(
####+END:
            self,
            paramName,
            paramValue,
    ):
        """Returns a dict of FileParam s. Reads in all FPs at self.fps_absBasePath()."""
        namesWithAbsPath = self.fps_manifestDictBuild() # fps_namesWithAbsPath()
        #fpBase = namesWithAbsPath[paramName]
        fpBase = self.fileTreeBaseGet()
        b.fp.FileParamWriteTo(fpBase, paramName, paramValue)

####+BEGIN: b:py3:cs:method/typing :methodName "fps_getParam" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fps_getParam/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def fps_getParam(
####+END:
            self,
            paramName,
    ):
        """Returns a dict of FileParam s. Reads in all FPs at self.fps_absBasePath()."""
        fileCmndParams = self.fps_manifestGet()
        fpBase = self.fileTreeBaseGet()
        try:
            fileParName = self.cmndParNameToFileParName(paramName, fileCmndParams[paramName].cmndParam)
        except KeyError:
            return None
        paramValue = b.fp.FileParamReadFrom(fpBase, fileParName,)
        return paramValue

####+BEGIN: b:py3:cs:method/typing :methodName "fps_fetchParam" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fps_fetchParam/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def fps_fetchParam(
####+END:
            self,
            paramName,
    ):
        """Fetch tries class's FPs first. Then does a getParamsDict and repeats the fetch."""
        namesWithAbsPath = self.fps_namesWithAbsPath()
        #print(namesWithAbsPath)
        fpBase = os.path.abspath(namesWithAbsPath[paramName])
        #print(fpBase)
        paramValue = b.fp.FileParamReadFrom(fpBase, paramName,)
        return paramValue


####+BEGIN: b:py3:cs:method/typing :methodName "fps_getParamsDict" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fps_getParamsDict/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def fps_getParamsDict(
####+END:
            self,
            paramName,
    ):
        """Returns a dict of FileParam s. Reads in all FPs at self.fps_absBasePath()."""
        namesWithAbsPath = self.fps_manifestDictBuild()

        #print(namesWithAbsPath)
        #fpBase = os.path.abspath(namesWithAbsPath[paramName])
        fpBase = self.fileTreeBaseGet()
        #print(fpBase)
        paramValue = b.fp.FileParamReadFrom(fpBase, paramName,)
        return paramValue

####+BEGIN: b:py3:cs:method/typing :methodName "fps_getParamsAsDictValue" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fps_getParamsAsDictValue/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def fps_getParamsAsDictValue(
####+END:
            self,
            paramNamesList,
            fpsBase=None,
    ):
        """When paramNamesList == [] get all."""
        if fpsBase == None:
            fpsBase = self.fileTreeBaseGet()
        fpsDictValue =  b.fp.parsGetAsDictValue(paramNamesList, fpsBase)
        return fpsDictValue


####+BEGIN: b:py3:cs:method/typing :methodName "fps_absBasePath" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fps_absBasePath/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def fps_absBasePath(
####+END:
           self,
    ):
        return self.fileTreeBaseGet()




####+BEGIN: bx:cs:py3:section :title "CS-Lib Examples"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS-Lib Examples*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "examples_csu" :comment "" :parsMand "fpBase cls" :parsOpt "sectionTitle" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<examples_csu>>  =verify= parsMand=fpBase cls parsOpt=sectionTitle ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class examples_csu(cs.Cmnd):
    cmndParamsMandatory = [ 'fpBase', 'cls', ]
    cmndParamsOptional = [ 'sectionTitle', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             fpBase: typing.Optional[str]=None,  # Cs Mandatory Param
             cls: typing.Optional[str]=None,  # Cs Mandatory Param
             sectionTitle: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'fpBase': fpBase, 'cls': cls, 'sectionTitle': sectionTitle, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        fpBase = csParam.mappedValue('fpBase', fpBase)
        cls = csParam.mappedValue('cls', cls)
        sectionTitle = csParam.mappedValue('sectionTitle', sectionTitle)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Basic example command.
        #+end_org """)

        fpBaseInst = pattern.sameInstance(getattr(__main__, cls), fpBase=fpBase)
        fpCmndParams = fpBaseInst.fps_manifestGet()

        od = collections.OrderedDict
        cmnd = cs.examples.cmndEnter
        # literal = cs.examples.execInsert


        fpBaseClsPars = od([('fpBase', fpBase), ('cls', cls)])

        cs.examples.menuChapter('*fpsCls Access And Management -- fpCmndParam Model*')

        cmnd('fpBaseClsFullReport', pars=fpBaseClsPars, comment="# Full Get/Read Report")

        cs.examples.menuSection('*Args (not Pars) Oriented Get Set Cmnds*')

        cmnd('fpCmndParamsReveal', pars=fpBaseClsPars, args="getExamples", comment="# Interactive Use Only - Functional")
        cmnd('fpCmndParamsReveal', pars=fpBaseClsPars, args="setExamples", comment="# Interactive Use Only - Functional")
        cmnd('fpCmndParamsReveal', pars=fpBaseClsPars, args="values", comment="# Interactive Use Only - Incomplete")
        cmnd('fpCmndParamsReveal', pars=fpBaseClsPars, args="all", comment="# Interactive Use Only - Functional ")

        cs.examples.menuSection('*fpsCls Set FileParam with CmndParam --  fpCmndParam Model*')

        cmnd('fpCmndParamsSetAllInit', pars=fpBaseClsPars, comment="# Initialize ALL fpCmndParams")

        for eachParam in fpCmndParams:
            eachCmndParam = od([('fpBase', fpBase), ('cls', cls), (f'{eachParam}', "TBD-Value")])
            cmnd('fpCmndParamsSet', pars=eachCmndParam, comment="# Set FileParam using CmndParam")

        cs.examples.menuSection('*fpsCls /Get/ FileParam with CmndParam --  fpCmndParam Model*')

        cmnd('fpCmndParamsGetAll', pars=fpBaseClsPars, comment="| pyLiteralTo.cs -i stdinToBlack  # Get ALL fpCmndParams")

        for eachParam in fpCmndParams:
            eachCmndParam = od([('fpBase', fpBase), ('cls', cls), (f'{eachParam}', "")])
            cmnd('fpCmndParamsGet', pars=eachCmndParam, comment="# Get FileParam using CmndParam")

        cs.examples.menuChapter('*fpsCls Access And Management -- at fpBase Pure Model*')

        b.fp_csu.examplesFpBase(pathlib.Path(fpBase),)

        return(cmndOutcome)

        # cmnd('fpParamsSetDefaults', pars=fpBaseClsPars, comment="# List FPs")

        # cmnd('fpParamsRead', pars=fpBaseClsPars, comment="# List FPs")
        # cmnd('fpParamsRead', pars=fpBaseClsPars, args="basic setExamples getExamples", comment="# List FPs")


        # cs.examples.menuChapter('*Revival Process*')

        # cmnd('fpParamsList', pars=fpBaseClsPars, comment="# List FPs")
        # cmnd('fpParamsList', pars=fpBaseClsPars, args="basic setExamples getExamples", comment="# List FPs")


        # cmnd('fpParamsInfoDict', pars=fpBaseClsPars, comment="# List FPs")
        # cmnd('fpParamsValueDict', pars=fpBaseClsPars, comment="# List FPs")
        # cmnd('fpParamsSet', pars=fpBaseClsPars, comment="# List FPs")
        # cmnd('fpParamSetWithNameValue', pars=fpBaseClsPars, args="parName parValue", comment="# WORKS")
        # cmnd('fpParamGetWithName', pars=fpBaseClsPars, args="parName", comment="# WORKS")
        # cmnd('fpParamsSetDefaults', pars=fpBaseClsPars, comment="# KeyError: 'exampleFP'")
        # cmnd('fpParamsRead', pars=fpBaseClsPars, comment="# List FPs")

        # literal("facter networking.interfaces.lo.bindings[0].address  # Fails, you can't do that")

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CmndSvcs" :anchor ""  :extraInfo "File Parameters Get/Set -- Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CmndSvcs_: |]]  File Parameters Get/Set -- Commands  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fpBaseClsFullReport" :extent "verify" :parsMand "fpBase cls" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fpBaseClsFullReport>>  =verify= parsMand=fpBase cls ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fpBaseClsFullReport(cs.Cmnd):
    cmndParamsMandatory = [ 'fpBase', 'cls', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             fpBase: typing.Optional[str]=None,  # Cs Mandatory Param
             cls: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'fpBase': fpBase, 'cls': cls, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        fpBase = csParam.mappedValue('fpBase', fpBase)
        cls = csParam.mappedValue('cls', cls)
####+END:

        if rtInv.outs:
            print(f"fpBase={fpBase}")
            print(f"cls={cls}\n")

        cmndOutcome = fpCmndParamsGetAll().pyCmnd(fpBase=fpBase, cls=cls)
        result = black.format_str(str(cmndOutcome.results), mode=black.Mode())
        if rtInv.outs:
            print("b.fpCls.fpCmndParamsGetAll()::")
            print(result)

        cmndOutcome = b.fp_csu.fpBaseParsGetAsDictValue().pyCmnd(fpBase=fpBase,)
        result = black.format_str(str(cmndOutcome.results), mode=black.Mode())
        if rtInv.outs:
            print("b.fp_csu.fpBaseParsGetAsDictValue()::")
            print(result)

        cmndOutcome = b.fp_csu.fpBaseDictReadDeep().pyCmnd(fpBase=fpBase,)
        result = black.format_str(str(cmndOutcome.results), mode=black.Mode())
        if rtInv.outs:
            print("b.fp_csu.fpBaseDictReadDeep()::")
            print(result)
            

        return cmndOutcome.set(opResults=None)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fpCmndParamsReveal" :extent "verify" :parsMand "fpBase cls" :parsOpt "" :argsMin 0 :argsMax 3 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fpCmndParamsReveal>>  =verify= parsMand=fpBase cls argsMax=3 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fpCmndParamsReveal(cs.Cmnd):
    cmndParamsMandatory = [ 'fpBase', 'cls', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 3,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             fpBase: typing.Optional[str]=None,  # Cs Mandatory Param
             cls: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'fpBase': fpBase, 'cls': cls, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        fpBase = csParam.mappedValue('fpBase', fpBase)
        cls = csParam.mappedValue('cls', cls)
####+END:

        fpBaseInst = b.pattern.sameInstance(getattr(__main__, cls), fpBase=fpBase)

        fpCmndParamDict = fpBaseInst.fps_manifestDictBuild()

        # print(f"AAA {fpBase} {cls} {fps_namesWithAbsPath}")

        cmndArgsSpecDict = self.cmndArgsSpec()

        #if interactive:
        if True:
            formatTypes = self.cmndArgsGet("0&3", cmndArgsSpecDict, argsList)
        else:
            formatTypes = argsList

        if formatTypes:
            if formatTypes[0] == "all":
                    cmndArgsSpec = cmndArgsSpecDict.argPositionFind("0&2")
                    argChoices = cmndArgsSpec.argChoicesGet()
                    argChoices.pop(0)
                    formatTypes = argChoices

        for each in formatTypes:    # type: ignore
            if each == 'values':
                FP_listCsParams(fpCmndParamDict,)
            elif each == 'getExamples':
                menu_getExamples(fpBaseInst,)
            elif each == 'setExamples':
                # print("Set Examples Come Here")
                menu_setExamples(fpBaseInst,)
            else:
                io.eh.problem_usageError(f"Unknown {each}")

        return cmndOutcome

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """
***** Cmnd Args Specification
"""
        cmndArgsSpecDict = cs.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&2",
            argName="formatTypes",
            argDefault="all",
            argChoices=['all', 'values', 'setExamples', 'getExamples'],
            argDescription="Action to be specified by rest"
        )

        return cmndArgsSpecDict


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CmndSvcs" :anchor ""  :extraInfo "FileParam As CmndParam Model Set -- Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CmndSvcs_: |]]  FileParam As CmndParam Model Set -- Commands  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fpCmndParamsSetAllInit" :parsMand "fpBase cls" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fpCmndParamsSetAllInit>>  =verify= parsMand=fpBase cls ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fpCmndParamsSetAllInit(cs.Cmnd):
    cmndParamsMandatory = [ 'fpBase', 'cls', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             fpBase: typing.Optional[str]=None,  # Cs Mandatory Param
             cls: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'fpBase': fpBase, 'cls': cls, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        fpBase = csParam.mappedValue('fpBase', fpBase)
        cls = csParam.mappedValue('cls', cls)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Walk through all the fpCmndParams and set them to CsParam.fileParInit using CsParam.writeAsFileParam.
        #+end_org """)

        fpBaseInst = pattern.sameInstance(getattr(__main__, cls), fpBase=fpBase)
        fpCmndParams = fpBaseInst.fps_manifestDictBuild()
        # fpCmndParams = fpBaseInst.fps_manifestGet()

        for eachParam, fpCmndParam  in fpCmndParams.items():
            thisCsParam = fpCmndParam.cmndParam
            thisFileParam = fpCmndParam.fileParam
            thisCsParam.fileParName = thisFileParam.parNameGet()
            fileParInit = thisCsParam.fileParInit
            thisCsParam.parValueSet(fileParInit)
            thisCsParam.writeAsFileParam(parRoot=str(fpCmndParam.fileParam.parBaseGet()))

        return cmndOutcome

    
####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fpCmndParamsSet" :parsMand "fpBase cls" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fpCmndParamsSet>>  =verify= parsMand=fpBase cls ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fpCmndParamsSet(cs.Cmnd):
    cmndParamsMandatory = [ 'fpBase', 'cls', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             fpBase: typing.Optional[str]=None,  # Cs Mandatory Param
             cls: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'fpBase': fpBase, 'cls': cls, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        fpBase = csParam.mappedValue('fpBase', fpBase)
        cls = csParam.mappedValue('cls', cls)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]fpCmndParams and their values are taken from cmndLine and are set accordingly.
        #+end_org """)


        fpBaseInst = pattern.sameInstance(getattr(__main__, cls), fpBase=fpBase)
        fpCmndParams = fpBaseInst.fps_manifestGet()

        G = cs.globalContext.get()
        csParams = G.icmParamDictGet()
        csRunArgs = G.icmRunArgsGet() #; cs.unusedSuppressForEval(csRunArgs)

        cmndParamsDict = dict()

        missingRunArgs = True

        # Read from cmndLine into callParamsDict
        for eachKey in fpCmndParams:
            cmndParamsDict[eachKey] = None
            try:
                exec("cmndParamsDict[eachKey] = csRunArgs." + eachKey)
            except AttributeError:
                continue

            if cmndParamsDict[eachKey] is not None:
                # At least one was specified.
                missingRunArgs = False

        if missingRunArgs == True:
            print("NOTYET: Usage Problem: Missing  Parameter")

        # Write relevant cmndParams as fileParams
        for eachParam, fpCmndParam  in fpCmndParams.items():
            # print(f"{eachParam}, {eachDest}")
            if cmndParamsDict[eachParam]:
                thisCsParam = csParams.parNameFind(eachParam)   # type: ignore
                thisCsParam.parValueSet(cmndParamsDict[eachParam])
                # print(fpCmndParam.fileParam)
                # print(fpCmndParam.fileParam.parBaseGet())
                # print(thisCsParam)
                thisCsParam.writeAsFileParam(parRoot=str(fpCmndParam.fileParam.parBaseGet()))


        #print(fpBaseInst.basePath_obtain())

        return cmndOutcome


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CmndSvcs" :anchor ""  :extraInfo "FileParam As CmndParam Model Get  -- Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CmndSvcs_: |]]  FileParam As CmndParam Model Set -- Commands  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fpCmndParamsGetAll" :parsMand "fpBase cls" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fpCmndParamsGetAll>>  =verify= parsMand=fpBase cls ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fpCmndParamsGetAll(cs.Cmnd):
    cmndParamsMandatory = [ 'fpBase', 'cls', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             fpBase: typing.Optional[str]=None,  # Cs Mandatory Param
             cls: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'fpBase': fpBase, 'cls': cls, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        fpBase = csParam.mappedValue('fpBase', fpBase)
        cls = csParam.mappedValue('cls', cls)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Walk through fpCmndParams of {cls}, obtain their vaues and return it as dict.
        #+end_org """)

        fpBaseInst = pattern.sameInstance(getattr(__main__, cls), fpBase=fpBase)
        fpCmndParams = fpBaseInst.fps_manifestGet()

        results = dict()

        for eachParam in fpCmndParams:
            paramValue = fpBaseInst.fps_getParam(eachParam,).parValueGet()
            results[eachParam] = paramValue

        cmndOutcome.results = results

        return cmndOutcome


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fpCmndParamsGet" :parsMand "fpBase cls" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fpCmndParamsGet>>  =verify= parsMand=fpBase cls ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fpCmndParamsGet(cs.Cmnd):
    cmndParamsMandatory = [ 'fpBase', 'cls', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             fpBase: typing.Optional[str]=None,  # Cs Mandatory Param
             cls: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'fpBase': fpBase, 'cls': cls, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        fpBase = csParam.mappedValue('fpBase', fpBase)
        cls = csParam.mappedValue('cls', cls)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] look in cmndArgs=sys.argv and find specified fpCmndParams. Obtain those values and return as dict.
        #+end_org """)

        fpBaseInst = pattern.sameInstance(getattr(__main__, cls), fpBase=fpBase)
        fpCmndParams = fpBaseInst.fps_manifestGet()

        G = cs.globalContext.get()
        csParams = G.icmParamDictGet()
        csRunArgs = G.icmRunArgsGet() #; cs.unusedSuppressForEval(csRunArgs)

        cmndParamsDict = dict()
        missingRunArgs = True

        # Read from cmndLine into callParamsDict
        for eachKey in fpCmndParams:
            for eachArg in cmndArgs:
                # print(f"{eachKey} {eachArg}")
                if f"--{eachKey}=" == eachArg:
                    cmndParamsDict[eachKey] = "Present"
                    missingRunArgs = False

        if missingRunArgs == True:
            print("NOTYET: Usage Problem: Missing  Parameter")
            return failed(cmndOutcome)

        results = dict()

        # Write relevant cmndParams as fileParams
        for eachParam, eachValue  in cmndParamsDict.items():
            paramValue = fpBaseInst.fps_getParam(eachParam,).parValueGet()
            results[eachParam] = paramValue

        cmndOutcome.results = results

        return cmndOutcome

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CmndSvcs" :anchor ""  :extraInfo "FileParam Pure  Model -- Set Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CmndSvcs_: |]]  FileParam As CmndParam Model Set -- Commands  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fpParamSetWithNameValue" :comment "OBSOLETED by: fpCmndParamsSet" :parsMand "fpBase cls" :parsOpt "" :argsMin 2 :argsMax 2 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fpParamSetWithNameValue>>  *OBSOLETED by: fpCmndParamsSet*  =verify= parsMand=fpBase cls argsMin=2 argsMax=2 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fpParamSetWithNameValue(cs.Cmnd):
    cmndParamsMandatory = [ 'fpBase', 'cls', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 2, 'Max': 2,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             fpBase: typing.Optional[str]=None,  # Cs Mandatory Param
             cls: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:
        """OBSOLETED by: fpCmndParamsSet"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'fpBase': fpBase, 'cls': cls, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        fpBase = csParam.mappedValue('fpBase', fpBase)
        cls = csParam.mappedValue('cls', cls)
####+END:

        print("Obsoleted by: fpParamSetWithNameValue to fpCmndParamsSet")
        return cmndOutcome

        cmndArgsSpecDict = self.cmndArgsSpec()
        paramName = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        paramValue = self.cmndArgsGet("1", cmndArgsSpecDict, argsList)

        #print(f"{paramName} {paramValue}")

        fpBaseInst = pattern.sameInstance(getattr(__main__, cls), fpBase=fpBase)

        fpBaseInst.fps_setParam(paramName, paramValue)

        return cmndOutcome


####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """
***** Cmnd Args Specification
"""
        cmndArgsSpecDict = cs.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0",
            argName="paramName",
            argDefault="OopsName",
            argChoices=[],
            argDescription="Action to be specified by rest"
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="1",
            argName="paramValue",
            argDefault="OopsValue",
            argChoices=[],
            argDescription="Action to be specified by rest"
        )

        return cmndArgsSpecDict

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fpBaseRead" :parsMand "fpBase" :parsOpt "" :argsMin 0 :argsMax 999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fpBaseRead>>  =verify= parsMand=fpBase argsMax=999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fpBaseRead(cs.Cmnd):
    cmndParamsMandatory = [ 'fpBase', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 999,}

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
        # fpBaseInst = pattern.sameInstance(getattr(__main__, cls), fpBase=fpBase)
        # fpBaseDir = fpBaseInst.fileTreeBaseGet()  # type: ignore

        # cmndArgsSpecDict = self.cmndArgsSpec(fpBase, cls)

        if True:
            formatTypes = self.cmndArgsGet("0&999", cmndArgsSpecDict, argsList)
        else:
            formatTypes = effectiveArgsList

        for each in formatTypes:   # type: ignore
            if each == 'all':
                print(f"""format={each} -- fpBaseDir={fpBaseDir}""")
                FP_readTreeAtBaseDir_CmndOutput(
                    interactive=True,
                    fpBaseDir=fpBaseDir,
                    cmndOutcome=cmndOutcome,
                )
            # elif each == 'obj':
            #     cmndOutcome= fpBaseDir.fps_readTree()
            #     if cmndOutcome.error: return cmndOutcome

            #     thisParamDict = fpBaseDir.fps_dictParams
            #     if interactive:
            #         icm.ANN_write(fpBaseDir.fps_absBasePath())
            #         icm.FILE_paramDictPrint(thisParamDict)

            else:
                print(f"""format={each} -- fpBaseDir={fpBaseDir}""")

                # Read the wholething in:
                # FP_readTreeAtBaseDir_CmndOutput(
                #     interactive=False,
                #     fpBaseDir=fpBaseDir,
                #     cmndOutcome=cmndOutcome,
                # )
                #
                # print(cmndOutcome.results)
                #fpsDict = cmndOutcome.results
                #fp = fpsDict[each]
                #print(fp.parValueGet())

                # Or read one by one.
                fp = icm.FileParamReadFrom(
                    parRoot=fpBaseDir,
                    parName=each,
                )
                print(fp.parValueGet())   # type: ignore

        return cmndOutcome

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self fpBase cls"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, fpBase, cls, ):
####+END:
        """
***** Cmnd Args Specification
"""
        cmndArgsSpecDict = cs.CmndArgsSpecDict()
        argChoices = ['all', ]


        fpBaseInst = pattern.sameInstance(getattr(__main__, cls), fpBase=fpBase)

        for each in fpBaseInst.fps_namesWithRelPath():  # type: ignore
            argChoices.append(each)

        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&999",
            argName="formatTypes",
            argDefault="all",
            argChoices=argChoices,
            argDescription="One, many or all"
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:func/typing :funcName "FP_readTreeAtBaseDir_CmndOutput" :funcType "extTyped" :retType "extTyped" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /FP_readTreeAtBaseDir_CmndOutput/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def FP_readTreeAtBaseDir_CmndOutput(
####+END:
    interactive,
    fpBaseDir,
    cmndOutcome,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Invokes FP_readTreeAtBaseDir.cmnd as interactive-output only.
    #+end_org """

    # Interactive-Output + Chained-Outcome Command Invokation
    #
    FP_readTreeAtBaseDir = b.fp.FP_readTreeAtBaseDir()
    FP_readTreeAtBaseDir.cmndLineInputOverRide = True
    FP_readTreeAtBaseDir.cmndOutcome = cmndOutcome

    return FP_readTreeAtBaseDir.cmnd(
        interactive=interactive,
        FPsDir=fpBaseDir,
    )



####+BEGIN: b:py3:cs:func/typing :funcName "menu_setExamples" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-       [[elisp:(outline-show-subtree+toggle)][||]] /menu_setExamples/ deco=    [[elisp:(org-cycle)][| ]]
#+end_org """
def menu_setExamples(
####+END:
        fpBaseInst,
):
    G = cs.globalContext.get()
    csParams = G.icmParamDictGet()
    # fps_namesWithAbsPath = fpBaseInst.fps_namesWithAbsPath()
    fps_namesWithAbsPath = fpBaseInst.fps_manifestDictBuild()


    csMainName = G.icmMyName()

    cmndFrontStr = f"""{csMainName} --fpBase="{fpBaseInst.fileTreeBaseGet()}" --cls="{fpBaseInst.__class__.__name__}" -i fpParamSetWithNameValue """

    for eachParam, eachDest  in fps_namesWithAbsPath.items():
        # thisCsParam = csParams.parNameFind(eachParam)   # type: ignore
        # print(f"{cmndFrontStr} {thisCsParam.parNameGet()} __VOID__")
        print(f"{cmndFrontStr} {eachParam}  __VOID__")


####+BEGIN: b:py3:cs:func/typing :funcName "menu_getExamples" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-       [[elisp:(outline-show-subtree+toggle)][||]] /menu_getExamples/ deco=    [[elisp:(org-cycle)][| ]]
#+end_org """
def menu_getExamples(
####+END:
        fpBaseInst,
):
    G = cs.globalContext.get()
    csParams = G.icmParamDictGet()
    #fps_namesWithAbsPath = fpBaseInst.fps_namesWithAbsPath()
    fps_namesWithAbsPath = fpBaseInst.fps_manifestDictBuild()

    csMainName = G.icmMyName()

    cmndFrontStr = f"""{csMainName} --fpBase="{fpBaseInst.fileTreeBaseGet()}" --cls="{fpBaseInst.__class__.__name__}" -i fpParamGetWithName """

    for eachParam, eachDest  in fps_namesWithAbsPath.items():
        #thisCsParam = csParams.parNameFind(eachParam)   # type: ignore
        #print(f"{cmndFrontStr} {thisCsParam.parNameGet()}")
        #print(f"{cmndFrontStr} {eachDest.cmndParam.parNameGet()}")
        print(f"{cmndFrontStr} {eachParam}")


####+BEGIN: b:py3:cs:orgItem/basic :type "=OBSOLETED= " :title "*Junk Yard*" :comment "General"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =OBSOLETED=  [[elisp:(outline-show-subtree+toggle)][||]] *Junk Yard* General  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fpParamsValueDictObsolete" :parsMand "fpBase cls" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fpParamsValueDictObsolete>>  =verify= parsMand=fpBase cls ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fpParamsValueDictObsolete(cs.Cmnd):
    cmndParamsMandatory = [ 'fpBase', 'cls', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             fpBase: typing.Optional[str]=None,  # Cs Mandatory Param
             cls: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'fpBase': fpBase, 'cls': cls, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        fpBase = csParam.mappedValue('fpBase', fpBase)
        cls = csParam.mappedValue('cls', cls)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Return a dict of parName:parValue as results
        #+end_org """)

        fpBaseInst = pattern.sameInstance(getattr(__main__, cls), fpBase)
        fps_namesWithAbsPath = fpBaseInst.fps_namesWithAbsPath()  # type: ignore

        csParams = cs.G.icmParamDictGet()
        fps_namesWithAbsPath = fpBaseInst.fps_namesWithAbsPath()

        result = {}

        for eachParam, eachDest  in fps_namesWithAbsPath.items():
            thisCsParam = csParams.parNameFind(eachParam)   # type: ignore

            if b.fpCls.fpParamGetWithName(cmndOutcome=cmndOutcome).cmnd(
                    rtInv=rtInv,
                    cmndOutcome=cmndOutcome,
                    fpBase=fpBaseInst.fileTreeBaseGet(),
                    cls=fpBaseInst.__class__.__name__,
                    argsList=[thisCsParam.parNameGet()],
            ).isProblematic(): return(b_io.eh.badOutcome(cmndOutcome))

            eachParamValue = cmndOutcome.results.parValueGet()

            result[eachParam] = eachParamValue

        cmndOutcome.results = result

        print(cmndOutcome.results)

        return cmndOutcome


####+BEGIN: bx:cs:python:func :funcName "FP_writeDefaultsWithIcmParams" :funcType "succFail" :retType "bool" :deco "" :argsList "icmParamsAndDests"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-succFail [[elisp:(outline-show-subtree+toggle)][||]] /FP_writeDefaultsWithIcmParams/ retType=bool argsList=(icmParamsAndDests)  [[elisp:(org-cycle)][| ]]
#+end_org """
def FP_writeDefaultsWithIcmParams(
    icmParamsAndDests,
):
####+END:
    G = cs.globalContext.get()
    icmParams = G.icmParamDictGet()

    # Write relevant cmndParams as fileParams
    for eachParam, eachDest  in icmParamsAndDests.items():
        thisIcmParam = icmParams.parNameFind(eachParam)   # type: ignore
        thisIcmParam.parValueSet(thisIcmParam.parDefaultGet())
        thisIcmParam.writeAsFileParam(parRoot=eachDest,)

####+BEGINNOT: bx:cs:python:func :funcName "FP_writeWithIcmParams" :funcType "succFail" :retType "bool" :deco "" :argsList "icmParamsAndDests"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-succFail [[elisp:(outline-show-subtree+toggle)][||]] /FP_writeWithIcmParams/ retType=bool argsList=(icmParamsAndDests)  [[elisp:(org-cycle)][| ]]
#+end_org """
def FP_writeWithCsParams(
        fpCmndParams,
):
####+END:
    G = cs.globalContext.get()
    csParams = G.icmParamDictGet()
    csRunArgs = G.icmRunArgsGet() #; cs.unusedSuppressForEval(csRunArgs)

    cmndParamsDict = dict()

    # Read from cmndLine into callParamsDict
    for eachKey in fpCmndParams:
        cmndParamsDict[eachKey] = None
        try:
            exec("cmndParamsDict[eachKey] = csRunArgs." + eachKey)
        except AttributeError:
            continue

    # Write relevant cmndParams as fileParams
    for eachParam, fpCmndParam  in fpCmndParams.items():
        # print(f"{eachParam}, {eachDest}")
        if cmndParamsDict[eachParam]:
            thisCsParam = csParams.parNameFind(eachParam)   # type: ignore
            thisCsParam.parFpValueSet(cmndParamsDict[eachParam])
            # print(fpCmndParam.fileParam)
            # print(fpCmndParam.fileParam.parBaseGet())
            # print(thisCsParam)
            thisCsParam.writeAsFileParam(parRoot=str(fpCmndParam.fileParam.parBaseGet()))


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fpParamGetWithName" :comment "OBSOLETED by: fpCmndParamsGet" :parsMand "fpBase cls" :parsOpt "" :argsMin 1 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fpParamGetWithName>>  *OBSOLETED by: fpCmndParamsGet*  =verify= parsMand=fpBase cls argsMin=1 argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fpParamGetWithName(cs.Cmnd):
    cmndParamsMandatory = [ 'fpBase', 'cls', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             fpBase: typing.Optional[str]=None,  # Cs Mandatory Param
             cls: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:
        """OBSOLETED by: fpCmndParamsGet"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'fpBase': fpBase, 'cls': cls, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        fpBase = csParam.mappedValue('fpBase', fpBase)
        cls = csParam.mappedValue('cls', cls)
####+END:

        # print("Obsoleted by: fpParamGetWithName to fpCmndParamsGet")
        # return cmndOutcome

        cmndArgsSpecDict = self.cmndArgsSpec()
        paramName = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)

        fpBaseInst = pattern.sameInstance(getattr(__main__, cls), fpBase=fpBase)

        paramInfo = fpBaseInst.fps_getParam(paramName,)

        print(f"{paramInfo.parValueGet()}")

        # cmndOutcome.results = paramInfo

        return cmndOutcome


####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """
***** Cmnd Args Specification
"""
        cmndArgsSpecDict = cs.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0",
            argName="paramName",
            argDefault="OopsName",
            argChoices=[],
            argDescription="Action to be specified by rest"
        )

        return cmndArgsSpecDict



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fpParamsSetDefaults" :comment "OBSOLETED" :parsMand "fpBase cls" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fpParamsSetDefaults>>  *OBSOLETED*  =verify= parsMand=fpBase cls ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fpParamsSetDefaults(cs.Cmnd):
    cmndParamsMandatory = [ 'fpBase', 'cls', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             fpBase: typing.Optional[str]=None,  # Cs Mandatory Param
             cls: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:
        """OBSOLETED"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'fpBase': fpBase, 'cls': cls, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        fpBase = csParam.mappedValue('fpBase', fpBase)
        cls = csParam.mappedValue('cls', cls)
####+END:
        fpBaseInst = pattern.sameInstance(getattr(__main__, cls), fpBase)
        fps_namesWithAbsPath = fpBaseInst.fps_namesWithAbsPath()  # type: ignore

        FP_writeDefaultsWithIcmParams(fps_namesWithAbsPath,)

        return cmndOutcome



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fpParamsInfoDict" :comment "OBSOLETED" :parsMand "fpBase cls" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fpParamsInfoDict>>  *OBSOLETED*  =verify= parsMand=fpBase cls ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fpParamsInfoDict(cs.Cmnd):
    cmndParamsMandatory = [ 'fpBase', 'cls', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             fpBase: typing.Optional[str]=None,  # Cs Mandatory Param
             cls: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:
        """OBSOLETED"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'fpBase': fpBase, 'cls': cls, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        fpBase = csParam.mappedValue('fpBase', fpBase)
        cls = csParam.mappedValue('cls', cls)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Return a dict of parName:parValue as results
        #+end_org """)

        fpBaseInst = pattern.sameInstance(getattr(__main__, cls), fpBase)

        fps_namesWithAbsPath = fpBaseInst.fps_manifestDictBuild()
        # fps_namesWithAbsPath = fpBaseInst.fps_namesWithAbsPath()  # type: ignore

        csParams = cs.G.icmParamDictGet()
        # fps_namesWithAbsPath = fpBaseInst.fps_namesWithAbsPath()

        result = {}

        print("ZZ")
        print(fps_namesWithAbsPath)

        for eachParam, eachDest  in fps_namesWithAbsPath.items():
            thisCsParam = csParams.parNameFind(eachParam)   # type: ignore

            if b.fpCls.fpParamGetWithName(cmndOutcome=cmndOutcome).cmnd(
                    rtInv=rtInv,
                    cmndOutcome=cmndOutcome,
                    fpBase=fpBaseInst.fileTreeBaseGet(),
                    cls=fpBaseInst.__class__.__name__,
                    argsList=[thisCsParam.parNameGet()],
            ).isProblematic(): return(b_io.eh.badOutcome(cmndOutcome))

            eachParamValue = cmndOutcome.results

            result[eachParam] = eachParamValue

        cmndOutcome.results = result

        print(cmndOutcome.results)

        return cmndOutcome



####+BEGIN: b:py3:cs:func/typing :funcName "csParamValuesPlus" :comment "OBSOLTED" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-       [[elisp:(outline-show-subtree+toggle)][||]] /csParamValuesPlus/  OBSOLTED  [[elisp:(org-cycle)][| ]]
#+end_org """
def csParamValuesPlus(
####+END:
        fpBaseInst,
):
    G = cs.globalContext.get()
    csParams = G.icmParamDictGet()
    fps_namesWithAbsPath = fpBaseInst.fps_namesWithAbsPath()

    csMainName = G.icmMyName()

    cmndFrontStr = f"""{csMainName} --fpBase="{fpBaseInst.fileTreeBaseGet()}" --cls="{fpBaseInst.__class__.__name__}" -i fpParamSetWithNameValue """

    for eachParam, eachDest  in fps_namesWithAbsPath.items():
        thisCsParam = csParams.parNameFind(eachParam)   # type: ignore

        if b.fpCls.fpParamsList(cmndOutcome=cmndOutcome).cmnd(
                rtInv=rtInv,
                cmndOutcome=cmndOutcome,
                fpBase=fpBaseInst.fileTreeBaseGet(),
                cls=fpBaseInst.__class__.__name__,
                argsList=[thisCsParam.parNameGet()],
        ).isProblematic(): return(b_io.eh.badOutcome(cmndOutcome))

        eachParamValue = cmndOutcome.results
        print(thisCsParam)
        print(eachDest)
        print(eachParamValue)

    return




####+BEGINNOT: bx:cs:python:func :funcName "FP_listIcmParams" :comment "OBSOLETED" :funcType "succFail" :retType "bool" :deco "" :argsList "icmParamsAndDests"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-succFail [[elisp:(outline-show-subtree+toggle)][||]] /FP_listIcmParams/ retType=bool argsList=(icmParamsAndDests)  [[elisp:(org-cycle)][| ]]
#+end_org """
def FP_listCsParams(
    fpCmndParamDict,
):
####+END:
    G = cs.globalContext.get()
    csRunArgs = G.icmRunArgsGet() #; cs.unusedSuppressForEval(csRunArgs)
    csParams = G.icmParamDictGet()

    # List relevant cmndParams as fileParams
    for eachParam, fpCmndParam in fpCmndParamDict.items():
        thisCsParam = csParams.parNameFind(eachParam)   # type: ignore
        print("-----------")
        # print(eachDest)
        print(fpCmndParam.fileParam.parBaseGet())
        print(thisCsParam)


fpParamsReveal = fpCmndParamsReveal

        

####+BEGIN: b:prog:file/endOfFile :extraParams nil
""" #+begin_org
* *[[elisp:(org-cycle)][| END-OF-FILE |]]* :: emacs and org variables and control parameters
#+end_org """
### local variables:
### no-byte-compile: t
### end:
####+END:
