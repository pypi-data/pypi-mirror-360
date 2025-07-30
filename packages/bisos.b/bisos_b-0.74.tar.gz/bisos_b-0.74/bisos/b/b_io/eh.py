# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =BPF-Lib= for log based error processing.
#+end_org """

####+BEGIN: b:py3:cs:file/dblockControls :classification "bpf-lib"
""" #+begin_org
* [[elisp:(org-cycle)][| /Control Parameters Of This File/ |]] :: dblk ctrls classifications=bpf-lib
#+BEGIN_SRC emacs-lisp
(setq-local b:dblockControls t) ; (setq-local b:dblockControls nil)
(put 'b:dblockControls 'py3:cs:Classification "bpf-lib") ; one of cs-mu, cs-u, cs-lib, bpf-lib, pyLibPure
#+END_SRC
#+RESULTS:
: bpf-lib
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
** This File: /bisos/git/auth/bxRepos/bisos-pip/b/py3/bisos/b/b_io/eh.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:python:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['eh'], }
csInfo['version'] = '202209252745'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'eh-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/PyFwrk/bisos.crypt/_nodeBase_/fullUsagePanel-en.org][PyFwrk bisos.crypt Panel]]
Module description comes here.
** Relevant Panels:
** Status: In use with BISOS
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

####+BEGIN: b:py3:cs:orgItem/basic :type "=PyImports= " :title "*Py Library IMPORTS*" :comment "-- with classification based framework/imports"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =PyImports=  [[elisp:(outline-show-subtree+toggle)][||]] *Py Library IMPORTS* -- with classification based framework/imports  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:framework/imports :basedOn "classification"
""" #+begin_org
** Imports Based On Classification=bpf-lib
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io

####+END:

import sys
import logging

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "EH: ICM Error Handling On Top Of Python Exceptions" :anchor "" :extraInfo " (io.eh. Module)"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _EH: ICM Error Handling On Top Of Python Exceptions_: |]]   (io.eh. Module)  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END

####+BEGIN: b:py3:cs:func/typing :funcName "critical_cmndArgsPositional" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /critical_cmndArgsPositional/   [[elisp:(org-cycle)][| ]]
#+end_org """
def critical_cmndArgsPositional(
####+END:
        *v,
        **k,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Used to report problems with expected positional arguments.
    #+end_org """

    logger = b_io.log.controller.loggerGet()

    b_io.log.controller.formatterExtra()

    pathname, lineno, funcName = b.ast.stackFrameInfoGetValues(2)

    outString = format(*v, **k)
    logger.critical(
        f"EH_Critical_cmndArgsPositional: {outString}",
        extra={
            'extraPathname': pathname,
            'extraLineno': lineno,
            'extraFuncName': funcName,
        }
    )

    b_io.log.controller.formatterBasic()

    return
    #raise RuntimeError()

####+BEGIN: b:py3:cs:func/typing :funcName "critical_cmndArgsOptional" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /critical_cmndArgsOptional/   [[elisp:(org-cycle)][| ]]
#+end_org """
def critical_cmndArgsOptional(
####+END:
        *v,
        **k,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    logger = b_io.log.controller.loggerGet()

    b_io.log.controller.formatterExtra()

    pathname, lineno, funcName = b.ast.stackFrameInfoGetValues(2)

    outString = format(*v, **k)
    logger.critical(
        f"EH_Critical_cmndArgsOptional: {outString}",
        extra={
            'extraPathname': pathname,
            'extraLineno': lineno,
            'extraFuncName': funcName,
        }
    )

    b_io.log.controller.formatterBasic()

    return


    #raise RuntimeError()

####+BEGIN: b:py3:cs:func/typing :funcName "critical_usageError" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /critical_usageError/   [[elisp:(org-cycle)][| ]]
#+end_org """
def critical_usageError(
####+END:
        *v,
        **k,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    logger = b_io.log.controller.loggerGet()

    b_io.log.controller.formatterExtra()

    pathname, lineno, funcName = b.ast.stackFrameInfoGetValues(2)

    outString = format(*v, **k)
    logger.critical(
        f"EH_Critical_UsageError: {outString}",
        extra={
            'extraPathname': pathname,
            'extraLineno': lineno,
            'extraFuncName': funcName,
        }
    )

    b_io.log.controller.formatterBasic()

    # return(b.op.ReturnCode.UsageError)
    #raise RuntimeError()

####+BEGIN: b:py3:cs:func/typing :funcName "problem_notyet" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /problem_notyet/   [[elisp:(org-cycle)][| ]]
#+end_org """
def problem_notyet(
####+END:
        *v,
        **k,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    logger = b_io.log.controller.loggerGet()

    b_io.log.controller.formatterExtra()

    pathname, lineno, funcName = b.ast.stackFrameInfoGetValues(2)

    outString = format(*v, **k)
    logger.critical(
        f"EH_Problem_NOTYET: {outString}",
        extra={
            'extraPathname': pathname,
            'extraLineno': lineno,
            'extraFuncName': funcName,
        }
    )

    b_io.log.controller.formatterBasic()

    #raise RuntimeError()

####+BEGIN: b:py3:cs:func/typing :funcName "problem_info" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /problem_info/   [[elisp:(org-cycle)][| ]]
#+end_org """
def problem_info(
####+END:
        *v,
        **k,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    logger = b_io.log.controller.loggerGet()

    b_io.log.controller.formatterExtra()

    pathname, lineno, funcName = b.ast.stackFrameInfoGetValues(2)

    outString = format(*v, **k)
    logger.critical(
        f"EH_Problem_INFO: {outString}",
        extra={
            'extraPathname': pathname,
            'extraLineno': lineno,
            'extraFuncName': funcName,
        }
    )

    b_io.log.controller.formatterBasic()

    return



####+BEGIN: b:py3:cs:func/typing :funcName "problem_usageError" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /problem_usageError/   [[elisp:(org-cycle)][| ]]
#+end_org """
def problem_usageError(
####+END:
        *v,
        **k,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    logger = b_io.log.controller.loggerGet()

    b_io.log.controller.formatterExtra()

    pathname, lineno, funcName = b.ast.stackFrameInfoGetValues(2)

    outString = format(*v, **k)
    logger.critical(
        f"EH_Problem_UsageError: {outString}",
        extra={
            'extraPathname': pathname,
            'extraLineno': lineno,
            'extraFuncName': funcName,
        }
    )

    b_io.log.controller.formatterBasic()

    return




####+BEGIN: b:py3:cs:func/typing :funcName "problem_usageError_wOp" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /problem_usageError_wOp/   [[elisp:(org-cycle)][| ]]
#+end_org """
def problem_usageError_wOp(
####+END:
        outcome,
        *v,
        **k,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    logger = b_io.log.controller.loggerGet()

    b_io.log.controller.formatterExtra()

    pathname, lineno, funcName = b.ast.stackFrameInfoGetValues(2)

    outString = format(*v, **k)
    logger.critical(
        f"EH_Problem_UsageError: {outString}",
        extra={
            'extraPathname': pathname,
            'extraLineno': lineno,
            'extraFuncName': funcName,
        }
    )

    b_io.log.controller.formatterBasic()

    errStr='io.eh.: ' + outString + ' -- ' + b.ast.stackFrameInfoGet(2)
    return(outcome.set(
        opError=b.op.OpError.UsageError,
        opErrInfo=errStr,
    ))


####+BEGIN: b:py3:cs:func/typing :funcName "critical_unassigedError" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /critical_unassigedError/   [[elisp:(org-cycle)][| ]]
#+end_org """
def critical_unassigedError(
####+END:
        *v,
        **k,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    logger = b_io.log.controller.loggerGet()

    b_io.log.controller.formatterExtra()

    pathname, lineno, funcName = b.ast.stackFrameInfoGetValues(2)

    outString = format(*v, **k)
    logger.critical(
        f"EH_Critical_UnassigedError: {outString}",
        extra={
            'extraPathname': pathname,
            'extraLineno': lineno,
            'extraFuncName': funcName,
        }
    )

    b_io.log.controller.formatterBasic()
    return
    #raise RuntimeError()

####+BEGIN: b:py3:cs:func/typing :funcName "critical_oops" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /critical_oops/   [[elisp:(org-cycle)][| ]]
#+end_org """
def critical_oops(
####+END:
        *v,
        **k,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    logger = b_io.log.controller.loggerGet()

    b_io.log.controller.formatterExtra()

    pathname, lineno, funcName = b.ast.stackFrameInfoGetValues(2)

    outString = format(*v, **k)
    logger.critical(
        f"EH_Critical_Oops: {outString}",
        extra={
            'extraPathname': pathname,
            'extraLineno': lineno,
            'extraFuncName': funcName,
        }
    )

    b_io.log.controller.formatterBasic()
    return

    # traceback.print_stack()
    #raise RuntimeError()

####+BEGIN: b:py3:cs:func/typing :funcName "critical_exception" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /critical_exception/   [[elisp:(org-cycle)][| ]]
#+end_org """
def critical_exception(
####+END:
        e,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Usage Example:
    try: m=2/0
    except Exception as e: io.eh.critical_exception(e)
    #+end_org """

    logControler = b_io.log.Control()
    logger = logControler.loggerGet()

    #fn = FUNC_currentGet()

    outString = format(e)

    logger.critical('io.eh.: ' + outString + ' -- ' + b.ast.stackFrameInfoGet(2) )

    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logger.critical(
        "io.eh.: {exc_type} {fname} {lineno}"
        .format(
            exc_type=exc_type,
            fname=fname,
            lineno=exc_tb.tb_lineno
        )
    )

    logging.exception(e)

    # Or any of the
    #logger.error("io.eh.critical_exception", exc_info=True)
    #print(traceback.format_exc())

####+BEGIN: b:py3:cs:func/typing :funcName "badOutcome" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /badOutcome/   [[elisp:(org-cycle)][| ]]
#+end_org """
def badOutcome(
####+END:
        outcome,
        outcomeInfo=None,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    outcomeInfoStr=""
    if outcomeInfo is not None:
        outcomeInfoStr=f" -- {outcomeInfo}"

    print(f"io.eh.badOutcome: {outcomeInfoStr} -- InvokedBy NOTYET, Operation Failed: Stdcmnd={outcome.stdcmnd} Error={outcome.error} -- {outcome.errInfo}"
          , file=sys.stderr)
    print(('io.eh.: ' + ' -- ' + b.ast.stackFrameInfoGet(2) ), file=sys.stderr)

    return outcome

####+BEGIN: b:py3:cs:func/typing :funcName "badLastOutcome" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /badLastOutcome/   [[elisp:(org-cycle)][| ]]
#+end_org """
def badLastOutcome(
####+END:
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """
    return (
        io.eh.badOutcome(
            cs.G.lastOpOutcome
        ))

####+BEGIN: b:py3:cs:func/typing :funcName "eh_badLastOutcome" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /eh_badLastOutcome/   [[elisp:(org-cycle)][| ]]
#+end_org """
def eh_badLastOutcome(
####+END:
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    return (
            cs.G.lastOpOutcome
    )


####+BEGIN: b:py3:cs:func/typing :funcName "runTime" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /runTime/   [[elisp:(org-cycle)][| ]]
#+end_org """
def runTime(
####+END:
        *v,
        **k,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    logControler = b_io.log.Control()
    logger = logControler.loggerGet()

    fn = b.ast.FUNC_currentGet()
    argsLength =  b.ast.FUNC_argsLength(fn, v, k)

    if argsLength == 2:   # empty '()'
        outString = ''
    else:
        outString = format(*v, **k)

    logger.error('io.eh.: ' + outString + ' -- ' + b.ast.stackFrameInfoGet(2) )
    raise RuntimeError()

####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
