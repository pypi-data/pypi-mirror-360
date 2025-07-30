#!/usr/bin/env python

__all__ = ['A2p2Client']

import time
import traceback
import os
import configparser
import logging

from a2p2 import __version__
from a2p2.facility import FacilityManager
from a2p2.gui import MainWindow
from a2p2.ob import OB
from a2p2.samp import A2p2SampClient
from a2p2.vlti.facility import VltiFacility



# prepare global logging
a2p2Rootlogger = logging.getLogger("a2p2")
a2p2Rootlogger.setLevel(logging.INFO)
# uncomment next two lines to log requests done by p2api as debug and maybe other ones...
#a2p2Rootlogger = logging.getLogger()
#a2p2Rootlogger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
consoleFormatter = logging.Formatter(
    '%(levelname)s - %(name)s  - %(asctime)s - %(filename)s:%(lineno)d - %(message)s')
console.setFormatter(consoleFormatter)
a2p2Rootlogger.addHandler(console)

logger = logging.getLogger(__name__)


class A2p2Client():
    """Transmit your Aspro2 observation to remote Observatory scheduling database.

       with A2p2Client() as a2p2:
           a2p2.run()
           ..."""

    def __init__(self, fakeAPI=False, verbose=False):
        """Create the A2p2 client."""

        self.preferences = A2P2ClientPreferences()

        self.apiName = ""
        if fakeAPI:
            self.apiName = "fakeAPI"
        self.fakeAPI = fakeAPI

        if verbose:
            a2p2Rootlogger.setLevel(logging.DEBUG)

        self.ui = MainWindow(self)
        # Instantiate the samp client and connect to the hub later
        self.a2p2SampClient = A2p2SampClient()
        self.facilityManager = FacilityManager(self)

        if self.preferences.exists():
            A2P2ClientPreferences.updatePreferencesFile()
            self.ui.addToLog(
                f"Using preference from '{A2P2ClientPreferences.getPreferencesFileName()}'.\n")
        else:
            self.ui.addToLog(
                "No preference file found, please create one so your data persists (launch program with -c option).\n")

        self.ui.addToLog("Please often update ( pip install -U [--user] a2p2 ) and don't hesitate to send any feedback or issues!\n\n")


        self.errors = []

        pass

    def __enter__(self):
        """Handle starting the 'with' statements."""

        self.ui.addToLog("              Welcome in the A2P2 V" + __version__)
        self.ui.addToLog("")
        self.ui.addToLog("( https://github.com/JMMC-OpenDev/a2p2/wiki )")

        return self

    def __del__(self):
        """Handle deleting the object."""
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        """Handle closing the 'with' statement."""
        del self.a2p2SampClient
        del self.ui
        # TODO close the connection to the obs database ?

        # WARNING do not return self only. Else exceptions are hidden
        # return self

    def __str__(self):
        instruments = "\n- ".join(["Supported instruments:", "TBD"])
        apis = "\n- ".join(["Supported APIs:", "TBD"])
        return """a2p2 client\n%s\n%s\n""" % (instruments, apis)

    def changeSampStatus(self, connected_flag):
        self.sampConnected = connected_flag

    def setProgress(self, perc, actionName=None):
        if actionName:
            print("%s action progress is  %s" % (actionName, perc))
        else:
            print("progress is  %s %%" % (perc))

    def clearErrors(self):
        self.errors.clear()

    def getErrors(self):
        return self.errors

    def addError(self, error):
        self.errors.append(error)

    def processOB(self, ob):
        self.facilityManager.processOB(ob)

    def run(self):
        # bool of status change
        flag = [0]

        logger.info("Running client ...")

        # handle autologin
        if self.preferences.getP2AutoLoginBoolean():
            logger.debug("Autologin using '%s' file" %
                         A2P2ClientPreferences.getPreferencesFileName())
            self.ui.loop()
            vltifacility = self.facilityManager.facilities.get(
                VltiFacility.getName())
            vltifacility.autologin()

        # We now run the loop to wait for the message in a try/finally block so that if
        # the program is interrupted e.g. by control-C, the client terminates
        # gracefully. ( but sometimes fails inside tkinter/__init__.py CallWrapper/__call__() )

        # We test every 1s to see if the hub has sent a message
        delay = 0.1
        each = 10
        loop_cnt = 0
        warnForAspro = True

        while loop_cnt >= 0:
            try:
                loop_cnt += 1
                time.sleep(delay)

#                if loop_cnt % each == 0:
#                    logger.debug(f"loop {loop_cnt}")

                self.ui.loop()

                # process any stacked OBs
                self.facilityManager.processOB()

                if not self.a2p2SampClient.is_connected() and loop_cnt % each == 0:
                    try:
                        self.a2p2SampClient.connect()
                        self.ui.setSampId(self.a2p2SampClient.get_public_id())
                    except:
                        self.ui.setSampId(None)
                        if warnForAspro:
                            warnForAspro = False
                            self.ui.addToLog(
                                "\nPlease launch Aspro2 to submit your OBs.")
                        # TODO test for other exception than SAMPHubError(u'Unable to find a running SAMP Hub.',)
                        pass

                if self.a2p2SampClient.has_message():
                    try:
                        if self.a2p2SampClient.has_ob_message():
                            ob = OB(self.a2p2SampClient.get_ob_url())
                            self.facilityManager.processOB(ob)
                    except:
                        self.ui.addToLog(
                            "Exception during a2p2 ob creation: " + traceback.format_exc(), False)
                        self.ui.addToLog("Can't process last OB")

                    try:
                        if self.a2p2SampClient.has_model_message():
                                m = self.a2p2SampClient.get_model()
                                self.showModel(m)
                    except:
                        self.ui.addToLog(
                            "Exception during a2p2 ob creation: " + traceback.format_exc(), False)
                        self.ui.addToLog("Can't process last OB")

                    # always clear previous received message
                    self.a2p2SampClient.clear_message()

                if self.ui.requestAbort:
                    loop_cnt = -1
            except KeyboardInterrupt:
                loop_cnt = -1
        print("\nDisconnecting SAMP ...")
        self.a2p2SampClient.disconnect()
        print("Bye!")


    def createPreferencesFile():
        A2P2ClientPreferences.createPreferencesFile()


    def showModel(self, xmlmodel):
        from a2p2.jmmc.models import modelsFromXml
        self.ui.addToLog("Received star model")
        self.ui.addToLog(modelsFromXml(xmlmodel))


class A2P2ClientPreferences():
    # define application name
    appname = "a2p2"

    def __init__(self):
        self._config = A2P2ClientPreferences.getPreferences()
        pass

    def exists(self):
        if self._config.sections():
            return True
        else:
            return False

    def getPreferences():
        preferences_file = A2P2ClientPreferences.getPreferencesFileName()
        config = configparser.ConfigParser(allow_no_value=True)
        config.read(preferences_file)
        return config

    def getPreferencesFileName():
        from appdirs import user_config_dir
        preferences_file = os.path.join(user_config_dir(
            A2P2ClientPreferences.appname), "prefs.ini")
        return preferences_file
    def updatePreferencesFile():
        return
        # TODO
        # we suppose the file exists
        filename = A2P2ClientPreferences.getPreferencesFileName()
        buffer=""
        for line in open(filename):
            buffer+=line+"\n"
        print (buffer)

    def createPreferencesFile():
        filename = A2P2ClientPreferences.getPreferencesFileName()
        if os.path.exists(filename):
            print(f"{filename} already exists. Nothing done")
            p=A2P2ClientPreferences()
            versionInPref=p.getA2P2Version()
            if __version__ != versionInPref:
                print(f"HINT: You may try to backup this file (V{versionInPref}) and merge with a new generated one for V{__version__}.")
        else:
            import getpass

            config = configparser.ConfigParser(allow_no_value=True)
            #config['DEFAULT'] = {'_noprefyet': '42'}

            config['a2p2'] = {}
            s = config['a2p2']
            s['# A2P2 SECTION'] = ""
            s['# = > please do not modify next properties <'] = ""
            s['version'] = __version__


            config['jmmc'] = {}
            s = config['jmmc']
            s['# JMMC SECTION'] = ""
            s['# = > please uncomment and update next properties to make it active <'] = ""
            s['#login'] = "my.email@my.lab"
            s['#password'] = "12345zZ"

            config['chara'] = {}
            s = config['chara']
            s['# CHARA SECTION'] = ""
            s['# = > please uncomment and update next properties to make it active <'] = ""
            s['# = > queueserver may be uncommented to forward OB to a remote server instead <'] = ""
            s['#queueserver'] = 'http://192.168.3.153:2468/test,http://localhost:2468/test'

            config['p2'] = {}
            s=config['p2']
            s['# ESO P2 SECTION'] = ""
            s['# = > please uncomment and update next properties to make it active <'] = ""
            s['#username'] = getpass.getuser()
            s['#password'] = "12345zZ"
            s['#autologin'] = "yes"
            s['# = > please change next properties to change the name recorded in the OB comments <'] = ""
            s['user_comment_name'] = f"{getpass.getuser()}"

            config['p2.iss.vltitype'] = {}
            s=config['p2.iss.vltitype']
            s['# = > please uncomment the default values to add for ISS.VLTITYPE <'] = ""
            s['# = > all supported will be added for any VLTI instrument if info is not provided by Aspro2 <'] = None
            s['#snapshot'] = None
            s['#imaging'] = None
            s['#time-series'] = None
            s['#astrometry'] = None

            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w+') as configfile:
                config.write(configfile)

            print("'%s' template file created to store preferences. Please check and adjust it's content." % filename)

    def getConfig(self, section, key, default=None):
        try:
            return self._config[section][key]
        except:
            return default

    def getConfigKeys(self, section, default=None):
        try:
            return list(self._config[section].keys())
        except:
            return default


    def getConfigBoolean(self, section, key, default=None):
        try:
            return self._config.getboolean(section, key)
        except:
            return default

    # Retrieve A2P2 prefs
    def getA2P2Version(self):
        return self.getConfig("a2p2", "version", 'missing')

    # Retrieve JMMC prefs
    def getJmmcLogin(self):
        return self.getConfig("jmmc", "login", None)

    def getJmmcPassword(self):
        return self.getConfig("jmmc", "password", None)

    # Retrieve CHARA prefs
    def getCharaQueueServer(self):
        s = self.getConfig("chara", "queueserver", None)
        if s:
            return s.split(",")


    # Retrieve P2 prefs
    def getP2Username(self):
        """ Get P2 username in config or use default demo account """
        return self.getConfig("p2", "username", '52052')

    def getP2Password(self):
        """Get P2 password in config or use default demo account"""
        return self.getConfig("p2", "password", 'tutorial')

    def getP2UserCommentName(self):
        import getpass
        return self.getConfig("p2", "user_comment_name", getpass.getuser())

    def getP2AutoLoginBoolean(self):
        return self.getConfigBoolean("p2", "autologin", False)


