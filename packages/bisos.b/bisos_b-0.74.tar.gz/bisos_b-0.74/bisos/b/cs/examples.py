# -*- coding: utf-8 -*-

""" #+begin_org
* *[Summary]* :: A =CS-Lib= for facilitating Command Menus.
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
** This File: /bisos/git/auth/bxRepos/bisos-pip/b/py3/bisos/b/cs/examples.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:python:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
from ast import Pass
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['examples'], }
csInfo['version'] = '202209241240'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'examples-Panel.org'
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

__all__ = [ 'commonExamples', ]

import os
import sys

from bisos.b import b_io
from bisos import b

from bisos.b import cs

import collections

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "G_examples" :anchor "" :extraInfo "*G_commonExamples -- Common features included in G_examples() + devExamples(), etc*"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _G_examples_: |]]  *G_commonExamples -- Common features included in G_examples() + devExamples(), etc*  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "commonExamples" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<commonExamples>> ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class commonExamples(cs.Cmnd):
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
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Provide a menu of common icm examples.
        #+end_org """)

        G_myFullName = sys.argv[0]
        G_myName = os.path.basename(G_myFullName)

        menuChapter('/Intercatively Invokable Module (ICM) General Usage Model/')

        print(( G_myName + " --help" ))
        print(( G_myName + " -i model" ))
        print(( G_myName + " -i icmHelp" ))
        print(( G_myName + " -i icmOptionsExamples" ))
        print(( G_myName + " -i csInfo" ))
        print(( G_myName + " -i icmInUpdate ./var" ))
        print(( G_myName + " -i cmndInfo cmndName" ))
        print(( G_myName + " -i cmndInfo cmndInfo" ))
        print(( G_myName + " -i devExamples" ))
        print(( G_myName + " -i describe" ))
        print(( G_myName + " -i describe" + " |" + " emlVisit"))
        print(( G_myName + " -i examples" ))
        print(f"{G_myName} -i examples | emlOutFilter.sh -i iimToEmlStdout  | emlVisit")
        # print(( G_myName + " -i examples" + " |" + " icmToEmlVisit"))

        return(cmndOutcome)


####+BEGIN: b:py3:cs:func/typing :funcName "commonBrief" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /commonBrief/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def commonBrief(
####+END:
        roMenu=False,
        interactive=False,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    G_myFullName = sys.argv[0]
    G_myName = os.path.basename(G_myFullName)

    menuChapter('/Command Service (CS) Brief Usage/')

    print(( G_myName + " -i commonExamples" + "    # Help, Model, icmOptionsExample"))
    print(( G_myName + " -i describe" + " |" + " emlVisit"))
    # print(( G_myName + " -i examples" + " |" + " icmToEmlVisit"))
    print(f"{G_myName} -i examples | emlOutFilter.sh -i iimToEmlStdout  | emlVisit")
    print(( G_myName + " -i visit"))
    print(( """emlVisit -v -n showRun -i gotoPanel """ + G_myFullName))

    invokerName = cs.ro.csMuInvokerName()
    performerName = cs.ro.csMuPerformerName()

    if cs.ro.csMuIsDirect() is True:
        if roMenu is True:
            menuChapter('/Remote Operations -- Performer And Invoker/')

            # print(f"""csRo-manage.cs --perfName="localhost" --rosmu="{G_myName}"  -i ro_sapCreate""")
            # print(f"""{G_myName} --perfName="localhost" -i csPerformer  & # in background Start rpyc CS Service""")
            # print(f"""csRo-manage.cs --perfName="localhost" --rosmu="{G_myName}"  -i ro_fps list""")
            # print(f"""{G_myName}  --perfName="localhost" -i examples""")

            print(( G_myName + " -i roEnable" + "    # Create Symlinks For -roPerf and -roInv"))
            print(( invokerName + "    # Remote Operations Performer"))
            print(( performerName + "   # Remote Operations Invoker"))

    elif cs.ro.csMuIsPerformer() is True:
        menuChapter('/Direct Commands and roInvoker/')
        directName = cs.ro.csMuDirectName()
        invokerName = cs.ro.csMuInvokerName()
        print(( directName + "    # Direct Commands"))
        print(( invokerName + "   # Remote Operations Invoker"))

    elif cs.ro.csMuIsInvoker() is True:
        menuChapter('/Direct Commands and roInvoker/')
        directName = cs.ro.csMuDirectName()
        performerName = cs.ro.csMuPerformerName()
        print(( directName + "    # Direct Commands"))
        print(( performerName + "   # Remote Operations Performer"))

    else:
        oops()


    # menuChapter('*ICM Blee Player Invokations*')
    # b_io.ann.write("icmPlayer.sh -h -v -n showRun -i grouped {G_myName}".format(G_myName=G_myName))

####+BEGIN: b:py3:cs:func/typing :funcName "devExamples" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /devExamples/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def devExamples(
####+END:
        interactive=False,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    G_myName = sys.argv[0]

    print("======== Development =========")

    # print(("python -m trace -l " + G_myName + " | egrep -v " + '\'/python2.7/|\<string\>\''))
    print(("python -m trace -l " + G_myName))
    print(("python -m trace -t " + G_myName))


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "icmOptionsExamples" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<icmOptionsExamples>> ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class icmOptionsExamples(cs.Cmnd):
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
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Print a summary of the ICM Model.
        #+end_org """)

        G_myFullName = sys.argv[0]
        G_myName = os.path.basename(G_myFullName)

        print("==== cmndEx Built-In Feature Examples =====")

        print(( G_myName + " -i icm.cmndExample arg1 arg2" ))
        print(( G_myName + " -v 20" + " -i icm.cmndExample arg1 arg2" ))
        print(( G_myName + " -v 1" + " -i icm.cmndExample arg1 arg2" ))
        print(( G_myName + " --runMode dryRun" + " -i icm.cmndExample arg1 arg2" ))
        print(( G_myName + " -v 1" + " --callTrackings monitor-" + " -i icm.cmndExample arg1 arg2" ))
        print(( G_myName + " -v 1" + " --callTrackings monitor+" + " --callTrackings invoke+" + " -i icm.cmndExample arg1 arg2" ))
        print(( G_myName + " -v 1" + " --callTrackings monitor-" + " --callTrackings invoke-" + " -i icm.cmndExample arg1 arg2" ))
        print(( G_myName + " --docstring" + " -i describe" ))

        return cmndOutcome

####+BEGIN: b:py3:cs:func/typing :funcName "myName" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /myName/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def myName(
####+END:
        myName: str,
        myFullName: str,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Emit =myName= and =myFullName=
    #+end_org """

    print(f"#######    *{myName}*    ##########")
    print(f"=======  {myFullName}   ===========")
    if cs.G.seedOfThisPlant is None:
        pass
        # print("UnSeeded")
    else:
        print(f"=======  PlantedCSU :: {cs.G.plantOfThisSeed}   ===========")
        print(f"=======  Seed :: {cs.G.seedOfThisPlant}   ===========")

####+BEGIN: b:py3:cs:func/typing :funcName "ex_gCommon" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /ex_gCommon/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def ex_gCommon(
####+END:
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    G = cs.IcmGlobalContext()
    icmExampleMyName(G.icmMyName(), G.icmMyFullName())
    G_commonBriefExamples()
    #G_commonExamples()


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Example Sections" :anchor "" :extraInfo "*cmndExample -- Simple Usage Example -- Seperators*"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Example Sections_: |]]  *cmndExample -- Simple Usage Example -- Seperators*  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END

####+BEGIN: bx:cs:py3:section :title "Menu Sections"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Menu Sections*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "menuPart" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /menuPart/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def menuPart(
####+END:
        title: str,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """
    print(("@@@@@@@@  " + title + "  @@@@@@@@@"))

####+BEGIN: b:py3:cs:func/typing :funcName "menuChapter" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /menuChapter/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def menuChapter(
####+END:
        title: str,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """
    print(("#######  " + title + "  ##########"))

####+BEGIN: b:py3:cs:func/typing :funcName "menuSection" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /menuSection/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def menuSection(
####+END:
        title: str,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """
    print(("=======  " + title + "  =========="))


####+BEGIN: b:py3:cs:func/typing :funcName "menuSubSection" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /menuSubSection/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def menuSubSection(
####+END:
        title: str,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """
    print(("%%%%%%%  " + title + "  %%%%%%%%%%%"))

####+BEGIN: bx:cs:py3:section :title "Menu Items"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Menu Items*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "menuItemInsert" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /menuItemInsert/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def menuItemInsert(
####+END:
        commandLine: str,
        icmName: str='',          # Defaults to G_myName
        verbosity: str='basic',
        comment: str='none',
        icmWrapper: str='',

) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] vebosity is one of: 'none', 'little', 'some',  'full'
    #+end_org """

    G_myFullName = sys.argv[0]
    G_myName = os.path.basename(G_myFullName)

    if comment == 'none':
        fullCommandLine = commandLine
    else:
        fullCommandLine = commandLine + '         ' + comment

    if icmName:
        G_myName = icmName

    if icmWrapper:
        G_myName = icmWrapper + " " + G_myName

    if verbosity == 'none':
        #print( G_myName + " -v 30" + " " + fullCommandLine)
        print(( G_myName + " " + fullCommandLine))
    elif verbosity == 'basic':
        print(( G_myName + " -v 1"  + " " + fullCommandLine ))
    elif verbosity == 'little':
        print(( G_myName + " -v 20" + " " + fullCommandLine ))
    elif verbosity == 'some':
        print(( G_myName + " -v 1"  + " --callTrackings monitor-" + " --callTrackings invoke-" + " " + fullCommandLine ))
    elif verbosity == 'full':
        print(( G_myName + " -v 1"  + " --callTrackings monitor+" + " --callTrackings invoke+" + " " + fullCommandLine ))
    else:
        return io.eh.io.eh.critical_oops('')

####+BEGIN: b:py3:cs:func/typing :funcName "csCmndLine" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /csCmndLine/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def csCmndLine(
####+END:
        cmndName: str,
        cmndPars: typing.Dict[str, str],
        cmndArgs: str,
        verbosity: str='basic',
        comment: str='none',
        icmWrapper: str='',
        icmName: str='',
) -> str:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Returns cmndLine as string.
    #+end_org """

    cmndParsStr = ""
    for key in cmndPars:
        cmndParsStr += f"""--{key}="{cmndPars[key]}" """

    if not icmName:
        icmName = cs.G.icmMyName()

    dashV = icmVerbosityTagToDashV(verbosity)

    cmndLine = f"""{icmWrapper} {icmName} {dashV} {cmndParsStr} -i {cmndName} {cmndArgs} {comment}"""

    return cmndLine

####+BEGIN: b:py3:cs:func/typing :funcName "icmVerbosityTagToDashV" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /icmVerbosityTagToDashV/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def icmVerbosityTagToDashV(
####+END:
        verbosity: str,
) -> str:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    result = ""

    if verbosity == 'none':
        result = ""
    elif verbosity == 'basic':
        result = " -v 1"
    elif verbosity == 'little':
        result = " -v 20"
    elif verbosity == 'some':
        result = " -v 1"
    elif verbosity == 'full':
        result = " -v 1 --callTrackings monitor+ --callTrackings invoke+"
    else:
        return io.eh.io.eh.critical_oops('')
    return result

####+BEGIN: b:py3:cs:func/typing :funcName "ex_gExtCmndMenuItem" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /ex_gExtCmndMenuItem/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def ex_gExtCmndMenuItem(
####+END:
        cmndName: str,
        cmndPars: typing.Dict[str, str],
        cmndArgs: str,
        verbosity: str='basic',
        comment: str='none',
        icmWrapper: str='',
        icmName: str='',
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Returns cmndLine as string.
    #+end_org """

    cmndParsStr = ""
    for key in cmndPars:
        cmndParsStr += """--{parName}="{parValue}" """.format(parName=key, parValue=cmndPars[key])

    cmndLine = """{cmndParsStr} -i {cmndName} {cmndArgs}""".format(
        cmndName=cmndName, cmndParsStr=cmndParsStr, cmndArgs=cmndArgs
    )

    menuItem(
        cmndLine=cmndLine,
        verbosity=verbosity,
        comment=comment,
        icmWrapper=icmWrapper,
        icmName=icmName,
    )

####+BEGIN: b:py3:cs:func/typing :funcName "perfNameParsInsert" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /perfNameParsInsert/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def perfNameParsInsert(
####+END:
        pars: collections.OrderedDict,
        perfName: str,
) -> collections.OrderedDict:
    result = pars.copy()
    result.update({'perfName': perfName})
    result.move_to_end('perfName', last=False)
    return result

####+BEGIN: b:py3:cs:func/typing :funcName "cmndEnter" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /cmndEnter/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def cmndEnter(
####+END:
        name: str,
        pars: collections.OrderedDict[str, str]=collections.OrderedDict(),
        args: str="",
        verb: list[str]=[],
        comment: str='none',
        wrapper: str='',
        csName: str='',
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Constructs cmndLine based on positional args and specific other args. Calls ~menuItemInsert~.
    For services, it looks at invModel and roSap.
    #+end_org """

    #rpycEnable = ""

    #if cs.G.icmRunArgsGet().ex_invModel == "rpyc":
    #    rpycEnable = " --invModel=rpyc"

    roEnable = ""

    perfName = cs.G.icmRunArgsGet().perfName
    if perfName is not None:
        roEnable = f" --perfName={perfName}"

    cmndParsStr = ""
    for key in pars:
        cmndParsStr += f"""--{key}="{pars[key]}" """

    cmndLine = f"""{cmndParsStr}{roEnable} -i {name} {args}"""

    #print(cmndLine)

    if not verb:
        verb = ['none']

    for eachVerbosity in verb:
        menuItemInsert(
            commandLine=cmndLine,
            verbosity=eachVerbosity,
            comment=comment,
            icmWrapper=wrapper,
            icmName=csName,
        )




####+BEGIN: b:py3:cs:func/typing :funcName "cmndInsert" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /cmndInsert/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def cmndInsert(
####+END:
        cmndName: str,
        cmndPars: typing.Dict[str, str],
        cmndArgs: str,
        verbosity: str='basic',
        comment: str='none',
        icmWrapper: str='',
        icmName: str='',
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Constructs cmndLine based on positional args and specific other args. Calls ~menuItemInsert~.
    For services, it looks at invModel and roSap.
    #+end_org """

    #rpycEnable = ""

    #if cs.G.icmRunArgsGet().ex_invModel == "rpyc":
    #    rpycEnable = " --invModel=rpyc"

    roEnable = ""

    perfName = cs.G.icmRunArgsGet().perfName
    if perfName is not None:
        roEnable = f" --perfName={perfName}"


    cmndParsStr = ""
    for key in cmndPars:
        cmndParsStr += """--{parName}="{parValue}" """.format(parName=key, parValue=cmndPars[key])

    cmndLine = f"""{cmndParsStr}{roEnable} -i {cmndName} {cmndArgs}"""

    menuItemInsert(
        commandLine=cmndLine,
        verbosity=verbosity,
        comment=comment,
        icmWrapper=icmWrapper,
        icmName=icmName,
    )


####+BEGIN: b:py3:cs:func/typing :funcName "execInsert" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /execInsert/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def execInsert(
####+END:
        execLine: str,
        wrapper: str='',
        comment: str='none',
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Output an Non-ICM menu line.
    #+end_org """

    if comment == 'none':
        fullCommandLine = execLine
    else:
        fullCommandLine = execLine + '         ' + comment

    if wrapper:
        fullCommandLine = wrapper + fullCommandLine

    print(fullCommandLine)

####+BEGIN: b:py3:cs:func/typing :funcName "cmndExampleExternalCmndItem" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /cmndExampleExternalCmndItem/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def cmndExampleExternalCmndItem(
####+END:
        commandLine: str,
        verbosity: str='basic',
        comment: str='none'
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Output an Non-ICM menu line.
    #+end_org """

    #G_myFullName = sys.argv[0]
    #G_myName = os.path.basename(G_myFullName)

    if comment == 'none':
        fullCommandLine = commandLine
    else:
        fullCommandLine = commandLine + '         ' + comment

    print( fullCommandLine )


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
