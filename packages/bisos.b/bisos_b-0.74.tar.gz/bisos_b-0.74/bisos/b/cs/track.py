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
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['track'], }
csInfo['version'] = '202209082210'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'track-Panel.org'
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



#from bisos.b import cs
#from bisos.cs import runArgs

from bisos.b import b_io

from bisos import b

import sys
import datetime



"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  TIME_nowTag    [[elisp:(org-cycle)][| ]]
"""

def TIME_nowTag():
    INTERVAL_TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"
    startTime = datetime.strftime(datetime.now(), INTERVAL_TIMESTAMP_FORMAT)
    return startTime
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  STR_insertMultiples    [[elisp:(org-cycle)][| ]]
"""

def STR_indentMultiples(multiple=1, unit="  "): STR_insertMultiples(multiple=1, unit="  ") # obsoleted


def STR_insertMultiples(
                multiple=1,
                unit="  ",
):
    """Return multiples of unit."""
    retVal = ""
    count = 0
    while count < multiple:
        retVal = retVal + unit
        count = count + 1
    return retVal


"""
*  [[elisp:(org-cycle)][| ]]  /General/            :: *Call Tracking (decorators)* [[elisp:(org-cycle)][| ]]
"""



"""
**  [[elisp:(org-cycle)][| ]]  Decorator     ::  Callable Tracking subjectToTracking()   [[elisp:(org-cycle)][| ]]
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  subjectToTracking    [[elisp:(org-cycle)][| ]]
"""

# https://stackoverflow.com/questions/739654/how-to-make-function-decorators-and-chain-them-together
# https://stackoverflow.com/questions/11731136/class-method-decorator-with-self-arguments


def track(fnLoc=True, fnEntry=True, fnExit=True):
    """[DECORATOR-WITH-ARGS:]  Passes parameters to subSubjectToTracking. See subSubjectToTracking.
    """

    def subSubjectToTracking(fn):
        """[DECORATOR:] tracks calls to a function.

        Returns a decorated version of the input function which "tracks" calls
        made to it by writing out the function's name and the arguments it was
        called with.
        Do so subject to icmRunArgs_isCallTrackingMonitorOn and
        fnLoc, fnEntry, fnExit parameters.
        """

        import functools
        # Unpack function's arg count, arg names, arg defaults
        code = fn.__code__
        argcount = code.co_argcount
        argnames = code.co_varnames[:argcount]
        fn_defaults = fn.__defaults__ or list()
        argdefs = dict(list(zip(argnames[-len(fn_defaults):], fn_defaults)))

        @functools.wraps(fn)
        def wrapped(*v, **k):
            if (fnLoc == False) and (fnEntry == False) and (fnExit == False):
                return fn(*v, **k)

            #if icmRunArgs_isCallTrackingMonitorOff():   # normally on, turns-off with monitor-
                #return fn(*v, **k)

            if not b.cs.runArgs.isCallTrackingMonitorOn(): # normally off, turns-on with monitor+
                return fn(*v, **k)

            # Collect function arguments by chaining together positional,
            # defaulted, extra positional and keyword arguments.
            positional = list(map(b.ast.format_arg_value, list(zip(argnames, v))))
            defaulted = [b.ast.format_arg_value((a, argdefs[a]))
                         for a in argnames[len(v):] if a not in k]
            nameless = list(map(repr, v[argcount:]))
            keyword = list(map(b.ast.format_arg_value, list(k.items())))
            args = positional + defaulted + nameless + keyword

            logControler = b_io.log.controller
            logger = logControler.loggerGet()

            depth = b.ast.stackFrameDepth(2)
            indentation = STR_indentMultiples(multiple=depth)

            # if fnLoc:
            #     logger.debug(format('%s Monitoring(M-Call-%s): ' % (indentation, depth)) + b.ast.stackFrameInfoGet(2))

            if fnEntry:
                b_io.log.controller.formatterExtra()
                pathname, lineno, funcName = b.ast.stackFrameInfoGetValues(2)
                logger.debug(
                    "%s M-Enter-%s: %s(%s) AT %s" % (indentation, depth, fn.__name__, ", ".join(args), b.ast.stackFrameInfoGet(2)),
                    extra={
                        'extraPathname': pathname,
                        'extraLineno': lineno,
                        'extraFuncName': funcName,
                    },
                )
                b_io.log.controller.formatterBasic()

            retVal = fn(*v, **k)

            if fnExit:
                b_io.log.controller.formatterExtra()
                pathname, lineno, funcName = b.ast.stackFrameInfoGetValues(2)
                logger.debug(
                    "%s M-Return-%s(%s):  %s AT %s" % (indentation, depth, fn.__name__, retVal, b.ast.stackFrameInfoGet(2)),
                    extra={
                        'extraPathname': pathname,
                        'extraLineno': lineno,
                        'extraFuncName': funcName,
                    },
                )
                b_io.log.controller.formatterBasic()

            return retVal
        return wrapped
    return subSubjectToTracking


def trackWorks(fnLoc=True, fnEntry=True, fnExit=True):
    """[DECORATOR-WITH-ARGS:]  Passes parameters to subSubjectToTracking. See subSubjectToTracking.
    """

    def subSubjectToTracking(fn):
        """[DECORATOR:] tracks calls to a function.

        Returns a decorated version of the input function which "tracks" calls
        made to it by writing out the function's name and the arguments it was
        called with.
        Do so subject to icmRunArgs_isCallTrackingMonitorOn and
        fnLoc, fnEntry, fnExit parameters.
        """

        import functools
        # Unpack function's arg count, arg names, arg defaults
        code = fn.__code__
        argcount = code.co_argcount
        argnames = code.co_varnames[:argcount]
        fn_defaults = fn.__defaults__ or list()
        argdefs = dict(list(zip(argnames[-len(fn_defaults):], fn_defaults)))

        @functools.wraps(fn)
        def wrapped(*v, **k):
            if (fnLoc == False) and (fnEntry == False) and (fnExit == False):
                return fn(*v, **k)

            #if icmRunArgs_isCallTrackingMonitorOff():   # normally on, turns-off with monitor-
                #return fn(*v, **k)

            if not b.cs.runArgs.isCallTrackingMonitorOn(): # normally off, turns-on with monitor+
                return fn(*v, **k)

            # Collect function arguments by chaining together positional,
            # defaulted, extra positional and keyword arguments.
            positional = list(map(b.ast.format_arg_value, list(zip(argnames, v))))
            defaulted = [b.ast.format_arg_value((a, argdefs[a]))
                         for a in argnames[len(v):] if a not in k]
            nameless = list(map(repr, v[argcount:]))
            keyword = list(map(b.ast.format_arg_value, list(k.items())))
            args = positional + defaulted + nameless + keyword

            logControler = b_io.log.controller
            logger = logControler.loggerGet()

            depth = b.ast.stackFrameDepth(2)
            indentation = STR_indentMultiples(multiple=depth)

            # if fnLoc:
            #     logger.debug(format('%s Monitoring(M-Call-%s): ' % (indentation, depth)) + b.ast.stackFrameInfoGet(2))

            if fnEntry:
                logger.debug( "%s M-Enter-%s: %s(%s) AT %s" % (indentation, depth, fn.__name__, ", ".join(args), b.ast.stackFrameInfoGet(2)))

            retVal = fn(*v, **k)

            if fnExit:
                logger.debug( "%s M-Return-%s(%s):  %s AT %s" % (indentation, depth, fn.__name__, retVal, b.ast.stackFrameInfoGet(2)))

            return retVal
        return wrapped
    return subSubjectToTracking



def subjectToTrackingNull(fnLoc=True, fnEntry=True, fnExit=True):
    """[DECORATOR-WITH-ARGS:]  Passes parameters to subSubjectToTracking. See subSubjectToTracking.
    """
    #import bisos.cs.runArgs

    def subSubjectToTracking(fn):
        """[DECORATOR:] tracks calls to a function.

        Returns a decorated version of the input function which "tracks" calls
        made to it by writing out the function's name and the arguments it was
        called with.
        Do so subject to icmRunArgs_isCallTrackingMonitorOn and
        fnLoc, fnEntry, fnExit parameters.
        """

        import functools
        # Unpack function's arg count, arg names, arg defaults
        code = fn.__code__
        argcount = code.co_argcount
        argnames = code.co_varnames[:argcount]
        fn_defaults = fn.__defaults__ or list()
        argdefs = dict(list(zip(argnames[-len(fn_defaults):], fn_defaults)))

        @functools.wraps(fn)
        def wrapped(*v, **k):
            retVal = fn(*v, **k)
            return retVal
        return wrapped
    return subSubjectToTracking



"""
**  [[elisp:(org-cycle)][| ]]  Func          ::  Invokation Tracking do() and doLog()  [[elisp:(org-cycle)][| ]]
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  do    [[elisp:(org-cycle)][| ]]
"""
@track(fnLoc=True, fnEntry=True, fnExit=True)
def do(fn, *v, **k):
    """Invokes fn with args (*v, **k) and logs the invocation and return based on invoke+/-.

    If invoke+ is set, invokation is logged. Otherwise it just invokes the function.
    Example Usage:
    instead of thisFunc(thatArg) in order to track thisFunc we:
    do(thisFunc, thatArg)
    """

    return

    if cs.icmRunArgs_isCallTrackingInvokeOff():
        return fn(*v, **k)

    #
    # Even though the call is identical because of stackFrameInfoGet(2)
    # in there, we are not going to --  return doLog(fn, *v, **k)
    # And instead we are duplicating the code.
    # Consider this an instance for why python should have macros.
    #

    # Unpack function's arg count, arg names, arg defaults
    code = fn.__code__
    argcount = code.co_argcount
    argnames = code.co_varnames[:argcount]
    fn_defaults = fn.__defaults__ or list()
    argdefs = dict(list(zip(argnames[-len(fn_defaults):], fn_defaults)))

    # Collect function arguments by chaining together positional,
    # defaulted, extra positional and keyword arguments.
    positional = list(map(ucf.format_arg_value, list(zip(argnames, v))))
    defaulted = [ucf.format_arg_value((a, argdefs[a]))
                 for a in argnames[len(v):] if a not in k]
    nameless = list(map(repr, v[argcount:]))
    keyword = list(map(ucf.format_arg_value, list(k.items())))
    args = positional + defaulted + nameless + keyword

    logControler = b.io.log.Control()
    logger = logControler.loggerGet()
    depth = ucf.stackFrameDepth(2)
    indentation = ucf.STR_indentMultiples(multiple=depth)

    logger.debug(format('%s Invoking(I-Call-%s): ' % (indentation, depth)) + b.ast.stackFrameInfoGet(2))
    logger.debug( "%s I-Enter-%s: %s(%s)" % (indentation, depth, fn.__name__, ", ".join(args)) )
    retVal = fn(*v, **k)
    logger.debug( "%s I-Return-%s(%s):  %s" % (indentation, depth, fn.__name__, retVal) )
    return retVal


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  doLog    [[elisp:(org-cycle)][| ]]
"""
@track(fnLoc=True, fnEntry=True, fnExit=True)
def doLog(fn, *v, **k):
    """Invokes fn with args (*v, **k) and logs the invocation and return.
    """

    # Unpack function's arg count, arg names, arg defaults
    code = fn.__code__
    argcount = code.co_argcount
    argnames = code.co_varnames[:argcount]
    fn_defaults = fn.__defaults__ or list()
    argdefs = dict(list(zip(argnames[-len(fn_defaults):], fn_defaults)))

    # Collect function arguments by chaining together positional,
    # defaulted, extra positional and keyword arguments.
    positional = list(map(ucf.format_arg_value, list(zip(argnames, v))))
    defaulted = [ucf.format_arg_value((a, argdefs[a]))
                 for a in argnames[len(v):] if a not in k]
    nameless = list(map(repr, v[argcount:]))
    keyword = list(map(ucf.format_arg_value, list(k.items())))
    args = positional + defaulted + nameless + keyword

    logControler = b.io.log.Control()
    logger = logControler.loggerGet()
    depth = ucf.stackFrameDepth(2)
    indentation = ucf.STR_indentMultiples(multiple=depth)

    logger.debug(format('Invoking(I-Call-%s): ' % (depth)) + b.ast.stackFrameInfoGet(2))
    logger.debug( "%s I-Enter-%s: %s(%s)" % (indentation, depth, fn.__name__, ", ".join(args)) )
    retVal = fn(*v, **k)
    logger.debug( "%s I-Return-%s(%s):  %s" % (indentation, depth, fn.__name__, retVal) )
    return retVal



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
