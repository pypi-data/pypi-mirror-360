# -*- coding: utf-8 -*-

""" #+begin_org
* *[Summary]* :: A =PyLib= for dispatching CS Main.
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

import __main__

import typing
import types

import sys

from bisos.b import b_io
from bisos.b import cs
from bisos import b

import importlib


####+BEGIN: b:py3:cs:func/typing :funcName "classedCmndsDict" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /classedCmndsDict/   [[elisp:(org-cycle)][| ]]
#+end_org """
def classedCmndsDict(
####+END:
        importedCmndsModules: typing.List[str],
) -> typing.Dict[str, typing.Any]:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Given a list of modules as =importedCmndsModules=, return a dictionary of [cmndName, cmndClass]
    The resulting dictionary also include built-in cmnds and also __main__

    Implemetation:: is currently redundant, it overlaps inCmnd.cmndList_mainsMethods()
    for each moduleName, we find its file; we then use inCmnd.cmndList_mainsMethods()
    to get a list of all the CmndNames in those files. Then for each of the
    CmndNames, we find the CmndClass.
    #+end_org """

    from bisos.b.cs import inCmnd  #  Should be done here to prevent circular import

    importedCmndsFilesList = []
    cmndsModulesList = importedCmndsModules

    for moduleName in importedCmndsModules:
        # print(f"INFO:: moduleName={moduleName}")
        if 'plantedCsu' in moduleName:
            continue

        spec = importlib.util.find_spec(moduleName)
        if spec is None:
            print(f"EH_Problem: find_spec failed for {moduleName}")
            continue

        importedCmndsFilesList.append(spec.origin)

    for moduleName in ["bisos.b.cs.inCmnd", "bisos.b.cs.examples", "bisos.b.cs.rpyc", "bisos.b.cs.ro"]:
        # print(f"INFO:: moduleName={moduleName}")

        if moduleName not in cmndsModulesList:
            spec = importlib.util.find_spec(moduleName)
            if spec is None:
                print(f"EH_Problem:: find_spec failed for {moduleName}")
                continue

            cmndsModulesList.append(moduleName)
            importedCmndsFilesList.append(spec.origin)


    # print(importedCmndsFilesList)

    rtInv = cs.RtInvoker.new_cmnd()
    outcome = b.op.Outcome()

    callDict = dict()
    for eachCmnd in inCmnd.cmndList_mainsMethods().cmnd(
            rtInv=rtInv,
            cmndOutcome=outcome,
            importedCmnds={}, # __main__.g_importedCmnds -- Being obsoleted
            mainFileName=__main__.__file__,
            importedCmndsFilesList=importedCmndsFilesList,
    ):
        # print(f"INFO:: eachCmnd={eachCmnd}")

        mainModule = sys.modules['__main__']
        # Use getattr to check for the attribute, defaulting to None if it doesn't exist
        cmndClass = getattr(mainModule, eachCmnd, None)
        if cmndClass is None:
            # print(f"TRIVIAL:: {eachCmnd} is not in __main__")
            pass
        else:
            # print(f"INFO:: Added __main__.{eachCmnd}")
            callDict[eachCmnd] = cmndClass
            continue

        for eachModuleName in cmndsModulesList:
            eachModule = importlib.import_module(eachModuleName)
            cmndClass = getattr(eachModule, eachCmnd, None)
            if cmndClass is None:
                # print(f"TRIVIAL:: {eachCmnd} is not in {eachModuleName}")
                pass
            else:
                # print(f"INFO:: Added {eachModuleName}::{eachCmnd}")
                callDict[eachCmnd] = cmndClass
                continue

    # print(callDict)

    return callDict


####+BEGIN: bx:cs:py3:func :funcName "g_csMain" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /g_csMain/  [[elisp:(org-cycle)][| ]]
#+end_org """
def g_csMain(
####+END:
        noCmndEntry=None,   # Name of cmnd to invoke when nothing is specified on the command line
        extraParamsHook=None,   # List of additional parameters
        importedCmndsModules=[],
        csPreCmndsHook=None,
        csPostCmndsHook=None,
        csInfo=None,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] This ICM's specific information is passed to G_mainWithClass
    #+end_org """

    G = cs.globalContext.get()
    G.csInfoSet(csInfo)

    examples = None
    mainEntry = None

    if noCmndEntry:
        if type(noCmndEntry) is types.FunctionType:
            mainEntry = noCmndEntry
            # examples is None
        else:  # We then assume it is a Cmnd
            examples = noCmndEntry
            mainEntry = noCmndEntry

    # With atexit, sys.exit raises SystemExit

    try:
        sys.exit(
            cs.G_mainWithClass(
                inArgv=sys.argv[1:],                 # Mandatory
                #extraArgs=__main__.g_argsExtraSpecify,        # Mandatory
                extraArgs=extraParamsHook,
                G_examples=examples,               # Mandatory
                classedCmndsDict=classedCmndsDict(importedCmndsModules),   # Mandatory
                mainEntry=mainEntry,
                g_icmPreCmnds=csPreCmndsHook,
                g_icmPostCmnds=csPostCmndsHook,
            )
        )
    except SystemExit as e:
        # Handle the SystemExit exception
        # print(f"SystemExit caught with code: {e}")
        pass


####+BEGIN: b:py3:cs:func/typing :funcName "G_main" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /G_main/   [[elisp:(org-cycle)][| ]]
#+end_org """
def G_main(
####+END:
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Replaces ICM dispatcher for other command line args parsings.
    #+end_org """
    pass


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
