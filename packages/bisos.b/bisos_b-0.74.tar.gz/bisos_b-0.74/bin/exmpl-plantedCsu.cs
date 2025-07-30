#!/usr/bin/env python

""" #+begin_org
* Panel::  [[file:/bisos/panels/bisos-apps/NameOfThePanelComeHere/_nodeBase_/fullUsagePanel-en.org]]
* Overview and Relevant Pointers
#+end_org """

from bisos import b
from bisos.b import cmndsSeed
from bisos.b import cs
from bisos.b import b_io

import collections
import typing

def commonParamsSpecify(csParams: cs.param.CmndParamDict,) -> None:
    # print("HERE")
    # print(csParams)
    csParams.parDictAdd(
        parName='par1Example',
        parDescription="Description of par1Example comes here",
        argparseLongOpt='--par1Example',
    )
    csParams.parDictAdd(
        parName='par2Example',
        parDescription="Description of par2Example comes here",
        parDefault='ParTwoDefault',
        argparseLongOpt='--par2Example',
    )

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "parsArgsStdinCmndResult" :extent "verify" :comment "stdin as input" :parsMand "par1Example" :parsOpt "par2Example" :argsMin 1 :argsMax 9999 :pyInv "methodInvokeArg"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<parsArgsStdinCmndResult>>  *stdin as input*  =verify= parsMand=par1Example parsOpt=par2Example argsMin=1 argsMax=9999 ro=cli pyInv=methodInvokeArg   [[elisp:(org-cycle)][| ]]
#+end_org """
class parsArgsStdinCmndResult(cs.Cmnd):
    cmndParamsMandatory = [ 'par1Example', ]
    cmndParamsOptional = [ 'par2Example', ]
    cmndArgsLen = {'Min': 1, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             par1Example: typing.Optional[str]=None,  # Cs Mandatory Param
             par2Example: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
             methodInvokeArg: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:
        """stdin as input"""
        callParamsDict = {'par1Example': par1Example, 'par2Example': par2Example, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] This is an example of a CmndSvc with lots of features.
The features include:

        1) An optional parameter called someParam
        2) A first mandatory argument called action which must be one of list or print.
        3) An optional set of additional argumets.

The param, and args are then validated and form a single string.
That string is then echoed in a sub-prococessed. The stdout of that sub-proc is assigned
to a variable similar to bash back-quoting.

And that variable is then printed.

Variations of this are captured as snippets to be used.
        #+end_org """)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  exmpl-seeded-cmnds.cs --par1Example="par1Mantory" --par2Example="par2Optional" -i parsArgsStdinCmndResult arg1 argTwo
#+end_src
#+RESULTS:
: cmndArgs= arg1  argTwo
: stdin instead of methodInvokeArg =
: cmndParams= par1Mantory par2Optional
: cmnd results come here
        #+end_org """)

        if self.justCaptureP(): return cmndOutcome


        action = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        actionArgs = self.cmndArgsGet("1&9999", cmndArgsSpecDict, argsList)

        actionArgsStr = ""
        for each in actionArgs:
            actionArgsStr = actionArgsStr + " " + each

        actionAndArgs = f"""{action} {actionArgsStr}"""


        b.comment.orgMode(""" #+begin_org
*****  [[elisp:(org-cycle)][| *Note:* | ]] Next we take in stdin, when interactive.
After that, we print the results and then provide a result in =cmndOutcome=.
        #+end_org """)

        if not methodInvokeArg:
            methodInvokeArg = b_io.stdin.read()

        print(f"cmndArgs= {actionAndArgs}")
        print(f"stdin instead of methodInvokeArg = {methodInvokeArg}")
        print(f"cmndParams= {par1Example} {par2Example}")

        return cmndOutcome.set(
            opError=b.op.OpError.Success,
            opResults="cmnd results come here",
        )

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self,):
        """  #+begin_org
*** [[elisp:(org-cycle)][| *cmndArgsSpec:* | ]] First arg defines rest
        #+end_org """

        cmndArgsSpecDict = cs.arg.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0",
            argName="action",
            argChoices=['echo', 'encrypt', 'ls', 'date'],
            argDescription="Action to be specified by rest"
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="1&9999",
            argName="actionArgs",
            argChoices=[],
            argDescription="Rest of args for use by action"
        )

        return cmndArgsSpecDict

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "pyCmndInvOf_parsArgsStdinCmndResult" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<pyCmndInvOf_parsArgsStdinCmndResult>> ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class pyCmndInvOf_parsArgsStdinCmndResult(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  exmpl-seeded-cmnds.cs -i pyCmndInvOf_parsArgsStdinCmndResult
#+end_src
#+RESULTS:
: cmndArgs= echo  py_arg2Val
: stdin instead of methodInvokeArg = py method invoke arg
: cmndParams= py_par1Val None
        #+end_org """)

        if self.justCaptureP(): return cmndOutcome

        if not (results := parsArgsStdinCmndResult(cmndOutcome=cmndOutcome).pyCmnd(
                par1Example="py_par1Val",
                argsList=['echo', 'py_arg2Val'],
                methodInvokeArg="py method invoke arg"
        ).results): return(b_io.eh.badOutcome(cmndOutcome))

        return(cmndOutcome)

def examples_csu() -> None:
    """Common Usage Examples for this Command-Service Unit"""

    od = collections.OrderedDict
    cmnd = cs.examples.cmndEnter

    cs.examples.menuChapter('*Cmnds, PyInv, With Params, Args, Stdin Producing Outcome*')

    csWrapper = "echo From Stdin HereComes Some ClearText | "

    mandatoryPars = od([('par1Example', "valueOfParOne"),])
    optionalPars = od([('par2Example', "valueOfParTwo"),])
    mandatoryAndOptionalPars = od([('par1Example', "valueOfParOne"), ('par2Example', "valueOfParTwo")])
    cmndArgs = "echo some thing"

    cmnd('parsArgsStdinCmndResult', args=cmndArgs, pars=mandatoryPars, comment=" # Uses default value of optional param")
    cmnd('parsArgsStdinCmndResult', args=cmndArgs, pars=optionalPars, comment=" # Bad usage, missing mandatory param")
    cmnd('parsArgsStdinCmndResult', args=cmndArgs, pars=mandatoryAndOptionalPars, comment=" # Both mandatory and optional params")

    cs.examples.menuSection('*Stdin in addition to args or instead of args*')

    cmnd('parsArgsStdinCmndResult', wrapper=csWrapper, args=cmndArgs, pars=mandatoryAndOptionalPars, comment=" # Both stdin and args are used")
    cmnd('parsArgsStdinCmndResult', wrapper=csWrapper, pars=mandatoryAndOptionalPars, comment=" # Stdin instead of  args")

    cs.examples.menuSection('Direct PyInv of parsArgsStdinCmndResult*')

    cmnd('pyCmndInvOf_parsArgsStdinCmndResult', comment=" # Uses py invokes parsArgsStdinCmndResult")


# cmndsSeed.register(
#     commonParamsFuncs=[commonParamsSpecify,],
#     examplesFuncsList=[examples_csu,],
# )

# cmndsSeed.plantWithWhich("seedCmnds.cs")
