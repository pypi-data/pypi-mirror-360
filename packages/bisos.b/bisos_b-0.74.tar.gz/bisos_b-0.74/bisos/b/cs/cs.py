# -*- coding: utf-8 -*-

""" #+begin_org
* *[Summary]* :: A =CS-Lib= for creating and managing BPO's gpg and encryption/decryption.
#+end_org """

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
** This File: /bisos/git/auth/bxRepos/bisos-pip/b/py3/bisos/b/cs/cs.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:python:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['cs'], }
csInfo['version'] = '202209240339'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'cs-Panel.org'
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


NOT__all__ = [
    'G',
    'Cmnd',
    'argsparseBasedOnCsParams',
    'G_mainWithClass',
    'cmndCallParamsValidate',
    'cmndSubclassesNames',
    'csuList_importedModules',
    'csuList_commonParamsSpecify',
    'cmndNameToClass',
]

import __main__

import os
import sys

import enum

from bisos import b

from bisos.b import cs

from bisos.b import b_io



from datetime import datetime
import time

import argparse

import abc

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Cmnd Abstract Class" :anchor ""  :extraInfo "An Expectation Complete Operation"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Cmnd Abstract Class_: |]]  An Expectation Complete Operation  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

#G = bisos.cs.globalContext.get()
G = cs.globalContext.get()

####+BEGIN: b:py3:class/decl :className "Cmnd" :classType "abs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-abs    [[elisp:(outline-show-subtree+toggle)][||]] /Cmnd/  superClass=object  [[elisp:(org-cycle)][| ]]
#+end_org """
class Cmnd(object):
####+END:
    """
** Root class of an ICM's Cmnd.
"""
    from bisos import b

    cmndParamsMandatory = list()  # ['inFile']
    cmndParamsOptional = list()   # ['perhaps']
    cmndArgsLen = {'Min': 0, 'Max':0,}
    cmndArgsSpecObsoltedByMethod = dict()  # {1: []}

    cmndVisibility = ["all"]  # users, developers, internal
    cmndUsers = []            # lsipusr
    cmndGroups = []           # bystar
    cmndImpact = []           # read, modify

    rtInvConstraints = None

    def __init__(self,
                 cmndLineInputOverRide=None,
                 cmndOutcome = None,
    ):
        self.cmndLineInputOverRide = cmndLineInputOverRide
        self.cmndOutcome = cmndOutcome
        self.obtainDocStr = False

    def docStrClass(self,):
        return self.__class__.__doc__

    def docStrCmndMethod(self,):
        return self.cmnd.__doc__

    def cmndDocStr(self, inStr):
        if self.cmnd.__doc__:
            self.cmnd.__func__.__doc__ = f"""{self.cmnd.__doc__}\n{inStr}"""
        else:
            self.cmnd.__func__.__doc__ = inStr
        return self.obtainDocStr

    def captureRunStr(self, inStr):
        "In org-mode, with src_sh provide examples of running the cmnd. Can function as unit test as well."
        self.cmndRunStr = inStr

    def justCaptureP(self,):
        "NOTYET, Predicate. CS Players can set this to True. based on runArgs, return True or False."
        return False

    def docStrClassSet(self, docStr):
        """attribute '__doc__' of 'method' objects is not writable, so we use class."""
        self.__class__.__doc__ = docStr
        return self.obtainDocStr

    def obtainDocStrSet(self):
        self.obtainDocStr = True

    def docStrCmndDesc(self,):
        return self.cmnd.cmndDesc.__doc__

    def paramsMandatory(self,):
        return self.__class__.cmndParamsMandatory

    def paramsOptional(self,):
        return self.__class__.cmndParamsOptional

    def argsLen(self,):
        return self.__class__.cmndArgsLen

    def argsDesc(self,):
        return self.__class__.cmndArgsSpecObsoltedByMethod

    def users(self,):
        return self.__class__.cmndUsers

    def groups(self,):
        return self.__class__.cmndGroups

    def impact(self,):
        return self.__class__.cmndImpact

    def visibility(self,):
        return self.__class__.cmndVisibility

    def getOpOutcome(self):
        if self.cmndOutcome:
            return self.cmndOutcome
        self.cmndOutcome = b.op.Outcome(invokerName=self.myName())
        return self.cmndOutcome
        #return OpOutcome(invokerName=self.myName())

    def cmndLineValidate(
            self,
            outcome,
    ):
        if self.cmndLineInputOverRide:
            return True

        errorStr = self.cmndArgsLenValidate()
        if errorStr:
            outcome.error = b.op.OpError.CmndLineUsageError
            outcome.errInfo = errorStr
            return False
        errorStr = self.cmndParamsMandatoryValidate()
        if errorStr:
            outcome.error = b.op.OpError.CmndLineUsageError
            outcome.errInfo = errorStr
            return False
        errorStr = self.cmndParamsOptionalValidate()
        if errorStr:
            outcome.error = b.op.OpError.CmndLineUsageError
            outcome.errInfo = errorStr
            return False
        return True

    def cmndArgsLenValidate(self,
    ):
        """ If not as expected, return an error string, otherwise, None.

    expectedCmndArgsLen is a dcitionary with 'Min' and 'Max' range.
    """
        G = cs.globalContext.get()
        cmndArgsLen = len(G.icmRunArgsGet().cmndArgs)
        expectedCmndArgsLen = self.__class__.cmndArgsLen

        def errStr():
            errorStr = "Bad Number Of cmndArgs: cmndArgs={cmndArgs} --".format(cmndArgs=cmndArgsLen)
            if expectedCmndArgsLen['Min'] == expectedCmndArgsLen['Max']:
                errorStr = errorStr + "Expected {nu}".format(nu=expectedCmndArgsLen['Min'])
            else:
                errorStr = errorStr + "Expected between {min} and {max}".format(
                    min=expectedCmndArgsLen['Min'],
                    max=expectedCmndArgsLen['Max']
                )
            return errorStr

        if cmndArgsLen < expectedCmndArgsLen['Min']:
            retVal = errStr()
        elif cmndArgsLen > expectedCmndArgsLen['Max']:
            retVal = errStr()
        else:
            retVal = None

        #parser=argparse.ArgumentParser()
        #parser.print_help()

        return(retVal)

    def cmndParamsMandatoryValidate(self,
    ):
        """If not as expected, return an error string, otherwise, None.

    expectedCmndArgsLen is a dcitionary with 'Min' and 'Max' range.
    """

        G = cs.globalContext.get()
        icmRunArgs = G.icmRunArgsGet()
        icmRunArgsDict = vars(icmRunArgs)

        cmndParamsMandatory = self.__class__.cmndParamsMandatory

        for each in cmndParamsMandatory:
            if each in list(icmRunArgsDict.keys()):
                continue
            else:
                return "Unexpected Mandatory Param: param={param} --".format(param=each)

        for each in cmndParamsMandatory:
            if icmRunArgsDict[each] == None:
                return "Missing Mandatory Param: param={param} --".format(param=each)
            else:
                continue

        for each in cmndParamsMandatory:
            exec(
                "G.usageParams.{paramName} = icmRunArgs.{paramName}"
                .format(paramName=each)
            )
        return None

    def cmndParamsOptionalValidate(self,
    ):
        """If not as expected, return an error string, otherwise, None.

    expectedCmndArgsLen is a dcitionary with 'Min' and 'Max' range.
    """
        G = cs.globalContext.get()
        icmRunArgs = G.icmRunArgsGet()
        icmRunArgsDict = vars(icmRunArgs)

        cmndParamsOptional = self.__class__.cmndParamsOptional

        for each in cmndParamsOptional:
            if each in list(icmRunArgsDict.keys()):
                continue
            else:
                return "Unexpected Optional Param: param={param} --".format(param=each)

        for each in cmndParamsOptional:
            #if icmRunArgsDict[each] != None:
            exec(
                "G.usageParams.{paramName} = icmRunArgs.{paramName}"
                .format(paramName=each)
            )
        return None

    def cmndMyName(self):
        return self.__class__.__name__

    def myName(self):
        return self.cmndMyName()

    @abc.abstractmethod
    def cmnd(
            self,
            rtInv,
            cmndOutcome,
    ) -> b.op.Outcome:
        print("This is default Cmnd Class Definition -- It is expected to be overwritten. You should never see this.")
        outcome = b.op.Outcome()
        return outcome

    def cmndArgsSpec(self):
        # This is default Cmnd Class Definition -- It is expected to be overwritten. You should never see this."
        return None

    def cmndArgsGet(
            self,
            argPosition,
            cmndArgsSpecDict,
            effectiveArgsList,
            # ) -> list[str]:
    ) -> str:

        def argDefaultGet(
                cmndArgsSpecDict,
                argPosition,
        ):
            if cmndArgsSpecDict:
                cmndArgsSpec = cmndArgsSpecDict.argPositionFind(argPosition)
                return cmndArgsSpec.argDefaultGet()
            else:
                return ""

        min, max = cs.arg.cmndArgPositionToMinAndMax(argPosition)

        if min == None:
            return None

        if min == max:
            # We are returning a string as value
            if len(effectiveArgsList) >= (min + 1):
                return effectiveArgsList[min]
            else:
                return argDefaultGet(cmndArgsSpecDict, argPosition)

        elif max == -1:
            argsList = list()
            if len(effectiveArgsList) >= (min + 1):
                for count in range(0, min):
                    effectiveArgsList.pop(count)
                return effectiveArgsList
            else:
                defaultArg = argDefaultGet(cmndArgsSpecDict, argPosition)
                if defaultArg:
                    argsList.append(
                        argDefaultGet(cmndArgsSpecDict, argPosition)
                    )
                return argsList

        else:
            argsList = list()
            if len(effectiveArgsList) >= (min + 1):
                for count in range(min, max):
                    if len(effectiveArgsList) > count:
                        argsList.append(effectiveArgsList[count])
            else:
                defaultArg = argDefaultGet(cmndArgsSpecDict, argPosition)
                if defaultArg:
                    argsList.append(
                        argDefaultGet(cmndArgsSpecDict, argPosition)
                    )
            return argsList


    def cmndArgsValidate(
            self,
            effectiveArgsList,
            cmndArgsSpecDict,
            outcome=None,
    ):
        """
** TODO Place Holder -- Should validate argsList to confirm that it is consistent with cmndArgsSpec
"""
        if not cmndArgsSpecDict:
            return True

        retVal = True

        def reportInvalidCmndLineArgValue(
            cmndLineArgValue,
            argChoices,
        ):
            print("cmndLineArgValue={cmndLineArgValue} is not in {argChoices}".format(
                cmndLineArgValue=cmndLineArgValue, argChoices=argChoices,
            ))
            return False

        cmndArgsSpecDictDict = cmndArgsSpecDict.argDictGet()
        for argPosition, cmndArgSpec in cmndArgsSpecDictDict.items():
            argChoices = cmndArgSpec.argChoicesGet()

            if not argChoices:
                continue

            if argChoices == "any":
                continue

            min, max = cs.arg.cmndArgPositionToMinAndMax(argPosition)

            if min == None:
                # io.eh.problem()
                return None

            if min == max:
                # There is just one value
                if len(effectiveArgsList) >= (min + 1):
                    cmndLineArgValue =  effectiveArgsList[min]

                    if not cmndLineArgValue in argChoices:
                        retVal = reportInvalidCmndLineArgValue(
                            cmndLineArgValue,
                            argChoices,
                        )

            elif max == -1:
                if len(effectiveArgsList) >= (min + 1):
                    for count in range(0, min):
                        effectiveArgsList.pop(count)
                        for cmndLineArgValue in effectiveArgsList:
                            if not cmndLineArgValue in argChoices:
                                retVal = reportInvalidCmndLineArgValue(
                                    cmndLineArgValue,
                                    argChoices,
                                )

            else:
                for count in range(min, max):
                    if len(effectiveArgsList) >= (count + 1):
                        cmndLineArgValue = effectiveArgsList[count]
                        if not cmndLineArgValue in argChoices:
                            retVal = reportInvalidCmndLineArgValue(
                                cmndLineArgValue,
                                argChoices,
                            )

        return retVal

    def cmndCallTimeKwArgs(self,):
        """
** All value full icmpParams are then written off as file params.
        """
        G = cs.globalContext.get()
        icmRunArgs = G.icmRunArgsGet()

        applicableCmndKwArgs = dict()

        g_parDict = G.icmParamDictGet().parDictGet()

        for each in self.cmndParamsMandatory:
            try:
                eachIcmParam = g_parDict[each]
            except  KeyError:
                print(f"BadUsage: Missing parameter definition: {each}")
                return
            else:
                if not icmRunArgs.__dict__[each]:
                    print(f"BadUsage: Missing mandatory parameter zz: {each}")
                    return
                applicableCmndKwArgs.update({each: icmRunArgs.__dict__[each]})
                continue

        for each in self.cmndParamsOptional:
            try:
                eachIcmParam = g_parDict[each]
            except  KeyError:
                # That is okay. An optionale param was not specified.
                continue
            else:
                applicableCmndKwArgs.update({each: icmRunArgs.__dict__[each]})
                continue

        if icmRunArgs.cmndArgs:
            applicableCmndKwArgs.update({'argsList': icmRunArgs.cmndArgs})

        # print(f"YYY == {applicableCmndKwArgs}")
        return applicableCmndKwArgs

    def invModel(self,
            baseDir,
    ):
        """
** Writes out all inputs of the command as file parameters.
** Can be invoked from cmnd-line with --insAsFPs=basePath instead of cmnd().
** Returns an outcome.
** cmndParamsMandatory and optionals are walked through in icmRunArgs.
** Their values are then set in icmParam.
** All value full icmpParams are then written off as file params.
        """
        G = cs.globalContext.get()
        icmRunArgs = G.icmRunArgsGet()

        # print(f"cmndParamsMandatory={self.cmndParamsMandatory}")
        # print(f"cmndParamsOptional={self.cmndParamsOptional}")

        if not pathlib.Path(baseDir).is_dir():
            print(f"BadUsage: Missing {baseDir}")
            return

        #print(icmRunArgs)

        applicableIcmParams = CmndParamDict()

        def absorbApplicableIcmParam(icmParam, each):
            # print(f"4444 {each} {icmRunArgs.__dict__[each]}")
            icmParam.parValueSet(icmRunArgs.__dict__[each])
            applicableIcmParams.parDictAppend(eachIcmParam)

        g_parDict = IcmGlobalContext().icmParamDictGet().parDictGet()

        # print(g_parDict)

        for each in self.cmndParamsMandatory:
            try:
                eachIcmParam = g_parDict[each]
            except  KeyError:
                print(f"BadUsage: Missing parameter definition: {each}")
                return
            else:
                if not icmRunArgs.__dict__[each]:
                    print(f"BadUsage: Missing mandatory parameter: {each}")
                    return
                absorbApplicableIcmParam(eachIcmParam, each,)
                # applicableIcmParams.parDictAppend(eachIcmParam)
                continue

        for each in self.cmndParamsOptional:
            try:
                eachIcmParam = g_parDict[each]
            except  KeyError:
                # That is okay. An optionale param was not specified.
                continue
            else:
                absorbApplicableIcmParam(eachIcmParam, each,)
                continue

        cmndParamsBase = pathlib.Path(baseDir).joinpath('cmndPars')
        cmndParamsBase.mkdir(parents=True, exist_ok=True)

        csParamsToFileParamsUpdate(
            parRoot=cmndParamsBase,
            csParams=applicableIcmParams,
        )

        b.fp.FileParamWriteToPath(
            parNameFullPath=pathlib.Path(baseDir).joinpath('icmName'),
            parValue=G.icmMyName()
        )

        b.fp.FileParamWriteToPath(
            parNameFullPath=pathlib.Path(baseDir).joinpath('cmndName'),
            parValue=G.icmRunArgsGet().invokes[0]
        )

        print(applicableIcmParams)

        outcome = OpOutcome()
        return outcome

        # icmParam = g_parDict['bpoId']

        # icmParam.parValueSet("ZZZZHHHHLLLL")

        # for each in icmRunArgs.__dict__:
        #     print(each)
        #     if icmRunArgs.__dict__[each]:
        #         print(f"JJMM --- {each}")
        #         print(f"kkjj -- {icmRunArgs.__dict__[each]}")

        #         # g_param = g_parDict[each]

        # for key, icmParam in IcmGlobalContext().icmParamDictGet().parDictGet().items():
        #     if ( icmParam.argsparseShortOptGet() == None )  and ( icmParam.argsparseLongOptGet() == None ):
        #         break
        #     print(f"JJ {key} LL {icmParam}")


####+BEGIN: b:py3:cs:method/typing :methodName "invocationValidateParams" :methodType "eType" :deco ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-eType [[elisp:(outline-show-subtree+toggle)][||]] /invocationValidateParams/ deco=   [[elisp:(org-cycle)][| ]]
    #+end_org """
    def invocationValidateParams(
####+END:
            self,
            rtInv: cs.RtInvoker,
            outcome: b.op.Outcome,
            callParamDict: typing.Dict[str, str],
    )  -> b.op.Outcome:
        """ #+begin_org
** [[elisp:(org-cycle)][| DocStr| ]]  Validates invoked callParamDict against expectations and returns  outcome

if =rtInv= is cli, assume that it has already been validated.

Are all the mandatories present?
Are any other than mandatories or optionals present?

*** TODO Place holder,
        #+end_org """

        if callParamDict:
            return outcome
        # Validation comes here
        return outcome

####+BEGIN: b:py3:cs:method/typing :methodName "invocationValidateArgs" :methodType "eType" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-eType [[elisp:(outline-show-subtree+toggle)][||]] /invocationValidateArgs/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def invocationValidateArgs(
####+END:
            self,
            rtInv: cs.RtInvoker,
            outcome: b.op.Outcome,
            argsList: list[str],
    )  -> b.op.Outcome:
        """ #+begin_org
** [[elisp:(org-cycle)][| DocStr| ]]  Validates invoked argsList against expectations and returns  outcome

if =rtInv= is cli, assume that it has already been validated.

Are nu of args in range?
Are args values as expected?

*** TODO Place holder,
        #+end_org """

        if argsList:
            return outcome
        # Validation comes here
        return outcome


####+BEGIN: b:py3:cs:method/typing :methodName "invocationValidate" :methodType "eType"  :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-eType [[elisp:(outline-show-subtree+toggle)][||]] /invocationValidate/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def invocationValidate(
####+END:
            self,
            rtInv: cs.RtInvoker,
            outcome: b.op.Outcome,
            callParamDict: typing.Optional[typing.Dict[str, typing.Optional[str]]],
            argsList: typing.Optional[list[str]],
    )  -> b.op.Outcome:
        """ #+begin_org
** [[elisp:(org-cycle)][| DocStr| ]]  Returns the effectiveArgsList as a list of strings or None in case of failure.

Usage Pattern:

From within cmnd method -- or later from within a decorator,

    if not self.invocationValidate(rtInv, outcome, callParamDict, argsList):
       return cmndOutcome

        #+end_org """

        # Validate that rtInv is valid.

        self.rtInv = rtInv
        self.cmndOutcome = outcome
        return outcome

        if callParamDict is not None:
            self.invocationValidateParams(rtInv, outcome, callParamDict)

        if argsList is not None:
            self.invocationValidateArgs(rtInv, outcome, argsList)

        return outcome


####+BEGIN: b:py3:cs:method/typing :methodName "pyCmnd" :methodType "eType"  :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-eType [[elisp:(outline-show-subtree+toggle)][||]] /pyCmnd/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def pyCmnd(
####+END:
            self,
            rtInv=None,
            cmndOutcome=None,
            **kwArgs,
    )  -> b.op.Outcome:
        """ #+begin_org
** [[elisp:(org-cycle)][| DocStr| ]]  Calls Cmnd, Returns Outcome
pyCmnd invokactions are non-interactive
        #+end_org """

        if rtInv is None:
            rtInv = cs.RtInvoker.new_py()
        if cmndOutcome is None:
            cmndOutcome = b.op.Outcome()

        outcome = self.cmnd(
            rtInv=rtInv,
            cmndOutcome=cmndOutcome,
            **kwArgs,
        )

        return outcome

####+BEGIN: b:py3:cs:method/typing :methodName "pyWCmnd" :methodType "eType"  :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-eType [[elisp:(outline-show-subtree+toggle)][||]] /pyWCmnd/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def pyWCmnd(
####+END:
            self,
            cmndOutcome,
            **kwArgs,
    )  -> b.op.Outcome:
        """ #+begin_org
** [[elisp:(org-cycle)][| DocStr| ]]  A Wrapped Cmnd, Calls Cmnd, Returns Outcome
pyCmnd invokactions are non-interactive
        #+end_org """

        rtInv = cs.RtInvoker.new_py()

        outcome = self.cmnd(
            rtInv=rtInv,
            cmndOutcome=cmndOutcome,
            **kwArgs,
        )

        return outcome


####+BEGIN: b:py3:cs:method/typing :methodName "pyRoCmnd" :methodType "eType"  :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-eType [[elisp:(outline-show-subtree+toggle)][||]] /pyRoCmnd/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def pyRoCmnd(
####+END:
            self,
            rtInv=None,
            cmndOutcome=None,
            roSapPath=None,
            rosmu=None,
            perfName=None,
            svcName=None,
            **kwArgs,
    )  -> b.op.Outcome:
        """ #+begin_org
** [[elisp:(org-cycle)][| DocStr| ]]  Calls Cmnd, Returns Outcome
pyCmnd invokactions are non-interactive
        #+end_org """

        if rtInv is None:
            rtInv = cs.RtInvoker.new_py()
        if cmndOutcome is None:
            cmndOutcome = b.op.Outcome()

        cmndClass = self.__class__

        if roSapPath is None:
            roSapPath = cs.ro.SapBase_FPs.perfNameToRoSapPath(perfName, rosmu=rosmu, svcName=svcName)

        print(roSapPath)
        rpycInvResult =  cs.ro.roInvokeCmndAtSap(
            roSapPath,
            rtInv,
            cmndOutcome,
            cmndClass,
            ** kwArgs,
        )

        return cmndOutcome

####+BEGIN: b:py3:cs:method/typing :methodName "pyRoWCmnd" :methodType "eType"  :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-eType [[elisp:(outline-show-subtree+toggle)][||]] /pyRoWCmnd/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def pyRoWCmnd(
####+END:
            self,
            cmndOutcome,
            roSapPath=None,
            rosmu=None,
            perfName=None,
            svcName=None,
            **kwArgs,
    )  -> b.op.Outcome:
        """ #+begin_org
** [[elisp:(org-cycle)][| DocStr| ]]  A Wrapped Cmnd, Calls Cmnd, Returns Outcome
pyCmnd invokactions are non-interactive
        #+end_org """

        rtInv = cs.RtInvoker.new_py()

        outcome = self.pyRoCmnd(
            rtInv=rtInv,
            cmndOutcome=cmndOutcome,
            roSapPath=roSapPath,
            rosmu=rosmu,
            perfName=perfName,
            svcName=svcName,
            **kwArgs,
        )

        return outcome




####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CS Output" :anchor ""  :extraInfo "Perhaps It Belongs In The IO Package"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CS Output_: |]]  Perhaps It Belongs In The IO Package  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "icmOutputBaseGet" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /icmOutputBaseGet/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def icmOutputBaseGet(
####+END:
) -> str:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """
    return "./"

####+BEGIN: b:py3:cs:func/typing :funcName "icmOutputXlsGetPath" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /icmOutputXlsGetPath/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def icmOutputXlsGetPath(
####+END:
        fileBaseName,
) -> str:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """
    ts = time.time()
    st = datetime.fromtimestamp(ts).strftime('%y%m%d%H%M%S')
    fileName = fileBaseName + st + ".xlsx"
    return os.path.join(icmOutputBaseGet(), fileName)


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CS Types Enumeration" :anchor ""  :extraInfo "Needs to be revisited"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CS Types Enumeration_: |]]  Needs to be revisited  [[elisp:(org-shifttab)][<)]] E|
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

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "csuList" :anchor "" :extraInfo "Setup framework functions"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _csuList_: |]]  Setup framework functions  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END

####+BEGIN: b:py3:cs:func/typing :funcName "csuList_importedModules" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /csuList_importedModules/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def csuList_importedModules(
####+END:
         csuList: list,
) -> list:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Later we may do more.
    #+end_org """

    #print(csuList)
    return csuList


####+BEGIN: b:py3:cs:func/typing :funcName "csuList_commonParamsSpecify" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /csuList_commonParamsSpecify/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def csuList_commonParamsSpecify(
####+END:
        csuList: list,
        csParams: cs.param.CmndParamDict,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Walkthrough =csuList=, call module.commonParamsSpecify(=csParams=).
    #+end_org """

    for each in csuList:
        # Use of tm assumes that logging has been properly set.
        b_io.tm.note(each.split(".")[-1])  # last-part
        module = sys.modules[each]
        if hasattr(module, "commonParamsSpecify"):
            parsSpecFunc = getattr(module, "commonParamsSpecify")
            parsSpecFunc(csParams)

    module = sys.modules['__main__']
    if hasattr(module, "commonParamsSpecify"):
        parsSpecFunc = getattr(module, "commonParamsSpecify")
        parsSpecFunc(csParams)


    return


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Command Line Parsing With argparse" :anchor "" :extraInfo "just arg parse or more?"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Command Line Parsing With argparse_: |]]  just arg parse or more?  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END

####+BEGIN: b:py3:cs:func/typing :funcName "commonIcmParamsParser" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /commonIcmParamsParser/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def commonIcmParamsParser(
####+END:
        parser,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Module Common Command Line Parameters.
    #+end_org """

    print("NOTYET --- This Has been Obsoleted --- GGG")
    csParams = commonIcmParamsPrep()

    #argsparseBasedOnCsParams(parser, csParams)
    argsparseBasedOnCsParams(csParams)

    return

####+BEGIN: b:py3:cs:func/typing :funcName "argsCommonProc" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /argsCommonProc/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def argsCommonProc(
####+END:
        parser,
) -> None:
     """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Module Common Command Line Parameters.
     #+end_org """

     parser.add_argument(
         '-i',
         '--invokes',
         dest='invokes',
         action='append'
         )

     parser.add_argument(
         '-t',
         '--callTrackings',
         dest='callTrackings',
         action='append',
         choices=['invoke+', 'invoke-', 'monitor+', 'monitor-'],
         default=[]
         )

     parser.add_argument(
         '--runMode',
         dest='runMode',
         action='store',
         choices=['dryRun', 'fullRun', 'runDebug'],
         default='fullRun'
         )

     # NOTYET, delete this
     parser.add_argument(
         '--insAsFPs',
         dest='insAsFPs',
         metavar='ARG',
         action='store',
         default='None',
         help="Emit all inputs as FileParams At Specified Base",
         )

     parser.add_argument(
         '--csBase',
         dest='csBase',
         action='store',
         default='None',
         help="Command Services Base",
         )

     parser.add_argument(
         '--invModel',
         dest='invModel',
         action='store',
         default='None',
         help="Emit all inputs as FileParams At Specified Base",
         )

     parser.add_argument(
         '--ex_invModel',
         dest='ex_invModel',
         action='store',
         default='None',
         help="TBD",
         )

     # parser.add_argument(
     #     '--perfModel',
     #     dest='perfModel',
     #     action='store',
     #     default='None',
     #     help="",
     #     )

     # parser.add_argument(
     #     '--perfName',
     #     dest='perfName',
     #     metavar='ARG',
     #     action='store',
     #     default='None',
     #     help="",
     #     )

     # parser.add_argument(
     #     '--roSapPath',
     #     dest='roSapPath',
     #     action='store',
     #     default='None',
     #     help="Path of FP base. With ordinary commands, it remote invokes at Sap.",
     #     )

     # parser.add_argument(
     #     '--ex_roSapPath',
     #     dest='ex_roSapPath',
     #     action='store',
     #     default='None',
     #     help="",
     #     )

     parser.add_argument(
         '-v',
         '--verbosity',
         dest='verbosityLevel',
         metavar='ARG',
         action='store',
         default=None,
         help='Adds a Console Logger for the level specified in the range 1..50'
         )

     parser.add_argument(
         '--logFile',
         dest='logFile',
         metavar='ARG',
         action='store',
         default=None,
         help='Specifies destination LogFile for this run'
         )

     parser.add_argument(
         '--logFileLevel',
         dest='logFileLevel',
         metavar='ARG',
         action='store',
         default=None,
         help=''
         )

     parser.add_argument(
         '--docstring',
         action='store_true',
         dest="docstring"
         )

     parser.add_argument(
         'cmndArgs',
     #dest='cmndArgs',   #
         metavar='CMND',
         nargs='*',
         action='store',
         help='Interactively Invokable Function Arguments'
         )

     parser.add_argument(
         '--load',
         dest='loadFiles',
         action='append',
         default=[]
         )

     return

####+BEGIN: b:py3:cs:func/typing :funcName "G_argsProc" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /G_argsProc/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def G_argsProc(
####+END:
        arguments,
        extraArgs,
):
     """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] ICM-ICM Argument Parser. extraArgs resides in the G_ module.
     #+end_org """

     parser = argparse.ArgumentParser(
         description=__doc__
         )

     G.icmArgsParser = parser

     argsCommonProc(parser)
     #commonIcmParamsPrep()

     if extraArgs:
        #extraArgs(parser)
        extraArgs()

     #
     # The logic below breaks multiple --invokes.
     # Perhaps a distinction between --invoke and --invokes is an answer.
     #
     # We are inserting "--" after -i cmnd
     # to get things like -i run pip install --verbose
     #
     #
     index = 0
     for each in arguments:
         if each == "-i":
             arguments.insert(index+2, "--")
             break
         if each == "--invokes":
             arguments.insert(index+2, "--")
             break
         index = index + 1

     args = parser.parse_args(arguments)

     return args, parser

####+BEGIN: b:py3:cs:func/typing :funcName "argsparseBasedOnCsParams" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /argsparseBasedOnCsParams/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def argsparseBasedOnCsParams(
####+END:
        #parser,
        csParams,
) -> None:
     """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Convert csParams to parser.
     #+end_org """

     parser = G.icmArgsParser

     for key, icmParam in csParams.parDictGet().items():
         if ( icmParam.argsparseShortOptGet() == None )  and ( icmParam.argsparseLongOptGet() == None ):
             break

         if not icmParam.argsparseShortOptGet() == None:
             parser.add_argument(
                 icmParam.argsparseShortOptGet(),
                 icmParam.argsparseLongOptGet(),
                 dest = icmParam.parNameGet(),
                 nargs = icmParam.parNargsGet(),
                 action=icmParam.parActionGet(),
                 default = icmParam.parDefaultGet(),
                 help=icmParam.parDescriptionGet()
                 )
         else:
             parser.add_argument(
                icmParam.argsparseLongOptGet(),
                dest = icmParam.parNameGet(),
                nargs = icmParam.parNargsGet(),
                metavar = 'ARG',
                action=icmParam.parActionGet(),
                default = icmParam.parDefaultGet(),
                help=icmParam.parDescriptionGet()
                )

     # So that it can be processed later as well.
     G.icmParamDictSet(csParams)

     return

####+BEGIN: b:py3:cs:func/typing :funcName "libUserInit" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /libUserInit/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def libUserInit(
####+END:
        icmLineOpts,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] For situations when icm lib is being used outside of an ICM -- in the context of any app.
    #+end_org """
    parser = argparse.ArgumentParser(
         description=__doc__
    )
    argsCommonProc(parser)

    args = parser.parse_args(icmLineOpts)
    logControler = b_io.log.controller
    logControler.loggerSet(args)


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "G_main -- Invoked from ICM, calls invokesProc" :anchor "" :extraInfo ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _G_main -- Invoked from ICM, calls invokesProc_: |]]    [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END

# DO NOT DECORATE THIS FUNCTION

####+BEGIN: b:py3:cs:func/typing :funcName "G_main" :comment "DO NOT DECORATE THIS FUNCTION" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /G_main/  DO NOT DECORATE THIS FUNCTION deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def G_main(
####+END:
        inArgv,
        G_examples,
        extraArgs,
        invokesProc,
        mainEntry=None,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] This is the main entry point for Python.Icm.Icm (InteractiveInvokationModules)
    #+end_org """

    #
    # The order is important here,
    # 1) Parse The Command Line -- 2) LOG_ usese the command line -- 3) G. setup
    #
    icmRunArgs, icmArgsParser = G_argsProc(inArgv, extraArgs)

    logControler = controller
    logControler.loggerSet(icmRunArgs)

    logger = logControler.loggerGet()

    logger.info('Main Started: ' + b.ast.stackFrameInfoGet(1) )

    G = cs.globalContext.get()
    G.globalContextSet( icmRunArgs=icmRunArgs )
    G.icmArgsParser = icmArgsParser

    icmRunArgs_loadFiles()

    if len( inArgv ) == 0:
        if G_examples:
            G_examples()
            return

    if icmRunArgs.invokes:
        invokesProc()
    else:
        if mainEntry:
            mainEntry()

    return 0

# DO NOT DECORATE THIS FUNCTION
#
####+BEGIN: b:py3:cs:func/typing :funcName "G_mainWithClass" :comment "DO NOT DECORATE THIS FUNCTION" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /G_mainWithClass/  DO NOT DECORATE THIS FUNCTION  [[elisp:(org-cycle)][| ]]
#+end_org """
def G_mainWithClass(
####+END:
        inArgv,
        G_examples,
        extraArgs,  # this is really extraParamsHook
        classedCmndsDict,
        #funcedCmndsDict,
        mainEntry=None,
        g_icmPreCmnds=None,
        g_icmPostCmnds=None,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] This is the main entry point for Python.Icm.Icm (InteractiveInvokationModules)

Missing Feature. We want to use the logger inside of extraParamsHook.
    But, loggerSet needs runArgs.

    #+end_org """

    logControler = b_io.log.controller

    logArgv = ['-v', '30']
    if '-v' in inArgv:
        index = inArgv.index('-v')
        level = inArgv[index+1]
        logArgv = ['-v', level]

    # With logArgv, we set the logger, before extraParamsHook is run
    # G_argsProc runs args parse without the extraArgs
    #
    icmRunArgs, icmArgsParser = G_argsProc(logArgv, None)
    logControler.loggerSet(icmRunArgs)  # First loggerSet

    icmRunArgs, icmArgsParser = G_argsProc(inArgv, extraArgs)   # runs extraArgs with logArgv

    logControler.loggerSet(icmRunArgs)  # second loggerSet, with extraArgs

    logger = logControler.loggerGet()

    logger.info('Main Started: ' + b.ast.stackFrameInfoGet(1) )

    G = cs.globalContext.get()
    G.globalContextSet( icmRunArgs=icmRunArgs )
    G.icmArgsParser = icmArgsParser
    G.cmndMethodsDictSet(classedCmndsDict)
    #G.cmndFuncsDictSet(funcedCmndsDict)

    rtInv = cs.RtInvoker.new_cmnd()
    outcome = b.op.Outcome()

    cs.runArgs.loadFiles()

    if len( inArgv ) == 0:
        if G_examples:
            G_examples().cmnd(rtInv, outcome,)
            return

    if icmRunArgs.invokes:
        thisCmndName=icmRunArgs.invokes[0]

        if g_icmPreCmnds:
            g_icmPreCmnds()

        outcome = invokesProcAllClassed(
            classedCmndsDict,
            icmRunArgs
        )

        if g_icmPostCmnds:
            g_icmPostCmnds()


        if not outcome:
            return

        try:
            outcomeError = outcome.error
        except AttributeError:
            ANN_here("Consider returning an outcome. cmnd={cmnd}".format(cmnd=thisCmndName))
            return

        if outcomeError:
            if outcome.error != b.op.OpError.Success:
                if outcome.error == b.op.OpError.CmndLineUsageError:
                    sys.stderr.write(
                        "{myName}.{cmndName} Command Line Failed: Error={status} -- {errInfo}\n".
                        format(myName=G.icmMyName(),
                               cmndName=thisCmndName,
                               status=outcome.error,
                               errInfo=outcome.errInfo,
                    ))
                    print("------------------")
                    G.icmArgsParser.print_help()
                    print("------------------")
                    print("Run -i usage for more details.")
                else:
                    sys.stderr.write(
                        "{myName}.{cmndName} Failed: Error={status} -- {errInfo}\n".
                        format(myName=G.icmMyName(),
                               cmndName=thisCmndName,
                               status=outcome.error,
                               errInfo=outcome.errInfo,
                    ))
            else:
                #sys.stderr.write("{myName}.{cmndName} Completed Successfully: status={status}\n"
                logger.info(
                    "{myName}.{cmndName} Completed Successfully: status={status}".
                    format(myName=G.icmMyName(),
                           cmndName=thisCmndName,
                           status=outcome.error
                ))
        else:
            #sys.stderr.write("{myName}.{cmndName} Completed Successfully: status={status}\n"
            logger.info(
                "{myName}.{cmndName} Completed Successfully: status={status}".
                format(myName=G.icmMyName(),
                       cmndName=thisCmndName,
                       status=outcome.error
            ))
        if outcome.error == b.op.OpError.Success:
            return 0
        else:
           return outcome.error
    else:
        if mainEntry:
            import types
            if type(mainEntry) is types.FunctionType:
                mainEntry()
            else:
                rtInv = cs.RtInvoker.new_cmnd()
                outcome = b.op.Outcome()
                cmndKwArgs = mainEntry().cmndCallTimeKwArgs()
                cmndKwArgs.update({'rtInv': rtInv})
                cmndKwArgs.update({'cmndOutcome': outcome})
                if mainEntry().cmndArgsLen['Max'] != 0:  # Cmnd is expecting Arguments
                    cmndKwArgs.update({'argsList': G.icmRunArgsGet().cmndArgs})
                outcome = mainEntry().cmnd(**cmndKwArgs)
                return outcome.error

    print("DDD")
    return 0

####+BEGIN: b:py3:cs:func/typing :funcName "invOutcomeReportControl" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /invOutcomeReportControl/   [[elisp:(org-cycle)][| ]]
#+end_org """
def invOutcomeReportControl(
####+END:
        cmnd: bool = False,
        ro: bool = False,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    G.__class__._outcomeReportCmnd = cmnd
    G.__class__._outcomeReportRo = ro

####+BEGIN: b:py3:cs:func/typing :funcName "invOutcomeReportCmnd" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /invOutcomeReportCmnd/   [[elisp:(org-cycle)][| ]]
#+end_org """
def invOutcomeReportCmnd(
####+END:
        cmndOutcome: b.op.Outcome,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] When Cli, put stdout or results and stderr of cmndOutcome on stdout and stderr.
    #+end_org """

    # print(G.__class__._outcomeReportCmnd)

    if G.__class__._outcomeReportCmnd == False:
        return

    if cmndOutcome is  None:
        sys.stderr.write("Bad Cmnd Return -- No cmndOutcome\n")
        return

    if cmndOutcome.results is not  None:
        sys.stdout.write(f"{cmndOutcome.results}\n")
    else:
        # sys.stderr.write("Cmnd -- No Results\n")
        pass


####+BEGIN: b:py3:cs:func/typing :funcName "invOutcomeReportRo" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /invOutcomeReportRo/   [[elisp:(org-cycle)][| ]]
#+end_org """
def invOutcomeReportRo(
####+END:
        cmndOutcome: b.op.Outcome,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] When CliRo, put stdout or results and stderr of cmndOutcome on stdout and stderr.
    #+end_org """

    if G.__class__._outcomeReportRo == False:
        return

    if cmndOutcome.results is not None:
        sys.stdout.write(f"{cmndOutcome.results}\n")
    else:
        sys.stderr.write("Rpyc Invoker -- No Results\n")

####+BEGIN: b:py3:cs:func/typing :funcName "perfOutcomeReportRo" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /perfOutcomeReportRo/   [[elisp:(org-cycle)][| ]]
#+end_org """
def perfOutcomeReportRo(
####+END:
        cmndOutcome: b.op.Outcome,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] When CliRo, put stdout or results and stderr of cmndOutcome on stdout and stderr.
    #+end_org """

    if G.__class__._outcomeReportRo == False:
        return

    if cmndOutcome.results is not None:
        sys.stdout.write(f"Performer Outcome:: {cmndOutcome.results}\n")
    else:
        sys.stderr.write("Rpyc Performer -- No Results\n")

####+BEGIN: b:py3:cs:func/typing :funcName "reportOp_roPerfParams" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /reportOp_roPerfParams/   [[elisp:(org-cycle)][| ]]
#+end_org """
def reportOp_roPerfParams(
####+END:
        cmndClassName,
        args,
        kwArgs,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] When CliRo, put stdout or results and stderr of cmndOutcome on stdout and stderr.
    #+end_org """

    print(f"Performing: {cmndClassName} {args} {kwArgs}")

####+BEGINNOT: b:py3:cs:func/typing :funcName "invokesProcAllClassedInvModel" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /invokesProcAllClassed/ deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
#@io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def invokesProcAllClassedInvModel(
####+END:
        classedCmndsDict,
        icmRunArgs,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Process all invokations applicable to all (classed+funced of mains+libs) CMNDs.
    #+end_org """

    G = cs.globalContext.get()
    icmRunArgs = G.icmRunArgsGet()

    rtInv = cs.RtInvoker.new_cmnd()
    outcome = b.op.Outcome()

    def applyMethodBasedOnContext(
            classedCmnd,
    ):
        """ Chooses the method to apply Cmnd() to.
        """
        invModel = icmRunArgs.invModel  # This can be a "None" string but not a None
        csBase = icmRunArgs.csBase

        outcome = b.op.Outcome()

        if invModel == "None":
            #
            # applicableIcmParams = classedCmnd().absorbApplicableIcmParam()
            # outcome = classedCmnd().cmnd(**applicableIcmParams)
            #
            cmndKwArgs = classedCmnd().cmndCallTimeKwArgs()
            #print(f"{cmndKwArgs}")
            rtInv = cs.RtInvoker.new_cmnd()
            cmndKwArgs.update({'rtInv': rtInv})
            cmndKwArgs.update({'cmndOutcome': outcome})
            if classedCmnd().cmndArgsLen['Max'] != 0:  # Cmnd is expecting Arguments
                cmndKwArgs.update({'argsList': G.icmRunArgsGet().cmndArgs})
            #print(f"{cmndKwArgs}")
            outcome = classedCmnd().cmnd(**cmndKwArgs)

        elif invModel == "rpyc":
            print("in rpyc")

            cmndKwArgs = classedCmnd().cmndCallTimeKwArgs()
            rtInv = cs.RtInvoker.new_cmnd()
            cmndKwArgs.update({'rtInv': rtInv})
            cmndKwArgs.update({'cmndOutcome': outcome})
            if classedCmnd().cmndArgsLen['Max'] != 0:  # Cmnd is expecting Arguments
                cmndKwArgs.update({'argsList': G.icmRunArgsGet().cmndArgs})

            outcome = cs.rpyc.csInvoke(classedCmnd, **cmndKwArgs)

        else:
            if csBase == "None":
                print(f"BadUsage: Missing csBase, invModel={invModel}")
                outcome = b.op.Outcome()
                outcome.error = OpError.CmndLineUsageError
                outcome.errInfo = f"BadUsage: Missing csBase, invModel={invModel}"
            else:
                outcome = classedCmnd().invModel(csBase)

        return outcome

    for invoke in icmRunArgs.invokes:
        #print(f"Looking for {invoke}")
        #
        # First we try cmndList_mainsMethods()
        #
        try:
            classedCmnd = classedCmndsDict[invoke]
        except  KeyError:
            #print("TM_ Key Error")
            pass
        else:
            #print(f"Found {classedCmnd}")
            outcome = applyMethodBasedOnContext(classedCmnd)
            continue

        #
        # Next we try cmndList_libsMethods()
        #
        callDict = dict()
        for eachCmnd in cs.inCmnd.cmndList_libsMethods().cmnd(
                rtInv=rtInv,
                cmndOutcome=outcome,
        ):
            #print(f"looking at {eachCmnd}")
            try:
                callDict[eachCmnd] = eval("{eachCmnd}".format(eachCmnd=eachCmnd))
            except NameError:
                print(("io.eh.problem -- Skipping-b eval({eachCmnd})".format(eachCmnd=eachCmnd)))
                continue

        try:
            classedCmnd = callDict[invoke]
        except  KeyError:
            pass
        else:
            outcome = applyMethodBasedOnContext(classedCmnd)
            continue

        #
        # We tried everything and could not find any
        #

        # BUG, NOTYET, io.eh.problem goes to -v 20
        io.eh.io.eh.problem_info("Invalid Action: {invoke}"
                        .format(invoke=invoke))

        print(("Invalid Action: {invoke}"
                        .format(invoke=invoke)))

        outcome = b.op.Outcome()
        outcome.error = b.op.OpError.CmndLineUsageError
        outcome.errInfo = "Invalid Action: {invoke}".format(invoke=invoke)

    perfModel = icmRunArgs.perfModel  # This can be a "None" string but not a None

    #     if insAsFP_baseDir != "None":
    if perfModel != "None":
        # print("Capturing outcome")
        csBase = icmRunArgs.csBase
        if csBase == "None":
            pass
            # print(f"Missing csBase")
        else:
            b.fp.FileParamWriteToPath(
                parNameFullPath=pathlib.Path(csBase).joinpath('result'),
                parValue=outcome.results
            )


    # Check for perfModel and capture outcome
    return(outcome)


####+BEGINNOT: b:py3:cs:func/typing :funcName "invokesProcAllClassed" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /invokesProcAllClassed/ deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
#@io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def invokesProcAllClassed(
####+END:
        classedCmndsDict,
        icmRunArgs,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Process all invokations applicable to all (classed+funced of mains+libs) CMNDs.
    #+end_org """

    G = cs.globalContext.get()
    icmRunArgs = G.icmRunArgsGet()

    rtInv = cs.RtInvoker.new_cmnd()
    outcome = b.op.Outcome()

    def applyMethodBasedOnContext(
            classedCmnd,
    ):
        """ Chooses the method to apply Cmnd() to.
        """
        perfName = icmRunArgs.perfName  # This can be a "None" string but not None
        csBase = icmRunArgs.csBase

        outcome = b.op.Outcome()

        if classedCmnd().rtInvConstraints is not None:
            perfName = "None"

        if perfName == None or perfName == "None":
            #
            # applicableIcmParams = classedCmnd().absorbApplicableIcmParam()
            # outcome = classedCmnd().cmnd(**applicableIcmParams)
            #
            cmndKwArgs = classedCmnd().cmndCallTimeKwArgs()
            #print(f"{cmndKwArgs}")
            rtInv = cs.RtInvoker.new_cmnd()
            cmndKwArgs.update({'rtInv': rtInv})
            cmndKwArgs.update({'cmndOutcome': outcome})
            if classedCmnd().cmndArgsLen['Max'] == 0:  # Cmnd is expecting Arguments
                cmndKwArgs.pop('argsList', None)
            else:
                if G.icmRunArgsGet().cmndArgs:
                    if G.icmRunArgsGet().cmndArgs[0] == "--":
                        G.icmRunArgsGet().cmndArgs.pop(0)
                cmndKwArgs.update({'argsList': G.icmRunArgsGet().cmndArgs})
            outcome = classedCmnd().cmnd(**cmndKwArgs)

            invOutcomeReportCmnd(outcome)

        else:
            # print("in Remote Operation")

            roSapPath = cs.ro.SapBase_FPs.perfNameToRoSapPath(perfName)  # static method
            sapBaseFps = b.pattern.sameInstance(cs.ro.SapBase_FPs, roSapPath=roSapPath)

            portNu = sapBaseFps.fps_getParam('perfPortNu')
            ipAddr = sapBaseFps.fps_getParam('perfIpAddr')

            cmndKwArgs = classedCmnd().cmndCallTimeKwArgs()
            rtInv = cs.RtInvoker.new_cmnd()
            cmndKwArgs.update({'rtInv': rtInv})
            cmndKwArgs.update({'cmndOutcome': outcome})
            if classedCmnd().cmndArgsLen['Max'] != 0:  # Cmnd is expecting Arguments
                cmndKwArgs.update({'argsList': G.icmRunArgsGet().cmndArgs})

            rpycInvResult = cs.rpyc.csInvoke(
                ipAddr.parValueGet(),
                portNu.parValueGet(),
                classedCmnd,
                **cmndKwArgs,
            )
            if rpycInvResult:
                print("rpycInvResult, Not working as expected. Outcome is used instead.")

            invOutcomeReportRo(outcome)

        return outcome

    for invoke in icmRunArgs.invokes:
        #print(f"Looking for {invoke}")
        #
        # First we try cmndList_mainsMethods()
        #
        try:
            classedCmnd = classedCmndsDict[invoke]
        except  KeyError:
            #print("TM_ Key Error")
            pass
        else:
            #print(f"Found {classedCmnd}")
            outcome = applyMethodBasedOnContext(classedCmnd)
            continue

        #
        # Next we try cmndList_libsMethods()
        #
        callDict = dict()
        for eachCmnd in cs.inCmnd.cmndList_libsMethods().cmnd(
                rtInv=rtInv,
                cmndOutcome=outcome,
        ):
            #print(f"looking at {eachCmnd}")
            try:
                callDict[eachCmnd] = eval("{eachCmnd}".format(eachCmnd=eachCmnd))
            except NameError:
                print(("io.eh.problem -- Skipping-b eval({eachCmnd})".format(eachCmnd=eachCmnd)))
                continue

        try:
            classedCmnd = callDict[invoke]
        except  KeyError:
            pass
        else:
            outcome = applyMethodBasedOnContext(classedCmnd)
            continue

        #
        # We tried everything and could not find any
        #

        # BUG, NOTYET, io.eh.problem goes to -v 20
        b_io.eh.problem_info("Invalid Action: {invoke}"
                        .format(invoke=invoke))

        print(("Invalid Action: {invoke}"
                        .format(invoke=invoke)))

        outcome = b.op.Outcome()
        outcome.error = b.op.OpError.CmndLineUsageError
        outcome.errInfo = "Invalid Action: {invoke}".format(invoke=invoke)

    perfModel = icmRunArgs.perfModel  # This can be a "None" string but not a None

    #     if insAsFP_baseDir != "None":
    if perfModel != "None":
        #print("Capturing outcome")
        csBase = icmRunArgs.csBase
        if csBase == "None":
            pass
            # print(f"Missing csBase")
        else:
            b.fp.FileParamWriteToPath(
                parNameFullPath=pathlib.Path(csBase).joinpath('result'),
                parValue=outcome.results
            )


    # Check for perfModel and capture outcome
    return(outcome)



####+BEGIN: b:py3:cs:func/typing :funcName "cmndNameToClass" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /cmndNameToClass/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def cmndNameToClass(
####+END:
        cmndName: str,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Given cmndName, return cmndClass.
    #+end_org """

    G = cs.globalContext.get()
    classedCmndsDict = G.cmndMethodsDict()

    try:
        classedCmnd = classedCmndsDict[cmndName]
    except  KeyError:
        #print "TM_"
        pass
    else:
        return classedCmnd

    try:
        cmndClass = eval("{cmndName}".format(cmndName=cmndName))
    except NameError:
        return None

    if cmndName in cmndSubclassesNames():
        return cmndClass
    else:
        return None




####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "cmndsList -- List C-CMNDs and F-CMNDs in a given file and in icm library" :anchor "" :extraInfo ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _cmndsList -- List C-CMNDs and F-CMNDs in a given file and in icm library_: |]]    [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END


####+BEGIN: b:py3:cs:func/typing :funcName "cmndSubclassesNames" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /cmndSubclassesNames/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def cmndSubclassesNames(
####+END:
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Not using generators by choice.
    #+end_org """

    # return [each.__name__ for each in Cmnd.__subclasses__()]
    cmndsNames = list()
    for eachClass in Cmnd.__subclasses__():
        cmndsNames.append(eachClass.__name__)
    return cmndsNames

####+BEGIN: b:py3:cs:func/typing :funcName "cmndMainsMethodsToFileParamsUpdate" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /cmndMainsMethodsToFileParamsUpdate/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def cmndMainsMethodsToFileParamsUpdate(
####+END:
        parRoot: str,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """
    mainsCmndMethods = cmndList_mainsMethods().cmnd()
    for each in mainsCmndMethods:
        cmndToFileParamsUpdate(
            cmndName=each,
            parRoot=parRoot,
        )
    return


####+BEGIN: b:py3:cs:func/typing :funcName "cmndLibsMethodsToFileParamsUpdate" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /cmndLibsMethodsToFileParamsUpdate/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def cmndLibsMethodsToFileParamsUpdate(
####+END:
        parRoot: str,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """
    libsCmndMethods = cmndList_libsMethods().cmnd()
    for each in libsCmndMethods:
        cmndToFileParamsUpdate(
            cmndName=each,
            parRoot=parRoot,
        )
    return

####+BEGIN: b:py3:cs:func/typing :funcName "evalStringInMain" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /evalStringInMain/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def evalStringInMain(
####+END:
        inStr: str,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Given inStr eval that string in __main__.
    #+end_org """
    LOG_here("Eval-ing: __main__.{}".format(inStr))
    # try
    eval("__main__.{}".format(inStr))


####+BEGIN: b:py3:cs:func/typing :funcName "cmndToFileParamsUpdate" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /cmndToFileParamsUpdate/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def cmndToFileParamsUpdate(
####+END:
        cmndName,
        parRoot,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Write cmnd as fileParam.
    #+end_org """

    absoluteParRoot = os.path.abspath(parRoot)

    if not os.path.isdir(absoluteParRoot):
        try: os.makedirs( absoluteParRoot, 0o775 )
        except OSError: pass

    parValue = "unSet"

    b.fp.FileParamWriteTo(
        parRoot=absoluteParRoot,
        parName=cmndName,
        parValue=parValue,
    )

    def writeCmndAttrFV(
            cmndName,
            attrName,
            attrValue,
    ):
        varValueFullPath = os.path.join(
            absoluteParRoot,
            cmndName,
            attrName,
        )
        b.fv.writeToFilePathAndCreate(
            filePath=varValueFullPath,
            varValue=attrValue,
        )


    docStr = cmndDocStrShort().cmnd(
        cmndName=cmndName,
    )
    writeCmndAttrFV(
        cmndName=cmndName,
        attrName='description',
        attrValue=docStr,
    )

    docStr = cmndDocStrFull().cmnd(
        cmndName=cmndName,
    )
    writeCmndAttrFV(
        cmndName=cmndName,
        attrName='fullDesc',
        attrValue=docStr,
    )

    cmndClass = cmndNameToClass(cmndName)
    if not cmndClass: return

    writeCmndAttrFV(
        cmndName=cmndName,
        attrName='paramsMandatory',
        attrValue=cmndClass().paramsMandatory(),
    )
    writeCmndAttrFV(
        cmndName=cmndName,
        attrName='paramsOptional',
        attrValue=cmndClass().paramsOptional(),
    )
    writeCmndAttrFV(
        cmndName=cmndName,
        attrName='cmndInfo',
        attrValue=cmndInfoEssential().cmnd(
            interactive=False,
            orgLevel=2,
            cmndName=cmndName,
        )
    )

    return



####+BEGIN: b:py3:cs:func/typing :funcName "cmndCallParamsValidate" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /cmndCallParamsValidate/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def cmndCallParamsValidate(
####+END:
        callParamDict,
        rtInv: cs.RtInvoker,
        outcome=None,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Expected to be used in all CMNDs.


MB-2022 --- This is setting the variable not validating it.
    Perhaps the function should have been cmndCallParamsSet.

Usage Pattern:

    if not icm.cmndCallParamValidate(FPsDir, interactive, outcome=cmndOutcome):
       return cmndOutcome

    #+end_org """

    #G = cs.globalContext.get()
    #if type(callParamOrList) is not list: callParamOrList = [ callParamOrList ]

    if not outcome:
        outcome = OpOutcome()

    for key  in callParamDict:
        # print(f"111 {key}")
        # interactive could be true in two situations:
        # 1) When a cs is executed on cmnd-line.
        # 2) When a cs is invoked with interactive as true.
        # When (2) callParamDict[key] is expcted to be true by having been specified at invokation.
        #
        if not callParamDict[key]:
            # MB-2022 The logic here seems wrong. When non-interactive, only mandattories
            # should be verified.
            # if not interactive:
            #     return eh_problem_usageError(
            #         outcome,
            #         "Missing Non-Interactive Arg {}".format(key),
            #     )
            if rtInv.outs:
                exec("callParamDict[key] = IcmGlobalContext().usageParams." + key)
            # print(f"222 {callParamDict[key]}")


    return True


####+BEGIN: bx:cs:python:icmItem :itemType "Global" :itemTitle "mainsClassedCmndsGlobal = None"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Global     [[elisp:(outline-show-subtree+toggle)][||]] mainsClassedCmndsGlobal = None  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

mainsClassedCmndsGlobal = None




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
