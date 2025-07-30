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
** This File: /bisos/git/auth/bxRepos/bisos-pip/b/py3/bisos/b/cs/inCmnd.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:python:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['inCmnd'], }
csInfo['version'] = '202209242120'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'inCmnd-Panel.org'
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

from bisos.b import b_io
from bisos import b
from bisos.b import cs

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CmndSvcs" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CmndSvcs_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:


####+BEGIN: bx:cs:py3:section :title "Service Related Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Service Related Commands*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

#rpyc_csPerformer = cs.rpyc_csPerformer

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "rpyc_csPerformer2" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<rpyc_csPerformer2>> ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class rpyc_csPerformer2(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """)

        # Announce that the service is being started
        cs.rpyc.csPerform()

        return(cmndOutcome)



####+BEGIN: bx:cs:py3:section :title "/Player Support/      :: *Framework cmnds That are expected by the ICM-Player*"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] */Player Support/      :: *Framework cmnds That are expected by the ICM-Player**  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

#rpyc_csPerformer = cs.rpyc.rpyc_csPerformer

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "icmLanguage" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<icmLanguage>> ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class icmLanguage(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Returns python. Part of icm framework.
        #+end_org """)

        if interactive:
            print("python")

        return cmndOutcome.set(
            opError=b.op.OpError.Success,
            opResults="python"
        )

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "icmCmndPartIncludes" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<icmCmndPartIncludes>> ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class icmCmndPartIncludes(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

####+END:
            self.cmndDocStr(f""" #+begin_org
    ** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  NOTYET Returns True. Part of icm framework
            #+end_org """)

            return(cmndOutcome)

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "icmInUpdate" :comment "" :parsMand "" :parsOpt "" :argsMin 1 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<icmInUpdate>> argsMin=1 argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class icmInUpdate(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Given a baseDir, update icmIn. "Part of icm framework.
        #+end_org """)

        if interactive:
            G = cs.globalContext.get()
            icmRunArgs = G.icmRunArgsGet()
            icmsBase = icmRunArgs.cmndArgs[0]
        else:
            if not icmsBase:
                io.eh.problem_usageError("")
                return

        G_myFullName = sys.argv[0]
        G_myName = os.path.basename(G_myFullName)

        icmInBase = icmsBase + "/" + G_myName + "/icmIn"

        print("{icmInBase}".format(icmInBase=icmInBase))

        csParamsToFileParamsUpdate(
            parRoot="{icmInBase}/paramsFp".format(icmInBase=icmInBase),
            csParams=G.icmParamDictGet(),
        )

        csParamsToFileParamsUpdate(
            parRoot="{icmInBase}/commonParamsFp".format(icmInBase=icmInBase),
            csParams=commonIcmParamsPrep(),
        )

        cmndMainsMethodsToFileParamsUpdate(
            parRoot="{icmInBase}/cmndMainsFp".format(icmInBase=icmInBase),
        )

        cmndLibsMethodsToFileParamsUpdate(
            parRoot="{icmInBase}/cmndLibsFp".format(icmInBase=icmInBase),
        )

        return(cmndOutcome)

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "csInfoCmnd" :comment "" :parsMand "" :parsOpt "" :argsMin 1 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<csInfoCmnd>> argsMin=1 argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class csInfoCmnd(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Given a baseDir, update icmIn. Part of icm framework.
        #+end_org """)

        # if interactive:
        G = cs.IcmGlobalContext()
        #     icmRunArgs = G.icmRunArgsGet()
        #     icmInBase = icmRunArgs.cmndArgs[0]
        # else:
        #     if not icmInBase:
        #         io.eh.problem_usageError("")
        #         return

        print("* ICM Specified Parameters")

        csParams = G.icmParamDictGet()

        for key, icmParam in csParams.parDictGet().items():
            if ( icmParam.argsparseShortOptGet() == None )  and ( icmParam.argsparseLongOptGet() == None ):
                break

            print("** " + key)
            print("*** " + str(icmParam))

        print("* ICM Common Parameters")

        csParams = commonIcmParamsPrep()

        for key, icmParam in csParams.parDictGet().items():
            if ( icmParam.argsparseShortOptGet() == None )  and ( icmParam.argsparseLongOptGet() == None ):
                break

            print("** " + key)
            print("*** " + str(icmParam))

        print("* ICM Mains Methods")

        mainsMethods = cmndList_mainsMethods().cmnd(interactive=False)
        for each in mainsMethods:
            cmndInfo().cmnd(
                interactive=True,
                orgLevel=2,
                cmndName=each,
            )

        print("* ICM Libs Methods")

        libsMethods = cmndList_libsMethods().cmnd(interactive=False)
        for each in libsMethods:
            cmndInfo().cmnd(
                interactive=True,
                orgLevel=2,
                cmndName=each,
            )

        return(cmndOutcome)

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "version" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<version>> ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class version(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  ICM version number.
        #+end_org """)

        """Version number is obtained from."""
        __version__ = "NOTYET"
        #if interactive:
        if True:
            print(("* ICM-Version: {ver}".format(ver=str( __version__ ))))
            return
        else:
            return(format(str(__version__)))

        return(cmndOutcome)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "visit" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<visit>> ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class visit(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Visit The ICM Module. Use emacs client to visit the ICM module.
        #+end_org """)

        myFullName = sys.argv[0]

        if b.subProc.Op(outcome=cmndOutcome, log=1).bash(
                f"""emlVisit -v -n showRun -i gotoPanel {myFullName}""",
        ).isProblematic():  return(b_io.eh.badOutcome(cmndOutcome))

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=None,
        )


    
####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "visitPrev" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<visitPrev>>  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class visitPrev(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Visit The ICM Module. Use emacs client to visit the ICM module.
        #+end_org """)


        myName=self.myName()
        G = cs.globalContext.get()
        thisOutcome = OpOutcome(invokerName=myName)

        thisOutcome = subProc_bash(
            """emlVisit -v -n showRun -i gotoPanel {myFullName}"""
            .format(myFullName=G.icmMyFullName()),
            stdin=None, outcome=thisOutcome,
        ).out()

        if thisOutcome.isProblematic():
            return(io.eh.badOutcome(thisOutcome))

        return(cmndOutcome)

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "cmndInfo" :comment "" :parsMand "orgLevel" :parsOpt "" :argsMin 1 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<cmndInfo>> parsMand=orgLevel argsMin=1 argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class cmndInfo(cs.Cmnd):
    cmndParamsMandatory = [ 'orgLevel', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             orgLevel: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Returns a human oriented string for the specified cmndName's expected pars/args usage.
        Used by ICM Players to inform user of a given cmndName capabilities.
        #+end_org """)

        cmndName=None,  # cmndArgs[0]
        orgLevel=2,


        myName=self.myName()
        G = cs.globalContext.get()
        thisOutcome = OpOutcome(invokerName=myName)

        if not cmndName:
            if not interactive:
                io.eh.problem_usageError("")
                return
            cmndName = G.icmRunArgsGet().cmndArgs[0]

        cmndClass = cmndNameToClass(cmndName)
        if not cmndClass: return

        outString = list()

        def orgIndentStr(subLevel): return "*" * (orgLevel + subLevel)

        outString.append("{baseOrgStr} {cmndName}\n".format(
            baseOrgStr=orgIndentStr(0),
            cmndName=cmndName,
        ))
        outString.append("{baseOrgStr} cmndShortDocStr={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndDocStrShort().cmnd(
                interactive=False,
                cmndName=cmndName,
        )))
        outString.append("{baseOrgStr} cmndFullDocStr={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndDocStrFull().cmnd(
                interactive=False,
                cmndName=cmndName,
        )))
        outString.append("{baseOrgStr} classDocStrOf={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=classDocStrOf().cmnd(
                interactive=False,
                argsList=[cmndName],
        )))
        outString.append("{baseOrgStr} cmndParamsMandatory={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().paramsMandatory(),
        ))
        outString.append("{baseOrgStr} cmndParamsOptional={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().paramsOptional(),
        ))
        outString.append("{baseOrgStr} cmndArgsLen={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().argsLen(),
        ))
        outString.append("{baseOrgStr} cmndArgsSpec={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().argsDesc(),
        ))
        outString.append("{baseOrgStr} cmndUsers={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().users(),
        ))
        outString.append("{baseOrgStr} cmndGroups={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().groups(),
        ))
        outString.append("{baseOrgStr} cmndImapct={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().impact(),
        ))
        outString.append("{baseOrgStr} cmndVisibility={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().visibility(),
        ))

        if interactive:
            # print adds an extra line at the end in Python 2.X
            sys.stdout.write("".join(outString))

        return thisOutcome.set(
            opError=OpError.Success,
            opResults="".join(outString)
        )

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "cmndInfoEssential" :comment "" :parsMand "" :parsOpt "" :argsMin 1 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<cmndInfoEssential>> argsMin=1 argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class cmndInfoEssential(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Returns a human oriented string for the specified cmndName's expected pars/args usage.
        Used by ICM Players to inform user of a given cmndName capabilities.
        #+end_org """)

        myName=self.myName()
        G = cs.globalContext.get()
        thisOutcome = OpOutcome(invokerName=myName)

        if not cmndName:
            if not interactive:
                io.eh.problem_usageError("")
                return
            cmndName = G.icmRunArgsGet().cmndArgs[0]

        cmndClass = cmndNameToClass(cmndName)
        if not cmndClass: return

        outString = list()

        def orgIndentStr(subLevel): return "*" * (orgLevel + subLevel)

        outString.append("{baseOrgStr} cmndFullDocStr={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndDocStrFull().cmnd(
                interactive=False,
                cmndName=cmndName,
        )))
        outString.append("{baseOrgStr} cmndParamsMandatory={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().paramsMandatory(),
        ))
        outString.append("{baseOrgStr} cmndParamsOptional={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().paramsOptional(),
        ))
        outString.append("{baseOrgStr} cmndArgsLen={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().argsLen(),
        ))
        outString.append("{baseOrgStr} cmndArgsSpec={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().argsDesc(),
        ))
        outString.append("{baseOrgStr} cmndUsers={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().users(),
        ))
        outString.append("{baseOrgStr} cmndGroups={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().groups(),
        ))
        outString.append("{baseOrgStr} cmndImapct={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().impact(),
        ))
        outString.append("{baseOrgStr} cmndVisibility={str}\n".format(
            baseOrgStr=orgIndentStr(1),
            str=cmndClass().visibility(),
        ))

        if interactive:
            # print adds an extra line at the end in Python 2.X
            sys.stdout.write("".join(outString))

        return thisOutcome.set(
            opError=OpError.Success,
            opResults="".join(outString)
        )

####+BEGIN: bx:cs:py3:section :title "cmndsList -- List C-CMNDs and F-CMNDs in a given file and in icm librarytitle"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *cmndsList -- List C-CMNDs and F-CMNDs in a given file and in icm librarytitle*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "cmndList_allMethods" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<cmndList_allMethods>> ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class cmndList_allMethods(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  List All Classed-CMNDs.
        Is based on subclasses of Cmnd and which are in the main module.
When interactive is false, return the list and when true print it and return the list.
        #+end_org """)

        allClassedCmndNames = cs.cmndSubclassesNames()

        if interactive:
            ucf.listPrintItems(allClassedCmndNames)

        return allClassedCmndNames


####+BEGIN: bx:cs:py3:section :title "GLOBAL Declaration Of mainsClassedCmndsGlobal = None"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *GLOBAL Declaration Of mainsClassedCmndsGlobal = None*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

mainsClassedCmndsGlobal = None

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "cmndList_mainsMethods" :comment "USED IN MAIN" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv "importedCmnds mainFileName importedCmndsFilesList"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<cmndList_mainsMethods>>  *USED IN MAIN* ro=cli pyInv=importedCmnds mainFileName importedCmndsFilesList   [[elisp:(org-cycle)][| ]]
#+end_org """
class cmndList_mainsMethods(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             importedCmnds: typing.Any=None,   # pyInv Argument
             mainFileName: typing.Any=None,   # pyInv Argument
             importedCmndsFilesList: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:
        """USED IN MAIN"""
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Is based on subclasses of Cmnd and which are in the main module.
When interactive is false, return the list and when true print it and return the list.

importedCmndsList was added later with icmMainProxy.
*** TODO Should return through cmndOutcome
        #+end_org """)

        global mainsClassedCmndsGlobal

        allClassedCmndNames = cs.cmndSubclassesNames()

        if not mainFileName:
            mainFileName = sys.argv[0]

        mainClasses = b.ast.ast_topLevelClassNamesInFile(
            mainFileName,
        )

        #print mainClasses

        relevantClasses = mainClasses
        for key, modPath in importedCmnds.items():
            if modPath.endswith('.pyc') and os.path.exists(modPath[:-1]):
                modPath = modPath[:-1]
            relevantClasses += b.ast.ast_topLevelClassNamesInFile(modPath)

        for modPath in importedCmndsFilesList:
            if modPath.endswith('.pyc') and os.path.exists(modPath[:-1]):
                modPath = modPath[:-1]
            relevantClasses += b.ast.ast_topLevelClassNamesInFile(modPath)

        mainsClassedCmnds = set.intersection(
            set(allClassedCmndNames),
            set(relevantClasses),
        )

        #if rtInv.outs: NOTYET
        if False:
            b.ast.listPrintItems(mainsClassedCmnds)

        mainsClassedCmndsGlobal = mainsClassedCmnds

        return mainsClassedCmnds

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "cmndList_libsMethods" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<cmndList_libsMethods>> ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class cmndList_libsMethods(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  List All NAMES of C-CMNDs of the Libs Module.
        When interactive is false, return the list and when true print it.

        #+end_org """)


        global mainsClassedCmndsGlobal

        allClassedCmndNames = cs.cmndSubclassesNames()

        #mainClasses = ucf.ast_topLevelClassNamesInFile(
        #    sys.argv[0]
        #)

        #ANN_here(allClassedCmndNames)
        #print mainClasses
        #libsClassedCmnds = set(allClassedCmndNames) - set(mainClasses)
        libsClassedCmnds = set(allClassedCmndNames) - set(mainsClassedCmndsGlobal)

        #if interactive:
        if True:
            #b.ast.listPrintItems(libsClassedCmnds)
            print(libsClassedCmnds)

        return libsClassedCmnds

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "cmndClassDocStr" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 1 :pyInv "cmndName"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<cmndClassDocStr>> argsMax=1 ro=cli pyInv=cmndName   [[elisp:(org-cycle)][| ]]
#+end_org """
class cmndClassDocStr(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 1,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
             cmndName: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:

####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Given a list of cmnds as Args, for each return the the class docStr.
        The Cmnd class from which this is drived, includes docStr extractors.
        #+end_org """)

        G = cs.globalContext.get()
        if not cmndName:
            if not interactive:
                io.eh.problem_usageError("")
                return None
            cmndName = G.icmRunArgsGet().cmndArgs[0]

        cmndClass = cmndNameToClass(cmndName)
        if not cmndClass: return None

        docStr = cmndClass().docStrClass()

        if interactive: print(docStr)

        return docStr

####+BEGIN: b:py3:cs:cmnd/classHead :modPrefix "" :cmndName "cmndHelp" :comment "" :parsMand "" :parsOpt "" :argsMin 1 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<cmndHelp>> argsMin=1 argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class cmndHelp(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
        #+end_org """)

        cmndName = effectiveArgsList[0]

        cmndClass = cmndNameToClass(cmndName)
        if not cmndClass: return None

        docStr = cmndClass().cmndDocStr()

        if interactive: print(docStr)
        return docStr


####+BEGIN: b:py3:cs:cmnd/classHead :modPrefix "" :cmndName "null" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<null>> ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class null(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] A command that does nothing. The null Command. -- Can be combined with --load.
    When used with --load it can result in execution of loaded extensions.
        #+end_org """)

        return cmndOutcome

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "cmndMethodDocStr" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<cmndMethodDocStr>> ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class cmndMethodDocStr(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  "Given a list of cmnds as Args, for each return the cmnd() funcs docStr.
        The Cmnd class from which this is drived, includes docStr extractors.
        #+end_org """)

        G = cs.globalContext.get()
        if not cmndName:
            if not interactive:
                io.eh.problem_usageError("")
                return
            cmndName = G.icmRunArgsGet().cmndArgs[0]

        cmndClass = cmndNameToClass(cmndName)
        if not cmndClass: return

        docStr = cmndClass().docStrCmndMethod()

        if interactive:
            print(docStr)

        return docStr

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "cmndDocStrShort" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<cmndDocStrShort>> ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class cmndDocStrShort(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Given a list of cmnds as Args, for each return the the class docStr.
        The Cmnd class from which this is drived, includes docStr extractors.
        #+end_org """)

        classDocStr = cmndClassDocStr().cmnd(
                interactive=False,
                cmndName=cmndName,
        )
        if not classDocStr: return None

        shortDocStr = ucf.STR_getFirstLine(classDocStr)

        if interactive: print(shortDocStr)
        return shortDocStr

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "cmndDocStrFull" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv "cmndName"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<cmndDocStrFull>> ro=cli pyInv=cmndName   [[elisp:(org-cycle)][| ]]
#+end_org """
class cmndDocStrFull(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             cmndName: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:

####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Given a list of cmnds as Args, for each return the cmnd() funcs docStr.
        The Cmnd class from which this is drived, includes docStr extractors.
        #+end_org """)

        classDocStr = cmndClassDocStr().cmnd(
                interactive=False,
                cmndName=cmndName,
        )
        if not classDocStr: return None

        methodDocStr = cmndMethodDocStr().cmnd(
                interactive=False,
                cmndName=cmndName,
        )
        if not methodDocStr: return None

        longDocStr = classDocStr + "\n" + methodDocStr

        if interactive: print(longDocStr)
        return longDocStr


#
# NOTYET. Added on 12/16/2021.

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "classDocStrOf" :comment "" :parsMand "" :parsOpt "" :argsMin 1 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<classDocStrOf>> argsMin=1 argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class classDocStrOf(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  fullUpdate docString is here.
        #+end_org """)

        #thisCmnd = fullUpdate()
        thisCmnd = eval(f"__main__.{effectiveArgsList[0]}()")
        thisCmnd.obtainDocStrSet()
        thisCmnd.cmnd()
        return f"{thisCmnd.docStrClass()}"


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
