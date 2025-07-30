#!/usr/bin/env python

__all__ = []

import sys
import logging
from turtle import bgcolor

from a2p2.gui import FacilityUI

from tkinter import ttk
from tkinter import *
from tkinter.ttk import *

logger = logging.getLogger(__name__)


class VltiUI(FacilityUI):

    def __init__(self, a2p2client):
        logger.info("init VltiUI")
        FacilityUI.__init__(self, a2p2client)

        #self.container = Frame(self, bd=3, relief=SUNKEN)
        self.container = Frame(self, relief=SUNKEN)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.loginFrame = LoginFrame(self)
        self.loginFrame.grid(row=0, column=0, sticky="nsew")

        self.treeFrame = TreeFrame(self)
        self.treeFrame.grid(row=0, column=0, sticky="nsew")
        self.tree = self.treeFrame.tree

        self.container.pack(fill=BOTH, expand=True)
        self.treeItemToRuns = {}
        self.treeItemToP2Items = {}

        self.ob = None

    def showLoginFrame(self, ob):
        self.ob = ob
        self.addToLog(
            "Sorry, your %s OB can't be submitted, please log in first, select container and press submit button." %
            (ob.instrumentConfiguration.name))
        self.loginFrame.tkraise()

    def isBusy(self):
        self.tree.configure(selectmode='none')

    def isIdle(self):
        self.tree.configure(selectmode='browse')

    def showTreeFrame(self, ob=None):
        if ob:
            instrum = ob.instrumentConfiguration.name
        else:
            instrum = "incoming"
        self.addToLog(
            "Please select a runId in ESO P2 database to process %s OB" % instrum)
        self.treeFrame.tkraise()

    def fillTree(self, runs):
        logger.debug(f"Start filling tree with {len(runs)} runs")
        if len(runs) == 0:
            self.ShowErrorMessage(
                "No Runs defined, impossible to program ESO's P2 interface.")
            return
        # cleanup old entries if any
        for item in self.treeItemToRuns:
            try:
                self.tree.delete(item)
            except:
                pass
        self.treeItemToRuns = {}

        for run in runs:
            if self.facility.hasSupportedInsname(run['instrument']):
                cid = run['containerId']
                self._insertInTree('', run['progId'], cid, run, run)

    def updateTree(self, run, containerId):
        logger.debug(
            f"updateTree with run : {run}\n and containerId: {containerId}")
        items, _ = self.facility.api.getItems(containerId)
        logger.debug(f"sub items are {items}")
        logger.debug(f"item keys in tree: {self.treeItemToP2Items.keys()}")
        for item in items:
            if item['itemType'] in ['Folder', 'Concatenation', 'Group']:
                if str(item['containerId']) in self.treeItemToP2Items.keys():
                    logger.debug(f"Item {item['containerId']} already in tree")
                else:
                    logger.debug(f"adding in tree : {item}")
                    self._insertInTree(
                        containerId, item['name'], item['containerId'], run, item)
            else:
                logger.debug(f"not inserted in tree : {item}")
        # TODO get children of our tree and remove part non present in items

    def selectTreeItem(self, containerId):
        item = str(containerId)
        self.tree.selection_set(item)
        self.tree.see(item)
        self.facility.containerInfo.store(
            self.treeItemToRuns[item], self.treeItemToP2Items[item])

    def _insertInTree(self, parentContainerID, name, containerID, run, item):
        instrument = run['instrument']
        if run != item:
            label = item['itemType']
        else:
            # {"runId":60900301,"progId":"60.A-9003(B)","title":"Tutorial account","period":60,
            # "scheduledPeriod":60,"mode":"VM","instrument":"FORS2","telescope":"UT1","ipVersion":104.26,
            # "isToO":false,"owned":true,"delegated":false,"itemCount":0,"containerId":2587672,
            # "pi":{"emailAddress":"52052@nodomain.net","firstName":"Phase 1/2 Tutorial","lastName":"Account"},
            # "observingConstraints":{"seeing":2.0}}
            label = "%s Run (IP %s)" % (run['mode'], run['ipVersion'])

        e = self.tree.insert(parentContainerID, 'end', containerID,
                             text=name, values=(run['instrument'], label))
        self.treeItemToRuns[e] = run
        self.treeItemToP2Items[e] = item

        # add a dummy child so we can show to the user he has to walk into the tree
        if run['itemCount'] > 0:
            self.tree.insert(containerID, 'end',
                             f"{containerID}_fillme", values=[])
        # return new tree item
        return e

    def on_tree_selection_changed(self, selection):
        logger.debug(f"tree selection change: {selection}")
        curItem = self.tree.focus()
        ret = self.tree.item(curItem)
        if len(ret['values']) > 0:
            self.facility.containerInfo.store(
                self.treeItemToRuns[curItem], self.treeItemToP2Items[curItem])
            self.facility.tryLastOB()

    def on_tree_open(self, selection):
        logger.debug(f"tree open: {selection}")
        curItem = self.tree.focus()
        curChildren = self.tree.get_children(curItem)
        firstChild = curChildren[0]
        if not firstChild in self.treeItemToRuns.keys():
            self.tree.delete(firstChild)

            parentRun = self.treeItemToRuns[curItem]
            parentContainer = self.treeItemToP2Items[curItem]
            parentContainerID = parentContainer['containerId']
            self.updateTree(parentRun, parentContainerID)

    def showOBConfirmationButtons(self, ob=None, showAcqButtons=False):
        if not (ob):
            self.treeFrame.enable_buttons(False, showAcqButtons)
            return
        else:
            self.treeFrame.enable_buttons(True, showAcqButtons)

    def getIssVltitypeVars(self):
        return self.treeFrame.issVltiTypeCheckboxesVars

    def getAcquisitionType(self):
        return self.treeFrame.acquisitionType.get()


class TreeFrame(Frame):

    def __init__(self, vltiUI):
        Frame.__init__(self, vltiUI.container)
        self.vltiUI = vltiUI
        subframe = Frame(self)

        treeframe = Frame(subframe)
        self.tree = ttk.Treeview(
            treeframe, columns=('Project ID'), selectmode='browse')  # , 'instrument'))#, 'folder ID'))
        ysb = ttk.Scrollbar(
            treeframe, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(
            treeframe, orient='horizontal', command=self.tree.xview)

        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.tree.heading('#0', text='Project ID', anchor='w')
        self.tree.heading('#1', text='Instrument', anchor='w')
        self.tree.heading('#2', text='Container type', anchor='w')
        self.tree.bind(
            '<<TreeviewOpen>>', self.vltiUI.on_tree_open)
        self.tree.bind(
            '<<TreeviewSelect>>', self.vltiUI.on_tree_selection_changed)

        # grid layout does not expand and fill all area then move to pack
        #       self.tree.grid(row=0, column=0, sticky='nsew')
        #       ysb.grid(row=0, column=1, sticky='ns')
        #       xsb.grid(row=1, column=0, sticky='ew')
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        ysb.pack(side=RIGHT, fill="y")
        # xsb.pack(side=BOTTOM, fill="y") # will probably require to add
        # another 2 frames
        treeframe.pack(side=TOP, fill=BOTH, expand=True)

        # Control button Panel to abort /submit or provide more information to the current OB
        buttonframe = Frame(subframe)

        cindex = 0


        acquisitionFrame = Frame(buttonframe)

        self.acquisitionType = StringVar()
        self.acquisitionType.set("onaxis") # initialiser
        self.r1 = Radiobutton(acquisitionFrame, text="onaxis", variable=self.acquisitionType, value="onaxis")
        self.r2 = Radiobutton(acquisitionFrame, text="offaxis", variable=self.acquisitionType, value="offaxis")
        self.r3 = Radiobutton(acquisitionFrame, text="wide", variable=self.acquisitionType, value="wide")

        acquisitionFrame.grid(row=0, column=cindex)
        cindex += 1


        label = Label(buttonframe, text="|")
        label.grid(row=0, column=cindex)
        cindex += 1

        psection = "p2.iss.vltitype"
        pvltitypes = self.vltiUI.facility.a2p2client.preferences.getConfigKeys(
            psection)

        self.issVltiTypeCheckboxesVars = {}
        for isvt in self.vltiUI.facility.getIssVltiTypes():
            boolv = BooleanVar()
            self.issVltiTypeCheckboxesVars[isvt]=boolv
            boolv.set( not pvltitypes or len(pvltitypes)==0 or isvt in pvltitypes )
            logger.debug(f"Set preference value for {isvt} : {boolv.get()}")
            cb = Checkbutton(buttonframe, text=isvt, variable=boolv, onvalue=True, offvalue=False)
            cb.grid(row=0, column=cindex)
            cindex += 1

        self.abortButton = Button(buttonframe, text="Abort this OB",
                                  command=self.on_abortbutton_clicked, state=DISABLED)
        style = ttk.Style()
        sButtonStyle="Custom.TButton"
        ttk.Style().configure(sButtonStyle, background="green")
        self.submitButton = Button(
            buttonframe, text="Submit", command=self.on_submitbutton_clicked, state=DISABLED,
            style=sButtonStyle)
        self.abortButton.grid(row=0, column=cindex)
        cindex += 1
        self.submitButton.grid(row=0, column=cindex)
        buttonframe.pack(side=RIGHT)

        subframe.pack(side=TOP, fill=BOTH, expand=True)

    def enable_buttons(self, enableActions, showAcqButtons=False):
        if showAcqButtons and enableActions:
            self.r1.pack(side=LEFT)
            self.r2.pack(side=LEFT)
            self.r3.pack(side=LEFT)
        else:
            self.r1.pack_forget()
            self.r2.pack_forget()
            self.r3.pack_forget()

        if enableActions:
            flag = NORMAL
        else:
            flag = DISABLED
        self.submitButton["state"] = flag
        self.abortButton["state"] = flag

        # leave abort button always active to let user remove in case of error
        if self.vltiUI.facility.hasOB():
            self.abortButton["state"] = NORMAL

    def on_submitbutton_clicked(self):
        self.vltiUI.facility.popOB()
        self.enable_buttons(False)

    def on_abortbutton_clicked(self):
        self.vltiUI.facility.popOB(ignore=True)
        self.enable_buttons(False)


class LoginFrame(Frame):

    def __init__(self, vltiUI):
        Frame.__init__(self, vltiUI.container)
        self.vltiUI = vltiUI

        prefs = vltiUI.a2p2client.preferences

        self.loginframe = LabelFrame(
            self, text="login (ESO USER PORTAL or demo account)")

        self.username_label = Label(self.loginframe, text="USERNAME")
        self.username_label.pack()
        self.username = StringVar()
        self.username.set(prefs.getP2Username())
        self.username_entry = Entry(
            self.loginframe, textvariable=self.username)
        self.username_entry.pack()

        self.password_label = Label(self.loginframe, text="PASSWORD")
        self.password_label.pack()
        self.password = StringVar()
        self.password.set(prefs.getP2Password())
        self.password_entry = Entry(
            self.loginframe, textvariable=self.password, show="*")
        self.password_entry.pack()

        self.loginbutton = Button(
            self.loginframe, text="LOG IN", command=self.on_loginbutton_clicked)
        self.loginbutton.pack()

        self.loginframe.pack()
        self.pack(side=TOP, fill=BOTH, expand=True)

    def on_loginbutton_clicked(self):
        self.vltiUI.facility.connectAPI(
            self.username.get(), self.password.get(), self.vltiUI.ob)


# TODO move into a common part
def getFolders(p2api, containerId):
    folders = []
    items, _ = p2api.getItems(containerId)
    for item in items:
        if item['itemType'] in ['Folder', 'Concatenation']:
            folders.append(item)
    return folders
