# -*- coding: utf-8 -*-

""" #+begin_org
* *[Summary]* :: A =PyLib= formanipulation of File Tree Objects (FTO). (bisos.b.fto).
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
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['fto'], }
csInfo['version'] = '202209071611'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'fto-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* /[[elisp:(org-cycle)][| Description |]]/ :: [[file:/bisos/panels/bisos-model/fileTreeObject-FTO/fullUsagePanel-en.org][BPF File Tree Objcets (fto.) Panel]]
/FILE_TreeObject/    :: *FILE_TreeObject: A Tree of Nodes and Leaves on Top Of file system*
Facilitates building Tree hierarchies on the file system.
Super Class for FILE_Param and CmndParam

See panel for overview and details.

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


from bisos import b
from bisos.b import b_io
from bisos.b import cs

import os
import enum


####+BEGIN: bx:dblock:python:class :className "FileTreeItem" :superClass "enum.Enum" :comment "" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /FileTreeItem/ enum.Enum  [[elisp:(org-cycle)][| ]]
#+end_org """
class FileTreeItem(enum.Enum):
####+END:
    Branch = 'Branch'
    Leaf = 'Leaf'
    Ignore = 'Ignore'
    IgnoreBranch = 'ignoreBranch'
    IgnoreLeaf = 'ignoreLeaf'

####+BEGIN: bx:dblock:python:class :className "FILE_TreeObject" :superClass "" :comment "" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /FILE_TreeObject/ object  [[elisp:(org-cycle)][| ]]
#+end_org """
class FILE_TreeObject(object):
####+END:
    """Representation of a FILE_TreeObject in a file system directory (either a leaf or a node).

    This class is paralleled by /opt/public/osmt/bin/lcnObjectTree.libSh
    And is expected to be compatible with lcnObjectTree.libSh.

    A FILE_TreeObject is either a
       - FILE_TreeNode  # MB-2022, FILE_TreeBranch
       - FILE_TreeLeaf

    # MB-2022 An FTO_Node is either of FTO_Branch of FTO_Leaf

    A FILE_TreeObject consists of:
       1) FileSysDir
       2) _tree_
       3) _treeProc_
       4) _objectType_

    _tree_  in bash  typeset -A treeItemEnum=(
    [node]=node                   # this dir is a branch (node)
    [leaf]=leaf                   # this dir is a leaf
    [ignore]=ignore               # ignore this and everything below it
    [ignoreLeaf]=ignoreLeaf       # ignore this leaf
    [ignoreNode]=ignoreNode       # ignore this node but continue traversing
)

    _objectTypes_  Known objectTypes are FILE_Param


    """

    def __init__(self,
                 fileSysPath,
                 ):
        '''Constructor'''

        self.__fileSysPath = fileSysPath

    # MB-2021: parValueGet() is not defined below.
    #
    # def __str__(self):
    #     return  (
    #         """value: {value}\nread: {read}""".format(
    #             value=self.parValueGet(),
    #             read=self.attrReadGet(),
    #         )
    #     )
    #     # return  format(
    #     #     'value: ' + str(self.parValueGet()) +
    #     #     'read: ' + str(self.attrReadGet())
    #     #     )

    def fileTreeBaseSet(self, fileSysPath):
        self.__fileSysPath = fileSysPath

    def fileTreeBaseGet(self):
        return self.__fileSysPath


    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def nodeCreate(self, objectTypes=None, treeProc=None, ignore=None):
        """At the fileSysPath of the FILE_TreeObject, create a node.
        """
        absFileSysPath = os.path.abspath(self.__fileSysPath)

        if not os.path.isdir(absFileSysPath):
            try: os.makedirs( absFileSysPath, 0o777 )
            except OSError: pass

        thisFilePath= format(f"{absFileSysPath}/_tree_")
        with open(thisFilePath, "w") as thisFile:
             thisFile.write('node' +'\n')

    def leafCreate(self, objectTypes=None, treeProc=None, ignore=None):
        """At the fileSysPath of the FILE_TreeObject, create a leaf.
        """
        absFileSysPath = os.path.abspath(self.__fileSysPath)

        if not os.path.isdir(absFileSysPath):
            try: os.makedirs( absFileSysPath, 0o777 )
            except OSError: pass

        thisFilePath= format(f"{absFileSysPath}/_tree_")
        with open(thisFilePath, "w") as thisFile:
             thisFile.write('leaf' +'\n')

    def validityPredicate(self, objectTypes=None, treeProc=None, ignore=None):
        """At the fileSysPath of the FILE_TreeObject, create a verify that _tree_ is in place.
        """
        absFileSysPath = os.path.abspath(self.__fileSysPath)

        if not os.path.isdir(absFileSysPath):
            return 'NonExistent'

        filePathOf_tree_= format(f"{absFileSysPath}/_tree_")
        if not os.path.isfile(filePathOf_tree_):
            return 'NonExistent'

        lineString = open(filePathOf_tree_, 'r').read().strip()    # Making sure we get rid of \n on read()

        if lineString == 'node':
            return 'InPlace'
        else:
            io.eh.critical_usageError(f"lineString= {lineString}")
            return 'BadlyFormed'

    def nodePredicate(self, objectTypes=None, treeProc=None, ignore=None):
        """At the fileSysPath of the FILE_TreeObject, create a leaf.
        """
        print((self.__fileSysPath))

    def leafPredicate(self, objectTypes=None, treeProc=None, ignore=None):
        """At the fileSysPath of the FILE_TreeObject, create a leaf.
        """
        print((self.__fileSysPath))

    def nodeUpdate(self, objectTypes=None, treeProc=None, ignore=None):
        """At the fileSysPath of the FILE_TreeObject, create a leaf.
        """
        print((self.__fileSysPath))


    def leafUpdate(self, objectTypes=None, treeProc=None, ignore=None):
        """At the fileSysPath of the FILE_TreeObject, create a leaf.
        """

    def nodesEffectiveList(self):
        """At the fileSysPath of the FILE_TreeObject, create a leaf.
        """

    def leavesEffectiveList(self):
        """At the fileSysPath of the FILE_TreeObject, create a leaf.
        """

    def nodesList(self):
        """At the fileSysPath of the FILE_TreeObject, create a leaf.
        """

    def leavesList(self):
        """At the fileSysPath of the FILE_TreeObject, create a leaf.
        """

    def treeObjectInfo(self):
        """At the fileSysPath of the FILE_TreeObject, create a leaf.
        """

    def treeRecurse(self, command):
        """At the fileSysPath of the FILE_TreeObject, create a leaf.
        """



####+BEGIN: b:prog:file/endOfFile :extraParams nil
""" #+begin_org
* *[[elisp:(org-cycle)][| END-OF-FILE |]]* :: emacs and org variables and control parameters
#+end_org """
### local variables:
### no-byte-compile: t
### end:
####+END:
