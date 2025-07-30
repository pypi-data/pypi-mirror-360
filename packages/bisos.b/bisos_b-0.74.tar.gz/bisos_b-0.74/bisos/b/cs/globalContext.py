# -*- coding: utf-8 -*-

""" #+begin_org
* *[Summary]* :: A =CS-Lib= for creating and managing BPO's gpg and encryption/decryption.
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
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['globalContext'], }
csInfo['version'] = '202209034718'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'globalContext-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* /[[elisp:(org-cycle)][| Description |]]/ :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/PyFwrk/bisos.crypt/_nodeBase_/fullUsagePanel-en.org][PyFwrk bisos.crypt Panel]]
Module description comes here.
** Relevant Panels:
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

import os
import sys
import enum

from bisos.b import b_io

from bisos import b

import logging

from bisos.transit import pattern

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :title "CsGlobalContext Singleton Usage, provides global context"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CsGlobalContext Singleton Usage, provides global context_: |]]    [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:


####+BEGIN: bx:dblock:python:enum :enumName "ICM_GroupingType" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Enum       [[elisp:(outline-show-subtree+toggle)][||]] /ICM_GroupingType/  [[elisp:(org-cycle)][| ]]
#+end_org """
@enum.unique
class ICM_GroupingType(enum.Enum):
####+END:
    Pkged = 'Pkged'
    Grouped= 'Grouped'
    Scattered = 'Scattered'
    Unitary = 'Unitary'
    Standalone = 'Standalone'
    Other = 'Other'
    UnSet = 'UnSet'

####+BEGIN: bx:dblock:python:enum :enumName "ICM_PkgedModel" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Enum       [[elisp:(outline-show-subtree+toggle)][||]] /ICM_PkgedModel/  [[elisp:(org-cycle)][| ]]
#+end_org """
@enum.unique
class ICM_PkgedModel(enum.Enum):
####+END:
    BasicPkg = 'BasicPkg'
    ToicmPkg = 'ToicmPkg'
    EmpnaPkg = 'EmpnaPkg'
    UnSet = 'UnSet'

####+BEGIN: bx:dblock:python:enum :enumName "ICM_CmndParts" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Enum       [[elisp:(outline-show-subtree+toggle)][||]] /ICM_CmndParts/  [[elisp:(org-cycle)][| ]]
#+end_org """
@enum.unique
class ICM_CmndParts(enum.Enum):
####+END:
    Common = 'Common'
    Param = 'Param'
    Target = 'Target'
    Bxo = 'Bxo'
    Bxsrf = 'Bxsrf'
    UnSet = 'UnSet'

####+BEGIN: bx:dblock:python:enum :enumName "AuxInvokationContext" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Enum       [[elisp:(outline-show-subtree+toggle)][||]] /AuxInvokationContext/  [[elisp:(org-cycle)][| ]]
#+end_org """
@enum.unique
class AuxInvokationContext(enum.Enum):
####+END:
    UnSet = 'UnSet'
    IcmRole = 'IcmRole'
    CmndParamsAndArgs = 'CmndParamsAndArgs'
    DocString = 'DocString'

####+BEGIN: bx:dblock:python:class :className "CsGlobalContext" :superClass "" :comment "" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /CsGlobalContext/ object  [[elisp:(org-cycle)][| ]]
#+end_org """
class CsGlobalContext(object):
####+END:
     """ #+begin_org
** [[elisp:(org-cycle)][| DocStr| ]]  Singleton Usage Model: Interactively Invokable Module Global Context.
    #+end_org """

     icmArgsParser = None

     icmRunArgsThis = None
     #icmRunArgsThis = []

     icmParamDict = None       # ICM Specified Parameters in g_argsExtraSpecify()
     thisFuncName = None
     logger = None
     astModuleFunctionsList = None
     plantOfThisSeed = None
     seedOfThisPlant = None

     _csInfo = {}

     usageParams = b.types.Variables
     usageArgs = b.types.Variables

     # ICM-Profile Specifications
     icmGroupingType = ICM_GroupingType.UnSet
     icmPkgedModel = ICM_PkgedModel.UnSet
     icmCmndPartsList = [ICM_CmndParts.UnSet]

     _auxInvokationContext = AuxInvokationContext.UnSet
     _auxInvokationResults = None
     _cmndNames = None # All 3 of the above have been obsoleted

     _cmndFuncsDict = None
     _cmndMethodsDict = None

     lastOpOutcome = None

     _outcomeReportCmnd = False
     _outcomeReportRo = True


     def __init__(self):
        # self.__class__.invOutcomeReportCmnd = False
        # self.__class__.invOutcomeReportRo = True
        pass

     def globalContextSet(self,
                          icmRunArgs=None,
                          icmParamDict=None
                          ):
         """
         """
         #if not icmRunArgs == None:
         self.__class__.icmRunArgsThis = icmRunArgs

         # NOTYET, 2017 -- Review This
         if icmParamDict == None:
             pass
             #self.__class__.icmParamDict = CmndParamDict()

         logger = logging.getLogger(b_io.log.LOGGER)
         self.__class__.logger = logger

         self.__class__.astModuleFunctionsList = b.ast.ast_topLevelFunctionsInFile(
             self.icmMyFullName()
         )

     def icmRunArgsGet(self):
         return self.__class__.icmRunArgsThis

     def icmParamDictSet(self, icmParamDict):
         # print(f"XXX {icmParamDict}")
         self.__class__.icmParamDict = icmParamDict

     def icmParamDictGet(self):
         return self.__class__.icmParamDict

     def icmMyFullName(self):
          return os.path.abspath(sys.argv[0])

     def icmMyName(self):
         return os.path.basename(sys.argv[0])

     def icmModuleFunctionsList(self):
         return self.__class__.astModuleFunctionsList

     def curFuncNameSet(self, curFuncName):
         self.__class__.thisFuncName = curFuncName

     def curFuncName(self):
         return self.__class__.thisFuncName

     def auxInvokationContextSet(self, auxInvokationEnum):
         self.__class__._auxInvokationContext = auxInvokationEnum

     def auxInvokationContext(self):
         return self.__class__._auxInvokationContext

     def auxInvokationResultsSet(self, auxInvokationRes):
         self.__class__._auxInvokationResults = auxInvokationRes

     def auxInvokationResults(self):
         return self.__class__._auxInvokationResults

     def csInfoSet(self, csInfo):
         self.__class__._csInfo = csInfo

     def csInfo(self):
         return self.__class__._csInfo


     def cmndNamesSet(self, cmnds):
         self.__class__._cmndNames = cmnds

     def cmndNames(self):
         return self.__class__._cmndNames

     def cmndMethodsDictSet(self, cmnds):
         self.__class__._cmndMethodsDict = cmnds

     def cmndMethodsDict(self):
         return self.__class__._cmndMethodsDict

     def cmndFuncsDictSet(self, cmnds):
         self.__class__._cmndFuncsDict = cmnds

     def cmndFuncsDict(self):
         return self.__class__._cmndFuncsDict

G = pattern.singleton(CsGlobalContext)

# Instead of "G = CsGlobalContext()" -- to make it clear that G is a singltone.
# Only exposed as G and not CsGlobalContext. So, CsGlobalContext is not visible any how.

####+BEGIN: bx:cs:py3:func :funcName "get" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /get/  [[elisp:(org-cycle)][| ]]
#+end_org """
def get(
####+END:
) -> CsGlobalContext:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Returns the single G instance which makes it a singelton.
    CsGlobalContext can not be imported from this module.
    #+end_org """
    return G


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :title " ~End Of Editable Text~ "
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _ ~End Of Editable Text~ _: |]]    [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/bisos/apps/defaults/software/plusOrg/dblock/inserts/endOfFileControls.org"
#+STARTUP: showall
####+END:


####+BEGIN: b:prog:file/endOfFile :extraParams nil
""" #+begin_org
* *[[elisp:(org-cycle)][| END-OF-FILE |]]* :: emacs and org variables and control parameters
#+end_org """
### local variables:
### no-byte-compile: t
### end:
####+END:
