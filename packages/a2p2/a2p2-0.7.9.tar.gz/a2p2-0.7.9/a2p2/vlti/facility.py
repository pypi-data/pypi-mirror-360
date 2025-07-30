#!/usr/bin/env python

__all__ = []

import os
from tkinter.constants import TRUE
import traceback
import logging
import re

import p2api

from a2p2.facility import Facility
from a2p2.vlti.gui import VltiUI

MODE_SM = 'SM'

ITEMTYPE_CONCATENATION = 'Concatenation'

JMMC_LOGIN = 'jmmc'

TUTORIAL_LOGIN = '52052'
PRODUCTION_APITYPE = 'production'
DEMO_APITYPE = 'demo'

# TODO handle a period subdirectory
CONFDIR = "conf"

# Look for configuration files in the same level directory as this module/conf/
try:
    _confdir = os.path.join(os.path.dirname(__file__), CONFDIR)
except NameError:
    _confdir = CONFDIR
if os.path.isdir(_confdir):
    CONFDIR = _confdir
elif not os.path.isdir(CONFDIR):
    raise RuntimeError("can't find conf directory (%r)" % (CONFDIR,))

HELPTEXT = """
ESO's P2 repository for Observing Blocks (OBs):


Send configuration from Aspro:
- In ASPRO, have an object, or an object selected, and check that all important informations (magnitudes, but also Instrument and Fringe Tracker Modes, eventually hour angles), are correctly set.
- In menu "Interop" select "Send Obs. blocks to A2p2"
- Block(s) are created and put in the P2 repository.
- If the source had one or more calibrators, blocks are created for them too.
- For each block submitted, a report is produced. Warnings are usually not significant.
- For more than 1 object sent, a <b>folder</b> containing the two or more blocks is created. In the absence of availability of grouping OBs (like for CAL-SCI-CAL) provided by ESO, this is the closets we can do.
- All the new OBs and folders will be available on p2web at https://www.eso.org/p2

On your first valid VLTI's OB, A2p2 will ask for your ESO User Portal credentials to interact with P2 using it's API. You can follow actions and organize more in details your OB on https://www.eso.org/p2 . Please use prefilled values of the login panel for testing purpose and follow ESO database from https://www.eso.org/p2demo/
"""
HELPTEXT += "Config files loaded from " + CONFDIR

logger = logging.getLogger(__name__)

class VltiFacility(Facility):

    def __init__(self, a2p2client):
        Facility.__init__(self, a2p2client, VltiFacility.getName(), HELPTEXT)
        self.ui = VltiUI(self)

        # Instanciate instruments
        # TODO complete list and make it more object oriented
        from a2p2.vlti.gravity import Gravity
        gravity = Gravity(self)
        from a2p2.vlti.pionier import Pionier
        pionier = Pionier(self)
        from a2p2.vlti.matisse import Matisse
        matisse = Matisse(self)

        # complete help
        for i in self.getSupportedInstruments():
            self.facilityHelp += "\n" + i.getHelp()

        self.connected = False
        # set to demo by default (may change in connectAPI)
        self.apitype = 'demo'
        self.containerInfo = P2Container(self)

        # will store later : name for status info, api
        self.username = None
        self.api = None

        # store ob to insert after container selection if not done previously
        self.ob_to_confirm=[]
        self.ob_to_submit=[]


    def getName():
        return "VLTI"

    def autologin(self):
        self.ui.addToLog("\nAutologin into P2 API please wait...\n")
        self.ui.loginFrame.on_loginbutton_clicked()
        self.a2p2client.ui.showFacilityUI(self.ui)
        self.ui.showTreeFrame()

    def processOB(self, ob):
        # process last accepted OB if ob is None
        if not ob:
            self.processLastAcceptedOB()
            return

        # give focus on last updated UI
        self.a2p2client.ui.showFacilityUI(self.ui)
        # show ob dict for debug
        self.ui.addToLog(str(ob), False)

        # OB is checked and submitted by instrument
        period = ob.getPeriod()
        self.ui.addToLog(f"Request received for OB creation for P{period} - please press Submit or Abort button")

        # always stores OB and pop them if everything is ok or later selecting containers in the tree
        self.pushOB(ob)
        self.tryLastOB()

    def tryLastOB(self):
        self.showOBConfirmationButtons()
        # stop if no ob has to be handled
        if not self.hasOB():
            return

        ob = self.ob_to_confirm[-1]
        # run checkOB which may raise some error before connection request
        # TODO we should test much more because lot of stuff still are beeing processed on live ob creations

        period = ob.getPeriod()
        instrument = self.getInstrument(ob.instrumentConfiguration.name)
        insname = instrument.getShortName()

        # performs operation
        if not self.isConnected():
            self.ui.showLoginFrame(ob)
        elif not self.isReadyToSubmit(ob):
            # self.a2p2client.ui.addToLog("Receive OB for
            # '"+ob.instrumentConfiguration.name+"'")
            self.ui.addToLog(
                f"Selected folder must not be a concatenation. please choose another container for '{insname}' P'{period}'.")
        elif  insname.lower() != self.containerInfo.getInstrument().lower():
            self.ui.addToLog(
                f"'{self.containerInfo.getInstrument()}' selection in not applicable for received OB. Please choose another one for '{insname}' P'{period}'.")
        elif  period != int(self.containerInfo.getIpVersion()):
            self.ui.addToLog(
                f"Container's IpVersion '{int(self.containerInfo.getIpVersion())}' is not applicable for received OB's one '{period}', please select another '{insname}' container or change it in Aspro2.")
        else:
            self.showOBConfirmationButtons(ob, insname=="GRAVITY")

    def showOBConfirmationButtons(self, ob=None, showAcqButtons=False):
        self.ui.showOBConfirmationButtons(ob, showAcqButtons)

    def isReadyToSubmit(self, ob):
        return self.api and self.containerInfo.isOk(ob)

    def isConnected(self):
        return self.connected

    def setConnected(self, flag):
        self.connected = flag

    def pushOB(self,ob):
        self.ob_to_confirm.append(ob)

    def hasOB(self):
        return len(self.ob_to_confirm)>0

    def popOB(self, ignore=False):
        """ Called as last step : ob is for the selected container and User click on submit!
        If ignore is set to True, last ob is simply removed else it is forwarded to P2 and removed from stack. """

        if not self.hasOB():
            return

        # pop last OB
        o = self.ob_to_confirm.pop()
        self.showOBConfirmationButtons()

        if ignore:
            self.ui.addToLog("Last received OB has been aborted")
            return
        else:
            self.ob_to_submit.append(o)

    def processLastAcceptedOB(self):
        if len(self.ob_to_submit)==0:
            return

        o=self.ob_to_submit.pop()
        try:
            instrument = self.getInstrument(o.instrumentConfiguration.name)
            instrument.checkOB(o)
            # check for warnings and abort if requested by user
            # this implementation should be more detailled so we can have various VERSION associated to various warning
            if len(instrument.warnings)>0:
                linesep="\n  -  "
                header=""
                try:
                    # some ditTable may have a VERSION entry some not...
                    version=instrument.getDitTable()["VERSION"]
                    header= f"According to the template manual {version} :\n \n  - \n"
                except:
                    pass
                answer = self.ui.AskYesNoMessage(f"{header} {linesep.join(instrument.warnings)}\n\nClick \"Yes\" to proceed \"No\" to abort the submission")
                instrument.warnings.clear()
                if answer == False:
                    self.ui.addToLog("Submission has been marked to be aborted - do not proceed")
                    return

            self.ui.addToLog("Everything ready! Request OB creation inside selected container")
            instrument.submitOB(o, self.containerInfo)

            # TODO add P2Error handling P2Error(r.status_code, method, url,
            # r.json()['error'])
        except ValueError as e:
            traceback.print_exc()
            trace = traceback.format_exc(limit=1)
            # ui.ShowErrorMessage("Value error :\n %s \n%s\n\n%s" % (e, trace,
            # "Aborting submission to P2. Look at the whole traceback in the log."))
            self.ui.ShowErrorMessage("Value error :\n %s \n\n%s" %
                                    (e, "Aborting submission to P2. Please check LOG and fix before new submission."))
            trace = traceback.format_exc()
            self.ui.addToLog(trace, False)
            self.ui.setProgress(0)
        except Exception as e:
            traceback.print_exc()
            # limit = 2 should raise errors in our codes
            trace = traceback.format_exc(limit=1)
            self.ui.ShowErrorMessage(
                "General error or Absent Parameter in template!\n Missing magnitude or OB not set ?\n\nError :\n %s \n Please check LOG and fix before new submission." % (
                    trace))
            trace = traceback.format_exc()
            self.ui.addToLog(trace, False)
            self.ui.setProgress(0)

    def getStatus(self):
        ob_info=""
        if self.hasOB():
            ob_info=f" / {len(self.ob_to_confirm)} OB in stack"
        if self.isConnected():
            return f" P2API({self.apitype}) connected with {self.username} { ob_info }"

    def connectAPI(self, username, password, ob):
        if username == TUTORIAL_LOGIN: # or username == JMMC_LOGIN:
            self.apitype = DEMO_APITYPE
        else:
            self.apitype = PRODUCTION_APITYPE
        try:
            logger.info("Connecting to p2 api...")
            self.api = p2api.ApiConnection(self.apitype, username, password)

            self.ui.addToLog("Connected to p2 api (%s)"%self.apitype)
            # TODO test that api is ok and handle error if any...

            self.refreshTree()

            self.setConnected(True)
            self.username = username
            self.ui.showTreeFrame(ob)
        except:
            self.ui.ShowErrorMessage("Can't connect to P2 (see LOG).")
            trace = traceback.format_exc()
            self.ui.addToLog(trace, False, level=logging.ERROR)

    def refreshTree(self):
        runs, _ = self.api.getRuns()
        self.ui.fillTree(runs)

    def isDemoAPI(self):
        return self.apitype == DEMO_APITYPE

    def isTutorialAccount(self):
        return self.username == TUTORIAL_LOGIN

    def getAPI(self):
        return self.api

    def getConfDir(self):
        """
        returns the configuration directory with instrument's json files
        """
        return CONFDIR

    def getIssVltiTypes(self):
        return ['snapshot','imaging','time-series','astrometry']



# TODO Move code out of this class

class P2Container:
    # run object stores:
    # {'pi': {'lastName': 'Accont', 'emailAddress': '52052@nodomain.net', 'firstName': 'Phase 1/2 Ttorial'},
    # 'telescope': 'VLTI', 'title': 'p2 tutorial', 'schedledPeriod': 60, 'isToO': False, 'period': 60, 'owned': Tre,
    # 'ipVersion': 104.05, 'instrument': 'PIONIER', 'containerId': 1601182, 'observingConstraints': {'fli' : 'd', 'seeing': 0.8},
    # 'mode': 'SM', 'progId': '60.A-9253(T)', 'itemCont': 2, 'delegated': False, 'runId': 60925319}
    # and item (when not run) :
    # {u'containerStatus': u'P', u'itemType': u'Group', u'name': u'New Group', u'groupScore': 0.0,
    # u'containerId': 2609528, u'runId': 60925213, u'userPriority': 1, u'itemCount': 0, u'parentContainerId': 2609516}

    def __init__(self, facility):
        self.facility = facility
        self.run = None  # dict returned by p2api
        self.containerId = None
        self.item = None

    def store(self, run, item):
        self.run = run
        self.item = item
        self.containerId = item['containerId']
        self.log()

    def reset(self):
        self.run = None  # dict returned by p2api
        self.containerId = None
        self.item = None

    def log(self):
        logmsg = f"*** Working with {self} ***"
        if self.run != self.item and self.item['itemType'] == ITEMTYPE_CONCATENATION:
            self.reset()
            self.facility.ui.addToLog(
                "*** Please do not select a Concatenation and select another container. Or just append a calibrator. ***", )
            logger.info(logmsg)
        else:
            self.facility.ui.addToLog(logmsg)

    def isOk(self, ob):
        """ Tell if given container is ready to receive content of given OB."""
        if self.run == None:
            return False
        if self.run == self.item:
            return True

        has_calib = False
        has_science = False
        for obsConf in ob.observationConfiguration:
            if 'SCIENCE' in obsConf.type:
                has_science = True
            else:
                has_calib = True

        if has_science:
            return self.item['itemType'] != ITEMTYPE_CONCATENATION
        return has_calib

    def getInstrument(self):
        return self.run['instrument']

    def getIpVersion(self):
        return self.run['ipVersion']

    def isRoot(self):
        return self.item.keys() != None and 'pi' in self.item.keys()

    def isServiceModeRun(self):
        return self.run['mode'] == MODE_SM

    def __str__(self):
        return """instrument:'%s', containerId:'%s'""" % (self.run['instrument'], self.containerId)
