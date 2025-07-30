# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =bpf-lib= for
#+end_org """

####+BEGIN: b:py3:cs:file/dblockControls :classification "bpf-lib"
""" #+begin_org
* [[elisp:(org-cycle)][| /Control Parameters Of This File/ |]] :: dblk ctrls classifications=bpf-lib
#+BEGIN_SRC emacs-lisp
(setq-local b:dblockControls t) ; (setq-local b:dblockControls nil)
(put 'b:dblockControls 'py3:cs:Classification "bpf-lib") ; one of cs-mu, cs-u, cs-lib, bpf-lib, pyLibPure
#+END_SRC
#+RESULTS:
: cs-mu
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
** This File: /bisos/git/auth/bxRepos/bisos-pip/b/py3/bisos/b/importFile.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:py3:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['importFile'], }
csInfo['version'] = '202502233111'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'importFile-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/COMEEGA/_nodeBase_/fullUsagePanel-en.org][BISOS COMEEGA Panel]]
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

####+BEGIN: b:py3:file/workbench :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Workbench |]] :: [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pyclbr %s" (bx:buf-fname))))][pyclbr]] || [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pydoc ./%s" (bx:buf-fname))))][pydoc]] || [[elisp:(python-check (format "/bisos/pipx/bin/pyflakes %s" (bx:buf-fname)))][pyflakes]] | [[elisp:(python-check (format "/bisos/pipx/bin/pychecker %s" (bx:buf-fname))))][pychecker (executes)]] | [[elisp:(python-check (format "/bisos/pipx/bin/pycodestyle %s" (bx:buf-fname))))][pycodestyle]] | [[elisp:(python-check (format "/bisos/pipx/bin/flake8 %s" (bx:buf-fname))))][flake8]] | [[elisp:(python-check (format "/bisos/pipx/bin/pylint %s" (bx:buf-fname))))][pylint]]  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

from bisos import b
# from bisos.b import cs

import importlib.util
import importlib.machinery

import sys
import types
import pathlib
import shutil
import os

####+BEGIN: b:py3:cs:func/typing :funcName "importFileAs" :comment "~Based on importlib~" :funcType "eType" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-eType  [[elisp:(outline-show-subtree+toggle)][||]] /importFileAs/  ~Based on importlib~  [[elisp:(org-cycle)][| ]]
#+end_org """
def importFileAs(
####+END:
        modAsName: str,
        importedFilePath: str | pathlib.Path | None,
        callingFile: str = None,  # Typically called as __file__
        callingName: str = None,
) -> types.ModuleType | None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr* |]] Import ~importedFilePath~ as ~modAsName~, return imported *module*.

Load ~importedFilePath~ and register ~modAsName~ in =sys.modules=.
~importedFilePath~ can be any file and does not have to be a .py file. ~modAsName~ should be python valid.

Raises ImportError: If the file cannot be imported or any Exception: occuring during loading.

Refs:
Similar to: https://stackoverflow.com/questions/19009932/import-arbitrary-python-source-file-python-3-3
    but allows for other than .py files as well through importlib.machinery.SourceFileLoader.

Usage:
 aasMarmeeManage = importFileAs('aasMarmeeManage', '/bisos/bpip/bin/aasMarmeeManage.cs')

    #+end_org """

    # print(f"{modAsName} {importedFilePath} {callingFile} {callingName}")

    if callingFile is not None:
        #callingName = os.path.basename(callingFile)
        if importedFilePath is None:
            # print("importedFilePath is None")
            sys.modules[modAsName] = sys.modules[callingName]
            return None

        callingFileAbsPath = pathlib.Path(callingFile).resolve()
        importedFilePath =  pathlib.Path(importedFilePath).resolve()

        #print(f"HHH {callingFileAbsPath} {importedFilePath}")

        if callingFileAbsPath == importedFilePath:
            # print("Self Importing Skipped")
            return None

    # importlib.util.spec_from_file_location() enforces .py limitation but importlib.util.spec_from_loader() does not,
    spec = importlib.util.spec_from_file_location(modAsName, importedFilePath)

    if spec is None:
        # try specifying a loader
        loader = importlib.machinery.SourceFileLoader(modAsName, str(importedFilePath))
        spec = importlib.util.spec_from_loader(modAsName, loader)
        if spec is None:
            raise ImportError(f"Could not load spec for module '{modAsName}' at: {importedFilePath}")
    module = importlib.util.module_from_spec(spec)

    sys.modules[modAsName] = module

    try:
        spec.loader.exec_module(module)
    except FileNotFoundError as e:
        raise ImportError(f"{e.strerror}: {importedFilePath}") from e

    return module

####+BEGIN: b:py3:cs:func/typing :funcName "execFileAsMain" :comment "~__main__ module~" :funcType "eType" :deco "b.utils.idempotentMake" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-eType  [[elisp:(outline-show-subtree+toggle)][||]] /execFileAsMain/  ~__main__ module~ deco=b.utils.idempotentMake  [[elisp:(org-cycle)][| ]]
#+end_org """
@b.utils.idempotentMake
def execFileAsMain(
####+END:
        importedFilePath: typing.Union[str,  pathlib.Path],
) -> types.ModuleType | None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr* |]] Idempotently import ~importedFilePath~ as __main__, but have __main__.__file__ be sys.argv[0],  return imported *module*.
Key aspects to note:
    - execFileAsMain may be called twice, first atexit of plantedCsu. second when plantedCsu is imported by ~importedFilePath~
    - __main__.__file__ = sys.argv[0] is needed when using @atexit
    - __main__.__file__ is not going to be importedFilePath because Commands and Params are in plantedCsu
    #+end_org """

    import __main__
    # sys.argv[0] instead of importedFilePath
    __main__.__file__ = sys.argv[0]  # Needed when using @atexit

    return (
        importFileAs('__main__', importedFilePath,)
    )


####+BEGIN: b:py3:cs:func/typing :funcName "execWithWhich" :comment "~With which~" :funcType "eType" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-eType  [[elisp:(outline-show-subtree+toggle)][||]] /execWithWhich/  ~With which~  [[elisp:(org-cycle)][| ]]
#+end_org """
def execWithWhich(
####+END:
        inExecName: str,
) -> types.ModuleType | None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr* |]] Use /which/ to get the executable's path. Then  [[execFileAsMain]].
    #+end_org """

    execPath = shutil.which(inExecName)
    if execPath is None:
        pathEnvVar = os.environ.get("PATH")
        raise ImportError(f"Found nothing for {inExecName} -- PATH={pathEnvVar}")

    execFilePath = pathlib.Path(execPath).resolve()

    return (
        execFileAsMain(execFilePath,)
    )

####+BEGIN: b:py3:cs:func/typing :funcName "plantWithWhich" :comment "~With which~" :funcType "eType" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-eType  [[elisp:(outline-show-subtree+toggle)][||]] /plantWithWhich/  ~With which~  [[elisp:(org-cycle)][| ]]
#+end_org """
def plantWithWhich(
####+END:
        inExecName: str,
) -> types.ModuleType | None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr* |]] Use /which/ to get the executable's path. Record it as /b.cs.G.seedOfThisPlant/ Then  [[execWithWhich]].
    #+end_org """

    execPath = shutil.which(inExecName)
    if execPath is None:
        pathEnvVar = os.environ.get("PATH")
        raise ImportError(f"Found nothing for {inExecName} -- PATH={pathEnvVar}")

    execFilePath = pathlib.Path(execPath).resolve()

    b.cs.G.seedOfThisPlant = execFilePath
    b.cs.G.plantOfThisSeed = sys.argv[0]

    return (
        execWithWhich(inExecName,)
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
