# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =BPF-Lib= bProviding logging capabilities based on Python's log library.
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
** This File: /bisos/git/auth/bxRepos/bisos-pip/b/py3/bisos/b/io/log.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:py3:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['log'], }
csInfo['version'] = '202209233423'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'log-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* ~[[elisp:(org-cycle)][| Description |]]~ :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/PyFwrk/bisos.crypt/_nodeBase_/fullUsagePanel-en.org][PyFwrk bisos.crypt Panel]]
Sets up LOG for log, eh, tm,
Functions and methods in this module are not to be decorated. The conflict with cs.track. Further, these are meant to be dependable.
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



import logging
import getpass
import sys

from bisos.transit import pattern

logger = logging.getLogger('root') # We are using 'root' for all of bpf

#handler = logging.StreamHandler()
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(0)
handler.setFormatter(
    #logging.Formatter("%(asctime)s - %(levelname)s -\t%(pathname)s[%(lineno)d]:%(funcName)s():\t%(msg)s")
    logging.Formatter("* %(msg)s \n%(asctime)s - %(levelname)s -\t%(pathname)s[%(lineno)d]:%(funcName)s():")
    )
#logger.addHandler(handler)

#logger.info('connecting')

####+BEGIN: bx:cs:py3:section :title "LOG: ICM Logging Control -- On top of Standard of Python Logging"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *LOG: ICM Logging Control -- On top of Standard of Python Logging*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


#LOGGER = 'Icm.Python.Logger'
LOGGER = 'Icm'
CONSL_LEVEL_RANGE = list(range(0, 51))
#FORMAT_STR = '%(asctime)s %(levelname)s %(message)s'
#FORMAT_STR = '%(levelname)s %(message)s -- %(asctime)s'
FORMAT_STR = "* %(msg)s \n%(asctime)s - %(levelname)s -\t%(pathname)s::[%(lineno)d] %(funcName)s():"
FORMAT_EXTRA_STR = "* %(msg)s \n%(asctime)s - %(levelname)s -\t%(extraPathname)s::[%(extraLineno)d] %(extraFuncName)s():"


####+BEGIN: b:py3:cs:func/typing :funcName "logFileName" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /logFileName/   [[elisp:(org-cycle)][| ]]
#+end_org """
def logFileName(
####+END:
):
    return (
        "/tmp/{userName}-ICM.log".format(
            userName=getpass.getuser()
        )
    )


####+BEGIN: b:py3:cs:func/typing :funcName "getConsoleLevel" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /getConsoleLevel/   [[elisp:(org-cycle)][| ]]
#+end_org """
def getConsoleLevel(
####+END:
        args,
):
    level = args.verbosityLevel
    if level is None: return
    try: level = int(level)
    except: pass
    if level not in CONSL_LEVEL_RANGE:
        args.verbosityLevel = None
        print('warning: console log level ', level, ' not in range 1..50.')
        return
    return level


####+BEGIN: b:py3:class/decl :className "_Control" :superClass "" :comment "" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /_Control/  superClass=object  [[elisp:(org-cycle)][| ]]
#+end_org """
class _Control(object):
####+END:
    """ #+begin_org
** [[elisp:(org-cycle)][| DocStr| ]]  ICM Logging on top of basic Logging.
Handle indentation in context filter.
    https://stackoverflow.com/questions/45010539/python-logging-pathname-in-decorator
 https://stackoverflow.com/questions/40619855/dynamically-adjust-logging-format
https://docs.python.org/3/howto/logging-cookbook.html#adding-contextual-information-to-your-logging-output
    https://docs.python.org/3/howto/logging.html#logging-basic-tutorial
    #+end_org """

    args = None
    logger = None
    fh = None
    ch = None
    level = None

    def __init__(self):
        pass

    def loggerSet(self, args) -> logging.Logger:
        """
        """

        #print( args )    #TEMP

        self.__class__.args = args

        #logger = logging.getLogger(LOGGER)
        logger = logging.getLogger('root')

        self.__class__.logger = logger

        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(FORMAT_STR)
        ## Add FileHandler
        fh = logging.FileHandler(logFileName())
        fh.name = 'File Logger'
        fh.level = logging.WARNING
        fh.formatter = formatter
        logger.addHandler(fh)

        self.__class__.fh = fh

        ## Add (optionally) ConsoleHandler
        level = getConsoleLevel(args)

        self.__class__.level = level

        #print( 'level= ' + str(level) )  # TEMP

        if level is not None:
            #print( stackFrameInfoGet(1) )  # TEMP
            ch = logging.StreamHandler()
            ch.name = 'Console Logger'
            ch.level = level
            ch.formatter = formatter
            logger.addHandler(ch)
            #print( stackFrameInfoGet(1) )  # TEMP
            self.__class__.ch = ch
        return logger

    def formatterBasic(self):
        formatter = logging.Formatter(FORMAT_STR)
        fh = self.__class__.fh
        #fh.formatter = formatter
        fh.setFormatter(formatter)
        ch = self.__class__.ch
        #ch.formatter = formatter
        if ch:
            ch.setFormatter(formatter)


    def formatterExtra(self):
        formatter = logging.Formatter(FORMAT_EXTRA_STR)
        fh = self.__class__.fh
        #fh.formatter = formatter
        if fh:
            fh.setFormatter(formatter)
        ch = self.__class__.ch
        #ch.formatter = formatter
        if ch:
            ch.setFormatter(formatter)


    def loggerSetLevel(self, level):
        """
        """

        #print( args )    #TEMP

        #self.__class__.args = args

        logger = logging.getLogger(LOGGER)

        self.__class__.logger = logger

        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(FORMAT_STR)
        ## Add FileHandler
        fh = logging.FileHandler(logFileName())
        fh.name = 'File Logger'
        fh.level = logging.WARNING
        fh.formatter = formatter
        logger.addHandler(fh)

        self.__class__.fh = fh

        ## Add (optionally) ConsoleHandler
        #level = getConsoleLevel(args)

        self.__class__.level = level

        #print( 'level= ' + str(level) )  # TEMP

        if level is not None:
            #print( stackFrameInfoGet(1) )  # TEMP
            ch = logging.StreamHandler()
            ch.name = 'Console Logger'
            ch.level = level
            ch.formatter = formatter
            logger.addHandler(ch)
            #print( stackFrameInfoGet(1) )  # TEMP
        return logger

    def loggerGetLevel(self, ):
        """
        """
        return(self.__class__.level)


    def loggerReset(self):
        logger = self.__class__.logger
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(FORMAT_STR)
        fh = self.__class__.fh
        fh.formatter = formatter

    def loggerGet(self) -> logging.Logger:
        return self.__class__.logger


controller = pattern.singleton(_Control)

####+BEGIN: bx:cs:py3:section :title "LOG_: Significant Event Which Is Not An Error"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *LOG_: Significant Event Which Is Not An Error*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "note" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /note/   [[elisp:(org-cycle)][| ]]
#+end_org """
def note(
####+END:
        *v,
        **k,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """


    logControler = b_io.log.Control()
    logger = logControler.loggerGet()

    # fn = b.ast.FUNC_currentGet()
    # argsLength =  b.ast.FUNC_argsLength(fn, v, k)

    # if argsLength == 2:   # empty '()'
        # outString = ''
    # else:
        # outString = format(*v, **k)

    outString = format(*v, **k)

    logger.info( 'LOG_: ' + outString )

####+BEGIN: b:py3:cs:func/typing :funcName "here" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /here/   [[elisp:(org-cycle)][| ]]
#+end_org """
def here(
####+END:
        *v,
        **k,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Mark file and line -- do the equivalent of a print statement.
    #+end_org """
    logControler = b_io.log.controller
    logger = logControler.loggerGet()

    # fn = b.ast.FUNC_currentGet()
    # argsLength =  b.ast.FUNC_argsLength(fn, v, k)

    # if argsLength == 2:   # empty '()'
    #     outString = ''
    # else:
    #     outString = format(*v, **k)

    outString = format(*v, **k)

    logger.info('LOG_: ' + outString + ' -- ') #  + b.ast.stackFrameInfoGet(2) )


####+BEGIN: bx:cs:py3:section :title "Raw  Logging At Level"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Raw  Logging At Level*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "debug" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /debug/   [[elisp:(org-cycle)][| ]]
#+end_org """
def debug(
####+END:
        *v,
        **k,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    logControler = b_io.log.Control()
    logger = logControler.loggerGet()
    return (
        logger.debug(format(*v, **k))
    )

####+BEGIN: b:py3:cs:func/typing :funcName "info" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /info/   [[elisp:(org-cycle)][| ]]
#+end_org """
def info(
####+END:
        *v,
        **k,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    logControler = b_io.log.Control()
    logger = logControler.loggerGet()
    return (
        logger.info(format(*v, **k))
    )

####+BEGIN: b:py3:cs:func/typing :funcName "warning" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /warning/   [[elisp:(org-cycle)][| ]]
#+end_org """
def warning(
####+END:
        *v,
        **k,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    logControler = b_io.log.Control()
    logger = logControler.loggerGet()
    return (
        logger.info(format(*v, **k))
    )

####+BEGIN: b:py3:cs:func/typing :funcName "error" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /error/   [[elisp:(org-cycle)][| ]]
#+end_org """
def error(
####+END:
        *v,
        **k,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    logControler = b_io.log.Control()
    logger = logControler.loggerGet()
    return (
        logger.error(format(*v, **k))
    )

####+BEGIN: b:py3:cs:func/typing :funcName "critical" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /critical/   [[elisp:(org-cycle)][| ]]
#+end_org """
def critical(
####+END:
        *v,
        **k,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    logControler = b_io.log.Control()
    logger = logControler.loggerGet()
    return (
        logger.critical(format(*v, **k))
    )


####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
