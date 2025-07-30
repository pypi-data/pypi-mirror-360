# -*- coding: utf-8 -*-

""" #+begin_org
* *[Summary]* :: A =PyLib= for manipulation of AST using inspect.
#+end_org """

""" #+begin_org
* [[elisp:(org-cycle)][| /Control Parameters Of This File/ |]] :: dblock controls and classifications
#+BEGIN_SRC emacs-lisp
(setq-local b:dblockControls t) ; (setq-local b:dblockControls nil)
(put 'b:dblockControls 'py3:cs:Classification "pyLibPure") ; Pure Python Library
#+END_SRC
#+RESULTS:
: pyLibPure
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
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['fv'], }
csInfo['version'] = '202208172107'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'fv-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* /[[elisp:(org-cycle)][| Description |]]/ :: [[file:/bisos/panels/bisos-model/fileVariables/fullUsagePanel-en.org][BPF File Variables (fv) Panel]]  ---
See panel for description.
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

####+BEGIN: b:py3:cs:framework/imports :basedOn "classification"
""" #+begin_org
** Imports Based On Classification=pyLibPure
#+end_org """
# No CS imports for pyLibPure
####+END:

import sys
import inspect
import ast
import importlib


####+BEGIN: bx:cs:py3:section :title "Stack Frame   :: Frame Marking and Tracking -- stackFrameInfoGet(frameNu)" :subTitle "Stack Frame"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Stack Frame   :: Frame Marking and Tracking -- stackFrameInfoGet(frameNu)*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  format_arg_value    [[elisp:(org-cycle)][| ]]
"""

def format_arg_value(arg_val):
    """ Return a string representing a (name, value) pair.

    >>> format_arg_value(('x', (1, 2, 3)))
    'x=(1, 2, 3)'
    """
    arg, val = arg_val
    return "%s=%r" % (arg, val)



####+BEGIN: bx:cs:py3:func :funcName "stackFrameFuncGet" :funcType "extTyped" :retType "extTyped" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /stackFrameFuncGet/  [[elisp:(org-cycle)][| ]]
#+end_org """
def stackFrameFuncGet(
####+END:
        frameNu,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Perhaps get rid of this and do info.function in the caller
    #+end_org """

    try: frameNu = int(frameNu)
    except: pass

    callerframerecord = inspect.stack()[frameNu]      # 0 represents this line (current frame)
    # 1 represents line at caller
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)
    return (info.function)


####+BEGIN: b:py3:cs:func/typing :funcName "stackFrameInfoGetValues" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /stackFrameInfoGetValues/   [[elisp:(org-cycle)][| ]]
#+end_org """
def stackFrameInfoGetValues(
####+END:
        frameNu: int,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Returns A String --
    #+end_org """

    try: frameNu = int(frameNu)
    except: pass

    callerframerecord = inspect.stack()[frameNu]      # 0 represents this line (current frame)
    # 1 represents line at caller
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)
    # print info.filename                       # __FILE__     -> Test.py
    # print info.function                       # __FUNCTION__ -> Main
    # print info.lineno                         # __LINE__     -> 13

    return (
        info.filename,
        info.lineno,
        info.function,
        )

####+BEGIN: bx:cs:py3:func :funcName "stackFrameInfoGet" :funcType "extTyped" :retType "extTyped" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /stackFrameInfoGet/  [[elisp:(org-cycle)][| ]]
#+end_org """
def stackFrameInfoGet(
####+END:
        frameNu,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Returns A String --
    #+end_org """

    try: frameNu = int(frameNu)
    except: pass

    callerframerecord = inspect.stack()[frameNu]      # 0 represents this line (current frame)
    # 1 represents line at caller
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)
    # print info.filename                       # __FILE__     -> Test.py
    # print info.function                       # __FUNCTION__ -> Main
    # print info.lineno                         # __LINE__     -> 13

    return info.filename + ':' + str(info.lineno) + ':' + info.function + ':'

####+BEGIN: bx:cs:py3:func :funcName "stackFrameDepth" :funcType "extTyped" :retType "extTyped" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /stackFrameDepth/  [[elisp:(org-cycle)][| ]]
#+end_org """
def stackFrameDepth(
####+END:
        frameNu,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Returns depth of specified frame as an integer.
    Additionally creates top to that frame list. -- But UnUsed.
    #+end_org """

    try: frameNu = int(frameNu)
    except: pass

    caller_list = []

    callerframerecord = inspect.stack()[frameNu]      # 0 represents this line (current frame)
    # 1 represents line at caller
    frame = callerframerecord[0]

    #this_frame = frame  # Save current frame.

    level = 0
    while frame.f_back:
        level = level + 1
        caller_list.append('{0}()'.format(frame.f_code.co_name))
        frame = frame.f_back

    #caller_line = this_frame.f_back.f_lineno
    #callers =  '/'.join(reversed(caller_list))
    #logging.info('Line {0} : {1}'.format(caller_line, callers))
    return level


####+BEGIN: bx:cs:py3:func :funcName "stackFrameDocString" :funcType "extTyped" :retType "extTyped" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /stackFrameDocString/  [[elisp:(org-cycle)][| ]]
#+end_org """
def stackFrameDocString(
####+END:
        frameNu,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Returns getdoc()
    #+end_org """

    try: frameNu = int(frameNu)
    except: pass

    callerframerecord = inspect.stack()[frameNu]      #
    # 1 represents line at caller
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)

    func = FUNC_strToFunc( info.function )

    #print "Called from module", info.f_globals['__name__']
    #print( getattr(info.filename, info.function) )
    #print( inspect.getdoc(getattr(info.function)) )
    return inspect.getdoc( func )

####+BEGIN: bx:cs:py3:func :funcName "stackFrameArgsGet" :funcType "extTyped" :retType "extTyped" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /stackFrameArgsGet/  [[elisp:(org-cycle)][| ]]
#+end_org """
def stackFrameArgsGet(
####+END:
        frameNu,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Returns getdoc()
    #+end_org """

    try: frameNu = int(frameNu)
    except: pass

    callerframerecord = inspect.stack()[frameNu]      #
    # 1 represents line at caller
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)

    fn = FUNC_strToFunc( info.function )

    # Unpack function's arg count, arg names, arg defaults
    code = fn.__code__
    argcount = code.co_argcount

    argnames = code.co_varnames[:argcount]
    fn_defaults = fn.__defaults__ or list()
    argdefs = dict(list(zip(argnames[-len(fn_defaults):], fn_defaults)))
    #TM_here( info.function + ' -- '+ str(argcount) + str(argnames) + str(fn_defaults) + str(argdefs) )

    return argdefs



####+BEGIN: bx:cs:py3:section :title "AST_ -- Abstract Syntax Tree Analysis" :subTitle "Abstract Syntax"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *AST_ -- Abstract Syntax Tree Analysis*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  ast_topLevelClasses    [[elisp:(org-cycle)][| ]]
"""
def ast_topLevelClasses(body):
    classesList=list()
    for eachClass in body:
        if isinstance(eachClass, ast.ClassDef):
            classesList.append(eachClass)
    return (classesList)
    # Generator model is not re-usable -- Avoided by choice
    #return (f for f in body if isinstance(f, ast.FunctionDef))

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  ast_topLevelFunctions    [[elisp:(org-cycle)][| ]]
"""
def ast_topLevelFunctions(body):
    funcsList=list()
    for func in body:
        if isinstance(func, ast.FunctionDef):
            funcsList.append(func)
    return (funcsList)
    # Generator model is not re-usable
    #return (f for f in body if isinstance(f, ast.FunctionDef))

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  ast_parseFile    [[elisp:(org-cycle)][| ]]
"""
def ast_parseFile(filename):
    with open(filename, "rt") as thisFile:
        return ast.parse(thisFile.read(), filename=filename)

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  ast_topLevelFunctionsInFile    [[elisp:(org-cycle)][| ]]
"""
def ast_topLevelFunctionsInFile(filename):
    tree = ast_parseFile(filename)
    return(
        ast_topLevelFunctions(tree.body)
    )

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  ast_topLevelClassesInFile    [[elisp:(org-cycle)][| ]]
"""
def ast_topLevelClassesInFile(filename):
    tree = ast_parseFile(filename)
    return(
        ast_topLevelClasses(tree.body)
    )

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  ast_topLevelClassNamesInFile    [[elisp:(org-cycle)][| ]]
"""
def ast_topLevelClassNamesInFile(filename):
    classes = ast_topLevelClassesInFile(filename)
    classNames = list()
    for each in classes:
        classNames.append(each.name)
    return classNames

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  ast_topLevelFunctionNamesInFile    [[elisp:(org-cycle)][| ]]
"""
def ast_topLevelFunctionNamesInFile(filename):
    """Not using generators by choice."""
    funcs = ast_topLevelFunctionsInFile(filename)
    funcNames = list()
    for each in funcs:
        funcNames.append(each.name)
    return funcNames


####+BEGIN: bx:cs:py3:section :title "Function Related Utilities" :subTitle "FUNC_"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Function Related Utilities*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  FUNC_strToFunc    [[elisp:(org-cycle)][| ]]
"""
def FUNC_strToFunc(astr):
    """Given a String, return the callable with that name.

    BUG: if astr is that of a module, just __import__ does not work.
    """
    module, _, function = astr.rpartition('.')
    if module:
        __import__(module)
        mod = sys.modules[module]
        return getattr(mod, function)
    else:
        #mod = sys.modules['__main__']  # or whatever's the "default module"
        #return globals()[function]
        mod = __import__('__main__')

        print(function)
        #return locals()[function]
        return getattr(mod, function)

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  FUNC_currentGet    [[elisp:(org-cycle)][| ]]
"""

def FUNC_currentGet(frameNu=1):
    """Returns the object for current frame.
This is used by a function when that function is running.
It returns a pointer to the running function.
Further details of the function can then be obtained by FUNC_currentXxx.

If it is directly called by the running function, then frameNu is x.
If it is called by an intermediate function such as io.eh.problem, then frameNu is x+1.

    BUG: does not work outside of the main module with PY2. Needs PY3 testing.
    """

    frame,filename,line_number,function_name,lines,index = inspect.stack()[frameNu]
    # print(frame,filename,line_number,function_name,lines,index)

    modName = "." + inspect.getmodulename(filename)

    try:
        mod = importlib.import_module(modName, package="bisos")
    except ModuleNotFoundError:
        mod=None
    if mod:
        func = getattr(mod, function_name, None)
        if func:
            return func

    try:
        mod = importlib.import_module(modName, package="unisos")
    except ModuleNotFoundError:
        mod=None
    if mod:
        func = getattr(mod, function_name, None)
        if func:
            return func


    print("UCF-Problem: Missing mod and func. " + modName)
    return None


def FUNC_current():
    """ When called as iicm.FUNC_current() frameNu=2"""
    return FUNC_currentGet(frameNu=2)

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  Func_currentNameGet    [[elisp:(org-cycle)][| ]]
"""

def Func_currentNameGet():
    """Returns the name of the object for current frame which would be this function's name.

    BUG: does not work outside of the main module.
    """

    thisFunc = FUNC_currentGet(frameNu=2)
    return thisFunc.__name__


def FUNC_currentNameGet():
    """Returns the name of the object for current frame which would be this function's name.

    BUG: does not work outside of the main module.
    """

    thisFunc = FUNC_currentGet(frameNu=2)
    return thisFunc.__name__

def FUNC_currentName():
    """Returns the name of the object for current frame which would be this function's name.

    BUG: does not work outside of the main module.
    """

    thisFunc = FUNC_currentGet(frameNu=2)
    return thisFunc.__name__


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  FUNC_argsLength    [[elisp:(org-cycle)][| ]]
"""

def FUNC_argsLength(fn, *v, **k):
    """Returns the length of arguments, given a function object.
** TODO ============    Returns length of string '()' not the actual args.
    """

    # PY2.7  #NOTYET IMPORTANT
    if not fn:
        return


    # Unpack function's arg count, arg names, arg defaults
    code = fn.__code__
    argcount = code.co_argcount

    argnames = code.co_varnames[:argcount]
    fn_defaults = fn.__defaults__ or list()
    argdefs = dict(list(zip(argnames[-len(fn_defaults):], fn_defaults)))

    positional = list(map(format_arg_value, list(zip(argnames, v))))
    defaulted = [format_arg_value((a, argdefs[a]))
       for a in argnames[len(v):] if a not in k]
    nameless = list(map(repr, v[argcount:]))
    keyword = list(map(format_arg_value, list(k.items())))
    args = positional + defaulted + nameless + keyword

    return   len(args[0])

####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* *[[elisp:(org-cycle)][| ~End-Of-Editable-Text~ |]]* :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
