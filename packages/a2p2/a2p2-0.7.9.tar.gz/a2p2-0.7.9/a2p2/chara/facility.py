#!/usr/bin/env python

__all__ = []

from a2p2.chara.gui import CharaUI
from a2p2.facility import Facility
import requests
import logging
import traceback

HELPTEXT = "TODO update this HELP message in a2p2/chara/facility.py"

logger = logging.getLogger(__name__)

class CharaFacility(Facility):

    def __init__(self, a2p2client):
        Facility.__init__(self, a2p2client, "CHARA", HELPTEXT)
        self.charaUI = CharaUI(self)
        self.connected2OB2 = False
        self.validQueueServer = None

    def processOB(self, ob):
        if not ob:
            return

        self.a2p2client.ui.addToLog(
            "OB received for '" + self.facilityName + "' interferometer")
        # show ob dict for debug
        self.a2p2client.ui.addToLog(str(ob), False)

        # performs operation
        self.consumeOB(ob)

        # give focus on last updated UI
        self.a2p2client.ui.showFacilityUI(self.charaUI)

    def checkServer(self):
        if self.validQueueServer:
            # recheck ?
            return True
        else:
            # search and test servers from preferences
            queueServers=self.a2p2client.preferences.getCharaQueueServer()
            msg=""
            if queueServers :
                for queueServer in queueServers:
                    logger.debug(f'Trying to send OB on queuserver : {queueServer}')
                    try:
                        c=requests.get(queueServer, timeout=3)
                        msg+=f"Connection succeeded on OB server : {c.json()}\n"
                        self.validQueueServer = queueServer
                        break
                    except:
                        msg+=f"Connection failed on {queueServer}\n"

            self.a2p2client.ui.addToLog(msg)
            self.charaUI.display(msg)

            return self.validQueueServer

    def consumeOB(self, ob):
        if self.checkServer():
            try:
                r = requests.post(self.validQueueServer, json=ob.as_dict(), timeout=3)
                msg = ""
                msg+=f"OB sent to remote server queue : {r}"
                self.connected2OB2 = True
                self.a2p2client.ui.addToLog(msg)
                self.charaUI.display(msg)
            except:
                print(traceback.format_exc())
                msg=f"Can't send OB to the '{self.validQueueServer}' queue server, please relaunch it or try again for a new one."
                self.validQueueServer = None
                self.a2p2client.ui.addToLog(msg)
                self.charaUI.display(msg)
        else:
            msg=f"Can't find any queue server, please launch it, edit your preferences or check your ssh port forwarding"

        # display OB
        self.charaUI.displayOB(ob)


