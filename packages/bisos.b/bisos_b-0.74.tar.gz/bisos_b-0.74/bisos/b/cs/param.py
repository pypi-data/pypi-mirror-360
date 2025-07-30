# -*- coding: utf-8 -*-

""" #+begin_org
* *[Summary]* :: A =Py+CsLib= for Abstracting CS Cmnd Parameters (Param).
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
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['param'], }
csInfo['version'] = '202209034512'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'param-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* /[[elisp:(org-cycle)][| Description |]]/ :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/PyFwrk/bisos-pip/bisos.cs/_nodeBase_/fullUsagePanel-en.org][PyFwrk bisos.cs Panel]]
for Abstracting CS Cmnd Parameters (Param).
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

####+BEGIN: b:py3:cs:csItem :itemType "=PyImports= " :itemTitle "*Py Library IMPORTS*"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =PyImports=  [[elisp:(outline-show-subtree+toggle)][||]] *Py Library IMPORTS*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


import os

import enum
#

#import traceback

# import collections

# import pathlib

# from bisos.platform import bxPlatformConfig
# from bisos.platform import bxPlatformThis

# from bisos.basics import pattern

from bisos.b import b_io
from bisos import b


####+BEGIN: bx:cs:py3:section :title "CmndParam: ICM Parameter (CmndParam, CmndParamDict)"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CmndParam: ICM Parameter (CmndParam, CmndParamDict)*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: bx:dblock:python:enum :enumName "CmndParamScope" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Enum       [[elisp:(outline-show-subtree+toggle)][||]] /CmndParamScope/  [[elisp:(org-cycle)][| ]]
#+end_org """
@enum.unique
class CmndParamScope(enum.Enum):
####+END:
    TargetParam = 'TargetParam'
    IcmGeneralParam = 'IcmGeneralParam'
    CmndSpecificParam = 'CmndSpecificParam'

# CmndParamScope = ucf.enum('TargetParam', 'IcmGeneralParam', 'CmndSpecificParam')

####+BEGIN: bx:dblock:python:class :className "CmndParam" :superClass "" :comment "" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /CmndParam/ object  [[elisp:(org-cycle)][| ]]
#+end_org """
class CmndParam(object):
####+END:
     """Representation of an Interactively Invokable Module Parameter (CmndParam).

     An ICM Parameter is a superset of an argsparse parameter which also includes:
        - CMND relevance (Mandatory and Optional)
        - Maping onto FILE_Params


     CmndParam is initially used to setup ArgParse and other user-interface parameter aspects.
     """

     def __init__(self,
                  parName=None,
                  parDescription=None,
                  parDataType=None,
                  parDefault=None,
                  fileParInit=None,
                  fileParName=None,
                  # parChoices=None,
                  parChoices=[],
                  parScope=None,
                  parMetavar=None,
                  parAction='store',                    # Same as argparse's action
                  parNargs=None,                        # Same as argparse's nargs
                  parCmndApplicability=None,             # List of CMNDs to which this ICM is applicable
                  argparseShortOpt=None,
                  argparseLongOpt=None,
                 ):
         '''Constructor'''
         self.__parName = parName
         self.__parValue = None
         self.__parCmndApplicability = parCmndApplicability
         self.__parDescription = parDescription
         self.__parDataType = parDataType
         self.__parDefault = parDefault
         self.__fileParInit = fileParInit
         self.__fileParName = fileParName
         self.__parChoices = parChoices
         self.__parMetavar = parMetavar
         self.parActionSet(parAction)
         self.parNargsSet(parNargs)
         self.__argparseShortOpt =  argparseShortOpt
         self.__argparseLongOpt =  argparseLongOpt

     def __str__(self):
         return  ("""\
parName: {parName}
value: {value}
description: {description}""".
                  format(
                      parName=self.parNameGet(),
                      value=self.parValueGet(),
                      description=self.parDescriptionGet()
                  )
             )

     def parNameGet(self):
         """  """
         return self.__parName

     def parNameSet(self, parName):
         """        """
         self.__parName = parName

     def parValueGet(self):
         """        """
         return self.__parValue

     def parValueSet(self, value):
         """        """
         self.__parValue = value

     def parFpValueSet(self, value):
         """        """
         self.__parFpValue = value

     @property
     def fileParInit(self) -> str | None:
         return self.__fileParInit

     @fileParInit.setter
     def fileParInit(self, value: str | None,):
         self.__fileParInit = value

     @property
     def fileParName(self) -> str | None:
         return self.__fileParName

     @fileParName.setter
     def fileParName(self, value: str | None,):
         self.__fileParName = value

     def parDescriptionGet(self):
         """        """
         return self.__parDescription

     def parDescriptionSet(self, parDescription):
         """        """
         self.__parDescription = parDescription

     def parDataTypeGet(self):
         """        """
         return self.__parDataType

     def parDataTypeSet(self, parDataType):
         """        """
         self.__parDataType = parDataType

     def parDefaultGet(self):
         """        """
         return self.__parDefault

     def parDefaultSet(self, parDefault):
         """        """
         self.__parDefault = parDefault

     def parChoicesGet(self):
         """        """
         return self.__parChoices

     def parChoicesSet(self, parChoices):
         """        """
         self.__parChoices = parChoices

     def parActionGet(self):
         """        """
         return self.__parAction

     def parActionSet(self, parAction):
         """        """
         self.__parAction = parAction

     def parNargsGet(self):
         """        """
         return self.__parNargs

     def parNargsSet(self, parNargs):
         """        """
         self.__parNargs = parNargs

     def argsparseShortOptGet(self):
         """        """
         return self.__argparseShortOpt

     def argsparseShortOptSet(self, argsparseShortOpt):
         """        """
         self.__argparseShortOpt = argsparseShortOpt

     def argsparseLongOptGet(self):
         """        """
         return self.__argparseLongOpt

     def argsparseLongOptSet(self, argsparseLongOpt):
         """        """
         self.__argparseLongOpt = argsparseLongOpt

     def readFrom(self, parRoot=None, parName=None):
         """Read into a FILE_param content of parBase/parName.

         Returns a FILE_param which was contailed in parBase/parName.
         """

         absoluteParRoot = os.path.abspath(parRoot)

         if not os.path.isdir(absoluteParRoot):
             return None

         absoluteParBase = os.path.join(absoluteParRoot, parName)

         if not os.path.isdir(absoluteParBase):
             return None

         fileParam = self

         self.__parName = parName

         #
         # Now we will fill fileParam based on the directory content
         #
         for item in os.listdir(absoluteParBase):
             fileFullPath = os.path.join(absoluteParBase, item)
             if os.path.isfile(fileFullPath):

                 if item == 'value':
                     lineString = open(fileFullPath, 'r').read()
                     self.parValueSet(lineString)
                     continue

                 # Rest of the files are expected to be attributes

                 lineString = open(fileFullPath, 'r').read()
                 # NOTYET, check for exceptions
                 eval('self.attr' + str(item).title() + 'Set(lineString)')

         return fileParam

     # NOTYET 20220822 -- most likely due to a circular import
     #@io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
     def writeAsFileParam(
             self,
             parRoot=None,
     ):
         """Writing a FILE_param content of self.

         Returns a FILE_param which was contailed in parBase/parName.
         """

         absoluteParRoot = os.path.abspath(parRoot)

         if not os.path.isdir(absoluteParRoot):
            try: os.makedirs( absoluteParRoot, 0o775 )
            except OSError: pass

         #print absoluteParRoot

         #print
         #print self.parValueGet()

         parValue = self.parValueGet()
         if not parValue:
             parValue = "unSet"

         fileParName = self.parNameGet()
         if self.fileParName:
             fileParName = self.fileParName

         b.fp.FileParamWriteTo(
             parRoot=absoluteParRoot,
             parName=fileParName,
             parValue=parValue,
         )

         varValueFullPath = os.path.join(
             absoluteParRoot,
             fileParName,
             'description'
         )

         b.fv.writeToFilePathAndCreate(
             filePath=varValueFullPath,
             varValue=self.parDescriptionGet(),
         )

         varValueBaseDir = os.path.join(
             absoluteParRoot,
             fileParName,
             'enums'
         )

         for thisChoice in self.parChoicesGet():
             b.fv.writeToBaseDirAndCreate(
                 baseDir=varValueBaseDir,
                 varName=thisChoice,
                 varValue="",
             )

####+BEGIN: bx:dblock:python:class :className "CmndParamDict" :superClass "" :comment "" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /CmndParamDict/ object  [[elisp:(org-cycle)][| ]]
#+end_org """
class CmndParamDict(object):
####+END:
     """CS Parameters Dictionary -- Collection of CmndParam s can be placed in CmndParamDict

     From csParamDict
     """

     def __init__(self):
         self.__csParamDict = dict()

     def parDictAdd(self,
                    parName=None,
                    parDescription=None,
                    parDataType=None,
                    parMetavar=None,
                    parDefault=None,
                    fileParInit=None,
                    fileParName=None,
                    parChoices=[],
                    parScope=None,
                    parAction='store',
                    parNargs=None,
                    argparseShortOpt=None,
                    argparseLongOpt=None,
                   ):
         """        """
         thisParam = CmndParam(parName=parName,
                               parDescription=parDescription,
                               parDataType=parDataType,
                               parMetavar=parMetavar,
                               parDefault=parDefault,
                               fileParInit=fileParInit,
                               fileParName=fileParName,
                               parChoices=parChoices,
                               parScope=parScope,
                               parAction=parAction,
                               parNargs=parNargs,
                               argparseShortOpt=argparseShortOpt,
                               argparseLongOpt=argparseLongOpt,
                               )

         self.parDictAppend(thisParam)
         # print(f"rrr {thisParam}")

     def parDictAppend(self, csParam):
         """        """
         self.__csParamDict.update({csParam.parNameGet():csParam})


     def parDictGet(self):
         """        """
         return self.__csParamDict

     def parNameFind(self, parName):
         """        """
         found = self.__csParamDict[parName]
         return found


     def cmndApplicabilityUpdate(self,
                                cmnd=None,
                                mandatoryParams=None,
                                optionalParams=None,
                                ):
         """NOTYET -- Verify That Mandatory and Optional Params for this cmnd have been specified At Runtime."""

         return

####+BEGIN: bx:cs:py3:func :funcName "commonCsParamsPrep" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /commonCsParamsPrep/  [[elisp:(org-cycle)][| ]]
#+end_org """
def commonCsParamsPrep(
####+END:
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Module Common Command Line Parameters.
    #+end_org """

    print("NOTYET --- This Has been obsoleted??? ---- JJJJJJJJJJJJJJ")

    csParams = CmndParamDict()

    csParams.parDictAdd(
        parAction='append',
        parName='callTrackingsFF',
        parDescription="Set monitoring of calls and selected invokes.",
        parDataType=None,
        parDefault=[],
        parChoices=['invoke+', 'invoke-', 'monitor+', 'monitor-'],
        parScope=CmndParamScope.TargetParam,
        argparseShortOpt='-t',
        argparseLongOpt='--callTrackingsFF',  # NOTYET
        )

    csParams.parDictAdd(
        parAction='store',
        parName='runMode',
        parDescription="Run Mode as fullRun or dryRun",
        parDataType=None,
        parDefault='fullRun',
        parChoices=['dryRun', 'fullRun', 'runDebug'],
        parScope=CmndParamScope.TargetParam,
        #argparseShortOpt='-r',
        argparseLongOpt='--runMode',
        )

    csParams.parDictAdd(
        parAction='store',
        parName='verbosity',
        parDescription='Adds a Console Logger for the level specified in the range 1..50',
        parDataType=None,
        parDefault='30',
        parMetavar='ARG',
        parChoices=['1', '10', '20', '30', '40', '50',],
        parScope=CmndParamScope.TargetParam,
        argparseShortOpt='-v',
        argparseLongOpt='--verbosity',
        )

    csParams.parDictAdd(
        parAction='store',
        parName='logFile',
        parDescription='Specifies destination LogFile for this run',
        parDataType=None,
        parDefault=None,
        parMetavar='ARG',
        parChoices=[],
        parScope=CmndParamScope.TargetParam,
        #argparseShortOpt='-v',
        argparseLongOpt='--logFile',
        )

    csParams.parDictAdd(
        parAction='store',
        parName='sectionTitle',
        parDescription='For use as section title of examples',
        parDataType=None,
        parDefault=None,
        parMetavar='ARG',
        parChoices=[],
        parScope=CmndParamScope.TargetParam,
        #argparseShortOpt='-v',
        argparseLongOpt='--sectionTitle',
        )

    csParams.parDictAdd(
        parAction='store',
        parName='logFileLevel',
        parDescription='Specifies destination LogFile for this run',
        parDataType=None,
        parDefault=None,
        parMetavar='ARG',
        parChoices=[],
        parScope=CmndParamScope.TargetParam,
        #argparseShortOpt='-v',
        argparseLongOpt='--logFileLevel',
        )

    csParams.parDictAdd(
        parAction='store_true',
        parName='docstring',
        parDescription='Docstring',
        parDataType=None,
        parDefault=None,
        parMetavar='ARG',
        parChoices=[],
        parScope=CmndParamScope.TargetParam,
        #argparseShortOpt='-v',
        argparseLongOpt='--docString',
        )

    csParams.parDictAdd(
        parAction='store_true',
        parName='force',
        parDescription='Over writes default behaviour and forces actions',
        parDataType=None,
        parDefault=None,
        parMetavar='ARG',
        parChoices=[],
        parScope=CmndParamScope.TargetParam,
        argparseShortOpt='-f',
        argparseLongOpt='--force',
        )

    # csParams.parDictAdd(
    #
    #     parAction='store',
    #     parName='cmndArgs',
    #     parDescription='Docstring',
    #     parDataType=None,
    #     parDefault=None,
    #     parMetavar='ARG',
    #     parChoices=None,
    #     parScope=CmndParamScope.TargetParam,
    #     #argparseShortOpt='-v',
    #     argparseLongOpt='--logFileLevel',
    #     )


    csParams.parDictAdd(
        parAction='append',
        parName='loadfiles',
        parDescription='Load Files',
        parDataType=None,
        parDefault=None,
        parMetavar='ARG',
        parChoices=[],
        parScope=CmndParamScope.TargetParam,
        #argparseShortOpt='-l',
        argparseLongOpt='--load',
        )


    return csParams

commonIcmParamsPrep = commonCsParamsPrep

####+BEGIN: bx:cs:py3:func :funcName "csParamsToFileParamsUpdate" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /csParamsToFileParamsUpdate/  [[elisp:(org-cycle)][| ]]
#+end_org """
def csParamsToFileParamsUpdate(
####+END:
        parRoot,
        icmParams,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Convert icmParams to parser
    #+end_org """

    b_io.log.here("Updating icmParams at: {parRoot}".format(parRoot=parRoot))

    for key, icmParam in icmParams.parDictGet().items():
        if ( icmParam.argsparseShortOptGet() == None )  and ( icmParam.argsparseLongOptGet() == None ):
            break

        icmParam.writeAsFileParam(
            parRoot=parRoot,
        )

    return

icmParamsToFileParamsUpdate = csParamsToFileParamsUpdate

####+BEGIN: bx:cs:py3:func :funcName "cmndParamsMandatoryAssert" :funcType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /cmndParamsMandatoryAssert/  [[elisp:(org-cycle)][| ]]
#+end_org """
def cmndParamsMandatoryAssert(
####+END:
        parRoot,
        icmParams,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Convert icmParams to parser
    #+end_org """

    for key, value in paramsList.items():
        if value == None: return(io.eh.critical_usageError(key))



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
