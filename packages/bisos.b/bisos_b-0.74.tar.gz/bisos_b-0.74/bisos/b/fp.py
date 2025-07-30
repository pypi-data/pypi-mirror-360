# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =PyLib+CsLib= for manipulation of File Parameters (FP). ~bisos.b.fp~
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
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['fp'], }
csInfo['version'] = '202209125155'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'fp-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* /[[elisp:(org-cycle)][| Description |]]/ :: [[file:/bisos/panels/bisos-model/fileParameters/fullUsagePanel-en.org][File Parameters --- BISOS.B.FP Panel]]
See panel for details.
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

import typing

from bisos import b
from bisos.b import cs
from bisos.b import b_io

from bisos.transit import pattern

import os
import collections

import __main__

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Classes, Functions and Operations" :anchor ""  :extraInfo "FP Base Facilities"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Classes, Functions and Operations_: |]]  FP Base Facilities  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:class/decl :className "FileParam" :superClass "" :comment "" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /FileParam/  superClass=object   [[elisp:(org-cycle)][| ]]
#+end_org """
class FileParam(object):
####+END:
    """ #+begin_org
** [[elisp:(org-cycle)][| DocStr| ]]  Representation of One FILE Parameter.

    A FileParam consists of 3 parts
       1) ParameterName
       2) ParameterValue
       3) ParameterAttributes

    On the file system:
      1- name of directory is ParameterName
      2- content of ParameterName/value is ParameterValue
      3- rest of the files in ParameterName/ are ParameterAttributes.

    The concept of a FileParam is based on FileVariables which  dates back to [[http://www.qmailwiki.org/Qmail-control-files][Qmail Control Files]] (at least).
    A FileParam is broader than that concept in two respects.
     1) A FileParam is represented as a directory on the file system. This FileParam
        permits the parameter to have attributes beyond just a value. Other attributes
        are themselves in the form of a traditional filename/value.
     2) The scope of usage of a FileParam is any parameter not just a control parameter.


    We are deliberately not using a python dictionary to represent a FileParam
    instead it is a full fledged python-object.
    #+end_org """

    def __init__(self,
                 parName=None,
                 parValue=None,
                 storeBase=None,
                 # storeRoot=None,
                 # storeRel=None,
                 attrRead=None,
                 ):
        '''Constructor'''
        self.__parName = parName
        self.__parValue = parValue
        self.__storeBase = storeBase   # storeBase = storeRoot + storeRel
        # self.__storeRoot = storeRoot
        # self.__storeRel = storeRel
        self.__attrRead = attrRead


    def __str__(self):
        return  format(
            str(self.parNameGet()) + ": " + str(self.parValueGet())
            )

    def parBaseGet(self):
        """  """
        return self.__storeBase

    def parNameGet(self):
        """  """
        return self.__parName

    def parValueGet(self):
        """        """
        return self.__parValue

    def parValueGetLines(self):
        """        """
        if self.__parValue == None:
            return None
        return self.__parValue.splitlines()

    def parValueSet(self, value):
        """        """
        self.__parValue = value

    def attrReadGet(self):
        """        """
        return self.__attrRead

    def attrReadSet(self, attrRead):
        """        """
        self.__attrRead = attrRead

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def readFrom(self, storeBase=None, parName=None):
        """Read into a FILE_param content of parBase/parName.

        Returns a FILE_param which was contailed in parBase/parName.
        """
        if self.__storeBase == None and storeBase == None:
            return b_io.eh.problem_usageError("storeBase")

        if self.__parName == None and parName == None:
            return b_io.eh.problem_usageError("parName")

        if storeBase:
            self.__storeBase = storeBase

        if parName:
            self.__parName = parName

        self.__parName = parName

        parNameFullPath = os.path.join(self.__storeBase, parName)

        #print(parNameFullPath)

        return self.readFromPath(parNameFullPath)

    # Undecorated because called before initialization
    #@io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def readFromPath(self, parNameFullPath):
        """Read into a FILE_param content of parBase/parName.

        Returns a FILE_param which was contailed in parBase/parName.
        """

        if not os.path.isdir(parNameFullPath):
            #return b_io.eh.problem_usageError("parName: " + parNameFullPath)
            return None

        fileParam = self

        fileParam.__parName = os.path.basename(parNameFullPath)

        #
        # Now we will fill fileParam based on the directory content
        #
        #if os.path.exists(parNameFullPath):
            #return b_io.eh.problem_usageError(f"Missing Path: {parNameFullPath}")

        for item in os.listdir(parNameFullPath):
            if item == "CVS":
                continue
            fileFullPath = os.path.join(parNameFullPath, item)
            if os.path.isfile(fileFullPath):
                if item == 'value':
                    lineString = open(fileFullPath, 'r').read().strip()    # Making sure we get rid of \n on read()
                    self.parValueSet(lineString)
                    continue

                if item == 'value.gpg':
                    lineString = open(fileFullPath, 'r').read().strip()    # Making sure we get rid of \n on read()
                    self.parValueSet(lineString)
                    continue

                # Rest of the files are expected to be attributes

                #lineString = open(fileFullPath, 'r').read()
                # NOTYET, check for exceptions
                #eval('self.attr' + str(item).title() + 'Set(lineString)')
            #else:
                #io.eh.problem_usageError("Unexpected Non-File: " + fileFullPath)

        return fileParam


    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def writeAsEncrypted(self, storeBase=None, parName=None, parValue=None):
        """Write this FileParam to storeBase.

        """
        if self.__storeBase == None and storeBase == None:
            return b_io.eh.problem_usageError("storeBase")

        if self.__parName == None and parName == None:
            return b_io.eh.problem_usageError("parName")

        if self.__parValue == None and parValue == None:
            return b_io.eh.problem_usageError("parValue")

        if storeBase:
            self.__storeBase = storeBase

        if parName:
            self.__parName = parName
        else:
            parName = self.__parName

        if parValue:
            self.__parValue = parValue
        else:
            parValue = self.__parValue

        parNameFullPath = os.path.join(self.__storeBase, parName)
        try: os.makedirs( parNameFullPath, 0o777 )
        except OSError: pass

        fileTreeObject = b.fto.FILE_TreeObject(parNameFullPath)

        fileTreeObject.leafCreate()

        parValueFullPath = os.path.join(parNameFullPath, 'value.gpg')
        with open(parValueFullPath, 'wb') as valueFile:
             valueFile.write(parValue)
             # NOTYET, this should be a pr
             # b_io.pr("FileParam.writeTo path={path} value={value}".
             #          format(path=parValueFullPath, value=parValue))
             b_io.stderr("FileParam.writeTo path={path} value={value}".
                      format(path=parValueFullPath, value=parValue))

        return parNameFullPath



    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def writeTo(self, storeBase=None, parName=None, parValue=None):
        """Write this FileParam to storeBase.

        """
        if self.__storeBase == None and storeBase == None:
            return b_io.eh.problem_usageError("storeBase")

        if self.__parName == None and parName == None:
            return b_io.eh.problem_usageError("parName")

        if self.__parValue == None and parValue == None:
            return b_io.eh.problem_usageError("parValue")

        if storeBase:
            self.__storeBase = storeBase

        if parName:
            self.__parName = parName
        else:
            parName = self.__parName

        if parValue:
            self.__parValue = parValue
        else:
            parValue = self.__parValue

        parNameFullPath = os.path.join(self.__storeBase, parName)
        try: os.makedirs( parNameFullPath, 0o777 )
        except OSError: pass

        fileTreeObject = b.fto.FILE_TreeObject(parNameFullPath)

        fileTreeObject.leafCreate()

        parValueFullPath = os.path.join(parNameFullPath, 'value')
        with open(parValueFullPath, "w") as valueFile:
             valueFile.write(str(parValue) +'\n')
             # NOTYET, this should be a pr
             #b_io.pr("FileParam.writeTo path={path} value={value}".
             #         format(path=parValueFullPath, value=parValue))
             b_io.stderr("FileParam.writeTo path={path} value={value}".
                      format(path=parValueFullPath, value=parValue))

        return parNameFullPath


    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def writeToPath(self, parNameFullPath=None, parValue=None):
        """Write this FileParam to storeBase.
        """

        return self.writeTo(storeBase=os.path.dirname(parNameFullPath),
                            parName=os.path.basename(parNameFullPath),
                            parValue=parValue)


    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def writeToFromFile(self, storeBase=None, parName=None, parValueFile=None):
        """Write this FileParam to storeBase.

        """
        if self.__storeBase == None and storeBase == None:
            return b_io.eh.problem_usageError("storeBase")

        if self.__parName == None and parName == None:
            return b_io.eh.problem_usageError("parName")

        if parValueFile == None:
             return b_io.eh.problem_usageError("parValueFile")

        if storeBase:
            self.__storeBase = storeBase

        if parName:
            self.__parName = parName
        else:
            parName = self.__parName

        # if parValue:
        #     self.__parValue = parValue
        # else:
        #     parValue = self.__parValue

        parNameFullPath = os.path.join(self.__storeBase, parName)
        try: os.makedirs( parNameFullPath, 0o777 )
        except OSError: pass

        fileTreeObject = b.fto.FILE_TreeObject(parNameFullPath)

        fileTreeObject.leafCreate()

        parValueFullPath = os.path.join(parNameFullPath, 'value')
        with open(parValueFullPath, "w") as valueFile:
            with open(parValueFile, "r") as inFile:
                for line in inFile:
                    valueFile.write(line)

        return parNameFullPath


    def reCreationString(self):
        """Provide the string needed to recreate this object.

        """
        return


####+BEGIN: b:py3:class/decl :className "FileParamDict" :superClass "" :comment "" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /FileParamDict/  superClass=object   [[elisp:(org-cycle)][| ]]
#+end_org """
class FileParamDict(object):
####+END:
    """ #+begin_org
** [[elisp:(org-cycle)][| DocStr| ]] Maintain a list of FileParams.
    NOTYET, nesting of dictionaries.
    #+end_org """

    def __init__(self):
        self.__fileParamDict = dict()

    def parDictAdd(self, fileParam=None):
        """        """
        self.__fileParamDict.update({fileParam.parNameGet():fileParam})

    def parDictGet(self):
        """        """
        return self.__fileParamDict

    def parNameFind(self, parName=None):
        """        """
        return self.__fileParamDict[parName]

    def readFrom(self, path=None):
        """Read each file's content into a FLAT dictionary item with the filename as key.

        Returns a Dictionary of paramName:FileParam.
        """

        absolutePath = os.path.abspath(path)

        if not os.path.isdir(absolutePath):
            return None

        for item in os.listdir(absolutePath):
            fileFullPath = os.path.join(absolutePath, item)
            if os.path.isdir(fileFullPath):

                blank = FileParam()

                itemParam = blank.readFrom(storeBase=absolutePath, parName=item)

                self.parDictAdd(itemParam)

        return self.__fileParamDict

####+BEGIN: bx:cs:py3:section :title "*Individual Write Params Functional Interface*"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] **Individual Write Params Functional Interface**  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "FileParamWriteTo" :funcType "extTyped" :retType "extTyped" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /FileParamWriteTo/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def FileParamWriteTo(
####+END:d
        parRoot=None,
        parName=None,
        parValue=None,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    thisFileParam = FileParam(parName=parName, parValue=parValue,)

    if thisFileParam == None:
        return b_io.eh.critical_usageError('')

    return thisFileParam.writeTo(storeBase=parRoot)


####+BEGIN: b:py3:cs:func/typing :funcName "FileParamWriteToPath" :funcType "extTyped" :retType "extTyped" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /FileParamWriteToPath/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def FileParamWriteToPath(
####+END:
        parNameFullPath=None,
        parValue=None,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    thisFileParam = FileParam()

    if thisFileParam == None:
        return b_io.eh.critical_usageError('')

    return thisFileParam.writeToPath(parNameFullPath=parNameFullPath,
                                     parValue=parValue)


####+BEGIN: b:py3:cs:func/typing :funcName "FileParamWriteToFromFile" :funcType "extTyped" :retType "extTyped" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /FileParamWriteToFromFile/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def FileParamWriteToFromFile(
####+END:
        parRoot=None,
        parName=None,
        parValueFile=None,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    thisFileParam = FileParam(parName=parName)

    if thisFileParam == None:
        return b_io.eh.critical_usageError('')

    return thisFileParam.writeToFromFile(storeBase=parRoot, parValueFile=parValueFile)


####+BEGIN: b:py3:cs:func/typing :funcName "FileParamVerWriteTo" :funcType "extTyped" :retType "extTyped" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /FileParamVerWriteTo/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def FileParamVerWriteTo(
####+END:
        parRoot=None,
        parName=None,
        parVerTag=None,
        parValue=None,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Given ticmoBase, Create parName, then assign parValue to parVerTag
    #+end_org """

    parFullPath = os.path.join(parRoot, parName)
    try: os.makedirs( parFullPath, 0o777 )
    except OSError: pass

    thisFileParam = FileParam(parName=parVerTag,
                                    parValue=parValue,
                                    )

    if thisFileParam == None:
        return b_io.eh.critical_usageError('')

    return thisFileParam.writeTo(storeBase=parFullPath)


####+BEGIN: bx:cs:py3:section :title "*Individual Read Params Functional Interface*"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] **Individual Read Params Functional Interface**  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: b:py3:cs:func/typing :funcName "FileParamReadFrom" :funcType "extTyped" :retType "extTyped" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /FileParamReadFrom/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def FileParamReadFrom(
####+END:
        parRoot=None,
        parName=None,
        parVerTag=None,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    blank = FileParam()

    if blank == None:
        return b_io.eh.critical_usageError('blank')

    filePar = blank.readFrom(storeBase=parRoot, parName=parName)

    if filePar == None:
        print('in b.fp.FileParamReadFrom Missing: ' + str(parRoot) + parName)
        raise IOError
        #return b_io.eh.critical_usageError('blank')
        return None

    return filePar


####+BEGIN: b:py3:cs:func/typing :funcName "FileParamValueReadFrom" :funcType "extTyped" :retType "extTyped" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /FileParamValueReadFrom/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def FileParamValueReadFrom(
####+END:
        parRoot=None,
        parName=None,
        parVerTag=None,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    blank = FileParam()

    if blank == None:
        return b_io.eh.critical_usageError('blank')

    filePar = blank.readFrom(storeBase=parRoot, parName=parName)

    if filePar == None:
        fileFullPath = os.path.join(parRoot, parName)
        b_io.tm.note(f"In FileParamValueReadFrom Missing: {fileFullPath}")
        #raise IOError
        #return b_io.eh.critical_usageError('blank')
        return None

    return(filePar.parValueGet())


####+BEGIN: b:py3:cs:func/typing :funcName "FileParamReadFromPath" :funcType "extTyped" :retType "extTyped" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /FileParamReadFromPath/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def FileParamReadFromPath(
####+END:
        parRoot=None,
        parVerTag=None,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    blank = FileParam()

    if blank == None:
        return b_io.eh.critical_usageError('blank')

    filePar = blank.readFromPath(parRoot)

    if filePar == None:
        #print('Missing: ' + parRoot + parName)
        raise IOError
        #return b_io.eh.critical_usageError('blank')

    return filePar


####+BEGIN: b:py3:cs:func/typing :funcName "FileParamValueReadFromPath" :funcType "extTyped" :retType "extTyped" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /FileParamValueReadFromPath/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def FileParamValueReadFromPath(
####+END:
        parRoot=None,
        parVerTag=None,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    blank = FileParam()

    if blank == None:
        return b_io.eh.critical_usageError('blank')

    filePar = blank.readFromPath(parRoot)

    if filePar == None:
        print(('Missing: ' + parRoot))
        return b_io.eh.critical_usageError('blank')

    return(filePar.parValueGet())


####+BEGIN: b:py3:cs:func/typing :funcName "FileParamVerReadFrom" :funcType "extTyped" :retType "extTyped" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /FileParamVerReadFrom/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def FileParamVerReadFrom(
####+END:
        parRoot=None,
        parName=None,
        parVerTag=None,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    blank = FileParam()

    if blank == None:
        try:  b_io.eh.critical_usageError('blank')
        except RuntimeError:  return

    parFullPath = os.path.join(parRoot, parName)
    try: os.makedirs( parFullPath, 0o777 )
    except OSError: pass


    filePar = blank.readFrom(storeBase=parFullPath, parName=parVerTag)

    if filePar == None:
        #print('Missing: ' + parRoot + parName)
        return b_io.eh.critical_usageError('blank')

    #print(filePar.parValueGet())
    return filePar


####+BEGIN: bx:cs:py3:section :title "FILE_paramDict Functional Interface"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *FILE_paramDict Functional Interface*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: b:py3:cs:func/typing :funcName "readTreeAtBaseDir_wOp" :funcType "wOp" :retType "OpOutcome" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-wOp    [[elisp:(outline-show-subtree+toggle)][||]] /readTreeAtBaseDir_wOp/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def readTreeAtBaseDir_wOp(
####+END:
        fpsDir: typing.AnyStr,
        outcome: typing.Optional[b.op.Outcome] = None,
) -> b.op.Outcome:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] A Wrapped Operation with results
    #+end_org """

    if not outcome:
        outcome = b.op.Outcome()

    blankParDictObj  = FileParamDict()
    thisParamDict = blankParDictObj.readFrom(path=fpsDir)
    b_io.tm.here(f"path={fpsDir}")

    if thisParamDict == None:
        return b_io.eh.problem_usageError_wOp(
            outcome,
            "thisParamDict == None",
        )

    return outcome.set(
        opError=b.OpError.Success,
        opResults=thisParamDict,
    )


####+BEGIN: b:py3:cs:func/typing :funcName "parsGetAsDictValue_wOp" :funcType "wOp" :retType "OpOutcome" :deco "default" :argsList "typed"
""" #+begin_org
* _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-wOp    [[elisp:(outline-show-subtree+toggle)][||]] /parsGetAsDictValue_wOp/  deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def parsGetAsDictValue_wOp(
####+END:
        parNamesList: typing.Optional[list],
        fpsDir: typing.AnyStr,
        outcome: typing.Optional[b.op.Outcome] = None,
) -> b.op.Outcome:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] A Wrapped Operation with results being a dictionary of values.
    if not ~parNamesList~, get all the values.
    #+end_org """

    outcome = readTreeAtBaseDir_wOp(fpsDir, outcome=outcome)

    results = outcome.results

    opResults = dict()
    #opErrors = ""

    if parNamesList:
        for each in parNamesList:
            # NOTYET, If no results[each], we need to record it in opErrors
            if each in results.keys():
                opResults[each] = results[each].parValueGet()
            else:
                opResults[each] = "_UnFound_"

            print(f"{each} {eachFpValue}")
    else:
        for eachFpName in results:
            opResults[eachFpName] = results[eachFpName].parValueGet()
            # print(f"{eachFpName} {eachFpValue}")

    return outcome.set(
        opError=b.OpError.Success,
        opResults=opResults,
    )


####+BEGIN: b:py3:cs:func/typing :funcName "parsGetAsDictValue" :funcType "wOp" :retType "OpOutcome" :deco "default" :argsList "typed"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-wOp    [[elisp:(outline-show-subtree+toggle)][||]] /parsGetAsDictValue/  deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def parsGetAsDictValue(
####+END:
        parNamesList: typing.Optional[list],
        fpsDir: typing.AnyStr,
) -> typing.Dict[str, typing.Any]:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] A Wrapped Operation with results being a dictionary of values.
    if not ~parNamesList~, get all the values.
*** TODO --- NOTYET This needs to be moved to
    #+end_org """

    blankParDictObj  = FileParamDict()
    thisParamDict = blankParDictObj.readFrom(path=fpsDir)
    b_io.tm.here(f"path={fpsDir}")

    results = thisParamDict

    opResults = dict()
    #opErrors = ""

    if parNamesList:
        for each in parNamesList:
            # NOTYET, If no results[each], we need to record it in opErrors
            if each in results.keys():
                opResults[each] = results[each].parValueGet()
            else:
                opResults[each] = "UnFound"
            #print(f"{each} {eachFpValue}")
    else:
        for eachFpName in results:
            opResults[eachFpName] = results[eachFpName].parValueGet()
            #print(f"{eachFpName} {eachFpValue}")

    return opResults


####+BEGIN: bx:cs:py3:section :title "OLD ICM Junk Yard -- FILE_paramDict Functional Interface"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *OLD ICM Junk Yard -- FILE_paramDict Functional Interface*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "FILE_paramDictRead_ICM_OBSOLETED" :comment "OLD Style CMND" :funcType "extTyped" :retType "extTyped" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /FILE_paramDictRead_ICM_OBSOLETED/  OLD Style CMND deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def FILE_paramDictRead_ICM_OBSOLETED(
####+END:
        interactive=None, # NOTYET, icm.Interactivity.Both,
        inPathList=None
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Old Style CMND
    #+end_org """

    try: icm.callableEntryEnhancer(type='cmnd')
    except StopIteration:  return(icm.ReturnCode.ExtractionSuccess)

    G = cs.globalContext.get()
    G.curFuncNameSet(b.ast.FUNC_currentGet().__name__)

    if icm.Interactivity().interactiveInvokation(interactive):
        icmRunArgs = G.icmRunArgsGet()
        #if cmndArgsLengthValidate(cmndArgs=icmRunArgs.cmndArgs, expected=0, comparison=int__gt):
            #return(ReturnCode.UsageError)

        inPathList = []
        for thisPath in icm.icmRunArgs.cmndArgs:
            inPathList.append(thisPath)
    else:
        if inPathList == None:
            return b_io.eh.critical_usageError('inPathList is None and is Non-Interactive')

    for thisPath in inPathList:
        blankDict = FileParamDict()
        thisParamDict = blankDict.readFrom(path=thisPath)
        icm.TM_here('path=' + thisPath)

        if thisParamDict == None:
            continue

        for parName, filePar  in thisParamDict.items():
            print(('parName=' + parName))
            if filePar == None:
                continue
            thisValue=filePar.parValueGetLines()
            if thisValue == None:
                icm.TM_here("Skipping: " + filePar.parNameGet())
                continue
            print((
                filePar.parNameGet() +
                '=' +
                thisValue[0]))
    return



####+BEGIN: b:py3:cs:func/typing :funcName "FILE_paramDictReadObsolete" :comment "OLD Style CMND" :funcType "extTyped" :retType "extTyped" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /FILE_paramDictReadObsolete/  OLD Style CMND deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def FILE_paramDictReadObsolete(
####+END:
        interactive=None, # NOTYET, icm.Interactivity.Both,
        inPathList=None
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Old Style CMND
    #+end_org """

    G = cs.globalContext.get()

    if interactive:
        icmRunArgs = G.icmRunArgsGet()
        #if cmndArgsLengthValidate(cmndArgs=icmRunArgs.cmndArgs, expected=0, comparison=int__gt):
            #return(ReturnCode.UsageError)

        inPathList = []
        for thisPath in icm.icmRunArgs.cmndArgs:
            inPathList.append(thisPath)
    else:
        if inPathList == None:
            return b_io.eh.critical_usageError('inPathList is None and is Non-Interactive')

    for thisPath in inPathList:
        blankDict = FileParamDict()
        # print('path=' + thisPath)
        thisParamDict = blankDict.readFrom(path=thisPath)


        if thisParamDict == None:
            continue

        for parName, filePar  in thisParamDict.items():
            print(('parName=' + parName))
            if filePar == None:
                continue
            thisValue=filePar.parValueGetLines()
            if thisValue == None:
                # icm.TM_here("Skipping: " + filePar.parNameGet())
                continue
            print((
                filePar.parNameGet() +
                '=' +
                thisValue[0]))
    return


# FP_readTreeAtBaseDir = b.fp_csu.fpBaseDictRead   # OBSOLETED


def cmndCallParamsValidate(
        callParamDict,
        interactive,
        outcome=None,

):
    """Expected to be used in all CMNDs.

MB-2022 --- This is setting the variable not validating it.
    Perhaps the function should have been cmndCallParamsSet.

Usage Pattern:

    if not icm.cmndCallParamValidate(FPsDir, interactive, outcome=cmndOutcome):
       return cmndOutcome
"""
    #G = cs.globalContext.get()
    #if type(callParamOrList) is not list: callParamOrList = [ callParamOrList ]

    if not outcome:
        outcome = b.op.Outcome()

    for key  in callParamDict:
        # print(f"111 {key}")
        # interactive could be true in two situations:
        # 1) When a cs is executed on cmnd-line.
        # 2) When a cs is invoked with interactive as true.
        # When (2) callParamDict[key] is expcted to be true by having been specified at invokation.
        #
        if not callParamDict[key]:
            # MB-2022 The logic here seems wrong. When non-interactive, only mandattories
            # should be verified.
            # if not interactive:
            #     return eh_problem_usageError(
            #         outcome,
            #         "Missing Non-Interactive Arg {}".format(key),
            #     )
            if interactive:
                exec("callParamDict[key] = IcmGlobalContext().usageParams." + key)
            # print(f"222 {callParamDict[key]}")


    return True

####+BEGIN: b:py3:cs:func/typing :funcName "FILE_paramDictPrint" :funcType "extTyped" :retType "extTyped" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /FILE_paramDictPrint/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def FILE_paramDictPrint(
####+END:
        fileParamDict,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Returns a Dictionary of paramName:FileParam.
    #+end_org """
    for parName, filePar  in fileParamDict.items():
        #print('parName=' + parName)
        if filePar == None:
            continue
        thisValue=filePar.parValueGetLines()
        if thisValue == None:
            icm.TM_here("Skipping: " + filePar.parNameGet())
            continue
        if thisValue:
            print((
                filePar.parNameGet() +
                '=' +
                thisValue[0]))
        else: # Empty list
            print((
                filePar.parNameGet() +
                '='))



####+BEGIN: b:py3:cs:func/typing :funcName "FILE_paramDictReadDeep" :comment "OLD Style Cmnd" :funcType "extTyped" :retType "extTyped" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /FILE_paramDictReadDeep/ deco=default  =OLD Style Cmnd= deco=default   [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def FILE_paramDictReadDeep(
####+END:
        inPathList=None
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Uses os.walk.
    #+end_org """

    if inPathList == None:
            return b_io.eh.critical_usageError('inPathList is None')

    fileParamsDict = {}

    for thisPath in inPathList:
        #absolutePath = os.path.abspath(thisPath)

        if not os.path.isdir(thisPath):
            return b_io.eh.critical_usageError('Missing Directory: {thisPath}'.format(thisPath=thisPath))

        for root, dirs, files in os.walk(thisPath):
            #print("root={root}".format(root=root))
            #print ("dirs={dirs}".format(dirs=dirs))
            #print ("files={files}".format(files=files))

            thisFileParamValueFile = os.path.join(root, "value")
            if os.path.isfile(thisFileParamValueFile):
                try:
                    fileParam = FileParamReadFromPath(parRoot=root)
                except IOError:
                    b_io.eh.problem_info("Missing " + root)
                    continue

                fileParamsDict.update({root:fileParam.parValueGet()})

    return fileParamsDict


####+BEGIN: b:prog:file/endOfFile :extraParams nil
""" #+begin_org
* *[[elisp:(org-cycle)][| END-OF-FILE |]]* :: emacs and org variables and control parameters
#+end_org """
### local variables:
### no-byte-compile: t
### end:
####+END:
