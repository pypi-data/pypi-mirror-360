#!/usr/bin/env python

__all__ = []

import re

from a2p2.vlti.instrument import OBConstraints
from a2p2.vlti.instrument import OBTarget
from a2p2.vlti.instrument import TSF
from a2p2.vlti.instrument import VltiInstrument
import logging

HELPTEXT = """
    Please define MATISSE instrument help in a2p2/vlti/matisse.py
"""


class Matisse(VltiInstrument):

    def __init__(self, facility):
        # MATISSE_LM" MATISSE_N
        VltiInstrument.__init__(self, facility, "MATISSE_LM")

    def checkOB(self, ob, p2container=None):
        ui = self.ui

        instrumentConfiguration = ob.instrumentConfiguration
        BASELINE = ob.interferometerConfiguration.stations
        # Compute tel = UT or AT
        # TODO move code into common part
        if "U" in BASELINE:
            tel = "UT"
        else:
            tel = "AT"

        instrumentMode = instrumentConfiguration.instrumentMode
        fringeTrackerMode = "GRA4MAT" in instrumentConfiguration.fringeTrackerMode
        if fringeTrackerMode:
            tsfSuffix = "_ft"
            ui.addToLog("OB requested with GRA4MAT")
        else:
            tsfSuffix = ""
            ui.addToLog("OB requested without GRA4MAT")

        for observationConfiguration in self.getSequence(ob):

            # create keywords storage objects
            acqTSF = TSF(self, f"MATISSE_img_acq{tsfSuffix}.tsf")  # or .tsfx?
            obsTSF = TSF(self, f"MATISSE_hyb_obs{tsfSuffix}.tsf")

            obConstraints = OBConstraints(self)

            if 'SCIENCE' in observationConfiguration.type:
                obsTSF.DPR_CATG = 'SCIENCE'  # Default OB are CALIB
            else:
                obsTSF.DPR_CATG = 'CALIB'

            scienceTarget = observationConfiguration.SCTarget
            obTarget = OBTarget(self, scienceTarget)

            # Set baseline  interferometric array code (should be a keywordlist)
            acqTSF.ISS_BASELINE = [self.getBaselineCode(ob)]

            self.checkIssVltiType(acqTSF)

            # define some default values
            VIS = 1.0  # FIXME

            # Retrieve Fluxes
            acqTSF.SEQ_TARG_FLUX_L = self.getFlux(scienceTarget, "L_JY")
            acqTSF.SEQ_TARG_FLUX_N = self.getFlux(scienceTarget, "N_JY")
            acqTSF.SEQ_TARG_MAG_K = self.getFlux(scienceTarget, "K")
            # H is only present in _ft template
            if fringeTrackerMode:
                try:
                    acqTSF.SEQ_TARG_MAG_H = self.getFlux(scienceTarget, "H")
                except:
                    ui.addToLog("H mag is missing. default value will be used",
                                displayString=True, level=logging.WARNING)

            # TODO : make AO & GS more consistent ( on Aspro2 side ? )
            # AO target
            aoTarget = ob.get(observationConfiguration, "AOTarget")
            if aoTarget != None:
                acqTSF.COU_AG_GSSOURCE = 'SETUPFILE'  # since we have an AO
                # TODO check if AO coords should be required by template
                # AORA, AODEC  = self.getCoords(aoTarget,
                # requirePrecision=False)
                acqTSF.COU_AG_PMA, acqTSF.COU_AG_PMD = self.getPMCoords(
                    aoTarget)

            # Guide Star
            gsTarget = ob.get(observationConfiguration, 'GSTarget')
            if gsTarget != None:
                acqTSF.COU_AG_GSSOURCE = 'SETUPFILE'  # since we have a GS
                # special hack waiting for uniform way
                alpha, delta = self.getCoords(gsTarget, requirePrecision=False)
                acqTSF.COU_AG_ALPHA, acqTSF.COU_AG_DELTA = alpha.replace(
                    ":", ""), delta.replace(":", "")
                acqTSF.COU_AG_PMA, acqTSF.COU_AG_PMD = self.getPMCoords(
                    gsTarget)

                # no PMRA, PMDE for GS ??

                acqTSF.COU_GS_MAG = self.getFlux(gsTarget, "V")
                try:
                    if "AT" in tel:  # try better band observing on UT
                        acqTSF.COU_GS_MAG = self.getFlux(gsTarget, "G")
                except:
                    ui.addToLog(
                        "G mag can't be retreived for AT on the guide star. Use V instead")
            else:
                acqTSF.COU_GS_MAG = self.getFlux(scienceTarget, "V")
                try:
                    if "AT" in tel:  # try better band observing on UT
                        acqTSF.COU_GS_MAG = self.getFlux(scienceTarget, "G")
                except:
                    ui.addToLog(
                        "G mag can't be retreived for AT on the science star. Use V instead")

            # LST interval
            try:
                obsConstraint = observationConfiguration.observationConstraints
                LSTINTERVAL = obsConstraint.LSTinterval
            except:
                LSTINTERVAL = None

            # Constraints
            obConstraints.name = 'Aspro-created constraints'
            skyTransparencyMagLimits = {"AT": 3, "UT": 5}
            #            if acqTSF.IAS.HMAG < skyTransparencyMagLimits[tel]:
            #                obConstraints.skyTransparency = 'Variable, thin cirrus'
            #            else:
            #                obConstraints.skyTransparency = 'Clear'

            obConstraints.skyTransparency = 'Clear'
            # FIXME: error (OB): "Phase 2 constraints must closely follow what was requested in the Phase 1 proposal.
            # The seeing value allowed for this OB is >= java0x0 arcsec."
            # FIXME REPLACE SEEING THAT IS NO MORE SUPPORTED
            # obConstraints.seeing = 1.0
            # baseline not in instrumecnstraints obConstraints.baseline = BASELINE.replace(' ', '-')
            # FIXME: default values NOT IN ASPRO!
            # constaints.airmass = 5.0
            # constaints.fli = 1
            # and store computed values in obsTSF

            # then call the ob-creation using the API if p2container exists.
            if p2container == None:
                ui.addToLog(obTarget.name +
                            " ready for p2 upload (details logged)")
                ui.addToLog(obTarget, False)
                ui.addToLog(obConstraints, False)
                ui.addToLog(acqTSF, False)
                ui.addToLog(obsTSF, False)
            else:
                self.createOB(p2container, obTarget, obConstraints, obsTSF.DPR_CATG, instrumentMode,
                                     LSTINTERVAL, [acqTSF, obsTSF])

    def formatDitTable(self):
        #    fluxTable = self.getDitTable()
        buffer = ' No dit table in use \n'
        # buffer = '   Tel | Spec |  spec band  | Flux (Jy)    | tau(ms)\n'
        #    buffer += '--------------------------------------------------------\n'
        #    for tel in ['AT']:
        #        for spec in ['Low','Med']:
        #            for band in  ['L','M','N']:
        #                for i in range(len(fluxTable[tel][spec][band]['Flux'])):
        #                    buffer += ' %3s | %4s | %3s | %2s |' % ( tel,
        #                        spec, band, tel)
        #                    buffer += ' %4.1f <K<= %3.1f | %4.1f' % (fluxTable[tel][spec][pol]['MAG'][i],
        #                                                             fluxTable[tel][spec][
        #                        pol]['MAG'][i + 1],
        #                        fluxTable[tel][spec][pol]['DIT'][i])
        #                    buffer += "\n"

        return buffer
