# -*- coding: utf-8 -*-

""" #+begin_org
* *[Summary]* :: A =CmndSvc= for
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
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['niche'], }
csInfo['version'] = '202209071237'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'niche-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* /[[elisp:(org-cycle)][| Description |]]/ :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/COMEEGA/_nodeBase_/fullUsagePanel-en.org][BISOS COMEEGA Panel]]
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

from bisos.b import cs
from bisos import b
from bisos.b import b_io


####+BEGIN: bx:cs:python:func :funcName "myNicheNameGet" :funcType "anyOrNone" :retType "bool" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /myNicheNameGet/ retType=bool argsList=nil  [[elisp:(org-cycle)][| ]]
#+end_org """
def myNicheNameGet():
####+END:
    """ #+begin_org
** Return with -niche name for running program. If it already has a -niche we take it out and re-insert it.
    #+end_org """
    myName = cs.G.icmMyName()
    myName = myName.replace('.cs', '')
    myName = myName.replace('-niche', '')
    return (f"{myName}-niche.cs")


####+BEGIN: bx:cs:python:func :funcName "myUnNicheNameGet" :funcType "anyOrNone" :retType "bool" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /myUnNicheNameGet/ retType=bool argsList=nil  [[elisp:(org-cycle)][| ]]
#+end_org """
def myUnNicheNameGet():
####+END:
    """ #+begin_org
**  Return with -niche name for running program.
    #+end_org """
    myName = cs.G.icmMyName()
    myName = myName.replace('.cs', '')
    myName = myName.replace('-niche', '')
    return (f"{myName}.cs")


####+BEGIN: bx:cs:python:func :funcName "nicheRun" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "nicheCs nicheAction"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /nicheRun/ retType=bool argsList=(nicheCs nicheAction)  [[elisp:(org-cycle)][| ]]
#+end_org """
def nicheRun(
    nicheCs,
    nicheAction,
):
####+END:
    """ #+begin_org
**  Locate nicheCs and run it.

    if [ -e $(G_icmBaseDirGet)/${nicheIcm} ] ; then
        lpDo $(G_icmBaseDirGet)/${nicheIcm} ${G_commandPrefs} -i "${nicheCommand}"
    else
        io.eh.problem "Missing $(G_icmBaseDirGet)/${nicheIcm} -- Execution Skipped"
        lpReturn 101
    fi

    #+end_org """
    print(f"""NOTYET, {nicheCs} {nicheAction}""")


####+BEGIN: bx:cs:python:func :funcName "unNicheRunExamples" :funcType "anyOrNone" :retType "bool" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /unNicheRunExamples/ retType=bool argsList=nil  [[elisp:(org-cycle)][| ]]
#+end_org """
def unNicheRunExamples():
####+END:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]] To be sorted out.

$( examplesSeperatorChapter "Run UnNiche ICM" )
${G_myUnNicheName}
    #+end_org """
    print(f"""\
    cs.examples.menuChapter('*Run UnNiche ICM*')
    {myUnNicheNameGet()}\
""")




####+BEGIN: bx:cs:python:func :funcName "examplesNicheRun" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "nicheScope"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /examplesNicheRun/ retType=bool argsList=(nicheScope)  [[elisp:(org-cycle)][| ]]
#+end_org """
def examplesNicheRun(
    nicheScope,
):
####+END:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]] Based on =nicheScope= provide examples for running -niche based on realm.
This is based on the bash nich_lib.sh version. See that for details.
        #+end_org """

    myNicheName = myNicheNameGet()

    if nicheScope == "container":
        outcome =  b.subProc.WOpW(invedBy=None, log=0).bash(
            f"""sysCharDeploy.sh -i selectedContainerBxoPath""")
        if outcome.isProblematic():
            b_io.eh.badOutcome(outcome)
        cs.examples.menuChapter('*Container Niche Examples*')
        print(f"""{outcome.stdoutRstrip}/sys/bin/{myNicheName}""")

    elif  nicheScope == "site":
        outcome =  b.subProc.WOpW(invedBy=None, log=0).bash(
            f"""sysCharDeploy.sh -i selectedSiteBxoPath""")
        if outcome.isProblematic():
            b_io.eh.badOutcome(outcome)
        cs.examples.menuChapter('*Selected Site Niche Examples*')
        print(f"""{outcome.stdoutRstrip}/sys/bin/{myNicheName}""")

    elif  nicheScope == "controller":
        outcome =  b.subProc.WOpW(invedBy=None, log=0).bash(
            f"""usgBpos.sh -i usgBpos_controller_bxoPath""")
        if outcome.isProblematic():
            b_io.eh.badOutcome(outcome)
        cs.examples.menuChapter('*Selected Controller Niche Examples*')
        print(f"""{outcome.stdoutRstrip}/sys/bin/{myNicheName}""")

    elif  nicheScope == "usageEnvs":
        outcome =  b.subProc.WOpW(invedBy=None, log=0).bash(
            f"""usgBpos.sh -i usgBpos_usageEnvs_fullUse_bxoPath""")
        if outcome.isProblematic():
            b_io.eh.badOutcome(outcome)
        cs.examples.menuChapter('*Selected Usage Niche Examples*')
        print(f"""{outcome.stdoutRstrip}/sys/bin/{myNicheName}""")

    else:
        b_io.eh.problem_usageError(
            f"""Unknown nicheScope={nicheScope}"""
        )

    return


####+BEGIN: b:prog:file/endOfFile :extraParams nil
""" #+begin_org
* *[[elisp:(org-cycle)][| END-OF-FILE |]]* :: emacs and org variables and control parameters
#+end_org """
### local variables:
### no-byte-compile: t
### end:
####+END:
